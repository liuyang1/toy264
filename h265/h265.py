<<<<<<< HEAD
import sys
sys.path.append("..")

from collections import namedtuple

import bin
from grammer import *
from h265_semantic import *

class H265NalUnit(GrammerUnit):

    def prs(self, ge):
        GrammerUnit._geparse(self, self.bsm, ge)


    def __init__(self, bs):
        self.bsm = bin.BitStreamM(bs)
        gelst = [ge('forbidden_zero_bit', 'u', 1),
                ge('nal_unit_type', 'u', 6),
                ge('nuh_layer_id', 'u', 6),
                ge('nuh_temporal_id', 'u', 3, post=inc)]
        self._geparselst(self.bsm, gelst)
    
    def dump(self):
        print("NALU %s" % (self.show_type()))
        super().dump()

    def show_type(self):
        return show_nal_unit_type(self.nal_unit_type)


class VPS(GrammerUnit):
    def prs(self, ge):
        GrammerUnit._geparse(self, self.bsm, ge)

    def __init__(self, bsm):
        self.bsm = bsm
        gelst = [ge('vps_video_parameter_set_id', 'u', 4),
                ge('vps_base_layer_internal_flag', 'u', 1),
                ge('vps_base_layer_avaiable_flag', 'u', 1),
                ge('vps_max_layers', 'u', 6, post=inc),
                ge('vps_max_sub_layers', 'u', 3, post=inc),
                ge('vps_temporal_id_nesting_flag', 'u', 1),
                ge('vps_reserved_16bits', 'u', 16)]
        self._geparselst(self.bsm, gelst)



    def dump(self):
        print("VPS")
        super().dump()


class SEI(GrammerUnit):
    def prs(self, ge):
        GrammerUnit._geparse(self, self.bsm, ge)

    def readUntilFF(self):
        v = 0
        while (b = self.prs(ge('byte', 'b'))) == 0xff:
            v += b
        v += b
        return v

    def __init__(self, bsm):
        self.bsm = bsm
        self.payload_type = self.readUntilFF()
        self.payload_size = self.readUntilFF()

||||||| merged common ancestors
=======
import 
>>>>>>> h265: update
