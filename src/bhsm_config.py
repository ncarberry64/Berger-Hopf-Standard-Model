"""BHSM geometry configuration audit.

The canonical choice is selected by theory configuration, not by residual
minimization. Round and legacy-low-a cases remain available controls.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import pi
from typing import Callable, Iterable

from constants import ALPHA_INV_LOW_ENERGY

BHSM_USES_ALPHA_HOPF_RESIDUAL = True


@dataclass(frozen=True)
class GeometryConfig:
    """Berger anisotropy configuration record."""

    name: str
    a: float
    source: str
    status: str
    notes: tuple[str, ...]


def round_geometry_config() -> GeometryConfig:
    """Return the round Berger baseline control."""

    return GeometryConfig(
        name="ROUND",
        a=1.0,
        source="round Berger baseline",
        status="BASELINE_CONTROL",
        notes=("Kept as a control geometry; not selected by residual minimization.",),
    )


def legacy_low_a_config() -> GeometryConfig:
    """Return the legacy low-a sensitivity configuration."""

    return GeometryConfig(
        name="LEGACY_LOW_A",
        a=0.573,
        source="legacy sensitivity value",
        status="LEGACY_SENSITIVITY",
        notes=("Retained for sensitivity scans only.",),
    )


def alpha_anchored_geometry_config() -> GeometryConfig:
    """Return the alpha-anchored Berger geometry candidate."""

    value = ALPHA_INV_LOW_ENERGY / (12.0 * pi**2)
    return GeometryConfig(
        name="ALPHA_ANCHORED",
        a=value,
        source="alpha^{-1}/(12*pi^2) Hopf/electroweak residual",
        status="CANONICAL_CANDIDATE",
        notes=(
            "Selected as canonical only when BHSM assumptions include epsilon_alpha = alpha^{-1}/(12*pi^2) - 1.",
            "This selection rule does not inspect empirical mass or CKM residuals.",
        ),
    )


def available_geometry_configs() -> tuple[GeometryConfig, ...]:
    """Return all audited geometry configurations."""

    return (
        round_geometry_config(),
        legacy_low_a_config(),
        alpha_anchored_geometry_config(),
    )


def canonical_geometry_config() -> GeometryConfig:
    """Return the model-level canonical geometry by theory rule."""

    if BHSM_USES_ALPHA_HOPF_RESIDUAL:
        config = alpha_anchored_geometry_config()
        return GeometryConfig(
            name=config.name,
            a=config.a,
            source=config.source,
            status="CANONICAL",
            notes=config.notes
            + (
                "Adopted because the BHSM scale sector contains epsilon_alpha = alpha^{-1}/(12*pi^2) - 1.",
                "Not chosen by fitting residuals.",
            ),
        )
    config = round_geometry_config()
    return GeometryConfig(
        name=config.name,
        a=config.a,
        source=config.source,
        status="CANONICAL",
        notes=config.notes + ("Alpha-anchored geometry remains a candidate only.",),
    )


def compare_geometry_configs(
    model_factory: Callable[..., object],
    configs: Iterable[GeometryConfig],
) -> list[dict[str, object]]:
    """Compare full BHSM ledger outputs across geometry configs."""

    from bhsm_model import compute_ckm_from_internal_rules, compute_geometric_couplings, compute_higgs_sector, compute_pmns_from_internal_rules, compute_yukawa_ratios
    from prediction_ledger import build_prediction_ledger
    from residual_audit import build_residual_audit, sector_residual_summary, worst_residuals

    rows: list[dict[str, object]] = []
    for config in configs:
        model = model_factory(geometry_config=config)
        ratios = compute_yukawa_ratios(model)
        ckm = compute_ckm_from_internal_rules(model)
        pmns = compute_pmns_from_internal_rules(model)
        couplings = compute_geometric_couplings(model)
        higgs = compute_higgs_sector(model)
        ledger = build_prediction_ledger(model)
        audit = build_residual_audit(ledger)
        sector_summary = sector_residual_summary(audit)
        worst = worst_residuals(audit, n=5)
        rows.append(
            {
                "geometry": asdict(config),
                "charged_fermion_mass_ratios": ratios,
                "ckm_angles": ckm["angles"],
                "ckm_status": ckm["status"],
                "pmns_effective": pmns["angles"],
                "pmns_status": pmns["status"],
                "gauge_couplings": couplings["values"],
                "higgs_electroweak": higgs["outputs"],
                "residual_summary": sector_summary,
                "worst_residuals": [
                    {
                        "prediction_id": row.prediction_id,
                        "relative_error": row.relative_error,
                        "log_error": row.log_error,
                        "severity": row.severity,
                    }
                    for row in worst
                ],
                "up_sector": {
                    "c_over_t": ratios["up_quarks"]["middle"],
                    "u_over_t": ratios["up_quarks"]["light"],
                    "sin_theta_13": ckm["angles"]["sin_theta_13"],
                },
                "selection_basis": "theory_config_not_empirical_residuals",
            }
        )
    return rows
