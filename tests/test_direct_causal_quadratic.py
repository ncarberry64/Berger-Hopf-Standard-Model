from itertools import product
import numpy as np
import pytest
from flint import arb, arb_mat, ctx
from bhsm.interface.direct_causal_quadratic import bound_causal_quadratic_family, transpose_inputs


@pytest.fixture(autouse=True)
def reference_precision():
    previous=ctx.prec;ctx.prec=768
    yield
    ctx.prec=previous


def empty(n,family):
    q={'LL':1,'LT':n,'TT':n*n}[family]
    return {key:arb_mat(n,q) for key in ('00','01','10','11')}


def test_neighbor_diagonals_cancel_before_later_norms():
    blocks=[empty(1,'LL'),empty(1,'LL')]
    blocks[0]['11']=arb_mat([[3]]);blocks[1]['00']=arb_mat([[6]])
    result=bound_causal_quadratic_family(np.array([[[0.]], [[-2.]]]),np.ones((3,1)),blocks.__getitem__,'LL',0)
    assert result['signed_center_node_bounds_upper'][2]==[0,0]
    assert 3<=result['frozen_inverse_quadratic_coefficients_upper'][0]<3.0000001
    assert result['all_intervals_covered'] and result['atoms']==3


def test_tt_adjacent_cancellation_requires_cartesian_transpose():
    blocks=[empty(2,'TT'),empty(2,'TT')]
    cross=arb_mat([[1,2,3,4],[-1,4,2,3]])
    blocks[1]['10']=cross;blocks[1]['01']=-transpose_inputs(cross,2)
    result=bound_causal_quadratic_family(np.zeros((2,2,2)),np.array([[0,0],[2,-1],[2,-1]]),blocks.__getitem__,'TT',0)
    assert result['frozen_inverse_quadratic_coefficients_upper']==[0,0]


def test_lt_keeps_different_ordered_input_terms():
    blocks=[empty(1,'LT'),empty(1,'LT')]
    blocks[1]['01']=arb_mat([[3]]);blocks[1]['10']=arb_mat([[-3]])
    result=bound_causal_quadratic_family(np.zeros((2,1,1)),np.ones((3,1)),blocks.__getitem__,'LT',0)
    # l1=t2=1, l2=-1, t1=1 gives 6; joining the two tensors would falsely give 0.
    assert 6<=result['frozen_inverse_quadratic_coefficients_upper'][0]<6.0000001
    assert result['mixed_two_radius_factor']==2


@pytest.mark.parametrize('family',['LL','LT','TT'])
def test_vector_recurrence_interval_corners_and_nonunit_output_axes(family):
    n=2;q={'LL':1,'LT':2,'TT':4}[family]
    blocks=[empty(n,family) for _ in range(3)]
    for i in range(3):
        for k,key in enumerate(('00','01','10','11')):
            if i==0 and key!='11':continue
            blocks[i][key]=arb_mat(n,q,[arb(((i+2*k+j)%7)-3)/8 for j in range(n*q)])
    blocks[1]['00'][0,0]+=arb(0,.125)
    maps=np.array([[[0,0],[0,0]],[[1,.5],[-.25,1]],[[0,1],[-1,.5]]])
    axes=np.array([[0,0],[2,-1],[-1,.5],[.5,1]])
    result=bound_causal_quadratic_family(maps,axes,blocks.__getitem__,family,0,precision=128,block_size=2)
    bound=[arb(v) for v in result['frozen_inverse_quadratic_coefficients_upper']]
    # Deterministic input corners for a unit block-sup ball. For LL use
    # scalar +/-1; LT one scalar family and one vector family. LL and TT
    # evaluate the quadratic form of one history, while LT is bilinear.
    for signs in product((-1,1),repeat=6):
        us=[None]+[([arb(signs[j])] if family!='TT' else [arb(signs[j])/2,arb(signs[j+3])/2]) for j in range(3)]
        vs=[None]+[([arb(signs[j+3])] if family=='LL' else [arb(signs[j+3])/2,arb(signs[j])/2]) for j in range(3)]
        if family in ('LL','TT'):vs=us
        for corner in (-1,1):
            z=arb_mat(n,1)
            for i in range(3):
                z=arb_mat(maps[i].tolist())*z
                for key in ('00','01','10','11'):
                    left,right=i+int(key[0]),i+int(key[1])
                    if left==0 or right==0:continue
                    matrix=arb_mat(n,q,blocks[i][key].entries())
                    if i==1 and key=='00':matrix[0,0]=matrix[0,0].mid()+arb(corner)/8
                    inputs=arb_mat(q,1,[u*v for u in us[left] for v in vs[right]])
                    z+=matrix*inputs
                e=arb_mat(n,1,axes[i+1].tolist());l=(e.transpose()*z)[0,0]
                t=z-e*l
                assert abs(l).upper()<=bound[0]
                assert sum(v*v for v in t.entries()).sqrt().upper()<=bound[1]
    assert result['error_transport']['maximum_node_error_norm_upper']>0
    assert not result['neighborhood_remainder_enclosed']


