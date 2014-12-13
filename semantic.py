def nal_uint_type(t):
    tbl = {0: 'reserved',
           1: 'slice',
           5: 'IDR slice',
           7: 'SPS Sequence Parameter Set',
           8: 'PPS Picture Parameter Set'
           }
    return tbl[t]

def isSPS(t):
    return t.nal_uint_type == 5
