"""Action/frame and derivative checks; test fields are not physical states."""
import numpy as np
import pytest

from bhsm.interface.muon_intrinsic_lepton_primal import (
    intrinsic_round_dirac_coefficients, lepton_primal_application,
)
from bhsm.interface.muon_native_dirac_hamiltonian import (
    canonical_lepton_hamiltonian_maps, canonical_product_factor_contract,
    electromagnetic_hamiltonian_source_maps, fixed_y_higgs_hamiltonian,
    inherited_product_factor_maps, lepton_current_hilbert_representation,
    product_factor_form_jets, retained_e1_source_vertices,
)


def test_inherited_full_fiber_charge_and_clifford_maps():
    r = lepton_current_hilbert_representation()
    assert r['Gram'].shape == (18, 18)
    assert np.count_nonzero(np.diag(r['EM_charge']) == 0) == 6
    assert np.count_nonzero(np.diag(r['EM_charge']) == -1) == 12
    for a in range(3):
        for b in range(3):
            np.testing.assert_allclose(r['alpha'][a]@r['alpha'][b]
                +r['alpha'][b]@r['alpha'][a], 2*(a == b)*r['Gram'], atol=2e-15)
    assert not r['CAR_state_selected']


def test_full_complex_H_mass_hermiticity_and_charged_H_ward_term():
    r = lepton_current_hilbert_representation()
    H = np.array([[2+3j, -4+5j]])
    m = fixed_y_higgs_hamiltonian(H)
    np.testing.assert_array_equal(m, m.conj().transpose(0, 2, 1))
    # Charged H1 is retained.  Holding H fixed would drop this nonzero term.
    delta = fixed_y_higgs_hamiltonian(1j*(H@r['Higgs_EM_charge'].T))
    commutator = 1j*(r['EM_charge']@m-m@r['EM_charge'])
    np.testing.assert_allclose(delta, commutator, atol=1e-17)
    assert np.linalg.norm(commutator) > 0
    neutral = fixed_y_higgs_hamiltonian(np.array([[0, 2+3j]]))
    np.testing.assert_array_equal(r['EM_charge']@neutral-neutral@r['EM_charge'], 0)


def test_density_rescaled_hamiltonian_matches_both_literal_weyl_eulers():
    rng = np.random.default_rng(508)
    points, nc = 2, 4
    values = rng.normal(size=(points, 18, nc))+1j*rng.normal(size=(points, 18, nc))
    spatial = rng.normal(size=(points, 3, 18, nc))+1j*rng.normal(size=(points, 3, 18, nc))
    time = rng.normal(size=(points, 18, nc))+1j*rng.normal(size=(points, 18, nc))
    coeff = rng.normal(size=nc)+1j*rng.normal(size=nc)
    N, R4, H4 = .8, 1.2, .3
    H = np.array([[1+2j, 3-4j], [2-1j, -3+4j]])
    Q = lepton_current_hilbert_representation()['EM_charge']
    omega = 1j*np.array([[.3, -.7, .8, -.2], [.4, .1, -.3, .9]])[:, :, None, None]*Q
    hamiltonian = canonical_lepton_hamiltonian_maps(value_map=values,
        spatial_derivative_map=spatial, H=H, R4=R4, gauge_connection=omega)
    scale = R4**1.5
    covtime = N*(time-1.5*H4*values+omega[:, 0]@values)/scale
    covspace = hamiltonian['spatial_covariant_derivative_map']/scale
    psi_values = values/scale
    derivatives = np.concatenate([covtime[:, None], covspace], axis=1)
    operators = intrinsic_round_dirac_coefficients(N=N, R4=R4,
                                                  coordinate_log_R4_rate=N*H4)
    result = lepton_primal_application(coefficients=coeff,
        value_map_L=psi_values[:, :12].reshape(points, 2, 3, 2, nc),
        value_map_e=psi_values[:, 12:].reshape(points, 3, 2, nc),
        derivative_map_L=derivatives[:, :, :12].reshape(points, 4, 2, 3, 2, nc),
        derivative_map_e=derivatives[:, :, 12:].reshape(points, 4, 3, 2, nc),
        H=H, principal_euler_coefficients=operators['principal_euler_coefficients'],
        contracted_spin=operators['contracted_spin'], spin_placement='CONTRACTED_ZERO_ORDER')
    literal = np.concatenate([result['Euler_L'].reshape(points, 12),
                              result['Euler_e'].reshape(points, 6)], axis=1)*scale
    canonical = (1j*time-hamiltonian['hamiltonian_map'])@coeff
    np.testing.assert_allclose(literal, canonical, atol=3e-14)


