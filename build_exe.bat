@echo off
echo ======================================================================
echo Building AikoArenaNotifier Standalone Windows Executable
echo ======================================================================

set PYTHON_EXE=.venv\Scripts\python.exe
if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python
)

"%PYTHON_EXE%" -m PyInstaller ^
    --noconfirm ^
    --onefile ^
    --noconsole ^
    --name AikoArenaNotifier ^
    --collect-all customtkinter ^
    --clean ^
    main.py

echo.
if %ERRORLEVEL% equ 0 (
    echo ======================================================================
    echo Build SUCCESS! Standalone executable is in: dist\AikoArenaNotifier.exe
    echo ======================================================================
) else (
    echo ======================================================================
    echo Build FAILED with error code %ERRORLEVEL%
    echo ======================================================================
)
pause
