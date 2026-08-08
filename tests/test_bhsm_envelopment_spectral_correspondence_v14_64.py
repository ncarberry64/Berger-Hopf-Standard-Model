from __future__ import annotations

import json
import math
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from bhsm.interface.completion.envelopment_spectral_correspondence_v14_64 import (
    VERSION,
    PRIMARY_VERDICT,
    EXACT_NEXT_OBJECT,
    VERTICES,
    EDGES,
    cycle_rank,
    edge_weight_from_length,
    incidence_dirac,
    vertex_gauge_transform,
    diamond_holonomy,
    phases_from_matrix,
    gauge_holonomy_witness,
    normalized_boundary_layer,
    boundary_trace_amplitude,
    boundary_layer_l2_norm_exact,
    trace_map_obstruction_payload,
    heat_multiplier,
    heat_semigroup_residual,
    exponential_heat_moment,
    heat_semigroup_profile_payload,
    geometric_trace_payload,
    incidence_distance_payload,
    finite_fermion_operator_payload,
    candidate_status_payload,
    next_branch_gate_payload,
    completion_gate_payload,
    artifact_payloads,
    materialize,
)


def test_version_and_fail_closed_status():
    assert VERSION == "v14.64"
    assert "RELATIVE_BOUNDARY" in PRIMARY_VERDICT or "CORRESPONDENCE" in PRIMARY_VERDICT
    assert "BOUNDARY_SPECTRAL_CORRESPONDENCE" in EXACT_NEXT_OBJECT


def test_envelopment_graph_has_one_cycle():
    assert len(VERTICES) == 4
    assert len(EDGES) == 4
    assert cycle_rank(4, 4, 1) == 1


