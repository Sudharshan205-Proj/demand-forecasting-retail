param(
    [string]$Root = (Get-Location).Path,
    [int]$Port = 8523
)

Set-Location $Root
$outDir = Join-Path $Root 'docs\final-audit\execution\phase-16'
$stdout = Join-Path $outDir 'command-001-stdout.txt'
$stderr = Join-Path $outDir 'command-001-stderr.txt'
$pidFile = Join-Path $outDir 'app.pid'

$p = Start-Process -FilePath (Join-Path $Root '.venv\Scripts\python.exe') `
    -ArgumentList '-m', 'streamlit', 'run', 'app/streamlit_app.py', '--server.port', $Port, '--server.headless', 'true' `
    -PassThru -RedirectStandardOutput $stdout -RedirectStandardError $stderr

$p.Id | Out-File -FilePath $pidFile -Encoding ascii
Write-Output ("app pid " + $p.Id)
