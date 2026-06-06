"""Falsification ledger and tolerance scoring for frozen BHSM v1 outputs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Any, Mapping


@dataclass(frozen=True)
class FalsificationCriterion:
    """One explicit way the frozen BHSM v1 package can fail or weaken."""

    id: str
    title: str
    statement: str
    status: str
    implications: tuple[str, ...]


def build_bhsm_falsification_ledger() -> tuple[FalsificationCriterion, ...]:
    """Return the BHSM v1 falsification criteria F1-F9."""

    return (
        FalsificationCriterion(
            "F1",
            "Canonical Geometry Failure",
            "If alpha-anchored a cannot be derived from the internal action, BHSM geometry weakens.",
            "OPEN_PROOF_OBLIGATION",
            ("Geometry branch becomes conditional rather than action-derived.",),
        ),
        FalsificationCriterion(
            "F2",
            "Mode-Selection Failure",
            "If Omega_f cannot be derived from the twisted Dirac/bundle action, mass hierarchy predictions remain unsupported.",
            "OPEN_PROOF_OBLIGATION",
            ("Flavor hierarchy branch weakens or must be revised.",),
        ),
        FalsificationCriterion(
            "F3",
            "Common-Scale Quark Failure",
            "If scheme-consistent quark ratios disagree beyond fixed tolerance bands, BHSM flavor mapping fails or must be revised.",
            "FALSIFIABLE_NUMERICAL_BRANCH",
            ("Quark flavor mapping is constrained by common-scale running comparisons.",),
        ),
        FalsificationCriterion(
            "F4",
            "CKM Failure",
            "If canonical BHSM V_us, V_cb, V_ub, delta, and J fail outside fixed tolerances, BHSM flavor mapping is falsified or constrained.",
            "FALSIFIABLE_NUMERICAL_BRANCH",
            ("CKM internal-rule screen must survive frozen tolerance bands.",),
        ),
        FalsificationCriterion(
            "F5",
            "PMNS Effective Failure",
            "If neutrino ordering, octant, or phase decisively contradict BHSM effective-extension outputs, the neutrino branch fails.",
            "EFFECTIVE_EXTENSION_BRANCH",
            ("PMNS rows are effective-extension screens, not minimal-SM outputs.",),
        ),
        FalsificationCriterion(
            "F6",
            "H_T Gap Failure",
            "If the full twisted Dirac/H_T spectrum produces extra light states below 4 pi^2 v, the SM-equivalent BHSM mapping fails.",
            "OPEN_SPECTRAL_THEOREM",
            ("Proxy H_T success must be replaced by the full spectrum.",),
        ),
        FalsificationCriterion(
            "F7",
            "Scalar Decoupling Failure",
            "If unscreened light scalar/topographic modes remain, BHSM fails as a Standard-Model-equivalent low-energy theory.",
            "OPEN_ACTION_LEVEL_PROOF",
            ("Scalar/topographic scaffold must be proven in the full action.",),
        ),
        FalsificationCriterion(
            "F8",
            "RG Matching Failure",
            "If higher-loop/threshold RG matching moves coupling agreement away from the electroweak scale beyond tolerance, the coupling branch weakens.",
            "OPEN_RG_MATCHING",
            ("One-loop/electroweak matching screen must survive higher-order matching.",),
        ),
        FalsificationCriterion(
            "F9",
            "No-Retuning Failure",
            "Any post-freeze adjustment of a, S, modes, or Z_virt based on residuals invalidates the v1.0 prediction set.",
            "FREEZE_CONSTRAINT",
            ("Frozen branches are invalidated by residual-driven retuning.",),
        ),
    )


def evaluate_prediction_against_tolerance(
    predicted: Any,
    reference: Any,
    tolerance: float | None = None,
    *,
    binary: bool = False,
    expected: Any = True,
    scheme_sensitive: bool = False,
) -> dict[str, object]:
    """Evaluate a value against a declared tolerance or binary expectation."""

    if binary:
        passes = predicted == expected
        return {
            "predicted": predicted,
            "reference": expected,
            "relative_error": None,
            "tolerance": "binary",
            "passes": bool(passes),
            "status": "PASS" if passes else "FAIL",
        }
    if predicted is None or reference is None:
        return {
            "predicted": predicted,
            "reference": reference,
            "relative_error": None,
            "tolerance": tolerance,
            "passes": None,
            "status": "NO_REFERENCE",
        }
    p = float(predicted)
    r = float(reference)
    relative = None if r == 0 else abs(p - r) / abs(r)
    passes = relative is not None and tolerance is not None and relative <= tolerance
    status = "PASS" if passes else "FAIL"
    if scheme_sensitive and not passes:
        status = "SCHEME_SENSITIVE"
    return {
        "predicted": p,
        "reference": r,
        "relative_error": float(relative) if relative is not None and isfinite(relative) else None,
        "tolerance": tolerance,
        "passes": bool(passes),
        "status": status,
    }


def _score_row(name: str, result: dict[str, object]) -> dict[str, object]:
    return {"id": name, **result}


def score_frozen_prediction_set(prediction_set: Any) -> dict[str, object]:
    """Score a frozen prediction set against predeclared tolerance bands."""

    from prediction_ledger import CKM_REFERENCES, PMNS_REFERENCES
    from constants import ALPHA3_MZ_EMPIRICAL, ALPHA_EM_INV_EW_EMPIRICAL, SIN2_THETA_W_EMPIRICAL, V_HIGGS_EMPIRICAL_GEV
    from mass_scheme import default_mass_references, build_ratio_reference

    tolerances: Mapping[str, Any] = prediction_set.tolerance_bands
    outputs: Mapping[str, Any] = prediction_set.outputs
    mass_refs = default_mass_references()["MIXED_DEFAULT"]
    rows: list[dict[str, object]] = []

    for rank, pair in {"middle": ("mu", "tau"), "light": ("e", "tau")}.items():
        ref = build_ratio_reference(pair[0], pair[1], mass_refs).ratio
        rows.append(_score_row(f"charged_leptons.{rank}", evaluate_prediction_against_tolerance(outputs["charged_lepton_ratios"][rank], ref, tolerances["charged_lepton_ratios"])))

    for rank, pair in {"middle": ("c", "t"), "light": ("u", "t")}.items():
        ref = build_ratio_reference(pair[0], pair[1], mass_refs).ratio
        rows.append(_score_row(f"up_quarks.{rank}", evaluate_prediction_against_tolerance(outputs["up_quark_ratios"][rank], ref, tolerances["quark_ratios_scheme_aware"], scheme_sensitive=True)))

    for rank, pair in {"middle": ("s", "b"), "light": ("d", "b")}.items():
        ref = build_ratio_reference(pair[0], pair[1], mass_refs).ratio
        rows.append(_score_row(f"down_quarks.{rank}", evaluate_prediction_against_tolerance(outputs["down_quark_ratios"][rank], ref, tolerances["quark_ratios_scheme_aware"], scheme_sensitive=True)))

    for name in ("sin_theta_12", "sin_theta_23", "sin_theta_13"):
        rows.append(_score_row(f"ckm.{name}", evaluate_prediction_against_tolerance(outputs["ckm"]["angles"][name], CKM_REFERENCES[name], tolerances["ckm_angles"])))
    rows.append(_score_row("ckm.delta_cp", evaluate_prediction_against_tolerance(outputs["ckm"]["delta"], CKM_REFERENCES["delta_cp"], tolerances["ckm_cp_jarlskog"])))
    rows.append(_score_row("ckm.jarlskog", evaluate_prediction_against_tolerance(outputs["ckm"]["jarlskog"], CKM_REFERENCES["jarlskog"], tolerances["ckm_cp_jarlskog"])))

    for name, ref in PMNS_REFERENCES.items():
        rows.append(_score_row(f"pmns.{name}", evaluate_prediction_against_tolerance(outputs["pmns_effective"][name], ref, tolerances["pmns_effective"])))

    rows.append(_score_row("gauge.alpha_3", evaluate_prediction_against_tolerance(outputs["gauge_couplings"]["alpha_3"], ALPHA3_MZ_EMPIRICAL, tolerances["gauge_couplings"])))
    rows.append(_score_row("gauge.sin2_theta_w", evaluate_prediction_against_tolerance(outputs["gauge_couplings"]["sin2_theta_w"], SIN2_THETA_W_EMPIRICAL, tolerances["gauge_couplings"])))
    rows.append(_score_row("gauge.alpha_em_inv_mew", evaluate_prediction_against_tolerance(outputs["gauge_couplings"]["alpha_em_inv_mew"], ALPHA_EM_INV_EW_EMPIRICAL, tolerances["gauge_couplings"])))
    rows.append(_score_row("higgs.v", evaluate_prediction_against_tolerance(outputs["higgs_electroweak"]["v_gev"], V_HIGGS_EMPIRICAL_GEV, tolerances["higgs_electroweak_v"])))
    rows.append(_score_row("higgs.m_h_zeroth", evaluate_prediction_against_tolerance(outputs["higgs_electroweak"]["m_H_approx_v_over_2"], 125.10, tolerances["higgs_mass_zeroth_order"])))
    rows.append(_score_row("ht_gap.passes", evaluate_prediction_against_tolerance(outputs["ht_gap_status"]["passes"], True, binary=True)))
    rows.append(_score_row("scalar_decoupling.passes", evaluate_prediction_against_tolerance(outputs["scalar_decoupling_status"]["passes"], True, binary=True)))

    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row["status"])] = counts.get(str(row["status"]), 0) + 1
    return {
        "branch": prediction_set.version.branch,
        "rows": rows,
        "status_counts": counts,
        "tolerances_declared_before_scoring": True,
        "falsification_criteria": [asdict(item) for item in build_bhsm_falsification_ledger()],
    }
