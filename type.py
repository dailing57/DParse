Epsilon = '__Epsilon__'
Dollar = '__Dollar__'
START = '__START__'


class Production:
    def __init__(self, left: str, right: tuple, reduce=None) -> None:
        self.left: str = left
        self.right: tuple = right
        self.reduce = reduce

    def __hash__(self) -> int:
        return hash((self.left, self.right))

    def __eq__(self, __o: object) -> bool:
        return (self.left, self.right) == (__o.left, __o.right)

    def __ne__(self, __o: object) -> bool:
        return not(self == __o)


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
