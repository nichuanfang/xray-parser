#!/usr/local/bin/python
# coding=utf-8；

import json
import logging
import os
import sys
import random 
import yaml
import re

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)


def generate_short_id():
    """生成short_id  8-16位随机数 数据来源0123456789abcdef
    """  
    return ''.join(random.sample('0123456789abcdef',16))
    pass

def generate_trojan_password():
    """生成trojan密码 8位随机数 数据来源0123456789abcdefghijklmnopqrstuvwxyz
    """    
    return ''.join(random.sample('0123456789abcdefghijklmnopqrstuvwxyz',8))

def handle_port(vless_port:str,trojan_port:str):
    """处理端口非默认值的情况

    Args:
        vless_port (str): vless端口
        trojan_port (str): trojan端口
    """    
    try:
        int(vless_port)
    except:
        logging.error(f'vless端口必须是整数!')
        raise RuntimeError
    try:
        int(trojan_port)
    except:
        logging.error(f'trojan端口必须是整数!')
        raise RuntimeError
    # ../docker-compose.yml
    with open('../docker-compose.yml','rb') as docker_compose_file: 
        docker_compose:dict = yaml.load(docker_compose_file,yaml.FullLoader)
        # 替换docker-compose.yml中的端口配置
        docker_compose['services']['xray-reality']['ports'] =  \
        [f'{vless_port}:{vless_port}',f'{trojan_port}:{trojan_port}']
    with open('../docker-compose.yml','wb') as docker_compose_file:
        # 保存 sort_keys=False 默认为True 会改变原文件字典的顺序
        yaml.dump(docker_compose,docker_compose_file,encoding='utf-8',allow_unicode=True,sort_keys=False)

def verify_dest_server_names(VLESS_DEST:str,handled_server_names:list):
    logging.info('======================校验dest与serverNames========================================')
    tls_ping_list = os.popen(f'./xray tls ping {VLESS_DEST}').readlines()
    match_res = None
    for tls_ping in tls_ping_list:
        match_res = re.match('^Allowed domains: .+$',tls_ping)
        if match_res is None:
            continue
        else:
            # Allowed domains:  [s0.awsstatic.com]
            res = match_res.string.split('[')[1].split(']')[0]
            if res != '':
                server_names = res.split(' ')
                if set(handled_server_names).issubset(server_names):
                    logging.info('======================dest与serverNames匹配!===================================')
                else:
                    logging.error('======================dest与serverNames不匹配!===================================')
                    raise RuntimeError
            # 只需校验第一个serverNames即可
            break

    if match_res is None:
        logging.error(f'======================目标域名{VLESS_DEST}不可用!===================================')
        raise RuntimeError

def get_assert_arg(index:int,msg:str):
        try:
            return sys.argv[index]
        except:
            raise RuntimeError(msg)



