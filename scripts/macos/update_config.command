#!/bin/bash

# 禁用代理
./disable_proxy.sh

# 使用 curl 下载配置文件并使用基本认证
curl -u "username:password" -o "/opt/homebrew/etc/xray/config.json" "https://www.jaychou.site/client/client-windows-config.json"

# 重启 xray 服务
./restart.sh

# 启用代理
./enable_proxy.sh
