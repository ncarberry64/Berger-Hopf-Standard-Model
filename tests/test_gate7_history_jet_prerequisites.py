"""Prevent promotion of mismatched centers or the auxiliary line border."""
import json
import sys
from pathlib import Path

import numpy as np
from flint import fmpq

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import audit_n12_gate7_history_jet_prerequisites as audit

PACKET = audit.BASE / 'gate7_history_jet_prerequisites_20260927'


def report():
    return json.loads((PACKET / 'report.json').read_bytes())


def test_fixed_state_relabel_outside_saved_descriptor_domain():
    r = report()
    d = r['fixed_state_relabel']
    c, radius = (fmpq(d[k]) for k in ('descriptor_domain_center_exact', 'descriptor_domain_radius_exact'))
    lam_upper = fmpq(r['node13']['lambda_owner']['upper_exact'])
    assert c - radius - lam_upper == fmpq(d['separation_lower_exact'])
    assert (c - lam_upper) / radius == fmpq(d['shift_over_radius_lower_exact'])
    assert c - radius > lam_upper
    assert (c - lam_upper) / radius > 15


def test_projected_line_border_cannot_recover_rayleigh_slope():
    # Adding alpha*I to H' changes lambda' while leaving the projected line RHS
    # and its auxiliary border unchanged. This tests the actual algebraic risk.
    psi = np.array([1., 0.])
    K = np.array([[0., 0., 1.], [0., 2., 0.], [1., 0., 0.]])
    Hp = np.array([[3., 4.], [4., 5.]])
    slopes, solutions = [], []
    for matrix in (Hp, Hp + 7 * np.eye(2)):
        slope = psi @ matrix @ psi
        rhs = np.r_[-(matrix @ psi - slope * psi), 0.]
        slopes.append(slope)
        solutions.append(np.linalg.solve(K, rhs))
    assert slopes == [3., 10.]
    np.testing.assert_array_equal(solutions[0], solutions[1])
    assert solutions[0][-1] == 0.
    assert report()['saved_derivative']['line_border_is_eigenvalue_derivative'] is False


def test_partial_covector_information_is_not_full_history_authority():
    r = report()
    assert fmpq(r['saved_derivative']['cpsi_Dlambda_Psi']['lower_exact']) > 0
    assert r['historical_covector']['same_center'] is False
    assert r['historical_covector']['weighted_center_distance_diagnostic'] > 3
    assert r['historical_jet']['nonlinear_transfer_certified'] is False
    assert r['comparisons']['old_vs_new'] is None
    assert r['comparisons']['owner_vs_new'] is None
    assert r['comparisons']['new_projector_uncertainty'] is None


def test_frozen_inputs_replay_and_fail_closed_flags():
    r = report()
    for path, sha in r['source_SHA256'].items():
        assert audit.digest(audit.ROOT / path) == sha
    receipt = json.loads((PACKET / 'reproduction.json').read_bytes())
    assert audit.digest(PACKET / 'report.json') == receipt['report_SHA256']
    assert receipt['fresh_processes'] == 2 and receipt['byte_identical']
    assert r['status'] == 'SAVED_OPERAND_HISTORY_JET_PREREQUISITES_CHECKED'
    for key in ('independent_descriptor_column_added', 'scientific_producers_run',
                'center_modified', 'new_history_jet_certified', 'center_certificate_promoted',
                'tolerances_changed', 'Layer_C_rebound', 'nonlinear_campaign_started',
                'surface_core_continuation_performed', 'Gate7_closed', 'FULL_BHSM_COMPLETE'):
        assert r[key] is False
