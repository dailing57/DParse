from .type import Epsilon, Error


class firstError(Error):
    pass


class FirstSet:
    def __init__(self, tokens, types, production) -> None:
        self.tokens = tokens
        self.types = types
        self.first = {}
        self.isEpsilon = set()
        for tk in tokens:
            self.first[tk] = [tk]
        while True:
            haveNew = 0
            for p in production:
                if len(p.right) == 0 or (len(p.right) == 1 and p.right[0] == ''):
                    self.isEpsilon.add(p.left)
                else:
                    isBreak = False
                    for it in p.right:
                        if self.isTerminal(it):
                            haveNew += self.addFirst(p.left, it)
                            isBreak = True
                            break
                        else:
                            if it in self.first:
                                for symbol in self.first[it]:
                                    haveNew += self.addFirst(p.left, symbol)
                            if it not in self.isEpsilon:
                                isBreak = True
                                break
                    if not isBreak:
                        self.isEpsilon.add(p.left)
            if haveNew == 0:
                break
        for symbol in self.isEpsilon:
            self.addFirst(symbol, Epsilon)

    def addFirst(self, x, y):
        assert(not self.isTerminal(x))
        assert(self.isTerminal(y))
        if x not in self.first:
            self.first[x] = [y]
            return 1
        else:
            arr = self.first[x]
            if y in arr:
                return 0
            else:
                arr.append(y)
                return 1

    def reportError(slef, msg):
        raise firstError(
            'DParse Build firstSet failed, {}'.format(msg))

    def isTerminal(self, name):
        if name in self.tokens or name == Epsilon:
            return True
        elif name in self.types:
            return False
        else:
            self.reportError('{} is not defined'.format(name))

    def query(self, *args):
        if len(args) == 0 or (len(args) == 1 and args[0] == Epsilon):
            return [Epsilon]
        res = set()
        isBreak = False
        for it in args:
            if self.isTerminal(it):
                res.add(it)
                isBreak = True
                break
            else:
                for symbol in self.first[it]:
                    if symbol != Epsilon:
                        res.add(symbol)
                if it not in self.isEpsilon:
                    isBreak = True
                    break
        if not isBreak:
            res.add(Epsilon)
        ans = [*res]
        ans.sort()
        return ans
