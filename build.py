#!/usr/local/bin/python
# coding=utf-8

import json
import logging
import os
import sys

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)

logging.info('xray客户端配置项: ')
logging.info('=================================================================')
logging.info('  密钥(secrets): ')
logging.info('    HC_HOST: xray服务器的ip')
logging.info('    HC_HOST: xray服务器的域名')
logging.info('    VLESS_UUID: xray uuid')
logging.info('    VLESS_WINDOWS_SHORT_ID: WINDOWS客户端的shortId')
logging.info('    VLESS_IOS_SHORT_ID: IOS客户端的shortId')
logging.info('    TROJAN_PASSWORD: trojan的密码')

logging.info('  变量(vars): ')
logging.info('    VLESS_SERVER_NAMES: xray服务端选用的服务域名列表')
logging.info('    VLESS_CLIENT_SERVER_NAME: xray客户端选用的服务域名')
logging.info('    VLESS_WINDOWS_SPIDERX: xray windows客户端选用的爬虫初始路径，必须以/开始')
logging.info('    VLESS_IOS_SPIDERX: xray ios客户端选用的爬虫初始路径，必须以/开始')
logging.info('    VLESS_PORT: vless端口 ')
logging.info('    TROJAN_PORT: trojan端口 ')
logging.info('=================================================================')
# 读取参数 
if len(sys.argv) < 10:
    raise RuntimeError('请确认xray相关变量与密钥都已配置!')

def get_assert_arg(index:int,msg:str):
    try:
        return sys.argv[index]
    except:
        raise RuntimeError(msg)


# xray uuid
VLESS_UUID = get_assert_arg(1,'secrets.VLESS_UUID: xray uuid未配置！')
# xray的目标域名
VLESS_DEST = get_assert_arg(2,'vars.VLESS_DEST: 目标域名未配置！')
# 逗号分割的，{VLESS_DEST}允许的服务列表 
VLESS_SERVER_NAMES = get_assert_arg(3,'vars.VLESS_SERVER_NAMES: dest对应的服务列表未配置！')
# vless通过xray x25519生成的密钥对的私钥 客户端必须与之对应
VLESS_PRIVATE_KEY = get_assert_arg(4,'secrets.VLESS_PRIVATE_KEY: xray私钥未配置！')
# windows平台的shortId 8-16位随机数 数据来源0123456789abcdef
VLESS_WINDOWS_SHORT_ID = get_assert_arg(5,'secrets.VLESS_WINDOWS_SHORT_ID: window平台的shortId未配置！')
# ios平台的shortId  8-16位随机数 数据来源0123456789abcdef
VLESS_IOS_SHORT_ID = get_assert_arg(6,'secrets.VLESS_IOS_SHORT_ID: ios平台的shortId未配置！')
# trojan密码  ios最佳实践  使用QX trojan协议 
TROJAN_PASSWORD = get_assert_arg(7,'secrets.TROJAN_PASSWORD: trojan密码未配置！')
# vless端口
VLESS_PORT = get_assert_arg(8,'vars.VLESS_PORT: vless端口未配置！')
# trojan端口
TROJAN_PORT = get_assert_arg(9,'vars.TROJAN_PORT: trojan端口未配置！')

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
