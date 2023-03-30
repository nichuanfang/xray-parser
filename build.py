#!/usr/bin/python3
# coding=utf-8”；

# webhook触发更新路由规则
import json
import os



with open('routing.json') as routing_file:
    routing = json.load(routing_file)

with open('dns.json') as dns_file:
    dns = json.load(dns_file)

inbounds = []
# 构建inbounds   文件夹路径 文件夹集合 文件集合
for dir_path,dir_list,file_list in os.walk('inbounds'):
    for file in file_list:
        with open(dir_path+'/'+file) as inbound_file:
            inbounds.append(json.load(inbound_file))

# 拼到client中 
with open('server.json') as server_file:
    server = json.load(server_file)

# 配置路由
server['routing'] = routing
# 配置dns
server['dns'] = dns

server['inbounds'] = inbounds

# 持久化
json.dump(server,open('/root/assets/config/server/config.json','w+'))