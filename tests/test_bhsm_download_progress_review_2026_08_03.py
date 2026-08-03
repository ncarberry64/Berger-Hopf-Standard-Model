from __future__ import annotations

from math import isclose

from sympy import Matrix, Rational, Symbol

from bhsm.interface.completion.download_progress_review_2026_08_03 import (
    AUTHORITATIVE_NEXT_OBJECT,
    PACKET_HASHES,
    archived_packet_hashes,
    candidate_lepton_numbers,
    inverse_octave,
    lower_attachment_root,
    materialize,
    packet_gram_matrix,
    packet_hessian,
    packet_tangent_basis,
    review_payload,
)


def test_archived_manual_packets_are_complete_and_hash_locked() -> None:
    assert len(PACKET_HASHES) == 9
    assert archived_packet_hashes() == PACKET_HASHES


def test_packet_gram_hessian_and_constraint_algebra() -> None:
    h = Symbol("h", real=True)
    gram = packet_gram_matrix()
    hessian = packet_hessian(h)
    tangent = packet_tangent_basis()
    constraint = Matrix([[-1, 1, 1]])
    assert gram.det() == Rational(3, 4)
    assert hessian.det() == (6 * h + 1) / 32
    assert constraint * tangent == Matrix.zeros(1, 2)
    assert (tangent.T * gram * tangent).det() == 4
    assert (tangent.T * hessian * tangent).det() == (48 * h + 35) / 64


def test_attachment_branch_is_ordered_and_inverse_recovers_supplied_octaves() -> None:
    h_core = 0.181391690148362
    roots = [lower_attachment_root(octave, h_core) for octave in (0, 35, 99)]
    assert roots == sorted(roots)
    for octave, root in zip((0, 35, 99), roots, strict=True):
        assert isclose(inverse_octave(root, h_core), octave, abs_tol=1e-8)


def test_dimensionful_numbers_are_reproduced_only_as_conditional_screens() -> None:
    numbers = candidate_lepton_numbers()
    assert numbers["classification"] == "CONDITIONAL_SCREEN_NOT_ACTION_DERIVED_PREDICTION"
    assert numbers["action_excluded_inputs"] == ["alpha_inv_low_energy", "Planck_energy_GeV"]
    assert isclose(numbers["candidate_masses_GeV"]["heavy"], 1.7589306145235935)
    assert isclose(numbers["candidate_masses_GeV"]["middle"], 0.10566682607467506)
    assert isclose(numbers["candidate_masses_GeV"]["light"], 0.0005229143548875558)


def test_review_fails_closed_without_changing_authoritative_status(tmp_path) -> None:
    payload = review_payload()
    assert payload["validation_passed"]
    assert payload["baseline_completion_status"]["authoritative_version"] == "v11.3"
    assert payload["completion_status"]["current_version"] == "v11.5"
    assert payload["completion_status"]["BHSM_1_0_release_complete"] is False
    assert payload["baseline_completion_status"]["exact_next_object"] == AUTHORITATIVE_NEXT_OBJECT
    assert payload["frozen_predictions_changed"] is False
    first = materialize(tmp_path).read_bytes()
    second = materialize(tmp_path).read_bytes()
    assert first == second
