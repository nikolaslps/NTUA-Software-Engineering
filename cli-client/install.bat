@echo off
REM Create the batch file wrapper
echo @echo off > "%~dp0se2437.bat"
echo python "%~dp0cli.py" %%* >> "%~dp0se2437.bat"

REM Add script directory to PATH
for %%X in ("%~dp0") do set "NEWPATH=%%X"
setx PATH "%PATH%;%NEWPATH%"
set "PATH=%PATH%;%NEWPATH%"

REM Register an alias for PowerShell
doskey se2437="%~dp0se2437.bat" $*

echo Installation complete!
echo You can now use 'se2437' without .\ in PowerShell (only for the current session).
pause
