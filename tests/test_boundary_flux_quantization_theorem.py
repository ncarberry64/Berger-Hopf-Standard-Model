from __future__ import annotations

from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_boundary_flux_quantization import (  # noqa: E402
    BOUNDARY_FLUX_QUANTIZATION_STRUCTURAL_CANDIDATE,
    CKM_H_MIX_DIM4_ANALOGY_ONLY,
    IDENTITY_CHANNEL_PROTECTION_STRUCTURAL_CANDIDATE,
    LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE,
    NEUTRINO_LEAKAGE_CHANNEL_REFINED,
    PURE_FIBER_DOUBLE_BRANCH_ANALOGY_ONLY,
    TRACELESS_BROWNIAN_ACTIVITY_STRUCTURAL_CANDIDATE,
    active_traceless_fraction,
    active_traceless_fraction_from_Omega,
    audit_payload,
    boundary_flux_number,
    charged_boundary_flux_table,
    ckm_channel_dilution_factor,
    cyclic_channel_dimension,
    end_algebra_split_label,
    endomorphism_channel_count,
    export_boundary_flux_outputs,
    identity_channel_count,
    is_integer_boundary_level,
    lepton_eta_flux_rule,
    pure_fiber_rank_projection,
    theorem_status_object,
    traceless_channel_count,
)
from constants import ALPHA_INV_LOW_ENERGY  # noqa: E402


def _sha(path: str) -> str:
    return hashlib.sha256(ROOT.joinpath(path).read_bytes()).hexdigest()


def test_exact_flux_channel_arithmetic() -> None:
    alpha = 1.0 / ALPHA_INV_LOW_ENERGY
    assert is_integer_boundary_level(3)
    assert boundary_flux_number(3) == Fraction(3, 1)
    assert cyclic_channel_dimension(3) == 3
    assert endomorphism_channel_count(3) == 9
    assert identity_channel_count(3) == 1
    assert traceless_channel_count(3) == 8
    assert active_traceless_fraction(3) == Fraction(8, 9)
    assert active_traceless_fraction_from_Omega(3) == Fraction(8, 9)
    assert math.isclose(lepton_eta_flux_rule(alpha, 3), 8 * alpha / (9 * math.pi))
    assert end_algebra_split_label(3) == "C I_3 + su(3)"
    assert pure_fiber_rank_projection(2, 1) == Fraction(1, 2)
    assert math.isclose(ckm_channel_dilution_factor(Fraction(1, 2), 4), 0.5 ** (1 / 16))


def test_invalid_flux_or_dimension_inputs_rejected() -> None:
    for call in (
        lambda: boundary_flux_number(0),
        lambda: boundary_flux_number(Fraction(3, 2)),
        lambda: endomorphism_channel_count(0),
        lambda: identity_channel_count(0),
        lambda: end_algebra_split_label(0),
        lambda: pure_fiber_rank_projection(0, 0),
        lambda: pure_fiber_rank_projection(2, 3),
        lambda: ckm_channel_dilution_factor(Fraction(0, 1), 4),
        lambda: ckm_channel_dilution_factor(Fraction(1, 2), 0),
    ):
        try:
            call()
        except ValueError:
            pass
        else:  # pragma: no cover
            raise AssertionError("invalid input should raise ValueError")


def test_charged_boundary_flux_table_matches_known_modes() -> None:
    table = charged_boundary_flux_table()
    assert table["lepton_middle"]["omega"] == 3
    assert table["lepton_light"]["candidate_dim_H"] == 3
    assert table["up_middle"]["omega"] == 6
    assert table["up_light"]["candidate_dim_H"] == 6
    assert table["down_middle"]["omega"] == 12
    assert table["down_light"]["candidate_dim_H"] == 12
    assert table["lepton_middle"]["traceless_channels"] == 8


