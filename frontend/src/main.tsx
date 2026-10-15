import React, { useEffect, useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { Bot, Files, Folder, MonitorCog, Settings, SquareTerminal, X, Minus, Maximize2, ListTodo } from 'lucide-react'
import './styles.css'

type AppId = 'terminal' | 'files' | 'tasks' | 'monitor' | 'settings' | 'assistant'

type WindowState = {
  id: AppId
  title: string
  open: boolean
  minimized: boolean
  maximized: boolean
  x: number
  y: number
  w: number
  h: number
  z: number
}

const apiBase = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8765'

const appMeta: Record<AppId, { title: string; icon: React.ReactNode }> = {
  terminal: { title: 'Terminal', icon: <SquareTerminal size={22} /> },
  files: { title: 'Files', icon: <Files size={22} /> },
  tasks: { title: 'Tasks', icon: <ListTodo size={22} /> },
  monitor: { title: 'System Monitor', icon: <MonitorCog size={22} /> },
  settings: { title: 'Settings', icon: <Settings size={22} /> },
  assistant: { title: 'Nila AI', icon: <Bot size={22} /> },
}

const initialWindows: WindowState[] = Object.entries(appMeta).map(([id, meta], i) => ({
  id: id as AppId,
  title: meta.title,
  open: false,
  minimized: false,
  maximized: false,
  x: 80 + i * 26,
  y: 70 + i * 20,
  w: 720,
  h: 480,
  z: i + 1,
}))

function App() {
  const [windows, setWindows] = useState(initialWindows)
  const [clock, setClock] = useState(new Date())

  useEffect(() => {
    const t = setInterval(() => setClock(new Date()), 1000)
    return () => clearInterval(t)
  }, [])

  const topZ = useMemo(() => Math.max(...windows.map(w => w.z), 1), [windows])

  function patch(id: AppId, data: Partial<WindowState>) {
    setWindows(prev => prev.map(w => w.id === id ? { ...w, ...data } : w))
  }

  function openApp(id: AppId) {
    patch(id, { open: true, minimized: false, z: topZ + 1 })
  }

  function focus(id: AppId) {
    patch(id, { z: topZ + 1 })
  }

  return <div className="desktop">
    <div className="desktop-grid">
      {(Object.keys(appMeta) as AppId[]).map(id => <button className="desktop-icon" key={id} onDoubleClick={() => openApp(id)} onClick={() => openApp(id)}>
        <span className="desktop-icon-box">{appMeta[id].icon}</span>
        <span>{appMeta[id].title}</span>
      </button>)}
    </div>

    {windows.filter(w => w.open && !w.minimized).map(w => <Window key={w.id} data={w} onFocus={() => focus(w.id)} onPatch={d => patch(w.id, d)}>
      <AppSurface id={w.id} />
    </Window>)}

    <footer className="taskbar">
      <button className="launcher" onClick={() => openApp('assistant')}><Bot size={19} /> Nila</button>
      <div className="taskbar-apps">
        {windows.filter(w => w.open).map(w => <button key={w.id} className={w.minimized ? 'task-button muted' : 'task-button'} onClick={() => patch(w.id, { minimized: !w.minimized, z: topZ + 1 })}>{appMeta[w.id].icon}<span>{w.title}</span></button>)}
      </div>
      <div className="clock">{clock.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}<small>{clock.toLocaleDateString()}</small></div>
    </footer>
  </div>
}

function Window({ data, onFocus, onPatch, children }: { data: WindowState; onFocus: () => void; onPatch: (d: Partial<WindowState>) => void; children: React.ReactNode }) {
  const style = data.maximized ? { inset: '12px 12px 58px 12px', zIndex: data.z } : { left: data.x, top: data.y, width: data.w, height: data.h, zIndex: data.z }
  return <section className="window" style={style as React.CSSProperties} onMouseDown={onFocus}>
    <header className="window-titlebar">
      <div className="window-title">{appMeta[data.id].icon}<span>{data.title}</span></div>
      <div className="window-controls">
        <button onClick={() => onPatch({ minimized: true })}><Minus size={16} /></button>
        <button onClick={() => onPatch({ maximized: !data.maximized })}><Maximize2 size={15} /></button>
        <button onClick={() => onPatch({ open: false })}><X size={16} /></button>
      </div>
    </header>
    <div className="window-body">{children}</div>
  </section>
}

function AppSurface({ id }: { id: AppId }) {
  if (id === 'monitor') return <ResourceMonitor />
  if (id === 'files') return <FileManager />
  if (id === 'tasks') return <TaskManager />
  if (id === 'terminal') return <TerminalPlaceholder />
  if (id === 'assistant') return <Assistant />
  return <div className="panel"><h2>Settings</h2><p>Resource, AI, permissions, tools, browser, security and storage settings are being wired to backend configuration.</p></div>
}

function ResourceMonitor() {
  const [data, setData] = useState<any>(null)
  useEffect(() => {
    const load = () => fetch(`${apiBase}/api/resources`).then(r => r.json()).then(setData).catch(() => setData(null))
    load(); const t = setInterval(load, 5000); return () => clearInterval(t)
  }, [])
  if (!data) return <div className="panel"><h2>System Monitor</h2><p>Backend unavailable.</p></div>
  const gb = (v: number) => (v / 1024 / 1024 / 1024).toFixed(1)
  return <div className="panel"><h2>System Monitor</h2><div className="stats">
    <Stat label="CPU" value={`${data.cpu_percent}%`} />
    <Stat label="RAM" value={`${data.memory.percent}%`} sub={`${gb(data.memory.available)} GB free`} />
    <Stat label="Swap" value={`${data.swap.percent}%`} />
    <Stat label="Disk" value={`${data.disk.percent}%`} sub={`${gb(data.disk.free)} GB free`} />
    <Stat label="Pressure" value={data.pressure} />
  </div></div>
}

function Stat({ label, value, sub }: { label: string; value: string; sub?: string }) { return <div className="stat"><span>{label}</span><strong>{value}</strong>{sub && <small>{sub}</small>}</div> }

function FileManager() {
  const [items, setItems] = useState<any[]>([])
  const [error, setError] = useState('')
  const load = () => fetch(`${apiBase}/api/files`).then(r => r.json()).then(d => { setItems(d.items || []); setError('') }).catch(() => setError('Backend unavailable'))
  useEffect(load, [])
  return <div className="panel"><div className="toolbar"><Folder size={18}/><strong>Shared files</strong><button onClick={load}>Refresh</button></div>{error ? <p>{error}</p> : <div className="file-list">{items.length === 0 ? <p>No files yet.</p> : items.map(i => <div className="file-row" key={i.name}><span>{i.type === 'directory' ? 'Folder' : 'File'}</span><strong>{i.name}</strong><small>{i.size ?? ''}</small></div>)}</div>}</div>
}

function TaskManager() {
  const [tasks, setTasks] = useState<any[]>([])
  const load = () => fetch(`${apiBase}/api/tasks`).then(r => r.json()).then(setTasks).catch(() => setTasks([]))
  useEffect(() => { load(); const t = setInterval(load, 4000); return () => clearInterval(t) }, [])
  return <div className="panel"><h2>Autonomous Tasks</h2>{tasks.length === 0 ? <p>No tasks have been created.</p> : tasks.map(t => <div className="task-card" key={t.id}><div><strong>{t.name}</strong><small>{t.objective}</small></div><span className="badge">{t.state}</span></div>)}</div>
}

function TerminalPlaceholder() {
  return <div className="terminal"><div className="terminal-line">nila@virtual-computer:~$</div><p>Real PTY/WebSocket terminal integration is the next implementation milestone. This surface intentionally does not fake command output.</p></div>
}

function Assistant() {
  return <div className="assistant"><div className="assistant-hero"><Bot size={28}/><div><h2>Nila AI</h2><p>Local agent workspace</p></div></div><div className="assistant-note">The planner/runtime boundary is structured for local llama.cpp integration. AI-generated actions must pass schema, permission and filesystem validation before execution.</div><div className="assistant-input"><input placeholder="Ask Nila to create, inspect, test or fix something…" disabled/><button disabled>Send</button></div></div>
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>)
