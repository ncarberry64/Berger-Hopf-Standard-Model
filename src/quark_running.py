"""Approximate common-scale quark mass running scaffold.

This module provides a transparent one-loop-inspired comparison pipeline. It
does not implement precision QCD matching, threshold corrections, or fitted
mass inputs, and it does not modify BHSM predictions.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import isfinite, log, log10, pi, sqrt
from pathlib import Path
from typing import Any, Iterable

from mass_scheme import MassReference, build_ratio_reference, default_mass_references
from mode_selection import admissible_modes, omega_up
from berger_spectrum import berger_lambda
from constants import ALPHA_INV_LOW_ENERGY, S_OVERLAP
from yukawa_overlap import mass_ratio


MZ = 91.1876
MT_LIKE_SCALE = 172.69
TEN_GEV = 10.0
TARGET_SCALES = (MZ, MT_LIKE_SCALE, TEN_GEV)
FIXED_NF_APPROX = "FIXED_NF_APPROX"
PIECEWISE_NF_APPROX = "PIECEWISE_NF_APPROX"
PLACEHOLDER_PRECISION_QCD = "PLACEHOLDER_PRECISION_QCD"
QUARK_REFERENCE_SCALES = {
    "u": 2.0,
    "d": 2.0,
    "s": 2.0,
    "c": 1.27,
    "b": 4.18,
    "t": 172.69,
}


@dataclass(frozen=True)
class RunningConfig:
    """Configuration for the approximate common-scale running scaffold."""

    target_scale: float
    alpha_s_mz: float = 0.1180
    mz: float = MZ
    loop_order: str = "one_loop_inspired"
    nf_policy: str = "fixed_nf_5_no_threshold_matching"
    status: str = "APPROXIMATE_RUNNING_SCAFFOLD"
    notes: tuple[str, ...] = (
        "Uses fixed-nf one-loop alpha_s and a mass anomalous-dimension-inspired exponent.",
        "No threshold matching, higher-loop QCD, or uncertainty propagation is implemented.",
    )
    mass_exponent_p: float = 12.0 / 23.0


@dataclass(frozen=True)
class QuarkThreshold:
    """One approximate active-flavor threshold."""

    particle: str
    mass: float
    scale: float
    active_nf_below: int
    active_nf_above: int


def _beta0(nf: int) -> float:
    return 11.0 - (2.0 * float(nf) / 3.0)


def default_thresholds() -> tuple[QuarkThreshold, ...]:
    """Return approximate c, b, t active-flavor thresholds."""

    return (
        QuarkThreshold("c", 1.27, 1.27, 3, 4),
        QuarkThreshold("b", 4.18, 4.18, 4, 5),
        QuarkThreshold("t", 172.69, 172.69, 5, 6),
    )


def nf_at_scale(mu: float, thresholds: Iterable[QuarkThreshold] | None = None) -> int:
    """Return the approximate active flavor count at a scale."""

    if mu <= 0:
        raise ValueError("scale must be positive")
    rows = sorted(tuple(thresholds or default_thresholds()), key=lambda item: item.scale)
    nf = rows[0].active_nf_below if rows else 5
    for threshold in rows:
        if mu >= threshold.scale:
            nf = threshold.active_nf_above
    return nf


def alpha_s_one_loop(mu: float, alpha_s_mz: float = 0.1180, mz: float = MZ, nf: int = 5) -> float:
    """Return fixed-nf one-loop alpha_s normalized at MZ."""

    if mu <= 0 or mz <= 0:
        raise ValueError("scales must be positive")
    denominator = 1.0 + (alpha_s_mz * _beta0(nf) / (2.0 * pi)) * log(float(mu) / float(mz))
    if denominator <= 0:
        raise ValueError("one-loop denominator is nonpositive at this scale")
    value = float(alpha_s_mz) / denominator
    if not isfinite(value) or value <= 0:
        raise ValueError("alpha_s_one_loop produced an invalid value")
    return value


def _segment_boundaries(mu_from: float, mu_to: float, thresholds: Iterable[QuarkThreshold]) -> list[float]:
    low = min(mu_from, mu_to)
    high = max(mu_from, mu_to)
    interior = [
        threshold.scale
        for threshold in thresholds
        if low < threshold.scale < high
    ]
    if mu_to >= mu_from:
        return [mu_from, *sorted(interior), mu_to]
    return [mu_from, *sorted(interior, reverse=True), mu_to]


def _evolve_alpha_piecewise(
    alpha_start: float,
    mu_from: float,
    mu_to: float,
    thresholds: Iterable[QuarkThreshold],
) -> float:
    alpha = float(alpha_start)
    points = _segment_boundaries(mu_from, mu_to, thresholds)
    for start, end in zip(points, points[1:]):
        if start == end:
            continue
        midpoint = sqrt(start * end)
        nf = nf_at_scale(midpoint, thresholds)
        inverse = (1.0 / alpha) + (_beta0(nf) / (2.0 * pi)) * log(end / start)
        if inverse <= 0:
            raise ValueError("piecewise alpha_s evolution produced nonpositive inverse coupling")
        alpha = 1.0 / inverse
    if not isfinite(alpha) or alpha <= 0:
        raise ValueError("piecewise alpha_s evolution produced invalid alpha_s")
    return float(alpha)


def alpha_s_piecewise_one_loop(
    mu: float,
    alpha_s_mz: float = 0.1180,
    mz: float = MZ,
    thresholds: Iterable[QuarkThreshold] | None = None,
) -> float:
    """Return threshold-aware one-loop alpha_s normalized at MZ."""

    if mu <= 0 or mz <= 0:
        raise ValueError("scales must be positive")
    rows = tuple(thresholds or default_thresholds())
    if mu == mz:
        return float(alpha_s_mz)
    return _evolve_alpha_piecewise(alpha_s_mz, mz, mu, rows)


def mass_running_factor_one_loop(
    mu_from: float,
    mu_to: float,
    alpha_s_mz: float = 0.1180,
    mz: float = MZ,
    nf: int = 5,
    p: float = 12.0 / 23.0,
) -> float:
    """Return approximate factor m(mu_to)/m(mu_from)."""

    if mu_from <= 0 or mu_to <= 0:
        raise ValueError("scales must be positive")
    if mu_from == mu_to:
        return 1.0
    alpha_from = alpha_s_one_loop(mu_from, alpha_s_mz=alpha_s_mz, mz=mz, nf=nf)
    alpha_to = alpha_s_one_loop(mu_to, alpha_s_mz=alpha_s_mz, mz=mz, nf=nf)
    return float((alpha_to / alpha_from) ** p)


def _mass_exponent_for_nf(nf: int) -> float:
    return 12.0 / (33.0 - 2.0 * float(nf))


def mass_running_piecewise(
    mu_from: float,
    mu_to: float,
    alpha_s_mz: float = 0.1180,
    mz: float = MZ,
    thresholds: Iterable[QuarkThreshold] | None = None,
    exponent_policy: str = PIECEWISE_NF_APPROX,
) -> float:
    """Return approximate threshold-aware mass-running factor."""

    if exponent_policy == PLACEHOLDER_PRECISION_QCD:
        raise NotImplementedError("precision QCD threshold matching is not implemented")
    if exponent_policy == FIXED_NF_APPROX:
        return mass_running_factor_one_loop(mu_from, mu_to, alpha_s_mz=alpha_s_mz, mz=mz, nf=5)
    if exponent_policy != PIECEWISE_NF_APPROX:
        raise ValueError(f"unknown exponent policy: {exponent_policy}")
    if mu_from <= 0 or mu_to <= 0:
        raise ValueError("scales must be positive")
    if mu_from == mu_to:
        return 1.0
    rows = tuple(thresholds or default_thresholds())
    factor = 1.0
    points = _segment_boundaries(mu_from, mu_to, rows)
    for start, end in zip(points, points[1:]):
        midpoint = sqrt(start * end)
        nf = nf_at_scale(midpoint, rows)
        alpha_start = alpha_s_piecewise_one_loop(start, alpha_s_mz=alpha_s_mz, mz=mz, thresholds=rows)
        alpha_end = alpha_s_piecewise_one_loop(end, alpha_s_mz=alpha_s_mz, mz=mz, thresholds=rows)
        factor *= (alpha_end / alpha_start) ** _mass_exponent_for_nf(nf)
    return float(factor)


def run_mass_piecewise(
    mass: float,
    mu_from: float,
    mu_to: float,
    alpha_s_mz: float = 0.1180,
    mz: float = MZ,
    thresholds: Iterable[QuarkThreshold] | None = None,
    exponent_policy: str = PIECEWISE_NF_APPROX,
) -> float:
    """Run a quark mass with the threshold-aware approximate scaffold."""

    return float(mass) * mass_running_piecewise(
        mu_from,
        mu_to,
        alpha_s_mz=alpha_s_mz,
        mz=mz,
        thresholds=thresholds,
        exponent_policy=exponent_policy,
    )


def run_mass_one_loop(
    mass: float,
    mu_from: float,
    mu_to: float,
    alpha_s_mz: float = 0.1180,
    mz: float = MZ,
    nf: int = 5,
    p: float = 12.0 / 23.0,
) -> float:
    """Run a quark mass with the approximate scaffold factor."""

    return float(mass) * mass_running_factor_one_loop(
        mu_from,
        mu_to,
        alpha_s_mz=alpha_s_mz,
        mz=mz,
        nf=nf,
        p=p,
    )


def _running_config(target_scale: float) -> RunningConfig:
    return RunningConfig(target_scale=float(target_scale))


def build_common_scale_references(target_scale: float) -> dict[str, MassReference]:
    """Return approximate common-scale quark references plus unchanged leptons."""

    config = _running_config(target_scale)
    mixed = default_mass_references()["MIXED_DEFAULT"]
    rows: dict[str, MassReference] = {}
    for particle, ref in mixed.items():
        if particle in QUARK_REFERENCE_SCALES:
            mu_from = QUARK_REFERENCE_SCALES[particle]
            value = run_mass_one_loop(
                ref.value,
                mu_from,
                config.target_scale,
                alpha_s_mz=config.alpha_s_mz,
                mz=config.mz,
                nf=5,
                p=config.mass_exponent_p,
            )
            rows[particle] = MassReference(
                particle=particle,
                value=value,
                unit=ref.unit,
                scheme="COMMON_SCALE_APPROX",
                scale=f"{config.target_scale:g} GeV",
                source_label="approx_one_loop_running_from_repo_current",
                uncertainty=None,
                notes=(
                    f"APPROXIMATE_RUNNING_SCAFFOLD with p={config.mass_exponent_p}.",
                    "No threshold matching or higher-loop QCD is implemented.",
                ),
            )
        else:
            rows[particle] = ref
    return rows


def build_threshold_common_scale_references(
    target_scale: float,
    thresholds: Iterable[QuarkThreshold] | None = None,
    exponent_policy: str = PIECEWISE_NF_APPROX,
    top_reference_variant: str = "CURRENT_AMBIGUOUS_TOP",
) -> dict[str, MassReference]:
    """Return threshold-aware common-scale quark references.

    Top-reference variants are labels only in this phase; all reuse the current
    repo value to avoid inventing precision running masses.
    """

    if top_reference_variant not in {"CURRENT_AMBIGUOUS_TOP", "TOP_POLE_LIKE_CURRENT", "TOP_RUNNING_MASS_PLACEHOLDER"}:
        raise ValueError(f"unknown top reference variant: {top_reference_variant}")
    if exponent_policy == PLACEHOLDER_PRECISION_QCD:
        raise NotImplementedError("precision QCD threshold matching is not implemented")
    mixed = default_mass_references()["MIXED_DEFAULT"]
    rows: dict[str, MassReference] = {}
    for particle, ref in mixed.items():
        if particle in QUARK_REFERENCE_SCALES:
            value = run_mass_piecewise(
                ref.value,
                QUARK_REFERENCE_SCALES[particle],
                target_scale,
                thresholds=thresholds,
                exponent_policy=exponent_policy,
            )
            source_label = "threshold_piecewise_running_from_repo_current"
            notes = [
                f"{exponent_policy}; approximate threshold-aware scaffold.",
                "No precision QCD matching, higher-loop running, or uncertainty propagation is implemented.",
            ]
            if particle == "t":
                notes.append(f"Top reference variant `{top_reference_variant}` reuses the current repo value as sensitivity labeling only.")
            rows[particle] = MassReference(
                particle=particle,
                value=value,
                unit=ref.unit,
                scheme="COMMON_SCALE_THRESHOLD_APPROX",
                scale=f"{float(target_scale):g} GeV",
                source_label=source_label,
                uncertainty=None,
                notes=tuple(notes),
            )
        else:
            rows[particle] = ref
    return rows


def _relative_error(predicted: float, reference: float) -> float:
    return abs(float(predicted) - float(reference)) / abs(float(reference))


def compare_bhsm_to_common_scale(model: Any, target_scale: float) -> list[dict[str, object]]:
    """Compare BHSM quark ratios to approximate common-scale references."""

    references = build_common_scale_references(target_scale)
    ratios = {sector: dict(yukawa.ratios) for sector, yukawa in model.yukawa_sectors.items()}
    pairs = {
        "mass_ratio.up_quarks.middle": ("up_quarks", "middle", "c", "t"),
        "mass_ratio.up_quarks.light": ("up_quarks", "light", "u", "t"),
        "mass_ratio.down_quarks.middle": ("down_quarks", "middle", "s", "b"),
        "mass_ratio.down_quarks.light": ("down_quarks", "light", "d", "b"),
    }
    rows: list[dict[str, object]] = []
    for row_id, (sector, rank, numerator, denominator) in pairs.items():
        ref = build_ratio_reference(numerator, denominator, references)
        predicted = float(ratios[sector][rank])
        rows.append(
            {
                "id": row_id,
                "target_scale": float(target_scale),
                "predicted": predicted,
                "reference": ref.ratio,
                "relative_error": _relative_error(predicted, ref.ratio),
                "log_error": None if predicted <= 0 or ref.ratio <= 0 else log10(predicted / ref.ratio),
                "scheme": ref.scheme,
                "scale": ref.scale,
                "scheme_consistent": ref.scheme_consistent,
                "status": "APPROXIMATE_RUNNING_SCAFFOLD",
                "notes": ref.notes,
            }
        )
    return rows


def _quark_ratio_pairs() -> dict[str, tuple[str, str, str, str]]:
    return {
        "mass_ratio.up_quarks.middle": ("up_quarks", "middle", "c", "t"),
        "mass_ratio.up_quarks.light": ("up_quarks", "light", "u", "t"),
        "mass_ratio.down_quarks.middle": ("down_quarks", "middle", "s", "b"),
        "mass_ratio.down_quarks.light": ("down_quarks", "light", "d", "b"),
    }


def compare_bhsm_to_threshold_common_scale(
    model: Any,
    target_scale: float,
    exponent_policy: str = PIECEWISE_NF_APPROX,
    top_reference_variant: str = "CURRENT_AMBIGUOUS_TOP",
) -> list[dict[str, object]]:
    """Compare BHSM quark ratios to threshold-aware approximate references."""

    references = build_threshold_common_scale_references(
        target_scale,
        exponent_policy=exponent_policy,
        top_reference_variant=top_reference_variant,
    )
    ratios = {sector: dict(yukawa.ratios) for sector, yukawa in model.yukawa_sectors.items()}
    rows = []
    for row_id, (sector, rank, numerator, denominator) in _quark_ratio_pairs().items():
        ref = build_ratio_reference(numerator, denominator, references)
        predicted = float(ratios[sector][rank])
        rows.append(
            {
                "id": row_id,
                "target_scale": float(target_scale),
                "predicted": predicted,
                "reference": ref.ratio,
                "relative_error": _relative_error(predicted, ref.ratio),
                "log_error": None if predicted <= 0 or ref.ratio <= 0 else log10(predicted / ref.ratio),
                "scheme": ref.scheme,
                "scale": ref.scale,
                "scheme_consistent": ref.scheme_consistent,
                "status": "THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD",
                "exponent_policy": exponent_policy,
                "top_reference_variant": top_reference_variant,
                "notes": ref.notes,
            }
        )
    return rows


def top_reference_audit(model: Any, target_scale: float = MZ) -> list[dict[str, object]]:
    """Return top-reference labeling sensitivity for c/t and u/t."""

    rows = []
    for variant in ("CURRENT_AMBIGUOUS_TOP", "TOP_POLE_LIKE_CURRENT", "TOP_RUNNING_MASS_PLACEHOLDER"):
        comparisons = compare_bhsm_to_threshold_common_scale(
            model,
            target_scale,
            exponent_policy=PIECEWISE_NF_APPROX,
            top_reference_variant=variant,
        )
        for row in comparisons:
            if row["id"] in {"mass_ratio.up_quarks.middle", "mass_ratio.up_quarks.light"}:
                rows.append({
                    **row,
                    "sensitivity_only": True,
                    "variant_note": "Variant changes labels only and reuses current top value; no precise top running mass is invented.",
                })
    return rows


def charm_mode_diagnostic(model: Any, k_max: int = 40, target_scale: float = MZ) -> dict[str, object]:
    """Diagnose the charm-mode residual without changing the up-sector ledger."""

    config = model.geometry_config
    ratios = {sector: dict(yukawa.ratios) for sector, yukawa in model.yukawa_sectors.items()}
    threshold_rows = compare_bhsm_to_threshold_common_scale(model, target_scale)
    threshold_ref = next(row for row in threshold_rows if row["id"] == "mass_ratio.up_quarks.middle")
    mixed_ref = 1.27 / 172.69
    current_mode = (6, 0)
    modes = admissible_modes("up", k_max)
    current_index = modes.index(current_mode)
    next_mode = modes[current_index + 1]
    next_suppression = mass_ratio(*next_mode, a=config.a)
    current_prediction = ratios["up_quarks"]["middle"]
    required_factor_threshold = threshold_ref["reference"] / current_prediction
    required_factor_mixed = mixed_ref / current_prediction
    alpha = 1.0 / ALPHA_INV_LOW_ENERGY
    candidates = {
        "1/sqrt(2)": 1.0 / sqrt(2.0),
        "1/2": 0.5,
        "1/sqrt(3)": 1.0 / sqrt(3.0),
        "1/3": 1.0 / 3.0,
        "sqrt(alpha)": sqrt(alpha),
        "2*sqrt(alpha)": 2.0 * sqrt(alpha),
    }
    candidate_rows = [
        {
            "candidate": name,
            "value": value,
            "distance_to_threshold_factor": abs(value - required_factor_threshold),
            "diagnostic_only": True,
        }
        for name, value in candidates.items()
    ]
    candidate_rows.sort(key=lambda row: row["distance_to_threshold_factor"])
    if next_suppression < threshold_ref["reference"]:
        next_assessment = "overcorrects"
    elif next_suppression > threshold_ref["reference"]:
        next_assessment = "undercorrects"
    else:
        next_assessment = "matches"
    return {
        "current_charm_mode": {
            "mode": current_mode,
            "q": current_mode[0] - 2 * current_mode[1],
            "omega_u": omega_up(*current_mode),
            "lambda": berger_lambda(*current_mode, a=config.a),
            "prediction": current_prediction,
        },
        "next_admissible_mode": {
            "mode": next_mode,
            "lambda": berger_lambda(*next_mode, a=config.a),
            "suppression": next_suppression,
            "assessment_vs_threshold_reference": next_assessment,
        },
        "first_five_admissible_modes": [
            {
                "mode": mode,
                "lambda": berger_lambda(*mode, a=config.a),
                "suppression": mass_ratio(*mode, a=config.a),
            }
            for mode in modes[:5]
        ],
        "references": {
            "mixed_default_c_over_t": mixed_ref,
            "threshold_common_scale_c_over_t": threshold_ref["reference"],
        },
        "required_normalization_factor": {
            "mixed_default": required_factor_mixed,
            "threshold_common_scale": required_factor_threshold,
        },
        "simple_factor_diagnostic": candidate_rows,
        "ledger_changed": False,
        "adopted_factor": None,
    }


def charm_top_tension_report(model: Any, target_scale: float = MZ) -> dict[str, object]:
    """Return a localized diagnostic report for the c/t tension."""

    fixed = compare_bhsm_to_common_scale(model, target_scale)
    piecewise = compare_bhsm_to_threshold_common_scale(model, target_scale)
    fixed_ct = next(row for row in fixed if row["id"] == "mass_ratio.up_quarks.middle")
    piecewise_ct = next(row for row in piecewise if row["id"] == "mass_ratio.up_quarks.middle")
    mode = charm_mode_diagnostic(model, target_scale=target_scale)
    likely = (
        "The c/t tension is not removed by the approximate threshold-aware scaffold. "
        "It remains localized to the charm/up-sector comparison and may reflect "
        "top/charm reference ambiguity, missing precision threshold matching, a "
        "missing representation normalization, or a genuine BHSM charm-mode tension."
    )
    return {
        "canonical_geometry": {
            "name": model.geometry_config.name,
            "a": model.geometry_config.a,
        },
        "target_scale": target_scale,
        "fixed_nf": fixed,
        "piecewise_nf": piecewise,
        "ct_summary": {
            "fixed_nf_reference": fixed_ct["reference"],
            "fixed_nf_relative_error": fixed_ct["relative_error"],
            "piecewise_nf_reference": piecewise_ct["reference"],
            "piecewise_nf_relative_error": piecewise_ct["relative_error"],
        },
        "top_reference_audit": top_reference_audit(model, target_scale),
        "charm_mode_diagnostic": mode,
        "likely_root_cause_classification": {
            "approximate_running_scaffold_issue": True,
            "top_charm_reference_inconsistency": True,
            "missing_threshold_matching": True,
            "missing_up_sector_representation_normalization": "diagnostic_only",
            "genuine_bhsm_charm_mode_tension": "possible",
            "summary": likely,
        },
        "model_changed": False,
        "limitations": (
            "Diagnostic only; no BHSM parameter, geometry, S, mode ledger, or normalization factor is changed.",
            "Top running-mass-like variant is a label-only placeholder reusing current values.",
            "Piecewise running remains approximate and is not precision QCD.",
        ),
    }


def quark_running_report(model: Any, target_scales: Iterable[float] = TARGET_SCALES) -> dict[str, object]:
    """Return common-scale running audit tables."""

    targets = tuple(float(scale) for scale in target_scales)
    return {
        "configs": [asdict(_running_config(scale)) for scale in targets],
        "alpha_s": {
            str(scale): alpha_s_one_loop(scale)
            for scale in targets
        },
        "common_scale_references": {
            str(scale): {
                particle: asdict(ref)
                for particle, ref in build_common_scale_references(scale).items()
                if particle in QUARK_REFERENCE_SCALES
            }
            for scale in targets
        },
        "comparisons": {
            str(scale): compare_bhsm_to_common_scale(model, scale)
            for scale in targets
        },
        "threshold_aware_comparisons": {
            str(scale): compare_bhsm_to_threshold_common_scale(model, scale)
            for scale in targets
        },
        "limitations": (
            "Approximate one-loop-inspired scaffold only.",
            "No threshold matching, higher-loop running, or precision mass-scheme treatment is implemented.",
            "BHSM predictions and canonical geometry are unchanged.",
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


def export_quark_running_report_json(model: Any, path: str | Path, target_scales: Iterable[float] = TARGET_SCALES) -> None:
    """Export the quark running audit as JSON."""

    Path(path).write_text(json.dumps(_jsonable(quark_running_report(model, target_scales)), indent=2, sort_keys=True) + "\n")


def export_quark_running_report_markdown(model: Any, path: str | Path, target_scales: Iterable[float] = TARGET_SCALES) -> None:
    """Export the quark running audit as Markdown."""

    report = quark_running_report(model, target_scales)
    lines = [
        "# BHSM Quark Running Audit",
        "",
        "This is an APPROXIMATE_RUNNING_SCAFFOLD. It does not tune BHSM parameters or claim precision QCD matching.",
        "",
        "## Common-Scale Comparisons",
        "",
        "| Target Scale | Ratio | BHSM | Reference | Relative Error | Scheme | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for scale, rows in report["comparisons"].items():
        for row in rows:
            lines.append(
                "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                    scale,
                    row["id"],
                    row["predicted"],
                    row["reference"],
                    row["relative_error"],
                    row["scheme"],
                    row["status"],
                )
            )
    lines.extend([
        "",
        "## Threshold-Aware Approximate Comparisons",
        "",
        "| Target Scale | Ratio | BHSM | Reference | Relative Error | Scheme | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ])
    for scale, rows in report["threshold_aware_comparisons"].items():
        for row in rows:
            lines.append(
                "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
                    scale,
                    row["id"],
                    row["predicted"],
                    row["reference"],
                    row["relative_error"],
                    row["scheme"],
                    row["status"],
                )
            )
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.append("")
    Path(path).write_text("\n".join(lines))


def common_scale_residual_markdown_section(model: Any, target_scales: Iterable[float] = TARGET_SCALES) -> str:
    """Return a Markdown section suitable for appending to residual audits."""

    report = quark_running_report(model, target_scales)
    lines = [
        "",
        "## COMMON_SCALE_APPROX Residual Section",
        "",
        "These rows are separate approximate-running comparisons and do not replace the MIXED_DEFAULT residual audit.",
        "",
        "| Target Scale | Ratio | BHSM | Common-Scale Approx Reference | Relative Error | Status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for scale, rows in report["comparisons"].items():
        for row in rows:
            lines.append(
                f"| `{scale}` | `{row['id']}` | `{row['predicted']}` | `{row['reference']}` | `{row['relative_error']}` | `{row['status']}` |"
            )
    lines.append("")
    return "\n".join(lines)


def threshold_residual_markdown_section(model: Any, target_scales: Iterable[float] = TARGET_SCALES) -> str:
    """Return a Markdown section for threshold-aware residual audit rows."""

    report = quark_running_report(model, target_scales)
    lines = [
        "",
        "## THRESHOLD_AWARE_COMMON_SCALE Residual Section",
        "",
        "These rows are diagnostic approximate threshold-aware comparisons and do not replace the MIXED_DEFAULT audit.",
        "",
        "| Target Scale | Ratio | BHSM | Threshold-Aware Reference | Relative Error | Status |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for scale, rows in report["threshold_aware_comparisons"].items():
        for row in rows:
            lines.append(
                f"| `{scale}` | `{row['id']}` | `{row['predicted']}` | `{row['reference']}` | `{row['relative_error']}` | `{row['status']}` |"
            )
    lines.append("")
    return "\n".join(lines)


def export_charm_top_tension_report_json(model: Any, path: str | Path, target_scale: float = MZ) -> None:
    """Export the charm/top tension audit as JSON."""

    Path(path).write_text(json.dumps(_jsonable(charm_top_tension_report(model, target_scale)), indent=2, sort_keys=True) + "\n")


def export_charm_top_tension_report_markdown(model: Any, path: str | Path, target_scale: float = MZ) -> None:
    """Export the charm/top tension audit as Markdown."""

    report = charm_top_tension_report(model, target_scale)
    mode = report["charm_mode_diagnostic"]
    lines = [
        "# BHSM Charm/Top Tension Audit",
        "",
        "This diagnostic does not tune BHSM parameters, geometry, S, or the mode ledger.",
        "",
        "## c/t Running Comparison",
        "",
        f"- Fixed-nf c/t reference: `{report['ct_summary']['fixed_nf_reference']}`",
        f"- Fixed-nf relative error: `{report['ct_summary']['fixed_nf_relative_error']}`",
        f"- Piecewise-nf c/t reference: `{report['ct_summary']['piecewise_nf_reference']}`",
        f"- Piecewise-nf relative error: `{report['ct_summary']['piecewise_nf_relative_error']}`",
        "",
        "## Charm Mode Diagnostic",
        "",
        f"- Current charm mode: `{tuple(mode['current_charm_mode']['mode'])}`",
        f"- Current lambda: `{mode['current_charm_mode']['lambda']}`",
        f"- Next admissible mode: `{tuple(mode['next_admissible_mode']['mode'])}`",
        f"- Next-mode assessment: `{mode['next_admissible_mode']['assessment_vs_threshold_reference']}`",
        "",
        "## Simple Normalization Factor Diagnostic",
        "",
        "| Candidate | Value | Distance to threshold factor | Adopted |",
        "| --- | --- | --- | --- |",
    ]
    for row in mode["simple_factor_diagnostic"]:
        lines.append(
            f"| `{row['candidate']}` | `{row['value']}` | `{row['distance_to_threshold_factor']}` | `False` |"
        )
    lines.extend([
        "",
        "## Likely Root Cause Classification",
        "",
        report["likely_root_cause_classification"]["summary"],
        "",
        "## Limitations",
        "",
    ])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.append("")
    Path(path).write_text("\n".join(lines))
