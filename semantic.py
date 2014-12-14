def nal_unit_type(t):
    tbl = {0: 'reserved',
           1: 'slice',
           5: 'IDR slice',
           7: 'SPS Sequence Parameter Set',
           8: 'PPS Picture Parameter Set'
           }
    return tbl[t]


def isSPS(t):
    return t.nal_unit_type == 7


def isPPS(t):
    return t.nal_unit_type == 8


def isSlice(t):
    return t.nal_unit_type in [1, 5]


def SliceType(v):
    tbl = ['P', 'B', 'I', 'SP', 'SI', 'P', 'B', 'I', 'SP', 'SI']
    return tbl[v]


def isSliceType(v, s):
    return SliceType(v) == s

def isInSliceType(v, l):
    return any([SliceType(v) == s for s in l])
