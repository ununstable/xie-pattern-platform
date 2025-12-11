@echo off
echo 正在启动纹样库平台...
echo.

echo 第一步：启动Flask应用...
start cmd /k "python app.py"

timeout /t 5 /nobreak >nul
echo.

echo 第二步：启动natapp隧道...
echo 您的公网地址：https://d556b698.natappfree.cc
echo.

natapp -config=natapp_config.ini
pause