import sys
from pathlib import Path

import pytest
from flint import arb_mat, ctx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from freeze_n12_gate7_formation_action_basis import orthonormal_kernel_frame


def test_complete_kernel_frame_and_raw_action_metric():
    with ctx.workprec(256):
        J=arb_mat([[1,0,0]])
        projector=arb_mat([[0,0,0],[0,1,0],[0,0,1]])
        Q=orthonormal_kernel_frame(projector,arb_mat([[7,-8],[1,1],[1,-1]]))
        assert J*Q==arb_mat(1,2)
        gram=Q.transpose()*Q
        assert all((gram[i,j]-int(i==j)).contains(0) for i in range(2) for j in range(2))
        W=arb_mat([[2,0,0],[0,3,0],[0,0,5]])
        raw=W.solve(Q)
        metric_gram=raw.transpose()*W.transpose()*W*raw
        assert all((metric_gram[i,j]-int(i==j)).contains(0) for i in range(2) for j in range(2))


def test_no_zero_direction_replaced_by_arbitrary_kernel_seed():
    with pytest.raises(ArithmeticError,match='independence'):
        orthonormal_kernel_frame(arb_mat([[0,0],[0,1]]),arb_mat([[1],[0]]))
