from __future__ import annotations

from dataclasses import dataclass
from math import log
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"
FORBIDDEN_CONFIG_KEYS = (
    "mixed_pole_running_comparison",
    "fit_transport_to_residuals",
    "transport_factors_fit_to_residuals",
    "residual_absorber_transport",
    "sector_specific_fit",
    "tau_fit_to_masses",
    "sigma_fit_to_masses",
    "observed_masses_used_as_derivation_inputs",
    "empirical_targets_used",
    "CKM_data",
    "PMNS_data",
    "neutrino_data",
    "Higgs_data",
    "gauge_target_data",
    "cosmology_target_data",
)


@dataclass(frozen=True)
class TransportConfigValidation:
    valid: bool
    forbidden_keys_found: Tuple[str, ...]
    mixed_pole_running_comparison_allowed: bool
    transport_factors_fit_to_residuals: bool
    observed_masses_used_as_derivation_inputs: bool
    empirical_targets_used: bool


def validate_reference_scale(mu_ref: float) -> float:
    if mu_ref <= 0:
        raise ValueError("mu_ref must be positive")
    return float(mu_ref)


def validate_transport_config(config: Mapping[str, object]) -> TransportConfigValidation:
    forbidden = tuple(key for key in FORBIDDEN_CONFIG_KEYS if key in config and bool(config[key]))
    mixed_allowed = bool(config.get("mixed_pole_running_comparison_allowed", False))
    fit_transport = bool(config.get("transport_factors_fit_to_residuals", False))
    observed = bool(config.get("observed_masses_used_as_derivation_inputs", False))
    empirical = bool(config.get("empirical_targets_used", False))
    return TransportConfigValidation(
        valid=not forbidden and not mixed_allowed and not fit_transport and not observed and not empirical,
        forbidden_keys_found=forbidden,
        mixed_pole_running_comparison_allowed=mixed_allowed,
        transport_factors_fit_to_residuals=fit_transport,
        observed_masses_used_as_derivation_inputs=observed,
        empirical_targets_used=empirical,
    )


def same_sector_log_ratios(y_values: Sequence[float]) -> Dict[str, float]:
    if len(y_values) != 3:
        raise ValueError("expected three same-sector values in heavy, middle, light order")
    if any(value <= 0 for value in y_values):
        raise ValueError("same-sector log ratios require positive values")
    heavy, middle, light = [float(value) for value in y_values]
    return {
        "ln_y_heavy_over_middle": log(heavy / middle),
        "ln_y_middle_over_light": log(middle / light),
        "ln_y_heavy_over_light": log(heavy / light),
    }


def transported_yukawa(Y_geom: float, transport_factor: float) -> float:
    if Y_geom < 0:
        raise ValueError("Y_geom must be nonnegative")
    if transport_factor <= 0:
        raise ValueError("transport_factor must be positive")
    return float(Y_geom) * float(transport_factor)


def transported_same_sector_ratios(
    Y_geom: Sequence[float],
    transport_factors: Sequence[float],
) -> Dict[str, float]:
    if len(Y_geom) != len(transport_factors):
        raise ValueError("Y_geom and transport_factors must have matching lengths")
    transported = [
        transported_yukawa(y_value, factor)
        for y_value, factor in zip(Y_geom, transport_factors)
    ]
    return same_sector_log_ratios(transported)


def same_sector_gauge_cancellation_metadata(sector: str) -> Dict[str, object]:
    return {
        "sector": sector,
        "ordinary_gauge_running_cancels_in_same_sector_ratios": True,
        "reason": (
            "All generations in a charged sector share the same gauge representation; "
            "ordinary gauge-running factors are common within the sector."
        ),
        "cancellation_is_structural_not_mass_fit": True,
    }


def build_transport_decomposition_template() -> Dict[str, object]:
    return {
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "empirical_targets_used": False,
        "observed_masses_used_as_derivation_inputs": False,
        "mixed_pole_running_comparison_allowed": False,
        "transport_factors_fit_to_residuals": False,
        "charged_precision_closure": "OPEN",
        "transport_decomposition": {
            "T_f_i": [
                "T_gauge,f",
                "T_Yukawa,self,f_i",
                "T_threshold,f_i",
                "T_scheme,f",
            ],
            "formula": "T_f_i = T_gauge,f * T_Yukawa,self,f_i * T_threshold,f_i * T_scheme,f",
        },
        "same_sector_cancellation": {
            sector: same_sector_gauge_cancellation_metadata(sector)
            for sector in ("lepton", "up", "down")
        },
        "open_items": [
            "numerical residual RG coefficients",
            "full scheme/common-scale target population",
            "cross-sector transported mass ratios",
        ],
    }


def _empty_target_row(quantity: str) -> Dict[str, object]:
    return {
        "quantity": quantity,
        "value": None,
        "uncertainty": None,
        "scale": None,
        "scheme": None,
        "input_role": "EMPIRICAL_COMPARISON_INPUT",
        "derivation_input": False,
        "populated": False,
    }


