& .\disable_proxy.bat
Invoke-WebRequest -Uri "https://www.chuanfang.org/client/geoip.dat" -Headers @{"Authorization" = "Basic "+[System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes("用户名:密码" ))} -Method Get -OutFile '.\geoip.dat'
& .\restart.bat
& .\enable_proxy.bat
