"""Manual theory-delta audit for the BHSM completion candidate package.

The entries here are candidate-only interpretive updates.  They do not mutate
the frozen BHSM branches, official predictions, constants, or tolerances.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import exp, pi, sqrt
from pathlib import Path
from typing import Any

from bhsm_model import build_bhsm_model
from bhsm_v1 import compare_bhsm_v1_branches
from charged_lepton_precision_closure import baseline_residuals, fit_eta_from_mu_tau
from constants import ALPHA_INV_LOW_ENERGY
from flavor_matrix import canonical_ckm_delta


SCREENED_ALPHA_PI_LEPTON_CANDIDATE_NOT_DERIVED = (
    "SCREENED_ALPHA_PI_LEPTON_CANDIDATE_NOT_DERIVED"
)
LIGHT_UP_THREE_COFRAME_CANDIDATE_NOT_DERIVED = (
    "LIGHT_UP_THREE_COFRAME_CANDIDATE_NOT_DERIVED"
)
CKM_FOUR_PROJECTION_CANDIDATE_NOT_DERIVED = "CKM_FOUR_PROJECTION_CANDIDATE_NOT_DERIVED"
PURE_FIBER_DOUBLET_CANDIDATE_NOT_DERIVED = "PURE_FIBER_DOUBLET_CANDIDATE_NOT_DERIVED"
NEUTRINO_LEAKAGE_LEDGER_CANDIDATE_ONLY = "NEUTRINO_LEAKAGE_LEDGER_CANDIDATE_ONLY"
CP_HOPF_HOLONOMY_CANDIDATE_NOT_DERIVED = "CP_HOPF_HOLONOMY_CANDIDATE_NOT_DERIVED"
HIGGS_LOWEST_SURFACE_MODE_CANDIDATE_GAP_PROOF_OPEN = (
    "HIGGS_LOWEST_SURFACE_MODE_CANDIDATE_GAP_PROOF_OPEN"
)
CANDIDATE_NOT_OFFICIAL = "CANDIDATE_NOT_OFFICIAL"


@dataclass(frozen=True)
class EtaDeltaRow:
    """One charged-lepton eta comparison row."""

    candidate: str
    eta_l: float
    formula: str
    source: str
    derived: bool
    candidate_only: bool
    mu_tau_prediction: float
    mu_tau_relative_error: float
    e_tau_prediction: float
    e_tau_relative_error: float
    improves_mu_tau: bool
    improves_e_tau: bool


@dataclass(frozen=True)
class ManualDeltaReport:
    """Structured manual theory-delta report."""

    status: str
    official_outputs_changed: bool
    frozen_files_changed: bool
    lepton_eta_status: str
    preferred_lepton_eta_candidate: str
    best_numeric_lepton_eta_candidate: str
    light_up_status: str
    ckm_projection_status: str
    pure_fiber_doublet_status: str
    neutrino_ledger_status: str
    cp_holonomy_status: str
    higgs_surface_mode_status: str
    blockers_closed: tuple[str, ...]
    blockers_remaining: tuple[str, ...]


def _relative_error(predicted: float, reference: float) -> float:
    return abs(predicted - reference) / abs(reference)


def frozen_sanity_payload() -> dict[str, Any]:
    """Return official branch immutability checks."""

    comparison = compare_bhsm_v1_branches()
    changed = [row for row in comparison["rows"] if row["changed"]]
    return {
        "BHSM_BARE_V1_unchanged": comparison["branches"][0] == "BHSM_BARE_V1",
        "BHSM_DRESSED_V1_CANDIDATE_unchanged": comparison["branches"][1]
        == "BHSM_DRESSED_V1_CANDIDATE",
        "dressed_branch_changes_only_c_over_t": len(changed) == 1
        and changed[0]["quantity"] == "c/t",
        "u_over_t_unchanged": next(row for row in comparison["rows"] if row["quantity"] == "u/t")[
            "changed"
        ]
        is False,
        "ckm_sin_theta_13_unchanged": next(
            row for row in comparison["rows"] if row["quantity"] == "sin_theta_13"
        )["changed"]
        is False,
        "changed_rows": changed,
    }


def lepton_eta_delta_rows() -> tuple[EtaDeltaRow, ...]:
    """Compare baseline, fitted eta, and predeclared manual eta candidates."""

    alpha = 1.0 / ALPHA_INV_LOW_ENERGY
    eta_values = (
        (
            "baseline_no_dressing",
            0.0,
            "eta_l=0",
            "official frozen BHSM lepton ratios",
            False,
        ),
        (
            "fitted_eta_from_mu_tau",
            fit_eta_from_mu_tau(),
            "eta_l fitted from mu/tau",
            "fit diagnostic only; not a derivation",
            False,
        ),
        (
            "alpha_over_pi",
            alpha / pi,
            "eta_l=alpha/pi",
            "electromagnetic stochastic phase-averaged dressing candidate",
            False,
        ),
        (
            "screened_8alpha_over_9pi",
            8.0 * alpha / (9.0 * pi),
            "eta_l=(alpha/pi)*(1-1/Omega_l^2)=8alpha/(9pi), Omega_l=3",
            "eight stochastic lepton boundary channels with one coherent/protected channel",
            False,
        ),
        (
            "sqrt3_alpha_over_2pi",
            sqrt(3.0) * alpha / (2.0 * pi),
            "eta_l=sqrt(3)alpha/(2pi)",
            "diagnostic geometric factor; weaker channel-count interpretation",
            False,
        ),
    )
    rows = {row.quantity: row for row in baseline_residuals()}
    mu = rows["mu/tau"]
    electron = rows["e/tau"]
    out: list[EtaDeltaRow] = []
    for name, eta, formula, source, derived in eta_values:
        mu_pred = mu.predicted * exp(-eta * 5.0)
        e_pred = electron.predicted * exp(-eta * 18.0)
        mu_err = _relative_error(mu_pred, mu.reference)
        e_err = _relative_error(e_pred, electron.reference)
        out.append(
            EtaDeltaRow(
                candidate=name,
                eta_l=float(eta),
                formula=formula,
                source=source,
                derived=derived,
                candidate_only=name != "baseline_no_dressing",
                mu_tau_prediction=float(mu_pred),
                mu_tau_relative_error=float(mu_err),
                e_tau_prediction=float(e_pred),
                e_tau_relative_error=float(e_err),
                improves_mu_tau=mu_err < mu.relative_error,
                improves_e_tau=e_err < electron.relative_error,
            )
        )
    return tuple(out)


def lepton_eta_delta_payload() -> dict[str, Any]:
    """Return manual lepton eta candidate comparison."""

    rows = lepton_eta_delta_rows()
    preferred = next(row for row in rows if row.candidate == "screened_8alpha_over_9pi")
    best_numeric = min((row for row in rows if row.candidate != "baseline_no_dressing"), key=lambda row: row.e_tau_relative_error)
    return {
        "status": SCREENED_ALPHA_PI_LEPTON_CANDIDATE_NOT_DERIVED,
        "candidate_only": True,
        "official": False,
        "omega_l": 3,
        "preferred_candidate": preferred,
        "best_numeric_candidate": best_numeric,
        "rows": rows,
        "interpretation": (
            "alpha/pi is treated as an electromagnetic stochastic phase-averaged dressing; "
            "Omega_l^2=9 supplies a screened lepton boundary-channel count with one coherent/protected channel and eight stochastic channels."
        ),
        "closure": "does_not_close_lepton_blocker",
        "limitation": "The 8/9 screening factor is not derived from an action or spectrum in this branch.",
    }


def light_up_three_coframe_payload() -> dict[str, Any]:
    """Return candidate-only light-up three-coframe projection audit."""

    comparison = compare_bhsm_v1_branches()
    u_row = next(row for row in comparison["rows"] if row["quantity"] == "u/t")
    sin13 = next(row for row in comparison["rows"] if row["quantity"] == "sin_theta_13")
    candidate = float(u_row["bare"]) / sqrt(3.0)
    return {
        "status": LIGHT_UP_THREE_COFRAME_CANDIDATE_NOT_DERIVED,
        "candidate_only": True,
        "official": False,
        "rule": "Z_u_light=1/sqrt(3)",
        "interpretation": (
            "The light-up mode may have base/coframe participation spread across three internal coframe directions; "
            "the observed mass channel receives one normalized projection."
        ),
        "official_u_over_t": u_row,
        "candidate_u_over_t": candidate,
        "ckm_sin_theta_13_unchanged": sin13["changed"] is False,
        "official_predictions_changed": False,
        "limitation": "Candidate is not derived and is not applied to frozen outputs.",
    }


def ckm_four_projection_payload() -> dict[str, Any]:
    """Return manual CKM four-projection interpretation for the 1/16 exponent."""

    return {
        "status": CKM_FOUR_PROJECTION_CANDIDATE_NOT_DERIVED,
        "candidate_only": True,
        "official": False,
        "rule": "s23_candidate=s23_frozen*(1/2)^(1/16)",
        "projection_layers": (
            "mass/probability dressing to amplitude",
            "full internal mode to left-handed weak component",
            "up-sector dressing to up/down rotation mismatch",
            "diagonal mass dressing to off-diagonal 2-3 overlap correlation",
        ),
        "layer_support": "interpretive only; all four projection layers are not independently derived",
        "limitation": "Candidate remains non-official unless all four projection layers are independently supported.",
    }


def pure_fiber_doublet_payload() -> dict[str, Any]:
    """Return manual pure-fiber doublet interpretation for Z_virt^{u,2}=1/2."""

    return {
        "status": PURE_FIBER_DOUBLET_CANDIDATE_NOT_DERIVED,
        "candidate_only": True,
        "official": False,
        "mode": (6, 0),
        "mode_property": "nonzero pure-fiber middle-up mode with j=0",
        "rule": "two virtual fiber-orientation branches; physical projection selects one, giving rank ratio 1/2",
        "official_c_over_t_branch_changed": False,
        "limitation": "The two-branch doublet does not yet follow from repo geometry/action/spectrum.",
    }


def neutrino_leakage_payload() -> dict[str, Any]:
    """Return candidate-only neutrino leakage ledger."""

    return {
        "status": NEUTRINO_LEAKAGE_LEDGER_CANDIDATE_ONLY,
        "candidate_only": True,
        "ordinary_FTL_claim": False,
        "no_numerical_pmns_claim_added": True,
        "interpretation": (
            "Neutrinos are logged as possible topological leakage modes: weakly field-attached, ghost-like residual boundary modes."
        ),
        "safety": "No ordinary faster-than-light claim and no new PMNS numerical claim.",
    }


def cp_hopf_holonomy_payload() -> dict[str, Any]:
    """Return candidate-only CKM CP Hopf holonomy note."""

    delta = canonical_ckm_delta(build_bhsm_model())
    return {
        "status": CP_HOPF_HOLONOMY_CANDIDATE_NOT_DERIVED,
        "candidate_only": True,
        "official": False,
        "existing_phase_screen": delta,
        "holonomy_machinery_present": True,
        "interpretation": "CKM CP phase may be residual Hopf holonomy after sector projection.",
        "limitation": "Existing Hopf-phase screen is present, but residual-holonomy derivation is not proven here.",
    }


def higgs_surface_mode_payload() -> dict[str, Any]:
    """Return candidate-only Higgs surface-mode framing."""

    return {
        "status": HIGGS_LOWEST_SURFACE_MODE_CANDIDATE_GAP_PROOF_OPEN,
        "candidate_only": True,
        "official": False,
        "interpretation": (
            "Higgs is framed as the lowest global topographic/white-hole-surface mode; "
            "Higgs sets electroweak scale while BHSM sets the internal hierarchy; higher scalar modes are gapped harmonics."
        ),
        "connects_to": ("scalar_decoupling.py", "spectral_gap.py", "scalar_higgs_gap_completion_audit.json"),
        "full_spectral_proof": False,
        "limitation": "Full scalar/topographic spectral proof remains open.",
    }


def audit_payload() -> dict[str, Any]:
    """Return full manual theory-delta audit payload."""

    report = ManualDeltaReport(
        status="BHSM_COMPLETION_MANUAL_THEORY_DELTA_CANDIDATE_ONLY",
        official_outputs_changed=False,
        frozen_files_changed=False,
        lepton_eta_status=SCREENED_ALPHA_PI_LEPTON_CANDIDATE_NOT_DERIVED,
        preferred_lepton_eta_candidate="screened_8alpha_over_9pi",
        best_numeric_lepton_eta_candidate=lepton_eta_delta_payload()["best_numeric_candidate"].candidate,
        light_up_status=LIGHT_UP_THREE_COFRAME_CANDIDATE_NOT_DERIVED,
        ckm_projection_status=CKM_FOUR_PROJECTION_CANDIDATE_NOT_DERIVED,
        pure_fiber_doublet_status=PURE_FIBER_DOUBLET_CANDIDATE_NOT_DERIVED,
        neutrino_ledger_status=NEUTRINO_LEAKAGE_LEDGER_CANDIDATE_ONLY,
        cp_holonomy_status=CP_HOPF_HOLONOMY_CANDIDATE_NOT_DERIVED,
        higgs_surface_mode_status=HIGGS_LOWEST_SURFACE_MODE_CANDIDATE_GAP_PROOF_OPEN,
        blockers_closed=(),
        blockers_remaining=(
            "derive eta_l screening factor from BHSM boundary geometry",
            "derive light-up three-coframe projection",
            "derive CKM four-projection chain",
            "derive pure-fiber doublet from geometry/action/spectrum",
            "derive neutrino leakage ledger from full operator",
            "derive CKM CP residual holonomy",
            "complete Higgs/scalar surface-mode spectral proof",
        ),
    )
    return {
        "report": report,
        "frozen_sanity": frozen_sanity_payload(),
        "lepton_eta": lepton_eta_delta_payload(),
        "light_up_three_coframe": light_up_three_coframe_payload(),
        "ckm_four_projection": ckm_four_projection_payload(),
        "pure_fiber_doublet": pure_fiber_doublet_payload(),
        "neutrino_leakage": neutrino_leakage_payload(),
        "cp_hopf_holonomy": cp_hopf_holonomy_payload(),
        "higgs_surface_mode": higgs_surface_mode_payload(),
        "claim_discipline": {
            "no_official_prediction_change": True,
            "no_retuning": True,
            "no_sm_replacement_claim": True,
            "candidate_only": True,
        },
    }


def _jsonable(value: object) -> object:
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def render_markdown(payload: dict[str, Any] | None = None) -> str:
    """Render manual theory delta as Markdown."""

    payload = payload or audit_payload()
    report = payload["report"]
    lepton = payload["lepton_eta"]
    lines = [
        "# BHSM Completion Gap Closure V2",
        "",
        f"Status: `{report.status}`",
        "",
        "This delta integrates manual theory updates only. Every new item remains candidate-only and non-official.",
        "",
        "## Screened Charged-Lepton Eta Candidate",
        "",
        f"Status: `{payload['report'].lepton_eta_status}`",
        "Preferred candidate: `eta_l=(alpha/pi)*(1-1/Omega_l^2)=8alpha/(9pi)` with `Omega_l=3`.",
        "",
        "| Candidate | eta_l | mu/tau rel err | e/tau rel err | Candidate only |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in lepton["rows"]:
        lines.append(
            f"| `{row.candidate}` | `{row.eta_l}` | `{row.mu_tau_relative_error}` | `{row.e_tau_relative_error}` | `{row.candidate_only}` |"
        )
    lines.extend(
        [
            "",
            f"Best numeric eta candidate: `{payload['report'].best_numeric_lepton_eta_candidate}`.",
            f"Preferred structural eta candidate: `{payload['report'].preferred_lepton_eta_candidate}`.",
            "",
            "## Light-Up Three-Coframe Candidate",
            "",
            f"Status: `{payload['light_up_three_coframe']['status']}`",
            f"Candidate `u/t`: `{payload['light_up_three_coframe']['candidate_u_over_t']}`.",
            "CKM `sin_theta_13` is not changed by this candidate audit.",
            "",
            "## CKM Four-Projection Explanation",
            "",
            f"Status: `{payload['ckm_four_projection']['status']}`",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["ckm_four_projection"]["projection_layers"])
    lines.extend(
        [
            "",
            "## Pure-Fiber c/t Doublet Explanation",
            "",
            f"Status: `{payload['pure_fiber_doublet']['status']}`",
            payload["pure_fiber_doublet"]["rule"],
            "",
            "## Neutrino Leakage Candidate Ledger",
            "",
            f"Status: `{payload['neutrino_leakage']['status']}`",
            f"ordinary_FTL_claim: `{payload['neutrino_leakage']['ordinary_FTL_claim']}`",
            "",
            "## CKM CP Hopf Holonomy Candidate",
            "",
            f"Status: `{payload['cp_hopf_holonomy']['status']}`",
            payload["cp_hopf_holonomy"]["interpretation"],
            "",
            "## Higgs Surface-Mode Framing",
            "",
            f"Status: `{payload['higgs_surface_mode']['status']}`",
            payload["higgs_surface_mode"]["interpretation"],
            "",
            "## Blockers",
            "",
            f"Blockers closed: `{list(report.blockers_closed)}`",
            "",
            "Blockers remaining:",
        ]
    )
    lines.extend(f"- {item}" for item in report.blockers_remaining)
    lines.extend(
        [
            "",
            "## Claim Discipline",
            "",
            "- No official frozen outputs are changed.",
            "- No retuning is performed.",
            "- No Standard Model replacement or proof claim is made.",
            "- No ordinary faster-than-light neutrino claim is made.",
            "- No mass-drift mechanism is introduced.",
            "",
        ]
    )
    return "\n".join(lines)


def export_manual_theory_delta_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export docs, theory note, and audit files."""

    base = Path(root)
    payload = audit_payload()
    markdown = render_markdown(payload)
    paths = {
        "doc_md": base / "docs" / "BHSM_COMPLETION_GAP_CLOSURE_V2.md",
        "doc_json": base / "docs" / "BHSM_COMPLETION_GAP_CLOSURE_V2.json",
        "theory": base / "theory" / "mode_local_stochastic_projection_dressing_completion_note.md",
        "audit_md": base / "audits" / "bhsm_completion_manual_theory_delta_audit.md",
        "audit_json": base / "audits" / "bhsm_completion_manual_theory_delta_audit.json",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["doc_md"].write_text(markdown, encoding="utf-8")
    paths["theory"].write_text(markdown, encoding="utf-8")
    paths["audit_md"].write_text(markdown, encoding="utf-8")
    json_text = json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n"
    paths["doc_json"].write_text(json_text, encoding="utf-8")
    paths["audit_json"].write_text(json_text, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_manual_theory_delta_outputs()
