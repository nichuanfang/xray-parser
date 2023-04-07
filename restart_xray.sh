#!/bin/bash
wget https://18326186224:0820nCf9270@config.vencenter.cn/server/config.json -O /usr/local/etc/xray/config.json
systemctl restart xray.service
