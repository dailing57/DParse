import json
from .first import FirstSet
from .type import ParserConfig, Production, START, Epsilon, Dollar, Error


class dfaError(Error):
    pass


def groupBy(productions: list[Production]):
    mp: dict[str, list[Production]] = {}
    for it in productions:
        if it.left not in mp:
            mp[it.left] = [it]
        else:
            mp[it.left].append(it)
    return mp


class Item:
    def __init__(self, production, pos=0, lookup=Epsilon) -> None:
        self.production: Production = production
        self.pos: int = pos
        self.lookup: str = lookup

    def __hash__(self) -> int:
        return hash((self.production, self.pos, self.lookup))

    def __eq__(self, __o: object) -> bool:
        return self.production == __o.production and self.pos == __o.pos and self.lookup == __o.lookup

    def __str__(self) -> str:
        s = ' '.join([str(x) for x in [
                     *self.production.right[:self.pos], '.', *self.production.right[self.pos:]]])
        s = s + ' lookup=' + self.lookup + '\n'
        return s

    def __repr__(self) -> str:
        return self.__str__()


class LRDFA:
    def reportError(self, msg: str):
        raise dfaError('DParse Build LRdfa failed, {}'.format(msg))

    def isTerminal(self, name):
        if name in self.tokens or name == Epsilon:
            return True
        elif name in self.types:
            return False
        else:
            self.reportError('{} is not defined'.format(name))

    def __init__(self, config: ParserConfig) -> None:
        self.tokens = set({*config.tokens, Dollar})
        self.types = set({*config.types, START})

        assert(self.isTerminal(config.start) == False)
        self.productions = [Production(
            left=START, right=tuple([config.start]), reduce=(lambda val: val))]
        for it in config.productions:
            left = it.left
            right = it.right
            if left is None or right is None:
                self.reportError('Config miss left or right {}'.format(
                    json.dumps(it, default=lambda o: o.__dict__, indent=4)))
            assert(self.isTerminal(left) == False)
            for r in right:
                for symbol in r.rule:
                    self.isTerminal(symbol)
                self.productions.append(Production(
                    left=left, right=tuple(r.rule), reduce=r.reduce))

        firstSet = FirstSet(self.tokens, self.types, self.productions)
        group = groupBy(self.productions)

        closureCache: dict[frozenset[Item], list[Item]] = {}

        def closure(I: frozenset[Item]):
            if I in closureCache:
                return closureCache[I]
            ans = set(I)
            q = [*I]
            while len(q) > 0:
                cur = q.pop(0)
                if cur.pos >= len(cur.production.right):
                    continue
                B = cur.production.right[cur.pos]
                firstBeta = firstSet.query(
                    *cur.production.right[cur.pos+1:], cur.lookup)
                if B in group:
                    for prod in group[B]:
                        for b in firstBeta:
                            item = Item(prod, 0, b)
                            if item not in ans:
                                ans.add(item)
                                q.append(item)
            r = frozenset(ans)
            closureCache[I] = r
            return r

        def move(I: frozenset[Item], w: str):
            ans: set[Item] = set()
            for item in I:
                if item.pos < len(item.production.right) and item.production.right[item.pos] == w:
                    ans.add(Item(item.production, item.pos+1, item.lookup))
            return closure(frozenset(ans))

        allT = set({*self.tokens, *self.types})
        allT.remove(Dollar)
        st = Item(self.productions[0], 0, Dollar)
        C = [closure(frozenset([st]))]
        q = [C[0]]
        mp: dict[tuple[Item], int] = {C[0]: 0}
        while len(q) > 0:
            cur = q.pop(0)
            for ch in allT:
                v = move(cur, ch)
                if len(v) == 0:
                    continue
                if v not in mp:
                    mp[v] = len(C)
                    C.append(v)
                    q.append(v)
        self.items = C
        Action = [{} for it in C]
        Goto = [{} for it in C]
        for i in range(len(C)):
            I = C[i]
            for item in I:
                assert(self.isTerminal(item.lookup))
                if item.pos == len(item.production.right):
                    act = 'Accepted' if item.production == self.productions[
                        0] and item.pos == 1 and item.lookup == Dollar else item.production
                    if item.lookup in Action[i] and Action[i][item.lookup] != act:
                        if type(Action[i][item.lookup]) == int:
                            self.reportError('shift-reduce conflict')
                        else:
                            print(item.production.left)
                            print(item.production.right)
                            self.reportError('reduce-reduce conflict')
                    Action[i][item.lookup] = act
                else:
                    ch = item.production.right[item.pos]
                    v = move(I, ch)
                    if len(v) > 0:
                        j = mp[v]
                        if self.isTerminal(ch):
                            if ch in Action[i] and Action[i][ch] != j:
                                self.reportError('shift-reduce conflict')
                            Action[i][ch] = j
                        else:
                            if ch in Goto[i] and Goto[i][ch] != j:
                                self.reportError('construct Goto failed')
                            Goto[i][ch] = j
        self.Action = Action
        self.Goto = Goto
