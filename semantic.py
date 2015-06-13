def nal_unit_type(t):
    tbl = {0: 'reserved',
           1: 'slice',
           5: 'IDR slice',
           7: 'SPS Sequence Parameter Set',
           8: 'PPS Picture Parameter Set',
           9: 'delimter',
           }
    return tbl[t]


def isSPS(t):
    return t.nal_unit_type == 7


def showProfile(pps):
    p = pps.profile_idc
    flag = pps.constraint_set_flag
    # TODO: more detail
    if p == 144:
        return "High444"
    elif p == 122:
        return "High422"
    elif p == 110:
        return "High10"
    elif p == 100 or (p == 77 and flag == 1):
        return "High"
    elif p == 88:
        return "Extern"
    elif p == 77:
        return "Main"
    elif p == 66:
        return "Baseline"


def isPPS(t):
    return t.nal_unit_type == 8


def isSlice(t):
    return t.nal_unit_type in [1, 5]


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
        l =  ['16x8', '8x16']
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
