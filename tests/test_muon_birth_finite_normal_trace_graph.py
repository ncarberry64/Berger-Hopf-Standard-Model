"""Actual finite response graph, including both fields and nonlinear contacts."""
from pathlib import Path
import numpy as np
import pytest
from bhsm.interface.muon_birth_attached_phase import load_attached_endpoint
from bhsm.interface.muon_birth_normal_trace_graph import normal_trace_graph_action_two_jet
from bhsm.interface.muon_birth_finite_normal_trace_graph import (
    finite_normal_trace_graph_action_two_jet, finite_normal_trace_graph_action_value,
)

ROOT = Path(__file__).resolve().parents[1]
INPUT = 'artifacts/muon_parent_gauge_geometry_correction_20261010/paired_attachment_endpoint_run_1'


def pair():
    p = load_attached_endpoint(INPUT, side='incoming', repository=ROOT, radial_points=6, cap_points=48)
    c = load_attached_endpoint(INPUT, side='outgoing', repository=ROOT, radial_points=6, cap_points=48)
    return np.array([p['raw'], c['raw']]), p['representation'], p['receipt']['action_parameters']


def test_zero_normal_matches_retained_graph_all_internal_contacts():
    raw, rep, parameters = pair()
    old = normal_trace_graph_action_two_jet(raw, raw, rep, **parameters)
    new = finite_normal_trace_graph_action_two_jet(raw, raw, rep, **parameters)
    assert old['value'] == pytest.approx(new['value'], rel=2e-14, abs=3e-13)
    np.testing.assert_allclose(old['raw_gradient'], new['raw_gradient'], rtol=3e-11, atol=3e-10)
    np.testing.assert_allclose(old['raw_hessian'], new['raw_hessian'], rtol=3e-11, atol=2e-8)
    assert not new['source_image_projected']
    assert not new['full_stationary_birth_or_physical_formation_selected']


def test_finite_same_action_graph_hessian_matches_independent_literal_application():
    reference, rep, parameters = pair()
    raw = reference.copy(); raw[:, 98] = .001; raw[:, 99] = .00001
    a = finite_normal_trace_graph_action_two_jet(raw, reference, rep, **parameters)
    direction = np.zeros_like(raw)
    direction[:, 98] = 1.; direction[:, 99] = .01
    direction[0, 0] = .02; direction[1, 108] = .05; direction[1, 261] = .01
    expected_first = a['raw_gradient']@direction.ravel()
    expected_second = direction.ravel()@a['raw_hessian']@direction.ravel()
    value = finite_normal_trace_graph_action_value(raw, reference, rep, **parameters)
    assert a['value'] == pytest.approx(value, abs=2e-13, rel=2e-14)
    defects = []
    for step in (8e-5, 4e-5):
        p = finite_normal_trace_graph_action_value(raw+step*direction, reference, rep, **parameters)
        n = finite_normal_trace_graph_action_value(raw-step*direction, reference, rep, **parameters)
        first = (p-n)/(2*step); second = (p-2*value+n)/step**2
        defects.append(abs(second-expected_second))
    assert first == pytest.approx(expected_first, rel=2e-6, abs=2e-6)
    assert defects[1] < max(.45*defects[0], 3e-5)
    assert defects[1] < 3e-4
