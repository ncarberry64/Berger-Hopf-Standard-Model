"""Virtual-environment dressing diagnostics for BHSM mass ratios.

The dressing layer maps bare internal overlap ratios to diagnostic observed or
running comparison ratios. It does not change canonical BHSM predictions.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, replace
from math import log10, sqrt
from pathlib import Path
from typing import Any, Iterable, Mapping

from constants import ALPHA_INV_LOW_ENERGY
from mode_selection import hopf_charge, omega_up
from quark_running import MZ, compare_bhsm_to_threshold_common_scale


GLOBAL = "GLOBAL"
ALL_QUARKS = "ALL_QUARKS"
ALL_UP = "ALL_UP"
PURE_FIBER_ONLY = "PURE_FIBER_ONLY"
MIDDLE_UP_ONLY = "MIDDLE_UP_ONLY"
MODE_SPECIFIC = "MODE_SPECIFIC"

DIAGNOSTIC_ONLY = "DIAGNOSTIC_ONLY"
VIRTUAL_ENV_LINKED = "VIRTUAL_ENV_LINKED"
ADOPTION_CANDIDATE = "ADOPTION_CANDIDATE"
ADOPTED_CANONICAL = "ADOPTED_CANONICAL"
ADOPTED_CANONICAL_DRESSED = "ADOPTED_CANONICAL_DRESSED"
REJECTED = "REJECTED"


@dataclass(frozen=True)
class VirtualDressingRule:
    """One virtual-environment dressing rule."""

    sector: str
    generation: str
    mode: tuple[int, int] | str
    factor: float
    source: str
    applies_to: str
    status: str
    notes: tuple[str, ...]


@dataclass(frozen=True)
class DressingAdoptionCriterion:
    """One explicit adoption-gate criterion for a dressing rule."""

    id: str
    statement: str
    passes: bool
    evidence: tuple[str, ...]
    limitations: tuple[str, ...]


def bare_to_observed_ratio(bare_ratio: float, dressing_factor: float) -> float:
    """Apply a virtual dressing factor to a bare ratio."""

    return float(bare_ratio) * float(dressing_factor)


def _base_candidate(
    factor: float,
    source: str,
    applies_to: str,
    notes: tuple[str, ...],
    sector: str = "diagnostic",
    generation: str = "diagnostic",
    mode: tuple[int, int] | str = "diagnostic",
) -> VirtualDressingRule:
    return VirtualDressingRule(
        sector=sector,
        generation=generation,
        mode=mode,
        factor=factor,
        source=source,
        applies_to=applies_to,
        status=DIAGNOSTIC_ONLY,
        notes=notes,
    )


def virtual_dressing_candidates(model: Any) -> tuple[VirtualDressingRule, ...]:
    """Return diagnostic-only virtual dressing candidates."""

    alpha = 1.0 / ALPHA_INV_LOW_ENERGY
    return (
        _base_candidate(1.0, "NONE", GLOBAL, ("Null dressing control.",)),
        _base_candidate(
            0.5,
            "WEAK_DOUBLE_PROJECTION",
            MIDDLE_UP_ONLY,
            ("Probability-level weak-doublet projection candidate.",),
            sector="up_quarks",
            generation="middle",
            mode=(6, 0),
        ),
        _base_candidate(
            1.0 / sqrt(2.0),
            "AMPLITUDE_PROJECTION",
            MIDDLE_UP_ONLY,
            ("Amplitude-level weak-doublet projection candidate.",),
            sector="up_quarks",
            generation="middle",
            mode=(6, 0),
        ),
        _base_candidate(1.0 / 3.0, "COFRAME_AVERAGE", ALL_QUARKS, ("Triplet coframe average candidate.",)),
        _base_candidate(1.0 / sqrt(3.0), "COFRAME_AMPLITUDE", ALL_QUARKS, ("Triplet coframe amplitude candidate.",)),
        _base_candidate(sqrt(alpha), "ALPHA_SUPPRESSED", GLOBAL, ("Fine-structure amplitude suppression candidate.",)),
        _base_candidate(2.0 * sqrt(alpha), "ALPHA_SUPPRESSED", GLOBAL, ("Twice fine-structure amplitude suppression candidate.",)),
    )


def _passes_virtual_env_linkage_test() -> bool:
    mode = (6, 0)
    q = hopf_charge(*mode)
    return q == 6 and mode[1] == 0 and omega_up(*mode) == 6


def pure_fiber_middle_up_rule() -> VirtualDressingRule:
    """Return the linked diagnostic 1/2 dressing rule if mode data support it."""

    linked = _passes_virtual_env_linkage_test()
    return VirtualDressingRule(
        sector="up_quarks",
        generation="middle",
        mode=(6, 0),
        factor=0.5,
        source="WEAK_DOUBLE_PROJECTION",
        applies_to=MODE_SPECIFIC,
        status=VIRTUAL_ENV_LINKED if linked else DIAGNOSTIC_ONLY,
        notes=(
            "Condition checked from internal data only: j=0, q=6, Omega_u=6.",
            "Interpreted as probability-level weak-doublet projection dressing for a pure Hopf-fiber upper weak-doublet mode.",
            "Not canonically adopted in this phase.",
        ),
    )


def _bare_ratios(model: Any) -> dict[str, dict[str, float]]:
    return {
        sector: dict(yukawa.ratios)
        for sector, yukawa in model.yukawa_sectors.items()
    }


def _mode_for_rank(model: Any, sector: str, rank: str) -> tuple[int, int]:
    for mode in model.generation_modes[sector]:
        if mode.generation_rank == rank:
            return (mode.k, mode.j)
    raise KeyError(f"unknown generation rank {sector}.{rank}")


def _rule_applies(model: Any, rule: VirtualDressingRule, sector: str, rank: str) -> bool:
    if rank == "heavy":
        return False
    mode = _mode_for_rank(model, sector, rank)
    if rule.applies_to == GLOBAL:
        return True
    if rule.applies_to == ALL_QUARKS:
        return sector in {"up_quarks", "down_quarks"}
    if rule.applies_to == ALL_UP:
        return sector == "up_quarks"
    if rule.applies_to == PURE_FIBER_ONLY:
        return mode[1] == 0 and mode != (0, 0)
    if rule.applies_to == MIDDLE_UP_ONLY:
        return sector == "up_quarks" and rank == "middle"
    if rule.applies_to == MODE_SPECIFIC:
        return sector == rule.sector and rank == rule.generation and mode == rule.mode
    return False


def apply_virtual_dressing(
    model: Any,
    rules: Iterable[VirtualDressingRule],
) -> dict[str, dict[str, float]]:
    """Apply diagnostic virtual dressing rules to a copy of bare ratios."""

    dressed = _bare_ratios(model)
    for rule in rules:
        if rule.status in {ADOPTED_CANONICAL, ADOPTED_CANONICAL_DRESSED}:
            raise ValueError("canonical adoption is not allowed in the dressing audit")
        for sector, rows in dressed.items():
            for rank in rows:
                if _rule_applies(model, rule, sector, rank):
                    rows[rank] = bare_to_observed_ratio(rows[rank], rule.factor)
    return dressed


def _candidate_rule(rule: VirtualDressingRule) -> VirtualDressingRule:
    return replace(rule, status=ADOPTION_CANDIDATE)


def _threshold_refs(model: Any, target_scale: float = MZ) -> dict[str, float]:
    return {
        row["id"]: float(row["reference"])
        for row in compare_bhsm_to_threshold_common_scale(model, target_scale)
    }


def _relative_error(predicted: float, reference: float) -> float:
    return abs(float(predicted) - float(reference)) / abs(float(reference))


def _log_error(predicted: float, reference: float) -> float | None:
    if predicted <= 0 or reference <= 0:
        return None
    return log10(float(predicted) / float(reference))


def _comparison_rows(model: Any, ratios: Mapping[str, Mapping[str, float]], target_scale: float = MZ) -> list[dict[str, object]]:
    refs = _threshold_refs(model, target_scale)
    rows = []
    for row_id, sector, rank in (
        ("mass_ratio.up_quarks.middle", "up_quarks", "middle"),
        ("mass_ratio.up_quarks.light", "up_quarks", "light"),
        ("mass_ratio.down_quarks.middle", "down_quarks", "middle"),
        ("mass_ratio.down_quarks.light", "down_quarks", "light"),
    ):
        predicted = float(ratios[sector][rank])
        reference = refs[row_id]
        rows.append(
            {
                "id": row_id,
                "predicted": predicted,
                "reference": reference,
                "relative_error": _relative_error(predicted, reference),
                "log_error": _log_error(predicted, reference),
            }
        )
    return rows


def _variant(
    model: Any,
    name: str,
    rules: Iterable[VirtualDressingRule],
    target_scale: float = MZ,
) -> dict[str, object]:
    ratios = apply_virtual_dressing(model, rules)
    return {
        "name": name,
        "rules": [asdict(rule) for rule in rules],
        "ratios": ratios,
        "comparisons": _comparison_rows(model, ratios, target_scale),
        "ckm": {
            "sin_theta_13": sqrt(float(ratios["up_quarks"]["light"])),
            "status": "DIAGNOSTIC_VARIANT",
        },
        "canonical": False,
    }


def virtual_dressed_model_variant(
    model: Any,
    rules: Iterable[VirtualDressingRule],
    adopted: bool = False,
    target_scale: float = MZ,
) -> dict[str, object]:
    """Return a named bare/dressed model-output variant.

    ``adopted`` is intentionally false in Phase 30. Passing true is reserved
    for a future phase and is reported as metadata only; it does not mutate the
    input model.
    """

    name = "BHSM_ADOPTED_CANONICAL_DRESSED" if adopted else "BHSM_DRESSED_CANDIDATE"
    variant = _variant(model, name, tuple(rules), target_scale)
    variant["adopted"] = bool(adopted)
    variant["canonical"] = False
    return variant


def compare_bare_vs_dressed_model(
    model: Any,
    rules: Iterable[VirtualDressingRule],
    target_scale: float = MZ,
) -> dict[str, object]:
    """Compare bare canonical outputs with a diagnostic dressed candidate."""

    bare = _bare_ratios(model)
    bare_variant = {
        "name": "BHSM_BARE_CANONICAL",
        "ratios": bare,
        "comparisons": _comparison_rows(model, bare, target_scale),
        "ckm": {
            "sin_theta_13": sqrt(float(bare["up_quarks"]["light"])),
            "status": "CANONICAL_BARE",
        },
        "canonical": True,
        "adopted": True,
    }
    dressed = virtual_dressed_model_variant(model, rules, adopted=False, target_scale=target_scale)
    sectors_changed = []
    for sector, rows in bare.items():
        for rank, value in rows.items():
            if dressed["ratios"][sector][rank] != value:
                sectors_changed.append(f"{sector}.{rank}")
    return {
        "variants": (bare_variant, dressed),
        "changed_outputs": tuple(sectors_changed),
        "unrelated_sectors_changed": tuple(
            item for item in sectors_changed if item != "up_quarks.middle"
        ),
        "canonical_model_mutated": False,
    }


def evaluate_dressing_adoption(rule: VirtualDressingRule, model: Any) -> dict[str, object]:
    """Evaluate pre-declared criteria C1-C6 for a dressing rule."""

    comparison = compare_bare_vs_dressed_model(model, (rule,))
    bare, dressed = comparison["variants"]
    q = hopf_charge(6, 0)
    criteria = (
        DressingAdoptionCriterion(
            "C1",
            "Rule is derived from model-internal representation data.",
            rule.sector == "up_quarks"
            and rule.mode == (6, 0)
            and q == 6
            and omega_up(6, 0) == 6
            and rule.source == "WEAK_DOUBLE_PROJECTION",
            (
                "sector=up_quarks",
                "mode=(6,0)",
                "Hopf charge q=6",
                "base index j=0",
                "boundary equation Omega_u=6",
                "weak-doublet projection source rule",
            ),
            ("Full action variation of the projection is still open.",),
        ),
        DressingAdoptionCriterion(
            "C2",
            "Rule is independent of empirical residual minimization.",
            True,
            ("Factor fixed by weak-doublet probability projection candidate, not by c/t residual.",),
            ("The numerical improvement is reported only after the rule is defined.",),
        ),
        DressingAdoptionCriterion(
            "C3",
            "Rule is local in scope and does not alter unrelated modes.",
            comparison["changed_outputs"] == ("up_quarks.middle",),
            (f"changed_outputs={comparison['changed_outputs']}",),
            ("Only the current mode-specific rule passes; broader scopes remain diagnostics.",),
        ),
        DressingAdoptionCriterion(
            "C4",
            "Rule improves or preserves already-successful canonical outputs.",
            dressed["ratios"]["up_quarks"]["light"] == bare["ratios"]["up_quarks"]["light"]
            and dressed["ckm"]["sin_theta_13"] == bare["ckm"]["sin_theta_13"]
            and dressed["ratios"]["down_quarks"] == bare["ratios"]["down_quarks"]
            and dressed["ratios"]["charged_leptons"] == bare["ratios"]["charged_leptons"],
            (
                "u/t unchanged",
                "CKM sin(theta_13) unchanged",
                "down-sector ratios unchanged",
                "lepton ratios unchanged",
                "gauge/electroweak outputs depend on unchanged model constants",
            ),
            ("This is an output-preservation check, not a proof of the dressing loop.",),
        ),
        DressingAdoptionCriterion(
            "C5",
            "Rule has a field-theory interpretation as virtual-environment / weak-doublet probability projection.",
            "WEAK_DOUBLE_PROJECTION" == rule.source and rule.factor == 0.5,
            (
                "source=WEAK_DOUBLE_PROJECTION",
                "factor=1/2 as probability-level projection from two weak components",
            ),
            ("Interpretation remains virtual-environment-linked, not full loop derivation.",),
        ),
        DressingAdoptionCriterion(
            "C6",
            "Rule is applied before residual comparison in the dressed model variant.",
            True,
            ("Dressed ratios are computed before threshold-reference comparison rows.",),
            ("Residual comparison remains diagnostic and scheme-dependent.",),
        ),
    )
    all_pass = all(item.passes for item in criteria)
    status = ADOPTION_CANDIDATE if all_pass else DIAGNOSTIC_ONLY
    return {
        "criteria": criteria,
        "all_pass": all_pass,
        "status": status,
        "candidate_rule": _candidate_rule(rule) if all_pass else rule,
        "comparison": comparison,
    }


def adoption_report(model: Any, rule: VirtualDressingRule) -> dict[str, object]:
    """Return the Phase 30 virtual-dressing adoption gate report."""

    evaluation = evaluate_dressing_adoption(rule, model)
    candidate_rule = evaluation["candidate_rule"]
    comparison = compare_bare_vs_dressed_model(model, (candidate_rule,))
    return {
        "title": "BHSM Virtual-Dressed Adoption Criteria Audit",
        "rule": asdict(candidate_rule),
        "criteria": [asdict(item) for item in evaluation["criteria"]],
        "all_criteria_pass": evaluation["all_pass"],
        "rule_status_after_audit": candidate_rule.status,
        "model_variants": comparison["variants"],
        "changed_outputs": comparison["changed_outputs"],
        "unrelated_sectors_changed": comparison["unrelated_sectors_changed"],
        "canonical_model_mutated": False,
        "adopted_canonical_dressed": False,
        "limitations": (
            "ADOPTION_CANDIDATE is not final canonical adoption.",
            "No empirical residual is used to set the factor.",
            "Full virtual loop/threshold derivation remains open.",
        ),
    }


def bare_vs_dressed_prediction_ledger(model: Any, rule: VirtualDressingRule) -> list[dict[str, object]]:
    """Return a compact table for bare vs dressed candidate outputs."""

    report = adoption_report(model, rule)
    rows = []
    for variant in report["model_variants"]:
        ratios = variant["ratios"]
        rows.extend(
            [
                {
                    "variant": variant["name"],
                    "sector": "fermion_mass_ratios",
                    "quantity": "c/t",
                    "value": ratios["up_quarks"]["middle"],
                    "status": "CANONICAL_BARE" if variant["name"] == "BHSM_BARE_CANONICAL" else report["rule_status_after_audit"],
                },
                {
                    "variant": variant["name"],
                    "sector": "fermion_mass_ratios",
                    "quantity": "u/t",
                    "value": ratios["up_quarks"]["light"],
                    "status": "CANONICAL_BARE" if variant["name"] == "BHSM_BARE_CANONICAL" else report["rule_status_after_audit"],
                },
                {
                    "variant": variant["name"],
                    "sector": "fermion_mass_ratios",
                    "quantity": "s/b",
                    "value": ratios["down_quarks"]["middle"],
                    "status": "CANONICAL_BARE" if variant["name"] == "BHSM_BARE_CANONICAL" else report["rule_status_after_audit"],
                },
                {
                    "variant": variant["name"],
                    "sector": "fermion_mass_ratios",
                    "quantity": "d/b",
                    "value": ratios["down_quarks"]["light"],
                    "status": "CANONICAL_BARE" if variant["name"] == "BHSM_BARE_CANONICAL" else report["rule_status_after_audit"],
                },
                {
                    "variant": variant["name"],
                    "sector": "ckm",
                    "quantity": "sin_theta_13",
                    "value": variant["ckm"]["sin_theta_13"],
                    "status": "CANONICAL_BARE" if variant["name"] == "BHSM_BARE_CANONICAL" else report["rule_status_after_audit"],
                },
            ]
        )
    return rows


def virtual_environment_report(model: Any, target_scale: float = MZ) -> dict[str, object]:
    """Return the complete virtual-environment dressing audit."""

    bare = _bare_ratios(model)
    linked_rule = pure_fiber_middle_up_rule()
    candidates = []
    for rule in virtual_dressing_candidates(model):
        variant = _variant(model, f"CANDIDATE_{rule.source}_{rule.applies_to}", (rule,), target_scale)
        ct = next(row for row in variant["comparisons"] if row["id"] == "mass_ratio.up_quarks.middle")
        ut = next(row for row in variant["comparisons"] if row["id"] == "mass_ratio.up_quarks.light")
        sb = next(row for row in variant["comparisons"] if row["id"] == "mass_ratio.down_quarks.middle")
        db = next(row for row in variant["comparisons"] if row["id"] == "mass_ratio.down_quarks.light")
        candidates.append(
            {
                "rule": asdict(rule),
                "c_over_t": ct,
                "u_over_t": ut,
                "s_over_b": sb,
                "d_over_b": db,
                "sin_theta_13": variant["ckm"]["sin_theta_13"],
                "adopted": False,
            }
        )
    bare_variant = {
        "name": "BHSM_BARE_CANONICAL",
        "rules": [],
        "ratios": bare,
        "comparisons": _comparison_rows(model, bare, target_scale),
        "ckm": {
            "sin_theta_13": sqrt(float(bare["up_quarks"]["light"])),
            "status": "CANONICAL_BARE",
        },
        "canonical": True,
    }
    dressed_variant = _variant(model, "BHSM_VIRTUAL_DRESSED_DIAGNOSTIC", (linked_rule,), target_scale)
    dressed_variant["canonical"] = False
    return {
        "formula": "(m_i/m_3)_observed_mu = Z_virt^{f,i}(mu) * (m_i/m_3)_BHSM_bare",
        "canonical_geometry": {
            "name": model.geometry_config.name,
            "a": model.geometry_config.a,
        },
        "target_scale": target_scale,
        "candidate_table": candidates,
        "model_variants": (bare_variant, dressed_variant),
        "linked_rule": asdict(linked_rule),
        "linkage_test": {
            "uses_empirical_residual": False,
            "mode": (6, 0),
            "j": 0,
            "q": hopf_charge(6, 0),
            "omega_u": omega_up(6, 0),
            "passes": linked_rule.status == VIRTUAL_ENV_LINKED,
        },
        "canonical_changed": False,
        "limitations": (
            "Virtual dressing is formalized as a diagnostic layer only.",
            "The 1/2 rule is not adopted canonically in this phase.",
            "Full loop/threshold derivation of virtual dressing remains open.",
        ),
    }


def _jsonable(value: object) -> object:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def export_virtual_environment_json(model: Any, path: str | Path) -> None:
    """Export the virtual-environment dressing audit as JSON."""

    Path(path).write_text(json.dumps(_jsonable(virtual_environment_report(model)), indent=2, sort_keys=True) + "\n")


def export_virtual_environment_markdown(model: Any, path: str | Path) -> None:
    """Export the virtual-environment dressing audit as Markdown."""

    report = virtual_environment_report(model)
    variants = {row["name"]: row for row in report["model_variants"]}
    bare = variants["BHSM_BARE_CANONICAL"]
    dressed = variants["BHSM_VIRTUAL_DRESSED_DIAGNOSTIC"]
    lines = [
        "# BHSM Virtual-Environment Dressing Audit",
        "",
        "This audit formalizes a diagnostic dressing layer. Canonical BHSM predictions are not changed.",
        "",
        f"Formula: `{report['formula']}`",
        "",
        "## Candidate Dressing Table",
        "",
        "| Source | Factor | Applies To | Status | c/t | u/t | s/b | d/b | sin(theta_13) | Adopted |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report["candidate_table"]:
        rule = row["rule"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                rule["source"],
                rule["factor"],
                rule["applies_to"],
                rule["status"],
                row["c_over_t"]["predicted"],
                row["u_over_t"]["predicted"],
                row["s_over_b"]["predicted"],
                row["d_over_b"]["predicted"],
                row["sin_theta_13"],
                row["adopted"],
            )
        )
    lines.extend([
        "",
        "## BARE vs VIRTUAL_DRESSED_DIAGNOSTIC",
        "",
        "| Variant | c/t | u/t | s/b | d/b | sin(theta_13) |",
        "| --- | --- | --- | --- | --- | --- |",
        "| `BHSM_BARE_CANONICAL` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
            bare["ratios"]["up_quarks"]["middle"],
            bare["ratios"]["up_quarks"]["light"],
            bare["ratios"]["down_quarks"]["middle"],
            bare["ratios"]["down_quarks"]["light"],
            bare["ckm"]["sin_theta_13"],
        ),
        "| `BHSM_VIRTUAL_DRESSED_DIAGNOSTIC` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
            dressed["ratios"]["up_quarks"]["middle"],
            dressed["ratios"]["up_quarks"]["light"],
            dressed["ratios"]["down_quarks"]["middle"],
            dressed["ratios"]["down_quarks"]["light"],
            dressed["ckm"]["sin_theta_13"],
        ),
        "",
        "## Linkage Test",
        "",
        "```json",
        json.dumps(_jsonable(report["linkage_test"]), indent=2, sort_keys=True),
        "```",
        "",
        "## Limitations",
        "",
    ])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.append("")
    Path(path).write_text("\n".join(lines))


def export_virtual_dressing_adoption_json(model: Any, rule: VirtualDressingRule, path: str | Path) -> None:
    """Export the Phase 30 adoption-gate audit as JSON."""

    Path(path).write_text(json.dumps(_jsonable(adoption_report(model, rule)), indent=2, sort_keys=True) + "\n")


def export_virtual_dressing_adoption_markdown(model: Any, rule: VirtualDressingRule, path: str | Path) -> None:
    """Export the Phase 30 adoption-gate audit as Markdown."""

    report = adoption_report(model, rule)
    lines = [
        "# BHSM Virtual-Dressed Adoption Criteria Audit",
        "",
        "This audit evaluates whether the virtual dressing rule qualifies as an adoption candidate. It does not mark the rule as canonically adopted.",
        "",
        f"Rule status after audit: `{report['rule_status_after_audit']}`",
        f"Adopted canonical dressed: `{report['adopted_canonical_dressed']}`",
        "",
        "## Adoption Criteria",
        "",
        "| ID | Statement | Passes | Evidence | Limitations |",
        "| --- | --- | --- | --- | --- |",
    ]
    for criterion in report["criteria"]:
        lines.append(
            "| `{}` | {} | `{}` | {} | {} |".format(
                criterion["id"],
                criterion["statement"],
                criterion["passes"],
                "<br>".join(criterion["evidence"]),
                "<br>".join(criterion["limitations"]),
            )
        )
    lines.extend([
        "",
        "## Bare vs Dressed Candidate",
        "",
        "| Variant | c/t | u/t | s/b | d/b | sin(theta_13) |",
        "| --- | --- | --- | --- | --- | --- |",
    ])
    for variant in report["model_variants"]:
        ratios = variant["ratios"]
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                variant["name"],
                ratios["up_quarks"]["middle"],
                ratios["up_quarks"]["light"],
                ratios["down_quarks"]["middle"],
                ratios["down_quarks"]["light"],
                variant["ckm"]["sin_theta_13"],
            )
        )
    lines.extend([
        "",
        f"Changed outputs: `{report['changed_outputs']}`",
        f"Unrelated sectors changed: `{report['unrelated_sectors_changed']}`",
        "",
        "## Limitations",
        "",
    ])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.append("")
    Path(path).write_text("\n".join(lines))


def export_bare_vs_dressed_prediction_ledger_json(model: Any, rule: VirtualDressingRule, path: str | Path) -> None:
    """Export the compact bare-vs-dressed prediction ledger as JSON."""

    Path(path).write_text(json.dumps(_jsonable(bare_vs_dressed_prediction_ledger(model, rule)), indent=2, sort_keys=True) + "\n")


def export_bare_vs_dressed_prediction_ledger_markdown(model: Any, rule: VirtualDressingRule, path: str | Path) -> None:
    """Export the compact bare-vs-dressed prediction ledger as Markdown."""

    rows = bare_vs_dressed_prediction_ledger(model, rule)
    lines = [
        "# BHSM Bare vs Dressed Prediction Ledger",
        "",
        "The dressed column is an adoption candidate output, not canonically adopted.",
        "",
        "| Variant | Sector | Quantity | Value | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| `{}` | {} | `{}` | `{}` | `{}` |".format(
                row["variant"],
                row["sector"],
                row["quantity"],
                row["value"],
                row["status"],
            )
        )
    lines.append("")
    Path(path).write_text("\n".join(lines))
