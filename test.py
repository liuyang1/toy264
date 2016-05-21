import bin
import grammer
import semantic

if __name__ == "__main__":
    fn = "test.264"
    d = open(fn, 'rb').read()
    d = bin.nalu(d)
    SPSl, PPSl = [], []
    for nal in d:
        nal = grammer.nalunit(nal)
        print(nal.nal_ref_idc, end=" ")
        print(semantic.nal_unit_type(nal.nal_unit_type))
        if semantic.isSPS(nal):
            SPS = grammer.SPS(nal.rbsp)
            SPS.dump()
            SPSl.append(SPS)
        elif semantic.isPPS(nal):
            PPS = grammer.PPS(nal.rbsp, SPSl)
            PPS.dump()
            PPSl.append(PPS)
        elif semantic.isAU(nal):
            au = grammer.AU(nal.rbsp)
            au.dump()
        elif semantic.isSEI(nal):
            sei = grammer.SEI(nal.rbsp)
            sei.dump()
        elif semantic.isSlice(nal):
            bin.dump(nal.rbsp)
            SliceHead = grammer.SliceHead(nal, PPSl)
            SliceHead.dump()
        else:
            bin.dump(nal.rbsp)
