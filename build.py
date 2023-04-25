#!/usr/local/bin/python
# coding=utf-8；

# webhook触发更新路由规则
import json
import os
import sys
from  pynginxconfig import NginxConfig

# 读取参数 ${{ secrets.XRAY_DOMAIN }} ${{ secrets.XRAY_WINDOWS_KEY }} ${{ secrets.XRAY_TROJAN_KEY }}
if len(sys.argv) < 3:
    raise RuntimeError('请确认XRAY_DOMAIN,XRAY_WINDOWS_KEY,XRAY_TROJAN_KEY都已配置!')

# xray域名
XRAY_DOMAIN = sys.argv[1]
# xray协议key
XRAY_WINDOWS_KEY = sys.argv[2]
# trojan协议key
XRAY_TROJAN_KEY = sys.argv[3]

if XRAY_DOMAIN == '':
    raise RuntimeError('必须配置变量XRAY_DOMAIN!')
if XRAY_WINDOWS_KEY == '':
    raise RuntimeError('必须配置密钥XRAY_WINDOWS_KEY!')
if XRAY_TROJAN_KEY == '':
    raise RuntimeError('必须配置密钥XRAY_TROJAN_KEY!')

# 配置nginx文件
base_nc = NginxConfig()
with open('base_nginx.conf', 'r',encoding='utf-8') as f:
    base_conf = f.read() 
    base_nc.load(base_conf)

    server_1 = list(base_nc.data[0]['value'][1])
    server_1[1] = XRAY_DOMAIN
    base_nc.data[0]['value'][1]  = tuple(server_1)

    server_2 = list(base_nc.data[1]['value'][1])
    server_2[1] = XRAY_DOMAIN
    base_nc.data[1]['value'][1]  = tuple(server_2)

    server_3 = list(base_nc.data[2]['value'][1])
    server_3[1] = XRAY_DOMAIN
    base_nc.data[2]['value'][1]  = tuple(server_3)

    server_4 = list(base_nc.data[2]['value'][2])
    server_4[1] = f'^(.*) {XRAY_DOMAIN}$1 permanent'
    base_nc.data[2]['value'][2]  = tuple(server_4)


base_nc.savef('default.conf')


with open(f'routing.json') as routing_file:
    routing = json.load(routing_file)

with open(f'dns.json') as dns_file:
    dns = json.load(dns_file)

inbounds = []
# 构建inbounds   文件夹路径 文件夹集合 文件集合
for dir_path,dir_list,file_list in os.walk(f'inbounds'):
    for file in file_list:
        with open(dir_path+'/'+file) as inbound_file:
            server_dict:dict = json.load(inbound_file)
            if file[:-5]=='windows':
                # 添加密钥
                server_dict['settings']['clients'][0]['id'] = XRAY_WINDOWS_KEY
                server_dict['streamSettings']['tlsSettings']['serverName']=XRAY_DOMAIN
            elif file[:-5]=='trojan':
                # 添加密钥
                server_dict['settings']['clients'][0]['password'] = XRAY_TROJAN_KEY
            inbounds.append(server_dict) 

# 拼到client中 
with open(f'server.json') as server_file:
    server = json.load(server_file) 

# 配置路由
server['routing'] = routing
# 配置dns
server['dns'] = dns

server['inbounds'] = inbounds

# 持久化
json.dump(server,open(f'config.json','w+'))

