@echo off
echo ========================================
echo   ADH Dependencies Installation Fix
echo ========================================
echo.
echo This script will install dependencies with --legacy-peer-deps
echo to resolve React 19 RC compatibility issues.
echo.
pause

cd web

echo Cleaning old installations...
if exist "node_modules" (
    echo Removing node_modules folder...
    rmdir /s /q node_modules
)
if exist "package-lock.json" (
    echo Removing package-lock.json...
    del /f /q package-lock.json
)
echo.

echo Installing dependencies with --legacy-peer-deps...
call npm install --legacy-peer-deps

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo [SUCCESS] Dependencies installed!
    echo ========================================
    echo.
    echo You can now run: check_and_start.bat
    echo Or manually: npm run dev
    echo.
) else (
    echo.
    echo ========================================
    echo [ERROR] Installation failed
    echo ========================================
    echo.
    echo Please try:
    echo 1. Update npm: npm install -g npm@latest
    echo 2. Clear cache: npm cache clean --force
    echo 3. Try again
    echo.
)

pause
