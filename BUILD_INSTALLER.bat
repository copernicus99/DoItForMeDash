@echo off
setlocal EnableExtensions DisableDelayedExpansion
set "ROOT=%~dp0"
set "APP=%ROOT%dist\START_DASHBOARD.dist\DoItForMeDash.exe"
set "SETUP=%ROOT%installer\DoItForMeDash_Setup_1.4.5.exe"
set "LOG=%ROOT%ONE_CLICK_BUILD.log"

>"%LOG%" echo DoItForMe Dash v1.4.5 one-click build

echo ==============================================
echo DoItForMe Dash - One-Click Installer Builder
echo ==============================================
echo.
echo v1.4.5 includes a recording/playback launcher fix.
echo A fresh application build is required; older compiled EXEs cannot be reused.
goto :build

:build
  goto :inno
)

:build
echo Compiling application with Nuitka...
call "%ROOT%build\BUILD_WINDOWS.bat"
if errorlevel 1 goto :failed
if not exist "%APP%" (
  echo ERROR: Expected compiled executable not found.
  goto :failed
)

:inno
echo.
echo Checking Inno Setup...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%ROOT%build\ENSURE_INNO.ps1" -OutputFile "%ROOT%build\ISCC_PATH.txt"
if errorlevel 1 goto :failed
if not exist "%ROOT%build\ISCC_PATH.txt" goto :failed
set /p "ISCC="<"%ROOT%build\ISCC_PATH.txt"
if not exist "%ISCC%" (
  echo ERROR: Inno Setup compiler not found at %ISCC%
  goto :failed
)
echo Compiling Windows Setup installer...
"%ISCC%" "%ROOT%build\DoItForMeDash.iss" >>"%LOG%" 2>&1
if errorlevel 1 (
  echo ERROR: Inno Setup compilation failed. Check ONE_CLICK_BUILD.log.
  goto :failed
)
if not exist "%SETUP%" (
  echo ERROR: Installer was not found at expected location.
  goto :failed
)
echo.
echo ==============================================
echo SUCCESS! Installer created:
echo %SETUP%
echo ==============================================
echo.
explorer.exe /select,"%SETUP%"
pause
exit /b 0

:failed
echo.
echo BUILD FAILED. Review the messages and ONE_CLICK_BUILD.log.
echo Any successfully compiled EXE is retained in dist.
pause
exit /b 1
