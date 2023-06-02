@echo on
echo "wxray Restart"
taskkill /f /t /fi "imagename eq wxray.exe"
echo "wxray Stop"
start /d "D:\xray\Xray-v1.8.1-reality" wxray.exe
echo "wxray Start"
timeout /t 1
exit