# 创建配置 如果修改了默认端口（vless:443  trojan: 16789） 需要同步docker项目的docker-compose.yml 同时部署xray的服务器需要开放更新的两个端口！
def create_config():
    uuid_list = os.popen('./xray uuid').readlines()
    x25519_list = os.popen('./xray x25519').readlines()

    # xray生成的uuid
    uuid = uuid_list[0][:-1]
    # xray生成的私钥
    private_key = x25519_list[0][13:][:-1]

    logging.info('xray服务端配置项: ')
    logging.info('=================================================================')
    logging.info('  密钥(secrets): ')
    logging.info('  变量(vars): ')
    logging.info('    VLESS_DEST: xray的目标域名')
    logging.info('    VLESS_SERVER_NAMES: 逗号分割的，VLESS_DEST允许的服务列表 ')
    logging.info('    VLESS_PORT: vless端口 ')
    logging.info('    TROJAN_PORT: trojan端口 ')
    logging.info('=================================================================')
    # 读取参数 
    if len(sys.argv) < 4:
        raise RuntimeError('请确认xray相关变量与密钥都已配置!')

    # xray uuid
    VLESS_UUID = uuid
    # xray的目标域名
    VLESS_DEST = get_assert_arg(1,'vars.VLESS_DEST: 目标域名未配置！')
    # 逗号分割的，{VLESS_DEST}允许的服务列表 
    VLESS_SERVER_NAMES = get_assert_arg(2,'vars.VLESS_SERVER_NAMES: dest对应的服务列表未配置!')
    unhandled_server_names = VLESS_SERVER_NAMES.split(',')
    handled_server_names = []
    # 去空格
    for server_name in unhandled_server_names:
        handled_server_names.append(server_name.replace('\'','').replace('\"','').strip())
    verify_dest_server_names(VLESS_DEST,handled_server_names)
    # vless通过xray x25519生成的密钥对的私钥 客户端必须与之对应
    VLESS_PRIVATE_KEY = private_key
    # windows平台的shortId 8-16位随机数 数据来源0123456789abcdef
    VLESS_WINDOWS_SHORT_ID = generate_short_id()
    # ios平台的shortId  8-16位随机数 数据来源0123456789abcdef
    VLESS_IOS_SHORT_ID = generate_short_id()
    # trojan密码  ios最佳实践  使用QX trojan协议 
    TROJAN_PASSWORD = generate_trojan_password()
    # vless端口
    VLESS_PORT = get_assert_arg(3,'vars.VLESS_PORT: vless端口未配置!')
    # trojan端口
    TROJAN_PORT = get_assert_arg(4,'vars.TROJAN_PORT: trojan端口未配置!')
    # 处理端口非默认值的情况
    handle_port(VLESS_PORT,TROJAN_PORT)

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
                        raise RuntimeError('vars.VLESS_PORT必须为整数!')
                    # 添加密钥
                    server_dict['settings']['clients'][0]['id'] = VLESS_UUID
                    server_dict['streamSettings']['realitySettings']['dest'] = VLESS_DEST
                    server_dict['streamSettings']['realitySettings']['serverNames'] = handled_server_names
                    server_dict['streamSettings']['realitySettings']['privateKey'] = VLESS_PRIVATE_KEY
                    server_dict['streamSettings']['realitySettings']['shortIds'] = [VLESS_WINDOWS_SHORT_ID,VLESS_IOS_SHORT_ID]
                elif file[:-5]=='trojan':
                    try: 
                        server_dict['port'] = int(TROJAN_PORT)
                    except:
                        raise RuntimeError('vars.TROJAN_PORT必须为整数!')
                    # 添加密钥
                    server_dict['settings']['clients'][0]['password'] = TROJAN_PASSWORD
                inbounds.append(server_dict) 

    # 拼到client中 
    with open(f'server.json') as server_file:
        server = json.load(server_file)

    server['inbounds'] = inbounds
    # 持久化
    json.dump(server,open(f'dist/config.json','w+'))

# 更新配置
def update_config():
    # xray的目标域名
    VLESS_DEST = get_assert_arg(1,'vars.VLESS_DEST: 目标域名未配置！')
    # 逗号分割的，{VLESS_DEST}允许的服务列表 
    VLESS_SERVER_NAMES = get_assert_arg(2,'vars.VLESS_SERVER_NAMES: dest对应的服务列表未配置!')
    unhandled_server_names = VLESS_SERVER_NAMES.split(',')
    handled_server_names = []
    # 去空格
    for server_name in unhandled_server_names:
        handled_server_names.append(server_name.replace('\'','').replace('\"','').strip())
    # 校验dest与serverNames是否匹配
    verify_dest_server_names(VLESS_DEST.split(':')[0],handled_server_names)
    # vless端口
    VLESS_PORT = get_assert_arg(3,'vars.VLESS_PORT: vless端口未配置!')
    # trojan端口
    TROJAN_PORT = get_assert_arg(4,'vars.TROJAN_PORT: trojan端口未配置!')
    # 处理端口
    handle_port(VLESS_PORT,TROJAN_PORT)
    with open('../config/config.json','rb') as config_file:
        server_config:dict = json.load(config_file) 
        logging.info(f'=============更新前的配置信息：{json.dumps(server_config)}===============')
        inbounds:list = server_config['inbounds']
        for inbound in inbounds:
            if inbound['protocol'] == 'vless':
                inbound['port'] = VLESS_PORT
                inbound['streamSettings']['realitySettings']['dest'] = 's0.awsstatic.com:443'
                inbound['streamSettings']['realitySettings']['serverNames'] = handled_server_names
            else:
                inbound['port'] = TROJAN_PORT
    logging.info(f'=============更新后的配置信息：{json.dumps(server_config)}===============')

    raise RuntimeError
    with open('../config/config.json','wb') as config_file:

        pass
    


# 判断dockerfile/xray下面有没有config.json 文件 有的话直接读取配置 没有就生成
server_config:dict = {}
try:
    config_file_list = os.popen('ls ../config').readlines()
except:
    logging.info('config文件夹为空')
    config_file_list:dict = []

if len(config_file_list) == 0:
    logging.info('========================服务器配置文件不存在,生成基础配置========================')
    # 生成基础配置
    create_config()
    logging.info('========================服务器配置配置构建完成!==================================')
else:
    logging.info('========================服务器配置文件已存在,开始更新配置=========================')
    # 更新配置
    update_config()
    logging.info('========================服务器配置配置更新完成!==================================')