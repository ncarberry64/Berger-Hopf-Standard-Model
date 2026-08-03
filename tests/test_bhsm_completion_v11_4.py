from __future__ import annotations

from math import isclose

from sympy import Matrix

from bhsm.interface.completion.charged_lepton_action_v11_4 import action_payload
from bhsm.interface.completion.common_attachment_response_v11_4 import (
    constraint_jacobian,
    inverse_octave,
    kinetic_matrix,
    reduced_matrices,
    response_payload,
    response_roots,
    tangent_basis,
    whitening_map,
)
from bhsm.interface.completion.completion_gate_v11_4 import ARTIFACT_FILES, completion_payload, materialize
from bhsm.interface.completion.quark_yukawa_ckm_v11_4 import EXACT_NEXT_OBJECT, quark_payload


def test_canonical_whitened_common_domain_response() -> None:
    assert kinetic_matrix() == Matrix.eye(3)
    assert constraint_jacobian() * tangent_basis() == Matrix.zeros(1, 2)
    kinetic, hessian = reduced_matrices()
    assert kinetic == Matrix([[2, 1], [1, 2]])
    assert float(hessian.det()) > 0
    payload = response_payload()
    assert payload["validation_passed"]
    assert payload["normalization_fix"].startswith("retain the v11.3 action-whitened")
    assert whitening_map() == Matrix.eye(3)
    assert payload["validation"]["shared_whitening_map_applied_to_gram_and_hessian"]
    assert payload["whitening_provenance"]["incompatible_unwhitened_packet_pencil_used"] is False


def test_family_octave_roots_are_positive_nondegenerate_and_invertible() -> None:
    roots = [response_roots(octave)[0] for octave in (0, 35, 99)]
    assert 0 < roots[0] < roots[1] < roots[2]
    for octave, root in zip((0, 35, 99), roots, strict=True):
        assert isclose(inverse_octave(root), octave, abs_tol=1e-8)


def test_minimal_charged_lepton_action_candidate() -> None:
    payload = action_payload()
    assert payload["validation_passed"]
    assert payload["independent_Ye_retained"] is False
    assert payload["candidate_mass_status"].startswith("CONDITIONAL")
    masses = payload["candidate_mass_eigenvalues_GeV"]
    assert isclose(masses["tau_slot"], 1.7589306145235935)
    assert isclose(masses["mu_slot"], 0.10566682607467506)
    assert isclose(masses["e_slot"], 0.0005229143548875558)


def test_quark_pair_keeps_nontrivial_ckm_fail_closed() -> None:
    payload = quark_payload()
    assert payload["validation_passed"]
    assert payload["canonical_CKM"] == "I3"
    assert payload["canonical_Jarlskog"] == 0
    assert payload["exact_next_object"] == EXACT_NEXT_OBJECT


def test_v11_4_gate_advances_without_claiming_release_completion(tmp_path) -> None:
    gate = completion_payload()
    assert gate["validation_passed"]
    assert gate["Mark_II"] == "REACHED_ON_SELECTED_FINITE_RADIUS_CORE_BRANCH"
    assert gate["Mark_III"] == "NOT_REACHED"
    assert gate["BHSM_1_0_release_complete"] is False
    assert gate["exact_next_object"] == EXACT_NEXT_OBJECT
    first = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    second = {path.name: path.read_bytes() for path in materialize(tmp_path)}
    assert first == second
    assert set(first) == set(ARTIFACT_FILES.values())
