"""Precision-oriented QCD input architecture for BHSM v1.4.

No external data are fetched here. Current repository mass values are reused
with explicit scheme/source labels, and precision rows remain placeholders
until validated QCD inputs are supplied.
"""

from __future__ import annotations

from dataclasses import dataclass

from mass_scheme import default_mass_references
from quark_running import MZ


MIXED_DEFAULT = "MIXED_DEFAULT"
COMMON_SCALE_APPROX = "COMMON_SCALE_APPROX"
THRESHOLD_AWARE_APPROX = "THRESHOLD_AWARE_APPROX"
PDG_STYLE_REFERENCE_PLACEHOLDER = "PDG_STYLE_REFERENCE_PLACEHOLDER"
PRECISION_QCD_PLACEHOLDER = "PRECISION_QCD_PLACEHOLDER"


@dataclass(frozen=True)
class QuarkMassInput:
    """One quark mass input with comparison metadata."""

    particle: str
    value: float | None
    unit: str
    scheme: str
    scale_gev: float | None
    uncertainty: float | None
    source_label: str
    scheme_consistent: bool
    final: bool
    placeholder: bool
    notes: tuple[str, ...]


@dataclass(frozen=True)
class QCDReferenceSet:
    """Labeled quark-mass reference set."""

    name: str
    status: str
    inputs: tuple[QuarkMassInput, ...]
    target_scale_gev: float | None
    scheme_consistent: bool
    final: bool
    approximate: bool
    placeholder: bool
    notes: tuple[str, ...]


def _scale_from_text(particle: str) -> float:
    return {"u": 2.0, "d": 2.0, "s": 2.0, "c": 1.27, "b": 4.18, "t": 172.69}[particle]


def mixed_default_inputs() -> tuple[QuarkMassInput, ...]:
    """Return current repo quark inputs with mixed-scheme labels."""

    refs = default_mass_references()["MIXED_DEFAULT"]
    rows = []
    for particle in ("u", "c", "t", "d", "s", "b"):
        ref = refs[particle]
        rows.append(
            QuarkMassInput(
                particle=particle,
                value=float(ref.value),
                unit=ref.unit,
                scheme=ref.scheme,
                scale_gev=_scale_from_text(particle),
                uncertainty=ref.uncertainty,
                source_label=ref.source_label,
                scheme_consistent=False,
                final=False,
                placeholder=False,
                notes=tuple(ref.notes),
            )
        )
    return tuple(rows)


def common_scale_inputs(target_scale_gev: float = MZ, threshold_aware: bool = False) -> tuple[QuarkMassInput, ...]:
    """Return placeholder shells for running-produced inputs.

    Values are intentionally left ``None`` here. The matching module fills the
    values using the running scaffold so source data and running output remain
    separable.
    """

    scheme = "COMMON_SCALE_THRESHOLD_APPROX" if threshold_aware else "COMMON_SCALE_APPROX"
    source = "threshold_aware_running_scaffold" if threshold_aware else "one_loop_running_scaffold"
    return tuple(
        QuarkMassInput(
            particle=particle,
            value=None,
            unit="GeV",
            scheme=scheme,
            scale_gev=float(target_scale_gev),
            uncertainty=None,
            source_label=source,
            scheme_consistent=True,
            final=False,
            placeholder=False,
            notes=(
                "Approximate running output; not precision QCD.",
                "Uncertainty propagation is scaffolded but no input uncertainties are supplied.",
            ),
        )
        for particle in ("u", "c", "t", "d", "s", "b")
    )


def pdg_style_placeholder_inputs(target_scale_gev: float = MZ) -> tuple[QuarkMassInput, ...]:
    """Return explicit PDG-style placeholder rows without invented values."""

    return tuple(
        QuarkMassInput(
            particle=particle,
            value=None,
            unit="GeV",
            scheme=PDG_STYLE_REFERENCE_PLACEHOLDER,
            scale_gev=float(target_scale_gev),
            uncertainty=None,
            source_label="PDG_STYLE_REFERENCE_PLACEHOLDER",
            scheme_consistent=False,
            final=False,
            placeholder=True,
            notes=("Placeholder for future verified PDG-style common-scheme inputs.",),
        )
        for particle in ("u", "c", "t", "d", "s", "b")
    )


def precision_qcd_placeholder_inputs(target_scale_gev: float = MZ) -> tuple[QuarkMassInput, ...]:
    """Return explicit precision-QCD placeholder rows without invented values."""

    return tuple(
        QuarkMassInput(
            particle=particle,
            value=None,
            unit="GeV",
            scheme=PRECISION_QCD_PLACEHOLDER,
            scale_gev=float(target_scale_gev),
            uncertainty=None,
            source_label="PRECISION_QCD_PLACEHOLDER",
            scheme_consistent=False,
            final=False,
            placeholder=True,
            notes=("Placeholder for future validated two-/three-loop threshold-matched QCD inputs.",),
        )
        for particle in ("u", "c", "t", "d", "s", "b")
    )


def qcd_reference_sets(target_scale_gev: float = MZ) -> tuple[QCDReferenceSet, ...]:
    """Return all precision-oriented BHSM v1.4 reference sets."""

    return (
        QCDReferenceSet(
            name=MIXED_DEFAULT,
            status="SCHEME_SENSITIVE_BASELINE",
            inputs=mixed_default_inputs(),
            target_scale_gev=None,
            scheme_consistent=False,
            final=False,
            approximate=False,
            placeholder=False,
            notes=("Current mixed repository values; not final scheme-consistent QCD.",),
        ),
        QCDReferenceSet(
            name=COMMON_SCALE_APPROX,
            status="ONE_LOOP_APPROXIMATE_SCAFFOLD",
            inputs=common_scale_inputs(target_scale_gev, threshold_aware=False),
            target_scale_gev=float(target_scale_gev),
            scheme_consistent=True,
            final=False,
            approximate=True,
            placeholder=False,
            notes=("One-loop-inspired common-scale running scaffold.",),
        ),
        QCDReferenceSet(
            name=THRESHOLD_AWARE_APPROX,
            status="THRESHOLD_AWARE_APPROXIMATE_SCAFFOLD",
            inputs=common_scale_inputs(target_scale_gev, threshold_aware=True),
            target_scale_gev=float(target_scale_gev),
            scheme_consistent=True,
            final=False,
            approximate=True,
            placeholder=False,
            notes=("Piecewise threshold-aware running scaffold.",),
        ),
        QCDReferenceSet(
            name=PDG_STYLE_REFERENCE_PLACEHOLDER,
            status="PLACEHOLDER_NOT_COMPUTED",
            inputs=pdg_style_placeholder_inputs(target_scale_gev),
            target_scale_gev=float(target_scale_gev),
            scheme_consistent=False,
            final=False,
            approximate=False,
            placeholder=True,
            notes=("Metadata shell only; no PDG values are invented.",),
        ),
        QCDReferenceSet(
            name=PRECISION_QCD_PLACEHOLDER,
            status="PLACEHOLDER_NOT_COMPUTED",
            inputs=precision_qcd_placeholder_inputs(target_scale_gev),
            target_scale_gev=float(target_scale_gev),
            scheme_consistent=False,
            final=False,
            approximate=False,
            placeholder=True,
            notes=("Metadata shell only; precision QCD remains open.",),
        ),
    )
