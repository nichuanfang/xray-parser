#!/bin/bash
if [ ! -d "/root/code/xray-parser" ]; then
    cd /root/code
    git clone https://github.com/nichuanfang/xray-parser.git
else
    cd /root/code/xray-parser
    # 丢弃本地未提交变更
    git checkout .
    # 检出指定分支
    git checkout client
    git pull
fi
docker restart crawler
