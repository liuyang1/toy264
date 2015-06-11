import sys


import bin
import grammer
import semantic


def chkProfile(fn):
    d = open(fn, 'rb').read()
    d = bin.nalu(d)
    for nal in d:
        nal = grammer.nalunit(nal)
        if semantic.isSPS(nal):
            SPS = grammer.SPS(nal.rbsp)
            SPS.dump()
            # print (SPS.profile_idc, SPS.constraint_set_flag, SPS.level_idc)
            # return
        elif semantic.isPPS(nal):
            PPS = grammer.PPS(nal.rbsp, [SPS])
            PPS.dump()
        else:
            Slice = grammer.SliceHead(nal, [PPS])
            Slice.dump()


if __name__ == "__main__":
    chkProfile(sys.argv[1])
