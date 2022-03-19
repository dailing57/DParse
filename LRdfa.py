import json
from first import FirstSet
from type import ParserConfig, Production, START, Epsilon, Dollar, Error


class dfaError(Error):
    pass


def groupBy(productions: list[Production]):
    mp = {}
    for it in productions:
        mp[it.left] = [it]
    return mp


class Item:
    def __init__(self, production, pos=0, lookup=Epsilon) -> None:
        self.production: Production = production
        self.pos: int = pos
        self.lookup: str = lookup

    def __eq__(self, __o: object) -> bool:
        return self.__dict__ == __o.__dict__

    def __str__(self) -> str:
        return ' '.join([str(x) for x in [*self.production.right[:self.pos], '.', *self.production.right[self.pos:]]])

    def __repr__(self) -> str:
        return self.__str__()


class LRDFA:
    def reportError(msg: str):
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
            left=START, right=[config.start], reduce=(lambda val: val))]
        for it in config.productions:
            left = it.left
            right = it.right
            if left is None or right is None:
                self.reportError('Config miss left or right {}'.format(
                    json.dumps(it, default=lambda o: o.__dict__, indent=4)))
            for r in right:
                assert(self.isTerminal(left) == False)
                for symbol in r.rule:
                    self.isTerminal(symbol)
                self.productions.append(Production(
                    left=left, right=r.reduce, reduce=r.reduce))

        firstSet = FirstSet(self.tokens, self.types, self.productions)
        group = groupBy(self.productions)
        itemCache: list[Item] = []

        def getItem(x: Item):
            for y in itemCache:
                if x == y:
                    return y
            itemCache.append(x)
            return x

        closureCache: dict[Item, list[Item]] = {}

        def closure(I: list[Item]):
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
                            item = getItem(Item(prod, 0, b))
                            if item not in ans:
                                ans.add(item)
                                q.append(item)
            r = [*ans]
            closureCache[I] = r
            return r

        def move(I: list[Item], w: str):
            ans: list[Item] = []
            for item in I:
                if item.pos < len(item.production.right) and item.production.right[item.pos] == w:
                    ans.append(
                        getItem(Item(item.production, item.pos+1, item.lookup)))
            return closure(ans)

        allT = set(*self.tokens, *self.types)
        allT.remove(Dollar)
        st = getItem(Item(self.productions[0], 0, Dollar))
        C = [closure([st])]
        q = [C[0]]
        mp: dict[Item, int] = {C[0]: 0}
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
