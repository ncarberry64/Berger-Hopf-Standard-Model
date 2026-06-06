"""Table-driven BHSM model-output ledger.

The word "prediction" here means an executable model output or screen. Each
row carries its own status and limitation; proxy/scaffold rows are not final
confirmed predictions.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from math import isfinite
from pathlib import Path
from typing import Any, Iterable

import numpy as np

from bhsm_model import (
    BHSMModel,
    compute_ckm_from_internal_rules,
    compute_geometric_couplings,
    compute_higgs_sector,
    compute_ht_gap_status,
    compute_pmns_from_internal_rules,
    compute_scalar_decoupling_status,
    compute_yukawa_ratios,
)
from constants import (
    ALPHA3_MZ_EMPIRICAL,
    ALPHA_EM_INV_EW_EMPIRICAL,
    SIN2_THETA_W_EMPIRICAL,
    V_HIGGS_EMPIRICAL_GEV,
)
from mass_scheme import PARTICLE_FOR_RATIO, build_ratio_reference, default_mass_references
from spectral_gap import MU_H


CKM_REFERENCES = {
    "sin_theta_12": 0.22497,
    "sin_theta_23": 0.04108,
    "sin_theta_13": 0.00382,
    "delta_cp": 1.196,
    "jarlskog": 3.0e-5,
}

PMNS_REFERENCES = {
    "sin2_theta_12": 0.307,
    "sin2_theta_13": 0.0222,
    "sin2_theta_23": 0.558,
    "delta_m2_21_over_delta_m2_31": 7.42e-5 / 2.517e-3,
}


@dataclass(frozen=True)
class Prediction:
    """One auditable model-output row."""

    id: str
    sector: str
    quantity: str
    predicted: Any
    reference: Any
    absolute_error: float | None
    relative_error: float | None
    status: str
    source_module: str
    limitations: tuple[str, ...]
    metadata: dict[str, Any] = field(default_factory=dict)


def _error_pair(predicted: Any, reference: Any) -> tuple[float | None, float | None]:
    if predicted is None or reference is None:
        return None, None
    try:
        p = float(predicted)
        r = float(reference)
    except (TypeError, ValueError):
        return None, None
    absolute = abs(p - r)
    relative = None if r == 0 else absolute / abs(r)
    return float(absolute), float(relative) if relative is not None else None


def _prediction(
    id: str,
    sector: str,
    quantity: str,
    predicted: Any,
    reference: Any,
    status: str,
    source_module: str,
    limitations: Iterable[str],
    metadata: dict[str, Any] | None = None,
) -> Prediction:
    absolute, relative = _error_pair(predicted, reference)
    return Prediction(
        id=id,
        sector=sector,
        quantity=quantity,
        predicted=predicted,
        reference=reference,
        absolute_error=absolute,
        relative_error=relative,
        status=status,
        source_module=source_module,
        limitations=tuple(limitations),
        metadata=dict(metadata or {}),
    )


def _matrix_magnitudes(matrix: np.ndarray) -> list[list[float]]:
    return np.abs(np.asarray(matrix, dtype=float)).tolist()


def build_prediction_ledger(model: BHSMModel) -> list[Prediction]:
    """Build the complete table-driven BHSM model-output ledger."""

    rows: list[Prediction] = []

    yukawa = compute_yukawa_ratios(model)
    mass_references = default_mass_references()["MIXED_DEFAULT"]
    for sector, ratios in yukawa.items():
        for rank, value in ratios.items():
            if rank == "heavy":
                reference = 1.0
                quantity = "heavy/reference"
                scheme = "normalization"
                scale = "not_applicable"
                scheme_consistent = True
                scheme_sensitive = False
                pull = None
            else:
                quantity = f"{rank}/heavy"
                numerator, denominator = PARTICLE_FOR_RATIO[(sector, rank)]
                ratio_reference = build_ratio_reference(numerator, denominator, mass_references)
                reference = ratio_reference.ratio
                scheme = ratio_reference.scheme
                scale = ratio_reference.scale
                scheme_consistent = ratio_reference.scheme_consistent
                scheme_sensitive = sector in {"up_quarks", "down_quarks"} and not scheme_consistent
                pull = None
            rows.append(
                _prediction(
                    id=f"mass_ratio.{sector}.{rank}",
                    sector="fermion_mass_ratios",
                    quantity=f"{sector}.{quantity}",
                    predicted=value,
                    reference=reference,
                    status="SCREEN",
                    source_module="yukawa_overlap.py",
                    limitations=(
                        "Computed from internal overlap modes; numerical agreement is a screen, not a final prediction.",
                        "Quark mass references are scheme-sensitive unless a common-scale running scheme is supplied." if scheme_sensitive else "Mass reference is scheme-stable for this audit.",
                    ),
                    metadata={
                        "scheme": scheme,
                        "mass_scheme": scheme,
                        "scale": scale,
                        "scheme_consistent": scheme_consistent,
                        "scheme_sensitive": scheme_sensitive,
                        "pull": pull,
                    },
                )
            )

    ckm = compute_ckm_from_internal_rules(model)
    for name, value in dict(ckm["angles"]).items():
        rows.append(
            _prediction(
                id=f"ckm.{name}",
                sector="ckm",
                quantity=name,
                predicted=value,
                reference=CKM_REFERENCES[name],
                status=str(ckm["status"]),
                source_module="ckm.py",
                limitations=(str(ckm["limitation"]),),
            )
        )
    rows.append(
        _prediction(
            id="ckm.matrix_magnitudes",
            sector="ckm",
            quantity="|V_CKM|",
            predicted=_matrix_magnitudes(np.asarray(ckm["matrix_magnitudes"], dtype=float)),
            reference=None,
            status=str(ckm["status"]),
            source_module="ckm.py",
            limitations=(str(ckm["limitation"]),),
        )
    )
    rows.append(
        _prediction(
            id="ckm.delta_cp",
            sector="ckm",
            quantity="delta_cp",
            predicted=float(ckm["delta"]["delta"]),
            reference=CKM_REFERENCES["delta_cp"],
            status=str(ckm["cp_phase_status"]),
            source_module="flavor_matrix.py",
            limitations=(str(ckm["limitation"]),),
            metadata={
                "formula": ckm["delta"]["formula"],
                "delta_q": ckm["delta"]["delta_q"],
                "q_u": ckm["delta"]["q_u"],
                "q_d": ckm["delta"]["q_d"],
                "S": ckm["delta"]["S"],
            },
        )
    )
    rows.append(
        _prediction(
            id="ckm.jarlskog",
            sector="ckm",
            quantity="J_CKM",
            predicted=float(ckm["jarlskog"]),
            reference=CKM_REFERENCES["jarlskog"],
            status=str(ckm["cp_phase_status"]),
            source_module="flavor_matrix.py",
            limitations=(str(ckm["limitation"]),),
        )
    )

    pmns = compute_pmns_from_internal_rules(model)
    for name, value in dict(pmns["angles"]).items():
        rows.append(
            _prediction(
                id=f"pmns_effective.{name}",
                sector="pmns_effective",
                quantity=name,
                predicted=value,
                reference=PMNS_REFERENCES[name],
                status=str(pmns["status"]),
                source_module="pmns.py",
                limitations=(str(pmns["limitation"]),),
            )
        )

    couplings = compute_geometric_couplings(model)["values"]
    coupling_refs = {
        "alpha_1": None,
        "alpha_2": None,
        "alpha_3": ALPHA3_MZ_EMPIRICAL,
        "sin2_theta_w": SIN2_THETA_W_EMPIRICAL,
        "alpha_em_inv_mew": ALPHA_EM_INV_EW_EMPIRICAL,
    }
    for name, value in couplings.items():
        rows.append(
            _prediction(
                id=f"gauge_couplings.{name}",
                sector="gauge_couplings",
                quantity=name,
                predicted=value,
                reference=coupling_refs[name],
                status="SCREEN",
                source_module="gauge_couplings.py",
                limitations=(
                    "Geometric couplings are electroweak-scale matching screens; full threshold RG matching remains open.",
                ),
            )
        )

    higgs = compute_higgs_sector(model)["outputs"]
    higgs_refs = {
        "v": V_HIGGS_EMPIRICAL_GEV,
        "m_H_approx_v_over_2": 125.10,
        "M_lift": None,
    }
    higgs_values = {
        "v": higgs["v_gev"],
        "m_H_approx_v_over_2": float(higgs["v_gev"]) / 2.0,
        "M_lift": higgs["m_lift_gev"],
    }
    for name, value in higgs_values.items():
        rows.append(
            _prediction(
                id=f"higgs_electroweak.{name}",
                sector="higgs_electroweak",
                quantity=name,
                predicted=value,
                reference=higgs_refs[name],
                status="SCREEN",
                source_module="higgs_scale.py",
                limitations=(
                    "Electroweak scale output is a numerical screen, not an independent proof.",
                ),
            )
        )

    ht = compute_ht_gap_status(model)
    for name in ("first_complement_eigenvalue", "first_ht_complement_gap", "margin"):
        reference = MU_H if name == "first_ht_complement_gap" else None
        rows.append(
            _prediction(
                id=f"ht_gap.{name}",
                sector="ht_gap",
                quantity=name,
                predicted=ht[name],
                reference=reference,
                status="PROXY_AUDIT",
                source_module="ht_operator.py",
                limitations=(
                    "Level 2 finite-basis H_T proxy; full analytic spectrum remains open.",
                ),
            )
        )
    rows.append(
        _prediction(
            id="ht_gap.passes",
            sector="ht_gap",
            quantity="passes_proxy_gap",
            predicted=bool(ht["passes"]),
            reference=True,
            status="PROXY_AUDIT",
            source_module="ht_operator.py",
            limitations=(
                "Pass/fail applies only to the current finite-basis proxy audit.",
            ),
        )
    )

    scalar = compute_scalar_decoupling_status(model)
    for name in ("passes", "light_higgs_projection_count", "mode_count"):
        reference = True if name == "passes" else (1 if name == "light_higgs_projection_count" else None)
        rows.append(
            _prediction(
                id=f"scalar_decoupling.{name}",
                sector="scalar_decoupling",
                quantity=name,
                predicted=scalar[name],
                reference=reference,
                status="FINITE_BASIS_SCAFFOLD",
                source_module="scalar_decoupling.py",
                limitations=(
                    "Scalar/topographic decoupling remains a finite-basis scaffold; full action-level proof remains open.",
                ),
            )
        )

    return rows


def predictions_by_sector(ledger: Iterable[Prediction], sector: str) -> list[Prediction]:
    """Return prediction rows for a sector."""

    return [row for row in ledger if row.sector == sector]


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def export_prediction_ledger_json(ledger: Iterable[Prediction], path: str | Path) -> None:
    """Export the prediction ledger as JSON."""

    data = [_jsonable(asdict(row)) for row in ledger]
    Path(path).write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def export_prediction_ledger_markdown(ledger: Iterable[Prediction], path: str | Path) -> None:
    """Export the prediction ledger as a table-driven Markdown file."""

    rows = list(ledger)
    lines = [
        "# BHSM Prediction/Screen Ledger",
        "",
        "The term prediction here means model-output ledger entry. Rows keep their own screen, proxy, scaffold, or placeholder status.",
        "",
        "| ID | Sector | Quantity | Predicted | Reference | Relative Error | Status | Source | Limitations |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        relative = "" if row.relative_error is None else f"{row.relative_error:.12g}"
        lines.append(
            "| `{}` | {} | {} | `{}` | `{}` | {} | `{}` | `{}` | {} |".format(
                row.id,
                row.sector,
                row.quantity,
                _jsonable(row.predicted),
                _jsonable(row.reference),
                relative,
                row.status,
                row.source_module,
                "<br>".join(row.limitations),
            )
        )
    Path(path).write_text("\n".join(lines) + "\n")


def finite_relative_errors(ledger: Iterable[Prediction]) -> list[float]:
    """Return finite relative errors for report summaries."""

    values = [row.relative_error for row in ledger if row.relative_error is not None]
    return [float(value) for value in values if isfinite(float(value))]
