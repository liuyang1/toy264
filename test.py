import bin
import grammer
import semantic

if __name__ == "__main__":
    fn = "CABA2_SVA_B.264"
    d = open(fn, 'rb').read()
    d = bin.nalu(d)
    for nal in d:
        nal = grammer.naluint(nal)
        print(nal.nal_ref_idc, end=" ")
        print(semantic.nal_uint_type(nal.nal_uint_type))
        if semantic.isSPS(nal):
            SPS = grammer.SPS(nal.rbsp)
            SPS.dump()
        elif semantic.isPPS(nal):
            PPS = grammer.PPS(nal.rbsp)
            PPS.dump()
