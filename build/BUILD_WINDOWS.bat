@echo off
setlocal EnableExtensions DisableDelayedExpansion
rem Build from a short path to avoid Windows MAX_PATH issues during Nuitka installation.
set "SOURCE_ROOT=%~dp0.."
set "BUILD_DIR=%SystemDrive%\DDB_%RANDOM%_%RANDOM%"
set "SOURCE_APP=%SOURCE_ROOT%\GeometryDashAutomation"
set "BUILD_APP=%BUILD_DIR%\GeometryDashAutomation"
set "DEST_DIST=%SOURCE_ROOT%\dist\START_DASHBOARD.dist"

if not exist "%SOURCE_APP%\START_DASHBOARD.py" (
  echo ERROR: Application sources were not found next to the build folder.
  goto :fail
)
if exist "%BUILD_DIR%" (
  echo ERROR: Temporary build folder already exists: %BUILD_DIR%
  goto :fail
)
mkdir "%BUILD_DIR%" 2>nul
if errorlevel 1 (
  echo ERROR: Cannot create %BUILD_DIR%. Try running from a writable drive.
  goto :fail
)
mkdir "%BUILD_APP%" 2>nul
if errorlevel 1 goto :fail
>"%BUILD_DIR%\DoItForMeDash-build-marker.txt" echo Temporary build folder created by BUILD_WINDOWS.bat

echo Copying source into short build path: %BUILD_DIR%
robocopy "%SOURCE_APP%" "%BUILD_APP%" /E /XD .venv __pycache__ .idea /XF *.pyc /R:1 /W:1 /NFL /NDL /NJH /NJS
if errorlevel 8 goto :fail

echo Checking Microsoft C++ Build Tools...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0ENSURE_MSVC.ps1"
if errorlevel 1 (
  echo ERROR: MSVC compiler setup did not complete.
  goto :fail
)

pushd "%BUILD_APP%"
if errorlevel 1 goto :fail
py -3 -m venv .venv
if errorlevel 1 goto :fail_pop
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :fail_pop
".venv\Scripts\python.exe" -m pip install -r requirements.txt "Nuitka>=2.5,<3" ordered-set zstandard
if errorlevel 1 goto :fail_pop
".venv\Scripts\python.exe" -m nuitka --mode=standalone --msvc=latest --assume-yes-for-downloads --follow-imports --windows-console-mode=hide --include-data-files=dashboard.html=dashboard.html --include-data-files=doitforme_dash_banner.png=doitforme_dash_banner.png --output-dir="%BUILD_DIR%\dist" --output-filename=DoItForMeDash.exe START_DASHBOARD.py
if errorlevel 1 goto :fail_pop
popd

if not exist "%BUILD_DIR%\dist\START_DASHBOARD.dist\DoItForMeDash.exe" (
  echo ERROR: Nuitka did not produce the expected executable.
  goto :fail
)
if not exist "%SOURCE_ROOT%\dist" mkdir "%SOURCE_ROOT%\dist"
if not exist "%DEST_DIST%" mkdir "%DEST_DIST%"
echo Copying compiled application to original project...
robocopy "%BUILD_DIR%\dist\START_DASHBOARD.dist" "%DEST_DIST%" /E /R:1 /W:1 /NFL /NDL /NJH /NJS
if errorlevel 8 goto :fail
if not exist "%DEST_DIST%\DoItForMeDash.exe" goto :fail

if exist "%BUILD_DIR%\DoItForMeDash-build-marker.txt" rmdir /S /Q "%BUILD_DIR%"
echo.
echo SUCCESS: %DEST_DIST%\DoItForMeDash.exe
echo Application compilation complete. Return to BUILD_INSTALLER.bat to create Setup.
pause
exit /b 0

:fail_pop
popd
:fail
echo.
echo BUILD FAILED. Review messages above.
echo Temporary build files, if created, remain at: %BUILD_DIR%
echo No original source files were changed.
pause
exit /b 1
