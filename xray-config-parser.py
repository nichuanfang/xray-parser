#!/usr/bin/python3
# coding=utf-8”；
import json
from tkinter.messagebox import NO
from urllib import request
from entity.QxPolicy import QxPolicy
from entity.XrayPolicy import XrayPolicy
import logging

logging.getLogger().setLevel(logging.INFO)
logging.info("==========开始更新xray配置文件==============")

# 自定义分流规则
# https://ghproxy.com/https://raw.githubusercontent.com/nichuanfang/config-server/master/QX/MyPolicy.list
url = request.urlopen(
    "https://raw.githubusercontent.com/nichuanfang/config-server/master/QX/MyPolicy.list"
)
configPath: str = "D:\soft\Xray-windows-64\config.json"
# 读取xray配置文件config.json
config = open(configPath, "r")
res: dict = json.load(config)
config.close()
routing: dict = res.get("routing")
routingrules: list = routing.get("rules")

# 每次都从更新第1条之后 以及倒数第二条之前 中间的数据

myPolicy: str = url.read().decode()

lines: list = myPolicy.splitlines()

# 缓存lines的域名 移除会用到
cachedDomains: list = []
for item in lines:
    if item != "" and not item.startswith("#"):
        arr = item.split(",")
        cachedDomains.append(arr.__getitem__(1))

for item in lines:
    if item != "" and not item.startswith("#"):

        arr = item.split(",")
        # 封装成规则对象
        qx = QxPolicy(arr.__getitem__(0), arr.__getitem__(1),
                      arr.__getitem__(2))
        # 追加到本地的config.json中 当前目录
        # 格式化qx
        outboundTag = "direct"
        # 处理outboundTag
        if qx.policy.strip().upper() == "DIRECT":
            outboundTag = "direct"
        elif qx.policy.strip().upper() == "PROXY":
            outboundTag = "proxy"
        elif qx.policy.strip().upper() == "REJECT":
            outboundTag = "block"
        # 针对pikpak的策略 默认为proxy
        elif qx.policy.strip().upper() == "Pikpak":
            outboundTag = "proxy"
        # 其他策略默认为代理
        else:
            outboundTag = "proxy"
        # 处理domain
        domain: list = []
        if qx.typeOf == "HOST":
            domain.append("full:" + qx.path)
            pass
        elif qx.typeOf == "HOST-SUFFIX":
            domain.append(qx.path)

        xray = XrayPolicy("field", outboundTag, domain)
        # 代表不包含该域名
        flag: bool = False
        for rule in routingrules:
            domain: list = rule.get("domain")
            if domain == xray.domain:
                rule.__setitem__("outboundTag", xray.outboundTag)
                flag = True
            # 遍历domain 如果该domain的域名在自定义规则集中没有 则移除
            if domain is None:
                continue
            for url in domain:
                if url != "geosite:category-ads-all" and url != "geosite:gfw" and url != "geosite:greatfire" and url != "geoip:telegram":
                    if url.startswith("full:"):
                        url = url.replace("full:", "")
                    if url not in cachedDomains:
                        routingrules.remove(rule)

        if not flag:
            routingrules.insert(routingrules.__len__() - 3, xray.__dict__)

# 更新脚本文件
routing.update(rules=routingrules)
res.update(routing=routing)
config = open(configPath, "w+")
# ensure_ascii=False防止中文乱码
json.dump(res, config, ensure_ascii=False)
config.close()
logging.info("==========xray配置文件更新完毕!==============")
sleep(2)
