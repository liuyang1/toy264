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
        mask = 2 ** left - 2 ** right
        v = (b & mask) >> right
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
        if sum(t) % s == 0:
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
