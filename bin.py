import sys
import math


def dump(data):
    """
    pretty dump binary data with
    prefix lineno, every 16 bytes per line, every 4 bytes per chunk
    """
    idx = 0
    for i in data:
        if idx % 16 == 0:
            print("%08x" % (idx), end="  ")
        print("%02x" % (i), end=" ")
        idx = idx + 1
        if idx % 4 == 0:
            print(" ", end="")
        if idx % 16 == 0:
            print("")
    if (idx + 1) % 16 != 0:
        print("")


def nalu(data):
    r"""
    split raw bytes to nalus, split by H.264 start code
    >>> nalu(b'\x00\x00\x00\x01\xAA')
    [b'\xaa']
    >>> nalu(b'\x00\x00\x00\x01\xAA\x00\x00\x00\x01\xBB')
    [b'\xaa', b'\xbb']
    >>> nalu(b'\x00\x00\x00\x03\x00')
    [b'\x00\x00\x00\x00']
    >>> nalu(b'\xaa\x00\x00\x00\x01\x00\x00\x00\x03\x00')
    [b'\xaa', b'\x00\x00\x00\x00']
    """
    r = data.split(b'\x00\x00\x00\x01')
    # also support 000001 start code
    r = [i.split(b'\x00\x00\x01') for i in r]
    import itertools
    r = itertools.chain(*r)
    # resume conflict bytes with start code back
    m = [(b'\x00\x00\x00\x00', b'\x00\x00\x00\x03\x00'),
         (b'\x00\x00\x00\x01', b'\x00\x00\x00\x00\x01'),
         (b'\x00\x00\x00\x02', b'\x00\x00\x00\x00\x02'),
         (b'\x00\x00\x00\x03', b'\x00\x00\x00\x00\x03')]
    for orignal, trans in m:
        r = [i.replace(trans, orignal) for i in r]
    r = [i for i in r if i != b'']
    return r


def extBit(b, left, right):
    r"""
    extract bit from [left, right] bits
    >>> extBit(0x67, 7, 5)
    3
    """
    mask = 2 ** left - 2 ** right
    v = (b & mask) >> right
    return v


def onebytefield(b, widlst):
    r"""
    split one byte based on field list
    >>> onebytefield(0x67, [1, 2, 5])
    [0, 3, 7]
    >>> onebytefield(0xff, [1, 2, 5])
    [1, 3, 31]
    """
    assert sum(widlst) == 8
    left, right = 8, 8
    ret = []
    for i in widlst:
        right -= i
        v = extBit(b, left, right)
        ret.append(v)
        left -= i
    return ret


def sumsplit(widlst, s=8):
    r"""
    >>> sumsplit([1, 2, 5, 1, 7], 8)
    [[1, 2, 5], [1, 7]]
    """
    lst = []
    t = []
    for i in widlst:
        t.append(i)
        if sum(t) == s:
            lst.append(t)
            t = []
    return lst


def bytesfield(bs, widlst):
    r"""
    >>> bytesfield(b'\x67\xff', [1, 2, 5, 1, 2, 5])
    [0, 3, 7, 1, 3, 31]
    """
    import itertools
    widlst = sumsplit(widlst, 8)
    lst = [onebytefield(b, wid) for b, wid in zip(bs, widlst)]
    return list(itertools.chain(*lst))


def readBits(bs, offset, size=1):
    r"""
    >>> readBits(b'\x38', 0, 1)
    0
    >>> readBits(b'\x38', 2, 2)
    3
    >>> readBits(b'bb', 7, 3)
    1
    >>> readBits(b'bbb', 7, 11)
    393
    """
    co, bo = offset // 8, offset % 8
    b = bs[co]
    v = 0
    if size > 8 - bo:
        v = extBit(b, 8 - bo, 0)
        vv = v
        size -= 8 - bo
        while size > 8:
            co += 1
            b = bs[co]
            v = b
            vv = (vv << 8) + v
            size -= 8
        co += 1
        b = bs[co]
        v = extBit(b, 8, 8 - size)
        vv = (vv << size) + v
        v = vv
    else:
        v = extBit(b, 8 - bo, 8 - bo - size)
    return v


def readBitsIncOff(bs, offset, size=1):
    return readBits(bs, offset, size), offset + size


def deUnsignedExpl(bs, offset=0):
    r"""
    >>> deUnsignedExpl(b'\x38')
    (6, 5)
    >>> deUnsignedExpl(b'\x14')
    (9, 7)
    """
    leading = 0
    while readBits(bs, offset + leading) == 0:
        leading += 1
    v = readBits(bs, offset + leading + 1, leading)
    code = 2 ** leading - 1 + v
    newoffset = leading * 2 + 1 + offset
    return code, newoffset


def deSignedExpl(bs, offset=0):
    r"""
    >>> deSignedExpl(b'\x38')
    (-3, 5)
    """
    code, offset = deUnsignedExpl(bs, offset)
    ret = math.ceil(code / 2)
    if code % 2 == 0:
        ret *= -1
    return ret, offset


def deAdaptiveExpl(bs, offset=0):
    r"""

    """
    pass


def deCAVLC(bs, nC, offset=0):
    """
    """
    tab = tab.sel_nCTab(nC)


class BitStreamM():
    base = 8

    def __init__(self, bs, csr=0):
        self.bs = bs
        self.csr = csr

    def readBit(self, size):
        v, self.csr = readBitsIncOff(self.bs, self.csr, size)
        return v

    def align(self, byte=1):
        offset = byte * BitStreamM.base
        while self.csr % offset != 0:
            self.csr += 1

    def b(self):
        v, self.csr = readBitsIncOff(self.bs, self.csr, 8)
        return v

    def ue(self):
        v, self.csr = deUnsignedExpl(self.bs, self.csr)
        return v

    def se(self):
        v, self.csr = deSignedExpl(self.bs, self.csr)
        return v

    def ae(self):
        v, self.crs = deAdaptiveExpl(self.bs, self.csr)
        return v

    def ce(self, nC):
        v, self.crs = deCAVLC(self.bs, nC, self.csr)
        return v

    def isMoreData(self):
        return self.csr < len(self.bs) * BitStreamM.base

    def calldesp(self, s, *params):
        despmap = {'u': BitStreamM.readBit,
                   'ue': BitStreamM.ue, 'se': BitStreamM.se,
                   'b': BitStreamM.b,
                   'ae': None, 'ce': None, 'me': None, 'te': None}
        fn = despmap[s]
        if fn is None:
            raise Exception("%s @ BitStreamM not impl" % (s))
        if s == 'u':
            return fn(self, params[0])
        elif s == 'ce':
            nC = params[0]
            return fn(self, nC)
        else:
            return fn(self)

    def dump(self):
        print(self.bs)
        print(self.csr)
        print(self.csr / 8)
        print(self.csr % 8)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