def test_selected_component_does_not_read_or_claim_missing_intervals():
    seen=[]
    def read(i):
        seen.append(i);assert i==1
        result=empty(1,'LL');result['11']=arb_mat([[2]]);return result
    result=bound_causal_quadratic_family(np.ones((3,1,1)),np.ones((4,1)),read,'LL',0,active_intervals=[1])
    assert seen==[1] and not result['all_intervals_covered']
    assert 'ISOLATED_ADDITIVE' in result['scope']
    assert result['signed_center_node_bounds_upper'][3][0]>=2


def test_map_perturbation_lifts_source_uncertainty_once():
    blocks=[empty(1,'LL')];blocks[0]['11']=arb_mat([[arb(2,.125)]])
    result=bound_causal_quadratic_family(np.zeros((1,1,1)),np.ones((2,1)),blocks.__getitem__,'LL',.25)
    raw=result['signed_center_bounds_upper'][0]
    error=result['error_transport']['maximum_node_error_norm_upper']
    expected=raw+(.25*raw+error)/.75
    assert result['frozen_inverse_quadratic_coefficients_upper'][0]>=expected
    assert result['frozen_inverse_quadratic_coefficients_upper'][0]<expected+1e-12


def test_missing_blocks_initial_input_and_precision_changes_fail():
    maps=np.ones((2,1,1));axes=np.ones((3,1));previous=ctx.prec
    with pytest.raises(ValueError,match='four'):
        bound_causal_quadratic_family(maps,axes,lambda i:{'11':[[1]]},'LL',0)
    bad=empty(1,'LL');bad['00']=arb_mat([[1]])
    with pytest.raises(ValueError,match='fixed initial'):
        bound_causal_quadratic_family(maps,axes,lambda i:bad,'LL',0)
    def changed(i):ctx.prec=100;return empty(1,'LL')
    with pytest.raises(RuntimeError,match='precision'):
        bound_causal_quadratic_family(maps,axes,changed,'LL',0)
    assert ctx.prec==previous


@pytest.mark.parametrize('indices',[[],[0,0],[-1],[2],[True]])
def test_bad_selection_fails(indices):
    with pytest.raises(ValueError):
        bound_causal_quadratic_family(np.ones((2,1,1)),np.ones((3,1)),lambda i:empty(1,'LL'),'LL',0,active_intervals=indices)


@pytest.mark.parametrize('gain',[-1,1,float('nan')])
def test_invalid_map_gain_rejected_before_loading_sources(gain):
    def forbidden(i):raise AssertionError('invalid gain should fail before source I/O')
    with pytest.raises(ValueError):
        bound_causal_quadratic_family(np.ones((2,1,1)),np.ones((3,1)),forbidden,'LL',gain)
