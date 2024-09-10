@echo off

REM Define the log file
set LOGFILE=build.log

REM Notify the user and give them time to read the message
echo The build process has started.
echo Output will not be visible during the build process.
echo Please check %LOGFILE% for detailed output.
echo.
timeout /t 10 /nobreak >nul

REM Start logging
echo Starting build process... > %LOGFILE%

REM Check if the "build" folder exists, then delete it
if exist build (
    echo Deleting "build" folder... >> %LOGFILE%
    rmdir /s /q build >> %LOGFILE% 2>&1
) else (
    echo "build" folder does not exist. >> %LOGFILE%
)

REM Check if the "dist" folder exists, then delete it
if exist dist (
    echo Deleting "dist" folder... >> %LOGFILE%
    rmdir /s /q dist >> %LOGFILE% 2>&1
) else (
    echo "dist" folder does not exist. >> %LOGFILE%
)

REM Delete all .spec files in the current directory
echo Deleting all .spec files... >> %LOGFILE%
del /f /q *.spec >> %LOGFILE% 2>&1

echo Cleanup complete! >> %LOGFILE%

REM Install required Python packages from requirements.txt
if exist requirements.txt (
    echo Installing dependencies from requirements.txt... >> %LOGFILE%
    pip install -r requirements.txt >> %LOGFILE% 2>&1
) else (
    echo "requirements.txt" not found, skipping installation of dependencies. >> %LOGFILE%
)

REM Run PyInstaller to create the onefile executable with a custom name
echo Running PyInstaller for Twitch-Channel-Point-Farmer-2.0.exe... >> %LOGFILE%
python -m PyInstaller --onefile --name Twitch-Channel-Point-Farmer-2.0 main.py >> %LOGFILE% 2>&1

echo First PyInstaller build complete! >> %LOGFILE%

REM Run PyInstaller again for the headless version
echo Running PyInstaller for Twitch-Channel-Point-Farmer-2.0-HEADLESS.exe... >> %LOGFILE%
python -m PyInstaller --onefile --noconsole --name Twitch-Channel-Point-Farmer-2.0-HEADLESS main.py >> %LOGFILE% 2>&1

echo Second PyInstaller build complete! >> %LOGFILE%

echo Build process finished. >> %LOGFILE%
pause
