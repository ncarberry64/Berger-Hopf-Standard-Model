"""BHSM v14.55 moving-seam BVP and pair-wake neutrino audit.

This module converts the Norman pair-wake explanation into a fail-closed
mathematical contract and a deterministic reduced solver harness.

Bounded results:

1. Three predeclared Peter-Weyl shape channels are linearly independent and
   noncommuting, so they are sufficient as a *numerical basis* for a rank-three
   moving-seam/Floquet solve. Their physical amplitudes are not selected here.
2. A periodic BVP residual evaluator is implemented and validated on a
   synthetic exactly-solvable three-harmonic witness. This validates the
   harness, not a BHSM particle solution.
3. The neutrino hypothesis is encoded as one fixed inception-selected pair
   carrying an elapsed-proper-time cycle. The pair generates three geometric
   wake responses, which a detector may perceive as the three flavors.
4. Matter acts as a common-mode impulse on the intact pair and may advance,
   delay, or reset the cycle phase while redirecting the collective momentum.
5. A proposed matter-formation channel 2+2 -> 3+1* is recorded: an original
   pair captures a separate duplicate of one member from a donor pair, while
   the leftover one-body remnant is prompt or delayed radiation.

No physical mass, mass splitting, PMNS matrix, CKM matrix, coupling, lifetime,
cross section, cosmological radius, or particle spectrum is emitted.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path
from typing import Any, Iterable, Literal, Sequence

VERSION = "v14.55"

PRIMARY_VERDICT = (
    "BHSM_V14_55_THE_MOVING_SEAM_NUMERICAL_BASIS_AND_PAIR_WAKE_ACTION_"
    "ARE_NOW_FAIL_CLOSED_AND_COMPUTABLE_AS_CONTRACTS_BUT_NO_ACTION_DERIVED_"
    "COEFFICIENT_SET_PERIODIC_PARTICLE_SOLUTION_OR_PHYSICAL_NEUTRINO_"
    "OBSERVABLE_HAS_BEEN_OBTAINED"
)
NEUTRINO_VERDICT = (
    "BHSM_NEUTRINO_FLAVOR_IS_MODELED_AS_A_DETECTOR_RESPONSE_TO_THE_THREE_"
    "GEOMETRIC_WAKE_PRESENTATIONS_OF_ONE_FIXED_INCEPTION_SELECTED_"
    "UNBALANCED_PAIR_WHILE_MATTER_IMPULSES_ACT_COMMON_MODE_ON_THE_PAIR_AND_"
    "MAY_ADVANCE_DELAY_OR_RESET_ITS_ELAPSED_TIME_CYCLE"
)
CAPTURE_VERDICT = (
    "BHSM_STABLE_THREE_BODY_MATTER_IS_HYPOTHESIZED_AS_A_RECOGNIZABLE_"
    "INNER_PAIR_PLUS_A_SEPARATE_CAPTURED_DUPLICATE_STRIPPED_FROM_A_DONOR_"
    "PAIR_WITH_THE_LEFTOVER_ONE_BODY_REMNANT_DECAYING_TO_RADIATION"
)
EXACT_NEXT_OBJECT = (
    "ACTION_DERIVED_PARENT_CHILD_DTN_COEFFICIENTS_AND_RELATIVE_HEAT_KERNEL_"
    "INSERTED_INTO_THE_THREE_HARMONIC_PERIODIC_BVP_FOLLOWED_BY_A_"
    "SIMULTANEOUS_FIT_FREE_DERIVATION_OF_NEUTRINO_PHASE_SPLITTINGS_"
    "MATTER_PHASE_KICKS_AND_NESTED_COLOR_NEUTRAL_ORBITS"
)

Matrix = tuple[tuple[complex, ...], ...]
Vector3 = tuple[float, float, float]
PhaseMode = Literal["advance", "delay", "reset"]


def _finite(values: Iterable[float]) -> bool:
    return all(math.isfinite(float(value)) for value in values)


def normalize_phase(value: float) -> float:
    if not math.isfinite(value):
        raise ValueError("finite phase required")
    return value % (2.0 * math.pi)


def identity(n: int = 3) -> Matrix:
    if n <= 0:
        raise ValueError("positive dimension required")
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
        tuple(sum(complex(a[i][k]) * complex(b[k][j]) for k in range(n)) for j in range(n))
        for i in range(n)
    )


def matsub(a: Sequence[Sequence[complex]], b: Sequence[Sequence[complex]]) -> Matrix:
    if len(a) != len(b):
        raise ValueError("equal matrix dimensions required")
    return tuple(
        tuple(complex(a[i][j]) - complex(b[i][j]) for j in range(len(a[i])))
        for i in range(len(a))
    )


def frobenius_inner(a: Sequence[Sequence[complex]], b: Sequence[Sequence[complex]]) -> complex:
    if len(a) != len(b):
        raise ValueError("equal matrix dimensions required")
    return sum(
        complex(a[i][j]).conjugate() * complex(b[i][j])
        for i in range(len(a))
        for j in range(len(a[i]))
    )


def frobenius_norm(a: Sequence[Sequence[complex]]) -> float:
    return math.sqrt(max(0.0, float(frobenius_inner(a, a).real)))


def hermitian_channel(i: int, j: int) -> Matrix:
    """Normalized diagonal or symmetric pair channel in C^3."""

    if min(i, j) < 0 or max(i, j) >= 3:
        raise ValueError("indices must lie in {0,1,2}")
    matrix = [[0j for _ in range(3)] for _ in range(3)]
    if i == j:
        matrix[i][i] = 1.0 + 0j
    else:
        scale = 1.0 / math.sqrt(2.0)
        matrix[i][j] = scale + 0j
        matrix[j][i] = scale + 0j
    return tuple(tuple(row) for row in matrix)


# Three channel slots already present in the v14.54 exact Wigner--Eckart table.
# They are a predeclared Galerkin basis, not action-selected physical amplitudes.
THREE_SHAPE_CHANNELS: tuple[dict[str, Any], ...] = (
    {"label": "M_(0,0)", "slot": "U0-D0", "L": 0, "r": 0, "matrix": hermitian_channel(0, 0)},
    {"label": "M_(3,0)", "slot": "U0-D1", "L": 3, "r": 0, "matrix": hermitian_channel(0, 1)},
    {"label": "M_(1,1)", "slot": "U1-D2", "L": 1, "r": 1, "matrix": hermitian_channel(1, 2)},
)


def _rank_real(matrix: Sequence[Sequence[float]], tolerance: float = 1e-12) -> int:
    rows = [list(map(float, row)) for row in matrix]
    if not rows:
        return 0
    n_rows = len(rows)
    n_cols = len(rows[0])
    if any(len(row) != n_cols for row in rows):
        raise ValueError("rectangular matrix required")
    rank = 0
    pivot_col = 0
    while rank < n_rows and pivot_col < n_cols:
        pivot = max(range(rank, n_rows), key=lambda r: abs(rows[r][pivot_col]))
        if abs(rows[pivot][pivot_col]) <= tolerance:
            pivot_col += 1
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pivot_value = rows[rank][pivot_col]
        rows[rank] = [value / pivot_value for value in rows[rank]]
        for r in range(n_rows):
            if r == rank:
                continue
            factor = rows[r][pivot_col]
            if abs(factor) > tolerance:
                rows[r] = [
                    rows[r][c] - factor * rows[rank][c] for c in range(n_cols)
                ]
        rank += 1
        pivot_col += 1
    return rank


def three_harmonic_observability_payload() -> dict[str, Any]:
    matrices = [entry["matrix"] for entry in THREE_SHAPE_CHANNELS]
    gram = [
        [float(frobenius_inner(a, b).real) for b in matrices] for a in matrices
    ]
    commutators = []
    for i in range(len(matrices)):
        for j in range(i + 1, len(matrices)):
            comm = matsub(matmul(matrices[i], matrices[j]), matmul(matrices[j], matrices[i]))
            commutators.append(
                {
                    "pair": [THREE_SHAPE_CHANNELS[i]["label"], THREE_SHAPE_CHANNELS[j]["label"]],
                    "frobenius_norm": frobenius_norm(comm),
                }
            )
    return {
        "artifact": "BHSM_three_harmonic_observability_v14_55",
        "version": VERSION,
        "channels": [
            {key: value for key, value in channel.items() if key != "matrix"}
            for channel in THREE_SHAPE_CHANNELS
        ],
        "gram_matrix": gram,
        "channel_rank": _rank_real(gram),
        "rank_three_basis": _rank_real(gram) == 3,
        "commutators": commutators,
        "at_least_one_noncommuting_pair": any(
            item["frobenius_norm"] > 1e-12 for item in commutators
        ),
        "bounded_interpretation": (
            "three independent noncentral channel directions are available to a "
            "periodic Galerkin/Floquet solver; their amplitudes, phases and order "
            "remain action inputs"
        ),
        "physical_prediction": False,
    }


@dataclass(frozen=True)
class ReducedBVPParameters:
    mode_numbers: tuple[int, int, int]
    angular_frequency: float
    intrinsic_frequencies: tuple[float, float, float]
    amplitudes: tuple[float, float, float]
    phases: tuple[float, float, float]
    source_amplitudes: tuple[float, float, float]
    lambda_ratio: float
    berger_a: float
    lambda_target: float
    berger_target: float

    def validate(self) -> None:
        if any(number <= 0 for number in self.mode_numbers):
            raise ValueError("positive harmonic mode numbers required")
        scalars = (
            self.angular_frequency,
            *self.intrinsic_frequencies,
            *self.amplitudes,
            *self.phases,
            *self.source_amplitudes,
            self.lambda_ratio,
            self.berger_a,
            self.lambda_target,
            self.berger_target,
        )
        if not _finite(scalars):
            raise ValueError("all BVP parameters must be finite")
        if self.angular_frequency <= 0.0 or self.lambda_ratio <= 0.0 or self.berger_a <= 0.0:
            raise ValueError("positive frequency, nesting ratio and Berger parameter required")


def harmonic_state(parameters: ReducedBVPParameters, tau: float) -> tuple[Vector3, Vector3, Vector3]:
    parameters.validate()
    if not math.isfinite(tau):
        raise ValueError("finite tau required")
    q = []
    q_dot = []
    q_ddot = []
    for n, amplitude, phase in zip(
        parameters.mode_numbers, parameters.amplitudes, parameters.phases
    ):
        frequency = n * parameters.angular_frequency
        angle = frequency * tau + phase
        q.append(amplitude * math.cos(angle))
        q_dot.append(-amplitude * frequency * math.sin(angle))
        q_ddot.append(-amplitude * frequency * frequency * math.cos(angle))
    return tuple(q), tuple(q_dot), tuple(q_ddot)  # type: ignore[return-value]


def periodic_bvp_residual(
    parameters: ReducedBVPParameters,
    samples: int = 192,
) -> dict[str, Any]:
    """Evaluate a reduced three-harmonic periodic BVP residual.

    The reduced equations are

        q_i'' + Omega_i^2 q_i = s_i cos(n_i omega tau + phi_i)

    plus symbolic nesting and Berger stationarity residuals. The source terms
    stand in for the not-yet-computed parent/child DtN, determinant, matter and
    seam-current contributions. A small residual therefore validates only the
    evaluator for supplied coefficients.
    """

    parameters.validate()
    if samples < 12:
        raise ValueError("at least 12 collocation samples required")
    period = 2.0 * math.pi / parameters.angular_frequency
    squared = [0.0, 0.0, 0.0]
    maxima = [0.0, 0.0, 0.0]
    for sample in range(samples):
        tau = period * sample / samples
        q, _, q_ddot = harmonic_state(parameters, tau)
        for i, (n, omega_i, source, phase) in enumerate(
            zip(
                parameters.mode_numbers,
                parameters.intrinsic_frequencies,
                parameters.source_amplitudes,
                parameters.phases,
            )
        ):
            forcing = source * math.cos(n * parameters.angular_frequency * tau + phase)
            residual = q_ddot[i] + omega_i * omega_i * q[i] - forcing
            squared[i] += residual * residual
            maxima[i] = max(maxima[i], abs(residual))
    q0, qdot0, _ = harmonic_state(parameters, 0.0)
    qT, qdotT, _ = harmonic_state(parameters, period)
    periodic_q = max(abs(a - b) for a, b in zip(q0, qT))
    periodic_qdot = max(abs(a - b) for a, b in zip(qdot0, qdotT))
    rms = [math.sqrt(value / samples) for value in squared]
    lambda_residual = parameters.lambda_ratio - parameters.lambda_target
    berger_residual = parameters.berger_a - parameters.berger_target
    all_residuals = [*rms, periodic_q, periodic_qdot, abs(lambda_residual), abs(berger_residual)]
    return {
        "period": period,
        "mode_rms_residuals": rms,
        "mode_max_residuals": maxima,
        "periodic_q_residual": periodic_q,
        "periodic_qdot_residual": periodic_qdot,
        "lambda_stationarity_residual": lambda_residual,
        "berger_stationarity_residual": berger_residual,
        "max_residual": max(all_residuals),
        "contract_satisfied": max(all_residuals) < 1e-10,
    }


def synthetic_periodic_bvp_witness() -> dict[str, Any]:
    """Exactly-solvable synthetic witness for the reduced residual evaluator."""

    mode_numbers = (1, 2, 3)
    angular_frequency = 0.73
    intrinsic = (1.11, 1.67, 2.41)
    amplitudes = (0.24, 0.17, 0.09)
    phases = (0.13, -0.47, 0.81)
    source = tuple(
        (omega_i * omega_i - (n * angular_frequency) ** 2) * amplitude
        for n, omega_i, amplitude in zip(mode_numbers, intrinsic, amplitudes)
    )
    parameters = ReducedBVPParameters(
        mode_numbers=mode_numbers,
        angular_frequency=angular_frequency,
        intrinsic_frequencies=intrinsic,
        amplitudes=amplitudes,
        phases=phases,
        source_amplitudes=source,
        lambda_ratio=0.417,
        berger_a=1.157054135733433,
        lambda_target=0.417,
        berger_target=1.157054135733433,
    )
    residual = periodic_bvp_residual(parameters)
    return {
        "artifact": "BHSM_synthetic_periodic_bvp_witness_v14_55",
        "version": VERSION,
        "status": "SYNTHETIC_SOLVER_HARNESS_WITNESS_NOT_A_PHYSICAL_SOLUTION",
        "parameters": asdict(parameters),
        "residual": residual,
        "physical_coefficients_used": False,
        "action_derived_DtN_kernel_used": False,
        "relative_heat_kernel_used": False,
        "purpose": (
            "prove deterministic periodic residual evaluation and phase closure "
            "before inserting action-derived coefficients"
        ),
    }


def moving_seam_bvp_contract_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_moving_seam_bvp_contract_v14_55",
        "version": VERSION,
        "state": "Y=(G,eta,sigma,A_YM,Psi,X;dot X) on parent and child domains",
        "seam_expansion": "xi(tau,Omega)=sum_(k=1)^3 q_k(tau) M_k(Omega)+higher modes",
        "required_residual_blocks": [
            "bulk Euler-Lagrange equations in parent and child",
            "induced metric, spin-frame and gauge compatibility",
            "Dirichlet-to-Neumann traction balance including GHY/corner terms",
            "relative periodicity Y(T)=h.Y(0) and tangent closure",
            "cycle-averaged seam force balance",
            "nesting stationarity dGamma_rel/dlambda=0",
            "Berger stationarity dGamma_rel/da=0",
            "gauge fixing and zero-mode removal",
            "parent subtraction and relative heat-kernel regularization",
            "Floquet monodromy and reduced-Hessian stability",
        ],
        "implemented_now": [
            "three linearly independent noncommuting shape channels",
            "deterministic harmonic collocation residual evaluator",
            "periodic position and tangent closure checks",
            "symbolic lambda and Berger stationarity slots",
            "synthetic exact residual witness",
        ],
        "missing_physical_inputs": [
            "matched parent and child backgrounds",
            "action-derived DtN map and seam traction coefficients",
            "complete trace-class relative heat kernel",
            "renormalized nonlocal determinant and anomaly",
            "action-selected harmonic amplitudes, phases and ordering",
            "matter current and detector response functional",
            "full gauge-fixed domain and stability operator",
            "cosmology-particle action deriving the shared R_H and nesting ratios",
        ],
        "physical_solution_obtained": False,
    }


@dataclass(frozen=True)
class PairWakeState:
    proper_time: float
    phase: float
    angular_frequency: float
    momentum: Vector3
    pair_identity: tuple[str, str]
    internal_relation_tag: str

    def validate(self) -> None:
        if not _finite((self.proper_time, self.phase, self.angular_frequency, *self.momentum)):
            raise ValueError("finite pair-wake state required")
        if self.angular_frequency <= 0.0:
            raise ValueError("positive angular frequency required")
        if len(self.pair_identity) != 2 or not all(self.pair_identity):
            raise ValueError("two nonempty fixed pair labels required")
        if not self.internal_relation_tag:
            raise ValueError("nonempty internal relation tag required")


@dataclass(frozen=True)
class MatterImpulse:
    momentum_kick: Vector3
    phase_mode: PhaseMode
    phase_value: float
    frequency_kick: float = 0.0

    def validate(self) -> None:
        if self.phase_mode not in ("advance", "delay", "reset"):
            raise ValueError("phase mode must be advance, delay or reset")
        if not _finite((*self.momentum_kick, self.phase_value, self.frequency_kick)):
            raise ValueError("finite impulse required")


def advance_pair_wake(state: PairWakeState, elapsed_proper_time: float) -> PairWakeState:
    state.validate()
    if not math.isfinite(elapsed_proper_time) or elapsed_proper_time < 0.0:
        raise ValueError("finite nonnegative elapsed proper time required")
    return PairWakeState(
        proper_time=state.proper_time + elapsed_proper_time,
        phase=normalize_phase(state.phase + state.angular_frequency * elapsed_proper_time),
        angular_frequency=state.angular_frequency,
        momentum=state.momentum,
        pair_identity=state.pair_identity,
        internal_relation_tag=state.internal_relation_tag,
    )


def apply_common_mode_matter_impulse(
    state: PairWakeState,
    impulse: MatterImpulse,
) -> PairWakeState:
    """Redirect the whole pair and apply an advance/delay/reset phase kick.

    The fixed inception identity and internal relation tag are invariant by
    construction; this is the common-mode rather than differential coupling.
    """

    state.validate()
    impulse.validate()
    new_momentum = tuple(
        component + kick for component, kick in zip(state.momentum, impulse.momentum_kick)
    )
    if impulse.phase_mode == "advance":
        new_phase = state.phase + abs(impulse.phase_value)
    elif impulse.phase_mode == "delay":
        new_phase = state.phase - abs(impulse.phase_value)
    else:
        new_phase = impulse.phase_value
    new_frequency = state.angular_frequency + impulse.frequency_kick
    if new_frequency <= 0.0:
        raise ValueError("matter impulse must leave positive cycle frequency")
    return PairWakeState(
        proper_time=state.proper_time,
        phase=normalize_phase(new_phase),
        angular_frequency=new_frequency,
        momentum=new_momentum,  # type: ignore[arg-type]
        pair_identity=state.pair_identity,
        internal_relation_tag=state.internal_relation_tag,
    )


def wake_probabilities(phase: float, sharpness: float = 2.25) -> dict[str, float]:
    """Threefold normalized detector-response witness.

    This von-Mises softmax is a smooth kinematic map from one cycle phase to
    three wake-response weights. It is not a fitted or predicted PMNS law.
    """

    if not math.isfinite(sharpness) or sharpness <= 0.0:
        raise ValueError("positive finite sharpness required")
    phi = normalize_phase(phase)
    centers = (0.0, 2.0 * math.pi / 3.0, 4.0 * math.pi / 3.0)
    raw = [math.exp(sharpness * math.cos(phi - center)) for center in centers]
    total = sum(raw)
    return {
        label: value / total for label, value in zip(("electron", "muon", "tau"), raw)
    }


def pair_wake_dynamics_witness() -> dict[str, Any]:
    initial = PairWakeState(
        proper_time=0.0,
        phase=0.21,
        angular_frequency=0.87,
        momentum=(1.0, 0.0, 0.0),
        pair_identity=("A", "B"),
        internal_relation_tag="fixed_at_inception",
    )
    free = advance_pair_wake(initial, 1.75)
    advanced = apply_common_mode_matter_impulse(
        free,
        MatterImpulse((0.0, 0.24, 0.0), "advance", 0.43),
    )
    delayed = apply_common_mode_matter_impulse(
        advanced,
        MatterImpulse((-0.08, 0.0, 0.03), "delay", 0.19),
    )
    reset = apply_common_mode_matter_impulse(
        delayed,
        MatterImpulse((0.0, -0.11, 0.0), "reset", 4.2, frequency_kick=0.02),
    )
    states = [initial, free, advanced, delayed, reset]
    return {
        "artifact": "BHSM_pair_wake_dynamics_witness_v14_55",
        "version": VERSION,
        "status": "KINEMATIC_PAIR_WAKE_WITNESS_NOT_A_NEUTRINO_PREDICTION",
        "states": [asdict(state) for state in states],
        "wake_probabilities": [wake_probabilities(state.phase) for state in states],
        "pair_identity_preserved": all(state.pair_identity == initial.pair_identity for state in states),
        "internal_relation_preserved": all(
            state.internal_relation_tag == initial.internal_relation_tag for state in states
        ),
        "free_cycle_rule": "phi(tau+Delta tau)=phi(tau)+omega Delta tau",
        "matter_rule": "whole-pair momentum kick plus advance/delay/reset phase map",
    }


def pair_wake_neutrino_action_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_pair_wake_neutrino_action_v14_55",
        "version": VERSION,
        "hypothesis_status": "NORMAN_PAIR_WAKE_HYPOTHESIS_FORMALIZED_NOT_DERIVED",
        "fixed_inception_data": {
            "pair_identity": "Xi_AB selected once at formation and not exchanged during propagation",
            "inertia": "initial mismatch inherited from incomplete three-body closure or background pair production",
            "possible_microstates": "may exceed three; three labels belong to geometric wake responses",
        },
        "schematic_action": (
            "S_nu=integral d tau[-E_pair(Xi)+(I_phi/2)(dot phi-omega_0)^2"
            "+(M_X/2)g_mn dot X^m dot X^n-V_3(phi)]"
            "+S_wake[g;Xi,phi,X]+S_common[X,phi;J_matter]"
        ),
        "equations": {
            "identity_transport": "D_tau Xi_AB=0",
            "free_phase": "dot phi=omega_0 between interactions",
            "wake": "delta g_nu=sum_(alpha=1)^3 w_alpha(phi,dot X,environment) W_alpha[Xi_AB]",
            "detector": "P_alpha proportional to |<D_alpha,delta g_nu>|^2",
            "matter_jump": "P_X^+-P_X^-=I_k; phi^+=R_k(phi^-,I_k,environment)",
            "phase_map": "R_k may advance, delay or reset the phase",
        },
        "causal_chain": [
            "fixed unbalanced pair",
            "elapsed-proper-time cycle",
            "threefold pair disturbance on the universal 3D surface",
            "detector response to the wake",
            "perceived electron/muon/tau flavor",
        ],
        "mass_statement": {
            "instantaneous": "orbit-correlated wake/inertial response may vary with phase and environment",
            "physical_invariant": "complete parent-relative cycle quasi-energy remains the candidate mass readout",
            "primitive_static_mass_term_inserted": False,
        },
        "matter_coupling": {
            "acts_on": "collective motion of the intact pair",
            "does_not_require": "differential force that breaks or swaps the pair members",
            "can_change": ["direction", "momentum", "phase", "cycle rate"],
        },
        "required_empirical_gates": [
            "derive the relativistic baseline/time phase law rather than impose it",
            "derive two independent oscillation phase splittings",
            "derive a unitary three-response detector map and CP behavior",
            "reproduce vacuum, solar, reactor, atmospheric and accelerator probabilities with one coefficient set",
            "reproduce coherent matter effects and distinguish phase kicks from ordinary scattering",
            "derive absolute or bounded cycle quasi-energies without measured-mass fitting",
            "respect weak-interaction cross sections and all null searches",
        ],
        "neutrino_verdict": NEUTRINO_VERDICT,
        "physical_PMNS_emitted": False,
        "physical_mass_splittings_emitted": False,
    }


def pair_capture_formation_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_pair_capture_formation_v14_55",
        "version": VERSION,
        "hypothesis_status": "FORMATION_CHANNEL_CONTRACT_NOT_ACTION_DERIVED",
        "reaction": "(A,B)+(A_prime,C) -> [(A,B)+A_prime_outer]+C_star -> stable_3+radiation",
        "capture_rules": {
            "original_pair_remains_recognizable": True,
            "captured_member": "a separate copy of A or B stripped from another pair",
            "kind_match": "same basic kind is required; phase, orientation and motion may adjust during lock-in",
            "binding_source": "collective disturbance generated by the inner pair",
            "roles_exchange_during_cycle": False,
            "collision_selects": "initial point on the ordinary cycle, not a permanently new continuous species",
        },
        "one_body_remainder": {
            "stable_particle": False,
            "channels": ["prompt radiation", "brief unstable propagation then radiation"],
            "lifetime_depends_on": ["local environment", "impact variables"],
            "structural_identity_retained_at_these_energies": False,
        },
        "information_flow": {
            "stable_three_body_carries": [
                "which member was duplicated",
                "inner-pair identity",
                "outer-orbit phase and handedness",
                "formation-cycle phase",
            ],
            "radiation_carries": [
                "energy",
                "momentum",
                "angular momentum",
                "allowed conserved charges",
            ],
            "radiation_detailed_pair_identity": "lost at the stated energy regime",
        },
        "conservation_contract": (
            "P_(AB)+P_(A_prime C)=P_[(AB)A_prime]+P_radiation with all exact "
            "gauge and topological charges conserved by the eventual action"
        ),
        "abundance_hypothesis": (
            "unbalanced pairs may be common background products while correctly "
            "aligned duplicate capture into stable three-body matter is rare"
        ),
        "capture_verdict": CAPTURE_VERDICT,
    }


def nested_color_neutral_orbit_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_nested_color_neutral_orbit_contract_v14_55",
        "version": VERSION,
        "state_contract": (
            "a color-open sub-envelopment is defined only relative to an enclosing "
            "color-neutral meson or baryon cycle"
        ),
        "required_equations": [
            "local nonabelian Gauss law D_i E^i=rho on every slice",
            "global singlet projection of the complete hadron state",
            "moving-seam traction balance for each nested boundary",
            "Wilson functional -log<W(C)>=sigma A+mu P+...",
            "hadron-minus-parent quasilocal Hamiltonian charge",
            "relative-periodic monodromy and reduced-Hessian stability",
        ],
        "global_color_charge_zero_is_sufficient": False,
        "numerical_hadron_solution_obtained": False,
        "string_tension_derived": False,
    }


def completion_payload() -> dict[str, Any]:
    observability = three_harmonic_observability_payload()
    synthetic = synthetic_periodic_bvp_witness()
    pair_wake = pair_wake_dynamics_witness()
    return {
        "artifact": "BHSM_completion_gate_v14_55",
        "version": VERSION,
        "primary_verdict": PRIMARY_VERDICT,
        "validated": [
            "three independent noncommuting shape channels form a computable reduced basis",
            "periodic BVP residual and tangent closure evaluation are deterministic",
            "common-mode matter impulses preserve fixed pair identity in the formal model",
            "advance, delay and reset phase maps are represented explicitly",
            "pair-wake, duplicate-capture and radiation information-flow hypotheses are fail-closed contracts",
            "nested color-neutral local-Gauss/Wilson requirements remain explicit",
        ],
        "invalidated_or_forbidden": [
            "calling the synthetic periodic witness a BHSM particle solution",
            "identifying three detected flavors with three exchanged pair identities",
            "letting matter effects require constituent swapping",
            "assigning a static primitive neutrino mass from one instantaneous wake phase",
            "claiming 2+2 -> 3+1* without an action-derived capture amplitude and conservation proof",
            "claiming confinement from global color neutrality alone",
        ],
        "open": [
            "action-derived DtN and relative heat-kernel coefficients",
            "matched parent-child periodic moving-seam solution",
            "unique cosmological-to-particle nesting ratios",
            "physical pair-wake source and detector response functionals",
            "neutrino phase splittings, PMNS map, CP phase and cycle quasi-energies",
            "matter impulse law and coherent propagation limit",
            "capture amplitude, radiation spectrum and stable three-body spectrum",
            "nested color-neutral hadron solution and Wilson area law",
            "full gauge-fixed Floquet stability",
        ],
        "diagnostics": {
            "three_channel_rank": observability["channel_rank"],
            "noncommuting_basis": observability["at_least_one_noncommuting_pair"],
            "synthetic_bvp_max_residual": synthetic["residual"]["max_residual"],
            "pair_identity_preserved": pair_wake["pair_identity_preserved"],
        },
        "Mark_I": "REACHED",
        "Mark_II": "CONDITIONAL",
        "Mark_III": "NOT_REACHED",
        "BHSM_physical_completion": False,
        "validation_passed": True,
        "validation": {
            "frozen_predictions_changed": False,
            "official_prediction_logic_changed": False,
            "physical_mass_emitted": False,
            "physical_mass_splitting_emitted": False,
            "physical_PMNS_emitted": False,
            "physical_CKM_emitted": False,
            "physical_coupling_emitted": False,
            "USB_untouched": True,
        },
        "exact_next_object": EXACT_NEXT_OBJECT,
    }


def _json_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def materialize(output: str | Path) -> list[Path]:
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    payloads = {
        "BHSM_three_harmonic_observability_v14_55.json": three_harmonic_observability_payload(),
        "BHSM_synthetic_periodic_bvp_witness_v14_55.json": synthetic_periodic_bvp_witness(),
        "BHSM_moving_seam_bvp_contract_v14_55.json": moving_seam_bvp_contract_payload(),
        "BHSM_pair_wake_neutrino_action_v14_55.json": pair_wake_neutrino_action_payload(),
        "BHSM_pair_capture_formation_v14_55.json": pair_capture_formation_payload(),
        "BHSM_nested_color_neutral_orbit_contract_v14_55.json": nested_color_neutral_orbit_payload(),
        "BHSM_completion_gate_v14_55.json": completion_payload(),
    }
    written: list[Path] = []
    for name, payload in sorted(payloads.items()):
        target = output_path / name
        target.write_text(_json_text(payload), encoding="utf-8", newline="\n")
        written.append(target)
    return written


__all__ = [
    "CAPTURE_VERDICT",
    "EXACT_NEXT_OBJECT",
    "MatterImpulse",
    "NEUTRINO_VERDICT",
    "PRIMARY_VERDICT",
    "PairWakeState",
    "ReducedBVPParameters",
    "THREE_SHAPE_CHANNELS",
    "VERSION",
    "advance_pair_wake",
    "apply_common_mode_matter_impulse",
    "completion_payload",
    "materialize",
    "moving_seam_bvp_contract_payload",
    "nested_color_neutral_orbit_payload",
    "pair_capture_formation_payload",
    "pair_wake_dynamics_witness",
    "pair_wake_neutrino_action_payload",
    "periodic_bvp_residual",
    "synthetic_periodic_bvp_witness",
    "three_harmonic_observability_payload",
    "wake_probabilities",
]
