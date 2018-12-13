import sys
from collections import namedtuple

import bin
# import h265.semantic

descriptorDel = "|"


def dumpkv(k, v, padding=35):
    print("    %s %s" % (k.ljust(padding, '-'), v))


class GrammerUnit():

    def __init__(self, bs):
        self.data = self.init(bs)

    def _ins(self, k, v):
        if k not in self.__dict__.keys():
            self.__dict__[k] = v

    def dump(self):
        kl = self.__dict__.keys()
        notdisp = ['nal', 'SPS', 'PPS', 'bsm', 'VUI']
        kl = [k for k in kl if k not in notdisp]
        kl = sorted(kl)
        padding = max([len(i) for i in kl])
        for k in kl:
            dumpkv(k, self.__dict__[k], padding)

    def _chkcond(self, cond):
        if callable(cond):
            # apply lambda function as condition
            cond = cond()
        if isinstance(cond, int):
            cond = False if cond == 0 else True
        return cond

    def selDesp(self, desp):
        if descriptorDel in desp:
            desplst = desp.split('|')
            return desplst[self.descriptorIdx]
        return desp

    def _geparse(self, bsm, ge):
        if self._chkcond(ge.cond) is False:
            return
        desp = self.selDesp(ge.descriptor)
        v = bsm.calldesp(desp, ge.desp)
        if ge.post:
            v = ge.post(v)
        self._ins(ge.name, v)

    def _geparselst(self, bsm, gelst):
        for ge in gelst:
            self._geparse(bsm, ge)
            
    def _geparseseq(self, bsm, ges):
        lst = []
        while ges.until(ges.param):
            v = self._geparse(bsm, ges.ge)
            lst.append(self.__dict__[ges.ge.name])
        self._ins(ges.ge.name + 's', lst)


class GrammerElement():
    """
    name: string, 
    descriptor: string,     binary parse function
    desp: number,           param when calling binary parse function if need
    cond: bool,             conditional parse this element or not
    post: function,         when get value from DESCRIPTOR, then post processing
                            result with this func.
    """
    def __init__(self, name, descriptor,
                 desp=1, cond=True, post=None):
        self.name = name
        self.descriptor = descriptor
        self.desp = desp
        self.post = post
        self.cond = cond

    def dump(self):
        print(self.name)
        print(self.descriptor)
# ge is short alias for GrammerElement
ge = GrammerElement

class GrammerElementSeq():
    def __init__(self, ge, until=None, param=None):
        self.ge = ge
        self.repeat = 1
        self.until = until
        self.param = param
ges = GrammerElementSeq

def inc(x):
    return x + 1

def dec(x):
    return x - 1

class Nal(GrammerUnit):
    def __init__(self, bs):
        self.bsm = bin.BitStreamM(bs)
        gelst = [ge('forbidden_zerob_bit', 'u', 1),
                ge('nal_unit_type', 'u', 6),
                ge('nuh_layer_id', 'u', 6),
                ge('nuh_temporal_id', 'u', 3)]
        self._geparselst(self.bsm, gelst)

    def dump(self):
        print(self.nal_unit_type)
        print(self.nuh_layer_id)
        print(self.nuh_temporal_id)


if __name__ == "__main__":
    fn = "H265.es"
    d = open(fn, 'rb').read()
    d = bin.nalu(d)
    for nal in d:
        print(nal)
        nal = Nal(nal)
        print(nal)
        nal.dump()
        break
