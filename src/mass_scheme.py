"""Mass-reference scheme audit for BHSM ratio comparisons.

This module structures the comparison inputs already present in the repository.
It does not run QCD, fetch external data, or tune BHSM parameters.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import log10
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class MassReference:
    """One empirical mass input with scheme and scale labels."""

    particle: str
    value: float
    unit: str
    scheme: str
    scale: str
    source_label: str
    uncertainty: float | None
    notes: tuple[str, ...]


@dataclass(frozen=True)
class MassRatioReference:
    """A ratio reference with scheme-consistency metadata."""

    numerator: str
    denominator: str
    ratio: float
    scheme: str
    scale: str
    scheme_consistent: bool
    notes: tuple[str, ...]


PARTICLE_FOR_RATIO = {
    ("charged_leptons", "middle"): ("mu", "tau"),
    ("charged_leptons", "light"): ("e", "tau"),
    ("up_quarks", "middle"): ("c", "t"),
    ("up_quarks", "light"): ("u", "t"),
    ("down_quarks", "middle"): ("s", "b"),
    ("down_quarks", "light"): ("d", "b"),
}


def _mixed_default_references() -> dict[str, MassReference]:
    return {
        "e": MassReference("e", 0.510998950, "MeV", "pole", "on-shell", "repo_current", None, ("Charged lepton reference; scheme-stable for this audit.",)),
        "mu": MassReference("mu", 105.6583755, "MeV", "pole", "on-shell", "repo_current", None, ("Charged lepton reference; scheme-stable for this audit.",)),
        "tau": MassReference("tau", 1776.86, "MeV", "pole", "on-shell", "repo_current", None, ("Charged lepton reference; scheme-stable for this audit.",)),
        "u": MassReference("u", 0.00216, "GeV", "MSbar_mixed", "2 GeV light-reference", "repo_current", None, ("Current repo value; not run to a common top scale.",)),
        "c": MassReference("c", 1.27, "GeV", "MSbar_mixed", "self-scale charm-reference", "repo_current", None, ("Current repo value; not run to a common top scale.",)),
        "t": MassReference("t", 172.69, "GeV", "mixed_top_reference", "top mass reference", "repo_current", None, ("Current repo value; mixed with light-quark references.",)),
        "d": MassReference("d", 0.00467, "GeV", "MSbar_mixed", "2 GeV light-reference", "repo_current", None, ("Current repo value; not run to a common bottom scale.",)),
        "s": MassReference("s", 0.0934, "GeV", "MSbar_mixed", "2 GeV strange-reference", "repo_current", None, ("Current repo value; not run to a common bottom scale.",)),
        "b": MassReference("b", 4.18, "GeV", "MSbar_mixed", "bottom self-scale reference", "repo_current", None, ("Current repo value; mixed with light-quark references.",)),
    }


def _common_scale_placeholder_references() -> dict[str, MassReference]:
    rows = {}
    for particle, ref in _mixed_default_references().items():
        rows[particle] = MassReference(
            particle=ref.particle,
            value=ref.value,
            unit=ref.unit,
            scheme="COMMON_SCALE_PLACEHOLDER",
            scale="OPEN_COMMON_SCALE_RUNNING_NOT_IMPLEMENTED",
            source_label="placeholder_reuses_repo_current_values",
            uncertainty=None,
            notes=(
                "Placeholder only; values are not QCD-run to a common scale.",
                "Do not interpret this as a completed common-scale mass scheme.",
            ),
        )
    return rows


def default_mass_references() -> dict[str, dict[str, MassReference]]:
    """Return available mass-reference schemes."""

    return {
        "MIXED_DEFAULT": _mixed_default_references(),
        "COMMON_SCALE_PLACEHOLDER": _common_scale_placeholder_references(),
    }


def is_scheme_consistent(ref_a: MassReference, ref_b: MassReference) -> bool:
    """Return whether two mass references are in a usable common scheme/scale."""

    if "PLACEHOLDER" in ref_a.scheme or "PLACEHOLDER" in ref_b.scheme:
        return False
    if "mixed" in ref_a.scheme.lower() or "mixed" in ref_b.scheme.lower():
        return False
    if ref_a.scheme != ref_b.scheme:
        return False
    if ref_a.scale != ref_b.scale:
        return False
    return True


def build_ratio_reference(
    numerator: str,
    denominator: str,
    references: Mapping[str, MassReference],
) -> MassRatioReference:
    """Build a mass-ratio reference from labeled mass inputs."""

    ref_num = references[numerator]
    ref_den = references[denominator]
    ratio = float(ref_num.value) / float(ref_den.value)
    consistent = is_scheme_consistent(ref_num, ref_den)
    scheme = ref_num.scheme if ref_num.scheme == ref_den.scheme else f"{ref_num.scheme}/{ref_den.scheme}"
    scale = ref_num.scale if ref_num.scale == ref_den.scale else f"{ref_num.scale}/{ref_den.scale}"
    notes = (
        *ref_num.notes,
        *ref_den.notes,
        "Scheme-consistent comparison." if consistent else "Scheme-sensitive comparison; common-scale running remains open.",
    )
    return MassRatioReference(
        numerator=numerator,
        denominator=denominator,
        ratio=ratio,
        scheme=scheme,
        scale=scale,
        scheme_consistent=consistent,
        notes=tuple(dict.fromkeys(notes)),
    )


def _ratio_references_for_scheme(scheme_set: str) -> dict[str, MassRatioReference]:
    references = default_mass_references()[scheme_set]
    rows: dict[str, MassRatioReference] = {}
    for (sector, rank), particles in PARTICLE_FOR_RATIO.items():
        rows[f"{sector}.{rank}"] = build_ratio_reference(particles[0], particles[1], references)
    return rows


def mass_scheme_report() -> dict[str, object]:
    """Return a table-ready mass scheme audit report."""

    schemes = default_mass_references()
    return {
        "schemes": {
            name: {particle: asdict(ref) for particle, ref in refs.items()}
            for name, refs in schemes.items()
        },
        "ratio_references": {
            name: {key: asdict(row) for key, row in _ratio_references_for_scheme(name).items()}
            for name in schemes
        },
        "limitations": (
            "No external mass data are fetched.",
            "COMMON_SCALE_PLACEHOLDER reuses current values and does not implement QCD running.",
            "Quark cross-generation comparisons remain scheme-sensitive until common-scale running is supplied.",
        ),
    }


def _relative_error(predicted: float, reference: float) -> float:
    return abs(float(predicted) - float(reference)) / abs(float(reference))


def _pull(predicted: float, reference: float, uncertainty: float | None) -> float | None:
    if uncertainty is None or uncertainty == 0:
        return None
    return (float(predicted) - float(reference)) / float(uncertainty)


def compare_bhsm_ratios_to_schemes(model: Any, scheme_set: str) -> list[dict[str, object]]:
    """Compare BHSM ratios to one labeled mass-reference scheme."""

    if scheme_set not in default_mass_references():
        raise ValueError(f"unknown mass scheme set: {scheme_set}")
    ratios = {
        sector: dict(yukawa.ratios)
        for sector, yukawa in model.yukawa_sectors.items()
    }
    ratio_refs = _ratio_references_for_scheme(scheme_set)
    rows: list[dict[str, object]] = []
    for key, ref in ratio_refs.items():
        sector, rank = key.split(".")
        predicted = float(ratios[sector][rank])
        uncertainty = None
        # Ratio uncertainty is intentionally left open unless input references
        # carry uncertainties in a future phase.
        rows.append(
            {
                "id": f"mass_ratio.{sector}.{rank}",
                "scheme_set": scheme_set,
                "predicted": predicted,
                "reference": ref.ratio,
                "relative_error": _relative_error(predicted, ref.ratio),
                "log_error": None if predicted <= 0 or ref.ratio <= 0 else log10(predicted / ref.ratio),
                "pull": _pull(predicted, ref.ratio, uncertainty),
                "scheme": ref.scheme,
                "scale": ref.scale,
                "scheme_consistent": ref.scheme_consistent,
                "scheme_sensitive": not ref.scheme_consistent and sector in {"up_quarks", "down_quarks"},
                "notes": ref.notes,
            }
        )
    return rows


def _jsonable(value: object) -> object:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def export_mass_scheme_report_json(path: str | Path) -> None:
    """Export the mass scheme audit as JSON."""

    Path(path).write_text(json.dumps(_jsonable(mass_scheme_report()), indent=2, sort_keys=True) + "\n")


def export_mass_scheme_report_markdown(path: str | Path) -> None:
    """Export the mass scheme audit as Markdown."""

    report = mass_scheme_report()
    lines = [
        "# BHSM Mass Scheme Audit",
        "",
        "This audit structures mass-reference comparisons. It does not run QCD, fetch external data, tune masses, or change BHSM predictions.",
        "",
        "## Ratio References",
        "",
        "| Scheme Set | Ratio | Reference | Scheme | Scale | Scheme Consistent | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for scheme_set, rows in report["ratio_references"].items():
        for key, row in rows.items():
            lines.append(
                "| {} | `{}` | `{}` | `{}` | `{}` | `{}` | {} |".format(
                    scheme_set,
                    key,
                    row["ratio"],
                    row["scheme"],
                    row["scale"],
                    row["scheme_consistent"],
                    "<br>".join(row["notes"]),
                )
            )
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.append("")
    Path(path).write_text("\n".join(lines))
