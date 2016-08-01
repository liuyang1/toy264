import sys
from collections import namedtuple

import bin
import semantic

descriptorDel = "|"


def dumpkv(k, v, padding=35):
    print("    %s %s" % (k.ljust(padding, '-'), v))


class GrammerUnit():

    def __init__(self, bs):
        self.data = self.init(bs)

    def _ins(self, k, v):
        if k in self.__dict__.keys():
            # print("exist key %s value %s" % (k, self.__dict__[k]))
            pass
        self.__dict__[k] = v

    def dump(self):
        kl = self.__dict__.keys()
        notdisp = ['nal', 'SPS', 'PPS', 'bsm', 'VUI']
        kl = [k for k in kl if k not in notdisp]
        kl = sorted(kl)
        padding = max([len(i) for i in kl])
        for k in kl:
            dumpkv(k, self.__dict__[k], padding)

    def _chkcond(self, cond):
        if callable(cond):
            # apply lambda function as condition
            cond = cond()
        if isinstance(cond, int):
            cond = False if cond == 0 else True
        return cond

    def selDesp(self, desp):
        if descriptorDel in desp:
            desplst = desp.split('|')
            return desplst[self.descriptorIdx]
        return desp

    def _geparse(self, bsm, ge):
        if self._chkcond(ge.cond) is False:
            return
        desp = self.selDesp(ge.descriptor)
        v = bsm.calldesp(desp, ge.desp)
        if ge.post:
            v = ge.post(v)
        self._ins(ge.name, v)

    def _geparselst(self, bsm, gelst):
        for ge in gelst:
            self._geparse(bsm, ge)
            
    def _geparseseq(self, bsm, ges):
        lst = []
        while ges.until(ges.param):
            v = self._geparse(bsm, ges.ge)
            lst.append(self.__dict__[ges.ge.name])
        self._ins(ges.ge.name + 's', lst)


NalUnit = namedtuple('NalUnit', ['forbidden_zerob_bit',
                                 'nal_ref_idc',
                                 'nal_unit_type',
                                 'rbsp'])


def nalunit(bs):
    r"""
    >>> nalunit(b'\x67\x4d')
    NalUnit(forbidden_zerob_bit=0, nal_ref_idc=3, nal_unit_type=7, rbsp=b'M')
    """
    d = bin.bytesfield(bs, [1, 2, 5])
    d.append(bs[1:])
    return NalUnit(*d)


class GrammerElement():
    """
    name: string, 
    descriptor: string,     binary parse function
    desp: number,           param when calling binary parse function if need
    cond: bool,             conditional parse this element or not
    post: function,         when get value from DESCRIPTOR, then post processing
                            result with this func.
    """
    def __init__(self, name, descriptor,
                 desp=1, cond=True, post=None):
        self.name = name
        self.descriptor = descriptor
        self.desp = desp
        self.post = post
        self.cond = cond

    def dump(self):
        print(self.name)
        print(self.descriptor)
# ge is short alias for GrammerElement
ge = GrammerElement

class GrammerElementSeq():
    def __init__(self, ge, until=None, param=None):
        self.ge = ge
        self.repeat = 1
        self.until = until
        self.param = param
ges = GrammerElementSeq


def inc(x):
    return x + 1


class AU(GrammerUnit):

    def __init__(self, bs):
        self.bsm = bin.BitStreamM(bs)
        gelst = [ge('primary_pic_type', 'u', 3)]
        self._geparselst(self.bsm, gelst)

    def dump(self):
        print("AU")
        super().dump()


