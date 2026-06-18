from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm_boundary_projection_channels import (  # noqa: E402
    BOUNDARY_ACTION_STRUCTURAL_CANDIDATE,
    CKM_1_16_CHANNEL_DILUTION_STRUCTURAL_CANDIDATE,
    LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE,
    NEUTRINO_LEAKAGE_CHANNEL_CANDIDATE,
    PURE_FIBER_RANK_HALF_STRUCTURAL_CANDIDATE,
    active_channel_fraction,
    audit_payload,
    boundary_operator_values,
    ckm_channel_dilution,
    export_boundary_projection_channel_outputs,
    lepton_eta_channel_rule,
    pure_fiber_rank_projection,
)
from constants import ALPHA_INV_LOW_ENERGY  # noqa: E402


def _sha(path: str) -> str:
    return hashlib.sha256(ROOT.joinpath(path).read_bytes()).hexdigest()


def test_channel_arithmetic_rules() -> None:
    alpha = 1.0 / ALPHA_INV_LOW_ENERGY
    assert active_channel_fraction(3) == 8 / 9
    assert math.isclose(lepton_eta_channel_rule(alpha), 8 * alpha / (9 * math.pi))
    assert pure_fiber_rank_projection(2, 1) == 0.5
    assert math.isclose(ckm_channel_dilution(0.5, 4), 0.5 ** (1 / 16))


def test_boundary_operator_values_for_supplied_mode_pairs() -> None:
    values = boundary_operator_values()
    assert values["lepton_middle"]["omega"] == 3
    assert values["lepton_light"]["omega"] == 3
    assert values["up_middle"]["omega"] == 6
    assert values["up_light"]["omega"] == 6
    assert values["down_middle"]["omega"] == 12
    assert values["down_light"]["omega"] == 12


def test_payload_statuses_remain_candidate_only() -> None:
    payload = audit_payload()
    assert payload["official_outputs_modified"] is False
    assert payload["frozen_predictions_modified"] is False
    assert payload["prs_opened"] is False
    assert payload["lepton_status"] == LEPTON_8_9_CHANNEL_RULE_STRUCTURAL_CANDIDATE
    assert payload["pure_fiber_status"] == PURE_FIBER_RANK_HALF_STRUCTURAL_CANDIDATE
    assert payload["ckm_status"] == CKM_1_16_CHANNEL_DILUTION_STRUCTURAL_CANDIDATE
    assert payload["boundary_action_status"] == BOUNDARY_ACTION_STRUCTURAL_CANDIDATE
    assert payload["neutrino_status"] == NEUTRINO_LEAKAGE_CHANNEL_CANDIDATE
    assert payload["blockers_closed"] == ()
    assert set(payload["blockers_remaining"]) == {
        "lepton_8alpha_9pi",
        "pure_fiber_one_half",
        "ckm_one_sixteenth",
        "boundary_action",
        "neutrino_pmns",
    }
    assert payload["derived_components"] == ()
    assert payload["safe_to_merge_as_candidate_only"] is True


def test_official_outputs_and_frozen_files_are_unchanged_by_export() -> None:
    frozen_md = _sha("docs/frozen_predictions.md")
    frozen_json = _sha("docs/frozen_predictions.json")
    payload = export_boundary_projection_channel_outputs(ROOT)
    assert _sha("docs/frozen_predictions.md") == frozen_md
    assert _sha("docs/frozen_predictions.json") == frozen_json
    sanity = payload["frozen_sanity"]
    assert sanity["BHSM_BARE_V1_unchanged"] is True
    assert sanity["BHSM_DRESSED_V1_CANDIDATE_unchanged"] is True
    assert sanity["dressed_branch_changes_only_c_over_t"] is True
    assert sanity["u_over_t_unchanged"] is True
    assert sanity["ckm_sin_theta_13_unchanged"] is True
    comparison = payload["official_branch_comparison"]
    changed = [row for row in comparison["rows"] if row["changed"]]
    assert changed == [
        {
            "quantity": "c/t",
            "bare": 0.008310500554068288,
            "dressed": 0.004155250277034144,
            "changed": True,
        }
    ]


def test_audit_json_validates() -> None:
    export_boundary_projection_channel_outputs(ROOT)
    path = ROOT / "audits" / "boundary_projection_channel_theorem_audit.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "official_outputs_modified",
        "frozen_predictions_modified",
        "prs_opened",
        "theorem_status",
        "lepton_status",
        "pure_fiber_status",
        "ckm_status",
        "boundary_action_status",
        "neutrino_status",
        "blockers_closed",
        "blockers_remaining",
        "candidate_components",
        "derived_components",
        "rejected_components",
        "missing_assumptions",
        "forbidden_claims_absent",
        "safe_to_merge_as_candidate_only",
    }
    assert required.issubset(data)
    assert data["forbidden_claims_absent"] is True
    assert data["neutrino_ledger"]["ordinary_FTL_claim"] is False


def test_no_forbidden_claims_in_new_reports() -> None:
    export_boundary_projection_channel_outputs(ROOT)
    paths = [
        "theory/boundary_projection_channel_theorem.md",
        "audits/boundary_projection_channel_theorem_audit.md",
        "theory/neutrino_pmns_leakage_channel_ledger.md",
    ]
    text = "\n".join(ROOT.joinpath(path).read_text(encoding="utf-8").lower() for path in paths)
    forbidden = [
        "ordinary faster-than-light neutrino claim is made",
        "environmental mass-drift mechanism is introduced",
        "standard model replacement",
        "bhsm is proven",
        "bhsm is confirmed",
    ]
    for phrase in forbidden:
        assert phrase not in text
    assert "no ordinary superluminal neutrino claim is made" in text
    assert "no ordinary environmental mass drift claim is made" in text
