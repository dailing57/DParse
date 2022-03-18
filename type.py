Epsilon = 'EMP'


class Production:
    def __init__(self, left='', right=[]) -> None:
        self.left = left
        self.right = right

    def reduce(self, *args):
        pass
