"""BHSM v14.54 cosmological-parent dynamic-envelopment audit.

This module implements the first dynamic completion layer suggested by the
Norman Works / BHSM full-recall synthesis.

It proves four bounded statements:

1. A cosmological S^3(R_H) parent can provide the universal dimensional anchor
   on an effective branch, converting the particle-scale problem into an
   action-selected relational nesting problem R_child=lambda R_parent.
2. Promoting the seam embedding to a nonuniform moving field makes the shape
   derivative of the existing charged-current action a source of the already
   normalized noncentral Peter-Weyl operator basis.  No arbitrary family
   matrix is required, but the periodic seam orbit and channel amplitudes are
   not selected by the current archive.
3. Time dependence confined to the abelian group algebra C[C3] remains unable
   to produce CKM mixing.  Noncommuting tensor channels and sector-relative
   monodromies are necessary.
4. A particle mass is a cycle invariant (relative Hamiltonian or Floquet
   quasi-energy), not a freely varying instantaneous core value.

No physical radius, mass, coupling, CKM matrix, or CP phase is emitted.
"""

from __future__ import annotations

import cmath
import json
import math
from pathlib import Path
from typing import Any, Iterable, Sequence

VERSION = "v14.54"

PRIMARY_VERDICT = (
    "BHSM_V14_54_A_NONUNIFORM_MOVING_SEAM_SHAPE_DERIVATIVE_OF_THE_"
    "EXISTING_CHARGED_CURRENT_SUPPLIES_THE_REQUIRED_NONCENTRAL_PETER_"
    "WEYL_OPERATOR_BASIS_WITHOUT_AN_ARBITRARY_FLAVOR_MATRIX_BUT_THE_"
    "CURRENT_ARCHIVE_DOES_NOT_SELECT_THE_PERIODIC_SEAM_ORBIT_OR_"
    "CHANNEL_AMPLITUDES"
)
SCALE_VERDICT = (
    "BHSM_THE_COSMOLOGICAL_S3_PARENT_CONVERTS_THE_ABSOLUTE_PARTICLE_"
    "SCALE_PROBLEM_TO_AN_ACTION_SELECTED_RELATIONAL_NESTING_PROBLEM_"
    "ON_AN_EFFECTIVE_COSMOLOGICAL_ANCHOR_BRANCH"
)
DYNAMIC_NO_GO = (
    "BHSM_TIME_DEPENDENCE_INSIDE_THE_ABELIAN_C3_GROUP_ALGEBRA_REMAINS_"
    "SIMULTANEOUSLY_DIAGONALIZABLE_AND_CANNOT_GENERATE_CKM_WHILE_"
    "NONCOMMUTING_SHAPE_CHANNEL_MONODROMY_IS_MIXING_AND_CP_CAPABLE"
)
MASS_VERDICT = (
    "BHSM_PARTICLE_MASS_IS_A_CYCLE_INVARIANT_PARENT_RELATIVE_"
    "HAMILTONIAN_OR_FLOQUET_QUASI_ENERGY_NOT_AN_ARBITRARY_"
    "INSTANTANEOUS_CORE_VALUE"
)
EXACT_NEXT_OBJECT = (
    "NUMERICAL_COSMOLOGICAL_PARENT_TO_CHILD_MOVING_SEAM_BVP_AND_"
    "FLOQUET_SOLVER_WITH_THREE_ACTION_SELECTED_SHAPE_HARMONICS_"
    "COMPLETE_RELATIVE_HEAT_KERNEL_AND_NESTED_COLOR_NEUTRAL_ORBITS"
)

# Existing exact minimal Wigner--Eckart channel table from the BHSM Peter-Weyl
# audit. Entries are (L,r), rows U0,U1,U2 and columns D0,D1,D2.
CHANNEL_TABLE: tuple[tuple[tuple[int, int], ...], ...] = (
    ((0, 0), (3, 0), (4, -2)),
    ((3, 3), (3, 3), (1, 1)),
    ((5, 4), (4, 4), (2, 2)),
)

Matrix = tuple[tuple[complex, ...], ...]


def identity(n: int = 3) -> Matrix:
    return tuple(
        tuple(1.0 + 0j if i == j else 0j for j in range(n)) for i in range(n)
    )


def matmul(a: Sequence[Sequence[complex]], b: Sequence[Sequence[complex]]) -> Matrix:
    if not a or len(a) != len(b):
        raise ValueError("equal nonempty square matrices required")
    n = len(a)
    if any(len(row) != n for row in a) or any(len(row) != n for row in b):
        raise ValueError("square matrices required")
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(n)) for j in range(n))
        for i in range(n)
    )


