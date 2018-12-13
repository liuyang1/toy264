# Table 9-5
# (len, bits) -> (TotalCoeff, TrailingOnes)
nC01 = {(1, 1): (0, 0),
        (6, 0b0001010): (1, 0),
        (2, 0b01): (1, 1),
        (8, 0b00000111): (2, 0),
        (6, 0b000100): (2, 1),
        (3, 0b001): (2, 2),
        (9, 0b00000111): (3, 0),
        (8, 0b0000110): (3, 1),
        (7, 0b000101): (3, 2),
        (5, 0b00011): (3, 3),
        (10, 0b0000000111): (4, 0),
        (9, 0b000000110): (4, 1),
        (8, 0b0000101): (4, 2),
        (6, 0b000011): (4, 3),
        (11, 0b00000000111): (5, 0),
        (10, 0b0000000110): (5, 1),
        (9, 0b000000101): (5, 2),
        (7, 0b0000100): (5, 3),
        }

nC23 = {}
nC4567 = {}
nC8 = {}
nC_1 = {}
nC_2 = {}


def sel_nCTab(nC):
    if 0 <= nC < 2:
        return nC01
    elif 2 <= nC < 4:
        return nC23
    elif 4 <= nC < 8:
        return nC4567
    elif 8 <= nC:
        return nC8
    elif nC == -1:
        return nC_1
    elif nC == -2:
        return nC_2
    else:
        raise "cannot find tab for nC=%d" % (nC)


H261MbaStuffing = 34
# H261Startcode = 35
H261MbaVlcTbl = {
    (1, 0x80): 1, # 0b1
    (3, 0x60): 2, # 0b011
    (3, 0x40): 3, # 0b010
    (4, 0x30): 4, # 0b0011
    (4, 0x20): 5, # 0b0010
    (5, 0x11): 6, # 0b00011
    (5, 0x10): 7, # 0b00010
    (7, 0x0E): 8, # 0b0000 111
    (7, 0x0C): 9, # 0b0000 110
    (8, 0x0B): 10, # 0b0000 1011
    (8, 0x0A): 11, # 0b0000 1010
    (8, 0x09): 12, # 0b0000 1001
    (8, 0x08): 13, # 0b0000 1000
    (8, 0x07): 14, # 0b0000 0111
    (8, 0x06): 15, # 0b0000 0110
    (10, 0x05C0): 16, # 0b0000 0101 11
    (10, 0x0580): 17, # 0b0000 0101 10
    (10, 0x0540): 18, # 0b0000 0101 01
    (10, 0x0500): 19, # 0b0000 0101 00
    (10, 0x04C0): 20, # 0b0000 0100 11
    (10, 0x0480): 21, # 0b0000 0100 10
    (11, 0x0460): 22, # 0b0000 0100 011
    (11, 0x0440): 23, # 0b0000 0100 010
    (11, 0x0420): 24, # 0b0000 0100 001
    (11, 0x0400): 25, # 0b0000 0100 000
    (11, 0x03E0): 26, # 0b0000 0011 111
    (11, 0x03C0): 27, # 0b0000 0011 110
    (11, 0x03A0): 28, # 0b0000 0011 101
    (11, 0x0380): 29, # 0b0000 0011 100
    (11, 0x0360): 30, # 0b0000 0011 011
    (11, 0x0340): 31, # 0b0000 0011 010
    (11, 0x0320): 32, # 0b0000 0011 001
    (11, 0x0300): 33, # 0b0000 0011 000
    (11, 0x01E0): H261MbaStuffing, # 0b0000 0001 111
    # (16, 0x0001): StartCode, # 0b0000 0000 0000 0001
}
