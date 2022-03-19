Epsilon = '__Epsilon__'
Dollar = '__Dollar__'
START = '__START__'


class Production:
    def __init__(self, left: str, right: list, reduce=None) -> None:
        self.left: str = left
        self.right: list = right
        self.reduce = reduce


class ProductionRightRule:
    def __init__(self, rule: list[str], reduce=None) -> None:
        self.rule: list[str] = rule
        self.reduce = reduce


class ProductionRule:
    def __init__(self, left: str, right: list[ProductionRightRule]) -> None:
        self.left: str = left
        self.right: list[ProductionRightRule] = right


class ParserConfig:
    def __init__(self, start: str, tokens: list[str], types: list[str], productions: list[ProductionRule]) -> None:
        self.start: str = start
        self.tokens: list[str] = tokens
        self.types: list[str] = types
        self.productions: list[ProductionRule] = productions


class Error(Exception):
    def __init__(self, message=None):
        self.message = f'{self.__class__.__name__}: {message}'
