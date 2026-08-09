from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

import pytest

from bhsm.interface.completion.aether_completion_gate_v15_0 import (
    EXACT_NEXT_OBJECT,
    OUTCOME,
    PRIMARY_VERDICT,
    artifact_payloads,
    completion_payload,
    materialize,
)
from bhsm.interface.completion.aether_emergent_clock_energy_v15_0 import (
    Process,
    clock_ratio,
    clocked_energy,
)
from bhsm.interface.completion.aether_encapsulation_correspondence_v15_0 import EventSpan
from bhsm.interface.completion.aether_haar_barrier_v15_0 import (
    compact_coordinate_distance_to_one,
    compact_depth_coordinate,
    decimal_haar_distance_to_one,
    finite_action_length_bound,
    haar_distance,
    support_depth,
)
from bhsm.interface.completion.aether_parent_stratification_v15_0 import (
    AetherState,
    CORE_STRATUM,
    core_state,
    geometric_state,
    reconstruct_bhsm,
)
from bhsm.interface.completion.aether_reconstruction_v15_0 import (
    ReconstructionEvidence,
    edge_spectral_distance,
    high_excitation_counterexample,
    reconstruction_predicate,
)

ROOT = Path(__file__).resolve().parents[1]


def test_exact_support_depth_and_distance_formula() -> None:
    scale = 2.5
    u = math.exp(-3.0)
    assert support_depth(u, scale) == pytest.approx(7.5)
    assert haar_distance(1.0, u, scale) == pytest.approx(7.5)


def test_haar_distance_diverges_at_regular_endpoint() -> None:
    values = [decimal_haar_distance_to_one(n) for n in (1, 2, 4, 8, 16, 32)]
    assert all(b > a for a, b in zip(values, values[1:]))
    assert float(values[-1] / values[0]) == pytest.approx(32.0)


def test_bounded_coordinate_does_not_compactify_physical_metric() -> None:
    zs = [compact_depth_coordinate(10.0 ** (-n)) for n in (1, 2, 4, 8)]
    assert all(0.0 < z < 1.0 for z in zs)
    assert all(b > a for a, b in zip(zs, zs[1:]))
    distances = [compact_coordinate_distance_to_one(1.0 - delta) for delta in (0.5, 0.25, 0.125, 0.0625)]
    assert distances == [1.0, 3.0, 7.0, 15.0]


def test_finite_duration_finite_action_cannot_cover_infinite_length() -> None:
    assert math.isfinite(finite_action_length_bound(4.0, 9.0))
    assert finite_action_length_bound(4.0, 9.0) == 6.0


def test_support_domain_rejects_endpoint_and_invalid_scale() -> None:
    with pytest.raises(ValueError):
        support_depth(0.0)
    with pytest.raises(ValueError):
        support_depth(0.5, 0.0)


def test_core_schema_assigns_no_spacetime_time_or_energy() -> None:
    core = core_state("C", invariant="I")
    assert core.stratum == CORE_STRATUM
    assert not ({"upsilon", "spacetime_coordinates", "time", "duration", "energy", "energy_density"} & set(core.data))
    assert reconstruct_bhsm(core) is None


@pytest.mark.parametrize("field", ["upsilon", "spacetime_coordinates", "time", "energy", "velocity", "preferred_frame"])
def test_core_schema_rejects_geometric_and_preferred_frame_fields(field: str) -> None:
    with pytest.raises(ValueError):
        AetherState("bad", CORE_STRATUM, {field: 0})


def test_upsilon_exists_only_on_regular_reconstructible_branch() -> None:
    regular = geometric_state("G", 0.25)
    reconstructed = reconstruct_bhsm(regular)
    assert reconstructed is not None
    assert reconstructed["regular_support"]["upsilon"] == 0.25
    assert reconstructed["stratification"] == ["M8", "M5_plus", "M5_minus", "M4"]


def test_reconstruction_predicate_preserves_v14_64_domain_gate() -> None:
    state = geometric_state("G", 1.0)
    valid = ReconstructionEvidence(True, True, True, True, True, True, True)
    invalid_trace = ReconstructionEvidence(True, True, True, True, False, False, True)
    assert reconstruction_predicate(state, valid) == "RECONSTRUCTIBLE_BHSM_GEOMETRY"
    assert reconstruction_predicate(state, invalid_trace) == "NONRECONSTRUCTIBLE_AETHER_STATE"
    assert edge_spectral_distance(0.25) == 4.0


