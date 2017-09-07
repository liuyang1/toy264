import sys
sys.path.append("..")

import bin
import h265
import grammer

if __name__ == "__main__":
    fn = "test.265"
    d = open(fn, 'rb').read()
    d = bin.nalu(d)
    vps, sps, pps = [], [], []
    print("split nal OK")
    for bs in d:
        nal = h265.H265NalUnit(bs)
        str_type = nal.show_type()
        if "unknown" in str_type:
            continue
        elif "VPS" in str_type:
            VPS = h265.VPS(nal.bsm)
            VPS.dump()
        elif "SEI" in str_type:
            SEI = h265.SEI(nal.bsm)
            SEI.dump()
        else:
            nal.dump()


