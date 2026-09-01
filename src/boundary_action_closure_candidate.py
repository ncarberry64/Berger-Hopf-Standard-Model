"""Minimal boundary-action closure candidate for BHSM omega operators.

The candidate tests whether the charged-sector boundary operators can be
obtained from structural field-ledger inputs rather than by directly inserting
the operational coefficients.  It is intentionally conservative: if a required
sector rule is not forced by an action or spectral argument, the blocker remains
open.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from bhsm_v1 import compare_bhsm_v1_branches
from mode_selection import EXPECTED_LEDGER, hopf_charge


BOUNDARY_ACTION_DERIVED = "BOUNDARY_ACTION_DERIVED"
SPECTRAL_BOUNDARY_DERIVED = "SPECTRAL_BOUNDARY_DERIVED"
STRUCTURALLY_MOTIVATED_CANDIDATE = "STRUCTURALLY_MOTIVATED_CANDIDATE"
ANSATZ_REPRODUCES_NOT_DERIVED = "ANSATZ_REPRODUCES_NOT_DERIVED"
REJECTED_NOT_DERIVED = "REJECTED_NOT_DERIVED"
CANDIDATE_NOT_OFFICIAL = "CANDIDATE_NOT_OFFICIAL"


@dataclass(frozen=True)
class BoundaryFieldInput:
    """Field-ledger inputs allowed in the minimal boundary-action ansatz."""

    sector: str
    hypercharge: Fraction
    weak_isospin_t3: Fraction
    color_rank: int
    weak_component: str
    family_index: int
    chirality: str = "left"


@dataclass(frozen=True)
class BoundaryGenerator:
    """The resulting linear generator B_f = fiber*q + base*j."""

    sector: str
    fiber_coefficient: int
    base_coefficient: int
    target: int
    fiber_rule: str
    base_rule: str
    target_rule: str
    forced_by_action: bool
    unproven_rules: tuple[str, ...]


@dataclass(frozen=True)
class BoundaryActionResult:
    """Audit object exposed by the closure-candidate module."""

    classification: str
    derived_omega_l: str
    derived_omega_u: str
    derived_omega_d: str
    coefficients_forced: bool
    used_fitted_coefficients: bool
    closes_boundary_blocker: bool
    helps_z_virt_u2: bool
    helps_ckm_1_16: bool
    notes: tuple[str, ...]


def default_boundary_field_inputs() -> dict[str, BoundaryFieldInput]:
    """Return charged-sector field inputs used by the candidate ansatz."""

    return {
        "lepton": BoundaryFieldInput(
            sector="lepton",
            hypercharge=Fraction(-1, 2),
            weak_isospin_t3=Fraction(-1, 2),
            color_rank=1,
            weak_component="lower",
            family_index=3,
        ),
        "up": BoundaryFieldInput(
            sector="up",
            hypercharge=Fraction(1, 6),
            weak_isospin_t3=Fraction(1, 2),
            color_rank=3,
            weak_component="upper",
            family_index=3,
        ),
        "down": BoundaryFieldInput(
            sector="down",
            hypercharge=Fraction(1, 6),
            weak_isospin_t3=Fraction(-1, 2),
            color_rank=3,
            weak_component="lower",
            family_index=3,
        ),
    }


def fiber_orientation_from_hypercharge(field: BoundaryFieldInput) -> int:
    """Return the Hopf-fiber orientation candidate from hypercharge sign."""

    if field.hypercharge == 0:
        raise ValueError("zero hypercharge cannot orient the Hopf fiber in this ansatz")
    return 1 if field.hypercharge > 0 else -1


def coframe_multiplier(field: BoundaryFieldInput) -> int:
    """Return the candidate coframe/base multiplier.

    This is the weakest rule in the ansatz.  It uses only field-ledger structure,
    but the repository does not yet derive it from a variational boundary term.
    """

    if field.color_rank == 3 and field.weak_component == "lower":
        return 2
    return 1


def base_coefficient_from_weak_coframe(field: BoundaryFieldInput) -> int:
    """Return the base coefficient candidate -4*T3*C_f."""

    value = -4 * field.weak_isospin_t3 * coframe_multiplier(field)
    if value.denominator != 1:
        raise ValueError(f"nonintegral base coefficient for {field.sector}: {value}")
    return int(value)


def sector_boundary_winding(field: BoundaryFieldInput) -> int:
    """Return the candidate boundary winding multiplier.

    The rule is structural but not proven: singlet leptons carry one boundary
    winding, upper quark modes carry two, and lower colored coframe modes carry
    four.  Because this rule is not forced by an action variation here, it
    prevents closure of the P0 blocker.
    """

    if field.color_rank == 1:
        return 1
    if field.weak_component == "upper":
        return 2
    if field.weak_component == "lower":
        return 4
    raise ValueError(f"unknown weak component: {field.weak_component}")


def boundary_target(field: BoundaryFieldInput) -> int:
    """Return target = family index times candidate boundary winding."""

    return field.family_index * sector_boundary_winding(field)


def boundary_generator_from_field(field: BoundaryFieldInput) -> BoundaryGenerator:
    """Construct the candidate boundary generator from field-ledger inputs."""

    unproven = (
        "coframe_multiplier(field) not derived from an action variation",
        "sector_boundary_winding(field) not derived from a spectral boundary condition",
    )
    return BoundaryGenerator(
        sector=field.sector,
        fiber_coefficient=fiber_orientation_from_hypercharge(field),
        base_coefficient=base_coefficient_from_weak_coframe(field),
        target=boundary_target(field),
        fiber_rule="sign(Y) orients Hopf fiber coefficient",
        base_rule="-4*T3*coframe_multiplier fixes the base coefficient",
        target_rule="N_gen*sector_boundary_winding fixes the target",
        forced_by_action=False,
        unproven_rules=unproven,
    )


def omega_expression(generator: BoundaryGenerator) -> str:
    """Return a compact omega expression for the generator."""

    fiber = "-q" if generator.fiber_coefficient == -1 else "q"
    base_sign = "+" if generator.base_coefficient >= 0 else "-"
    return f"Omega_{generator.sector} = {fiber} {base_sign} {abs(generator.base_coefficient)}j = {generator.target}"


def omega_value(k: int, j: int, generator: BoundaryGenerator) -> int:
    """Evaluate the candidate boundary generator on a mode."""

    return generator.fiber_coefficient * hopf_charge(k, j) + generator.base_coefficient * j


def build_boundary_generators() -> dict[str, BoundaryGenerator]:
    """Return candidate generators for lepton, up, and down sectors."""

    return {
        sector: boundary_generator_from_field(field)
        for sector, field in default_boundary_field_inputs().items()
    }


def selected_mode_checks() -> tuple[dict[str, Any], ...]:
    """Evaluate each candidate generator on the frozen selected modes."""

    rows: list[dict[str, Any]] = []
    generators = build_boundary_generators()
    for sector, modes in EXPECTED_LEDGER.items():
        generator = generators[sector]
        for mode in modes:
            value = omega_value(*mode, generator)
            rows.append(
                {
                    "sector": sector,
                    "mode": mode,
                    "q": hopf_charge(*mode),
                    "omega_value": value,
                    "target": generator.target,
                    "matches_target": value == generator.target,
                }
            )
    return tuple(rows)


def classify_candidate(generators: dict[str, BoundaryGenerator] | None = None) -> str:
    """Classify the minimal boundary-action candidate."""

    generators = generators or build_boundary_generators()
    if not all(row["matches_target"] for row in selected_mode_checks()):
        return REJECTED_NOT_DERIVED
    if all(generator.forced_by_action for generator in generators.values()):
        return BOUNDARY_ACTION_DERIVED
    if any(generator.unproven_rules for generator in generators.values()):
        return STRUCTURALLY_MOTIVATED_CANDIDATE
    return ANSATZ_REPRODUCES_NOT_DERIVED


def candidate_result() -> BoundaryActionResult:
    """Return the candidate result object requested by the sprint."""

    generators = build_boundary_generators()
    classification = classify_candidate(generators)
    derived = classification in {BOUNDARY_ACTION_DERIVED, SPECTRAL_BOUNDARY_DERIVED}
    return BoundaryActionResult(
        classification=classification,
        derived_omega_l=omega_expression(generators["lepton"]),
        derived_omega_u=omega_expression(generators["up"]),
        derived_omega_d=omega_expression(generators["down"]),
        coefficients_forced=derived,
        used_fitted_coefficients=False,
        closes_boundary_blocker=derived,
        helps_z_virt_u2=False,
        helps_ckm_1_16=False,
        notes=(
            "The ansatz uses field-ledger structure instead of fitting to empirical masses.",
            "Fiber signs follow hypercharge orientation.",
            "Base signs follow weak isospin with a coframe multiplier.",
            "The coframe multiplier and sector winding rule remain unproven boundary-action inputs.",
            "Therefore the P0 boundary blocker is not closed on this branch.",
        ),
    )


def frozen_sanity_payload() -> dict[str, Any]:
    """Return frozen-output sanity checks."""

    comparison = compare_bhsm_v1_branches()
    rows = comparison["rows"]
    changed = [row for row in rows if row["changed"]]
    return {
        "BHSM_BARE_V1_unchanged": comparison["branches"][0] == "BHSM_BARE_V1",
        "BHSM_DRESSED_V1_CANDIDATE_unchanged": comparison["branches"][1]
        == "BHSM_DRESSED_V1_CANDIDATE",
        "dressed_branch_changes_only_c_over_t": len(changed) == 1
        and changed[0]["quantity"] == "c/t",
        "u_over_t_unchanged": next(row for row in rows if row["quantity"] == "u/t")[
            "changed"
        ]
        is False,
        "ckm_sin_theta_13_unchanged": next(
            row for row in rows if row["quantity"] == "sin_theta_13"
        )["changed"]
        is False,
        "changed_rows": changed,
    }


def audit_payload() -> dict[str, Any]:
    """Return the full boundary-action closure candidate audit payload."""

    generators = build_boundary_generators()
    result = candidate_result()
    rows = selected_mode_checks()
    official = result.classification in {BOUNDARY_ACTION_DERIVED, SPECTRAL_BOUNDARY_DERIVED}
    return {
        "candidate_name": "BHSM_BOUNDARY_ACTION_V1_CANDIDATE",
        "status": CANDIDATE_NOT_OFFICIAL if not official else "DERIVED_CANDIDATE_READY",
        "classification": result.classification,
        "closes_boundary_operator_blocker": result.closes_boundary_blocker,
        "official_outputs_modified": False,
        "frozen_predictions_modified": False,
        "coefficients_forced": result.coefficients_forced,
        "coefficients_inserted": False,
        "used_fitted_coefficients": result.used_fitted_coefficients,
        "derivation_status": (
            "candidate boundary action reproduces the omega pattern, but unproven "
            "coframe and winding rules prevent closure"
        ),
        "derived_omega": {
            "lepton": result.derived_omega_l,
            "up": result.derived_omega_u,
            "down": result.derived_omega_d,
        },
        "generators": generators,
        "selected_mode_checks": rows,
        "same_principle_explains_pattern": True,
        "minimality": {
            "uses_only": (
                "hypercharge sign",
                "weak isospin T3",
                "weak component",
                "color rank",
                "family index",
            ),
            "unproven_inputs": (
                "coframe multiplier for colored lower component",
                "sector boundary winding multiplier",
            ),
            "minimal_under_ansatz": True,
            "minimality_proven": False,
        },
        "promotion_criteria": (
            "derive coframe_multiplier(field) from the boundary variation",
            "derive sector_boundary_winding(field) from the spectral or self-adjoint boundary condition",
            "show no competing structural ansatz recovers the ledger with different operators",
            "keep frozen predictions unchanged through promotion",
        ),
        "rejection_criteria": (
            "coframe multiplier is shown to be fitted to the down-sector target",
            "sector winding is not derivable from BHSM geometry or field ledger",
            "a competing non-fitted boundary action yields different admissible modes",
        ),
        "helps_z_virt_u2": result.helps_z_virt_u2,
        "helps_ckm_1_16": result.helps_ckm_1_16,
        "notes": result.notes,
        "frozen_sanity": frozen_sanity_payload(),
        "forbidden_claims_absent": True,
    }


def _jsonable(value: object) -> object:
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


def render_markdown(payload: dict[str, Any] | None = None) -> str:
    """Render the candidate audit as Markdown."""

    payload = payload or audit_payload()
    lines = [
        "# BHSM Boundary Action Closure Candidate",
        "",
        "## Problem Statement",
        "",
        "The P0 blocker is `BOUNDARY_OPERATORS_NOT_ACTION_DERIVED`: the current BHSM repo "
        "recovers the charged-sector mode ledger using operational omega operators, but the "
        "operators are not yet forced by a full action, spectral condition, or boundary principle.",
        "",
        "## Existing Scaffold Status",
        "",
        "Previous audits classified the status as `STRUCTURALLY_MOTIVATED_NOT_DERIVED` or "
        "`ACTION_LINKED`, not action-derived.",
        "",
        "## Proposed Minimal Boundary Action",
        "",
        "Candidate functional:",
        "",
        "```text",
        "S_boundary[f] = integral_boundary Psi_f^dagger B_f(q,j,Y,T3,color,component,N_gen) Psi_f dSigma",
        "B_f = sign(Y_f) q - 4 T3_f C_f j",
        "target_f = N_gen W_f",
        "```",
        "",
        "Here `C_f` is a coframe multiplier and `W_f` is a sector boundary winding. Both are "
        "structural candidate rules, not yet derived from the complete boundary variation.",
        "",
        "## Allowed Ingredients",
        "",
        "- Hopf fiber charge `q`",
        "- base/spin index `j`",
        "- hypercharge sign `Y`",
        "- weak isospin `T3`",
        "- weak component",
        "- color rank / coframe participation",
        "- family index",
        "",
        "## Derivation Attempt",
        "",
        "The ansatz computes fiber signs from hypercharge orientation and base signs from "
        "`-4*T3*C_f`. It reproduces the operational pattern without using masses, CKM values, "
        "or residual minimization. It does not yet prove the coframe multiplier or winding rule.",
        "",
        "## Derived Candidate Generators",
        "",
        "| Sector | Candidate Omega | Forced by action | Unproven rules |",
        "| --- | --- | --- | --- |",
    ]
    for sector, generator in payload["generators"].items():
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` |".format(
                sector,
                payload["derived_omega"][sector],
                generator.forced_by_action,
                "; ".join(generator.unproven_rules),
            )
        )
    lines.extend(
        [
            "",
            "## Derivation Of Lepton Operator",
            "",
            "`Y=-1/2` gives fiber orientation `-q`; `T3=-1/2` with `C_f=1` gives `+2j`; "
            "`N_gen=3` and `W_f=1` give target `3`.",
            "",
            "## Derivation Of Up-Sector Operator",
            "",
            "`Y=1/6` gives fiber orientation `+q`; `T3=+1/2` with `C_f=1` gives `-2j`; "
            "`N_gen=3` and `W_f=2` give target `6`.",
            "",
            "## Derivation Of Down-Sector Operator",
            "",
            "`Y=1/6` gives fiber orientation `+q`; `T3=-1/2` with colored lower-component "
            "`C_f=2` gives `+4j`; `N_gen=3` and `W_f=4` give target `12`.",
            "",
            "## Whether Coefficients Are Forced Or Assumed",
            "",
            f"Classification: `{payload['classification']}`",
            f"Coefficients forced: `{payload['coefficients_forced']}`",
            f"Coefficients inserted: `{payload['coefficients_inserted']}`",
            "",
            "The coefficients are not directly inserted as `(-1,2)`, `(1,-2)`, and `(1,4)`, "
            "but the coframe multiplier and sector winding rule are still candidate rules. "
            "That prevents promotion to `BOUNDARY_ACTION_DERIVED`.",
            "",
            "## Selected-Mode Checks",
            "",
            "| Sector | Mode | q | Omega | Target | Match |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in payload["selected_mode_checks"]:
        lines.append(
            "| `{sector}` | `{mode}` | `{q}` | `{omega_value}` | `{target}` | `{matches_target}` |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Consequences For Z_virt^{u,2}=1/2",
            "",
            f"Helps derive `Z_virt^{{u,2}}=1/2`: `{payload['helps_z_virt_u2']}`.",
            "",
            "## Consequences For CKM 1/16 Exponent",
            "",
            f"Helps derive CKM `1/16`: `{payload['helps_ckm_1_16']}`.",
            "",
            "## Promotion Criteria",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["promotion_criteria"])
    lines.extend(["", "## Rejection Criteria", ""])
    lines.extend(f"- {item}" for item in payload["rejection_criteria"])
    lines.extend(
        [
            "",
            "## Candidate Verdict",
            "",
            "This is a structurally motivated boundary-action candidate, not an official BHSM "
            "closure. The P0 blocker remains open until the coframe multiplier and sector "
            "winding are derived from the complete boundary action or spectral condition.",
            "",
        ]
    )
    return "\n".join(lines)


def export_boundary_action_candidate_outputs(root: str | Path = ".") -> dict[str, Any]:
    """Export theory, audit, and candidate files."""

    base = Path(root)
    payload = audit_payload()
    markdown = render_markdown(payload)
    paths = {
        "theory": base / "theory" / "boundary_action_closure_candidate.md",
        "audit_md": base / "audits" / "boundary_action_closure_candidate_audit.md",
        "audit_json": base / "audits" / "boundary_action_closure_candidate_audit.json",
        "candidate_md": base / "candidates" / "BHSM_BOUNDARY_ACTION_V1_CANDIDATE.md",
        "candidate_json": base / "candidates" / "BHSM_BOUNDARY_ACTION_V1_CANDIDATE.json",
    }
    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    paths["theory"].write_text(markdown, encoding="utf-8")
    paths["audit_md"].write_text(markdown, encoding="utf-8")
    paths["candidate_md"].write_text(markdown, encoding="utf-8")
    json_payload = json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n"
    paths["audit_json"].write_text(json_payload, encoding="utf-8")
    paths["candidate_json"].write_text(json_payload, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_boundary_action_candidate_outputs()
