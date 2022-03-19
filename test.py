
import json


class Production:
    def __init__(self, left: str, right: list, reduce=None) -> None:
        self.left: str = left
        self.right: list = right
        self.reduce = reduce
        self.st = set()


p = Production(left='s', right=[1], reduce=(lambda val: val))
mp: dict[Production, list[Production]] = {}
mp[p] = [p]
if p in mp:
    print(p)
