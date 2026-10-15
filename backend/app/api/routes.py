from __future__ import annotations
from uuid import uuid4
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.ai.chat import assign
from app.ai.runtime import respond, runtime_settings, status as ai_status
from app.core.config import settings
from app.resources.monitor import pressure_level, snapshot
from app.security.audit import recent, record
from app.security.control import Capability, controller
from app.security.paths import PathSecurityError, resolve_inside
from app.tasks.snapshots import snapshots
from app.tasks.state import TaskState, transition
from app.tasks.workspace import WorkspaceManager
from app.tools.registry import REGISTRY, inspect_tool
router=APIRouter(); workspace_manager=WorkspaceManager(settings.workspace_root); TASKS:dict[str,dict]={}
class FileWrite(BaseModel): path:str; content:str=Field(max_length=2_000_000)
class TaskCreate(BaseModel): name:str=Field(min_length=1,max_length=120); objective:str=Field(min_length=1,max_length=2000)
class ChatMessage(BaseModel): message:str=Field(min_length=1,max_length=8000); assign_task:bool=True
class SecurityModes(BaseModel): safe_mode:bool|None=None; local_only:bool|None=None
class CapabilityUpdate(BaseModel): allowed:bool
class AISettings(BaseModel): cloud_enabled:bool|None=None; web_search_enabled:bool|None=None
@router.get('/health')
def health(): return {'status':'ok','service':'nila-virtual-computer','version':'0.3.0','platform':settings.platform}
@router.get('/resources')
def resources():
 data=snapshot(settings.data_root if settings.data_root.exists() else settings.shared_root.anchor or '/'); data['pressure']=pressure_level(data); return data
@router.get('/files')
def list_files(path:str='.'):
 try: target=resolve_inside(settings.shared_root,path)
 except PathSecurityError as exc: raise HTTPException(400,str(exc)) from exc
 if target==settings.shared_root: target.mkdir(parents=True,exist_ok=True)
 if not target.exists() or not target.is_dir(): raise HTTPException(404,'directory not found')
 return {'path':str(target.relative_to(settings.shared_root)),'items':[{'name':i.name,'type':'directory' if i.is_dir() else 'file','size':i.stat().st_size if i.is_file() else None} for i in sorted(target.iterdir(),key=lambda p:(not p.is_dir(),p.name.lower()))]}
@router.post('/files')
def write_file(payload:FileWrite):
 try: controller.require(Capability.FILES); target=resolve_inside(settings.shared_root,payload.path)
 except (PathSecurityError,PermissionError) as exc: raise HTTPException(403,str(exc)) from exc
 target.parent.mkdir(parents=True,exist_ok=True); target.write_text(payload.content,encoding='utf-8'); record('file.write',actor='user',details={'path':str(target.relative_to(settings.shared_root))}); return {'ok':True,'path':str(target.relative_to(settings.shared_root))}
def _create_task(name:str,objective:str):
 if controller.snapshot()['emergency_stop']: raise HTTPException(423,'AI emergency stop is active')
 task_id=f'task-{uuid4().hex[:12]}'; workspace=workspace_manager.create(task_id); task={'id':task_id,'name':name,'objective':objective,'state':TaskState.QUEUED.value,'workspace':str(workspace),'verification':'pending'}; TASKS[task_id]=task; record('task.created',actor='user',task_id=task_id,details={'name':name}); return task
@router.post('/tasks')
def create_task(payload:TaskCreate): return _create_task(payload.name,payload.objective)
@router.get('/ai/settings')
def get_ai_settings(): return ai_status()
@router.post('/ai/settings')
def set_ai_settings(payload:AISettings):
 if payload.cloud_enabled is not None: runtime_settings.cloud_enabled=payload.cloud_enabled
 if payload.web_search_enabled is not None: runtime_settings.web_search_enabled=payload.web_search_enabled
 record('ai.settings',actor='user',details={'cloud_enabled':runtime_settings.cloud_enabled,'web_search_enabled':runtime_settings.web_search_enabled}); return ai_status()
@router.post('/ai/chat')
def ai_chat(payload:ChatMessage):
 if controller.snapshot()['emergency_stop']: raise HTTPException(423,'AI emergency stop is active')
 try: answer=respond(payload.message)
 except (PermissionError,RuntimeError,ValueError,OSError) as exc: raise HTTPException(503,str(exc)) from exc
 task=None
 if payload.assign_task:
  assignment=assign(payload.message); task=_create_task(assignment.task_name,assignment.objective); record('ai.chat.assignment',actor='user',task_id=task['id'],details={'chat_id':assignment.id})
 record('ai.chat',actor='user',task_id=task['id'] if task else None,details={'provider':answer['provider'],'source_count':len(answer['sources'])})
 return {**answer,'task':task,'security':controller.snapshot()}
@router.get('/tasks')
def list_tasks(): return list(TASKS.values())
@router.post('/tasks/{task_id}/transition/{target}')
def transition_task(task_id:str,target:TaskState):
 task=TASKS.get(task_id)
 if not task: raise HTTPException(404,'task not found')
 if controller.snapshot()['emergency_stop'] and target in {TaskState.PREPARING,TaskState.RUNNING}: raise HTTPException(423,'AI emergency stop is active')
 try: task['state']=transition(TaskState(task['state']),target).value
 except ValueError as exc: raise HTTPException(409,str(exc)) from exc
 record('task.transition',task_id=task_id,details={'state':task['state']}); return task
@router.post('/tasks/{task_id}/snapshot')
def create_snapshot(task_id:str):
 task=TASKS.get(task_id)
 if not task: raise HTTPException(404,'task not found')
 path=snapshots.create(task_id,workspace_manager.get(task_id)); record('task.snapshot',task_id=task_id,details={'snapshot':path.name}); return {'ok':True,'snapshot':path.name}
@router.get('/security')
def security_state(): return controller.snapshot()
@router.post('/security/emergency-stop')
def emergency_stop():
 state=controller.set_emergency_stop(True)
 for task in TASKS.values():
  if task['state'] not in {TaskState.COMPLETED.value,TaskState.FAILED.value,TaskState.CANCELLED.value}: task['state']=TaskState.PAUSED.value
 record('security.emergency_stop',actor='user'); return state
@router.post('/security/resume')
def resume_ai(): state=controller.set_emergency_stop(False); record('security.resume',actor='user'); return state
@router.post('/security/modes')
def security_modes(payload:SecurityModes): state=controller.set_mode(safe_mode=payload.safe_mode,local_only=payload.local_only); record('security.modes',actor='user',details=state); return state
@router.post('/security/capabilities/{capability}')
def capability_update(capability:Capability,payload:CapabilityUpdate): state=controller.set_capability(capability,payload.allowed); record('security.capability',actor='user',details={'capability':capability.value,'allowed':payload.allowed}); return state
@router.get('/audit')
def audit(limit:int=100): return recent(limit)
@router.get('/tools')
def tools(): return [{**spec.__dict__,**inspect_tool(tool_id)} for tool_id,spec in REGISTRY.items()]
