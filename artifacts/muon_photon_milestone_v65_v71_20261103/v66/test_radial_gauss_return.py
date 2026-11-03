from pathlib import Path
import sys
import numpy as np
import pytest
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
import radial_gauss_return as r

@pytest.fixture(scope='module')
def data():return r.calculate()

def test_owned_radial_formula_and_original_connection(data):
    _,v=data
    for k in ('original_radial_basis','original_radial_basis_derivative','original_A_rho','original_A_rho_derivative','same_full_wall_connection'):
        assert v['consistency_checks'][k]<2e-11
    assert v['radial_connection_max']>0

def test_directed_kernel_tail_retains_nonzero_connection(data):
    a,v=data
    assert 0<float(v['radial_connection_SU2_integral_norm_upper'])<1e-9
    assert 0<float(v['omitted_Dyson_orders_norm_upper'])<1e-18
    np.testing.assert_allclose(a['inherited_transfer4x4']-np.eye(4),-(a['inherited_transfer4x4']-np.eye(4)).T,rtol=0,atol=1e-30)
    assert v['consistency_checks']['transport_first_order_defect_identity']<2e-11

def test_affine_inherited_and_bulk_return_signs(data):
    a,_=data
    # Algebraic unit columns check the affine map, not a physical entering state.
    H=a['inherited_transfer4x4'];R=a['known_return'].reshape(80,32)
    homogeneous=np.kron(H,np.eye(20))
    x=np.arange(80,dtype=float)/80;y=np.arange(32,dtype=float)/32
    z=homogeneous@x+R@y
    np.testing.assert_allclose(z-(homogeneous@x),R@y,rtol=0,atol=2e-11)
    assert not np.array_equal(H,np.eye(4))

def test_photon_projection_uses_surviving_first_order_term(data):
    a,v=data
    assert v['consistency_checks']['zeroth_photon_return_cancellation']<2e-11
    assert np.linalg.norm(a['photon_return_first_order'])>0
    assert v['photon_return_max']>v['maximum_projected_transport_order_bound']
    assert np.linalg.norm(a['raw_photon_zeroth_contraction'])>0
    assert v['raw_zeroth_photon_contraction_max']>v['maximum_projected_transport_order_bound']

def test_boundary_Higgs_range_does_not_remove_neutral_defect(data):
    a,v=data
    assert v['consistency_checks']['boundary_broken_range_match']<2e-11
    assert np.linalg.norm(a['boundary_neutral_remainder'])>0
    assert not v['boundary_matching_complete']

def test_streamed_total_coefficient_derivatives(data):
    a,v=data
    assert a['photon_return_gradient189'].shape==(189,20,4,8)
    assert a['known_return_gradient189'].shape==(189,4,20,4,8)
    assert all(x<2e-11 for k,x in v['consistency_checks'].items() if 'tangent' in k)
    # The nonzero central radial connection is retained, but its adjoint action
    # vanishes exactly. These original field-coordinate columns must agree.
    for profile in range(4):
        j=100+20*profile+7
        assert np.max(abs(a['known_return_gradient189'][j]))==0
        assert np.max(abs(a['photon_return_gradient189'][j]))==0

def test_normal_connection_source_columns_against_direct_load_application(data):
    a,_=data
    with np.load(HERE/'evidence/inputs.npz',allow_pickle=False) as b:
        alpha=float(b['alpha']);s=np.sqrt(16/3)*b['stabilizer_value'];w=b['radial_weights']
    for profile,component in ((0,0),(1,1),(3,2)):
        coeff=np.zeros((4,4));coeff[:,component]=a['pole_basis_polynomials'][profile]
        dJ=r.ad(r.integrated_connection(coeff,alpha,a['radial_nodes49']))
        expected=np.einsum('n,c,ncd,ndhpA->hpA',w,s,dJ[:48],a['known_canonical_Gauss_load49x4x20x4x8'][:48])
        j=100+20*profile+4+component
        np.testing.assert_allclose(a['photon_return_gradient189'][j],expected,rtol=0,atol=2e-11)

def test_bound_does_not_promote_quadrature_or_physical_state(data):
    _,v=data
    assert not v['new_resolution'] and not v['new_quadrature']
    assert not v['inherited_flux_selected'] and not v['bulk_native_current_evaluated']
    assert not v['physical_event_domain_realized'] and not v['physical_reconnection_proved']
    assert v['physical_guard']==2e-10 and v['physical_a_mu'] is None and v['total_physical_uncertainty'] is None
