import first
from type import Production

firstset = first.FirstSet(
    set({'a', 'b', 'c'}),
    set({'S', 'A', 'B', 'C', 'D'}),
    [
        Production(left='S', right=['A', 'B']),
        Production(left='S', right=['b', 'C']),
        Production(left='A', right=['']),
        Production(left='A', right=['b']),
        Production(left='B', right=[]),
        Production(left='B', right=['a', 'D']),
        Production(left='C', right=['A', 'D']),
        Production(left='C', right=['b']),
        Production(left='D', right=['a', 'S']),
        Production(left='D', right=['c']),
    ])

print(firstset.query('S'))
print(firstset.query('A'))
print(firstset.query('B'))
print(firstset.query('C'))
print(firstset.query('D'))
print(firstset.isEpsilon)
print(firstset.query('A', 'S'))