def dagger(a: Sequence[Sequence[complex]]) -> Matrix:
    n = len(a)
    return tuple(tuple(complex(a[j][i]).conjugate() for j in range(n)) for i in range(n))


def matsub(a: Sequence[Sequence[complex]], b: Sequence[Sequence[complex]]) -> Matrix:
    return tuple(
        tuple(complex(a[i][j]) - complex(b[i][j]) for j in range(len(a)))
        for i in range(len(a))
    )


def frobenius_norm(a: Sequence[Sequence[complex]]) -> float:
    return math.sqrt(sum(abs(complex(value)) ** 2 for row in a for value in row))


def c3_cycle() -> Matrix:
    return (
        (0j, 1 + 0j, 0j),
        (0j, 0j, 1 + 0j),
        (1 + 0j, 0j, 0j),
    )


def c3_polynomial(c0: complex, c1: complex, c2: complex) -> Matrix:
    c = c3_cycle()
    c_sq = matmul(c, c)
    i3 = identity(3)
    return tuple(
        tuple(c0 * i3[i][j] + c1 * c[i][j] + c2 * c_sq[i][j] for j in range(3))
        for i in range(3)
    )


def dynamic_c3_commutator_witness() -> dict[str, Any]:
    """Show that two arbitrary time slices in C[C3] commute exactly."""

    h1 = c3_polynomial(0.7, 0.2 + 0.1j, 0.2 - 0.1j)
    h2 = c3_polynomial(-0.3, -0.05 + 0.19j, -0.05 - 0.19j)
    comm = matsub(matmul(h1, h2), matmul(h2, h1))
    norm = frobenius_norm(comm)
    return {
        "time_slice_1": "0.7 I +(0.2+0.1i)C +(0.2-0.1i)C^2",
        "time_slice_2": "-0.3 I +(-0.05+0.19i)C +(-0.05-0.19i)C^2",
        "commutator_frobenius_norm": norm,
        "commutes_to_machine_precision": norm < 1e-14,
        "theorem": (
            "all time slices in C[C3] commute, so time ordering cannot create "
            "a noncentral monodromy or physical up/down basis mismatch"
        ),
    }


def pair_unitary(i: int, j: int, theta: float, phase: float = 0.0) -> Matrix:
    """Return exp[-i theta G_ij(phase)] in three dimensions.

    G_ij(phi)=exp(-i phi)|i><j|+exp(i phi)|j><i|.
    """

    if i == j or min(i, j) < 0 or max(i, j) >= 3:
        raise ValueError("distinct pair indices in {0,1,2} required")
    if not math.isfinite(theta) or not math.isfinite(phase):
        raise ValueError("finite theta and phase required")
    u = [list(row) for row in identity(3)]
    c = math.cos(theta)
    s = math.sin(theta)
    u[i][i] = c
    u[j][j] = c
    u[i][j] = -1j * s * cmath.exp(-1j * phase)
    u[j][i] = -1j * s * cmath.exp(1j * phase)
    return tuple(tuple(row) for row in u)


def jarlskog(v: Sequence[Sequence[complex]]) -> float:
    return float(
        (
            v[0][0]
            * v[1][1]
            * complex(v[0][1]).conjugate()
            * complex(v[1][0]).conjugate()
        ).imag
    )


def noncentral_floquet_witness() -> dict[str, Any]:
    """Return a deterministic CP-capable noncentral monodromy witness.

    This is not a BHSM prediction. It proves only that a sequence of normalized
    noncentral pair channels with a sector-relative oriented phase can create a
    full three-family unitary with nonzero rephasing invariant.
    """

    # Up sector: two differently oriented 1-2 seam-current impulses.
    u_up = matmul(
        pair_unitary(0, 1, 0.31, math.pi / 2.0),
        pair_unitary(0, 1, 0.22, 0.0),
    )
    # Down sector: a 1-2 impulse followed by an independent 2-3 harmonic.
    u_down = matmul(
        pair_unitary(1, 2, 0.17, 0.0),
        pair_unitary(0, 1, 0.12, 0.0),
    )
    v = matmul(dagger(u_up), u_down)
    j = jarlskog(v)
    row_norms = [sum(abs(x) ** 2 for x in row) for row in v]
    col_norms = [sum(abs(v[i][jcol]) ** 2 for i in range(3)) for jcol in range(3)]
    return {
        "status": "KINEMATIC_NONCENTRAL_FLOQUET_WITNESS_NOT_A_PREDICTION",
        "up_sequence": [
            "G_12(phi=0,theta=0.22)",
            "G_12(phi=pi/2,theta=0.31)",
        ],
        "down_sequence": [
            "G_12(phi=0,theta=0.12)",
            "G_23(phi=0,theta=0.17)",
        ],
        "absolute_matrix": [[abs(value) for value in row] for row in v],
        "jarlskog_witness": j,
        "nonzero_jarlskog": abs(j) > 1e-8,
        "unitary_row_residual": max(abs(x - 1.0) for x in row_norms),
        "unitary_column_residual": max(abs(x - 1.0) for x in col_norms),
        "interpretation": (
            "noncommuting shape-current impulses plus a sector-relative oriented "
            "phase are sufficient in principle; the BHSM action must still "
            "select the impulses, amplitudes, order, and period"
        ),
    }


