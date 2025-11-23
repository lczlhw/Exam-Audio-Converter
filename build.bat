@echo off
chcp 65001 >nul
set PYTHONUTF8=1
TITLE Python 项目打包工具
echo ==============================
echo   PyInstaller 自动打包开始
echo ==============================

REM 清理旧构建
echo 清理旧构建文件...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM 安装依赖
echo 检查 Python 依赖...
pip install -r requirements.txt

REM 运行打包
echo 开始使用 app.spec 构建...
pyinstaller main.spec --clean

REM 检查结果
if exist dist\exam_audio_converter.exe (
    echo ------------------------------
    echo 打包成功！
    echo 文件位置：dist\exam_audio_converter.exe
    echo ------------------------------
) else (
    echo *** 打包失败，请检查错误信息 ***
)

pause
