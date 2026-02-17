@echo off
echo.
echo =============================================
echo   实时互动数字人 - 无Dify依赖版本
echo =============================================
echo.

REM 检查是否安装了npm
where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 错误: 未找到npm。请确保已安装Node.js。
    echo 从 https://nodejs.org 下载并安装Node.js
    pause
    exit /b 1
)

REM 检查是否安装了依赖
if not exist "node_modules" (
    echo 安装项目依赖...
    npm install
    if %ERRORLEVEL% neq 0 (
        echo 依赖安装失败
        pause
        exit /b 1
    )
    echo.
)

echo 启动数字人系统...
echo 访问 http://localhost:3000/no-dify 开始使用
echo.
npm run dev