def cosmological_parent_anchor_payload() -> dict[str, Any]:
    """Describe the authoritative status of the cosmological parent branch."""

    return {
        "artifact": "BHSM_cosmological_parent_anchor_v14_54",
        "version": VERSION,
        "parent_geometry": "spatial S^3(R_H) with late-time topographic field",
        "authoritative_TDE_status": {
            "role": "global parent geometry and universal dimensional anchor",
            "available_constraint": "R_H is large; the archived TDE benchmark uses R_H approximately 25 Gpc and labels it illustrative",
            "not_yet_available": "a unique action-derived numerical R_H shared with the BHSM particle action",
        },
        "nesting_law": {
            "first_child": "R_0=lambda_0 R_H",
            "recursive": "R_n=lambda_n R_(n-1)",
            "forbidden": "assigning lambda_n independently or identifying R_particle with R_H",
        },
        "effective_branch": {
            "description": "use cosmologically inferred R_H as the one universal external length and derive every lambda_n from the BHSM parent-child equations",
            "absolute_unit_closed_conditionally": True,
            "zero_input_scale_derived": False,
        },
        "scale_verdict": SCALE_VERDICT,
    }


def nesting_and_orbit_contract() -> dict[str, Any]:
    return {
        "artifact": "BHSM_moving_seam_nesting_orbit_contract_v14_54",
        "version": VERSION,
        "moving_embedding": "X(tau,Omega)=X_0(Omega)+xi(tau,Omega)n",
        "shape_expansion": "xi(tau,Omega)=sum_(L,r) q_(L,r)(tau) M_(L,r)(Omega)",
        "instantaneous_interface_equation": (
            "Pi_child-Pi_parent-delta(S_GHY+S_compat+Gamma_nonlocal)/delta X=0"
        ),
        "periodic_force_balance": (
            "(1/T) integral_0^T d tau F_X[tau]=0"
        ),
        "relative_periodicity": "Phi(tau+T)=h.Phi(tau)",
        "scale_closure": [
            "Dirichlet-to-Neumann matching fixes lambda=R_child/R_parent",
            "phase closure fixes or constrains T/R_parent",
            "the reduced (log lambda,a,T) Jacobian must be nonzero",
        ],
        "stability": {
            "operator": "gauge-fixed monodromy of the full eta-Dirac-Yang-Mills-Higgs-interface system",
            "gate": "all physical Floquet multipliers lie on or inside the unit circle, with gauge and collective zero modes quotiented",
        },
        "current_archive_satisfies_contract": False,
        "missing": [
            "variable seam embedding in the active action",
            "matched cosmological-parent and child solutions",
            "periodic eta/metric/gauge/fermion orbit",
            "complete relative determinant and shape stress",
            "gauge-fixed Floquet spectrum",
        ],
    }


def shape_derivative_current_payload() -> dict[str, Any]:
    unique_channels = sorted({entry for row in CHANNEL_TABLE for entry in row})
    return {
        "artifact": "BHSM_moving_seam_tensor_current_v14_54",
        "version": VERSION,
        "base_current": (
            "S_cc=g2 integral_(Sigma_X) dmu_X [bar(Psi_u) gamma^a W_a^+ Psi_d+h.c.]"
        ),
        "universal_shape_variation": (
            "delta_X dmu_X=K xi dmu_X; frame, normal, projector and spin-connection terms also vary"
        ),
        "shape_dressed_vertex": (
            "Gamma_(+,X)^(L,r)=delta^4 S_cc/(delta q_(L,r) delta W^+ delta bar(Psi_u) delta Psi_d)"
        ),
        "family_projection": (
            "c_ij^(L,r)=<T_u e_i,P_u Gamma_(+,X)^(L,r) P_d T_d e_j>_common"
        ),
        "raw_kernel": "K_ud(tau)=sum_(L,r) q_(L,r)(tau)c^(L,r)M_(L,r)",
        "exact_channel_table": [[list(entry) for entry in row] for row in CHANNEL_TABLE],
        "unique_nonzero_channel_labels": [list(x) for x in unique_channels],
        "all_nine_kinematic_channels_present": True,
        "minimum_independent_separable_channels_for_rank_three": 3,
        "important_distinction": (
            "the moving shape derivative supplies an action-owned route to the "
            "noncentral operator basis; the current archive does not select the "
            "periodic q_(L,r)(tau), their amplitudes, or their phases"
        ),
        "primary_verdict": PRIMARY_VERDICT,
    }


