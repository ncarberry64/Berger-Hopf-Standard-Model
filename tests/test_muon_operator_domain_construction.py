"""Tests of literal quotient/area matching and necessary second incidence."""
import numpy as np
import pytest

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import subprocess
import sys
from bhsm.interface import muon_surface_incidence_second_jet as surface

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location('surface_audit', ROOT/'audits/bhsm_surface_incidence_second_jet_20261015.py')
audit = module_from_spec(spec)
spec.loader.exec_module(audit)
control_inputs = audit.control_inputs
flat_normal_shape_control = audit.flat_normal_shape_control
literal_mp_jets = audit.literal_mp_jets


@pytest.mark.parametrize('seed,lorentzian', ((16131, False), (16153, True)))
def test_full_mixed_jet_against_literal_quotient_and_area(seed, lorentzian):
    G, T, gamma = control_inputs(seed, lorentzian)
    out = surface.surface_incidence_second_jet(
        metric8_jet=G, tangent_inclusion_jet=T, gamma_jet=gamma)
    Q, h, rho, action = literal_mp_jets(G, T, gamma)
    for actual, expected in ((out['quotient_metric_jet'], Q),
            (out['induced_metric_jet'], h), (out['worldvolume_density_jet'], rho),
            (out['signed_area_action_jet'], action)):
        assert np.max(abs(actual-expected)) < 1e-12
    assert out['induced_signature'] == ((1, 3) if lorentzian else (0, 4))
    for axis in (1, 2):
        predicted = (np.sum(out['metric8_covector_density']*G[axis])
            + np.sum(out['tangent_inclusion_covector_density']*T[axis])
            + out['gamma_covector_density']*gamma[axis])
        assert abs(predicted-action[axis]) < 1e-12


def test_flat_normal_shape_first_metric_kernel_retains_second_incidence():
    out, hxy, rhoxy, actionxy = flat_normal_shape_control()
    assert np.max(abs(out['induced_metric_jet'][1:3])) == 0
    assert np.max(abs(out['induced_metric_jet'][3]-hxy)) < 1e-14
    assert abs(out['worldvolume_density_jet'][3]-rhoxy) < 1e-14
    assert abs(out['signed_area_action_jet'][3]-actionxy) < 1e-14
    assert abs(actionxy) > .1


def test_missing_complex_or_degenerate_inputs_are_not_replaced():
    G, T, gamma = control_inputs(16153, True)
    with pytest.raises(ValueError):
        surface.surface_incidence_second_jet(
            metric8_jet=G, tangent_inclusion_jet=None, gamma_jet=gamma)
    with pytest.raises(ValueError):
        surface.surface_incidence_second_jet(
            metric8_jet=G+1e-8j, tangent_inclusion_jet=T, gamma_jet=gamma)
    bad = T.copy()
    bad[0] = 0
    with pytest.raises(ValueError):
        surface.surface_incidence_second_jet(
            metric8_jet=G, tangent_inclusion_jet=bad, gamma_jet=gamma)
    with pytest.raises(ValueError):
        surface.surface_incidence_second_jet(
            metric8_jet=G, tangent_inclusion_jet=T, gamma_jet=None)


@pytest.fixture(scope='module')
def regular_domain_application(tmp_path_factory):
    output = tmp_path_factory.mktemp('regular_fp_domain') / 'literal_controls'
    command = [sys.executable, str(ROOT/'audits/bhsm_regular_reset_brst_domain_20261015.py'),
               '--out', str(output)]
    subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
    return json.loads((output/'result.json').read_bytes())


def test_regular_fp_domain_against_independent_literal_maps_and_green_form(regular_domain_application):
    for row in regular_domain_application['records']:
        assert row['independent_mp70_total_pullback_jet_error'] < 1e-12
        assert row['arbitrary_trace_cross_green_factorization_error'] < 1e-12
        assert row['matched_domain_cross_green_all_jets'] < 1e-12
        assert row['wrong_antighost_field_density_rule_detected'] > .1
        assert row['independent_antighost_vs_ghost_norm'] > 1
        assert row['incompatible_mixed_unitarity_jet_rejected'] is True


def test_linear_internal_brst_keeps_all_four_supplied_axes(regular_domain_application):
    for row in regular_domain_application['records']:
        assert row['internal_brst_four_axis_intertwining_error'] < 1e-12
        assert row['existing_affine_owner_incidence_error'] < 1e-12
        assert row['nonzero_temporal_parent_connection_norm'] > .1
        assert row['nonzero_temporal_child_connection_norm'] > .1
        assert row['nonzero_temporal_bundle_derivative_norm'] > .1
    assert regular_domain_application['physical_incidence_packet_consumed'] is False
    assert regular_domain_application['physical_outgoing_domain_evaluated'] is False
    assert regular_domain_application['full_derivative_at_2e_minus_10_passed'] is False
    assert regular_domain_application['coupled_corrections'] == 0
