"""Frozen BHSM v1.0 prediction sets.

The v1 branches are no-retuning snapshots. Construction does not inspect
residuals and scoring cannot modify frozen values.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from math import isclose
from pathlib import Path
from typing import Any, Mapping

from bhsm_config import canonical_geometry_config
from bhsm_model import (
    build_bhsm_model,
    compute_ckm_from_internal_rules,
    compute_geometric_couplings,
    compute_higgs_sector,
    compute_ht_gap_status,
    compute_pmns_from_internal_rules,
    compute_scalar_decoupling_status,
    compute_yukawa_ratios,
)
from constants import MODE_LEDGER, S_OVERLAP
from falsification import build_bhsm_falsification_ledger, score_frozen_prediction_set
from virtual_environment import pure_fiber_middle_up_rule, apply_virtual_dressing


BARE_BRANCH = "BHSM_BARE_V1"
DRESSED_BRANCH = "BHSM_DRESSED_V1_CANDIDATE"


@dataclass(frozen=True)
class BHSMVersion:
    """Frozen BHSM branch metadata."""

    name: str
    branch: str
    geometry_a: float
    overlap_s: float
    mode_ledger: Mapping[str, Mapping[str, tuple[int, int]]]
    dressing_rules: tuple[Mapping[str, Any], ...]
    status: str
    notes: tuple[str, ...]

    def __post_init__(self) -> None:
        """Reject off-freeze metadata through the normal constructor path."""

        if self.branch not in {BARE_BRANCH, DRESSED_BRANCH}:
            raise ValueError(f"unknown frozen BHSM v1 branch: {self.branch}")
        if not isclose(self.geometry_a, canonical_geometry_config().a, rel_tol=0.0, abs_tol=1e-15):
            raise ValueError("BHSM v1 freezes alpha-anchored geometry a")
        if not isclose(self.overlap_s, S_OVERLAP, rel_tol=0.0, abs_tol=1e-15):
            raise ValueError("BHSM v1 freezes S=1/(4*pi)")
        if self.mode_ledger != MODE_LEDGER:
            raise ValueError("BHSM v1 freezes the supplied mode ledger")
        if self.branch == BARE_BRANCH and self.dressing_rules:
            raise ValueError("BHSM_BARE_V1 cannot include dressing rules")
        if self.branch == DRESSED_BRANCH:
            if len(self.dressing_rules) != 1:
                raise ValueError("BHSM_DRESSED_V1_CANDIDATE requires exactly one dressing rule")
            rule = self.dressing_rules[0]
            if (
                rule.get("sector") != "up_quarks"
                or rule.get("generation") != "middle"
                or tuple(rule.get("mode", ())) != (6, 0)
                or not isclose(float(rule.get("factor", 0.0)), 0.5, rel_tol=0.0, abs_tol=1e-15)
            ):
                raise ValueError("BHSM v1 dressed candidate freezes only Z_virt^{u,2}=1/2 on mode (6,0)")


@dataclass(frozen=True)
class FrozenPredictionSet:
    """Frozen predictions plus declared tolerance/falsification metadata."""

    version: BHSMVersion
    outputs: Mapping[str, Any]
    tolerance_bands: Mapping[str, Any]
    falsification_ledger: tuple[Any, ...]
    score_summary: Mapping[str, Any] | None = None


def declared_tolerance_bands() -> dict[str, Any]:
    """Return tolerance bands declared before frozen-set scoring."""

    return {
        "exact_status": "pass_fail",
        "gauge_couplings": 0.01,
        "higgs_electroweak_v": 0.01,
        "higgs_mass_zeroth_order": 0.02,
        "charged_lepton_ratios": 0.25,
        "quark_ratios_scheme_aware": 0.25,
        "quark_ratios_otherwise": "SCHEME_SENSITIVE",
        "ckm_angles": 0.10,
        "ckm_cp_jarlskog": 0.10,
        "pmns_effective": 0.05,
        "ht_gap": "binary_pass_fail",
        "scalar_decoupling": "binary_scaffold_pass_fail",
    }


def _jsonable(value: object) -> object:
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return value


def _model_outputs(model: Any, ratios: Mapping[str, Mapping[str, float]]) -> dict[str, Any]:
    ckm = compute_ckm_from_internal_rules(model)
    pmns = compute_pmns_from_internal_rules(model)
    couplings = compute_geometric_couplings(model)["values"]
    higgs_outputs = compute_higgs_sector(model)["outputs"]
    return {
        "charged_lepton_ratios": dict(ratios["charged_leptons"]),
        "up_quark_ratios": dict(ratios["up_quarks"]),
        "down_quark_ratios": dict(ratios["down_quarks"]),
        "ckm": {
            "angles": dict(ckm["angles"]),
            "delta": float(ckm["delta"]["delta"]),
            "jarlskog": float(ckm["jarlskog"]),
            "matrix_magnitudes": ckm["matrix_magnitudes"].tolist(),
            "status": ckm["status"],
        },
        "pmns_effective": dict(pmns["angles"]),
        "gauge_couplings": dict(couplings),
        "higgs_electroweak": {
            "v_gev": float(higgs_outputs["v_gev"]),
            "m_H_approx_v_over_2": float(higgs_outputs["v_gev"]) / 2.0,
            "M_lift": float(higgs_outputs["m_lift_gev"]),
        },
        "ht_gap_status": compute_ht_gap_status(model),
        "scalar_decoupling_status": compute_scalar_decoupling_status(model),
    }


def _version(model: Any, branch: str, dressing_rules: tuple[Mapping[str, Any], ...], status: str) -> BHSMVersion:
    return BHSMVersion(
        name="BHSM v1.0",
        branch=branch,
        geometry_a=model.geometry_config.a,
        overlap_s=S_OVERLAP,
        mode_ledger=MODE_LEDGER,
        dressing_rules=dressing_rules,
        status=status,
        notes=(
            "Frozen no-retuning prediction set.",
            "Changing a, S, modes, or Z_virt based on residuals invalidates v1.0.",
        ),
    )


def _with_score(prediction_set: FrozenPredictionSet) -> FrozenPredictionSet:
    return FrozenPredictionSet(
        version=prediction_set.version,
        outputs=prediction_set.outputs,
        tolerance_bands=prediction_set.tolerance_bands,
        falsification_ledger=prediction_set.falsification_ledger,
        score_summary=score_frozen_prediction_set(prediction_set),
    )


def build_bhsm_bare_v1() -> FrozenPredictionSet:
    """Build the frozen bare canonical v1 branch."""

    model = build_bhsm_model()
    ratios = compute_yukawa_ratios(model)
    frozen = FrozenPredictionSet(
        version=_version(model, BARE_BRANCH, (), "FROZEN_BARE_CANONICAL"),
        outputs=_model_outputs(model, ratios),
        tolerance_bands=declared_tolerance_bands(),
        falsification_ledger=build_bhsm_falsification_ledger(),
        score_summary=None,
    )
    return _with_score(frozen)


def build_bhsm_dressed_v1_candidate() -> FrozenPredictionSet:
    """Build the frozen dressed-candidate v1 branch."""

    model = build_bhsm_model()
    rule = pure_fiber_middle_up_rule()
    ratios = apply_virtual_dressing(model, (rule,))
    frozen = FrozenPredictionSet(
        version=_version(model, DRESSED_BRANCH, (asdict(rule),), "FROZEN_DRESSED_CANDIDATE"),
        outputs=_model_outputs(model, ratios),
        tolerance_bands=declared_tolerance_bands(),
        falsification_ledger=build_bhsm_falsification_ledger(),
        score_summary=None,
    )
    return _with_score(frozen)


def compare_bhsm_v1_branches() -> dict[str, Any]:
    """Return a compact comparison of bare and dressed v1 branches."""

    bare = build_bhsm_bare_v1()
    dressed = build_bhsm_dressed_v1_candidate()
    rows = []
    for quantity, path in {
        "c/t": ("up_quark_ratios", "middle"),
        "u/t": ("up_quark_ratios", "light"),
        "s/b": ("down_quark_ratios", "middle"),
        "d/b": ("down_quark_ratios", "light"),
        "sin_theta_13": ("ckm", "angles", "sin_theta_13"),
    }.items():
        bare_value = bare.outputs[path[0]][path[1]] if len(path) == 2 else bare.outputs[path[0]][path[1]][path[2]]
        dressed_value = dressed.outputs[path[0]][path[1]] if len(path) == 2 else dressed.outputs[path[0]][path[1]][path[2]]
        rows.append(
            {
                "quantity": quantity,
                "bare": bare_value,
                "dressed": dressed_value,
                "changed": bare_value != dressed_value,
            }
        )
    return {
        "branches": (bare.version.branch, dressed.version.branch),
        "rows": rows,
        "tolerance_bands": declared_tolerance_bands(),
        "bare_score": bare.score_summary["status_counts"],
        "dressed_score": dressed.score_summary["status_counts"],
        "no_retuning": True,
    }


def export_frozen_prediction_set_json(path: str | Path) -> None:
    """Export both frozen v1 branches as JSON."""

    data = {
        "prediction_sets": (build_bhsm_bare_v1(), build_bhsm_dressed_v1_candidate()),
        "comparison": compare_bhsm_v1_branches(),
    }
    Path(path).write_text(json.dumps(_jsonable(data), indent=2, sort_keys=True) + "\n")


def export_frozen_prediction_set_markdown(path: str | Path) -> None:
    """Export both frozen v1 branches as Markdown."""

    bare = build_bhsm_bare_v1()
    dressed = build_bhsm_dressed_v1_candidate()
    comparison = compare_bhsm_v1_branches()
    lines = [
        "# BHSM v1.0 Frozen Prediction Set",
        "",
        "This is a no-retuning frozen prediction package with bare and dressed-candidate branches.",
        "",
        "## Tolerance Bands",
        "",
        "| Class | Tolerance |",
        "| --- | --- |",
    ]
    for key, value in declared_tolerance_bands().items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend([
        "",
        "## Branch Comparison",
        "",
        "| Quantity | BHSM_BARE_V1 | BHSM_DRESSED_V1_CANDIDATE | Changed |",
        "| --- | --- | --- | --- |",
    ])
    for row in comparison["rows"]:
        lines.append(f"| `{row['quantity']}` | `{row['bare']}` | `{row['dressed']}` | `{row['changed']}` |")
    lines.extend([
        "",
        "## Score Summary",
        "",
        f"- Bare: `{bare.score_summary['status_counts']}`",
        f"- Dressed candidate: `{dressed.score_summary['status_counts']}`",
        "",
        "## Freeze Notes",
        "",
        "- Canonical geometry, overlap width, mode ledger, and dressing rule are frozen.",
        "- No residual-driven retuning is allowed.",
        "- The dressed branch is a candidate branch, not a proof of the full internal action.",
        "",
    ])
    Path(path).write_text("\n".join(lines))


def export_falsification_ledger_json(path: str | Path) -> None:
    """Export the v1 falsification ledger as JSON."""

    Path(path).write_text(json.dumps(_jsonable(build_bhsm_falsification_ledger()), indent=2, sort_keys=True) + "\n")


def export_falsification_ledger_markdown(path: str | Path) -> None:
    """Export the v1 falsification ledger as Markdown."""

    lines = [
        "# BHSM v1.0 Falsification Ledger",
        "",
        "| ID | Title | Statement | Status | Implications |",
        "| --- | --- | --- | --- | --- |",
    ]
    for criterion in build_bhsm_falsification_ledger():
        lines.append(
            "| `{}` | {} | {} | `{}` | {} |".format(
                criterion.id,
                criterion.title,
                criterion.statement,
                criterion.status,
                "<br>".join(criterion.implications),
            )
        )
    lines.append("")
    Path(path).write_text("\n".join(lines))
