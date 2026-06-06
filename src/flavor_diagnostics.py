"""Flavor residual root-cause diagnostics for the BHSM model.

This module diagnoses the current up-sector and CKM V_ub residuals. It does
not tune parameters or change the charged-sector mode ledger.
"""

from __future__ import annotations

import json
from math import isfinite, log10, pi, sqrt
from pathlib import Path
from typing import Any

from berger_spectrum import berger_lambda, hopf_charge
from bhsm_config import GeometryConfig, canonical_geometry_config
from bhsm_model import BHSMModel, compute_ckm_from_internal_rules, compute_yukawa_ratios
from ckm import ckm_angles_from_bhsm_ratios
from constants import ALPHA_INV_LOW_ENERGY, EMPIRICAL_MASS_RATIOS, S_OVERLAP
from mode_selection import admissible_modes, omega_up
from prediction_ledger import CKM_REFERENCES
from yukawa_overlap import mass_ratio


UP_MIDDLE_MODE = (6, 0)
UP_LIGHT_MODE = (10, 1)


def _relative_error(predicted: float, reference: float) -> float:
    return abs((predicted - reference) / reference)


def _log_error(predicted: float, reference: float) -> float:
    if predicted <= 0 or reference <= 0:
        raise ValueError("log error requires positive values")
    return float(log10(predicted / reference))


def mode_overlap_breakdown(
    sector: str,
    mode: tuple[int, int],
    geometry_config: GeometryConfig | None = None,
) -> dict[str, object]:
    """Return the Berger overlap calculation for one mode."""

    config = canonical_geometry_config() if geometry_config is None else geometry_config
    k, j = mode
    lam = berger_lambda(k, j, a=config.a)
    return {
        "sector": sector,
        "mode": (k, j),
        "q": hopf_charge(k, j),
        "omega_u": omega_up(k, j) if sector == "up_quarks" else None,
        "geometry": config.name,
        "a": config.a,
        "S": S_OVERLAP,
        "lambda": lam,
        "suppression": mass_ratio(k, j, a=config.a, s=S_OVERLAP),
    }


def up_sector_diagnostic(model: BHSMModel) -> dict[str, object]:
    """Return current up-sector residual diagnostics."""

    ratios = compute_yukawa_ratios(model)["up_quarks"]
    refs = EMPIRICAL_MASS_RATIOS["up_quarks"]
    c_pred = ratios["middle"]
    u_pred = ratios["light"]
    c_ref = refs["middle"]
    u_ref = refs["light"]
    sin13_pred = sqrt(u_pred)
    sin13_ref = CKM_REFERENCES["sin_theta_13"]
    return {
        "geometry": model.geometry_config.name,
        "a": model.geometry_config.a,
        "S": S_OVERLAP,
        "middle_mode": mode_overlap_breakdown("up_quarks", UP_MIDDLE_MODE, model.geometry_config),
        "light_mode": mode_overlap_breakdown("up_quarks", UP_LIGHT_MODE, model.geometry_config),
        "predicted": {
            "c_over_t": c_pred,
            "u_over_t": u_pred,
            "sqrt_u_over_t": sin13_pred,
        },
        "reference": {
            "c_over_t": c_ref,
            "u_over_t": u_ref,
            "sin_theta_13": sin13_ref,
        },
        "relative_error": {
            "c_over_t": _relative_error(c_pred, c_ref),
            "u_over_t": _relative_error(u_pred, u_ref),
            "sin_theta_13": _relative_error(sin13_pred, sin13_ref),
        },
        "log_error": {
            "c_over_t": _log_error(c_pred, c_ref),
            "u_over_t": _log_error(u_pred, u_ref),
            "sin_theta_13": _log_error(sin13_pred, sin13_ref),
        },
        "notes": (
            "Up-sector references are scheme-sensitive because no uniform quark mass scheme/scale is implemented.",
            "No mode or overlap parameter is changed by this diagnostic.",
        ),
    }


def compare_overlap_constants() -> dict[str, object]:
    """Return current and conceptual overlap constants used in sensitivity scans."""

    alpha_scaled_a = ALPHA_INV_LOW_ENERGY / (12.0 * pi**2)
    canonical = canonical_geometry_config()
    return {
        "current": {
            "geometry": canonical.name,
            "a": canonical.a,
            "S": S_OVERLAP,
        },
        "conceptual_sensitivity_values": {
            "S": S_OVERLAP,
            "a_values": (0.573, 1.0, alpha_scaled_a),
        },
        "sensitivity_only": True,
        "note": "These values are compared diagnostically and do not revise the model default.",
    }


def _suppression_for_mode(mode: tuple[int, int], a: float) -> float:
    return mass_ratio(mode[0], mode[1], a=a, s=S_OVERLAP)


