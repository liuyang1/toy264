def nal_unit_type(t):
    tbl = {0: 'Trail_N,Trail_R',
           1: 'non-IDR slice',
           2: 'partition A slice',
           3: 'partition B slice',
           4: 'partition C slice',
           5: 'IDR slice',
           6: 'SEI Supplemental enhancement information',
           7: 'SPS Sequence Parameter Set',
           8: 'PPS Picture Parameter Set',
           9: 'access unit delimter',
           10: 'end of sequence',
           11: 'end of stream',
           12: 'filler data',
           13: 'SPS extension',
           14: 'prefix nal unit',
           15: 'subset SPS',
           16: 'depth param set',
           17: 'reserved',
           18: 'reserved',
           19: 'slice layer without partitioning',
           20: 'slice layer ext',
           21: 'avc 3d extension',
           }
    return tbl[t]