@pytest.mark.parametrize('n', range(4))
def test_round_S3_signed_blocks_match_retained_product_W(n):
    j = n/2
    levels = np.arange(j, -j-1, -1)
    plus = np.zeros((n+1, n+1), complex)
    for col in range(1, n+1):
        m = levels[col]
        plus[col-1, col] = np.sqrt((j-m)*(j+m+1))
    angular = np.array([(plus+plus.conj().T)/2,
                        (plus-plus.conj().T)/(2j), np.diag(levels)])
    rep = lepton_current_hilbert_representation()
    sigma = rep['alpha'][:, 12:14, 12:14]
    Dhat = 1.5*np.eye(2*(n+1))+2*sum(np.kron(s, J) for s, J in zip(sigma, angular))
    expected = np.r_[np.repeat(-(n+.5), n), np.repeat(n+1.5, n+2)]
    np.testing.assert_allclose(np.linalg.eigvalsh(Dhat), expected, atol=3e-15)
    # The two Weyl signs are separate from spatial signs and family labels.
    assert rep['factor_massless_W'] == 'diag(-Dhat_S3,+Dhat_S3)/R4 on the appropriate Weyl copies'


def test_photon_insertion_matches_differentiated_owned_Hamiltonian():
    rng = np.random.default_rng(43)
    values = rng.normal(size=(2, 18, 3))+1j*rng.normal(size=(2, 18, 3))
    spatial = rng.normal(size=(2, 3, 18, 3))+1j*rng.normal(size=(2, 3, 18, 3))
    H = np.array([[2+3j, -1+4j], [5+1j, -3+2j]])
    dH = np.array([[.2-.1j, -.3+.4j], [.1+.2j, .4-.3j]])
    a = np.array([[.3, -.1, .7, .2], [.4, -.2, .6, .3]])
    e, R4, step = .3, 1.1, 1e-5
    source = electromagnetic_hamiltonian_source_maps(value_map=values, R4=R4,
        photon_one_form=a, electromagnetic_coupling=e, delta_H=dH)
    def apply(s):
        return canonical_lepton_hamiltonian_maps(value_map=values,
            spatial_derivative_map=spatial, H=H+s*dH, R4=R4,
            gauge_connection=s*source['delta_Omega'])['hamiltonian_map']
    np.testing.assert_allclose((apply(step)-apply(-step))/(2*step), source['source_map'], atol=4e-10)
    np.testing.assert_allclose(source['source_operator'],
        source['source_operator'].conj().transpose(0, 2, 1), atol=1e-17)


def test_positive_factor_is_distinct_from_lorentz_evolution():
    v = np.ones((1, 18, 1), complex)
    result = inherited_product_factor_maps(proper_time_derivative_map=v,
        spatial_mass_hamiltonian_map=2*v, factor_temporal_connection_map=1j*v)
    np.testing.assert_array_equal(result['factor_map'], (3+1j)*v)
    assert not result['Lorentz_temporal_Hamiltonian_automatically_used_as_factor_connection']
    assert not result['heat_invocation_permitted']
    contract = canonical_product_factor_contract()
    assert '-[D_tau_factor,W_spatial_mass]' in contract['equations']['positive_bulk']
    assert not contract['scalar_owner_reduction_is_full_interacting_domain_certificate']


def test_time_dependent_gauge_covariance_and_failure_of_naive_lorentz_factor():
    r = lepton_current_hilbert_representation()
    Q, QH = r['EM_charge'], r['Higgs_EM_charge']
    theta, theta_rate = .7, .4
    U = np.diag(np.exp(1j*theta*np.diag(Q)))
    UH = np.diag(np.exp(1j*theta*np.diag(QH)))
    Udot = 1j*theta_rate*Q@U
    H = np.array([[1+2j, 3-4j]])
    V, dt = np.eye(18)[None], (2j*np.eye(18))[None]
    base = canonical_lepton_hamiltonian_maps(value_map=V,
        spatial_derivative_map=np.zeros((1,3,18,18)), H=H,
        R4=1, gauge_connection=np.zeros((1,4,18,18)))
    omega = np.zeros((1,4,18,18), complex)
    omega[0,0] = -Udot@U.conj().T
    transformed = canonical_lepton_hamiltonian_maps(value_map=U@V,
        spatial_derivative_map=np.zeros((1,3,18,18)), H=H@UH.T,
        R4=1, gauge_connection=omega)
    dt_prime = Udot@V+U@dt
    original_factor = inherited_product_factor_maps(proper_time_derivative_map=dt,
        spatial_mass_hamiltonian_map=base['spatial_mass_hamiltonian_map'],
        factor_temporal_connection_map=np.zeros_like(V))['factor_map']
    transformed_factor = inherited_product_factor_maps(proper_time_derivative_map=dt_prime,
        spatial_mass_hamiltonian_map=transformed['spatial_mass_hamiltonian_map'],
        factor_temporal_connection_map=omega[:,0]@(U@V))['factor_map']
    np.testing.assert_allclose(transformed_factor, U@original_factor, atol=1e-15)
    # The Lorentz Euler remains covariant, but ∂tau+H_can does not.
    np.testing.assert_allclose(1j*dt_prime-transformed['hamiltonian_map'],
        U@(1j*dt-base['hamiltonian_map']), atol=1e-15)
    defect = dt_prime+transformed['hamiltonian_map']-U@(dt+base['hamiltonian_map'])
    np.testing.assert_allclose(defect, (1+1j)*Udot@V, atol=1e-15)
    assert np.linalg.norm(defect) > 1