def build_common_scale_target_schema() -> Dict[str, object]:
    return {
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "empirical_targets_used": False,
        "observed_masses_used_as_derivation_inputs": False,
        "mixed_pole_running_comparison_allowed": False,
        "transport_factors_fit_to_residuals": False,
        "charged_precision_closure": "OPEN",
        "schema_status": "EXPORTED_EMPTY_COMPARISON_SCHEMA",
        "target_rows": {
            "charged_same_sector_ratios": [
                _empty_target_row("ln_y_tau_over_y_mu"),
                _empty_target_row("ln_y_mu_over_y_e"),
                _empty_target_row("ln_y_top_over_y_charm"),
                _empty_target_row("ln_y_charm_over_y_up"),
                _empty_target_row("ln_y_bottom_over_y_strange"),
                _empty_target_row("ln_y_strange_over_y_down"),
            ],
            "charged_cross_sector_ratios": [
                _empty_target_row("ln_y_tau_over_y_top"),
                _empty_target_row("ln_y_bottom_over_y_tau"),
            ],
        },
        "notes": [
            "Future empirical values are comparison inputs only.",
            "No empirical charged masses are derivation inputs.",
            "Mixed pole/running comparisons are forbidden at the geometric gate.",
        ],
    }


def _package_entry(
    status: str,
    source_artifact: str | None,
    comparison_ready: bool,
    open_blockers: Iterable[str],
    uses_empirical_input: bool = False,
) -> Dict[str, object]:
    return {
        "status": status,
        "source_artifact": source_artifact,
        "uses_empirical_input": uses_empirical_input,
        "comparison_ready": comparison_ready,
        "open_blockers": list(open_blockers),
    }


def build_prediction_package_skeleton() -> Dict[str, object]:
    return {
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "empirical_targets_used": False,
        "observed_masses_used_as_derivation_inputs": False,
        "mixed_pole_running_comparison_allowed": False,
        "transport_factors_fit_to_residuals": False,
        "charged_precision_closure": "OPEN",
        "package_status": "EXPORTED_NOT_COMPARISON_READY",
        "sections": {
            "charged_same_sector_ratios": _package_entry(
                "STRUCTURAL_RESPONSE_EXPORTED",
                "artifacts/tau_response_curves_A_background_identity_v1.json",
                False,
                ["boundary-derived tau/sigma", "common-scale target population"],
            ),
            "charged_cross_sector_ratios": _package_entry(
                "OPEN",
                None,
                False,
                ["cross-sector transported mass ratios", "scheme/common-scale alignment"],
            ),
            "neutral_mass_splittings": _package_entry(
                "OPEN",
                None,
                False,
                ["neutral eta/beta/kappa final derivation", "neutral threshold rules"],
            ),
            "PMNS_angles_and_phase": _package_entry(
                "STRUCTURAL_SOURCE_ONLY",
                None,
                False,
                ["PMNS numerical closure"],
            ),
            "CKM_angles_and_phase": _package_entry(
                "STRUCTURAL_SOURCE_ONLY",
                None,
                False,
                ["CKM numerical closure", "CP numerical closure"],
            ),
            "CP_Jarlskog_invariants": _package_entry(
                "STRUCTURAL_SOURCE_ONLY",
                None,
                False,
                ["CP numerical closure"],
            ),
            "gauge_couplings": _package_entry(
                "OPEN",
                None,
                False,
                ["residual RG coefficients", "full scheme/common-scale alignment"],
            ),
            "sin2_theta_W": _package_entry(
                "OPEN",
                None,
                False,
                ["Higgs/electroweak absolute scale"],
            ),
            "W_Z_Higgs_scale": _package_entry(
                "OPEN",
                None,
                False,
                ["Higgs/electroweak absolute scale"],
            ),
            "open_boundary_parameters": _package_entry(
                "OPEN_LOCALIZABLE",
                "artifacts/universal_tau_sigma_response_scaffold_v1.json",
                False,
                ["boundary-derived tau/sigma", "boundary-derived chi"],
            ),
            "claim_status": _package_entry(
                "NUMERICAL_CLOSURE_OPEN",
                "artifacts/full_BHSM_claim_status_table_v2.json",
                False,
                ["final populated comparison-ready prediction package"],
            ),
            "forbidden_feedback": _package_entry(
                "GUARDED",
                "artifacts/forbidden_claim_audit_v2.json",
                False,
                [],
            ),
        },
    }


def transport_interface_artifact() -> Dict[str, object]:
    validation = validate_transport_config(
        {
            "mixed_pole_running_comparison_allowed": False,
            "transport_factors_fit_to_residuals": False,
            "observed_masses_used_as_derivation_inputs": False,
            "empirical_targets_used": False,
        }
    )
    return {
        "public_status": PUBLIC_STATUS,
        "official_predictions_changed": False,
        "audit": "common_scale_charged_transport_interface",
        "status": "IMPLEMENTED_CONDITIONAL",
        "empirical_targets_used": False,
        "observed_masses_used_as_derivation_inputs": False,
        "mixed_pole_running_comparison_allowed": False,
        "transport_factors_fit_to_residuals": False,
        "charged_precision_closure": "OPEN",
        "transport_formula": "y_f_i(mu_ref) = T_f_i(mu_ref,Lambda_BH) * Y_f_i(tau)",
        "same_sector_log_ratio_formula": "r_f,ij(mu_ref)=ln[y_f_i(mu_ref)/y_f_j(mu_ref)]",
        "config_validation": {
            "valid": validation.valid,
            "forbidden_keys_found": list(validation.forbidden_keys_found),
        },
        "decomposition_artifact": "artifacts/charged_transport_decomposition_template_v1.json",
        "target_schema_artifact": "artifacts/common_scale_charged_target_schema_v1.json",
        "prediction_package_skeleton": "artifacts/BHSM_prediction_package_skeleton_v1.json",
    }
