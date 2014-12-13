from collections import namedtuple

import bin


class GrammerUnit():

    def __init__(self, bs):
        self.data = self.init(bs)

    def init(self, bs):
        pass

    def dump(self):
        for t, d in self.data._asdict():
            print(t, d)

NalUnit = namedtuple('NalUnit', ['forbidden_zerob_bit',
                                 'nal_ref_idc',
                                 'nal_uint_type',
                                 'rbsp'])


def naluint(bs):
    r"""
    >>> naluint(b'\x67\x4d')
    NalUnit(forbidden_zerob_bit=0, nal_ref_idc=3, nal_uint_type=7, rbsp=b'M')
    """
    d = bin.bytesfield(bs, [1, 2, 5])
    d.append(bs[1:])
    return NalUnit(*d)


SPSd = namedtuple('SPSd', ['profile_idc',
                           'constraint_set_flag',
                           'reserved',
                           'level_idc'
                           ])
wid = [8, 3, 5, 8]


def sps(bs):
    d = bin.bytesfield(bs, wid)
    return SPS(*d)


class SPS(GrammerUnit):

    def __init__(self, bs):
        d = bin.bytesfield(bs, wid)
        self.data = SPSd(*d)

    def dump(self):
        print (self.data)
