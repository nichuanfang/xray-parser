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

    def get_env(env: str):
        res = os.environ.get(env)
        if res == None:
            raise RuntimeError(f'环境变量{env}未配置!')
        return res

    def get_uuid(server_config: dict, vless_inbound: dict):
        """获取uuid

        Args:
            server_config 服务器配置
            vless_inbound  vless配置
        """
        return vless_inbound['settings']['clients'][0]['id']

    def get_vless_port(server_config: dict, vless_inbound: dict):
        """获取vless端口

        Args:
            server_config (dict): 服务器配置
            vless_inbound (dict): vless配置

        Returns:
            _type_: 端口号
        """
        return vless_inbound['port']

    def get_trojan_password(server_config: dict, trojan_inbound: dict):
        """获取trojan密码

        Args:
            server_config (dict): 服务器配置
            trojan_inbound (dict): trojan配置

        Returns:
            _type_: 密码
        """
        return trojan_inbound['settings']['clients'][0]['password']

    def get_trojan_port(server_config: dict, trojan_inbound: dict):
        """获取trojan端口号

        Args:
            server_config (dict): 服务器配置
            trojan_inbound (dict): trojan配置

        Returns:
            _type_: 端口号
        """
        return trojan_inbound['port']

    # 从config.json中读取配置
    with open('../config/config.json', 'rb') as config_file:
        server_config: dict = json.load(config_file)
        inbounds: list = server_config['inbounds']
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
        DC_DOMAIN = get_env('VPS_DOMAIN')
        # xray服务器的IP
        DC_HOST = get_env('VPS_HOST')
        # xray uuid
        VLESS_UUID = get_uuid(server_config, vless_inbound)
        # vless端口
        VLESS_PORT = get_vless_port(server_config, vless_inbound)
        # trojan密码  ios最佳实践  使用QX trojan协议
        TROJAN_PASSWORD = get_trojan_password(server_config, trojan_inbound)
        # trojan端口
        TROJAN_PORT = get_trojan_port(server_config, trojan_inbound)

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
        client['routing'] = {'domainStrategy': strategy, 'rules': rules}

        # 生成window平台的config.json
        client['outbounds'][0]['settings']['vnext'][0]['address'] = DC_HOST
        client['outbounds'][0]['settings']['vnext'][0]['port'] = int(
            VLESS_PORT)
        client['outbounds'][0]['settings']['vnext'][0]['users'][0]['id'] = VLESS_UUID
        # 持久化
        json.dump(client, open('dist/client-windows-config.json', 'w+'))
        # 生成ios平台的config.json
        json.dump(client, open('dist/client-ios-config.json', 'w+'))

        # 生成trojan配置文件
        with open('dist/trojan.txt', 'w+') as trojan:
            trojan.writelines(
                f'trojan={DC_DOMAIN}:{TROJAN_PORT}, password={TROJAN_PASSWORD}, over-tls=true, tls-verification=true, fast-open=false, udp-relay=false, tag=mysub')


# 判断服务端配置是否存在 不存在直接中止构建
server_config: dict = {}
try:
    config_file_list = os.popen('cat ../config/config.json').readlines()
except:
    logging.info('config服务端配置为空!!!')
    config_file_list: dict = []

if len(config_file_list) == 0:
    logging.error(
        '========================服务器配置文件不存在中止构建========================')
else:
    logging.info('========================开始更新客户端配置=========================')
    # 更新配置
    update_config()
    logging.info(
        '========================服务器配置配置更新完成!==================================')
