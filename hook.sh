#!/bin/bash
if [ ! -d "/root/xray-parser" ]; then
    cd /root
    git clone https://github.com/nichuanfang/xray-parser.git
else
    cd /root/xray-parser
    # 丢弃本地变更
    git checkout .
    # 检出指定分支
    git checkout client
    git pull
fi
docker restart crawler
