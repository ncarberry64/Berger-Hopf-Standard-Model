import numpy as np
import pytest
from bhsm.interface.muon_chronological_common_y_current import common_y_current_chunk


def test_all_four_coupled_source_orders_against_one_full_nonsymmetric_inverse():
    rng=np.random.default_rng(84176);n,d,c=2,6,4;rows=np.array([1,4])
    rnd=lambda s:rng.normal(size=s)+1j*rng.normal(size=s)
    K=rnd((n*d,n*d))+12*np.eye(n*d)
    rg,lg=rnd((n,d,c)),rnd((n,d,c));rh,lh=np.zeros_like(rg),np.zeros_like(lg)
    rg[:,rows]=0;lg[:,rows]=0;rh[:,rows]=rnd((n,2,c));lh[:,rows]=rnd((n,2,c))
    def data(y):
        r,l=rg+y*rh,lg+y*lh
        return dict(original_literal_right_current_source=r,original_literal_left_transpose_source=l,
            original_current_response=np.linalg.solve(K,r.reshape(n*d,c)).reshape(n,d,c),
            original_transpose_current_adjoint=np.linalg.solve(K.T,l.reshape(n*d,c)).reshape(n,d,c))
    ym,ye=.07,.002;a=common_y_current_chunk(ym,ye,data(ym),data(ye),scalar_rows=rows)
    flat=lambda x:x.reshape(n*d,c)
    u=[np.linalg.solve(K,flat(r))for r in(rg,rh)]
    expected=np.array([flat(l).T@v for l,v in((lg,u[0]),(lg,u[1]),(lh,u[0]),(lh,u[1]))])
    np.testing.assert_allclose(a['ordered_GG_GH_HG_HH'],expected,rtol=2e-12,atol=2e-13)
    np.testing.assert_allclose(a['ordered_GG_GH_HG_HH'],a['independent_transpose_ordered_GG_GH_HG_HH'],rtol=2e-12,atol=2e-13)
    np.testing.assert_allclose(a['source_polynomial_paired_current'],a['independent_family_binary_difference'],rtol=3e-12,atol=2e-13)
    assert np.linalg.norm(expected[1])>.1 and np.linalg.norm(expected[2])>.1
    assert a['GG_paired_coefficient_is_algebraic_zero']


def test_common_gauge_source_and_real_fixed_y_are_action_requirements():
    zero=np.zeros((1,3,2),complex)
    a=dict(original_literal_right_current_source=zero.copy(),original_literal_left_transpose_source=zero.copy(),
           original_current_response=zero.copy(),original_transpose_current_adjoint=zero.copy())
    with pytest.raises(ValueError,match='REAL'):common_y_current_chunk(.03+0j,.001,a,a,scalar_rows=np.array([2]))
    b={k:v.copy()for k,v in a.items()};b['original_literal_right_current_source'][0,0,0]=1e-30
    with pytest.raises(ValueError,match='identical'):common_y_current_chunk(.03,.001,a,b,scalar_rows=np.array([2]))
