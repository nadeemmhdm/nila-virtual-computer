$ErrorActionPreference='Stop'
$Root=Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Backend=Join-Path $Root 'backend'
$Frontend=Join-Path $Root 'frontend'
$Py=Join-Path $Backend '.venv\Scripts\python.exe'
if(-not (Test-Path $Py)){ throw 'Backend virtual environment missing. Run install.ps1 first.' }
Write-Host '== Python syntax =='; & $Py -m compileall -q (Join-Path $Backend 'app')
Write-Host '== Backend tests =='; & $Py -m pytest (Join-Path $Root 'tests') -q
Write-Host '== Frontend build =='; Push-Location $Frontend; try { npm run build } finally { Pop-Location }
Write-Host '== Backend health =='; Invoke-RestMethod 'http://127.0.0.1:8765/api/health' -TimeoutSec 5 | Out-Null
$task=Get-ScheduledTask -TaskName 'NilaVirtualComputer' -ErrorAction Stop
if($task.State -eq 'Disabled'){ throw 'NilaVirtualComputer scheduled task is disabled.' }
Write-Host '[PASS] Windows verification completed.'
