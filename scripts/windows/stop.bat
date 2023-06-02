@echo on
echo "wxray Restart"
taskkill /f /t /fi "imagename eq wxray.exe"
echo "wxray Stop"
timeout /t 1
exit