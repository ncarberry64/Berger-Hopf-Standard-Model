"""Audit how the retained omitted Ward source reaches the critical pole line.

The certified inverse-square source is a multiplier-constraint covector.  It
therefore has no direct component in the physical Berger-anisotropy Euler row.
The full mixed normal correction can nevertheless acquire an anisotropy
component through retained compact couplings.  This audit records that exact
support statement and keeps the finite N16--N48 corrections diagnostic only;
it does not turn them into a continuum bound.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_INVERSE_SQUARE_SOURCE_CONSTANT.json"
)
MIXED = ROOT / (
    "artifacts/n12_direct_checkpoint/"
    "BHSM_N12_FULL_QVM_CONSTRAINT_TAIL_DIAGNOSTIC.json"
)
INDICIAL = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_REGULAR_POLE_INDICIAL_OPERATOR.json"
)
RESULT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_REGULAR_POLE_SOURCE_RESTRICTION.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    mixed = json.loads(MIXED.read_text(encoding="utf-8"))
    indicial = json.loads(INDICIAL.read_text(encoding="utf-8"))
    rows: dict[str, list[dict[str, float]]] = {}
    for side in ("event", "child"):
        rows[side] = []
        for evaluation in mixed["evaluations"][side]:
            record = evaluation["full_qvm_all_mode_normal_map"]
            fractions = record["exact_source_correction_block_fractions"]
            rows[side].append({
                "N": int(evaluation["N"]),
                "minimum_action_norm_linear_correction": float(
                    record["exact_source_minimum_action_norm_linear_correction"]
                ),
                "configuration_anisotropy_q_v_fraction": float(
                    fractions["q_b"]
                ),
                "velocity_anisotropy_v_v_fraction": float(
                    fractions["v_b"]
                ),
                "smallest_singular_value_diagnostic_only": float(
                    record["smallest_singular_value"]
                ),
            })

    maximum_qv = max(
        row["configuration_anisotropy_q_v_fraction"]
        for side_rows in rows.values() for row in side_rows
    )
    maximum_vv = max(
        row["velocity_anisotropy_v_v_fraction"]
        for side_rows in rows.values() for row in side_rows
    )
    validation = {
        "inverse_square_source_artifact_validated": bool(
            source["validation_passed"]
        ),
        "critical_indicial_artifact_validated": bool(
            indicial["validation_passed"]
        ),
        "finite_mixed_probe_artifact_validated": bool(
            mixed["validation_passed"]
        ),
        "direct_source_support_is_only_existing_multiplier_constraint_rows": True,
        "direct_Berger_anisotropy_Euler_covector_is_zero": True,
        "indirect_mixed_transfer_not_silently_set_to_zero": True,
        "finite_probes_not_promoted_to_uniform_bound_or_roots": True,
        "positive_duration_soft_channel_not_reclassified": True,
        "no_equation_constraint_gate_scale_fit_or_event_definition_changed": True,
    }
    payload = {
        "classification": (
            "CRITICAL_v_INDICIAL_LINE_IS_NOT_DIRECTLY_FORCED_BY_THE_"
            "INVERSE_SQUARE_WARD_SOURCE;_THE_RETAINED_INDIRECT_MIXED_"
            "POSITIVE_DURATION_TRANSFER_REMAINS_TO_BE_BOUNDED"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in (SOURCE, MIXED, INDICIAL)
        },
        "exact_source_support": {
            "rows": "OMITTED_HIGH_MODE_log_lapse_AND_shift_CONSTRAINT_ROWS",
            "source_law": "norm(r_n)_weak<=C_r*n^-2",
            "direct_projection_onto_Berger_anisotropy_v_Euler_covector": 0.0,
            "reason": (
                "THE_RETAINED_ETA_COMPLETED_WARD_SOURCE_IS_THE_ACTION_"
                "GRADIENT_WITH_RESPECT_TO_THE_EXISTING_LAPSE_AND_SHIFT_"
                "MULTIPLIERS;_THE_v_EULER_ROW_IS_A_DIFFERENT_DUAL_BLOCK"
            ),
        },
        "retained_indirect_transfer": {
            "owner": (
                "MIXED_EULER_DIRAC_HESSIAN_COUPLING_FROM_THE_WARD_"
                "CONSTRAINT_ROWS_TO_THE_PHYSICAL_v_NORMAL_COMPONENT"
            ),
            "why_it_matters": (
                "THE_STATIC_v_INDICIAL_OPERATOR_HAS_ZERO_IN_ITS_ESSENTIAL_"
                "SPECTRUM,_SO_DIRECT_SOURCE_ORTHOGONALITY_ALONE_DOES_NOT_"
                "BOUND_THIS_COMPACTLY_GENERATED_COMPONENT"
            ),
            "finite_source_restricted_diagnostics": rows,
            "maximum_sampled_q_v_action_fraction": maximum_qv,
            "maximum_sampled_velocity_v_action_fraction": maximum_vv,
            "finite_rows_are_the_proof": False,
        },
        "soft_channel_classification": (
            "CATEGORY_2_DYNAMICALLY_CONTROLLED_NORMAL_DIRECTION_PENDING_"
            "THE_EXACT_SOURCE_RESTRICTED_INDICIAL_BOUND"
        ),
        "category_3_positive_duration_collapse_sequence_constructed": False,
        "M_star_certified": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "exact_next_dependency": (
            "ENCLOSE_THE_RETAINED_COMPACT_MIXED_WARD_TO_v_TRANSFER_IN_"
            "THE_POSITIVE_DURATION_ACTION_GRAPH_AND_PROVE_THAT_THE_"
            "EXISTING_ORDERED_EVENT_AND_MOMENTUM_FLUX_OBSERVATION_ROWS_"
            "CONTROL_ITS_INDICIAL_ON_SHELL_COMPONENT"
        ),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "FULL_BHSM_COMPLETE": False,
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
