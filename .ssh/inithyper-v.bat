echo off

for /F %%i in ('powershell -command get-executionpolicy') do ( set Executionpolicyinfo=%%i)
echo %Executionpolicyinfo%|findstr "AllSigned"
IF %errorlevel% equ 0 (powershell -command set-executionpolicy RemoteSigned)
echo %Executionpolicyinfo%|findstr "Restricted"
IF %errorlevel% equ 0 (powershell -command set-executionpolicy RemoteSigned)
powershell -command get-executionpolicy

powershell -command "&{%~dp0inithyper-v.ps1}"
pause
