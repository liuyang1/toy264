import sys
sys.path.append("..")

from grammer import *


class Picture(GrammerUnit):

    def prs(self, ge):
        GrammerUnit._geparse(self, self.bsm, ge)

    def prsseq(self, ges):
        GrammerUnit._geparseseq(self, self.bsm, ges)

    def __init__(self, bs):
        self.bsm = bin.BitStreamM(bs)
        gelst = [ge('PSC', 'u', 20),
                 ge('TR', 'u', 5),
                 ge('PTYPE', 'u', 6)]
        self._geparselst(self.bsm, gelst)
        def fn(self):
            self.prs(ge('PEI', 'u', 1))
            return self.PEI == 1
        self.prsseq(ges(ge('PSPARE', 'u', 8), until=fn, param=self))
        self.GOB()

    def GOB(self):
        return
      
    def dump(self):
        print('Picture')
        super().dump()
