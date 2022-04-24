from typing import Generator
from DLex.lexer import Token
from .type import ParserConfig, Production, Dollar
from .LRdfa import LRDFA


class LRParser:
    def __init__(self, config: ParserConfig) -> None:
        self.hooks = config.hooks
        self.dfa = LRDFA(config=config)
        self.action = self.dfa.Action
        self.goto = self.dfa.Goto

    def run(self, tokens: Generator, *args: list):
        if self.hooks is not None and self.hooks.beforeCreated is not None:
            self.hooks.beforeCreated(*args)
        curCh: Token = next(tokens)
        stk = [0]
        val = [None]
        while True:
            state = stk[-1]
            if curCh.type in self.action[state]:
                act = self.action[state][curCh.type]
                if type(act) == int:
                    stk.append(act)
                    val.append(curCh)
                    curCh = next(tokens)
                elif type(act) == Production:
                    arg = []
                    for i in range(len(act.right)):
                        stk.pop()
                        arg.append(val.pop())
                    state = self.goto[stk[-1]][act.left]
                    stk.append(state)
                    arg.reverse()
                    val.append(act.reduce(*arg)
                               if act.reduce is not None else None)
                elif act == 'Accepted':
                    break
            else:
                return False, curCh
        if self.hooks is not None and self.hooks.created is not None:
            ok = True
            value = self.hooks.created(val[1], *args)
            return ok, value
        else:
            ok = True
            value = val[1]
            return ok, value

    def parse(self, tokens: Generator or list[Token], *args: list):
        def gen():
            yield from tokens
            EOF = Token(type=Dollar, value=Dollar, col=-1, row=-1)
            while True:
                yield EOF
        return self.run(gen(), *args)
