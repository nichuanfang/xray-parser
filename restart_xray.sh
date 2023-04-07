#!/bin/bash
wget https://config.vencenter.cn/server/config.json -O /usr/local/etc/xray/config.json
systemctl restart xray.service
