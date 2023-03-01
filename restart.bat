@echo on
echo "wxray Restart"
taskkill /f /t /fi "imagename eq wxray.exe"
echo "wxray Stop"
start /d "D:\soft\Xray-windows-64" wxray.exe
echo "wxray Start"
pause