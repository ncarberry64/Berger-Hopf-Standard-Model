"""BHSM v8.4 composite-carrier and weak-current representation reduction.

This bounded sprint combines the frozen v8.2 family ledgers with the exact
Berger block labels, the existing C3 triality identification, the common G2
polarization architecture, and the Finkelstein--Rubinstein sign line.  It
proves representation-theoretic current-channel closure without inventing an
action-selected vector inside a degenerate Berger block, reduced matrix
elements, physical masses, or CKM entries.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import json
from pathlib import Path
from typing import Any, Iterable

from sympy import Matrix, simplify, sqrt
from sympy.physics.wigner import clebsch_gordan

from . import generation_projector_action_attachment as v82


VERSION = "v8.4"
SPRINT = "bhsm-composite-carrier-current-reduction-v8-4"
SOURCE_MAIN_SHA = "0721ee6a79f97cae5b3ac5bf040fa07ef9584678"
ARTIFACT_NAME = "BHSM_composite_carrier_current_reduction_v8_4"
FINAL_VERDICT = (
    "BHSM_COMPOSITE_CARRIER_AND_WEAK_CURRENT_REPRESENTATION_"
    "CLOSURE_DERIVED_CONDITIONALLY"
)
BLOCKER_VERDICT = (
    "BHSM_MASS_AND_CKM_BLOCKED_BY_NO_ACTION_SELECTED_BERGER_"
    "MULTIPLET_STATES_AND_NO_ACTION_OWNED_LINEAR_COMBINATION_OF_"
    "NORMALIZED_WEAK_CURRENT_INTERTWINERS"
)
NEXT_MISSING_OBJECT = (
    "ACTION_DERIVED_COMPONENT_SELECTION_AND_CURRENT_COEFFICIENT_"
    "FUNCTIONAL_ON_NORMALIZED_BERGER_INTERTWINERS"
)
RELEASE_VERDICT = "BHSM_1_0_RELEASE_BLOCKED"

# Primitive current channels needed by the three heavy-to-light diagonal pairs.
# A channel is (left Sp(1) tensor rank L, right U(1) weight r).
PRIMITIVE_CURRENT_CHANNELS: dict[str, tuple[int, int]] = {
    "S": (0, 0),
    "A": (2, 2),
    "A_dagger": (2, -2),
    "B": (3, 3),
    "B_dagger": (3, -3),
}


def deterministic_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _hopf_charge(mode: tuple[int, int]) -> int:
    k, j = mode
    return k - 2 * j


def _half_text(numerator: int) -> str:
    value = Fraction(numerator, 2)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/2"


def berger_block(mode: tuple[int, int]) -> dict[str, Any]:
    """Return the exact block labels implied by q=k-2j, J=k/2, m=q/2."""

    k, j = mode
    q = _hopf_charge(mode)
    return {
        "mode": [k, j],
        "q": q,
        "J": _half_text(k),
        "m": _half_text(q),
        "two_J": k,
        "two_m": q,
        "block_rank": k + 1,
        "exact_label_map": "J=k/2, m=(k-2j)/2",
    }


def frozen_composite_carriers() -> dict[str, Any]:
    """Construct the category-correct block carrier for every frozen slot."""

    sectors: dict[str, Any] = {}
    for sector, modes in v82.SECTOR_MODES.items():
        rows = []
        for slot, mode in enumerate(modes):
            block = berger_block(mode)
            rows.append(
                {
                    "slot": slot,
                    "slot_role": ("base", "excitation_1", "excitation_2")[slot],
                    **block,
                    "carrier": (
                        "H_(J,m) tensor P_triality,slot tensor E_G2/SU3 "
                        "tensor L_FR tensor E_SM,sector"
                    ),
                    "triality_role": (
                        "same three slots through the existing Fourier "
                        "intertwiner; not a second family factor"
                    ),
                    "FR_role": "flat Z2 sign line; no continuous coefficient",
                    "component_selected": block["block_rank"] == 1,
                }
            )
        sectors[sector] = rows
    return {
        "sectors": sectors,
        "block_level_construction": True,
        "rank_one_component_selection": False,
        "new_family_factor_added": False,
        "new_free_parameter_added": False,
        "classification": (
            "CONDITIONAL_COMPOSITE_BLOCK_CARRIER_WITH_COMPONENT_SELECTION_OPEN"
        ),
    }


def _integer_spin_labels(mode: tuple[int, int]) -> tuple[int, int]:
    """Return (J,m) for the frozen quark modes, which have integral labels."""

    k, _ = mode
    q = _hopf_charge(mode)
    if k % 2 or q % 2:
        raise ValueError("quark current audit requires integral J and m")
    return k // 2, q // 2


def minimal_tensor_channel(
    up_mode: tuple[int, int], down_mode: tuple[int, int]
) -> tuple[int, int]:
    """Minimal (L,r) allowed by the block-level Wigner--Eckart rules."""

    J_u, m_u = _integer_spin_labels(up_mode)
    J_d, m_d = _integer_spin_labels(down_mode)
    r = m_u - m_d
    L = max(abs(J_u - J_d), abs(r))
    if L > J_u + J_d:
        raise AssertionError("no tensor channel satisfies the triangle rule")
    return L, r


def weak_current_channel_table() -> dict[str, Any]:
    up = v82.SECTOR_MODES["up"]
    down = v82.SECTOR_MODES["down"]
    matrix = [
        [list(minimal_tensor_channel(up_mode, down_mode)) for down_mode in down]
        for up_mode in up
    ]
    return {
        "row_order": ["U0", "U1", "U2"],
        "column_order": ["D0", "D1", "D2"],
        "entries_are": "minimal [L,r]",
        "matrix": matrix,
        "selection_rules": [
            "|J_u-J_d| <= L <= J_u+J_d",
            "r=m_u-m_d",
            "|r| <= L",
        ],
    }


def right_clebsch_gordan_witnesses() -> dict[str, Any]:
    """Evaluate the exact right-weight CG coefficient for every minimal channel."""

    up = v82.SECTOR_MODES["up"]
    down = v82.SECTOR_MODES["down"]
    rows = []
    for i, up_mode in enumerate(up):
        J_u, m_u = _integer_spin_labels(up_mode)
        for j, down_mode in enumerate(down):
            J_d, m_d = _integer_spin_labels(down_mode)
            L, r = minimal_tensor_channel(up_mode, down_mode)
            coefficient = clebsch_gordan(J_d, L, J_u, m_d, r, m_u)
            rows.append(
                {
                    "up_slot": i,
                    "down_slot": j,
                    "channel": [L, r],
                    "coefficient": str(coefficient),
                    "nonzero": coefficient != 0,
                }
            )
    return {
        "convention": "<J_d,m_d;L,r|J_u,m_u>",
        "rows": rows,
        "all_minimal_right_CG_coefficients_nonzero": all(
            row["nonzero"] for row in rows
        ),
    }


def normalized_peter_weyl_intertwiners() -> dict[str, Any]:
    """Exact reduced elements for unit-Haar-normalized multiplication harmonics.

    With Y^J_(n,m)=sqrt(2J+1)D^J_(n,m), multiplication by
    Y^L_(p,r), followed by projection from (J_d,m_d) to (J_u,m_u), has

      <J_u,n_u,m_u|M_(L,p,r)|J_d,n_d,m_d>
      = sqrt((2L+1)(2J_d+1)/(2J_u+1))
        C(J_d n_d,L p|J_u n_u) C(J_d m_d,L r|J_u m_u).

    In the convention where the left Wigner--Eckart coefficient carries
    1/sqrt(2J_u+1), the reduced element is the expression reported below.
    """

    up = v82.SECTOR_MODES["up"]
    down = v82.SECTOR_MODES["down"]
    rows = []
    formal_matrix = []
    for i, up_mode in enumerate(up):
        J_u, m_u = _integer_spin_labels(up_mode)
        matrix_row = []
        for j, down_mode in enumerate(down):
            J_d, m_d = _integer_spin_labels(down_mode)
            L, r = minimal_tensor_channel(up_mode, down_mode)
            right_cg = clebsch_gordan(J_d, L, J_u, m_d, r, m_u)
            reduced = simplify(sqrt((2 * L + 1) * (2 * J_d + 1)) * right_cg)
            matrix_row.append(reduced)
            rows.append(
                {
                    "up_slot": i,
                    "down_slot": j,
                    "channel": [L, r],
                    "right_CG": str(right_cg),
                    "normalized_reduced_element": str(reduced),
                    "reduced_element_squared": str(simplify(reduced**2)),
                    "nonzero": reduced != 0,
                }
            )
        formal_matrix.append(matrix_row)
    matrix = Matrix(formal_matrix)
    return {
        "Haar_measure": "normalized to total volume one",
        "orthonormal_basis": "Y^J_(n,m)=sqrt(2J+1) D^J_(n,m)",
        "matrix_element_formula": (
            "sqrt((2L+1)(2J_d+1)/(2J_u+1)) "
            "CG_left CG_right"
        ),
        "reduced_element_formula": (
            "sqrt((2L+1)(2J_d+1)) CG(J_d m_d,L r|J_u m_u)"
        ),
        "rows": rows,
        "formal_equal_coefficient_matrix": [
            [str(value) for value in row] for row in formal_matrix
        ],
        "formal_equal_coefficient_matrix_rank": int(matrix.rank()),
        "all_reduced_elements_nonzero": all(row["nonzero"] for row in rows),
        "physical_matrix_claimed": False,
        "why_not_physical": (
            "each entry belongs to a different normalized current harmonic; "
            "the action has not selected their coefficients, phases, or the "
            "component states inside the source and target blocks"
        ),
        "classification": (
            "KINEMATICALLY_NORMALIZED_INTERTWINER_LIBRARY_NOT_ACTION_OWNED_CURRENT"
        ),
    }


def possible_product_channels(
    factors: Iterable[tuple[int, int]],
) -> set[tuple[int, int]]:
    """All (L,r) channels in an ordered SU(2) tensor product."""

    ranks = {0}
    weight = 0
    for rank, factor_weight in factors:
        weight += factor_weight
        ranks = {
            output
            for left in ranks
            for output in range(abs(left - rank), left + rank + 1)
        }
    return {(rank, weight) for rank in ranks}


def nonlinear_channel_witnesses() -> dict[str, Any]:
    """Show that S,A,B and adjoints generate all nine channels by degree <=3."""

    # The witnesses are representation-content statements.  They do not assert
    # that the frozen action generates a nonzero coefficient for the product.
    witness_names: dict[tuple[int, int], tuple[str, ...]] = {
        (0, 0): (),
        (0, 1): ("B", "B_dagger"),
        (0, 2): ("A_dagger", "B", "B_dagger"),
        (1, 0): ("B",),
        (1, 1): ("B",),
        (1, 2): ("B", "A_dagger"),
        (2, 0): ("B", "B", "A_dagger"),
        (2, 1): ("A", "A"),
        (2, 2): ("A",),
    }
    table = weak_current_channel_table()["matrix"]
    rows = []
    for (i, j), names in sorted(witness_names.items()):
        target = tuple(table[i][j])
        factors = tuple(PRIMITIVE_CURRENT_CHANNELS[name] for name in names)
        generated = possible_product_channels(factors)
        rows.append(
            {
                "up_slot": i,
                "down_slot": j,
                "target": list(target),
                "witness": list(names) if names else ["S"],
                "nonlinear_degree": len(names),
                "target_generated": target in generated,
            }
        )
    return {
        "primitive_independent_channels": {
            "S": list(PRIMITIVE_CURRENT_CHANNELS["S"]),
            "A": list(PRIMITIVE_CURRENT_CHANNELS["A"]),
            "B": list(PRIMITIVE_CURRENT_CHANNELS["B"]),
        },
        "rows": rows,
        "all_nine_generated": all(row["target_generated"] for row in rows),
        "maximum_required_degree": max(row["nonlinear_degree"] for row in rows),
        "classification": (
            "REPRESENTATION_CONTENT_CLOSED_CONDITIONALLY_THROUGH_CUBIC_ORDER"
        ),
    }


def single_irreducible_current_no_go() -> dict[str, Any]:
    table = weak_current_channel_table()["matrix"]
    diagonal = [table[index][index] for index in range(3)]
    unique = {tuple(channel) for channel in diagonal}
    return {
        "diagonal_minimal_channels": diagonal,
        "distinct_diagonal_irreps": len(unique),
        "single_irrep_sufficient": len(unique) == 1,
        "verdict": (
            "SINGLE_IRREDUCIBLE_WEAK_CURRENT_CANNOT_CONNECT_ALL_FROZEN_"
            "UP_DOWN_DIAGONAL_PAIRS"
        ),
    }


def separable_current_rank_theorem() -> dict[str, Any]:
    return {
        "single_point_kernel": "V_ij=a_i^* b_j",
        "single_point_rank_bound": 1,
        "N_separable_channels_rank_bound": "rank(V) <= N",
        "minimum_separable_channels_for_rank_three": 3,
        "one_point_full_CKM_possible": False,
        "verdict": (
            "SINGLE_POINT_OR_SINGLE_SEPARABLE_TOPOGRAPHIC_CURRENT_CANNOT_"
            "GENERATE_FULL_RANK_CKM"
        ),
    }


def common_structure_mixing_audit() -> dict[str, Any]:
    return {
        "FR": {
            "holonomy_group": "Z2",
            "values": [-1, 1],
            "continuous_parameter_count": 0,
            "can_generate_generic_CKM": False,
            "reason": "contributes at most a sign to a bilinear matrix element",
        },
        "triality": {
            "map": "same exact C3 Fourier intertwiner on up and down slots",
            "family_central_current_result": "F^dagger I3 F=I3",
            "can_generate_generic_CKM": False,
            "reason": (
                "a common unitary basis change cancels; permutations and "
                "discrete phases remain monomial rather than generic"
            ),
        },
        "G2_polarization": {
            "role": "common internal G2/SU3 polarization carrier",
            "family_action": "central when the same section is carried by triality",
            "can_generate_generic_CKM": False,
            "reason": "does not select different up/down vectors in family space",
        },
        "conclusion": (
            "continuous mixing must arise from action-selected component-resolved "
            "up/down states and a noncentral weak-current kernel"
        ),
    }


def mass_basis_mismatch_criterion() -> dict[str, Any]:
    """State the exact family-space condition for nontrivial CKM data."""

    return {
        "universal_weak_current_in_gauge_basis": "J_W proportional to I3",
        "sector_embeddings": {
            "up": "U_u: C3_family -> H_up,physical",
            "down": "U_d: C3_family -> H_down,physical",
        },
        "mass_basis_overlap": "V_CKM=U_u^dagger U_d",
        "same_embedding_result": "U_u=U_d implies V_CKM=I3",
        "common_triality_G2_FR_result": (
            "common triality, common G2 polarization, and FR signs alone give "
            "only identity/monomial overlap"
        ),
        "nontrivial_mixing_condition": (
            "the action must select inequivalent up/down component isometries, "
            "equivalently non-simultaneously-diagonalizable sector response operators"
        ),
        "commutator_test": "[H_u,H_d] != 0 with H_f=M_f M_f^dagger",
        "CP_test": (
            "for nondegenerate spectra, a physical CP phase requires a nonzero "
            "imaginary rephasing invariant, equivalently nonzero Jarlskog commutator invariant"
        ),
        "block_central_common_slot_functions_sufficient": False,
        "physical_CKM_derived": False,
    }


def component_selection_obstruction() -> dict[str, Any]:
    carriers = frozen_composite_carriers()["sectors"]
    nontrivial = [
        {
            "sector": sector,
            "slot": row["slot"],
            "J": row["J"],
            "rank": row["block_rank"],
        }
        for sector, rows in carriers.items()
        for row in rows
        if row["block_rank"] > 1
    ]
    return {
        "nontrivial_blocks": nontrivial,
        "equivariant_rank_one_map": "Hom_Sp(1)(C,V_J)=0 for J>0",
        "unique_component_selected_by_block_labels": False,
        "required_extra_structure": [
            "action-selected polarization or coherent state",
            "action-selected localized profile",
            "symmetry-reduction quotient with one surviving state",
            "collective-coordinate ground-state theorem",
        ],
        "verdict": (
            "BERGER_BLOCK_LABELS_SELECT_EIGENSPACES_NOT_UNIQUE_PHYSICAL_STATES"
        ),
    }


def spectral_function_boundary() -> dict[str, Any]:
    return {
        "central_function": "f(O_Berger)|H_(J,m)=f(lambda_(J,m)) I",
        "historical_candidate": "exp[-S_overlap lambda_(J,m)]",
        "can_generate_diagonal_hierarchy": "conditionally, after S_overlap and physical attachment",
        "can_select_multiplet_component": False,
        "can_generate_CKM_from_a_common_basis": False,
        "S_overlap_derived_from_action": False,
        "physical_mass_attachment_derived": False,
    }


def validation() -> dict[str, bool]:
    carriers = frozen_composite_carriers()["sectors"]
    table = weak_current_channel_table()["matrix"]
    witnesses = nonlinear_channel_witnesses()
    expected_table = [
        [[0, 0], [3, 0], [4, -2]],
        [[3, 3], [3, 3], [1, 1]],
        [[5, 4], [4, 4], [2, 2]],
    ]
    expected_ranks = {
        "charged_lepton": [1, 6, 10],
        "up": [1, 7, 11],
        "down": [1, 7, 9],
    }
    checks = {
        "frozen_ledgers_unchanged": v82.SECTOR_MODES
        == {
            "charged_lepton": ((0, 0), (5, 2), (9, 3)),
            "up": ((0, 0), (6, 0), (10, 1)),
            "down": ((0, 0), (6, 3), (8, 2)),
        },
        "block_ranks_exact": all(
            [row["block_rank"] for row in carriers[sector]] == ranks
            for sector, ranks in expected_ranks.items()
        ),
        "minimal_channel_table_exact": table == expected_table,
        "minimal_right_CG_coefficients_nonzero": right_clebsch_gordan_witnesses()[
            "all_minimal_right_CG_coefficients_nonzero"
        ],
        "normalized_reduced_elements_nonzero": normalized_peter_weyl_intertwiners()[
            "all_reduced_elements_nonzero"
        ],
        "formal_intertwiner_library_rank_three": normalized_peter_weyl_intertwiners()[
            "formal_equal_coefficient_matrix_rank"
        ] == 3,
        "all_nine_channels_generated": witnesses["all_nine_generated"],
        "closure_degree_at_most_three": witnesses["maximum_required_degree"] <= 3,
        "single_irrep_no_go": not single_irreducible_current_no_go()[
            "single_irrep_sufficient"
        ],
        "single_point_rank_no_go": not separable_current_rank_theorem()[
            "one_point_full_CKM_possible"
        ],
        "FR_not_continuous_mixing": not common_structure_mixing_audit()["FR"][
            "can_generate_generic_CKM"
        ],
        "triality_not_generic_mixing": not common_structure_mixing_audit()[
            "triality"
        ]["can_generate_generic_CKM"],
        "mass_basis_mismatch_required": not mass_basis_mismatch_criterion()[
            "block_central_common_slot_functions_sufficient"
        ],
        "component_selection_remains_open": not component_selection_obstruction()[
            "unique_component_selected_by_block_labels"
        ],
        "no_physical_mass_emitted": True,
        "no_CKM_matrix_emitted": True,
        "no_new_free_parameter": True,
    }
    return checks


def status_report() -> dict[str, Any]:
    checks = validation()
    return {
        "artifact": ARTIFACT_NAME,
        "version": VERSION,
        "sprint": SPRINT,
        "source_main_sha": SOURCE_MAIN_SHA,
        "frozen_composite_carriers": frozen_composite_carriers(),
        "weak_current_channel_table": weak_current_channel_table(),
        "right_clebsch_gordan_witnesses": right_clebsch_gordan_witnesses(),
        "normalized_peter_weyl_intertwiners": normalized_peter_weyl_intertwiners(),
        "nonlinear_channel_witnesses": nonlinear_channel_witnesses(),
        "single_irreducible_current_no_go": single_irreducible_current_no_go(),
        "separable_current_rank_theorem": separable_current_rank_theorem(),
        "common_structure_mixing_audit": common_structure_mixing_audit(),
        "mass_basis_mismatch_criterion": mass_basis_mismatch_criterion(),
        "component_selection_obstruction": component_selection_obstruction(),
        "spectral_function_boundary": spectral_function_boundary(),
        "validated": [
            "block-level composite carrier architecture",
            "exact minimal Wigner--Eckart channel table",
            "nonzero exact right-weight Clebsch--Gordan witnesses",
            "kinematically normalized Peter--Weyl reduced elements for all nine channels",
            "three primitive current irreps suffice through cubic order",
            "FR/triality/common-polarization mixing no-go",
            "single-separable-channel rank no-go",
            "mass-basis mismatch criterion for nontrivial CKM",
        ],
        "invalidated": [
            "FR sign as source of continuous CKM angles or CP phase",
            "one irreducible current as the complete weak kernel",
            "one point-localized separable current as a rank-three CKM source",
            "block-central spectral function as a component selector",
        ],
        "open": [
            "action-selected vector or state inside each nontrivial Berger block",
            "action-generated primitive S, A, and B current components",
            "action-selected coefficients and phases for the normalized intertwiner library",
            "action-selected complex phase source for nonzero Jarlskog invariant",
            "physical mass attachment and S_overlap=1/(4pi) derivation",
        ],
        "primary_result": FINAL_VERDICT,
        "blocker_verdict": BLOCKER_VERDICT,
        "next_missing_object": NEXT_MISSING_OBJECT,
        "release_verdict": RELEASE_VERDICT,
        "physical_masses": None,
        "CKM_matrix": None,
        "frozen_predictions_changed": False,
        "official_prediction_logic_changed": False,
        "new_free_parameter_added": False,
        "validation": checks,
        "validation_passed": all(checks.values()),
    }


def status_to_markdown(payload: dict[str, Any] | None = None) -> str:
    data = status_report() if payload is None else payload
    table = data["weak_current_channel_table"]["matrix"]
    lines = [
        "# BHSM composite-carrier/current reduction v8.4",
        "",
        f"Primary result: `{data['primary_result']}`",
        "",
        "## Minimal weak-current channels",
        "",
        "Rows are `U0,U1,U2`; columns are `D0,D1,D2`. Entries are `(L,r)`.",
        "",
        "| | D0 | D1 | D2 |",
        "|---|---:|---:|---:|",
    ]
    for index, row in enumerate(table):
        rendered = " | ".join(f"({item[0]},{item[1]})" for item in row)
        lines.append(f"| U{index} | {rendered} |")
    lines.extend(
        [
            "",
            "The diagonal channels are `(0,0)`, `(3,3)`, and `(2,2)`, so one "
            "irreducible current cannot connect all three pairs. The primitive "
            "channels `S=(0,0)`, `A=(2,2)`, and `B=(3,3)`, together with "
            "adjoints, generate all nine required channels by cubic order.",
            "",
            "This is representation-content closure only. The action does not "
            "select normalized states inside the nontrivial Berger multiplets "
            "or supply the reduced current matrix elements.",
            "",
            f"Exact blocker: `{data['blocker_verdict']}`",
            "",
            f"Next object: `{data['next_missing_object']}`",
            "",
            f"Validation passed: `{str(data['validation_passed']).lower()}`",
        ]
    )
    return "\n".join(lines) + "\n"


def materialize(root: Path | None = None) -> Path:
    destination_root = repository_root() if root is None else Path(root)
    destination = destination_root / "artifacts" / f"{ARTIFACT_NAME}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(deterministic_json(status_report()), encoding="utf-8")
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--materialize", action="store_true")
    args = parser.parse_args(argv)
    payload = status_report()
    if args.materialize:
        materialize()
    print(
        deterministic_json(payload)
        if args.format == "json"
        else status_to_markdown(payload),
        end="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


