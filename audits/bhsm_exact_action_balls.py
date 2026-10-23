"""Shared exact action-ball API; eight dyadic component arrays per matrix."""
import numpy as np
from bhsm_baton_zoo_exact_acb_packets import encode,decode_matrix,decode_array,mutually_contains


def export_acb_exact_dyadic(matrix,prefix):
    packet=encode(matrix,prefix);packet.pop(prefix+'_exact_shape')
    return packet


def parse_acb_exact_dyadic(packet,prefix):
    supplied=dict(packet);supplied[prefix+'_exact_shape']=np.asarray(packet[prefix+'_real_mid_exponent'].shape,int)
    return decode_matrix(supplied,prefix)


def parse_acb_exact_array(packet,prefix):
    supplied=dict(packet);supplied[prefix+'_exact_shape']=np.asarray(packet[prefix+'_real_mid_exponent'].shape,int)
    return decode_array(supplied,prefix)
