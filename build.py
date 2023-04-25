#!/usr/local/bin/python
# coding=utf-8；

# webhook触发更新路由规则
import json
import os

# 读取环境变量

# xray协议key
XRAY_WINDOWS_KEY = os.environ.get('XRAY_WINDOWS_KEY','')
# trojan协议key
XRAY_TROJAN_KEY = os.environ.get('XRAY_TROJAN_KEY','')

if XRAY_WINDOWS_KEY == '':
    raise RuntimeError('必须配置环境变量XRAY_WINDOWS_KEY!')

if XRAY_TROJAN_KEY == '':
    raise RuntimeError('必须配置环境变量XRAY_TROJAN_KEY!')

XRAY_PARSER_PATH = '/xray-parser/'
XRAY_PATH = '/xray/'

with open(f'{XRAY_PARSER_PATH}routing.json') as routing_file:
    routing = json.load(routing_file)

with open(f'{XRAY_PARSER_PATH}dns.json') as dns_file:
    dns = json.load(dns_file)

inbounds = []
# 构建inbounds   文件夹路径 文件夹集合 文件集合
for dir_path,dir_list,file_list in os.walk(f'{XRAY_PARSER_PATH}inbounds'):
    for file in file_list:
        with open(dir_path+'/'+file) as inbound_file:
            server_dict:dict = json.load(inbound_file)
            if file[:-5]=='windows':
                # 添加密钥
                server_dict['settings']['clients'][0]['id'] = XRAY_WINDOWS_KEY
            elif file[:-5]=='trojan':
                # 添加密钥
                server_dict['settings']['clients'][0]['password'] = XRAY_TROJAN_KEY
            inbounds.append(server_dict) 

# 拼到client中 
with open(f'{XRAY_PARSER_PATH}server.json') as server_file:
    server = json.load(server_file) 

# 配置路由
server['routing'] = routing
# 配置dns
server['dns'] = dns

server['inbounds'] = inbounds

# 持久化
json.dump(server,open(f'{XRAY_PATH}config.json','w+'))