def test_cycle_rank_rejects_invalid_graph_counts():
    for args in ((0,1,1),(3,-1,1),(3,2,4)):
        try:
            cycle_rank(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid graph counts accepted")


def test_edge_distance_calibration():
    assert edge_weight_from_length(2.0) == 0.5
    try:
        edge_weight_from_length(0.0)
    except ValueError:
        pass
    else:
        raise AssertionError("zero length accepted")


def test_incidence_dirac_is_hermitian():
    lengths = {"e_8p":2.0,"e_8m":2.5,"e_p4":0.8,"e_m4":1.1}
    phases = {"e_8p":0.2,"e_8m":-0.4,"e_p4":0.7,"e_m4":0.1}
    d = incidence_dirac(lengths, phases)
    assert np.linalg.norm(d - np.conjugate(d.T)) < 1e-14


def test_vertex_gauge_preserves_spectrum_and_loop_holonomy():
    lengths = {"e_8p":2.0,"e_8m":2.5,"e_p4":0.8,"e_m4":1.1}
    phases = {"e_8p":0.2,"e_8m":-0.4,"e_p4":0.7,"e_m4":0.1}
    d = incidence_dirac(lengths, phases)
    dg = vertex_gauge_transform(d, (0.31,-0.27,0.41,0.13))
    assert np.max(np.abs(np.linalg.eigvalsh(d)-np.linalg.eigvalsh(dg))) < 1e-12
    h0 = diamond_holonomy(phases)
    h1 = diamond_holonomy(phases_from_matrix(dg))
    assert abs(math.atan2(math.sin(h1-h0), math.cos(h1-h0))) < 1e-12


def test_holonomy_witness_has_one_invariant_phase():
    p = gauge_holonomy_witness()
    assert p["cycle_rank"] == 1
    assert p["holonomy_invariance_residual"] < 1e-12
    assert p["spectrum_invariance_residual"] < 1e-12
    assert p["physical_BHSM_prediction"] is False


def test_boundary_layer_is_exactly_l2_normalized_formula():
    for n in (1,2,8,32):
        # exact analytic contract plus a numerical quadrature check
        assert boundary_layer_l2_norm_exact(n) == 1.0
        xs = np.linspace(0.0, 1.0, 200001)
        ys = np.abs(normalized_boundary_layer(n, xs))**2
        val = np.trapezoid(ys, xs)
        assert abs(val-1.0) < 3e-6


def test_boundary_trace_witness_grows_without_bound():
    a1 = boundary_trace_amplitude(1)
    a16 = boundary_trace_amplitude(16)
    a256 = boundary_trace_amplitude(256)
    assert a16 > a1
    assert a256 > a16
    assert a256 > 20.0


def test_trace_map_payload_fail_closed():
    p = trace_map_obstruction_payload()
    assert p["trace_L2_to_boundary_bounded"] is False
    assert p["naive_finite_incidence_matrix_is_exact_continuum_operator"] is False
    assert p["last_boundary_value"] > 20.0


def test_heat_semigroup_composition():
    for t,s,u in ((0.1,0.2,3.0),(1.0,2.0,0.7),(5.0,0.5,1.2)):
        assert heat_semigroup_residual(t,s,u) < 1e-15


def test_heat_multiplier_rejects_invalid_parameters():
    for args in ((-1.0,1.0),(1.0,-1.0)):
        try:
            heat_multiplier(*args)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid heat parameter accepted")


def test_unit_rate_heat_moments_are_fixed():
    for p in (8,6,5,4,3,2,0):
        assert exponential_heat_moment(p,1.0) == 1.0


def test_heat_branch_is_candidate_not_auto_adopted():
    p = heat_semigroup_profile_payload()
    assert p["v14_63_generic_profile_ambiguity_removed_if_branch_adopted"] is True
    assert p["branch_derived_by_existing_BHSM_action"] is False
    assert p["new_foundational_axiom_required"] is True
    assert p["can_be_selected_after_particle_comparison"] is False


def test_geometric_trace_removes_fitted_weights_conditionally():
    p = geometric_trace_payload()
    assert p["canonical_unweighted_direct_sum_trace_available"] is True
    assert p["arbitrary_weighted_trace_needed"] is False
    assert p["geometric_incidence"]["M5_caps"] == 2


def test_incidence_distance_payload_does_not_overclaim_global_metric():
    p = incidence_distance_payload()
    assert p["edge_magnitudes_fixed_once_geometric_lengths_are_action_selected"] is True
    assert p["edge_phases_fully_fixed"] is False
    assert p["global_full_Connes_distance_claimed"] is False


def test_finite_fermion_reclassification_forbids_data_insertion():
    p = finite_fermion_operator_payload()
    assert p["static_Yukawa_matrix_may_be_inserted_from_data"] is False
    assert p["current_archive_has_complete_microscopic_Gamma_for_these_derivatives"] is False
    assert p["therefore_zero_input_flavor_closed"] is False


def test_status_ledger_has_all_four_categories():
    p = candidate_status_payload()
    assert len(p["validated"]) >= 5
    assert len(p["invalidated"]) >= 3
    assert len(p["reclassified"]) >= 3
    assert len(p["open"]) >= 5


def test_next_branch_gate_forbids_postcomparison_choice():
    p = next_branch_gate_payload()
    assert p["branch_A"]["status"] == "AVAILABLE_AS_PREDECLARED_FOUNDATIONAL_CANDIDATE"
    assert p["automatic_foundational_choice_made_by_v14_64"] is False
    assert p["postcomparison_branch_selection_forbidden"] is True


def test_completion_gate_fail_closed_and_usb_untouched():
    p = completion_gate_payload()
    assert p["full_BHSM_complete"] is False
    assert p["mark_III"] == "NOT_REACHED"
    assert p["usb_touched"] is False
    assert p["naive_continuum_direct_sum_spectral_triple_closed"] is False
    assert p["heat_semigroup_branch_authoritatively_adopted"] is False
    assert len(p["missing_checks"]) >= 10


def test_artifacts_are_json_serializable_finite():
    def walk(x):
        if isinstance(x,float):
            assert math.isfinite(x)
        elif isinstance(x,dict):
            for v in x.values(): walk(v)
        elif isinstance(x,(list,tuple)):
            for v in x: walk(v)
    payloads = artifact_payloads()
    assert len(payloads) == 9
    for payload in payloads.values():
        s = json.dumps(payload, sort_keys=True, separators=(",",":"), allow_nan=False)
        assert s.startswith("{")
        walk(payload)


def test_materialization_byte_deterministic(tmp_path):
    a,b = tmp_path/"a", tmp_path/"b"
    materialize(a); materialize(b)
    names = sorted(p.name for p in a.iterdir())
    assert len(names) == 9
    assert names == sorted(p.name for p in b.iterdir())
    for name in names:
        assert (a/name).read_bytes() == (b/name).read_bytes()
