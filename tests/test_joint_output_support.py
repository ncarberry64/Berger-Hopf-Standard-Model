from flint import arb,arb_mat,ctx
from bhsm.interface.joint_output_support import box_image_norm,euclidean_image_norm,joint_constant_support


def test_output_gram_retains_opposite_signs_across_output_rows():
    old=ctx.prec
    try:
        ctx.prec=256
        matrix=arb_mat([[1,1],[1,-1]])
        assert box_image_norm(matrix)==2
        assert euclidean_image_norm(matrix)>=arb(2).sqrt()
        assert euclidean_image_norm(matrix)<arb('1.415')
        assert joint_constant_support(matrix,[(0,2,'box')])==2
        uncertain=arb_mat([[arb(1,'1e-12'),1],[1,arb(-1,'1e-12')]])
        assert box_image_norm(uncertain)>=2
        assert box_image_norm(uncertain)<arb('2.000001')
    finally:
        ctx.prec=old
