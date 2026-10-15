$ErrorActionPreference = 'Stop'
$Repo = 'https://github.com/nadeemmhdm/nila-virtual-computer.git'
$InstallRoot = Join-Path $env:ProgramData 'NilaVirtualComputer\source'
$DataRoot = Join-Path $env:ProgramData 'NilaVirtualComputer'
$SharedRoot = Join-Path $env:PUBLIC 'NilaVirtualComputer\Shared'
$TaskName = 'NilaVirtualComputer'

function Info($m) { Write-Host "`n[NVC] $m" -ForegroundColor Cyan }
function Need-Admin {
  $id=[Security.Principal.WindowsIdentity]::GetCurrent()
  $p=New-Object Security.Principal.WindowsPrincipal($id)
  if(-not $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){ throw 'Run PowerShell as Administrator.' }
}
function Ensure-WingetPackage($id,$command) {
  if(Get-Command $command -ErrorAction SilentlyContinue){ return }
  if(-not (Get-Command winget -ErrorAction SilentlyContinue)){ throw "winget is required to install $id automatically." }
  Info "Installing $id"
  winget install --id $id --exact --silent --accept-package-agreements --accept-source-agreements
  $env:Path=[Environment]::GetEnvironmentVariable('Path','Machine')+';'+[Environment]::GetEnvironmentVariable('Path','User')
  if(-not (Get-Command $command -ErrorAction SilentlyContinue)){ throw "$id installation completed but $command is not available in PATH. Reopen PowerShell and rerun." }
}

Need-Admin
Ensure-WingetPackage 'Git.Git' 'git'
Ensure-WingetPackage 'Python.Python.3.12' 'python'
Ensure-WingetPackage 'OpenJS.NodeJS.LTS' 'node'

New-Item -ItemType Directory -Force -Path $DataRoot,$SharedRoot | Out-Null
if(Test-Path (Join-Path $InstallRoot '.git')) {
  Info 'Updating repository'
  git -C $InstallRoot fetch --prune origin
  git -C $InstallRoot reset --hard origin/main
} else {
  Info 'Cloning repository'
  if(Test-Path $InstallRoot){ Remove-Item -Recurse -Force $InstallRoot }
  git clone --depth 1 $Repo $InstallRoot
}

Info 'Creating Python environment'
$Backend=Join-Path $InstallRoot 'backend'
$Venv=Join-Path $Backend '.venv'
python -m venv $Venv
$Py=Join-Path $Venv 'Scripts\python.exe'
& $Py -m pip install --upgrade pip
& $Py -m pip install -r (Join-Path $Backend 'requirements.txt')

Info 'Building Web Desktop'
Push-Location (Join-Path $InstallRoot 'frontend')
npm install
npm run build
Pop-Location

[Environment]::SetEnvironmentVariable('NVC_DATA_ROOT',$DataRoot,'Machine')
[Environment]::SetEnvironmentVariable('NVC_WORKSPACE_ROOT',(Join-Path $DataRoot 'workspaces'),'Machine')
[Environment]::SetEnvironmentVariable('NVC_SHARED_ROOT',$SharedRoot,'Machine')
[Environment]::SetEnvironmentVariable('NVC_DATABASE_PATH',(Join-Path $DataRoot 'nila.db'),'Machine')
New-Item -ItemType Directory -Force -Path (Join-Path $DataRoot 'workspaces') | Out-Null

Info 'Installing auto-start task'
$Uvicorn=Join-Path $Venv 'Scripts\uvicorn.exe'
$Action=New-ScheduledTaskAction -Execute $Uvicorn -Argument 'app.main:app --host 127.0.0.1 --port 8765' -WorkingDirectory $Backend
$Trigger=New-ScheduledTaskTrigger -AtStartup
$Principal=New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
$Settings=New-ScheduledTaskSettingsSet -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit ([TimeSpan]::Zero)
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Force | Out-Null
Start-ScheduledTask -TaskName $TaskName

Info 'Running tests'
& $Py -m compileall -q (Join-Path $Backend 'app')
& $Py -m pytest (Join-Path $InstallRoot 'tests') -q
Push-Location (Join-Path $InstallRoot 'frontend'); npm run build; Pop-Location

Info 'Checking backend health'
$healthy=$false
for($i=0;$i -lt 20;$i++){
  try { $r=Invoke-RestMethod 'http://127.0.0.1:8765/api/health' -TimeoutSec 3; $healthy=$true; break } catch { Start-Sleep 1 }
}
if(-not $healthy){ throw 'Backend health check failed.' }

Info 'Windows installation and verification completed'
Write-Host "Source: $InstallRoot"
Write-Host 'Backend: http://127.0.0.1:8765'
Write-Host "Shared: $SharedRoot"