def test_process_cocycle_is_additive_and_clock_is_a_ratio() -> None:
    first = Process("A", "B", Fraction(2, 3))
    second = Process("B", "C", Fraction(1, 6))
    composed = first.then(second)
    assert composed.depth == Fraction(5, 6)
    assert clock_ratio(composed, Fraction(5, 12)) == 2


def test_energy_is_introduced_only_after_clock_calibration() -> None:
    assert clocked_energy(3.0, 2.0, 4.0) == 6.0
    with pytest.raises(ValueError):
        clocked_energy(1.0, 0.0)


def test_event_correspondence_composition_is_associative() -> None:
    signature = (("I", "fixed"),)
    a = EventSpan("A", "B", ("a",), signature, Fraction(1, 5))
    b = EventSpan("B", "C", ("b",), signature, Fraction(2, 5))
    c = EventSpan("C", "D", ("c",), signature, Fraction(3, 5))
    assert a.then(b).then(c) == a.then(b.then(c))
    assert a.then(b).then(c).event_word == ("a", "b", "c")


def test_event_correspondence_identity_laws() -> None:
    signature = (("I", "fixed"),)
    event = EventSpan("A", "B", ("event",), signature, Fraction(2, 5))
    assert EventSpan.identity("A", signature).then(event) == event
    assert event.then(EventSpan.identity("B", signature)) == event


def test_event_invariants_survive_composition_and_mismatch_fails() -> None:
    signature = (("degree_eta", "1"),)
    a = EventSpan("A", "B", ("a",), signature)
    b = EventSpan("B", "C", ("b",), signature)
    assert a.then(b).invariant_signature == signature
    with pytest.raises(ValueError):
        a.then(EventSpan("B", "C", ("bad",), (("degree_eta", "0"),)))


def test_high_excitation_monotonicity_is_not_fabricated() -> None:
    witness = high_excitation_counterexample()
    assert witness["state_high"]["dimensionless_excitation"] > witness["state_low"]["dimensionless_excitation"]
    assert witness["state_high"]["Rec"] is witness["state_low"]["Rec"] is True
    assert witness["monotone_high_excitation_implies_lower_reconstructibility_derived"] is False


def test_completion_verdict_and_claim_boundaries() -> None:
    payload = completion_payload()
    assert OUTCOME == "OUTCOME_B"
    assert payload["primary_verdict"] == PRIMARY_VERDICT
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT
    assert payload["FULL_BHSM_COMPLETE"] is False
    assert payload["PHYSICAL_AETHER_TRANSITION_DERIVED"] is False
    assert payload["SPACETIME_EMERGENT_IN_NATURE_PROVED"] is False
    assert payload["new_continuous_parameter_introduced"] is False
    assert payload["new_fundamental_dynamical_field_introduced"] is False
    assert payload["validation_passed"] is True


def test_no_empirical_particle_or_cosmological_inputs_enter_package() -> None:
    text = json.dumps(artifact_payloads(), sort_keys=True).lower()
    for forbidden in ("measured_mass", "ckm_input", "pmns_input", "cosmological_fit", "particle_fit"):
        assert forbidden not in text
    assert completion_payload()["empirical_inputs_used"] is False


def test_frozen_predictions_and_official_logic_hashes_unchanged() -> None:
    expected = {
        "docs/frozen_predictions.md": "9ea147c56537520c86d3c4f9b864c6ba98bac9e64931edae96449f3b335a36c4",
        "docs/frozen_predictions.json": "f38210e0689871a25a9d5b0a1a4239883b7240cd7d0e25cdcf4c8cab72a2cbe7",
        "src/bhsm_model.py": "8fc5a59ac4fcafe4d3fca3249c46eaaf4ee2d0a019656333b75e3b1a989c8b3b",
        "src/bhsm/interface/predictions.py": "ea0539bef06184c619dd028eafafb76ea15e92a444483ff93637593f0eaa1fed",
        "artifacts/CKM_no_fit_operator_output_v1.json": "9c354e8812682c75187c00becb90ff44b5dcc74aef10992103df28b34321d757",
    }
    for relative, digest in expected.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest


def test_materializer_is_deterministic_and_strict_json(tmp_path: Path) -> None:
    first_paths = materialize(tmp_path)
    first = {path.name: path.read_bytes() for path in first_paths}
    second_paths = materialize(tmp_path)
    second = {path.name: path.read_bytes() for path in second_paths}
    assert first == second
    assert set(first) == set(artifact_payloads())
    for name, raw in first.items():
        assert json.loads(raw) == artifact_payloads()[name]