def scan_up_admissible_modes(
    k_max: int,
    geometry_config: GeometryConfig | None = None,
) -> dict[str, object]:
    """Scan admissible up-sector modes without changing the ledger."""

    config = canonical_geometry_config() if geometry_config is None else geometry_config
    modes = admissible_modes("up", k_max)
    refs = EMPIRICAL_MASS_RATIOS["up_quarks"]
    rows: list[dict[str, object]] = []
    for mode in modes[: max(5, min(len(modes), 5))]:
        suppression = _suppression_for_mode(mode, config.a)
        rows.append(
            {
                "mode": mode,
                "q": hopf_charge(*mode),
                "omega_u": omega_up(*mode),
                "lambda": berger_lambda(*mode, a=config.a),
                "suppression": suppression,
                "relative_error_vs_u_over_t": _relative_error(suppression, refs["light"]),
                "log_error_vs_u_over_t": _log_error(suppression, refs["light"]),
            }
        )
    current_index = modes.index(UP_LIGHT_MODE) if UP_LIGHT_MODE in modes else None
    next_mode = modes[current_index + 1] if current_index is not None and current_index + 1 < len(modes) else None
    next_assessment: dict[str, object] | None = None
    if next_mode is not None:
        next_suppression = _suppression_for_mode(next_mode, config.a)
        if next_suppression > refs["light"]:
            direction = "undercorrects"
        elif next_suppression < refs["light"]:
            direction = "overcorrects"
        else:
            direction = "matches"
        next_assessment = {
            "next_mode_after_current_light": next_mode,
            "suppression": next_suppression,
            "reference_u_over_t": refs["light"],
            "assessment": direction,
            "note": "Ledger is not changed; this is an admissible-mode sensitivity diagnostic.",
        }
    return {
        "k_max": k_max,
        "geometry": config.name,
        "a": config.a,
        "rule": "Omega_u = q - 2j = 6, q even, q >= 6",
        "first_five": rows,
        "current_light_mode": UP_LIGHT_MODE,
        "next_mode_assessment": next_assessment,
        "ledger_changed": False,
    }


def _constant_sensitivity_table() -> list[dict[str, object]]:
    constants = compare_overlap_constants()["conceptual_sensitivity_values"]
    rows: list[dict[str, object]] = []
    refs = EMPIRICAL_MASS_RATIOS["up_quarks"]
    sin13_ref = CKM_REFERENCES["sin_theta_13"]
    for a in constants["a_values"]:
        c_pred = _suppression_for_mode(UP_MIDDLE_MODE, float(a))
        u_pred = _suppression_for_mode(UP_LIGHT_MODE, float(a))
        sin13 = sqrt(u_pred)
        rows.append(
            {
                "a": float(a),
                "S": S_OVERLAP,
                "c_over_t": c_pred,
                "u_over_t": u_pred,
                "sin_theta_13": sin13,
                "relative_error": {
                    "c_over_t": _relative_error(c_pred, refs["middle"]),
                    "u_over_t": _relative_error(u_pred, refs["light"]),
                    "sin_theta_13": _relative_error(sin13, sin13_ref),
                },
                "sensitivity_only": True,
            }
        )
    return rows


def ckm_rule_breakdown(model: BHSMModel) -> dict[str, object]:
    """Compare current and exploratory CKM V_ub-related rules."""

    ratios = compute_yukawa_ratios(model)
    angles = ckm_angles_from_bhsm_ratios(ratios)
    current = angles["sin_theta_13"]
    d_over_s_factor = angles["sin_theta_12"]
    s_over_b = ratios["down_quarks"]["middle"]
    delta_lambda_lr = abs(
        berger_lambda(*UP_LIGHT_MODE, a=model.geometry_config.a)
        - berger_lambda(*UP_MIDDLE_MODE, a=model.geometry_config.a)
    )
    exp_factor = 10 ** (-(S_OVERLAP * delta_lambda_lr) / 2.302585092994046)
    alternatives = [
        {
            "id": "sqrt_u_over_t_times_sqrt_d_over_s",
            "formula": "sqrt(u/t) * sqrt(d/s)",
            "value": current * d_over_s_factor,
            "status": "EXPLORATORY_ONLY",
        },
        {
            "id": "sqrt_u_over_t_times_s_over_b",
            "formula": "sqrt(u/t) * (s/b)",
            "value": current * s_over_b,
            "status": "EXPLORATORY_ONLY",
        },
        {
            "id": "sqrt_u_over_t_times_exp_delta_lambda_lr",
            "formula": "sqrt(u/t) * exp[-S Delta lambda_LR]",
            "value": current * exp_factor,
            "delta_lambda_lr": delta_lambda_lr,
            "status": "EXPLORATORY_ONLY",
        },
    ]
    for row in alternatives:
        row["relative_error_vs_sin13"] = _relative_error(float(row["value"]), CKM_REFERENCES["sin_theta_13"])
        row["log_error_vs_sin13"] = _log_error(float(row["value"]), CKM_REFERENCES["sin_theta_13"])
    return {
        "current_rule": {
            "formula": "sqrt(u/t)",
            "value": current,
            "reference": CKM_REFERENCES["sin_theta_13"],
            "relative_error": _relative_error(current, CKM_REFERENCES["sin_theta_13"]),
            "log_error": _log_error(current, CKM_REFERENCES["sin_theta_13"]),
            "status": "IMPLEMENTED_SCREEN",
        },
        "exploratory_alternatives": alternatives,
        "adopted_alternative": None,
        "note": "Alternatives are diagnostics only and are not adopted as model rules.",
    }


