@echo off
:start
cls
set /p var=请选择模式(1白名单 2黑名单)：
echo.
if /i "%var%"=="" goto start
if /i %var%==1 goto a
if /i %var%==2 goto b else (echo 没有这个选项，请重试！~&pause)
goto start
:a
copy /y D:\soft\xray\config\white.json D:\soft\xray\config.json    
call restart.bat
echo 白名单已开启!
timeout /t 1
exit
goto start
:b
copy /y D:\soft\xray\config\black.json D:\soft\xray\config.json
call restart.bat
echo 黑名单已开启!
timeout /t 1
exitgoto start
