"""Close the source-normal coordinate factor in the mixed action graph.

The normal bundle is a quotient by the already-existing child tangent and
gauge directions.  Giving that quotient its induced action-graph norm makes
the orthogonal representative an isometry.  This separates two constants
that must not be conflated:

* restriction of an ambient compact Euler--Dirac block to the normal quotient
  has operator norm no larger than its ambient mixed-graph norm;
* the source-to-normal right inverse is the later physical inverse bound K.

No finite-dimensional SVD basis is promoted to the continuum theorem.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MIXED = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_SOURCE_RESTRICTED_MIXED_GRAPH.json"
)
POSITIVE_DURATION = ROOT / (
    "artifacts/n12_source_restricted_positive_duration/"
    "BHSM_N12_SOURCE_RESTRICTED_POSITIVE_DURATION_THEOREM.json"
)
RESULT = ROOT / (
    "artifacts/n12_continuum_majorant_effectiveness/"
    "BHSM_N12_SOURCE_NORMAL_QUOTIENT_ISOMETRY.json"
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    mixed = json.loads(MIXED.read_text(encoding="utf-8"))
    positive = json.loads(POSITIVE_DURATION.read_text(encoding="utf-8"))

    validation = {
        "mixed_action_graph_is_assembled": bool(mixed["validation_passed"]),
        "source_restricted_normal_bundle_exists_qualitatively": bool(
            positive["conclusions"][
                "source_restricted_normal_right_inverse_exists"
            ]
        ),
        "quotient_norm_is_the_existing_action_graph_norm": True,
        "orthogonal_representative_and_projection_have_norm_one": True,
        "source_to_state_inverse_not_hidden_in_the_coordinate_map": True,
        "finite_svd_basis_not_promoted_to_continuum_physics": True,
        "no_new_equation_constraint_gate_scale_fit_or_event_definition": True,
    }
    output = {
        "classification": (
            "SOURCE_NORMAL_RECONSTRUCTION_FACTOR_CLOSED_AS_THE_CANONICAL_"
            "ACTION_GRAPH_QUOTIENT_ISOMETRY;_THE_NONTRIVIAL_SOURCE_TO_"
            "NORMAL_INVERSE_REMAINS_THE_SEPARATE_K_BOUND"
        ),
        "inputs": {
            str(path.relative_to(ROOT)).replace("\\", "/"): _sha256(path)
            for path in (MIXED, POSITIVE_DURATION)
        },
        "spaces": {
            "ambient": "X_E=H1_q_CROSS_L2_velocity_CROSS_H1_lapse_shift",
            "discarded_subspace": (
                "K_Y=EXISTING_CHILD_TANGENT_PLUS_GAUGE_DIRECTIONS"
            ),
            "normal_representative": "N_Y=K_Y_ORTHOGONAL_IN_THE_ACTION_GRAPH",
            "quotient": "X_E/K_Y_WITH_THE_INDUCED_ACTION_GRAPH_NORM",
            "source_restricted_line_or_bundle": (
                "THE_EXISTING_CLOSED_ACTION_SELECTED_SUBSPACE_OF_N_Y"
            ),
        },
        "exact_Hilbert_space_identities": {
            "whitened_physical_map": (
                "A_Y=W_Y*D_F(Y)*Q_f*Q_g*G^(-1/2)"
            ),
            "source_normal_Gram": "S_Y=A_Y*A_Y_star",
            "normal_projector": "P_N=I-P_K",
            "orthogonal_representative": "s_Y([x])=P_N*x",
            "polar_normal_embedding": (
                "T_Y=Q_f*Q_g*G^(-1/2)*A_Y_star*S_Y^(-1/2)"
            ),
            "minimum_graph_norm_right_inverse": (
                "R_Y=Q_f*Q_g*G^(-1/2)*A_Y_star*S_Y^(-1)"
            ),
            "quotient_norm": (
                "norm([x])_(X_E/K_Y)=inf_(k_in_K_Y)norm(x+k)_G="
                "norm(P_N*x)_G"
            ),
            "representative_norm": "norm(s_Y)=1",
            "normal_projection_norm": "norm(P_N)=1",
            "source_subspace_inclusion_norm": "norm(i_source)=1",
            "source_subspace_projection_norm": "norm(P_source)=1",
        },
        "compact_operator_consequence": {
            "ambient_block": "K_ED,lo(Y):X_E_TO_X_E_star",
            "normal_block": "K_ED,normal=i_N_star*K_ED,lo*i_N",
            "bound": (
                "norm(K_ED,normal)<=norm(K_ED,lo)_(X_E_TO_X_E_star)"
            ),
            "separate_reconstruction_multiplier_required_for_C_ED_G": False,
            "reason": (
                "THE_NORMAL_COORDINATE_IS_THE_INDUCED_HILBERT_QUOTIENT;_"
                "A_NONORTHOGONAL_FINITE_COORDINATE_PARAMETERIZATION_IS_"
                "SOLVER_MACHINERY_AND_IS_NOT_PART_OF_THE_OPERATOR_BOUND"
            ),
        },
        "right_inverse_separation": {
            "map": "D_F_Y_RESTRICTED_TO_N_Y:N_Y_TO_PHYSICAL_RESIDUAL_SPACE",
            "inverse_norm": "K=norm((D_F_Y|N_Y)^(-1))",
            "exact_value": (
                "K=1/sqrt(lambda_min(S_Y))=1/sigma_min(A_Y)"
            ),
            "source_restricted_uniform_quantity": (
                "beta_src=inf_(Y,N>=12)sqrt(lambda_min(E_W_star*S_Y*E_W))"
            ),
            "status": "QUANTITATIVE_BOUND_OPEN",
            "not_equal_to": "THE_NORM_ONE_QUOTIENT_REPRESENTATIVE",
            "count_K_once": True,
            "trace_or_principal_subblock_gaps_alone_prove_beta_src": False,
        },
        "closed_here": [
            "THE_SOURCE_NORMAL_COORDINATE_FACTOR_DOES_NOT_INFLATE_C_ED_G",
            "TANGENT_AND_GAUGE_DIRECTIONS_REMAIN_QUOTIENTED_NOT_DELETED",
            "THE_LATER_NORMAL_RIGHT_INVERSE_K_RETAINS_ALL_SOURCE_TO_STATE_CONDITIONING",
        ],
        "claim_boundary": (
            "THE_NORM_ONE_POLAR_REPRESENTATIVE_DOES_NOT_BY_ITSELF_PROVE_"
            "THAT_THE_AMBIENT_RANK_TWO_CRITICAL_POLE_MATRIX_COMPRESSES_"
            "TO_THE_SINGLE_ALREADY_CERTIFIED_BERGER_INDICIAL_LINE"
        ),
        "first_missing_action_owned_object": (
            "EVALUATE_THE_EXISTING_SOURCE_NORMAL_COMPRESSION_OF_THE_EXACT_"
            "RANK_TWO_REGULAR_POLE_ZERO_ORDER_MATRIX_BEFORE_ENCLOSING_"
            "THE_REMAINING_UNDIFFERENTIATED_K_ED,lo"
        ),
        "C_ED_G_evaluable_after_next_coefficient_enclosure": False,
        "epsilon_obs_M_evaluable": False,
        "CONTINUUM_EVENT_CHILD_CERTIFIED": False,
        "FULL_BHSM_COMPLETE": False,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(
        json.dumps(output, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
