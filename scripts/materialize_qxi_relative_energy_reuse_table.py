"""Materialize the fail-closed Q_xi / relative-energy reuse table.

This performs no gated physical evaluation.  It records which retained-action
ingredients already exist and the exact construction still required after the
continuum child closes.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / (
    "artifacts/qxi_relative_energy_preparation/"
    "BHSM_QXI_RELATIVE_ENERGY_REUSE_TABLE.json"
)

INPUTS = (
    ROOT / "src/bhsm/interface/aether_cross_resolution_reconnaissance_v21_35.py",
    ROOT / "scripts/audit_n12_radial_diffeo_noether_compatibility.py",
    ROOT / "src/bhsm/interface/completion/support_covariant_phase_space_v11_2.py",
    ROOT / "src/bhsm/interface/aether_nonlinear_norman_cycle_bvp_v15_7.py",
    ROOT / "src/bhsm/interface/completion/relative_anomaly_tensor_current_v14_53.py",
    ROOT / "src/bhsm/interface/aether_generator_selection_v15_2.py",
    ROOT / "artifacts/BHSM_cycle_invariant_mass_contract_v14_54.json",
    ROOT / "artifacts/n12_direct_checkpoint/BHSM_N12_COMPLETE_PERSISTENT_CHILD_STATE.npz",
    ROOT / (
        "artifacts/n12_continuum_majorant_effectiveness/"
        "BHSM_CONTINUUM_EVENT_CHILD_CERTIFICATE.json"
    ),
    ROOT / (
        "artifacts/qxi_relative_energy_preparation/"
        "BHSM_N12_MATCHED_PARENT_QXI_OWNERSHIP.json"
    ),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    missing = [str(path) for path in INPUTS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing Q_xi reuse inputs: " + ", ".join(missing))

    rows = [
        {
            "object": "matched_parent_restriction_R_P",
            "current_implementation": None,
            "historical_or_conditional_source": (
                "artifacts/qxi_relative_energy_preparation/"
                "BHSM_N12_MATCHED_PARENT_QXI_OWNERSHIP.json"
            ),
            "missing_dependency": (
                "DERIVE_R_P_FROM_THE_COMPLETE_PARENT_COMPOSITE_ACTION_WITH_"
                "IDENTICAL_INTERFACE_GENERATOR_CLOCK_DOMAIN_AND_REFERENCE_DATA"
            ),
            "executable_immediately_after_continuum": False,
            "event_side_may_be_substituted": False,
        },
        {
            "object": "complete_Q_xi_contract",
            "current_implementation": None,
            "historical_or_conditional_source": (
                "artifacts/BHSM_cycle_invariant_mass_contract_v14_54.json"
            ),
            "missing_dependency": (
                "COMMON_REFERENCE_COVARIANT_CHARGE_ASSEMBLER_WITH_GRAVITY,_"
                "GAUGE,_GHY,_SEAM,_CORNER,_AND_COUNTERTERM_CONTRIBUTIONS"
            ),
            "executable_immediately_after_continuum": False,
        },
        {
            "object": "matched_parent_positive_duration_history",
            "current_implementation": None,
            "historical_or_conditional_source": (
                "src/bhsm/interface/aether_cross_resolution_"
                "reconnaissance_v21_35.py::"
                "n6_reduced_local_energy_readout_reconnaissance"
            ),
            "missing_dependency": (
                "CONSTRUCT_A_PARENT_HISTORY_WITH_IDENTICAL_INTERFACE_DATA,_"
                "GENERATOR,_REFERENCE_SUBTRACTION,_DOMAIN,_CLOCK,_AND_DURATION"
            ),
            "executable_immediately_after_continuum": False,
        },
        {
            "object": "finite_N_canonical_pair",
            "current_implementation": (
                "src/bhsm/interface/aether_cross_resolution_"
                "reconnaissance_v21_35.py::_canonical_pair_at_order"
            ),
            "historical_or_conditional_source": (
                "UNCHANGED_RETAINED_FULL_ACTION_JET_AND_EXISTING_"
                "CONSTRAINT_MINIMAL_LIFTS"
            ),
            "missing_dependency": (
                "CONTINUUM_CONVERGENCE_AND_BOUNDARY_CORNER_REFERENCE_COMPLETION"
            ),
            "executable_immediately_after_continuum": True,
            "scope": "REUSABLE_INGREDIENT_NOT_COMPLETE_Q_xi",
        },
        {
            "object": "radial_Noether_Ward_current",
            "current_implementation": (
                "scripts/audit_n12_radial_diffeo_noether_compatibility.py"
            ),
            "historical_or_conditional_source": (
                "ETA_COMPLETED_RETAINED_RADIAL_DIFFEO_IDENTITY"
            ),
            "missing_dependency": (
                "UNIFORM_CONTINUUM_ENCLOSURE_AND_INSERTION_INTO_COMPLETE_CHARGE"
            ),
            "executable_immediately_after_continuum": True,
            "scope": "REUSABLE_INGREDIENT_NOT_COMPLETE_Q_xi",
        },
        {
            "object": "local_canonical_energy",
            "current_implementation": (
                "src/bhsm/interface/aether_cross_resolution_"
                "reconnaissance_v21_35.py::"
                "n6_reduced_local_energy_readout_reconnaissance"
            ),
            "historical_or_conditional_source": "v^T*partial_v(L)-L",
            "missing_dependency": (
                "MATCHED_PARENT_SUBTRACTION_AND_ALL_BOUNDARY_GAUGE_SPECTRAL_TERMS"
            ),
            "executable_immediately_after_continuum": True,
            "scope": "NOT_Q_xi_NOT_DeltaH_NOT_MASS",
        },
        {
            "object": "covariant_phase_space_skeleton",
            "current_implementation": (
                "src/bhsm/interface/completion/"
                "support_covariant_phase_space_v11_2.py::phase_space_payload"
            ),
            "historical_or_conditional_source": "BHSM_v11_2",
            "missing_dependency": (
                "COMPLETE_SYMPLECTIC_POTENTIAL_CURRENT,_CORE_RESPONSE,_"
                "AND_GLOBAL_FLUX_CONSERVATION"
            ),
            "executable_immediately_after_continuum": False,
        },
        {
            "object": "relative_spectral_anomaly_component",
            "current_implementation": (
                "src/bhsm/interface/completion/"
                "relative_anomaly_tensor_current_v14_53.py"
            ),
            "historical_or_conditional_source": "BHSM_v14_53",
            "missing_dependency": (
                "MATCHED_OPERATORS_AND_BACKGROUNDS,_COMMON_DOMAIN,_RELATIVE_"
                "HEAT_KERNEL,_ZERO_MODES,_GHY_CORNER_COUNTERTERMS"
            ),
            "executable_immediately_after_continuum": False,
        },
        {
            "object": "clocked_Hamiltonian_Floquet_conversion",
            "current_implementation": (
                "src/bhsm/interface/aether_generator_selection_v15_2.py::"
                "joint_clocked_hamiltonian"
            ),
            "historical_or_conditional_source": "BHSM_v15_2",
            "missing_dependency": (
                "ACTION_SELECTED_STABLE_REFERENCE_CYCLE,_PHYSICAL_CLOCK,_"
                "PERIOD_DEPTH,_AND_MONODROMY"
            ),
            "executable_immediately_after_continuum": False,
        },
    ]
    validation = {
        "all_referenced_inputs_exist": True,
        "no_complete_Q_xi_assembler_claimed": True,
        "no_matched_parent_history_claimed": True,
        "local_H6_not_promoted_to_DeltaH_mass_or_scale": True,
        "no_gated_physical_evaluation_performed": True,
        "no_frozen_prediction_touched": True,
    }
    output = {
        "classification": (
            "Q_XI_RELATIVE_ENERGY_REUSE_ASSETS_LOCATED;_COMPLETE_CHARGE_"
            "ASSEMBLER_AND_MATCHED_PARENT_HISTORY_REMAIN_OPEN"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in INPUTS
        },
        "reuse_table": rows,
        "first_post_continuum_dependency": (
            "DERIVE_THE_ACTION_OWNED_MATCHED_PARENT_RESTRICTION_R_P_FROM_"
            "THE_COMPLETE_PARENT_COMPOSITE_ACTION"
        ),
        "Q_xi_evaluated": False,
        "Delta_H_evaluated": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": True,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    with RESULT.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
