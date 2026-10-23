import numpy as np
from bhsm.interface.muon_inherited_wall_lepton_application import inherited_wall_lepton_application
from bhsm.interface.muon_birth_finite_normal_phase import load_finite_normal_endpoint
from bhsm.interface.muon_parent_gauge_geometry_correction import ROOT
from bhsm.interface.muon_primal_trace_enriched_lepton_operator import primal_trace_enriched_lepton_operator
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation


def test_unprojected_wall_contact_matches_original_covariant_dirac_equation():
    base=load_finite_normal_endpoint('artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1',side='outgoing')
    with np.load(ROOT/'artifacts/muon_inherited_finite_normal_phase_20261011/run_1/application.npz',allow_pickle=False) as a:
        raw=a['stage_independent_raw'][0];wall=a['stage_wall_gauge'][0]
    r=inherited_wall_lepton_application(raw,wall,base['representation'])
    old=primal_trace_enriched_lepton_operator(raw,base['representation'])
    generators=lepton_unit_trace_gauge_representation()['generators']
    delta=wall-old['wall_trace'];alpha=lepton_current_hilbert_representation()['alpha']
    independent=-1j*sum(alpha[k]@sum(delta[k+2,c]*generators[c] for c in range(4)) for k in range(3))/r['R4']
    independent-=1j*sum(delta[0,c]*generators[c] for c in range(4))/r['N']
    np.testing.assert_allclose(r['H_can_profile_contact'],independent,rtol=1e-12,atol=1e-15)
    np.testing.assert_allclose(r['reconstructed_wall'],wall,rtol=0,atol=2e-16)
    assert np.linalg.norm(r['H_can_profile_contact'])>1e-12
    np.testing.assert_allclose(r['H_can'],r['H_can'].conj().T,rtol=0,atol=1e-14)


def test_zero_addendum_recovers_original_action_without_new_connection():
    base=load_finite_normal_endpoint('artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1',side='outgoing')
    raw=base['raw'];old=primal_trace_enriched_lepton_operator(raw,base['representation'])
    r=inherited_wall_lepton_application(raw,old['wall_trace'],base['representation'])
    np.testing.assert_allclose(r['H_can'],old['H_can'],rtol=0,atol=2e-15)
    np.testing.assert_allclose(r['omitted_profile_wall'],0,rtol=0,atol=2e-16)
