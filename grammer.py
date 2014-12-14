from collections import namedtuple

import bin


class GrammerUnit():

    def __init__(self, bs):
        self.data = self.init(bs)

    def _ins(self, k, v):
        self.__dict__[k] = v

    def dump(self):
        for k, v in self.__dict__.items():
            print(k.ljust(40), v)

    def _chkcond(self, cond):
        if isinstance(cond, str):
            cond = self.__dict__[cond]
            if isinstance(cond, int) and cond is 0:
                cond = False
        if cond is False:
            return False
        else:
            return True

    def _geparse(self, bsm, gelst):
        for ge in gelst:
            if self._chkcond(ge.cond) is False:
                continue
            if ge.repeat == 1:
                if ge.descriptor == 'ue':
                    v = bsm.ue()
                elif ge.descriptor == 'u':
                    v = bsm.readBit(ge.desp)
                else:
                    raise Exception('descriptor not impl')
            else:
                raise Exception('ge repeat not impl')
            if ge.post:
                v = ge.post(v)
            self._ins(ge.name, v)

NalUnit = namedtuple('NalUnit', ['forbidden_zerob_bit',
                                 'nal_ref_idc',
                                 'nal_uint_type',
                                 'rbsp'])


def naluint(bs):
    r"""
    >>> naluint(b'\x67\x4d')
    NalUnit(forbidden_zerob_bit=0, nal_ref_idc=3, nal_uint_type=7, rbsp=b'M')
    """
    d = bin.bytesfield(bs, [1, 2, 5])
    d.append(bs[1:])
    return NalUnit(*d)


class GrammerElement():

    def __init__(self, name, descriptor,
                 desp=1, cond=True, post=None, repeat=1):
        self.name = name
        self.descriptor = descriptor
        self.desp = desp
        self.post = post
        self.repeat = repeat
        self.cond = cond

ge = GrammerElement


class SPS(GrammerUnit):

    def __init__(self, bs):
        bsm = bin.BitStreamM(bs)
        gelst = [ge('profile_idc', 'u', 8),
                 ge('constraint_set_flag', 'u', 8),
                 ge('level_idc', 'u', 8),
                 ge('seq_parameter_set_id', 'ue'),
                 ge('max_frame_num', 'ue',
                    post=lambda x:2 ** (x + 4)),
                 ge('pic_order_cnt_type', 'ue'),
                 ge('max_pic_order_cnt_lsb', 'ue',
                    cond='pic_order_cnt_type', post=lambda x:2 ** (x + 4)),
                 ge('num_ref_frames', 'ue'),
                 ge('gaps_in_frame_num_value_allowed_flag', 'u'),
                 ge('pic_width_in_mbs', 'ue',
                    post=lambda x:x + 1),
                 ge('pic_height_in_mbs', 'ue',
                    post=lambda x:x + 1),
                 ge('frame_mbs_only_flag', 'u'),
                 ge('mb_apdative_frame_field_flag', 'u',
                    cond='frame_mbs_only_flag'),
                 ge('direct_8x8_inference_flag', 'u'),
                 ge('frame_cropping_flag', 'u'),
                 ge('frame_crop_left_offset', 'ue',
                    cond='frame_cropping_flag'),
                 ge('frame_crop_right_offset', 'ue',
                    cond='frame_cropping_flag'),
                 ge('frame_crop_top_offset', 'ue',
                    cond='frame_cropping_flag'),
                 ge('frame_crop_bottom_offset', 'ue',
                    cond='frame_cropping_flag'),
                 ge('vui_prameter_present_flag', 'u')
                 ]
        self._geparse(bsm, gelst)

    _ins = GrammerUnit._ins
    _geparse = GrammerUnit._geparse
    dump = GrammerUnit.dump


class PPS(GrammerUnit):

    def __init__(self, bs):
        bsm = bin.BitStreamM(bs)
        gelst = [ge('pic_parameter_set_id', 'ue'),
                 ge('seq_parameter_set_id', 'ue'),
                 ge('entropy_coding_mode_flag', 'u'),
                 ge('pic_order_present_flag', 'u'),
                 ge('num_slice_group', 'ue', post=lambda x:x+1),
                 ]
        self._geparse(bsm, gelst)

    _ins = GrammerUnit._ins
    _geparse = GrammerUnit._geparse
    dump = GrammerUnit.dump
