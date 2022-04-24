from .type import *
from .LRParser import LRParser
from DLex.lexer import Token
config = ParserConfig(
    start='S',
    tokens=['c', 'd'],
    types=['S', 'C'],
    productions=[
        ProductionRule(
            left='S',
            right=[
                ProductionRightRule(
                    rule=['C', 'C'],
                    reduce=(lambda l, r:l+r))
            ]
        ),
        ProductionRule(
            left='C',
            right=[
                ProductionRightRule(
                    rule=['c', 'C'],
                    reduce=(lambda token, C:1+C)
                ),
                ProductionRightRule(
                    rule=['d'],
                    reduce=(lambda a:0)
                )
            ]
        ),
    ]
)
parser = LRParser(config)
print(len(parser.dfa.items))
print(parser.dfa.items)
print(parser.parse([
    Token(type='c', value='c', row=0, col=1),
    Token(type='c', value='c', row=0, col=2),
    Token(type='c', value='c', row=0, col=3),
    Token(type='d', value='d', row=0, col=4),
    Token(type='c', value='c', row=0, col=5),
    Token(type='d', value='d', row=0, col=6),
]))

print(parser.parse([Token(type='c', value='c', row=0, col=1)]))
print(parser.parse([
    Token(type='d', value='d', row=0, col=1),
    Token(type='d', value='d', row=0, col=2),
    Token(type='d', value='d', row=0, col=3),
]))
