$ErrorActionPreference = 'Stop'
$vswhere = Join-Path ${env:ProgramFiles(x86)} 'Microsoft Visual Studio\Installer\vswhere.exe'
function Find-MSVC {
    if (-not (Test-Path $vswhere)) { return $null }
    $path = & $vswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $path) { return $null }
    $vcvars = Join-Path ($path | Select-Object -First 1) 'VC\Auxiliary\Build\vcvars64.bat'
    if (Test-Path $vcvars) { return $vcvars }
    return $null
}
$found = Find-MSVC
if ($found) { Write-Host "MSVC detected: $found"; exit 0 }
Write-Host 'Microsoft C++ Build Tools (MSVC) are required for Nuitka with Python 3.13.'
Write-Host 'The official Microsoft installer can download several GB and may request administrator permission.'
$answer = Read-Host 'Download and install Microsoft C++ Build Tools now? [Y/N]'
if ($answer -notmatch '^(y|yes)$') { Write-Host 'Installation declined. Build cannot continue.'; exit 2 }
$bootstrap = Join-Path $env:TEMP 'DoItForMeDash_vs_BuildTools.exe'
$url = 'https://aka.ms/vs/17/release/vs_BuildTools.exe'
try {
    Write-Host "Downloading Microsoft installer from $url"
    Invoke-WebRequest -Uri $url -OutFile $bootstrap -UseBasicParsing
    Write-Host 'Launching official installer. Approve Windows UAC if prompted.'
    $args = @('--add','Microsoft.VisualStudio.Workload.VCTools','--includeRecommended','--passive','--wait','--norestart')
    $proc = Start-Process -FilePath $bootstrap -ArgumentList $args -Wait -PassThru
    Write-Host "Installer exit code: $($proc.ExitCode)"
    if ($proc.ExitCode -eq 3010 -or $proc.ExitCode -eq 1641) {
        Write-Host 'A reboot is required. Restart Windows and run BUILD_WINDOWS.bat again.'
        exit 3
    }
    if ($proc.ExitCode -ne 0) { Write-Host 'Build Tools installation failed. Review the Visual Studio Installer logs.'; exit 4 }
    $found = Find-MSVC
    if (-not $found) {
        Write-Host 'MSVC was not detected after installation. Restart Windows and retry, or repair Build Tools.'
        exit 5
    }
    Write-Host "MSVC is ready: $found"
    exit 0
} catch {
    Write-Host "Build Tools setup failed: $($_.Exception.Message)"
    exit 6
}
