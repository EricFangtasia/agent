@echo off
echo ========================================
echo    ADH Digital Human Startup Tool
echo    (awesome-digital-human-live2d)
echo ========================================
echo.

cd web

REM Check Node.js
echo [1/5] Checking Node.js...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found, please install Node.js first
    pause
    exit /b 1
)
node --version
echo [OK] Node.js installed
echo.

REM Check Cubism Core files
echo [2/5] Checking Cubism Core files...
if exist "public\sentio\core\live2dcubismcore.min.js" (
    echo [OK] Found live2dcubismcore.min.js
) else (
    echo [ERROR] Missing public\sentio\core\live2dcubismcore.min.js
    echo         Please ensure the file exists
    pause
    exit /b 1
)
echo.

REM Check Live2D Framework
echo [3/5] Checking Live2D Framework...
if exist "lib\live2d\Framework" (
    echo [OK] Found Live2D Framework
) else (
    echo [ERROR] Missing lib\live2d\Framework
    pause
    exit /b 1
)
echo.

REM Check dependencies
echo [4/5] Checking dependencies...
if exist "node_modules" (
    echo [OK] Dependencies installed
) else (
    echo [INFO] Installing dependencies with --legacy-peer-deps...
    call npm install --legacy-peer-deps
    if %errorlevel% neq 0 (
        echo [ERROR] Dependencies installation failed
        pause
        exit /b 1
    )
)
echo.

REM Start project
echo [5/5] Starting development server...
echo.
echo ========================================
echo Starting ADH Digital Human Project...
echo URL: http://localhost:3000/sentio
echo TIP: Configure Dify service before use
echo Press Ctrl+C to stop server
echo ========================================
echo.
echo Notice: 
echo - Default ports: 3000 (frontend) / 8000 (backend)
echo - Configure Dify API in settings on first use
echo - See: ..\README.md for detailed configuration
echo.

npm run dev
