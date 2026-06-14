"""Charged-lepton eta_l derivation audit.

This module inventories predeclared BHSM sources that could independently fix
the charged-lepton dressing parameter ``eta_l`` in the non-official candidate

    Z_l(k,j) = exp[-eta_l * ((k - 2j)^2 + j^2)].

The audit deliberately separates fitted eta_l from independent structural
candidate values.  No candidate here changes frozen BHSM outputs.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import exp, isfinite, log, pi
from pathlib import Path
from typing import Any

from bhsm_v1 import compare_bhsm_v1_branches
from charged_lepton_precision_closure import (
    CANDIDATE_NOT_OFFICIAL,
    baseline_residuals,
    fit_eta_from_mu_tau,
    frozen_sanity_payload,
)
from constants import ALPHA_INV_LOW_ENERGY, S_OVERLAP
from gauge_couplings import coupling_screens
from higgs_scale import epsilon_alpha
from spectral_gap import MU_H


ETA_L_DERIVED = "ETA_L_DERIVED"
ETA_L_STRUCTURALLY_MOTIVATED_NOT_DERIVED = "ETA_L_STRUCTURALLY_MOTIVATED_NOT_DERIVED"
ETA_L_NUMERICAL_COINCIDENCE_REJECTED = "ETA_L_NUMERICAL_COINCIDENCE_REJECTED"
ETA_L_NOT_DERIVED_BLOCKER = "ETA_L_NOT_DERIVED_BLOCKER"

ALLOWED_CLASSIFICATIONS = (
    ETA_L_DERIVED,
    ETA_L_STRUCTURALLY_MOTIVATED_NOT_DERIVED,
    ETA_L_NUMERICAL_COINCIDENCE_REJECTED,
    ETA_L_NOT_DERIVED_BLOCKER,
)

LEPTON_NORM_EXPONENTS = {
    "tau/reference": 0.0,
    "mu/tau": 5.0,
    "e/tau": 18.0,
}
PRECISION_SCREEN_REL_TOL = 0.01


@dataclass(frozen=True)
class EtaCandidate:
    """One predeclared eta_l candidate source."""

    id: str
    eta_value: float
    source: str
    formula: str
    source_category: str
    independent_of_lepton_residuals: bool
    derived: bool
    structurally_motivated: bool
    numerical_coincidence_only: bool
    relative_difference_to_fitted_eta: float
    mu_tau_prediction: float
    mu_tau_relative_error: float
    e_tau_prediction: float
    e_tau_relative_error: float
    improves_mu_tau: bool
    improves_e_tau: bool
    improves_both: bool
    passes_precision_screen: bool
    closes_lepton_blocker: bool
    notes: tuple[str, ...]


@dataclass(frozen=True)
class EtaDerivationReport:
    """Structured result for the eta_l derivation sprint."""

    fitted_eta_l: float
    candidate_eta_values: tuple[EtaCandidate, ...]
    candidate_sources: tuple[str, ...]
    best_independent_candidate: str | None
    best_precision_candidate: str | None
    classification: str
    closes_lepton_blocker: bool
    candidate_status: str
    official_outputs_changed: bool
    official_lepton_ratios_changed: bool
    notes: tuple[str, ...]


def _baseline_by_quantity() -> dict[str, Any]:
    return {row.quantity: row for row in baseline_residuals()}


def _candidate_seed_inventory() -> tuple[dict[str, Any], ...]:
    """Return the fixed, predeclared eta_l candidate inventory."""

    alpha = 1.0 / ALPHA_INV_LOW_ENERGY
    couplings = coupling_screens()
    omega_l, omega_u, omega_d = 3.0, 6.0, 12.0
    omega_sum = omega_l + omega_u + omega_d
    return (
        {
            "id": "fine_structure_alpha",
            "eta_value": alpha,
            "source": "BHSM low-energy fine-structure input",
            "formula": "alpha",
            "source_category": "gauge",
            "structurally_motivated": True,
            "numerical_coincidence_only": False,
            "notes": ("Uses a BHSM gauge input, but no lepton-boundary derivation fixes eta_l=alpha.",),
        },
        {
            "id": "fine_structure_alpha_over_pi",
            "eta_value": alpha / pi,
            "source": "fine-structure input with one geometric circle factor",
            "formula": "alpha/pi",
            "source_category": "gauge_geometry",
            "structurally_motivated": True,
            "numerical_coincidence_only": False,
            "notes": (
                "Independent of lepton residuals and improves both rows in this audit.",
                "The repo does not derive the pi denominator from a charged-lepton loop/action.",
            ),
        },
        {
            "id": "gauge_alpha_1",
            "eta_value": couplings["alpha_1"],
            "source": "geometric gauge screen alpha_1",
            "formula": "1/(6*pi^2)",
            "source_category": "gauge",
            "structurally_motivated": True,
            "numerical_coincidence_only": False,
            "notes": ("Uses a supplied gauge screen, not a lepton dressing derivation.",),
        },
        {
            "id": "gauge_alpha_2",
            "eta_value": couplings["alpha_2"],
            "source": "geometric gauge screen alpha_2",
            "formula": "2/(6*pi^2)",
            "source_category": "gauge",
            "structurally_motivated": True,
            "numerical_coincidence_only": False,
            "notes": ("Uses a supplied gauge screen, not a lepton dressing derivation.",),
        },
        {
            "id": "gauge_alpha_3",
            "eta_value": couplings["alpha_3"],
            "source": "geometric gauge screen alpha_3",
            "formula": "7/(6*pi^2)",
            "source_category": "gauge",
            "structurally_motivated": True,
            "numerical_coincidence_only": False,
            "notes": ("QCD-like screen is not structurally scoped to charged leptons.",),
        },
        {
            "id": "universal_overlap_width",
            "eta_value": S_OVERLAP,
            "source": "universal overlap width",
            "formula": "S=1/(4*pi)",
            "source_category": "overlap_width",
            "structurally_motivated": True,
            "numerical_coincidence_only": False,
            "notes": ("S is already used in bare overlaps; reusing it as eta_l over-suppresses leptons.",),
        },
        {
            "id": "overlap_width_per_boundary_sum",
            "eta_value": S_OVERLAP / omega_sum,
            "source": "universal width divided by Omega_l+Omega_u+Omega_d",
            "formula": "S/(3+6+12)",
            "source_category": "boundary",
            "structurally_motivated": True,
            "numerical_coincidence_only": False,
            "notes": (
                "Uses boundary targets and S, but no action rule derives this normalization.",
            ),
        },
        {
            "id": "alpha_per_lepton_boundary",
            "eta_value": alpha / omega_l,
            "source": "fine-structure input divided by lepton boundary target",
            "formula": "alpha/Omega_l",
            "source_category": "boundary_gauge",
            "structurally_motivated": True,
            "numerical_coincidence_only": True,
            "notes": (
                "Numerically close to fitted eta_l, but dividing by Omega_l is not derived.",
            ),
        },
        {
            "id": "alpha_per_up_boundary",
            "eta_value": alpha / omega_u,
            "source": "fine-structure input divided by up boundary target",
            "formula": "alpha/Omega_u",
            "source_category": "boundary_gauge",
            "structurally_motivated": False,
            "numerical_coincidence_only": True,
            "notes": ("Wrong-sector boundary target for charged leptons; diagnostic only.",),
        },
        {
            "id": "alpha_per_down_boundary",
            "eta_value": alpha / omega_d,
            "source": "fine-structure input divided by down boundary target",
            "formula": "alpha/Omega_d",
            "source_category": "boundary_gauge",
            "structurally_motivated": False,
            "numerical_coincidence_only": True,
            "notes": ("Wrong-sector boundary target for charged leptons; diagnostic only.",),
        },
        {
            "id": "epsilon_alpha",
            "eta_value": epsilon_alpha(),
            "source": "alpha-anchored Higgs/electroweak residual",
            "formula": "alpha^{-1}/(12*pi^2)-1",
            "source_category": "higgs_scale",
            "structurally_motivated": True,
            "numerical_coincidence_only": False,
            "notes": ("Higgs scale residual is far too large as a lepton dressing eta.",),
        },
        {
            "id": "inverse_hopf_gap",
            "eta_value": 1.0 / MU_H,
            "source": "dimensionless Hopf gap",
            "formula": "1/(64*pi^5)",
            "source_category": "gap",
            "structurally_motivated": True,
            "numerical_coincidence_only": False,
            "notes": ("Gap inverse is independent but too small to repair the warning.",),
        },
        {
            "id": "zvirt_log_per_boundary_sum",
            "eta_value": log(2.0) / omega_sum,
            "source": "existing Z_virt^{u,2}=1/2 amplitude and boundary target sum",
            "formula": "log(2)/(3+6+12)",
            "source_category": "virtual_boundary",
            "structurally_motivated": True,
            "numerical_coincidence_only": False,
            "notes": (
                "Uses existing Z_virt, but Z_virt itself remains not derived and is up-sector scoped.",
            ),
        },
        {
            "id": "zvirt_log_per_64pi",
            "eta_value": log(2.0) / (64.0 * pi),
            "source": "existing Z_virt and Hopf-gap exponent scale",
            "formula": "log(2)/(64*pi)",
            "source_category": "virtual_gap",
            "structurally_motivated": True,
            "numerical_coincidence_only": True,
            "notes": ("A geometric coincidence check only; no BHSM rule selects 64*pi here.",),
        },
    )


def _evaluate_eta_candidate(seed: dict[str, Any]) -> EtaCandidate:
    fitted = fit_eta_from_mu_tau()
    rows = _baseline_by_quantity()
    mu = rows["mu/tau"]
    electron = rows["e/tau"]
    eta = float(seed["eta_value"])
    if eta <= 0 or not isfinite(eta):
        raise ValueError(f"invalid eta candidate {seed['id']}")
    mu_prediction = mu.predicted * exp(-eta * LEPTON_NORM_EXPONENTS["mu/tau"])
    e_prediction = electron.predicted * exp(-eta * LEPTON_NORM_EXPONENTS["e/tau"])
    mu_error = abs(mu_prediction - mu.reference) / abs(mu.reference)
    e_error = abs(e_prediction - electron.reference) / abs(electron.reference)
    improves_mu = mu_error < mu.relative_error
    improves_e = e_error < electron.relative_error
    return EtaCandidate(
        id=str(seed["id"]),
        eta_value=eta,
        source=str(seed["source"]),
        formula=str(seed["formula"]),
        source_category=str(seed["source_category"]),
        independent_of_lepton_residuals=True,
        derived=False,
        structurally_motivated=bool(seed["structurally_motivated"]),
        numerical_coincidence_only=bool(seed["numerical_coincidence_only"]),
        relative_difference_to_fitted_eta=abs(eta - fitted) / abs(fitted),
        mu_tau_prediction=mu_prediction,
        mu_tau_relative_error=mu_error,
        e_tau_prediction=e_prediction,
        e_tau_relative_error=e_error,
        improves_mu_tau=improves_mu,
        improves_e_tau=improves_e,
        improves_both=improves_mu and improves_e,
        passes_precision_screen=mu_error < PRECISION_SCREEN_REL_TOL
        and e_error < PRECISION_SCREEN_REL_TOL,
        closes_lepton_blocker=False,
        notes=tuple(seed["notes"]),
    )


def candidate_eta_values() -> tuple[EtaCandidate, ...]:
    """Return all predeclared eta_l candidates."""

    return tuple(_evaluate_eta_candidate(seed) for seed in _candidate_seed_inventory())


def best_independent_candidate(candidates: tuple[EtaCandidate, ...] | None = None) -> EtaCandidate | None:
    """Return the best independent, structural candidate by held-out e/tau error."""

    candidates = candidates or candidate_eta_values()
    eligible = [
        candidate
        for candidate in candidates
        if candidate.independent_of_lepton_residuals
        and candidate.structurally_motivated
        and not candidate.numerical_coincidence_only
        and candidate.improves_both
    ]
    if not eligible:
        return None
    return min(eligible, key=lambda item: item.e_tau_relative_error)


def eta_derivation_report() -> EtaDerivationReport:
    """Return the sprint-level eta_l derivation report."""

    candidates = candidate_eta_values()
    best = best_independent_candidate(candidates)
    precision_candidates = [candidate for candidate in candidates if candidate.passes_precision_screen]
    best_precision = (
        min(precision_candidates, key=lambda item: item.e_tau_relative_error)
        if precision_candidates
        else None
    )
    derived = [candidate for candidate in candidates if candidate.derived and candidate.improves_both]
    if derived:
        classification = ETA_L_DERIVED
        closes = True
    elif best is not None:
        classification = ETA_L_STRUCTURALLY_MOTIVATED_NOT_DERIVED
        closes = False
    elif any(candidate.numerical_coincidence_only and candidate.improves_both for candidate in candidates):
        classification = ETA_L_NUMERICAL_COINCIDENCE_REJECTED
        closes = False
    else:
        classification = ETA_L_NOT_DERIVED_BLOCKER
        closes = False
    return EtaDerivationReport(
        fitted_eta_l=fit_eta_from_mu_tau(),
        candidate_eta_values=candidates,
        candidate_sources=tuple(candidate.source for candidate in candidates),
        best_independent_candidate=best.id if best else None,
        best_precision_candidate=best_precision.id if best_precision else None,
        classification=classification,
        closes_lepton_blocker=closes,
        candidate_status=CANDIDATE_NOT_OFFICIAL if not closes else "DERIVED_CANDIDATE_READY_FOR_REVIEW",
        official_outputs_changed=False,
        official_lepton_ratios_changed=False,
        notes=(
            "The fitted eta_l remains the only value that exactly fits mu/tau by construction.",
            "alpha/pi is the strongest independent structural candidate in this inventory, but the pi denominator is not derived from the BHSM charged-lepton action.",
            "Numerically close boundary-normalized candidates are rejected unless a boundary rule independently fixes them.",
            "The lepton precision blocker stays open until eta_l has an independent pre-residual derivation.",
        ),
    )


def audit_payload() -> dict[str, Any]:
    """Return the full eta_l audit payload."""

    report = eta_derivation_report()
    return {
        "title": "BHSM charged-lepton eta_l derivation audit",
        "classification": report.classification,
        "fitted_eta_l": report.fitted_eta_l,
        "candidate_eta_values": report.candidate_eta_values,
        "candidate_sources": report.candidate_sources,
        "relative_difference_to_fitted_eta": {
            candidate.id: candidate.relative_difference_to_fitted_eta
            for candidate in report.candidate_eta_values
        },
        "whether_candidate_is_independent": {
            candidate.id: candidate.independent_of_lepton_residuals
            for candidate in report.candidate_eta_values
        },
        "whether_candidate_is_derived": {
            candidate.id: candidate.derived for candidate in report.candidate_eta_values
        },
        "best_independent_candidate": report.best_independent_candidate,
        "best_precision_candidate": report.best_precision_candidate,
        "closes_lepton_blocker": report.closes_lepton_blocker,
        "candidate_status": report.candidate_status,
        "official_outputs_changed": report.official_outputs_changed,
        "official_lepton_ratios_changed": report.official_lepton_ratios_changed,
        "frozen_sanity": frozen_sanity_payload(),
        "official_branch_comparison": compare_bhsm_v1_branches(),
        "baseline_residuals": baseline_residuals(),
        "notes": report.notes,
        "promotion_criteria": (
            "derive eta_l from an action, spectrum, boundary condition, or independently fixed BHSM scale",
            "pre-register eta_l before lepton residual comparison",
            "retain improvement for both mu/tau and e/tau",
            "show charged-lepton scope without altering frozen quark, CKM, gauge, Higgs, or H_T outputs",
        ),
        "rejection_criteria": (
            "eta_l remains fit from mu/tau",
            "candidate value is chosen only because it is numerically close to fitted eta_l",
            "candidate damages the held-out e/tau screen",
            "candidate requires post-freeze official output changes",
        ),
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
    """Render the eta derivation audit as Markdown."""

    payload = payload or audit_payload()
    lines = [
        "# Charged-Lepton Eta Derivation",
        "",
        "## Problem",
        "",
        "The charged-lepton dressing candidate improves precision screens only after fitting `eta_l` from `mu/tau`. This sprint asks whether `eta_l` can be fixed from existing BHSM structure before residual comparison.",
        "",
        "## Current eta_l Status",
        "",
        f"Fitted eta_l: `{payload['fitted_eta_l']}`",
        f"Classification: `{payload['classification']}`",
        f"Lepton precision blocker closed: `{payload['closes_lepton_blocker']}`",
        f"Candidate status: `{payload['candidate_status']}`",
        "",
        "## Candidate Sources Inspected",
        "",
        "| Candidate | eta_l | Source | Formula | Rel diff to fitted | mu/tau err | e/tau err | Independent | Derived | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for candidate in payload["candidate_eta_values"]:
        lines.append(
            "| `{}` | `{}` | {} | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | {} |".format(
                candidate.id,
                candidate.eta_value,
                candidate.source,
                candidate.formula,
                candidate.relative_difference_to_fitted_eta,
                candidate.mu_tau_relative_error,
                candidate.e_tau_relative_error,
                candidate.independent_of_lepton_residuals,
                candidate.derived,
                "<br>".join(candidate.notes),
            )
        )
    lines.extend(
        [
            "",
            "## Rejected Numerical Coincidences",
            "",
            "Boundary-normalized or large-scale combinations are reported but not accepted as derivations. In particular, `alpha/Omega_l`, `log(2)/(64*pi)`, and wrong-sector boundary normalizations are rejected unless a BHSM action or boundary rule fixes them independently.",
            "",
            "## Best Structural eta_l Candidates",
            "",
            f"Best independent candidate: `{payload['best_independent_candidate']}`",
            f"Best precision-screen candidate: `{payload['best_precision_candidate']}`",
            "",
            "`alpha/pi` is independent and structurally motivated by gauge/geometry inputs, and it improves both lepton rows in this audit. It is not derived because the repository does not contain a charged-lepton boundary/action argument that fixes the `1/pi` factor as eta_l.",
            "",
            "## eta_l Derivation Status",
            "",
            "The fitted eta_l remains fitted from `mu/tau`. The strongest non-fitted candidate is structurally motivated but not derived. No candidate in this inventory closes the lepton precision blocker.",
            "",
            "## Consequences For Lepton Precision Blocker",
            "",
            f"Lepton blocker closed: `{payload['closes_lepton_blocker']}`",
            f"Official lepton ratios changed: `{payload['official_lepton_ratios_changed']}`",
            f"Frozen outputs changed: `{payload['official_outputs_changed']}`",
            "",
            "## Promotion Criteria",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["promotion_criteria"])
    lines.extend(["", "## Rejection Criteria", ""])
    lines.extend(f"- {item}" for item in payload["rejection_criteria"])
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {item}" for item in payload["notes"])
    lines.append("")
    return "\n".join(lines)


def export_eta_derivation_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export theory and audit files."""

    base = Path(root)
    payload = audit_payload()
    markdown = render_markdown(payload)
    paths = {
        "theory": base / "theory" / "charged_lepton_eta_derivation.md",
        "audit_md": base / "audits" / "charged_lepton_eta_derivation_audit.md",
        "audit_json": base / "audits" / "charged_lepton_eta_derivation_audit.json",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["theory"].write_text(markdown, encoding="utf-8")
    paths["audit_md"].write_text(markdown, encoding="utf-8")
    paths["audit_json"].write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return payload


if __name__ == "__main__":
    export_eta_derivation_outputs()
