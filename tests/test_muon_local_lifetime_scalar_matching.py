from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_local_lifetime_scalar_matching import (
    retained_lambda_field_family,scalar_lambda_candidates,local_joint_matching_scan)
ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module',params=['incoming','outgoing'])
def family(request):return retained_lambda_field_family(request.param,repository=ROOT)


def test_original_full_action_lambda_variation_keeps_gauge_kinetic_and_mixed_blocks(family):
    C=family['proper_frequency_coefficients'];D=family['lambda_H_frequency_derivative']
    assert np.max(abs(family['lambda_H_affinity_residual']))<4e-16
    assert np.linalg.norm(D[0,64:68,64:68])>0
    mask=np.ones(D.shape,bool);mask[0,64:68,64:68]=False
    assert np.max(abs(D[mask]))<1e-13
    with np.load(ROOT/'artifacts/muon_coupled_lorentz_field_symbol_20261011/run_1/application.npz',allow_pickle=False)as a:
        assert np.array_equal(C,a[family['side']+'_proper_frequency_coefficients'])
    assert not family['original_phase_resolved_at_varied_lambda']


def test_scalar_pole_candidates_satisfy_the_complete_gauge_returned_equation(family):
    a=scalar_lambda_candidates(family,frequency=.2)
    assert np.max(a['local_pole_equation_relative_residual'])<5e-14
    assert np.max(a['radial_projection_fractions'])>.999999
    lam=a['local_lambda_candidates'][np.argmax(a['radial_projection_fractions'])]
    assert lam.real>0 and abs(lam.imag)<1e-10
    Q=family['field_quotient_lift'];C=family['proper_frequency_coefficients']+(lam-family['lambda_H_base'])*family['lambda_H_frequency_derivative']
    P=Q.T@sum(C[k]*.2**k for k in range(3))@Q
    hi=np.flatnonzero(np.any(Q[64:68]!=0,axis=0));gi=np.setdiff1d(np.arange(80),hi)
    v=a['scalar_returned_pole_vectors'][:,np.argmax(a['radial_projection_fractions'])]
    full=np.zeros(80,complex);full[hi]=v;full[gi]=-np.linalg.solve(P[np.ix_(gi,gi)],P[np.ix_(gi,hi)]@v)
    assert np.linalg.norm(P@full)/np.linalg.norm(P)/np.linalg.norm(full)<2e-13
    # All gauge return rows are present; this is not a scalar-only pole.
    assert np.linalg.norm(full[gi])>0


def test_local_matching_scan_does_not_replace_a_negative_seed_by_a_global_no_go(family):
    s=local_joint_matching_scan(family,muon_mass_GeV=.10565842526040435,
        electron_mass_GeV=.000510998950905377,scalar_mass_GeV=125.11,
        lifetime_seconds=2.1969803e-6,hbar_GeV_seconds=6.582119569509066e-25,
        frequencies=(.12,.3,.6,2.6))
    assert s['all_local_lambda_candidates'].shape==(4,4)
    assert len(s['positive_radial_candidate_equation_rows'])>0
    assert np.all(s['positive_radial_candidate_equation_rows'][:,1]>0)
    assert not s['global_no_solution_theorem']
    assert not s['physical_unit_or_pole_selected']
