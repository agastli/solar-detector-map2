@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

REM === Set your commit message with date and time ===
set COMMIT_MSG=Update on %date% at %time%

REM === Go to the current script directory ===
cd /d "%~dp0"

REM === Remove unnecessary LFS tracking ===
git lfs untrack "models/yolov8x.pt" >nul 2>&1
if exist .gitattributes (
    git add .gitattributes
)

REM === Ensure Git repo is initialized ===
git rev-parse --is-inside-work-tree >nul 2>&1
IF ERRORLEVEL 1 (
    echo Not a git repository. Initializing...
    git init
)

REM === Add remote if missing ===
git remote get-url origin >nul 2>&1
IF ERRORLEVEL 1 (
    git remote add origin https://github.com/agastli/solar-detector-app.git
)

REM === Switch or create the branch ===
git rev-parse --verify solar-app-dev >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    git checkout solar-app-dev
) ELSE (
    git checkout -b solar-app-dev
)

REM === Stage all changes ===
git add .

REM === Commit if there are changes ===
git diff --cached --quiet
IF %ERRORLEVEL% EQU 1 (
    git commit -m "%COMMIT_MSG%"
) ELSE (
    echo No changes to commit.
)

REM === Push to GitHub ===
git push -u origin solar-app-dev

ENDLOCAL
pause
