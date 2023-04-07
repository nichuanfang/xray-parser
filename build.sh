#!/bin/bash
# 生成dist文件
/usr/bin/python3 build.py
# 重启nginx服务 向外部提供https服务
docker restart nginx
sleep 3s
ssh -p 60022 -o StrictHostKeyChecking=no -t root@154.202.60.190 </root/code/xray-parser/restart_xray.sh
