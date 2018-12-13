import bin
import grammer
import semantic

if __name__ == "__main__":
    # fn = "video_es_all.dat"
    fn = "1.bin"
    d = open(fn, 'rb').read()
    d = bin.nalu(d)
    SPSl, PPSl = [], []
    for nal in d:
        nal = grammer.nalunit(nal)
        print("NAL ", nal.nal_ref_idc, end=" ")
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
            continue
            bin.dump(nal.rbsp)
            SliceHead = grammer.SliceHead(nal, PPSl)
            SliceHead.dump()
        else:
            bin.dump(nal.rbsp)
