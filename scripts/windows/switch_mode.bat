@echo off
:start
cls
set /p var=��ѡ��ģʽ(1��� 2������ 3������)��
echo.
if /i "%var%"=="" goto start
if /i %var%==1 goto a
if /i %var%==2 goto b
if /i %var%==3 (goto c) else (echo û�����ѡ������ԣ�~&pause)
goto start
:a
copy /y D:\soft\xray\config\mixed.json D:\soft\xray\config.json    
call restart.bat
echo ���ģʽ�ѿ���!
timeout /t 1
exit
goto start
:b
copy /y D:\soft\xray\config\white.json D:\soft\xray\config.json    
call restart.bat
echo �������ѿ���!
timeout /t 1
exit
goto start
:c
copy /y D:\soft\xray\config\black.json D:\soft\xray\config.json    
call restart.bat
echo �������ѿ���!
timeout /t 1
exitgoto start