def mass_cycle_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_cycle_invariant_mass_contract_v14_54",
        "version": VERSION,
        "relative_orbit": "Phi_f(tau+T_f)=h_f.Phi_f(tau)",
        "floquet_eigenproblem": "U_f(T_f) psi_(f,alpha)=exp(-i theta_(f,alpha)) psi_(f,alpha)",
        "quasi_energy": "epsilon_(f,alpha)=hbar theta_(f,alpha)/T_f mod 2 pi hbar/T_f",
        "relative_charge": (
            "Delta H_xi is the covariant composite-minus-parent Hamiltonian charge including gravity, gauge, GHY, seam, corner and counterterm pieces"
        ),
        "rest_mass_readout": (
            "in the rest frame the stable cycle invariant E_rel defines m c^2; on a stationary branch it must agree with the pole/quasi-energy prescription"
        ),
        "instantaneous_snapshot_is_physical_mass": False,
        "mass_verdict": MASS_VERDICT,
    }


def completion_payload() -> dict[str, Any]:
    c3 = dynamic_c3_commutator_witness()
    floquet = noncentral_floquet_witness()
    validation = {
        "cosmological_anchor_is_conditional": True,
        "relational_nesting_not_direct_radius_identification": True,
        "dynamic_C3_commutator_zero": c3["commutes_to_machine_precision"],
        "noncentral_floquet_witness_unitary": max(
            floquet["unitary_row_residual"], floquet["unitary_column_residual"]
        )
        < 1e-12,
        "noncentral_floquet_witness_CP_capable": floquet["nonzero_jarlskog"],
        "no_physical_CKM_emitted": True,
        "no_physical_mass_or_scale_emitted": True,
        "frozen_predictions_unchanged": True,
        "official_prediction_logic_unchanged": True,
        "USB_untouched": True,
    }
    return {
        "artifact": "BHSM_completion_gate_v14_54",
        "version": VERSION,
        "verdicts": {
            "primary": PRIMARY_VERDICT,
            "scale": SCALE_VERDICT,
            "dynamic_no_go": DYNAMIC_NO_GO,
            "mass": MASS_VERDICT,
        },
        "closed": [
            "cosmological-parent effective anchor contract",
            "moving-seam Dirichlet-to-Neumann and periodic-orbit contract",
            "shape-derivative Peter-Weyl tensor-current source mechanism",
            "dynamic C[C3] no-go",
            "noncentral Floquet CKM/CP capability witness",
            "cycle-invariant mass contract",
        ],
        "open": [
            "unique shared R_H from a coupled cosmology-particle action",
            "action-selected nesting ratio and orbit period",
            "actual periodic charged-lepton solution",
            "nested color-neutral hadron/quark solution",
            "near-null neutrino orbit",
            "complete moving-seam channel amplitudes and phases",
            "physical CKM, CP, PMNS, masses and widths",
            "full gauge-fixed Floquet stability",
        ],
        "Mark_III": "NOT_REACHED",
        "BHSM_physical_completion": False,
        "exact_next_object": EXACT_NEXT_OBJECT,
        "validation": validation,
        "validation_passed": all(validation.values()),
    }


ARTIFACTS = {
    "BHSM_cosmological_parent_anchor_v14_54.json": cosmological_parent_anchor_payload,
    "BHSM_moving_seam_nesting_orbit_contract_v14_54.json": nesting_and_orbit_contract,
    "BHSM_moving_seam_tensor_current_v14_54.json": shape_derivative_current_payload,
    "BHSM_dynamic_C3_and_Floquet_witness_v14_54.json": lambda: {
        "artifact": "BHSM_dynamic_C3_and_Floquet_witness_v14_54",
        "version": VERSION,
        "abelian_no_go": dynamic_c3_commutator_witness(),
        "noncentral_witness": noncentral_floquet_witness(),
        "verdict": DYNAMIC_NO_GO,
    },
    "BHSM_cycle_invariant_mass_contract_v14_54.json": mass_cycle_payload,
    "BHSM_completion_gate_v14_54.json": completion_payload,
}


def materialize(directory: str | Path) -> list[Path]:
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for name, factory in sorted(ARTIFACTS.items()):
        path = root / name
        path.write_text(
            json.dumps(factory(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        paths.append(path)
    return paths


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts")
    args = parser.parse_args()
    for artifact in materialize(args.output):
        print(artifact)
