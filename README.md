# toy264

a toy codec of H.264

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/bff5541c1efc49ae9847e813ccd7c774)](https://www.codacy.com/app/lujing-zui/toy264?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=liuyang1/toy264&amp;utm_campaign=Badge_Grade)
[![Code Health](https://landscape.io/github/liuyang1/toy264/master/landscape.svg?style=flat)](https://landscape.io/github/liuyang1/toy264/master)

only support python3

## syntax element support

- [X] u: unsigned int with n bits
- [X] ue: unsgined Exp-Golomb-coded
- [X] se: signed Exp-Golomb-coded
- [X] b: bytes
- [ ] ae
- [ ] ce: CAVLC
- [ ] me
- [ ] te

## H.261

- [X] picture
- [X] GOB
- [ ] MB

## H.264
### parser list

```
- [X] NALU
- [X] AU
- [X] SPS
    - [ ] high profile support
    - [X] VUI
    - [ ] hrd_param
    - [ ] vcl_hrd_param
- [X] PPS
- [X] SEI
    - [X] user data
- [.] Slice Head
    - [ ] pic_order_cnt_type == 1 case
    - [ ] RefPicListReordering
    - [ ] PicSizeInMbs
    - [X] macro block
    - [ ] mb_pred Intra case
    - [ ] residual_block_cavlc
 ```