class VUI(GrammerUnit):

    Extended_SAR = 255

    def prs(self, ge):
        GrammerUnit._geparse(self, self.bsm, ge)

    def __init__(self, bsm):
        self.bsm = bsm
        self.prs(ge('aspect_ratio_info_present_flag', 'u', 1))
        if self.aspect_ratio_info_present_flag:
            self.prs(ge('aspect_ratio_idc', 'u', 8))
            if self.aspect_ratio_idc == VUI.Extended_SAR:
                self.prs(ge('sar_width', 'u', 16))
                self.prs(ge('sar_height', 'u', 16))
        self.prs(ge('overscan_info_present_flag', 'u', 1))
        if self.overscan_info_present_flag:
            self.prs(ge('overscan_appropriate', 'u', 1))
        self.prs(ge('video_signal_type_present_flag', 'u', 1))
        if self.video_signal_type_present_flag:
            self.prs(ge('video_format', 'u', 3))
            self.prs(ge('video_full_range_flag', 'u', 1))
            self.prs(ge('colour_description_present_flag', 'u', 1))
            if self.colour_description_present_flag:
                self.prs(ge('colour_primaries', 'u', 8))
                self.prs(ge('transfer_characteristics', 'u', 8))
                self.prs(ge('matrix_coefficients', 'u', 8))
        self.prs(ge('chroma_loc_info_present_flag', 'u', 1))
        if self.chroma_loc_info_present_flag:
            self.prs(ge('chroma_sample_loc_type_top_field', 'ue'))
            self.prs(ge('chroma_sample_loc_type_bottom_field', 'ue'))
        self.prs(ge('timing_info_present_flag', 'u', 1))
        if self.timing_info_present_flag:
            self.prs(ge('num_units_in_tick', 'u', 32))
            self.prs(ge('time_scale', 'u', 32))
            self.prs(ge('fixed_frame_rate_flag', 'u', 1))
        self.prs(ge('nal_hrd_parameters_present_flag', 'u', 1))
        if self.nal_hrd_parameters_present_flag:
            print("TODO: hrd_param")
        self.prs(ge('vcl_hrd_parameters_present_flag', 'u', 1))
        if self.vcl_hrd_parameters_present_flag:
            print("TODO: vcl_hdr_param")
        if self.nal_hrd_parameters_present_flag or self.vcl_hrd_parameters_present_flag:
            self.prs(ge('low_dely_hrd_flag', 'u', 1))
        self.prs(ge('pic_struct_present_flag', 'u', 1))
        self.prs(ge('bitstream_restriction_flag', 'u', 1))
        if self.bitstream_restriction_flag:
            gelst = [ge('motion_vector_over_pic_boudaries_flag', 'u', 1),
                     ge('max_bytes_per_pic_denom', 'ue'),
                     ge('max_bits_per_mb_denom', 'ue'),
                     ge('max_mv_length_horizontal',
                        'ue', post=lambda x: 2 ** x),
                     ge('max_mv_length_vertical', 'ue', post=lambda x: 2 ** x),
                     ge('max_num_reorder_frames', 'ue'),
                     ge('max_dec_frame_buffering', 'ue'),
                     ]
            self._geparselst(self.bsm, gelst)

    def dump(self):
        print("VUI")
        super().dump()


class UserDataUnregistered(GrammerUnit):

    def prs(self, ge):
        GrammerUnit._geparse(self, self.bsm, ge)

    def __init__(self, bs, payloadSize):
        self.bsm = bin.BitStreamM(bs)
        self.prs(ge('itu_country_code', 'b'))
        if self.itu_country_code != 0xff:
            i = 1
        else:
            self.prs(ge('itu_country_code_ext', 'b'))
            i = 2
        # self.itu_payalod = bs[i: payloadSize]
        self.prs(ge('uuid', 'u', 128))
        print("length: %d payloadSize: %d" % (len(bs), payloadSize))
        self.user_data = bs[16:]

    def dump(self):
        print("UserData")
        super().dump()


class SEI(GrammerUnit):
    UserDataUnregisteredType = 5

    def __init__(self, bs):
        self.payload_type = 0
        i = 0
        while bs[i] == 0xff:
            self.payload_type += 0xff
            i += 1
        self.payload_type += bs[i]
        i += 1
        self.payload_size = 0
        while bs[i] == 0xff:
            self.payload_size += 0xff
            i += 1
        self.payload_size += bs[i]
        i += 1
        self.raw = bs[i:]
        self.data = None
        if self.payload_type == SEI.UserDataUnregisteredType:
            self.data = UserDataUnregistered(self.raw, self.payload_size)

    def dump(self):
        print("SEI")
        print("type: %d size: %d" % (self.payload_type, self.payload_size))
        if self.data:
            self.data.dump()
        else:
            bin.dump(self.raw)


