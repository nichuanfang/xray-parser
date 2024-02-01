# !/usr/local/bin/python
# coding=utf-8；
# 构建reality
# !/usr/local/bin/python
# coding=utf-8；
# 构建reality

# !/usr/local/bin/python
# coding=utf-8；
# 构建reality
# !/usr/local/bin/python
# coding=utf-8；
# 构建reality
import json
import logging
import os
import random
import re

import yaml

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)


def generate_trojan_password():
	"""生成trojan密码 8位随机数 数据来源0123456789abcdefghijklmnopqrstuvwxyz
	"""
	return ''.join(random.sample('0123456789abcdefghijklmnopqrstuvwxyz', 8))


def handle_port(vless_port: str, trojan_port: str):
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
	with open('../docker-compose.yml', 'rb') as docker_compose_file:
		docker_compose: dict = yaml.load(docker_compose_file, yaml.FullLoader)
		# 替换docker-compose.yml中的端口配置
		docker_compose['services']['xray-reality']['ports'] = \
			[f'{vless_port}:{vless_port}', f'{trojan_port}:{trojan_port}']
	with open('../docker-compose.yml', 'wb') as docker_compose_file:
		# 保存 sort_keys=False 默认为True 会改变原文件字典的顺序
		yaml.dump(docker_compose, docker_compose_file,
		          encoding='utf-8', allow_unicode=True, sort_keys=False)


def verify_dest_server_names(VLESS_DEST: str, handled_server_names: list):
	logging.info(
		'======================校验dest与serverNames========================================')
	tls_ping_list = os.popen(f'./xray tls ping {VLESS_DEST}').readlines()
	match_res = None
	for tls_ping in tls_ping_list:
		match_res = re.match('^Allowed domains: .+$', tls_ping)
		if match_res is None:
			continue
		else:
			# Allowed domains:  [s0.awsstatic.com]
			res = match_res.string.split('[')[1].split(']')[0]
			if res != '':
				server_names = res.split(' ')
				if set(handled_server_names).issubset(server_names):
					logging.info(
						'======================dest与serverNames匹配!===================================')
				else:
					logging.error(
						'======================dest与serverNames不匹配!===================================')
					raise RuntimeError
			# 只需校验第一个serverNames即可
			break
	
	if match_res is None:
		logging.error(
			f'======================目标域名{VLESS_DEST}不可用!===================================')
		raise RuntimeError


def getEnv(env: str):
	v = os.environ.get(env)
	if v is None:
		raise RuntimeError(f'环境变量{env}未配置!')
	return v


# 创建配置 如果修改了默认端口（vless:8443  trojan: 16789） 需要同步docker项目的docker-compose.yml 同时部署xray的服务器需要开放更新的两个端口！


def create_config():
	uuid_list = os.popen('./xray uuid').readlines()
	
	# xray生成的uuid
	uuid = uuid_list[0][:-1]
	
	logging.info('xray服务端配置项: ')
	logging.info(
		'=================================================================')
	logging.info('  密钥(secrets): ')
	logging.info('  变量(vars): ')
	logging.info('    VLESS_PORT: vless端口 ')
	logging.info('    TROJAN_PORT: trojan端口 ')
	logging.info(
		'=================================================================')
	# xray uuid
	VLESS_UUID = uuid
	# trojan密码  ios最佳实践  使用QX trojan协议
	TROJAN_PASSWORD = generate_trojan_password()
	# vless端口
	VLESS_PORT = getEnv('VLESS_PORT')
	# trojan端口
	TROJAN_PORT = getEnv('TROJAN_PORT')
	# 处理端口非默认值的情况
	handle_port(VLESS_PORT, TROJAN_PORT)
	
	inbounds = []
	# 构建inbounds   文件夹路径 文件夹集合 文件集合
	for dir_path, dir_list, file_list in os.walk('inbounds'):
		for file in file_list:
			with open(dir_path + '/' + file) as inbound_file:
				server_dict: dict = json.load(inbound_file)
				if file[:-5] == 'windows':
					try:
						server_dict['port'] = int(VLESS_PORT)
					except:
						raise RuntimeError('vars.VLESS_PORT必须为整数!')
					# 添加密钥
					server_dict['settings']['clients'][0]['id'] = VLESS_UUID
				elif file[:-5] == 'trojan':
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
	json.dump(server, open(f'dist/config.json', 'w+'))


logging.info('========================生成基础配置========================')
# 生成基础配置
create_config()
logging.info(
	'========================服务器配置配置构建完成!==================================')
