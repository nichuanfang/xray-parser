# 出站规则


class OutBounds:
    # 出站标签
    tag: str
    # 协议 freedom(直连) blackhole(阻断)  proxy(代理)
    protocol: str
    # 配置项 详情查看Project-X社区 https://xtls.github.io/en/
    settings: dict

    def __init__(self, tag: str, protocol: str, settings: dict) -> None:
        self.tag = tag
        self.protocol = protocol
        self.settings = settings
        pass
