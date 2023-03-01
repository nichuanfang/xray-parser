# qx规则


class QxPolicy:
    #HOST or HOST-SUFFIX etc.
    typeOf: str
    # Match route
    path: str
    #  policy should obey
    policy: str

    def __init__(self, typeOf=str, path=str, policy=str) -> None:
        self.typeOf = typeOf
        self.path = path
        self.policy = policy
