@echo off 
echo ��ʼ����ϵͳ�������Ժ�...
echo=
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f >nul 2>nul
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /d "127.0.0.1:10809" /f >nul 2>nul
echo ϵͳ�����ѿ���!
timeout /t 1 
