#!/usr/bin/python3
import urllib3

from urllib3.response import HTTPResponse

# 自定义分流规则
# https://ghproxy.com/https://raw.githubusercontent.com/nichuanfang/config-server/master/QX/MyPolicy.list
url = "https://ghproxy.com/https://raw.githubusercontent.com/nichuanfang/config-server/master/QX/MyPolicy.list"

print("downloading MyProxyConfig file with urllib3")

connection = urllib3.connection_from_url(url)

response = HTTPResponse(connection.request(method="GET", url=url, fields=None, headers=None))

print(response.data)