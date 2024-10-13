#!/bin/bash

# 获取当前的Wi-Fi服务名（通常为“Wi-Fi”）
wifi_service="Wi-Fi"

# 禁用 HTTP 代理
networksetup -setwebproxystate "$wifi_service" off

# 禁用 HTTPS 代理
networksetup -setsecurewebproxystate "$wifi_service" off

# 禁用 SOCKS 代理
networksetup -setsocksfirewallproxystate "$wifi_service" off

echo "已禁用当前 Wi-Fi 连接的 HTTP、HTTPS 和 SOCKS 代理"
