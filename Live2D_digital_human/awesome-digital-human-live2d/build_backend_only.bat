@echo off
chcp 65001 >nul
echo ========================================
echo    后端Python服务打包脚本
echo ========================================
echo.

:: 检查是否在正确的目录
if not exist "main.py" (
    echo [错误] 请在 awesome-digital-human-live2d 目录下运行此脚本
    pause
    exit /b 1
)

:: 安装PyInstaller
echo [步骤 1/2] 安装PyInstaller...
pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo [步骤 2/2] 打包后端服务...
echo 这可能需要几分钟时间，请耐心等待...
pyinstaller build_backend.spec --clean

if not exist "dist\DigitalHuman-Backend\DigitalHuman-Backend.exe" (
    echo.
    echo [错误] 打包失败！请检查错误信息
    pause
    exit /b 1
)

echo.
echo ========================================
echo    打包完成！
echo ========================================
echo.
echo 输出目录: dist\DigitalHuman-Backend\
echo 主程序: DigitalHuman-Backend.exe
echo.
echo 使用方法：
echo 1. 将整个 dist\DigitalHuman-Backend 文件夹复制到目标机器
echo 2. 双击 DigitalHuman-Backend.exe 启动服务
echo 3. 服务将在 http://localhost:8880 启动
echo.
echo 注意：configs 和 assets 目录已包含在打包文件中
echo.

:: 打开输出目录
explorer dist\DigitalHuman-Backend

pause
