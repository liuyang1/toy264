def show_nal_unit_type(t):
    tbl = {32: 'VPS NUT',
           33: 'SPS NUT',
           35: 'PPS NUT',
           36: 'EOS NUT', # end of sequence
           37: 'EOB NUT', # end of bitstream
           38: 'FD NUT',  # filler data
           39: 'PREFIX SEI NUT',
           40: 'SUFFIX SEI NUT',
           }
    return tbl[t] if t in tbl.keys() else "### unknown nal unit type ###"



