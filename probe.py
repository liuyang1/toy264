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
            print (SPS.profile_idc, SPS.constraint_set_flag, SPS.level_idc)
            # SPS.dump()
            return


if __name__ == "__main__":
    try:
        chkProfile(sys.argv[1])
    except:
        print("error")
