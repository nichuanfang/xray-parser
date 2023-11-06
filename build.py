#!/usr/local/bin/python
# coding=utf-8

import json
import logging
import os
import sys

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)

def update_config():
    logging.info('xray客户端配置项: ')
    logging.info('=================================================================')
    logging.info('  密钥(secrets): ')
    logging.info('    DC_DOMAIN: xray服务端的域名')
    logging.info('    DC_HOST: xray服务端的ip')
    logging.info('  变量(vars): ')
    logging.info('    VLESS_CLIENT_SERVER_NAME: xray客户端选用的服务域名')
    logging.info('=================================================================')
    # 读取参数 
    if len(sys.argv) < 4:
        raise RuntimeError('请确认xray相关变量与密钥都已配置!')

    def get_assert_arg(index:int,msg:str):
        try:
            return sys.argv[index]
        except:
            raise RuntimeError(msg)
        
    def get_uuid(server_config:dict,vless_inbound:dict):
        """获取uuid

        Args:
            server_config 服务器配置
            vless_inbound  vless配置
        """        
        return vless_inbound['settings']['clients'][0]['id']
    
    def generate_public_key(server_config:dict,vless_inbound:dict):
        """生成公钥

        Args:
            server_config (dict): 服务器配置
            vless_inbound (dict): vless配置

        Raises:
            RuntimeError: _description_

        Returns:
            _type_: 公钥
        """        
        logging.info('==================通过私钥生成公钥==========================')
        try:
            # 获取私钥
            private_key = vless_inbound['streamSettings']['realitySettings']['privateKey']
            public_key = os.popen(f'./xray x25519 -i {private_key}').readlines()[1][12:][:-1]
        except Exception as e:
            logging.error(f'==================公钥生成失败:{e.__str__()}==============================')
            raise RuntimeError
        logging.info('==================公钥已生成！==============================')
        return public_key


    def get_windows_short_id(server_config:dict,vless_inbound:dict):
        """获取windows的shortId

        Args:
            server_config (dict): 服务器配置
            vless_inbound (dict): vless配置

        Returns:
            _type_:shortId
        """        
        return vless_inbound['streamSettings']['realitySettings']['shortIds'][0]
    
    def get_ios_short_id(server_config:dict,vless_inbound:dict):
        """获取ios的shortId

        Args:
            server_config (dict): 服务器配置
            vless_inbound (dict): vless配置

        Returns:
            _type_:shortId
        """        
        return vless_inbound['streamSettings']['realitySettings']['shortIds'][1]
    
    def get_vless_port(server_config:dict,vless_inbound:dict):
        """获取vless端口

        Args:
            server_config (dict): 服务器配置
            vless_inbound (dict): vless配置

        Returns:
            _type_: 端口号
        """        
        return vless_inbound['port']
    
    def get_trojan_password(server_config:dict,trojan_inbound:dict):
        """获取trojan密码

        Args:
            server_config (dict): 服务器配置
            trojan_inbound (dict): trojan配置

        Returns:
            _type_: 密码
        """        
        return trojan_inbound['settings']['clients'][0]['password']
    
    def get_trojan_port(server_config:dict,trojan_inbound:dict):
        """获取trojan端口号

        Args:
            server_config (dict): 服务器配置
            trojan_inbound (dict): trojan配置

        Returns:
            _type_: 端口号
        """        
        return trojan_inbound['port']

    # 从config.json中读取配置
    with open('../config/config.json','rb') as config_file:
        server_config:dict = json.load(config_file)
        inbounds:list = server_config['inbounds']
        vless_inbound = {}
        trojan_inbound = {}
        for inbound in inbounds:
            if inbound['protocol'] == 'vless':
                vless_inbound = inbound
            elif inbound['protocol'] == 'trojan':
                trojan_inbound = inbound
        if vless_inbound == {}:
            raise RuntimeError('服务器配置错误!未发现vless配置')
        if trojan_inbound == {}:
            raise RuntimeError('服务器配置错误!未发现trojan配置')
        # xray服务器的域名
        DC_DOMAIN = get_assert_arg(1,'secrets.DC_DOMAIN: xray服务器的域名未配置!')
        # xray服务器的IP
        DC_HOST = get_assert_arg(2,'secrets.DC_HOST: xray服务器的IP未配置!')
        # xray uuid
        VLESS_UUID = get_uuid(server_config,vless_inbound)
        # 客户端使用的服务域名
        VLESS_CLIENT_SERVER_NAME = get_assert_arg(3,'vars.VLESS_CLIENT_SERVER_NAME: 客户端使用的服务域名未配置!')
        # 校验服务域名是否可用
        #verify_client_server_name(VLESS_CLIENT_SERVER_NAME,server_config,vless_inbound)
        # vless通过xray x25519生成的密钥对的公钥 服务端必须与之对应
        VLESS_PUBLIC_KEY = generate_public_key(server_config,vless_inbound)
        # windows平台的shortId 8-16位随机数 数据来源0123456789abcdef
        VLESS_WINDOWS_SHORT_ID = get_windows_short_id(server_config,vless_inbound)
        # ios平台的shortId  8-16位随机数 数据来源0123456789abcdef
        VLESS_IOS_SHORT_ID = get_ios_short_id(server_config,vless_inbound)
        # vless端口
        VLESS_PORT = get_vless_port(server_config,vless_inbound)
        # trojan密码  ios最佳实践  使用QX trojan协议 
        TROJAN_PASSWORD = get_trojan_password(server_config,trojan_inbound)
        # trojan端口
        TROJAN_PORT = get_trojan_port(server_config,trojan_inbound)

        # 构建完成后 同步到qx的路由规则里
        rules = []

        with open('routing/routing_header.json') as routing_header:
            rh = json.load(routing_header)

        with open('routing/routing_body.json') as routing_body:
            rb = json.load(routing_body)

        with open('routing/routing_footer.json') as routing_footer:
            rf = json.load(routing_footer)


        for hrule in rh['rules']:
            rules.append(hrule)

        for brule in rb['rules']:
            rules.append(brule)
            strategy = rb['domainStrategy']

        for frule in rf['rules']:
            rules.append(frule)

        # 拼到client中 
        with open('client.json') as client_file:
            client = json.load(client_file)

        # 配置路由
        client['routing'] = {'domainStrategy': strategy,'rules': rules}

        # 生成window平台的config.json
        client['outbounds'][0]['settings']['vnext'][0]['address'] = DC_HOST
        client['outbounds'][0]['settings']['vnext'][0]['port'] = int(VLESS_PORT)
        client['outbounds'][0]['settings']['vnext'][0]['users'][0]['id'] = VLESS_UUID
        client['outbounds'][0]['streamSettings']['realitySettings']['serverName'] = VLESS_CLIENT_SERVER_NAME
        client['outbounds'][0]['streamSettings']['realitySettings']['publicKey'] = VLESS_PUBLIC_KEY
        client['outbounds'][0]['streamSettings']['realitySettings']['shortId'] = VLESS_WINDOWS_SHORT_ID
        client['outbounds'][0]['streamSettings']['realitySettings']['spiderX'] = '/windows'
        # 持久化
        json.dump(client,open('dist/client-windows-config.json','w+'))
        # 生成ios平台的config.json
        client['outbounds'][0]['streamSettings']['realitySettings']['shortId'] = VLESS_IOS_SHORT_ID
        client['outbounds'][0]['streamSettings']['realitySettings']['spiderX'] = '/ios'
        # 持久化
        json.dump(client,open('dist/client-ios-config.json','w+'))

        # 生成trojan配置文件
        with open('dist/trojan.txt','w+') as trojan:
            trojan.writelines(f'trojan={DC_HOST}:{TROJAN_PORT}, password={TROJAN_PASSWORD}, over-tls=true, tls-verification=true, fast-open=false, udp-relay=false, tag=mysub')


# 判断服务端配置是否存在 不存在直接中止构建
server_config:dict = {}
try:
    config_file_list = os.popen('cat ../config/config.json').readlines()
except:
    logging.info('config服务端配置为空!!!')
    config_file_list:dict = []

if len(config_file_list) == 0:
    logging.error('========================服务器配置文件不存在中止构建========================')
else:
    logging.info('========================开始更新客户端配置=========================')
    # 更新配置
    update_config()
    logging.info('========================服务器配置配置更新完成!==================================')
