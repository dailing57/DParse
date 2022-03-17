from type import Epsilon, Production


class Error(Exception):
    def __init__(self, message=None):
        self.message = f'{self.__class__.__name__}: {message}'


class automatonError(Error):
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
            for left, right in production:
                if len(right) == 0 or (len(right) == 1 and right[0] == ''):
                    self.isEpsilon.add(left)
                else:
                    isBreak = False
                    for it in right:
                        if self.isTerminal(it):
                            haveNew += self.addFirst(left, it)
                            isBreak = True
                            break
                        else:
                            for symbol in self.first[it]:
                                haveNew += self.addFirst(left, symbol)
                            if it in self.isEpsilon:
                                isBreak = True
                                break
                    if isBreak:
                        self.isEpsilon.add(left)
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
        raise automatonError(
            'DParse Build LR automaton failed, {}'.format(msg))

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
                if it in self.isEpsilon:
                    isBreak = True
                    break
        if not isBreak:
            res.add(Epsilon)
        ans = [*res]
        ans.sort()
        return ans