#!/bin/bash
# 生成dist文件
python3 build.py
# 重启nginx服务 向外部提供https服务
docker restart nginx
