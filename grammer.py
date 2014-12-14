from collections import namedtuple

import bin
import semantic


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
            if cond not in self.__dict__.keys():
                return False
            cond = self.__dict__[cond]
            if isinstance(cond, int) and cond is 0:
                return False
        elif callable(cond):
            # apply lambda function as condition
            cond = cond()
        return cond

    def _geparse(self, bsm, ge):
        if self._chkcond(ge.cond) is False:
            return
        if ge.repeat == 1:
            if ge.descriptor == 'ue':
                v = bsm.ue()
            elif ge.descriptor == 'se':
                v = bsm.se()
            elif ge.descriptor == 'u':
                v = bsm.readBit(ge.desp)
            else:
                raise Exception('descriptor not impl')
        else:
            raise Exception('ge repeat not impl')
        if ge.post:
            v = ge.post(v)
        self._ins(ge.name, v)

    def _geparselst(self, bsm, gelst):
        for ge in gelst:
            self._geparse(bsm, ge)

NalUnit = namedtuple('NalUnit', ['forbidden_zerob_bit',
                                 'nal_ref_idc',
                                 'nal_unit_type',
                                 'rbsp'])


def naluint(bs):
    r"""
    >>> naluint(b'\x67\x4d')
    NalUnit(forbidden_zerob_bit=0, nal_ref_idc=3, nal_unit_type=7, rbsp=b'M')
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


def inc(x):
    return x + 1


class SPS(GrammerUnit):

    def prs(self, ge):
        GrammerUnit._geparse(self, self.bsm, ge)

    def __init__(self, bs):
        self.bsm = bin.BitStreamM(bs)
        gelst = [ge('profile_idc', 'u', 8),
                 ge('constraint_set_flag', 'u', 8),
                 ge('level_idc', 'u', 8),
                 ge('seq_parameter_set_id', 'ue'),
                 ge('log2_max_frame_num', 'ue',
                    post=lambda x:x + 4),
                 ge('pic_order_cnt_type', 'ue'),
                 ge('log2_max_pic_order_cnt_lsb', 'ue',
                    cond=lambda:self.pic_order_cnt_type, post=lambda x:x + 4),
                 ge('num_ref_frames', 'ue'),
                 ge('gaps_in_frame_num_value_allowed_flag', 'u'),
                 ge('pic_width_in_mbs', 'ue', post=inc),
                 ge('pic_height_in_mbs', 'ue', post=inc),
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
        self._geparselst(self.bsm, gelst)

    _ins = GrammerUnit._ins
    _geparselst = GrammerUnit._geparselst
    dump = GrammerUnit.dump


class PPS(GrammerUnit):

    def prs(self, ge):
        GrammerUnit._geparse(self, self.bsm, ge)
    def __init__(self, bs, SPSl=None):
        self.bsm = bin.BitStreamM(bs)
        gelst = [ge('pic_parameter_set_id', 'ue'),
                 ge('seq_parameter_set_id', 'ue'),
                 ge('entropy_coding_mode_flag', 'u'),
                 ge('pic_order_present_flag', 'u'),
                 ge('num_slice_groups', 'ue', post=inc),
                 ge('num_ref_idx_10_active', 'ue', post=inc),
                 ge('num_ref_idx_11_active', 'ue', post=inc),
                 ge('weighted_pred_flag', 'u'),
                 ge('weighted_bipred_flag', 'u', 2),
                 ge('pic_init_qp', 'se', post=lambda x:x + 26),
                 ge('pic_init_qs', 'se', post=lambda x:x + 26),
                 ge('chroma_qp_index_offset', 'se'),
                 ge('deblocking_filter_ctrl_present_flag', 'u'),
                 ge('constrained_intra_pred_flag', 'u'),
                 ge('redundant_pic_cnt_present_flag', 'u'),
                 ]
        self._geparselst(self.bsm, gelst)
        if self.seq_parameter_set_id < len(SPSl):
            self.SPS = SPSl[self.seq_parameter_set_id]
        else:
            raise Exception('not find SPS ' + str(self.seq_parameter_set_id))
        if self.num_slice_groups > 1:
            raise Exception('PPS slice_group not impl')

    _ins = GrammerUnit._ins
    _geparselst = GrammerUnit._geparselst
    dump = GrammerUnit.dump


class SliceHead(GrammerUnit):

    def __init__(self, nal, PPSl=[]):
        self.nal = nal
        self.bsm = bin.BitStreamM(nal.rbsp)
        gelst = [ge('first_mb_in_slice', 'ue'),
                 ge('slice_type', 'ue'),
                 ge('pic_parameter_set_id', 'ue'),
                 ]
        self._geparselst(self.bsm, gelst)
        if self.pic_parameter_set_id < len(PPSl):
            self.PPS = PPSl[self.pic_parameter_set_id]
            self.SPS = self.PPS.SPS
        else:
            raise Exception('not find PPS ' + str(self.pic_parameter_set_id))
        gelst = [ge('frame_num', 'u', self.SPS.log2_max_frame_num),
                 ge('field_pic_flag', 'u',
                    cond=lambda: not self.SPS.frame_mbs_only_flag),
                 ge('bottom_filed_flag', 'u',
                    cond='field_pic_flag'),
                 ge('idr_pic_id', 'ue',
                    cond=lambda: self.nal.nal_unit_type == 5),
                 ge('pic_order_cnt_lsb', 'u',
                    self.SPS.log2_max_pic_order_cnt_lsb,
                    cond=lambda: self.SPS.pic_order_cnt_type == 0),
                 ge('delta_pic_order_cnt_bottom', 'se',
                    cond=lambda: self.SPS.pic_order_cnt_type == 0
                    and self.PPS.pic_order_present_flag
                    and not self.field_pic_flag),
                 # TODO: pic_order_cnt_type 1, and other
                 ge('redundant_pic_cnt', 'ue',
                    cond=self.PPS.redundant_pic_cnt_present_flag),
                 ge('direct_spatial_mv_pred_flag', 'u',
                    cond=lambda:self.isSliceType('B')),
                 ge('num_ref_idx_active_override_flag', 'u',
                    cond=lambda:self.isInSliceType(['P', 'SP', 'B'])),
                 ge('num_ref_idx_10_active', 'ue',
                    cond=lambda:self.isInSliceType(['P', 'SP', 'B'])
                    and self.num_ref_idx_active_override_flag,
                    post=inc),
                 ge('num_ref_idx_11_active', 'ue',
                    cond=lambda:self.isSliceType('B')
                    and self.num_ref_idx_active_override_flag,
                    post=inc),
                 ]
        self._geparselst(self.bsm, gelst)
        self.parseRefPicListReordering()
        self.prsPredWeightTbl()
        self.prsDecRefPicMarking()
        if self.PPS.entropy_coding_mode_flag and self.isInSliceType(['I', 'SI']):
            self.prs(ge('cabac_init_idc', 'ue'))
        self.prs(ge('slice_qp_delta', 'se'))
        if self.isInSliceType(['SP', 'SI']):
            if self.isSliceType('SP'):
                self.prs(ge('sp_for_switch_flag', 'u'))
            self.prs(ge('slice_qs_delta', 'se'))
        if self.PPS.deblocking_filter_ctrl_present_flag:
            self.prs(ge('disable_deblocking_filter_idc', 'ue'))
            if self.disable_deblocking_filter_idc != 1:
                self.prs(ge('slice_alpha_c0_offset', 'se', post=lambda x:x*2))
                self.prs(ge('slice_beta_offset', 'se', post=lambda x:x*2))
        if self.PPS.num_slice_groups > 1:
            raise Exception('SliceHead num_slice_groups not impl')

    def isSliceType(self, t):
        return semantic.isSliceType(self.slice_type, t)

    def isInSliceType(self, ts):
        return any([self.isSliceType(t) for t in ts])

    def prs(self, ge):
        GrammerUnit._geparse(self, self.bsm, ge)

    def parseRefPicListReordering(self):
        if not self.isInSliceType(['I', 'B']):
            self.prs(ge('ref_pic_list_reordering_flag_10', 'u'))
            if (self.ref_pic_list_reordering_flag_10):
                raise Exception('not impl in RefPicListReordering')
        if self.isSliceType('B'):
            raise Exception("slicetype B not impl in RefPicListReordering")

    def prsPredWeightTbl(self):
        if (self.PPS.weighted_pred_flag and self.isInSliceType(['P', 'SP'])) or (self.PPS.weighted_bipred_flag and self.isSliceType('B')):
            self.prs(ge('luma_log2_weight_denom', 'ue'))
            self.prs(ge('chroma_log2_weight_denom', 'ue'))
            raise Exception("PrefWeightTbl not impl")

    def prsDecRefPicMarking(self):
        if self.nal.nal_ref_idc is 0:
            return
        if self.nal.nal_unit_type == 5:
            self.prs(ge('no_output_prior_pics_flag', 'u'))
            self.prs(ge('long_term_reference_flag', 'u'))
            return
        self.prs(ge('adaptive_ref_pic_marking_mode_flag', 'u'))
        if not self.adaptive_ref_pic_marking_mode_flag:
            return
        while 1:
            self.prs(ge('memory_mgn_ctrl_op', 'ue'))
            if self.memory_mgn_ctrl_op == 0:
                break
            elif self.memory_mgn_ctrl_op in [1, 3]:
                self.prs(ge('diff_of_pic_nums', 'ue', post=inc))
            elif self.memory_mgn_ctrl_op is 2:
                self.prs(ge('long_term_pic_num', 'ue'))
            elif self.memory_mgn_ctrl_op in [3, 6]:
                self.prs(ge('long_term_frame_idx', 'ue'))
            elif self.memory_mgn_ctrl_op == 4:
                self.prs(
                    ge('max_long_term_frame_idx', 'ue', post=lambda x: x - 1))
    _ins = GrammerUnit._ins
    _geparselst = GrammerUnit._geparselst
    dump = GrammerUnit.dump
