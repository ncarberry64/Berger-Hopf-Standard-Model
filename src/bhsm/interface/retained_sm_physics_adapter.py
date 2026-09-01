"""Match retained SM component artifacts into the universal physics engine.

The v15/v16 artifacts are reusable action components, not a license to
promote their historical centers as the current AE2 physical background.
This adapter extracts the data that genuinely match (bundle, representations,
selection rules, response seeds) and states the exact inputs still required
before physical poles or observables can be produced.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class RetainedSMComponentMatch:
    chiral_bundle: dict
    allowed_yukawa_channels: tuple[str, ...]
    gauge_response_seeds: dict[str, dict[str, float]]
    hs_channel_kinetic_seeds: dict[str, float]
    cycle_matching_scale_ratio: float
    bundle_validation_passed: bool
    response_validation_passed: bool
    scale_validation_passed: bool
    physical_higgs_direction_selected: bool
    replacement_quantum_saddle_solved: bool
    yukawa_matrices_derived: bool
    masses_and_mixing_derived: bool
    local_zero_momentum_couplings_derived: bool

    def matched_inputs(self) -> dict:
        return {
            "faithful_gauge_group": self.chiral_bundle["faithful_gauge_group"],
            "families": self.chiral_bundle["families"],
            "one_family_complex_dimension": self.chiral_bundle[
                "one_family_complex_dimension"
            ],
            "allowed_yukawa_channels": list(self.allowed_yukawa_channels),
            "gauge_response_sectors": sorted(self.gauge_response_seeds),
            "hs_channels": sorted(self.hs_channel_kinetic_seeds),
            "cycle_matching_scale_ratio": self.cycle_matching_scale_ratio,
            "historical_centers_promoted": False,
            "measured_SM_values_used": False,
        }

    def physical_engine_blockers(
        self,
        *,
        gate7_closed: bool,
        current_background_attached: bool,
        full_field_action_attached: bool,
        universal_gf_scale_attached: bool,
    ) -> tuple[str, ...]:
        blockers: list[str] = []
        if not gate7_closed:
            blockers.append("Gate7_closed_background")
        if not current_background_attached:
            blockers.append("current_AE2_background_attachment")
        if not full_field_action_attached:
            blockers.append("machine_readable_full_gauge_fermion_HS_action")
        if not universal_gf_scale_attached:
            blockers.append("single_owner_authorized_G_F_scale_map")
        if not self.replacement_quantum_saddle_solved:
            blockers.append("same_action_replacement_quantum_saddle")
        if not self.physical_higgs_direction_selected:
            blockers.append("action_selected_physical_HS_direction")
        if not self.local_zero_momentum_couplings_derived:
            blockers.append("local_zero_momentum_gauge_couplings")
        if not self.yukawa_matrices_derived:
            blockers.append("action_derived_Yukawa_matrices")
        if not self.masses_and_mixing_derived:
            blockers.append("action_derived_mass_and_mixing_spectrum")
        return tuple(blockers)


def _load(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_retained_sm_component_match(
    bundle_path: str | Path,
    response_path: str | Path,
    scale_path: str | Path,
) -> RetainedSMComponentMatch:
    bundle = _load(bundle_path)
    response = _load(response_path)
    scale = _load(scale_path)
    if bundle.get("artifact") != "BHSM_aether_hybrid_standard_model_bundle_v15_53":
        raise ValueError("unexpected retained SM bundle artifact")
    if response.get("artifact") != "BHSM_aether_common_gauge_hs_pushforward_v16_05":
        raise ValueError("unexpected common gauge/HS response artifact")
    if scale.get("artifact") != "BHSM_aether_cycle_scale_renormalization_v15_89":
        raise ValueError("unexpected retained cycle-scale artifact")

    response_core = response["common_M5_to_M4_pushforward"]["common_response"]
    yukawa_sums = bundle["yukawa_and_anomaly_ledger"]["Yukawa_hypercharge_sums"]
    allowed = tuple(sorted(name for name, total in yukawa_sums.items() if total == "0"))
    bundle_claim = bundle["claim_boundary"]
    response_claim = response["claim_boundary"]
    scale_claim = scale["claim_boundary"]
    return RetainedSMComponentMatch(
        chiral_bundle=bundle["chiral_bundle"],
        allowed_yukawa_channels=allowed,
        gauge_response_seeds=response_core["group_residues"],
        hs_channel_kinetic_seeds=response_core["HS_channel_kinetic_matrix"],
        cycle_matching_scale_ratio=float(
            scale["cycle_matching_scale"]["cycle_matching_scale_in_ell_kappa_inverse"]
        ),
        bundle_validation_passed=bool(bundle["validation_passed"]),
        response_validation_passed=bool(response["validation_passed"]),
        scale_validation_passed=bool(scale["validation_passed"]),
        physical_higgs_direction_selected=bool(
            response_claim["physical_single_Higgs_direction_selected"]
        ),
        replacement_quantum_saddle_solved=bool(
            response_claim["replacement_quantum_saddle_solved"]
        ),
        yukawa_matrices_derived=bool(bundle_claim["Yukawa_matrix_entries_derived"]),
        masses_and_mixing_derived=bool(
            bundle_claim["mass_eigenvalues_and_mixing_derived"]
        ),
        local_zero_momentum_couplings_derived=bool(
            scale_claim["local_zero_momentum_SM_couplings_derived"]
        ),
    )


__all__ = ["RetainedSMComponentMatch", "load_retained_sm_component_match"]