class SPS(GrammerUnit):

    def prs(self, ge):
        GrammerUnit._geparse(self, self.bsm, ge)

    def __init__(self, bs):
        self.bsm = bin.BitStreamM(bs)
        gelst = [ge('profile_idc', 'u', 8),
                 ge('constraint_set_flag', 'u', 8),
                 ge('level_idc', 'u', 8),
                 ge('seq_parameter_set_id', 'ue'),
                 ]
        self._geparselst(self.bsm, gelst)
        # TODO
        gelst = [ge('log2_max_frame_num', 'ue',
                    post=lambda x:x + 4),
                 ge('pic_order_cnt_type', 'ue')
                 ]
        self._geparselst(self.bsm, gelst)
        if self.pic_order_cnt_type == 0:
            self.prs(ge('log2_max_pic_order_cnt_lsb', 'ue',
                        post=lambda x: x + 4))
        elif self.pic_order_cnt_type == 1:
            self.prs(ge('delta_pic_order_always_zero_flag', 'u'))
            self.prs(ge('offset_for_non_ref_pic', 'se'))
            self.prs(ge('offset_for_top_to_bottom_field', 'se'))
            self.prs(ge('num_ref_frames_in_pic_order_cnt_cycle', 'ue'))
            lst = []
            for i in range(self.num_ref_frames_in_pic_order_cnt_cycle):
                # TODO: need impl REPEAT feature
                lst.append(self.bsm.se())
            self._ins('offset_for_ref_frame', lst)
        gelst = [ge('max_num_ref_frames', 'ue'),
                 ge('gaps_in_frame_num_value_allowed_flag', 'u'),
                 ge('pic_width_in_mbs', 'ue', post=inc),
                 ge('pic_height_in_map_units', 'ue', post=inc),
                 ge('frame_mbs_only_flag', 'u'),
                 ge('mb_adpative_frame_field_flag', 'u',
                     cond=lambda: not self.frame_mbs_only_flag),
                 ge('direct_8x8_inference_flag', 'u'),
                 ge('frame_cropping_flag', 'u'),
                 ge('frame_crop_left_offset', 'ue',
                     cond=lambda: self.frame_cropping_flag),
                 ge('frame_crop_right_offset', 'ue',
                     cond=lambda: self.frame_cropping_flag),
                 ge('frame_crop_top_offset', 'ue',
                     cond=lambda: self.frame_cropping_flag),
                 ge('frame_crop_bottom_offset', 'ue',
                     cond=lambda:self.frame_cropping_flag),
                 ge('vui_parameter_present_flag', 'u')
                 ]
        self._geparselst(self.bsm, gelst)
        if self.vui_parameter_present_flag:
            self.VUI = VUI(self.bsm)

    _ins = GrammerUnit._ins
    _geparselst = GrammerUnit._geparselst

    def dump(self):
        print("SPS")
        super().dump()
        k, v = "Profile", semantic.showProfile(self)
        dumpkv(k, v)
        if self.vui_parameter_present_flag:
            self.VUI.dump()


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
                 ]
        self._geparselst(self.bsm, gelst)
        if self.num_slice_groups > 1:
            raise Exception('PPS slice_group_map_type not impl')
        gelst = [ge('num_ref_idx_10_active', 'ue', post=inc),
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
        if SPSl != None and self.seq_parameter_set_id < len(SPSl):
            self.SPS = SPSl[self.seq_parameter_set_id]
        else:
            raise Exception('not find SPS ' + str(self.seq_parameter_set_id))

    _ins = GrammerUnit._ins
    _geparselst = GrammerUnit._geparselst

    def dump(self):
        print("PPS")
        super().dump()


class SliceHead(GrammerUnit):

    def __init__(self, nal, PPSl=[]):
        self.nal = nal
        self.bsm = bin.BitStreamM(nal.rbsp)
        self.prsHead(PPSl)
        self.prsData()

    def prsHead(self, PPSl):
        gelst = [ge('first_mb_in_slice', 'ue'),
                 ge('slice_type', 'ue'),
                 ge('pic_parameter_set_id', 'ue'),
                 ]
        self._geparselst(self.bsm, gelst)
        self.PPS = PPSl[self.pic_parameter_set_id]
        self.SPS = self.PPS.SPS
        self.descriptorIdx = self.PPS.entropy_coding_mode_flag
        gelst = [ge('frame_num', 'u', self.SPS.log2_max_frame_num),
                 ge('field_pic_flag', 'u',
                    cond=lambda: not self.SPS.frame_mbs_only_flag),
                 ge('bottom_filed_flag', 'u',
                    cond='field_pic_flag'),
                 ge('idr_pic_id', 'ue',
                    cond=lambda: self.nal.nal_unit_type == 5),
                 ge('pic_order_cnt_lsb', 'u',
                    # self.SPS.log2_max_pic_order_cnt_lsb,
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
                    cond=lambda:self.isSliceType('P', 'SP', 'B')),
                 ge('num_ref_idx_10_active', 'ue',
                    cond=lambda:self.isSliceType('P', 'SP', 'B')
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
        if self.PPS.entropy_coding_mode_flag and self.isSliceType('I', 'SI'):
            self.prs(ge('cabac_init_idc', 'ue'))
        self.prs(ge('slice_qp_delta', 'se'))
        if self.isSliceType('SP', 'SI'):
            if self.isSliceType('SP'):
                self.prs(ge('sp_for_switch_flag', 'u'))
            self.prs(ge('slice_qs_delta', 'se'))
        if self.PPS.deblocking_filter_ctrl_present_flag:
            self.prs(ge('disable_deblocking_filter_idc', 'ue'))
            if self.disable_deblocking_filter_idc != 1:
                self.prs(
                    ge('slice_alpha_c0_offset', 'se', post=lambda x: x * 2))
                self.prs(ge('slice_beta_offset', 'se', post=lambda x: x * 2))
        if self.PPS.num_slice_groups > 1:
            raise Exception('SliceHead num_slice_groups not impl')

    def isSliceType(self, *ts):
        return semantic.isSliceType(self.slice_type, *ts)

    def prs(self, ge):
        GrammerUnit._geparse(self, self.bsm, ge)

    def parseRefPicListReorderingIn(self):
        while 1:
            self.prs(ge('reordering_of_pic_nums_idc', 'ue'))
            if self.reordering_of_pic_nums_idc in [0, 1]:
                self.prs(ge('abs_diff_pic_num', 'ue', post=inc))
            elif self.reordering_of_pic_nums_idc == 2:
                self.prs(ge('long_term_pic_num', 'ue'))
            if self.reordering_of_pic_nums_idc == 3:
                break

    def parseRefPicListReordering(self):
        # TODO:
        # these reordering code is override
        if not self.isSliceType('I', 'B'):
            self.prs(ge('ref_pic_list_reordering_flag_l0', 'u'))
            if (self.ref_pic_list_reordering_flag_l0):
                self.parseRefPicListReorderingIn()
        if self.isSliceType('B'):
            self.prs(ge('ref_pic_list_reordering_flag_l1', 'u'))
            if (self.ref_pic_list_reordering_flag_l1):
                self.parseRefPicListReorderingIn()

    def prsPredWeightTbl(self):
        if (self.PPS.weighted_pred_flag and self.isSliceType('P', 'SP')) or (self.PPS.weighted_bipred_flag and self.isSliceType('B')):
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

    def updateMbSize(self):
        if 'mb_adpative_frame_field_flag' not in self.SPS.__dict__:
            self.MbaffFrameFlag = False
        else:
            self.MbaffFrameFlag = (
                self.SPS.mb_adpative_frame_field_flag and not self.field_pic_flag)
        # TODO
        # self.PicHeightInMbs = FrameHeightInMbs / (1 + self.field_pic_flag)
        self.PicSizeInMbs = self.SPS.pic_width_in_mbs * \
            self.SPS.pic_height_in_map_units

    def prsData(self):
        self.updateMbSize()
        if self.PPS.entropy_coding_mode_flag:
            self.bsm.align()
        currMbAddr = self.first_mb_in_slice * (1 + self.MbaffFrameFlag)
        moreDataFlag, prevMbSkipped = 1, 0
        while moreDataFlag:
            if not self.isSliceType('I') and not self.isSliceType('SI'):
                if not self.PPS.entropy_coding_mode_flag:
                    self.prs(ge('mb_skip_run', 'ue'))
                    prevMbSkipped = self.mb_skip_run > 0
                    for i in range(self.mb_skip_run):
                        currMbAddr = self.NextMbAddress(currMbAddr)
                    moreDataFlag = self.bsm.isMoreData()
                else:
                    self.prs(ge('mb_skip_flag', 'ae'))
                    moreDataFlag = not self.mb_skip_flag
            if moreDataFlag:
                if self.MbaffFrameFlag and (currMbAddr % 2 == 0 or (currMbAddr % 2 == 1 and prevMbSkipped)):
                    self.prs(ge('mb_field_decoding_flag', 'u|ae'))
            self.macroblock_layer()
            # TODO, more marcoblock
            break
            if not self.PPS.entropy_coding_mode_flag:
                moreDataFlag = self.bsm.isMoreData()
            else:
                if not self.isSliceType('I') or not self.isSliceType('SI'):
                    prevMbSkipped = self.mb_skip_flag
                if MbaffFrameFlag and currMbAddr % 2 == 0:
                    moreDataFlag = 1
                else:
                    self.prs(ge('end_of_slice_flag', 'ae'))
                    moreDataFlag = not self.end_of_slice_flag
            currMbAddr = self.NextMbAddress(currMbAddr)
        # end of slice data

    def macroblock_layer(self):
        self.prs(ge('mb_type', 'ue|ae'))
        MBType = semantic.MbTypeName(self.slice_type, self.mb_type)
        if MBType == "I_PCM":
            # TODO
            pass
        else:
            mbtype0 = semantic.MbPartPredMode(self.slice_type, self.mb_type, 0)
            print("mbtype0 " + mbtype0)
            if (mbtype0 != "Intra_4x4" and
                    mbtype0 != "Intra_16x16" and
                    semantic.NumMbPart(self.mb_type) == 4):
                self.sub_mb_pred()
            else:
                self.mb_pred()
            if mbtype0 != "Intra_16x16":
                self.prs(ge("coded_block_pattern", "me|ae"))
            luma, chroma = semantic.CodedBlockPattern(self.mb_type)
            if (luma > 0 or chroma > 0 or mbtype0 == "Intra_16x16"):
                self.prs(ge("mb_qp_delta", "se|ae"))
                self.residual()

    _ins = GrammerUnit._ins
    _geparselst = GrammerUnit._geparselst

    def residual(self):
        if not self.PPS.entropy_coding_mode_flag:
            residualFn = self.residual_block_cavlc
        else:
            residualFn = self.residual_block_cabac
        mbtype0 = semantic.MbPartPredMode(self.slice_type, self.mb_type, 0)
        if mbtype0 == "Intra_16x16":
            residualFn("Intra16x16DCLevel", 16)
        luma, chroma = semantic.CodedBlockPattern(self.mb_type)
        for i8x8 in range(4):
            for i4x4 in range(4):
                pass

    def sel_nC(self, target=None):
        if target == "ChromaDCLevel":
            print("TODO: select nC by chroma_format_idc")
            return 0
        if target == "Intra16x16DCLevel":
            luma4x4BlkIdx = 0

    def residual_block_cavlc(self, coeffLevel, maxNumCoeff):
        coeffLevel = [0 for i in range(maxNumCoeff)]
        self.prs(ge('coeff_token', 'ce'))
        pass

    def mb_pred(self):
        mbtype0 = semantic.MbPartPredMode(self.slice_type, self.mb_type, 0)
        if mbtype0 == "Intra_4x4" or mbtype0 == "Intra_16x16":
            if mbtype0 == "Intra_4x4":
                print("TODO")
            if mbtype0 == "Intra_8x8":
                print("TODO")
            self.prs(ge('intra_chroma_pred_mode', "ue|ae"))
            print(self.intra_chroma_pred_mode)
        elif mbtype0 == "Direct":
            print("mbtype0 Direct TODO")

    def NextMbAddress(self, n):
        i = n + 1
        # TODO
        while i < self.PicSizeInMbs and False:
            # and MbToSliceGroupMap[i] != MbToSliceGroupMap[n]:
            # always False when num_slice_groups == 1
            i += 1
        return i

    def dump(self):
        print("Slice")
        super().dump()
        k, v = "SliceType", semantic.SliceType(self.slice_type)
        dumpkv(k, v)
        k, v = 'MBType', semantic.MbTypeName(self.slice_type, self.mb_type)
        dumpkv(k, v)
