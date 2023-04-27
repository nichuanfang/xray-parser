#!/usr/local/bin/python
# coding=utf-8；

# webhook触发更新路由规则
import json
import logging
import os
import sys

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)

logging.info('xray配置项：')
logging.info('=================================================================')
logging.info('  密钥(secrets)：')
logging.info('    VLESS_UUID: xray uuid')
logging.info('    VLESS_DEST: xray的目标域名')
logging.info('    VLESS_PRIVATE_KEY: vless通过xray x25519生成的私钥')
logging.info('    VLESS_WINDOWS_SHORT_ID: windows平台的shortId，8-16位随机数 数据来源0123456789abcdef')
logging.info('    VLESS_IOS_SHORT_ID: ios平台的shortId，8-16位随机数 数据来源0123456789abcdef')
logging.info('    TROJAN_PASSWORD: trojan密码')
logging.info('  变量(vars)：')
logging.info('    VLESS_SERVER_NAMES: 逗号分割的，VLESS_DEST允许的服务列表 ')
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

inbounds = []
# 构建inbounds   文件夹路径 文件夹集合 文件集合
for dir_path,dir_list,file_list in os.walk('inbounds'):
    for file in file_list:
        with open(dir_path+'/'+file) as inbound_file:
            server_dict:dict = json.load(inbound_file)
            if file[:-5]=='windows':
                try:
                    server_dict['port'] = int(VLESS_PORT)
                except:
                    raise RuntimeError('vars.VLESS_PORT必须为整数！')
                # 添加密钥
                server_dict['settings']['clients'][0]['id'] = VLESS_UUID
                server_dict['streamSettings']['realitySettings']['dest'] = VLESS_DEST
                unhandled_server_names = VLESS_SERVER_NAMES.split(',')
                handled_server_names = []
                # 去空格
                for server_name in unhandled_server_names:
                    handled_server_names.append(server_name.replace('\'','').replace('\"','').strip())
                server_dict['streamSettings']['realitySettings']['serverNames'] = handled_server_names
                server_dict['streamSettings']['realitySettings']['privateKey'] = VLESS_PRIVATE_KEY
                server_dict['streamSettings']['realitySettings']['shortIds'] = [VLESS_WINDOWS_SHORT_ID,VLESS_IOS_SHORT_ID]
            elif file[:-5]=='trojan':
                try: 
                    server_dict['port'] = int(TROJAN_PORT)
                except:
                    raise RuntimeError('vars.TROJAN_PORT必须为整数！')
                # 添加密钥
                server_dict['settings']['clients'][0]['password'] = TROJAN_PASSWORD
            inbounds.append(server_dict) 

# 拼到client中 
with open(f'server.json') as server_file:
    server = json.load(server_file) 

server['inbounds'] = inbounds
# 持久化
json.dump(server,open(f'dist/config.json','w+'))