& .\disable_proxy.bat
& .\stop.bat
Invoke-WebRequest -Uri "https://www.jaychou.site/client/xray.exe" -Headers @{"Authorization" = "Basic "+[System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes("Username:Password" ))} -Method Get -OutFile '.\xray.exe'
Invoke-WebRequest -Uri "https://www.jaychou.site/client/wxray.exe" -Headers @{"Authorization" = "Basic "+[System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes("Username:Password" ))} -Method Get -OutFile '.\wxray.exe'
Invoke-WebRequest -Uri "https://www.jaychou.site/client/geoip.dat" -Headers @{"Authorization" = "Basic "+[System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes("Username:Password" ))} -Method Get -OutFile '.\geoip.dat'
Invoke-WebRequest -Uri "https://www.jaychou.site/client/geosite.dat" -Headers @{"Authorization" = "Basic "+[System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes("Username:Password" ))} -Method Get -OutFile '.\geosite.dat'
& .\restart.bat
& .\enable_proxy.bat
