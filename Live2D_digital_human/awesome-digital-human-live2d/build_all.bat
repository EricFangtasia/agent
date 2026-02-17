@echo off
chcp 65001 >nul
echo ========================================
echo    数字人Live2D完整打包脚本
echo ========================================
echo.

:: 检查是否在正确的目录
if not exist "main.py" (
    echo [错误] 请在 awesome-digital-human-live2d 目录下运行此脚本
    pause
    exit /b 1
)

:: 第一步：打包后端Python服务
echo [步骤 1/5] 安装PyInstaller...
pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo [步骤 2/5] 打包后端Python服务...
echo 这可能需要几分钟时间...
pyinstaller build_backend.spec --clean

if not exist "dist\DigitalHuman-Backend\DigitalHuman-Backend.exe" (
    echo [错误] 后端打包失败！
    pause
    exit /b 1
)

echo [成功] 后端打包完成！
echo 位置: dist\DigitalHuman-Backend\
echo.

:: 第二步：打包前端Electron应用
echo [步骤 3/5] 进入前端目录并安装依赖...
cd web

:: 检查node_modules是否存在
if not exist "node_modules" (
    echo 首次打包，正在安装依赖...
    call npm install
) else (
    echo 依赖已存在，安装Electron相关依赖...
    call npm install electron@^28.0.0 electron-builder@^24.13.3 --save-dev
)

echo.
echo [步骤 4/5] 构建Next.js静态文件...
call npm run build

if not exist "out" (
    echo [错误] Next.js构建失败！
    cd ..
    pause
    exit /b 1
)

echo [成功] Next.js构建完成！
echo.

echo [步骤 5/5] 打包Electron应用...
echo 这可能需要较长时间（下载Electron二进制文件）...
call npm run dist

if not exist "release" (
    echo [错误] Electron打包失败！
    cd ..
    pause
    exit /b 1
)

echo.
echo ========================================
echo    打包完成！
echo ========================================
echo.
echo 后端独立包位置: dist\DigitalHuman-Backend\
echo 前端Electron包位置: web\release\
echo.
echo 安装包文件:
dir /b release\*.exe 2>nul
echo.
echo 您可以运行安装包进行安装，或者直接运行便携版
echo.

cd ..
pause
