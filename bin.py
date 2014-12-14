import sys


def nalu(data):
    r"""
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
    >>> extBit(0x67, 7, 5)
    3
    """
    mask = 2 ** left - 2 ** right
    v = (b & mask) >> right
    return v


def onebytefield(b, widlst):
    r"""
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

ue = deUnsignedExpl

class BitStreamM():
    def __init__(self, bs, csr=0):
        self.bs = bs
        self.csr = csr
    def readBit(self, size):
        v, self.csr = readBitsIncOff(self.bs, self.csr, size)
        return v
    def ue(self):
        v, self.csr = ue(self.bs, self.csr)
        return v

if __name__ == "__main__":
    import doctest
    doctest.testmod()
