@echo off
setlocal

set "created=0"

REM Get today's date
for /f %%I in ('powershell -NoProfile -Command "Get-Date -Format \"yyyy-MM-dd\""') do set today=%%I

REM Input
set /p subtopic=Enter sub-topic name: 

REM Replace spaces with hyphens
set "safe_subtopic=%subtopic: =-%"

REM Folder name
if "%safe_subtopic%"=="" (
    set "folder_name=%today%"
) else (
    set "folder_name=%today%-%safe_subtopic%"
)

REM Create folder
if not exist "%folder_name%" (
    echo Creating folder: %folder_name%
    mkdir "%folder_name%" 2>nul
)

REM ✅ Check again if folder exists (important)
if exist "%folder_name%" (
    
    REM Create Python file
    (
        echo # Created on: %today%
        echo.
    ) > "%folder_name%\code.py"

    echo Created %folder_name%\code.py
    set created=1

) else (
    echo ❌ Failed to create folder "%folder_name%"
)

echo.
if "%created%"=="1" (
    echo Folder created successfully.
) else (
    echo Something went wrong.
)

endlocal