def scheme_sensitivity_report() -> dict[str, object]:
    """Return the quark-mass scheme diagnostic note."""

    return {
        "scheme_sensitive": True,
        "affected_rows": (
            "mass_ratio.up_quarks.middle",
            "mass_ratio.up_quarks.light",
            "mass_ratio.down_quarks.middle",
            "mass_ratio.down_quarks.light",
        ),
        "note": (
            "The repository does not implement a uniform renormalization scheme/scale "
            "for u, c, and t mass references. This marks the comparison as "
            "scheme-sensitive but does not hide the residual."
        ),
    }


def flavor_root_cause_report(model: BHSMModel) -> dict[str, object]:
    """Return the full up-sector and CKM V_ub diagnostic report."""

    up = up_sector_diagnostic(model)
    scan = scan_up_admissible_modes(40, model.geometry_config)
    constants = compare_overlap_constants()
    sensitivity = _constant_sensitivity_table()
    ckm = ckm_rule_breakdown(model)
    scheme = scheme_sensitivity_report()
    likely = (
        "The localized tension is not caused by a constants mismatch or missing "
        "CKM implementation. It traces to the current up-sector overlap ledger "
        "and the sqrt(u/t) V_ub screen, with quark mass-scheme sensitivity and "
        "possible missing representation/left-right normalization remaining open."
    )
    return {
        "up_sector": up,
        "up_admissible_scan": scan,
        "constants_audit": constants,
        "constant_sensitivity_table": sensitivity,
        "ckm_rule_breakdown": ckm,
        "mass_scheme": scheme,
        "likely_root_cause_classification": {
            "constants_or_implementation_mismatch": False,
            "mass_scheme_comparison_issue": True,
            "mode_selection_issue": "not resolved; next admissible mode sensitivity is diagnostic only",
            "missing_representation_normalization_factor": "open",
            "ckm_rule_limitation": True,
            "genuine_bhsm_tension": "possible under current rules",
            "summary": likely,
        },
        "model_changed": False,
        "limitations": (
            "Diagnostic only; no parameters, modes, or CKM rules are tuned.",
            "Exploratory CKM alternatives are not adopted.",
        ),
    }


def _jsonable(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def export_flavor_diagnostic_json(report: dict[str, object], path: str | Path) -> None:
    """Export flavor diagnostic report as JSON."""

    Path(path).write_text(json.dumps(_jsonable(report), indent=2, sort_keys=True) + "\n")


def export_flavor_diagnostic_markdown(report: dict[str, object], path: str | Path) -> None:
    """Export flavor diagnostic report as Markdown."""

    up = report["up_sector"]
    scan = report["up_admissible_scan"]
    ckm = report["ckm_rule_breakdown"]
    lines = [
        "# Flavor Residual Diagnostic",
        "",
        "This diagnostic does not tune parameters, change modes, or adopt exploratory CKM rules.",
        "",
        "## Current Up-Sector Constants",
        "",
        f"- a = `{up['a']}`",
        f"- S = `{up['S']}`",
        f"- lambda_(6,0) = `{up['middle_mode']['lambda']}`",
        f"- lambda_(10,1) = `{up['light_mode']['lambda']}`",
        "",
        "## Current Residuals",
        "",
        f"- c/t predicted `{up['predicted']['c_over_t']}`, reference `{up['reference']['c_over_t']}`",
        f"- u/t predicted `{up['predicted']['u_over_t']}`, reference `{up['reference']['u_over_t']}`",
        f"- sin(theta_13) predicted `{up['predicted']['sqrt_u_over_t']}`, reference `{up['reference']['sin_theta_13']}`",
        "",
        "## First Five Admissible Up Modes",
        "",
        "| Mode | q | Omega_u | lambda | suppression | rel error vs u/t |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in scan["first_five"]:
        lines.append(
            f"| `{tuple(row['mode'])}` | {row['q']} | {row['omega_u']} | {row['lambda']} | {row['suppression']} | {row['relative_error_vs_u_over_t']} |"
        )
    lines.extend(
        [
            "",
            "## Next-Mode Assessment",
            "",
            json.dumps(_jsonable(scan["next_mode_assessment"]), indent=2, sort_keys=True),
            "",
            "## Constant Sensitivity Table",
            "",
            "```json",
            json.dumps(_jsonable(report["constant_sensitivity_table"]), indent=2, sort_keys=True),
            "```",
            "",
            "## CKM Rule Breakdown",
            "",
            f"Current rule: `{ckm['current_rule']['formula']}` gives `{ckm['current_rule']['value']}`.",
            "",
            "Exploratory alternatives are diagnostics only:",
            "",
            "```json",
            json.dumps(_jsonable(ckm["exploratory_alternatives"]), indent=2, sort_keys=True),
            "```",
            "",
            "## Likely Root Cause",
            "",
            report["likely_root_cause_classification"]["summary"],
            "",
            "## Limitations",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.append("")
    Path(path).write_text("\n".join(lines))
