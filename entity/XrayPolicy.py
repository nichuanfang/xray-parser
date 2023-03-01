# xray 路由规则实体


class XrayPolicy:
    # 类型 默认为field
    type: str
    # 出站策略 block(阻断) direct(直连) proxy(代理)
    outboundTag: str
    # 域名规则 如果qx是HOST模式 domain为 `full:全域名` 如果qx模式为HOST-SUFFIX domain为`子域名`
    domain: list

    def __init__(self, type: str, outboundTag: str, domain: list) -> None:
        self.type = type
        self.outboundTag = outboundTag
        self.domain = domain
