#!/usr/bin/python3
# coding=utf-8”；

# webhook触发更新路由规则
import json


# 构建完成后 同步到qx的路由规则里
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
    strategy = rb['domainStrategy']

for frule in rf['rules']:
    rules.append(frule)

with open('dns.json') as dns_file:
    dns = json.load(dns_file)

# 拼到client中 
with open('client.json') as client_file:
    client = json.load(client_file)

# 配置路由
client['routing'] = {'domainStrategy': strategy,'rules': rules}
# 配置dns
client['dns'] = dns

# 持久化
json.dump(client,open('/root/assets/config/client/config.json','w+'))

outbound_tag_map = {
    'direct': 'DIRECT',
    'block': 'REJECT',
    'proxy': 'PROXY'
}


# 转化为QX的路由配置文件
with open('/root/assets/config/client/QxPolicy.list','w+') as qx:
    for rule in rb['rules']:
        # 把规则写到list里
        outboundTag:str = rule['outboundTag']
        # HOST-SUFFIX,1688.com,DIRECT
        domains:list = rule['domain']
        for domain in domains:
            if domain.startswith('full:'):
                qx.writelines('HOST,'+(domain[5:]+',')+(outbound_tag_map[outboundTag.lower()])+'\n')
            else:
                qx.writelines('HOST-SUFFIX,'+(domain+',')+(outbound_tag_map[outboundTag.lower()])+'\n')