def test_status_object_does_not_overclaim() -> None:
    status = theorem_status_object()
    assert status.theorem_status == BOUNDARY_FLUX_QUANTIZATION_STRUCTURAL_CANDIDATE
    assert status.identity_protection_status == IDENTITY_CHANNEL_PROTECTION_STRUCTURAL_CANDIDATE
    assert status.traceless_activity_status == TRACELESS_BROWNIAN_ACTIVITY_STRUCTURAL_CANDIDATE
    assert status.lepton_status == LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE
    assert status.pure_fiber_status == PURE_FIBER_DOUBLE_BRANCH_ANALOGY_ONLY
    assert status.ckm_status == CKM_H_MIX_DIM4_ANALOGY_ONLY
    assert status.neutrino_status == NEUTRINO_LEAKAGE_CHANNEL_REFINED
    assert status.does_dim_H_equal_abs_Omega_follow is False
    assert status.does_identity_channel_protection_follow is False
    assert status.does_traceless_activity_follow is False
    assert status.does_lepton_8_9_follow is False
    assert status.blockers_closed == ()


def test_payload_and_audit_json_validate() -> None:
    payload = export_boundary_flux_outputs(ROOT)
    assert payload["official_outputs_modified"] is False
    assert payload["frozen_predictions_modified"] is False
    assert payload["prs_opened"] is False
    assert payload["derived_components"] == ()
    assert payload["forbidden_claims_absent"] is True
    assert payload["safe_to_merge_as_candidate_only"] is True
    assert payload["neutrino_consequence"]["ordinary_FTL_claim"] is False
    path = ROOT / "audits" / "boundary_flux_quantization_theorem_audit.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "theorem_status",
        "flux_quantization_status",
        "cyclic_channel_space_status",
        "geometric_quantization_status",
        "boundary_algebra_status",
        "boundary_action_status",
        "identity_protection_status",
        "traceless_activity_status",
        "lepton_status",
        "pure_fiber_status",
        "ckm_status",
        "neutrino_status",
        "does_dim_H_equal_abs_Omega_follow",
        "does_identity_channel_protection_follow",
        "does_traceless_activity_follow",
        "does_lepton_8_9_follow",
        "blockers_closed",
        "blockers_remaining",
        "missing_assumptions",
    }
    assert required.issubset(data)


def test_official_outputs_and_frozen_files_unchanged_by_export() -> None:
    frozen_md = _sha("docs/frozen_predictions.md")
    frozen_json = _sha("docs/frozen_predictions.json")
    payload = export_boundary_flux_outputs(ROOT)
    assert _sha("docs/frozen_predictions.md") == frozen_md
    assert _sha("docs/frozen_predictions.json") == frozen_json
    sanity = payload["frozen_sanity"]
    assert sanity["BHSM_BARE_V1_unchanged"] is True
    assert sanity["BHSM_DRESSED_V1_CANDIDATE_unchanged"] is True
    assert sanity["dressed_branch_changes_only_c_over_t"] is True
    assert sanity["u_over_t_unchanged"] is True
    assert sanity["ckm_sin_theta_13_unchanged"] is True
    changed = [row for row in payload["official_branch_comparison"]["rows"] if row["changed"]]
    assert [row["quantity"] for row in changed] == ["c/t"]


def test_no_forbidden_claims_in_new_reports() -> None:
    export_boundary_flux_outputs(ROOT)
    paths = [
        "theory/boundary_flux_quantization_theorem.md",
        "theory/identity_traceless_channel_protection.md",
        "theory/neutrino_leakage_boundary_consequence.md",
    ]
    text = "\n".join(ROOT.joinpath(path).read_text(encoding="utf-8").lower() for path in paths)
    forbidden = [
        "ordinary faster-than-light neutrino claim is made",
        "ordinary environmental mass-drift claim",
        "standard model replacement",
        "bhsm is proven",
        "bhsm is confirmed",
        "full standard model derivation claim is made",
    ]
    for phrase in forbidden:
        assert phrase not in text
    assert "no ordinary superluminal neutrino claim is made" in text
    assert "no ordinary environmental mass drift claim is made" in text
