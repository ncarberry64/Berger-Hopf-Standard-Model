from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_boundary_channel_space import (  # noqa: E402
    BOUNDARY_CHANNEL_SPACE_STRUCTURAL_CANDIDATE,
    CKM_MIX_CHANNEL_SPACE_SUPPORTED_BY_ANALOGY,
    LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE,
    NEUTRINO_LEAKAGE_CHANNEL_CANDIDATE,
    PURE_FIBER_DOUBLE_CHANNEL_SUPPORTED_BY_ANALOGY,
    active_fraction_from_dim,
    active_fraction_from_Omega,
    active_traceless_count,
    audit_payload,
    boundary_level_abs,
    charged_sector_boundary_levels,
    cyclic_channel_dimension,
    end_channel_count,
    export_boundary_channel_space_outputs,
    lepton_eta_from_channel_space,
)
from constants import ALPHA_INV_LOW_ENERGY  # noqa: E402


def _sha(path: str) -> str:
    return hashlib.sha256(ROOT.joinpath(path).read_bytes()).hexdigest()


def test_channel_space_arithmetic() -> None:
    alpha = 1.0 / ALPHA_INV_LOW_ENERGY
    assert boundary_level_abs(-3) == 3
    assert cyclic_channel_dimension(3) == 3
    assert end_channel_count(3) == 9
    assert active_traceless_count(3) == 8
    assert active_fraction_from_dim(3) == 8 / 9
    assert active_fraction_from_Omega(3) == 8 / 9
    assert math.isclose(lepton_eta_from_channel_space(alpha, 3), 8 * alpha / (9 * math.pi))


def test_zero_or_bad_dimensions_rejected() -> None:
    for bad in (0,):
        try:
            boundary_level_abs(bad)
        except ValueError:
            pass
        else:  # pragma: no cover
            raise AssertionError("zero boundary level must be rejected")
    for bad in (0, -1):
        try:
            end_channel_count(bad)
        except ValueError:
            pass
        else:  # pragma: no cover
            raise AssertionError("nonpositive dim_H must be rejected")


def test_boundary_levels_use_supplied_mode_pairs() -> None:
    levels = charged_sector_boundary_levels()
    assert levels["lepton_middle"]["omega"] == 3
    assert levels["lepton_light"]["candidate_dim_H"] == 3
    assert levels["up_middle"]["omega"] == 6
    assert levels["up_light"]["candidate_dim_H"] == 6
    assert levels["down_middle"]["omega"] == 12
    assert levels["down_light"]["candidate_dim_H"] == 12


def test_payload_statuses_are_candidate_only() -> None:
    payload = audit_payload()
    assert payload["official_outputs_modified"] is False
    assert payload["frozen_predictions_modified"] is False
    assert payload["prs_opened"] is False
    assert payload["theorem_status"] == BOUNDARY_CHANNEL_SPACE_STRUCTURAL_CANDIDATE
    assert payload["lepton_status"] == LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE
    assert payload["pure_fiber_consequence_status"] == PURE_FIBER_DOUBLE_CHANNEL_SUPPORTED_BY_ANALOGY
    assert payload["ckm_consequence_status"] == CKM_MIX_CHANNEL_SPACE_SUPPORTED_BY_ANALOGY
    assert payload["neutrino_consequence_status"] == NEUTRINO_LEAKAGE_CHANNEL_CANDIDATE
    assert payload["does_dim_H_equal_abs_Omega_follow"] is False
    assert payload["does_identity_channel_protection_follow"] is False
    assert payload["does_active_traceless_fraction_follow"] is False
    assert payload["blockers_closed"] == ()
    assert payload["safe_to_merge_as_candidate_only"] is True


def test_official_outputs_and_frozen_files_are_unchanged_by_export() -> None:
    frozen_md = _sha("docs/frozen_predictions.md")
    frozen_json = _sha("docs/frozen_predictions.json")
    payload = export_boundary_channel_space_outputs(ROOT)
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


def test_audit_json_validates() -> None:
    export_boundary_channel_space_outputs(ROOT)
    path = ROOT / "audits" / "boundary_channel_space_construction_audit.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "official_outputs_modified",
        "frozen_predictions_modified",
        "prs_opened",
        "theorem_status",
        "lepton_status",
        "pure_fiber_consequence_status",
        "ckm_consequence_status",
        "neutrino_consequence_status",
        "derived_components",
        "candidate_components",
        "rejected_components",
        "missing_assumptions",
        "does_dim_H_equal_abs_Omega_follow",
        "does_identity_channel_protection_follow",
        "does_active_traceless_fraction_follow",
        "blockers_closed",
        "blockers_remaining",
        "forbidden_claims_absent",
        "safe_to_merge_as_candidate_only",
    }
    assert required.issubset(data)
    assert data["forbidden_claims_absent"] is True
    assert data["neutrino_consequence"]["ordinary_FTL_claim"] is False


def test_no_forbidden_claims_in_new_reports() -> None:
    export_boundary_channel_space_outputs(ROOT)
    paths = [
        "theory/boundary_channel_space_construction.md",
        "audits/boundary_channel_space_construction_audit.md",
        "theory/lepton_channel_space_8_9_consequence.md",
    ]
    text = "\n".join(ROOT.joinpath(path).read_text(encoding="utf-8").lower() for path in paths)
    forbidden = [
        "ordinary faster-than-light neutrino claim is made",
        "ordinary environmental mass-drift claim",
        "standard model replacement",
        "bhsm is proven",
        "bhsm is confirmed",
    ]
    for phrase in forbidden:
        assert phrase not in text
    assert "no ordinary superluminal neutrino claim is made" in text
    assert "no ordinary environmental mass drift claim is made" in text
