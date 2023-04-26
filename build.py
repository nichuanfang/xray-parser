#!/usr/local/bin/python
# coding=utf-8

# webhook触发更新路由规则
import json
import sys

# xray server ip
XRAY_IP = sys.argv[1]
# xray server domain
XRAY_DOMAIN = sys.argv[2]
# xray uuid for windows
XRAY_WINDOWS_KEY = sys.argv[3]
# trojan fallback for qx
XRAY_TROJAN_KEY = sys.argv[4]

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
client['outbounds'][0]['settings']['vnext'][0]['address'] = XRAY_IP
client['outbounds'][0]['settings']['vnext'][0]['users'][0]['id'] = XRAY_WINDOWS_KEY
client['outbounds'][0]['streamSettings']['tlsSettings']['serverName'] = XRAY_DOMAIN

# 持久化
json.dump(client,open('dist/config.json','w+'))

# 生成trojan配置文件
with open('dist/trojan.txt','w+') as trojan:
    trojan.writelines(f'trojan={XRAY_DOMAIN}:16789, password={XRAY_TROJAN_KEY}, over-tls=true, tls-verification=true, fast-open=false, udp-relay=false, tag=dogyun')


outbound_tag_map = {
    'direct': 'DIRECT',
    'block': 'REJECT',
    'proxy': 'PROXY'
}

# 转化为QX的路由配置文件
with open('dist/policy.list','w+') as qx:
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

# 转化为QX的路由配置文件
with open('dist/policy.txt','w+') as qx_preview:
    for rule in rb['rules']:
        # 把规则写到list里
        outboundTag:str = rule['outboundTag']
        # HOST-SUFFIX,1688.com,DIRECT
        domains:list = rule['domain']
        for domain in domains:
            if domain.startswith('full:'):
                qx_preview.writelines('HOST,'+(domain[5:]+',')+(outbound_tag_map[outboundTag.lower()])+'\n')
            else:
                qx_preview.writelines('HOST-SUFFIX,'+(domain+',')+(outbound_tag_map[outboundTag.lower()])+'\n')
