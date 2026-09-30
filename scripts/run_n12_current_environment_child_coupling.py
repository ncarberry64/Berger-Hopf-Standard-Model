"""Evaluate retained environmental source couplings on the current N12 path.

The canonical constant coexact source is normalized in proper time by the
existing source_profiles API. Its two commuting angular eigenchannels are
propagated through the existing inverse-free Weyl derivative API. Exact SM
hypercharges and the nine existing family projectors resolve sector couplings.
The gauge response remains family central. Intrinsic-Higgs lepton vertices and
the normalized quark family shapes are reported separately, without inserting
an unevaluated Higgs/HS bridge or deriving a new particle count.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
import sys
from typing import Any

import mpmath as mp
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from bhsm.interface.aether_rank16_u1_hs_vertex_matrices_v16_01 import source_profiles
from bhsm.interface.aether_hybrid_standard_model_bundle_v15_53 import yukawa_and_anomaly_ledger
from bhsm.interface.ae3_c2_coexact_hypercharge import lowest_weyl_coexact_hypercharge_source_jet
from bhsm.interface.ae3_c2_hopf_semigroup_transport import frozen_internal_semigroup_attachment
from bhsm.interface.ae3_family_harmonic_energy_pullback import MODE_ASSIGNMENTS, ROLE_ORDER, slot_projectors
from bhsm.interface.ae31_c2_intrinsic_m4_lepton_action import charged_lepton_yukawa_operator
from bhsm.interface.ae4_current_c2_factorized_hs_calderon import factorized_product_dirac_hs_weyl_jet

DEFAULT_PATH = ROOT / "artifacts/current_runtime/dop853_system_integration_current_finer/coefficient_path.npz"
DEFAULT_FIBERS = ROOT / "artifacts/action_extension/BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json"
DEFAULT_OUTPUT = ROOT / "artifacts/current_runtime/current_environment_child_coupling"


def _canonical(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return _canonical(value.tolist())
    if isinstance(value, np.generic):
        return _canonical(value.item())
    if isinstance(value, complex):
        return {"real": value.real, "imag": value.imag}
    if isinstance(value, dict):
        return {key: _canonical(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical(item) for item in value]
    return value


def _coefficient_path(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    with np.load(path, allow_pickle=False) as source:
        x = np.asarray(source["log_radius"], dtype=float)
        h = np.asarray(source["proper_durations"], dtype=float)
        tau = np.asarray(source["proper_times"], dtype=float)
    if (x.shape != (h.size + 1,) or tau.shape != x.shape or h.size < 1
            or not all(np.all(np.isfinite(value)) for value in (x, h, tau))
            or np.any(h <= 0) or np.any(np.diff(tau) <= 0)
            or not np.allclose(np.diff(tau), h, rtol=1e-12, atol=0)):
        raise ValueError("finite increasing proper-time coefficient path required")
    return x, h, tau


def _source_response(x: np.ndarray, h: np.ndarray, profile: np.ndarray, precision: int,
                     spectral_parameter: float) -> dict[str, Any]:
    """Apply the same commuting source law in its two angular eigenchannels."""
    responses = {}
    inverse = np.exp(-0.5 * (x[:-1] + x[1:]))
    for chirality, name in ((1, "plus"), (-1, "minus")):
        source_forms = lowest_weyl_coexact_hypercharge_source_jet(
            proper_durations=h, inverse_radii=inverse, source_profile=profile, chirality=chirality,
        )
        angular = {}
        for sigma_z in (1, -1):
            # The coexact API owns W(epsilon)=chi*(D+epsilon*p*sigma_z).
            # The factorized API accepts W=chi*D+epsilon*source_profile;
            # chi*sigma_z*p is exactly the same insertion on each eigenline.
            result = factorized_product_dirac_hs_weyl_jet(
                log_radii=x, proper_durations=h,
                dirac_eigenvalue_at_unit_radius=1.5, chirality=chirality,
                source_profile=chirality * sigma_z * profile,
                spectral_parameter=spectral_parameter, decimal_precision=precision,
                terminal_load=None,
            )
            angular[str(sigma_z)] = {
                "Weyl_birth_value": result["Weyl_birth_value"],
                "first_source_derivative": result["D_H_Weyl_birth"],
                "second_source_derivative": result["D2_H_Weyl_birth"],
                "first_source_derivative_decimal": result["D_H_Weyl_birth_decimal"],
                "second_source_derivative_decimal": result["D2_H_Weyl_birth_decimal"],
            }
        with mp.workdps(precision):
            first = mp.fsum(mp.mpf(row["first_source_derivative_decimal"]) for row in angular.values())
            second = mp.fsum(mp.mpf(row["second_source_derivative_decimal"]) for row in angular.values())
        responses[name] = {
            "chirality": chirality,
            "angular_eigenchannels": angular,
            "angular_trace_first_derivative": float(first),
            "angular_trace_second_derivative": float(second),
            "angular_trace_first_derivative_decimal": mp.nstr(first, n=precision),
            "angular_trace_second_derivative_decimal": mp.nstr(second, n=precision),
            "source_vertex_element_frobenius_norm": float(np.linalg.norm(source_forms["vertex_elements"])),
            "source_contact_element_frobenius_norm": float(np.linalg.norm(source_forms["contact_elements"])),
        }
        print(json.dumps({"stage": "coexact_source_response", "factor": name,
                          "first_trace": float(first), "second_trace": float(second)}), flush=True)
    return responses


def _family_rows(fibers_path: Path, responses: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    fibers = json.loads(fibers_path.read_text(encoding="utf-8"))["family_mode_C2_instantiation"]["rows"]
    if len(fibers) != 9 or len({(r["sector"], int(r["slot"])) for r in fibers}) != 9:
        raise ValueError("nine distinct existing charged-sector family fibers required")
    charges = {key: Fraction(value) for key, value in yukawa_and_anomaly_ledger()["charges"].items()}
    sector_charges = {"charged_lepton": (charges["L"], charges["e_c"], 1),
                      "up": (charges["Q"], charges["u_c"], 3),
                      "down": (charges["Q"], charges["d_c"], 3)}
    projectors = slot_projectors()
    yukawa = np.asarray(charged_lepton_yukawa_operator()["family_operator"], dtype=float)
    shapes = frozen_internal_semigroup_attachment()["sectors"]
    rows = []
    family_operators = {}
    for sector, (left, right, color) in sector_charges.items():
        square_weight = left * left + right * right
        family_operators[sector] = {
            "hypercharge_square_weight_per_LR_pair_exact": str(square_weight),
            "color_trace_hypercharge_square_weight_exact": str(color * square_weight),
            "factor_source_response_family_operators": {
                name: float(square_weight) * response["angular_trace_second_derivative"] * np.eye(3)
                for name, response in responses.items()
            },
        }
    for row in fibers:
        sector, slot = row["sector"], int(row["slot"])
        if sector not in sector_charges or not 0 <= slot < 3:
            raise ValueError("unknown existing charged-sector fiber")
        if tuple(row["mode_label"]) != MODE_ASSIGNMENTS[sector][slot]:
            raise ValueError("existing frozen mode/projector correspondence does not match")
        projector = projectors[slot]
        left, right, color = sector_charges[sector]
        internal = np.asarray(shapes[sector]["family_operator"], dtype=float)
        normalized_squared = float(np.trace(projector @ internal.T @ internal) / (internal[0, 0] ** 2))
        item = {
            "sector": sector, "slot": slot, "role": ROLE_ORDER[slot],
            "existing_mode_label": row["mode_label"], "existing_family_projector": projector,
            "hypercharges_exact": {"left": str(left), "right_conjugate": str(right)},
            "color_multiplicity": color,
            "hypercharge_square_weight_per_LR_pair_exact": str(left * left + right * right),
            "coexact_source_second_response_per_factor": {
                name: float(np.trace(projector @ value))
                for name, value in family_operators[sector]["factor_source_response_family_operators"].items()
            },
            "normalized_internal_family_response_squared_to_heavy": normalized_squared,
            "gauge_source_is_family_central": True,
        }
        if sector == "charged_lepton":
            item["intrinsic_Higgs_action_vertex"] = {
                "projected_Y_l": float(np.trace(projector @ yukawa)),
                "projected_Y_l_dagger_Y_l": float(np.trace(projector @ yukawa.T @ yukawa)),
                "source": "ae31_c2_intrinsic_m4_lepton_action.charged_lepton_yukawa_operator",
                "inserted_in_auxiliary_HS_Weyl_shift": False,
                "coupled_current_C2_LR_pole_or_energy_response_evaluated": False,
            }
        else:
            item["intrinsic_Higgs_action_vertex"] = {
                "absolute_Yukawa_normalization": None,
                "available_quantity": "EXISTING_SCALE_FREE_T_FAMILY_RESPONSE_ONLY",
                "normalization_owner": "SAME_ACTION_THIRD_VARIATION_c_u_OR_c_d",
                "lepton_prefactor_copied": False,
            }
        rows.append(item)
    return rows, family_operators


def evaluate_couplings(*, coefficient_path: Path, fibers: Path,
                       decimal_precision: int = 60, spectral_parameter: float = -1.0) -> dict[str, Any]:
    """Evaluate the source response at the caller's common resolvent parameter."""
    if decimal_precision < 50 or not np.isfinite(spectral_parameter) or spectral_parameter >= 0:
        raise ValueError("precision>=50 and a finite negative spectral parameter required")
    x, h, tau = _coefficient_path(coefficient_path)
    duration = float(h.sum())
    profile = np.asarray(source_profiles({"proper_times": 0.5 * (tau[:-1] + tau[1:]),
                                          "proper_duration": duration})["constant"], dtype=float)
    responses = _source_response(x, h, profile, decimal_precision, spectral_parameter)
    rows, operators = _family_rows(fibers, responses)
    source_norm_residual = abs(float(h @ (profile * profile)) - 1.0)
    commutator = max(float(np.linalg.norm(operator @ projector - projector @ operator))
                     for sector in operators.values()
                     for operator in sector["factor_source_response_family_operators"].values()
                     for projector in slot_projectors())
    return _canonical({
        "status": "CURRENT_N12_ENVIRONMENTAL_SOURCE_COUPLINGS_EVALUATED",
        "coefficient_path": str(coefficient_path.resolve()),
        "numerical_domain": {"node_count": x.size, "segment_count": h.size, "proper_duration": duration,
                             "spectral_parameter": spectral_parameter, "terminal_domain": "EXISTING_STOP_FRIEDRICHS_FINITE_CORE",
                             "external_source_center_E0": 0.0},
        "source": {"kind": "EXISTING_SPATIAL_COEXACT_U1_HYPERCHARGE",
                   "normalization": "p(tau)=1/sqrt(T);_integral_p_squared_d_tau=1",
                   "profile": profile, "profile_provider": "aether_rank16_u1_hs_vertex_matrices_v16_01.source_profiles",
                   "amplitude": "epsilon", "dimensionless_integrated_source_amplitude": "eta=epsilon*sqrt(T)",
                   "supplied_external_environment_amplitude": None},
        "factor_source_responses": responses, "family_source_response_operators": operators,
        "existing_fiber_couplings": rows,
        "numerical_residuals": {"constant_source_normalization": source_norm_residual,
                                "maximum_angular_first_trace_cancellation": max(abs(r["angular_trace_first_derivative"]) for r in responses.values()),
                                "maximum_family_projector_commutator": commutator,
                                "chiral_second_trace_difference": abs(responses["plus"]["angular_trace_second_derivative"] - responses["minus"]["angular_trace_second_derivative"])},
        "interpretation": {
            "source_response": "CONTINUOUS_CONORMAL_BOUNDARY_SUSCEPTIBILITY_ON_THE_RETAINED_NUMERICAL_PATH",
            "energy_stability_Hessian_or_lifetime_computed": False,
            "particle_count_derived": False, "input_fiber_count": len(rows),
            "generation_dependent_gauge_coupling_computed": False,
            "intrinsic_Higgs_identified_with_auxiliary_HS": False,
            "absolute_quark_Yukawa_prefactors_inserted": False,
            "environment_regime_threshold_inserted": False,
            "next_coupled_lepton_calculation": "INTRINSIC_HIGGS_LR_FIRST_ORDER_BLOCK_ON_THE_CURRENT_HISTORY_AND_ITS_DOMAIN",
        },
    })


def run(args: argparse.Namespace) -> dict[str, Any]:
    return evaluate_couplings(coefficient_path=args.coefficient_path, fibers=args.fibers,
                              decimal_precision=args.decimal_precision,
                              spectral_parameter=args.spectral_parameter)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coefficient-path", type=Path, default=DEFAULT_PATH)
    parser.add_argument("--fibers", type=Path, default=DEFAULT_FIBERS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--decimal-precision", type=int, default=60)
    parser.add_argument("--spectral-parameter", type=float, default=-1.0, help="common negative-axis resolvent parameter")
    args = parser.parse_args()
    if args.decimal_precision < 50 or not np.isfinite(args.spectral_parameter) or args.spectral_parameter >= 0:
        parser.error("at least fifty decimal digits and a finite negative spectral parameter required")
    payload = run(args)
    args.output.mkdir(parents=True, exist_ok=True)
    target = args.output / "report.json"
    target.write_text(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "report": str(target.resolve()),
                      "segment_count": payload["numerical_domain"]["segment_count"],
                      "proper_duration": payload["numerical_domain"]["proper_duration"],
                      "spectral_parameter": payload["numerical_domain"]["spectral_parameter"],
                      "residuals": payload["numerical_residuals"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
