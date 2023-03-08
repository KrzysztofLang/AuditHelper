@echo off
net user BITAdmin /add
net localgroup Administratorzy BITAdmin /add
xcopy "%~dp0\openaudit" "C:\BIT\"
xcopy "%~dp0\anydesk" "C:\BIT\" 
xcopy "%~dp0\nVision" "C:\BIT\"
msiexec/i "C:\BIT\AnyDesk_BetterIT_ACL.msi" /quiet
msiexec/i "C:\BIT\nVAgentInstall.msi" /quiet
start /w "" "C:\BIT\INSTALL.bat"
pause
