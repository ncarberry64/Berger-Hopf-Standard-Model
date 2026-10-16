"""Independent original two-boundary weak-equation controls, not a field solve."""
from __future__ import annotations

import mpmath as mp
import numpy as np
import pytest

from bhsm.interface.muon_two_collar_weak_domain import two_collar_weak_domain_jets


KEYS = ('value','x','y','xy')


def family():
    rng = np.random.default_rng(202610161152)
    def matrix(a):
        return mp.matrix([[mp.mpc(float(v.real),float(v.imag)) for v in row]
                          for row in np.asarray(a,complex)])
    def polynomial(n):
        contacts = [matrix(.07*(rng.normal(size=(n,n))+1j*rng.normal(size=(n,n))))
                    for _ in range(3)]
        return lambda x,y: mp.eye(n)+x*contacts[0]+y*contacts[1]+x*y*contacts[2]
    r,u,dual = polynomial(6),polynomial(6),polynomial(6)
    j0 = matrix(np.block([[np.zeros((3,3)),np.eye(3)],[-np.eye(3),np.zeros((3,3))]]))
    b0 = mp.zeros(2,6)
    b0[0,0]=1; b0[1,1]=1
    c0 = b0.T
    pl = matrix(np.diag([1,0])); pr = mp.eye(2)-pl
    t0 = matrix([[0,.23+.11j],[.23-.11j,0]])
    tx = matrix([[0,.12+.08j],[-.07+.03j,0]])
    ty = matrix([[0,-.17+.04j],[.09-.13j,0]])
    txy = matrix([[0,.06-.05j],[.02+.09j,0]])
    def data(x,y):
        rr,uu,dd = r(x,y),u(x,y),dual(x,y)
        b,j = b0*rr,j0*rr
        return dict(plus_green=j,minus_green=-dd**-1*j*uu**-1,
            geometric_right=uu,geometric_right_inverse=uu**-1,geometric_left_dual=dd,
            plus_normalized_trace=b,minus_normalized_trace=b*uu**-1,
            plus_canonical_source=c0,minus_canonical_source=dd**-1*c0,
            surface_kernel=t0+x*tx+y*ty+x*y*txy)
    def literal(x,y):
        d=data(x,y)
        # Solve the ORIGINAL equation J(U^-1 z-x)=C T(PL b+ x+PR b- z).
        c = d['plus_canonical_source']*pl+d['geometric_left_dual']*d['minus_canonical_source']*pr
        left = d['plus_green']*d['geometric_right_inverse']-c*d['surface_kernel']*pr*d['minus_normalized_trace']
        right = d['plus_green']+c*d['surface_kernel']*pl*d['plus_normalized_trace']
        return left**-1*right
    return data,literal


def jets(fun):
    zero=mp.mpf(0)
    result=dict(value=fun(zero,zero),x=mp.diff(lambda x:fun(x,zero),zero),
        y=mp.diff(lambda y:fun(zero,y),zero),
        xy=mp.diff(lambda x:mp.diff(lambda y:fun(x,y),zero),zero))
    return {key:np.array(value.tolist(),complex) for key,value in result.items()}


def inputs():
    with mp.workdps(64):
        data,literal=family()
        result={name:jets(lambda x,y,n=name:data(x,y)[n]) for name in data(mp.mpf(0),mp.mpf(0))}
        expected=jets(literal)
    result['left_chiral_projector']=np.diag([1,0])
    return result,expected


def test_original_two_boundary_equation_and_independent_mixed_domain_jets():
    data,expected=inputs()
    result=two_collar_weak_domain_jets(**data)
    for key in KEYS:
        assert np.max(abs(result['right_minus_from_plus'][key]-expected[key])) < 2e-13
    for name in ('original_weak_surface_rows','original_split_trace_rows',
            'original_two_trace_domain_graph_rows','original_two_trace_green_rows',
            'geometric_green_alignment_rows','geometric_inverse_rows',
            'geometric_reverse_inverse_rows','plus_selected_trace_jump_rows',
            'minus_selected_trace_jump_rows','isotropy_rows','nilpotence_rows',
            'Higgs_left_left_rows','Higgs_right_right_rows'):
        assert max(np.max(abs(a)) for a in result[name].values()) < 2e-13, name
    assert result['original_two_trace_graph']['value'].shape == (12,6)
    assert result['original_two_trace_domain_rows']['value'].shape == (6,12)
    assert result['original_boundary_trace_count'] == 12
    assert result['additional_boundary_trace_copies'] == 0
    assert result['full_fiber_rows_deleted'] == 0
    assert np.linalg.norm(result['original_free_graph_surface_defect']['value']) > .1
    assert np.linalg.norm(result['right_minus_from_plus']['xy']) > .01
    assert np.linalg.norm(data['geometric_left_dual']['x']-data['geometric_right']['x'].conj().T) > .1
    assert not result['full_physical_derivative_gate_passed']
    assert result['original_coupled_corrections_applied'] == 0


def test_surface_free_limit_is_the_original_geometric_graph():
    data,_=inputs()
    data['surface_kernel']={key:np.zeros((2,2),complex) for key in KEYS}
    result=two_collar_weak_domain_jets(**data)
    for key in KEYS:
        assert np.max(abs(result['right_minus_from_plus'][key]-data['geometric_right'][key])) < 1e-14


def test_bad_geometry_and_nonisotropy_are_reported_and_doubling_rejected():
    data,_=inputs()
    data['geometric_right_inverse']['x'][0,0]+=.2
    result=two_collar_weak_domain_jets(**data)
    assert np.max(abs(result['geometric_inverse_rows']['x'])) > .1
    assert np.max(abs(result['original_weak_surface_rows']['x'])) > .1
    data,_=inputs()
    data['plus_canonical_source']['value'][3,0]+=.3
    result=two_collar_weak_domain_jets(**data)
    assert np.max(abs(result['isotropy_rows']['value'])) > .1
    assert result['local_equations_returned_without_global_physical_admission']
    data,_=inputs()
    data['plus_normalized_trace']={key:np.hstack((a,a)) for key,a in data['plus_normalized_trace'].items()}
    with pytest.raises(ValueError,match='same-shape'):
        two_collar_weak_domain_jets(**data)
