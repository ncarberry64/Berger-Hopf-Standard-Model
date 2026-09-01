"""Exploratory CKM 2-3 mixing dressing audit.

This module tests pre-declared fractional powers of the existing
``Z_virt^{u,2}=1/2`` dressing factor as a possible 2-3 CKM-channel-only
suppression. It does not alter the frozen BHSM branches or prediction files.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import isfinite
from pathlib import Path
from typing import Iterable

import numpy as np

from bhsm_model import build_bhsm_model
from ckm import ckm_matrix_magnitudes
from flavor_matrix import canonical_ckm_angles, canonical_ckm_delta, jarlskog_invariant


STATUS = "EXPLORATORY_CANDIDATE"
Z_VIRT_U2 = 0.5

CKM_ELEMENT_ORDER = (
    ("Vud", 0, 0),
    ("Vus", 0, 1),
    ("Vub", 0, 2),
    ("Vcd", 1, 0),
    ("Vcs", 1, 1),
    ("Vcb", 1, 2),
    ("Vtd", 2, 0),
    ("Vts", 2, 1),
    ("Vtb", 2, 2),
)

PDG_STYLE_CKM_REFERENCES = {
    "Vud": 0.97367,
    "Vus": 0.22431,
    "Vub": 3.82e-3,
    "Vcd": 0.221,
    "Vcs": 0.975,
    "Vcb": 41.1e-3,
    "Vtd": 8.6e-3,
    "Vts": 41.5e-3,
    "Vtb": 1.010,
    "J_CKM": 3.0e-5,
}

PDG_STYLE_REFERENCE_NOTES = (
    "PDG-style direct CKM magnitudes use the 2024 PDG CKM matrix review values "
    "for element-by-element comparison; Vtb is a direct single-top style value "
    "and can exceed unity within uncertainty.",
    "J_CKM uses the repository's existing PDG-style reference value 3.0e-5.",
)


@dataclass(frozen=True)
class CKMDressingCandidate:
    """One pre-declared candidate fractional power of Z_virt."""

    label: str
    power: float | None
    factor: float
    status: str


@dataclass(frozen=True)
class CKMResidual:
    """Residual for one matrix element or Jarlskog row."""

    quantity: str
    predicted: float
    reference: float
    absolute_error: float
    relative_error: float


@dataclass(frozen=True)
class CKMDressingAuditRow:
    """Audit output for one candidate."""

    candidate: CKMDressingCandidate
    sin_theta_12: float
    sin_theta_23: float
    sin_theta_13: float
    delta: float
    matrix_magnitudes: list[list[float]]
    jarlskog: float
    residuals: tuple[CKMResidual, ...]
    improves_vcb_vts: bool
    damages_rest: bool
    conclusion: str


def candidate_powers() -> tuple[CKMDressingCandidate, ...]:
    """Return only the pre-declared dressing candidates."""

    powers: tuple[tuple[str, float | None], ...] = (
        ("no_correction", None),
        ("Z^(1/4)", 1.0 / 4.0),
        ("Z^(1/8)", 1.0 / 8.0),
        ("Z^(1/16)", 1.0 / 16.0),
    )
    return tuple(
        CKMDressingCandidate(
            label=label,
            power=power,
            factor=1.0 if power is None else float(Z_VIRT_U2**power),
            status=STATUS,
        )
        for label, power in powers
    )


def _relative_error(predicted: float, reference: float) -> float:
    if reference == 0.0:
        return 0.0 if predicted == 0.0 else float("inf")
    return abs(predicted - reference) / abs(reference)


def _residual(quantity: str, predicted: float, reference: float) -> CKMResidual:
    return CKMResidual(
        quantity=quantity,
        predicted=float(predicted),
        reference=float(reference),
        absolute_error=float(abs(predicted - reference)),
        relative_error=float(_relative_error(predicted, reference)),
    )


def _residuals(matrix: np.ndarray, jarlskog: float) -> tuple[CKMResidual, ...]:
    rows = [
        _residual(name, float(matrix[i, j]), PDG_STYLE_CKM_REFERENCES[name])
        for name, i, j in CKM_ELEMENT_ORDER
    ]
    rows.append(_residual("J_CKM", float(jarlskog), PDG_STYLE_CKM_REFERENCES["J_CKM"]))
    return tuple(rows)


def _residual_map(row: CKMDressingAuditRow) -> dict[str, CKMResidual]:
    return {residual.quantity: residual for residual in row.residuals}


def build_ckm_mixing_dressing_audit() -> tuple[CKMDressingAuditRow, ...]:
    """Build the CKM 2-3 dressing audit without changing frozen outputs."""

    model = build_bhsm_model()
    angles = canonical_ckm_angles(model)
    delta = float(canonical_ckm_delta(model)["delta"])

    rows: list[CKMDressingAuditRow] = []
    baseline_residuals: dict[str, CKMResidual] | None = None
    for candidate in candidate_powers():
        sin12 = float(angles["sin_theta_12"])
        sin23 = float(angles["sin_theta_23"] * candidate.factor)
        sin13 = float(angles["sin_theta_13"])
        matrix = ckm_matrix_magnitudes(sin12, sin23, sin13, delta=delta)
        jarlskog = jarlskog_invariant(sin12, sin23, sin13, delta)
        residuals = _residuals(matrix, jarlskog)
        temp_row = CKMDressingAuditRow(
            candidate=candidate,
            sin_theta_12=sin12,
            sin_theta_23=sin23,
            sin_theta_13=sin13,
            delta=delta,
            matrix_magnitudes=np.asarray(matrix, dtype=float).tolist(),
            jarlskog=float(jarlskog),
            residuals=residuals,
            improves_vcb_vts=False,
            damages_rest=False,
            conclusion="pending",
        )
        current = _residual_map(temp_row)
        if baseline_residuals is None:
            baseline_residuals = current
        improves = (
            current["Vcb"].relative_error < baseline_residuals["Vcb"].relative_error
            and current["Vts"].relative_error < baseline_residuals["Vts"].relative_error
        )
        watched = {"Vcb", "Vts"}
        damage_threshold = 0.01
        damages = any(
            current[name].relative_error
            > baseline_residuals[name].relative_error + damage_threshold
            for name in current
            if name not in watched
        )
        if candidate.power is None:
            conclusion = "baseline frozen CKM screen; no mixing dressing applied"
        elif improves and not damages:
            conclusion = "improves Vcb/Vts without material damage to non-2-3 rows in this audit"
        elif improves:
            conclusion = "improves Vcb/Vts but damages at least one non-2-3 row"
        else:
            conclusion = "does not improve both Vcb and Vts relative to the baseline"
        rows.append(
            CKMDressingAuditRow(
                candidate=candidate,
                sin_theta_12=temp_row.sin_theta_12,
                sin_theta_23=temp_row.sin_theta_23,
                sin_theta_13=temp_row.sin_theta_13,
                delta=temp_row.delta,
                matrix_magnitudes=temp_row.matrix_magnitudes,
                jarlskog=temp_row.jarlskog,
                residuals=temp_row.residuals,
                improves_vcb_vts=improves,
                damages_rest=damages,
                conclusion=conclusion,
            )
        )
    return tuple(rows)


def best_candidate(rows: Iterable[CKMDressingAuditRow]) -> CKMDressingAuditRow:
    """Return the lowest combined Vcb/Vts residual candidate."""

    row_tuple = tuple(rows)
    if not row_tuple:
        raise ValueError("rows must not be empty")
    return min(
        row_tuple,
        key=lambda row: (
            _residual_map(row)["Vcb"].relative_error
            + _residual_map(row)["Vts"].relative_error
        ),
    )


def export_ckm_mixing_dressing_audit_json(path: str | Path) -> None:
    """Export the audit rows to JSON."""

    rows = build_ckm_mixing_dressing_audit()
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": STATUS,
        "z_virt_u2": Z_VIRT_U2,
        "reference_notes": PDG_STYLE_REFERENCE_NOTES,
        "rows": [asdict(row) for row in rows],
        "best_candidate": asdict(best_candidate(rows)),
        "limitations": [
            "Exploratory audit only; not part of BHSM_BARE_V1 or BHSM_DRESSED_V1_CANDIDATE.",
            "Only pre-declared powers of the existing Z_virt^{u,2}=1/2 are tested.",
            "Any adopted mixing-dressing rule must be frozen before future external comparisons.",
        ],
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def export_ckm_mixing_dressing_audit_markdown(path: str | Path) -> None:
    """Export the audit report to Markdown."""

    rows = build_ckm_mixing_dressing_audit()
    best = best_candidate(rows)
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# CKM Mixing Dressing Candidate Audit",
        "",
        "Status: `EXPLORATORY_CANDIDATE`",
        "",
        "This audit tests whether fractional powers of the existing "
        "`Z_virt^{u,2}=1/2` dressing factor suppress only the CKM 2-3 "
        "mixing channel. It does not modify `BHSM_BARE_V1`, "
        "`BHSM_DRESSED_V1_CANDIDATE`, frozen prediction files, or released "
        "CKM outputs.",
        "",
        "Any adopted mixing-dressing rule must be frozen before future "
        "external comparisons.",
        "",
        "## Inputs",
        "",
        f"- `Z_virt^{{u,2}} = {Z_VIRT_U2}`",
        "- Tested candidates: `no_correction`, `Z^(1/4)`, `Z^(1/8)`, `Z^(1/16)`",
        "- Dressing scope: multiply only `sin_theta_23`; leave `sin_theta_12`, "
        "`sin_theta_13`, and Hopf-phase `delta_CKM` unchanged.",
        "- CKM reconstruction: standard CKM parameterization using matrix magnitudes.",
        "- Reference set: PDG-style direct CKM magnitudes plus existing repository "
        "`J_CKM = 3.0e-5` reference.",
        "",
        "## Candidate Summary",
        "",
        "| Candidate | Factor | sin(theta_23) | Vcb rel. err. | Vts rel. err. | J rel. err. | Improves Vcb/Vts | Damages rest | Conclusion |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in rows:
        residuals = _residual_map(row)
        lines.append(
            "| `{}` | `{:.12g}` | `{:.12g}` | `{:.6g}` | `{:.6g}` | `{:.6g}` | `{}` | `{}` | {} |".format(
                row.candidate.label,
                row.candidate.factor,
                row.sin_theta_23,
                residuals["Vcb"].relative_error,
                residuals["Vts"].relative_error,
                residuals["J_CKM"].relative_error,
                row.improves_vcb_vts,
                row.damages_rest,
                row.conclusion,
            )
        )
    lines.extend(
        [
            "",
            "## Full Residual Table",
            "",
            "| Candidate | Quantity | Predicted | Reference | Relative Error |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for row in rows:
        for residual in row.residuals:
            lines.append(
                "| `{}` | `{}` | `{:.12g}` | `{:.12g}` | `{:.6g}` |".format(
                    row.candidate.label,
                    residual.quantity,
                    residual.predicted,
                    residual.reference,
                    residual.relative_error,
                )
            )
    lines.extend(
        [
            "",
            "## Best 2-3 Residual Candidate",
            "",
            f"`{best.candidate.label}` has the lowest combined `Vcb`/`Vts` "
            "relative error among the pre-declared candidates.",
            "",
            "This is not an adopted BHSM rule. It is an exploratory candidate "
            "for a future freeze decision only.",
            "",
            "## Limitations",
            "",
            "- This audit is not part of the frozen release.",
            "- The CKM frozen values remain unchanged.",
            "- No parameter, mode, tolerance, or prediction output is retuned.",
            "- Matrix references are PDG-style comparison inputs, not fitting targets.",
            "- Any adopted mixing-dressing rule must be specified and frozen before "
            "future external comparisons.",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Generate the Markdown and JSON audit artifacts."""

    export_ckm_mixing_dressing_audit_markdown(
        Path("audits") / "ckm_mixing_dressing_candidate_audit.md"
    )
    export_ckm_mixing_dressing_audit_json(
        Path("audits") / "ckm_mixing_dressing_candidate_audit.json"
    )


if __name__ == "__main__":
    main()
