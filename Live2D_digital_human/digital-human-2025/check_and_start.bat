@echo off
echo ========================================
echo    Live2D Digital Human Startup Tool
echo ========================================
echo.

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
if exist "public\libs\live2dcubismcore.min.js" (
    echo [OK] Found live2dcubismcore.min.js
) else (
    echo [ERROR] Missing public\libs\live2dcubismcore.min.js
    echo         Please ensure the file exists
    pause
    exit /b 1
)
echo.

REM Check model files
echo [3/5] Checking Live2D model files...
if exist "public\haru_greeter_pro_jp\runtime\haru_greeter_t05.model3.json" (
    echo [OK] Found model files
) else (
    echo [WARN] Default model not found
    echo        Path: public\haru_greeter_pro_jp\runtime\haru_greeter_t05.model3.json
    echo        Digital human may not load properly
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
echo Starting Digital Human Project...
echo URL: http://localhost:3000
echo TIP: Open browser DevTools (F12) to check loading status
echo Press Ctrl+C to stop server
echo ========================================
echo.

npm run dev
