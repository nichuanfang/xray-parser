#!/bin/bash
wget --user 18326186224 --password 0820nCf9270 https://config.vencenter.cn/server/config.json -O /usr/local/etc/xray/config.json
systemctl restart xray.service
