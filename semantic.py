def nal_unit_type(t):
    tbl = {0: 'reserved',
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
           14: 'svc extension',
           20: 'avc 3d extension',
           }
    return tbl[t]


def isSPS(t):
    return t.nal_unit_type == 7


def isSEI(t):
    return t.nal_unit_type == 6


def showProfile(pps):
    p = pps.profile_idc
    flag = pps.constraint_set_flag
    if p == 244 and flag & 0x10:
        return "High444 Intra"
    elif p == 244:
        return "High444 Predictive"
    elif p == 144:
        return "High444"
    elif p == 122 and flag & 0x10:
        return "High422 Intra"
    elif p == 122:
        return "High422"
    elif p == 110 and flag & 0x10:
        return "High10 Intra"
    elif p == 110:
        return "High10"
    elif p == 100 and flag & 0x08 and flag & 0x04:
        return "Constrainted High"
    elif p == 100 and flag & 0x08:
        return "Progressive High"
    elif p == 100 or (p == 77 and flag == 1):
        return "High"
    elif p == 88:
        return "Extended"
    elif p == 77:
        return "Main"
    elif p == 66 and flag & 0x40:
        return "Constrainted Baseline"
    elif p == 66:
        return "Baseline"
    elif p == 44:
        return "CAVLC444 Intra"
    else:
        return "Unknown"


def isPPS(t):
    return t.nal_unit_type == 8


def isSlice(t):
    return t.nal_unit_type in [1, 5]


def isAU(t):
    return t.nal_unit_type == 9


def SliceType(v):
    tbl = ['P', 'B', 'I', 'SP', 'SI', 'P', 'B', 'I', 'SP', 'SI']
    return tbl[v]


def isSliceType(v, *l):
    r"""
    >>> isSliceType(0, 'P')
    True
    >>> isSliceType(0, 'P', 'B')
    True
    """
    return any([SliceType(v) == s for s in l])


def buildISliceMbTypeName():
    """
    >>> l = buildISliceMbTypeName()
    >>> l[1]
    'I_16x16_0_0_0'
    >>> l[14]
    'I_16x16_1_0_1'
    >>> l[20]
    'I_16x16_3_1_1'
    """
    lst = ['I_NxN']
    prefix = 'I_16x16'
    for i in range(1, 25):
        i = i - 1
        first = i % 4
        second = (i / 4) % 3
        third = (i / 4 / 3)
        s = "%s_%d_%d_%d" % (prefix, first, second, third)
        lst.append(s)
    lst.append('I_PCM')
    return lst


def buildBSliceMbTypeName():
    """
    >>> l = buildBSliceMbTypeName()
    >>> l[7]
    'B_L1_L1_8x16'
    >>> l[17]
    'B_Bi_L0_8x16'
    """
    lst = ['Direct', 'L0', 'L1', 'Bi']
    lst = [i + '_16x16' for i in lst]

    def addPair(prefix):
        l = ['16x8', '8x16']
        return [prefix + "_" + i for i in l]
    l = ['L0_L0', 'L1_L1', 'L0_L1', 'L1_L0',
         'L0_Bi', 'L1_Bi', 'Bi_L0', 'Bi_L1', 'Bi_Bi']
    for i in l:
        lst.extend(addPair(i))
    lst.extend(['B_8x8', 'B_Skip'])
    lst = ['B_' + i for i in lst]
    return lst

ISliceMbTypeNameMap = buildISliceMbTypeName()
SISliceMbTypeNameMap = ['SI'] + ISliceMbTypeNameMap
PSliceMbTypeNameMap = ['P_L0_16x16', 'P_L0_L0_16x8', 'P_L0_L0_8x16',
                       'P_8x8', 'P_8x8ref0'] + ISliceMbTypeNameMap
BSliceMbTypeNameMap = buildBSliceMbTypeName() + ISliceMbTypeNameMap
SliceTypeMapMbType = {'I': ISliceMbTypeNameMap,
                      'P': PSliceMbTypeNameMap,
                      'SP': PSliceMbTypeNameMap,
                      'B': BSliceMbTypeNameMap}


def MbTypeName(slice_type, v):
    m = SliceTypeMapMbType[SliceType(slice_type)]
    if v >= len(m):
        # TODO:
        print("out of range slice_type %s mb_type %d" % (slice_type, v))
        return m[-1]
    return m[v]


PMbTypePredMap = [["Pred_L0", "NONE"],
                  ["Pred_L0", "Pred_L0"],
                  ["Pred_L0", "Pred_L0"],
                  ["NONE", "NONE"],
                  ["NONE", "NONE"],
                  ["Pred_L0", "NONE"]]


def MbPartPredMode(slice_type, mb_type, n):
    sSlicet = SliceType(slice_type)
    if sSlicet == 'I':
        if mb_type == 0:
            return "Intra_4x4"
        elif mb_type == 25:
            return "NONE"
        else:
            return "Intra_16x16"
    elif sSlicet == "P":
        return PMbTypePredMap[mb_type][n]
    elif sSlicet == "B":
        # TODO
        return BMbTypePredMap[mb_type][n]


def NumMbPart(mb_type):
    pass


def CodedBlockPattern(mb_type):
    """
    >>> CodedBlockPattern(0)
    (None, None)
    >>> CodedBlockPattern(12)
    (2, 0)
    >>> CodedBlockPattern(13)
    (0, 15)
    """
    if mb_type > 25:
        raise Exception('unknown mb_type %d' % (mb_type))
    if mb_type == 0 or mb_type == 25:
        return None, None
    chroma = (mb_type - 1) // 4 % 3
    luma = 0 if mb_type <= 12 else 15
    return chroma, luma
