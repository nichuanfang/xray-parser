#!/bin/bash


proxy(){
  export http_proxy=http://127.0.0.1:10809
  export https_proxy=$http_proxy
  export socks_proxy=socks://127.0.0.1:10808
  echo -e "终端代理已开启。"
}

noproxy(){
  unset http_proxy https_proxy socks_proxy
  echo -e "终端代理已关闭。"
}

noproxy

# 使用 curl 下载配置文件并使用基本认证
curl -u "username:password" -o "/opt/homebrew/etc/xray/config.json" "https://www.jaychou.site/client/client-windows-config.json"

proxy
