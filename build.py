#!/usr/bin/python3
# coding=utf-8”；

# webhook触发更新路由规则
import json


# 构建完成后 同步到qx的路由规则里
policy_file_path = '/root/code/config-server/QX/MyPolicy.list'

rules = []

with open('routing_header.json') as routing_header:
    rh = json.load(routing_header)

with open('routing_body.json') as routing_body:
    rb = json.load(routing_body)

with open('routing_footer.json') as routing_footer:
    rf = json.load(routing_footer)


for hrule in rh['rules']:
    rules.append(hrule)

for brule in rb['rules']:
    rules.append(brule)

for frule in rf['rules']:
    rules.append(frule)

# 拼到client中 
with open('client.json') as client_file:
    client = json.load(client_file)

client['routing'] = rules
print(client)