def test_native_factor_temporal_connection_is_not_implicitly_chosen():
    V = np.eye(18)[None]
    with pytest.raises(ValueError, match='factor_temporal_connection_map is required'):
        inherited_product_factor_maps(proper_time_derivative_map=V,
            spatial_mass_hamiltonian_map=V, factor_temporal_connection_map=None)


def test_complete_fixed_core_mixed_contact_and_genuine_jet_match_difference():
    rng = np.random.default_rng(509)
    def matrix():
        return rng.normal(size=(3, 18, 2))+1j*rng.normal(size=(3, 18, 2))
    v, a, av, aj, avj = [matrix() for _ in range(5)]
    w = np.array([.2, .3, .4])
    jets = product_factor_form_jets(value_map=v, factor_map=a, factor_v=av,
        factor_J=aj, factor_vJ=avj, proper_time_unnormalized_Haar_weights=w)
    def K(s, t):
        b = a+s*av+t*aj+s*t*avj
        return np.einsum('p,pik,pil->kl', w, b.conj(), b)
    h = 1e-3
    finite = (K(h,h)-K(h,-h)-K(-h,h)+K(-h,-h))/(4*h*h)
    np.testing.assert_allclose(finite, jets['K_vJ'], atol=1e-8)
    np.testing.assert_allclose(jets['K_vJ'], jets['source_square_contact']
                              +jets['genuine_mixed_first_order_term'])
    assert np.linalg.norm(jets['genuine_mixed_first_order_term']) > 1
    assert np.linalg.eigvalsh(jets['K']).min() > 0
    assert not jets['heat_invocation_permitted']


def test_actual_E1_charge_vertices_and_source_square_contacts():
    e = np.sqrt(4*np.pi/137.035999206)
    result = retained_e1_source_vertices(e)
    r = result['geometry']['R4']
    for a in range(1, 4):
        contact = result['photon_source_square_contacts'][a, a]
        expected = 2*(e/r)**2*np.diag(np.r_[np.zeros(6), np.ones(12)])
        np.testing.assert_allclose(contact, expected, atol=2e-16)
    assert result['geometry']['H4'] != 0
    assert not result['full_physical_photon_lift_or_heat_weighting_evaluated']


@pytest.mark.parametrize('missing', ['H', 'gauge_connection'])
def test_no_silent_background_defaults(missing):
    args = dict(value_map=np.eye(18)[None], spatial_derivative_map=np.zeros((1,3,18,18)),
                H=np.zeros((1,2)), R4=1., gauge_connection=np.zeros((1,4,18,18)))
    args[missing] = None
    with pytest.raises(ValueError, match='required'):
        canonical_lepton_hamiltonian_maps(**args)


def test_noninternal_gauge_and_missing_genuine_jet_are_rejected():
    values = np.eye(18)[None]
    omega = np.zeros((1,4,18,18), complex)
    omega[0,1,0,1], omega[0,1,1,0] = 1, -1
    with pytest.raises(ValueError, match='internally'):
        canonical_lepton_hamiltonian_maps(value_map=values,
            spatial_derivative_map=np.zeros((1,3,18,18)), H=np.zeros((1,2)),
            R4=1, gauge_connection=omega)
    with pytest.raises(ValueError, match='factor_vJ is required'):
        product_factor_form_jets(value_map=values, factor_map=values,
            factor_v=values, factor_J=values, factor_vJ=None,
            proper_time_unnormalized_Haar_weights=[1])


@pytest.mark.parametrize('component', [0, 1, 2, 3])
def test_spin_connection_cannot_pass_as_internal_connection(component):
    omega = np.zeros((1,4,18,18), complex)
    omega[0,component] = 1j*lepton_current_hilbert_representation()['alpha'][0]
    with pytest.raises(ValueError, match='internally'):
        canonical_lepton_hamiltonian_maps(value_map=np.eye(18)[None],
            spatial_derivative_map=np.zeros((1,3,18,18)), H=np.zeros((1,2)),
            R4=1, gauge_connection=omega)
