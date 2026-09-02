"""Materialize the AE4 stratified Dirac--zeta owner selection."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.ae4_stratified_dirac_zeta_induced_owner import (
    ACTION_VERSION,
    CLASSIFICATION,
    claim_boundary,
    enclosure_holding_threshold_hypothesis,
    forward_time_domain_contract,
    historical_reconciliation,
    induced_local_weight_ledger,
    microscopic_owner_contract,
    native_spectral_length_contract,
    proper_time_moment_ratio,
)


A = ROOT / "artifacts/action_extension"
TARGET = A / "BHSM_AE4_STRATIFIED_DIRAC_ZETA_INDUCED_OWNER.json"
INPUTS = (
    ROOT / "artifacts/BHSM_stratified_Dirac_zeta_micro_source_exhaustion_v14_63.json",
    ROOT / "artifacts/BHSM_heat_semigroup_profile_gate_v14_64.json",
    ROOT / "artifacts/BHSM_geometric_cross_stratum_trace_gate_v14_64.json",
    ROOT / "artifacts/BHSM_aether_common_source_frechet_response_v15_99.json",
    ROOT / "artifacts/BHSM_aether_quantum_functional_accounting_v16_00.json",
    ROOT / "src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py",
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()


def build_payload() -> dict[str, Any]:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError(", ".join(missing))
    v1463, heat_profile, trace_gate, response, accounting = map(_load, INPUTS[:5])
    weights = induced_local_weight_ledger()
    owner = microscopic_owner_contract()
    reconciliation = historical_reconciliation()
    boundary = claim_boundary()
    native_scale = native_spectral_length_contract()
    time_domain = forward_time_domain_contract()
    stability = enclosure_holding_threshold_hypothesis()
    validation = {
        "v14_63_open_choice_recovered": not v1463["single_microscopic_functional_derived_in_current_archive"],
        "v14_64_exponential_semigroup_reused": heat_profile["scalar_multiplier"] == "f_t(u)=exp(-t u)",
        "v14_64_geometric_trace_reused": trace_gate["canonical_unweighted_direct_sum_trace_available"],
        "v15_99_one_operator_frechet_engine_reused": response["validation"]["all_responses_from_one_operator"],
        "v16_00_no_double_counting_reused": "counts_the_same" in accounting["determinant_accounting"]["incorrect_sum"],
        "one_scale_moment_ratio_exact": proper_time_moment_ratio(8, 4) == 0.5,
        "all_required_positive_order_moments_present": set(weights["derived_positive_order_moments"]) == {"F8", "F6", "F5", "F4", "F3", "F2"},
        "independent_Wilson_owners_retired": not owner["independent_M8_M5_M4_Wilson_owners_retained"],
        "native_scale_not_free_cutoff": not native_scale["ell_star_is_free_universal_cutoff"],
        "future_physical_time_only": time_domain["physical_time_orientation"] == "FUTURE_DIRECTED_ONLY",
        "stability_hypothesis_not_promoted": not stability["physical_decay_law_derived"],
        "global_domain_not_overclaimed": not boundary["AE4_GLOBAL_SELF_ADJOINT_STRATIFIED_DIRAC_DOMAIN_DERIVED"],
        "physical_coefficients_not_overclaimed": not boundary["AE4_PHYSICAL_M8_M5_M4_NUMERICAL_COEFFICIENTS_DERIVED"],
    }
    return {
        "artifact": "BHSM_AE4_STRATIFIED_DIRAC_ZETA_INDUCED_OWNER",
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "microscopic_owner_contract": owner,
        "native_spectral_length_contract": native_scale,
        "forward_time_domain_contract": time_domain,
        "enclosure_holding_threshold_hypothesis": stability,
        "induced_local_weight_ledger": weights,
        "historical_reconciliation": reconciliation,
        "claim_boundary": boundary,
        "inputs": {path.relative_to(ROOT).as_posix(): _sha(path) for path in INPUTS},
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }


def main() -> None:
    payload = build_payload()
    if not payload["validation_passed"]:
        raise SystemExit("AE4 microscopic owner selection failed")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(TARGET.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
