#!/bin/bash

# 定义代理地址和端口
proxy_host="127.0.0.1"
http_port="10809"
socks_port="10808"

# 获取当前的Wi-Fi服务名（通常为“Wi-Fi”）
wifi_service="Wi-Fi"

# 启用并设置 HTTP 代理
networksetup -setwebproxy "$wifi_service" "$proxy_host" "$http_port"
networksetup -setwebproxystate "$wifi_service" on

# 启用并设置 HTTPS 代理
networksetup -setsecurewebproxy "$wifi_service" "$proxy_host" "$http_port"
networksetup -setsecurewebproxystate "$wifi_service" on

# 启用并设置 SOCKS 代理
networksetup -setsocksfirewallproxy "$wifi_service" "$proxy_host" "$socks_port"
networksetup -setsocksfirewallproxystate "$wifi_service" on

echo "已启用当前 Wi-Fi 连接的 HTTP、HTTPS 和 SOCKS 代理"
