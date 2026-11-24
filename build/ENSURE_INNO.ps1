param([Parameter(Mandatory=$true)][string]$OutputFile)
$ErrorActionPreference = 'Stop'
function Find-Inno {
  $candidates = @(
    (Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 6\ISCC.exe'),
    (Join-Path $env:ProgramFiles 'Inno Setup 6\ISCC.exe'),
    (Join-Path $env:LOCALAPPDATA 'Programs\Inno Setup 6\ISCC.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'Inno Setup 7\ISCC.exe'),
    (Join-Path $env:ProgramFiles 'Inno Setup 7\ISCC.exe')
  )
  foreach ($p in $candidates) { if (Test-Path $p) { return $p } }
  foreach ($key in @('HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1','HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1','HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Inno Setup 6_is1')) {
    $item = Get-ItemProperty -Path $key -ErrorAction SilentlyContinue
    if ($item -and $item.InstallLocation) {
      $p = Join-Path $item.InstallLocation 'ISCC.exe'
      if (Test-Path $p) { return $p }
    }
  }
  $cmd = Get-Command ISCC.exe -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  return $null
}
$found=Find-Inno
if (-not $found) {
  Write-Host 'Inno Setup is not installed. It is required only on the PC building the installer.'
  $answer=Read-Host 'Install Inno Setup using Windows Package Manager (winget)? [Y/N]'
  if ($answer -notmatch '^(y|yes)$') { exit 2 }
  $winget=Get-Command winget.exe -ErrorAction SilentlyContinue
  if (-not $winget) {
    Write-Host 'winget is unavailable. Install Inno Setup from https://jrsoftware.org/isdl.php and retry.'
    exit 3
  }
  Write-Host 'Installing Inno Setup using the official winget package. Approve any UAC prompt.'
  & $winget.Source install --id JRSoftware.InnoSetup --exact --source winget --accept-source-agreements --accept-package-agreements
  if ($LASTEXITCODE -ne 0) {
    Write-Host "winget failed with exit code $LASTEXITCODE. Install from https://jrsoftware.org/isdl.php and retry."
    exit 4
  }
  $found=Find-Inno
  if (-not $found) {
    Write-Host 'Installation finished but ISCC.exe was not found. Restart this script after checking Inno Setup installation.'
    exit 5
  }
}
Set-Content -LiteralPath $OutputFile -Value $found -Encoding ascii
Write-Host "Inno Setup compiler: $found"
exit 0
