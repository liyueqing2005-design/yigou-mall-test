@echo off
chcp 65001 >nul
cd /d "%~dp0"

set "ALLURE=allure"
where allure >nul 2>nul
if errorlevel 1 set "ALLURE=C:\Users\qing124\allure\allure-2.46.0\bin\allure.bat"

echo 正在打开 Allure 测试报告，请保持本窗口打开，关闭本窗口即停止服务。
%ALLURE% open allure-report

pause
