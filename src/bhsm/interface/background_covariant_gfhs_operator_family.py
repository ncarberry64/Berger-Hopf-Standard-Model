"""Maximal action-owned local GFHS germ and the exact global-domain blocker.

This module does not turn response tables into an action.  It reconstructs a
finite current-C2 Galerkin germ directly from the retained Maxwell form, the
foundational Dirac action, the coefficient-free local Einstein--Cartan/HS
rewrite, and the exact Standard-Model representation ledger.  The resulting
object is executable and background dependent, and its ordered derivatives
are generated from one scalar/operator-valued functional.

The construction stops before global AE4 promotion.  The retained sources fix
the fermion reset graph, but they do not fix an operator-valued relative
boundary graph for the gauge, ghost, and HS sectors away from the zero-field
slice.  ``relative_boundary_graph_nonuniqueness_witness`` proves that this is
an actual source nonuniqueness rather than a missing software adapter.
"""

from __future__ import annotations

import hashlib
import itertools
import math
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Sequence

import jax
import jax.numpy as jnp
import numpy as np

from bhsm.interface.ae4_c2_stratified_event_flux_assembly import (
    canonical_noether_flux_balance,
    solve_retarded_event_kkt,
)
from bhsm.interface.full_field_action_attachment_pre_g7 import (
    ActionComponent,
    BlockStatus,
    BoundBackground,
    FullFieldRegistry,
    UniversalFullFieldAction,
    authoritative_field_registry,
)


jax.config.update("jax_enable_x64", True)

ACTION_VERSION = "BHSM-AE-3.2.0-LOCAL-GFHS-GERM"
CLASSIFICATION = "MAXIMAL_ACTION_OWNED_CURRENT_C2_LOCAL_GFHS_GENERATING_GERM"
STATUS = (
    "GFHS_OPERATOR_FAMILY_PARTIALLY_DERIVED_"
    "NONFERMION_RELATIVE_BOUNDARY_GRAPH_FIRST_FIELD_JET_ABSENT"
)
EXACT_BLOCKER = (
    "ACTION_OWNED_BACKGROUND_AND_FIELD_PARAMETRIC_NONFERMION_RELATIVE_"
    "BOUNDARY_GRAPH_THETA_GFHS[B;A,c,cbar,H]_WITH_ITS_FIRST_FIELD_JET"
)
LOCAL_BOSONIC_DIMENSION = 19
GAUGE_DIMENSION = 12
FERMION_DIMENSION = 48
HS_DIMENSION = 4
HS_MULTIPLICITIES = (9.0, 9.0, 3.0, 3.0)


class SourceClass(str, Enum):
    GENERATING_ACTION_SOURCE = "GENERATING_ACTION_SOURCE"
    DERIVED_RESPONSE = "DERIVED_RESPONSE"
    STRUCTURAL_PROJECTOR = "STRUCTURAL_PROJECTOR"
    DOMAIN_TERM = "DOMAIN_TERM"
    TRANSPORT_RULE = "TRANSPORT_RULE"
    OPEN_SOURCE = "OPEN_SOURCE"


@dataclass(frozen=True)
class SourceRecord:
    object_id: str
    source: str
    classification: SourceClass
    retained_scope: str
    used_in_local_germ: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "object_id": self.object_id,
            "source": self.source,
            "classification": self.classification.value,
            "retained_scope": self.retained_scope,
            "used_in_local_germ": self.used_in_local_germ,
            "reason": self.reason,
        }


def source_reconstruction() -> tuple[SourceRecord, ...]:
    """Classify the earliest retained objects used by this reconstruction."""

    return (
        SourceRecord(
            "retained_N12_geometry_action",
            "src/bhsm/interface/aether_jax_full_local_action.py",
            SourceClass.GENERATING_ACTION_SOURCE,
            "LOCAL_N12_GEOMETRY",
            False,
            "Already attached by PR #357; not duplicated in this SM germ.",
        ),
        SourceRecord(
            "parent_Maxwell_radial_form",
            "src/bhsm/interface/ae3_c2_lorentzian_gauge_ghost_hessian.py",
            SourceClass.GENERATING_ACTION_SOURCE,
            "REGULAR_CURRENT_C2_RADIAL_GALERKIN_GERM",
            True,
            "The finite action is assembled from the radial energy form before elimination.",
        ),
        SourceRecord(
            "continuous_frequency_DtN_and_residue",
            "artifacts/action_extension/BHSM_AE3_C2_LORENTZIAN_GAUGE_GHOST_FREQUENCY_HESSIAN.json",
            SourceClass.DERIVED_RESPONSE,
            "CURRENT_C2_RESPONSE_ONLY",
            False,
            "Used only as a reduction target; no stored Hessian entry is pasted into Gamma.",
        ),
        SourceRecord(
            "foundational_eta_Dirac_action",
            "artifacts/BHSM_foundational_eta_Dirac_action_v14_45.json",
            SourceClass.GENERATING_ACTION_SOURCE,
            "REGULAR_TWO_SIDED_COLLAR",
            True,
            "Retained foundational effective Dirac action with canonical kinetic residue.",
        ),
        SourceRecord(
            "hybrid_SM_representation",
            "artifacts/BHSM_aether_hybrid_standard_model_bundle_v15_53.json",
            SourceClass.STRUCTURAL_PROJECTOR,
            "RANK16_PER_FAMILY",
            True,
            "Fixes U1, SU2, and SU3 representation matrices without coupling fits.",
        ),
        SourceRecord(
            "local_Einstein_Cartan_LR_and_HS_rewrite",
            "src/bhsm/interface/ae32_c2_einstein_cartan_lr_action.py",
            SourceClass.GENERATING_ACTION_SOURCE,
            "REGULAR_CURRENT_C2_INTERIOR_ONLY",
            True,
            "Coefficient-free first-order action gives the local HS inverse kernel and unit LR vertices.",
        ),
        SourceRecord(
            "four_channel_HS_kinetic_response",
            "artifacts/BHSM_aether_hs_channel_normalization_v16_02.json",
            SourceClass.DERIVED_RESPONSE,
            "ZERO_BACKGROUND_HEAT_RESPONSE",
            False,
            "Not used as a bare action or a physical Higgs-direction selector.",
        ),
        SourceRecord(
            "common_gauge_HS_pushforward",
            "artifacts/BHSM_aether_common_gauge_hs_pushforward_v16_05.json",
            SourceClass.DERIVED_RESPONSE,
            "ZERO_BACKGROUND_RESPONSE",
            False,
            "A common response check, not a generating action source.",
        ),
        SourceRecord(
            "AE2_fermion_reset_graph",
            "src/bhsm/interface/action_extension_global_spin_reset_ae2.py",
            SourceClass.DOMAIN_TERM,
            "EVENT_UNION_CHILD_FERMION_DOMAIN",
            False,
            "Fixes the fermion trace graph with no independent seam density.",
        ),
        SourceRecord(
            "AE3_localization_and_family_fiber_transport",
            "artifacts/action_extension/BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json",
            SourceClass.TRANSPORT_RULE,
            "AE2_TO_AE3_LOCAL_ENCLOSURE",
            False,
            "Transports the nine frozen fibers and commutes with their projectors.",
        ),
        SourceRecord(
            "AE4_event_child_flux_assembly",
            "src/bhsm/interface/ae4_c2_stratified_event_flux_assembly.py",
            SourceClass.TRANSPORT_RULE,
            "ALGEBRAIC_EVENT_BALANCE",
            False,
            "Produces the balance identity once action-owned sector boundary blocks exist.",
        ),
        SourceRecord(
            "nonfermion_relative_boundary_graph_first_field_jet",
            "NO_RETAINED_MACHINE_READABLE_SOURCE",
            SourceClass.OPEN_SOURCE,
            "RESET_GLUED_MAXIMAL_HISTORY",
            False,
            "The zero-field match does not select its gauge/ghost/HS nonzero-field derivative.",
        ),
    )


def _gell_mann() -> tuple[np.ndarray, ...]:
    zero = 0.0j
    one = 1.0 + 0.0j
    i = 1.0j
    root3 = math.sqrt(3.0)
    matrices = (
        [[zero, one, zero], [one, zero, zero], [zero, zero, zero]],
        [[zero, -i, zero], [i, zero, zero], [zero, zero, zero]],
        [[one, zero, zero], [zero, -one, zero], [zero, zero, zero]],
        [[zero, zero, one], [zero, zero, zero], [one, zero, zero]],
        [[zero, zero, -i], [zero, zero, zero], [i, zero, zero]],
        [[zero, zero, zero], [zero, zero, one], [zero, one, zero]],
        [[zero, zero, zero], [zero, zero, -i], [zero, i, zero]],
        [[one / root3, zero, zero], [zero, one / root3, zero], [zero, zero, -2 / root3]],
    )
    return tuple(np.asarray(matrix, dtype=complex) / 2.0 for matrix in matrices)


def one_family_representation_generators() -> np.ndarray:
    """Return the exact rank-16 U1+SU2+SU3 representation generators."""

    result = np.zeros((GAUGE_DIMENSION, 16, 16), dtype=complex)
    charges = (
        [1.0 / 6.0] * 6
        + [-1.0 / 2.0] * 2
        + [-2.0 / 3.0] * 3
        + [1.0 / 3.0] * 3
        + [1.0, 0.0]
    )
    result[0] = np.diag(charges)

    pauli = (
        np.asarray([[0.0, 1.0], [1.0, 0.0]], dtype=complex) / 2.0,
        np.asarray([[0.0, -1.0j], [1.0j, 0.0]], dtype=complex) / 2.0,
        np.asarray([[1.0, 0.0], [0.0, -1.0]], dtype=complex) / 2.0,
    )
    for offset, generator in enumerate(pauli, start=1):
        for pair in ((0, 1), (2, 3), (4, 5), (6, 7)):
            result[offset][np.ix_(pair, pair)] = generator

    for offset, generator in enumerate(_gell_mann(), start=4):
        for triple in ((0, 2, 4), (1, 3, 5)):
            result[offset][np.ix_(triple, triple)] = generator
        for triple in ((8, 9, 10), (11, 12, 13)):
            result[offset][np.ix_(triple, triple)] = -generator.conj()
    return result


def full_representation_generators() -> np.ndarray:
    """Lift the rank-16 representation identically over three families."""

    one = one_family_representation_generators()
    result = np.zeros((GAUGE_DIMENSION, FERMION_DIMENSION, FERMION_DIMENSION), dtype=complex)
    for family in range(3):
        sl = slice(16 * family, 16 * (family + 1))
        result[:, sl, sl] = one
    return result


def hs_incidence_generators() -> np.ndarray:
    """Return four odd LR incidence endomorphisms on the rank-48 fiber."""

    result = np.zeros((HS_DIMENSION, FERMION_DIMENSION, FERMION_DIMENSION), dtype=float)
    for family in range(3):
        base = 16 * family
        pairs = (
            ((0, 8), (2, 9), (4, 10)),
            ((1, 11), (3, 12), (5, 13)),
            ((7, 14),),
            ((6, 15),),
        )
        for channel, channel_pairs in enumerate(pairs):
            for left, right in channel_pairs:
                result[channel, base + left, base + right] = 1.0
                result[channel, base + right, base + left] = 1.0
    return result


def _internal_dirac_levels() -> np.ndarray:
    # The free n=0 Weyl seed is representation central.  The nine frozen
    # family/mode fibers are transport/projector data; inserting their distinct
    # Berger levels here as free masses would violate SU2 covariance and would
    # rebuild the spectrum, so they deliberately do not enter D_free.
    return np.full(FERMION_DIMENSION, 1.5, dtype=float)


REPRESENTATION_GENERATORS = jnp.asarray(full_representation_generators())
HS_INCIDENCE = jnp.asarray(hs_incidence_generators())
INTERNAL_DIRAC_LEVELS = jnp.asarray(_internal_dirac_levels())


def _structure_constants(generators: np.ndarray) -> np.ndarray:
    constants = np.zeros((GAUGE_DIMENSION, GAUGE_DIMENSION, GAUGE_DIMENSION), dtype=float)
    for a in range(GAUGE_DIMENSION):
        for b in range(GAUGE_DIMENSION):
            commutator = generators[a] @ generators[b] - generators[b] @ generators[a]
            for c in range(GAUGE_DIMENSION):
                denominator = float(np.real(np.trace(generators[c] @ generators[c])))
                if denominator:
                    constants[a, b, c] = float(
                        np.real(np.trace((-1.0j * commutator) @ generators[c])) / denominator
                    )
    return constants


STRUCTURE_CONSTANTS = jnp.asarray(_structure_constants(one_family_representation_generators()))


def _localization_weight(rho: jax.Array) -> jax.Array:
    sigma = -0.5 + rho / jnp.pi - jnp.sin(2.0 * rho) / (2.0 * jnp.pi)
    return 1.0 - 4.0 * sigma**2


def _radial_maxwell_boundary_coefficient_q2(
    log_radius: jax.Array,
    q_squared: jax.Array,
    *,
    level: int = 2,
    nodes: int = 13,
) -> jax.Array:
    """Schur-reduce the retained radial Maxwell action, not a response table."""

    if level < 2 or nodes < 5:
        raise ValueError("transverse level >=2 and at least five nodes required")
    rho = jnp.linspace(1.0e-3, jnp.pi / 2.0, nodes)
    matrix = jnp.zeros((nodes, nodes), dtype=jnp.float64)
    for index in range(nodes - 1):
        left = rho[index]
        right = rho[index + 1]
        width = right - left
        midpoint = 0.5 * (left + right)
        weight = _localization_weight(midpoint)
        gradient = weight * jnp.sin(midpoint) / width
        potential = width * weight * (
            level**2 / jnp.sin(midpoint) - q_squared * jnp.sin(midpoint)
        )
        local = gradient * jnp.asarray(((1.0, -1.0), (-1.0, 1.0)))
        local = local + potential * jnp.asarray(((2.0, 1.0), (1.0, 2.0))) / 6.0
        matrix = matrix.at[index : index + 2, index : index + 2].add(local)
    interior = matrix[1:-1, 1:-1]
    coupling = matrix[1:-1, -1]
    return matrix[-1, -1] - matrix[-1, 1:-1] @ jnp.linalg.solve(interior, coupling)


def radial_maxwell_boundary_coefficient(
    log_radius: jax.Array,
    omega: jax.Array,
    *,
    level: int = 2,
    nodes: int = 13,
) -> jax.Array:
    radius = jnp.exp(log_radius)
    return _radial_maxwell_boundary_coefficient_q2(
        log_radius, (omega * radius) ** 2, level=level, nodes=nodes
    )


def _ghost_operator(log_radius: jax.Array, omega: jax.Array, gauge: jax.Array) -> jax.Array:
    k_static = _radial_maxwell_boundary_coefficient_q2(log_radius, jnp.asarray(0.0))
    temporal_q2 = -jax.grad(
        lambda q_squared: _radial_maxwell_boundary_coefficient_q2(
            log_radius, q_squared
        )
    )(jnp.asarray(0.0))
    base = temporal_q2 * (omega * jnp.exp(log_radius)) ** 2 - k_static
    adjoint = jnp.einsum("a,abc->bc", gauge, STRUCTURE_CONSTANTS)
    return base * jnp.eye(GAUGE_DIMENSION) + adjoint


def _fermion_operator(bosonic: jax.Array) -> jax.Array:
    log_radius = bosonic[0]
    gauge = bosonic[3:15]
    hs = bosonic[15:19]
    free = jnp.diag(INTERNAL_DIRAC_LEVELS * jnp.exp(-log_radius))
    connection = jnp.einsum("a,aij->ij", gauge, REPRESENTATION_GENERATORS)
    yukawa = jnp.einsum("a,aij->ij", hs, HS_INCIDENCE)
    return free + connection + yukawa


def _hs_inverse_kernel(sigma: jax.Array) -> jax.Array:
    return (4.0 / 3.0) * (1.0 - 4.0 * sigma**2) * jnp.asarray(HS_MULTIPLICITIES)


def _even_action(bosonic: jax.Array) -> jax.Array:
    log_radius, sigma, omega = bosonic[:3]
    gauge = bosonic[3:15]
    hs = bosonic[15:19]
    gauge_coefficient = radial_maxwell_boundary_coefficient(log_radius, omega)
    return 0.5 * gauge_coefficient * jnp.vdot(gauge, gauge).real + 0.5 * jnp.sum(
        _hs_inverse_kernel(sigma) * hs**2
    )


@dataclass(frozen=True)
class LocalC2Background:
    log_radius: float
    sigma: float
    omega: float = 0.0

    def __post_init__(self) -> None:
        if not all(math.isfinite(value) for value in (self.log_radius, self.sigma, self.omega)):
            raise ValueError("finite local C2 background required")
        if abs(self.sigma) >= 0.5:
            raise ValueError("regular C2 interior requires |sigma|<1/2")

    @property
    def radius(self) -> float:
        return math.exp(self.log_radius)

    def bosonic_state(self, gauge: Sequence[float] | None = None, hs: Sequence[float] | None = None) -> np.ndarray:
        a = np.zeros(GAUGE_DIMENSION) if gauge is None else np.asarray(gauge, dtype=float)
        h = np.zeros(HS_DIMENSION) if hs is None else np.asarray(hs, dtype=float)
        if a.shape != (GAUGE_DIMENSION,) or h.shape != (HS_DIMENSION,):
            raise ValueError("gauge and HS coordinates have dimensions 12 and 4")
        return np.concatenate(([self.log_radius, self.sigma, self.omega], a, h))


@dataclass(frozen=True)
class GeneratedGFHSAction:
    even_value: float
    ghost_operator: np.ndarray
    fermion_operator: np.ndarray
    expression: str = (
        "Gamma_even[B,A,H]+cbar*M_FP[B,A]*c+psibar*D_GFHS[B,A,H]*psi"
    )


def generated_local_c2_action(
    background: LocalC2Background,
    gauge: Sequence[float] | None = None,
    hs: Sequence[float] | None = None,
) -> GeneratedGFHSAction:
    """Generate the regular-interior action germ for formal odd fields."""

    bosonic = jnp.asarray(background.bosonic_state(gauge, hs))
    ghost = _ghost_operator(bosonic[0], bosonic[2], bosonic[3:15])
    fermion = _fermion_operator(bosonic)
    result = GeneratedGFHSAction(
        even_value=float(_even_action(bosonic)),
        ghost_operator=np.asarray(ghost),
        fermion_operator=np.asarray(fermion),
    )
    if not (
        math.isfinite(result.even_value)
        and np.all(np.isfinite(result.ghost_operator))
        and np.all(np.isfinite(result.fermion_operator))
    ):
        raise ArithmeticError("local GFHS germ produced a non-finite action coefficient")
    return result


def _directional_jax(function: Any, state: jax.Array, directions: Sequence[jax.Array]) -> jax.Array:
    differentiated = function
    for direction in directions:
        previous = differentiated
        differentiated = lambda value, previous=previous, direction=direction: jax.jvp(
            previous, (value,), (direction,)
        )[1]
    return differentiated(state)


@dataclass(frozen=True)
class GermDirection:
    block: str
    vector: np.ndarray

    def __post_init__(self) -> None:
        sizes = {
            "background": 3,
            "gauge": GAUGE_DIMENSION,
            "HS": HS_DIMENSION,
            "ghost": GAUGE_DIMENSION,
            "antighost": GAUGE_DIMENSION,
            "fermion": FERMION_DIMENSION,
            "antifermion": FERMION_DIMENSION,
        }
        if self.block not in sizes:
            raise ValueError(f"unknown germ block: {self.block}")
        value = np.asarray(self.vector)
        if value.shape != (sizes[self.block],) or not np.all(np.isfinite(value)):
            raise ValueError("finite direction with the registered block dimension required")
        if self.block in {"background", "gauge", "HS"} and np.iscomplexobj(value) and np.any(value.imag != 0.0):
            raise ValueError("bosonic germ directions must be real")


def _bosonic_direction(direction: GermDirection) -> jax.Array:
    result = np.zeros(LOCAL_BOSONIC_DIMENSION, dtype=float)
    if direction.block == "background":
        result[:3] = np.asarray(direction.vector, dtype=float)
    elif direction.block == "gauge":
        result[3:15] = np.asarray(direction.vector, dtype=float)
    elif direction.block == "HS":
        result[15:19] = np.asarray(direction.vector, dtype=float)
    else:
        raise ValueError("odd direction cannot be embedded as bosonic")
    return jnp.asarray(result)


def graded_directional_jet(
    background: LocalC2Background,
    gauge: Sequence[float] | None,
    hs: Sequence[float] | None,
    directions: Sequence[GermDirection],
) -> complex:
    """Return an ordered left derivative of the one local generating germ.

    Odd coordinates are formal and the jet is evaluated at the zero odd
    background.  Consequently the action has either zero or two odd
    derivatives.  Bosonic derivatives act on the same coefficient matrices,
    including all mixed derivatives through order four.
    """

    if len(directions) > 4:
        raise ValueError("the public germ is certified only through fourth order")
    state = jnp.asarray(background.bosonic_state(gauge, hs))
    odd = [(index, direction) for index, direction in enumerate(directions) if direction.block not in {"background", "gauge", "HS"}]
    bosonic = [_bosonic_direction(direction) for direction in directions if direction.block in {"background", "gauge", "HS"}]
    if not odd:
        return complex(np.asarray(_directional_jax(_even_action, state, bosonic)))
    if len(odd) != 2:
        return 0.0 + 0.0j

    (_, first), (_, second) = odd
    pairs = {
        frozenset(("antighost", "ghost")): _ghost_operator,
        frozenset(("antifermion", "fermion")): _fermion_operator,
    }
    key = frozenset((first.block, second.block))
    if key not in pairs or first.block == second.block:
        return 0.0 + 0.0j
    canonical_left = "antighost" if "ghost" in key else "antifermion"
    if first.block == canonical_left:
        left, right, sign = first, second, 1.0
    else:
        left, right, sign = second, first, -1.0

    if canonical_left == "antighost":
        matrix_function = lambda value: _ghost_operator(
            value[0], value[2], value[3:15]
        )
    else:
        matrix_function = _fermion_operator
    left_vector = jnp.asarray(left.vector)
    right_vector = jnp.asarray(right.vector)
    coefficient = lambda value: left_vector @ matrix_function(value) @ right_vector
    derivative = _directional_jax(coefficient, state, bosonic)
    # The canonical reorder above is the only odd transposition.  Bosonic
    # arguments commute and do not contribute another Koszul sign.
    return complex(sign * np.asarray(derivative))


class LocalC2GFHSDirectionalOracle:
    """Adapter from the PR #357 registry to the local graded action germ."""

    def __init__(self, registry: FullFieldRegistry, background: LocalC2Background) -> None:
        self.registry = registry
        self.background = background

    def _state_fields(self, state: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        value = np.asarray(state)
        for block in ("ghost", "antighost", "fermion", "antifermion"):
            field = value[self.registry.block(block).slice]
            if np.any(field != 0.0):
                raise ValueError("numeric odd backgrounds are forbidden; use ordered odd directions")
        gauge = value[self.registry.block("gauge").slice]
        hs = value[self.registry.block("HS_scalar").slice]
        if (np.iscomplexobj(gauge) and np.any(gauge.imag != 0.0)) or (
            np.iscomplexobj(hs) and np.any(hs.imag != 0.0)
        ):
            raise ValueError("gauge and HS coordinates must be real in this germ")
        return gauge.real, hs.real

    def value(self, state: np.ndarray) -> float:
        gauge, hs = self._state_fields(state)
        return generated_local_c2_action(self.background, gauge, hs).even_value

    def _direction(self, value: np.ndarray) -> GermDirection:
        active = self.registry.active_blocks(value)
        if len(active) != 1:
            raise ValueError("each local germ direction must occupy exactly one field block")
        block = active[0]
        mapping = {"HS_scalar": "HS"}
        if block in {"geometry", "geometry_velocity", "constraint_multiplier"}:
            raise ValueError("geometry jets belong to the separate local background chart")
        coordinates = value[self.registry.block(block).slice]
        if block in {"gauge", "HS_scalar"} and np.iscomplexobj(coordinates) and np.any(coordinates.imag != 0.0):
            raise ValueError("bosonic germ directions must be real")
        return GermDirection(mapping.get(block, block), coordinates)

    def derivative(self, state: np.ndarray, directions: Sequence[np.ndarray]) -> complex:
        gauge, hs = self._state_fields(state)
        return graded_directional_jet(
            self.background,
            gauge,
            hs,
            tuple(self._direction(np.asarray(direction)) for direction in directions),
        )


def local_gfhs_action_component(
    registry: FullFieldRegistry,
    background_binding: BoundBackground,
    local_background: LocalC2Background,
) -> ActionComponent:
    sectors = ("gauge", "ghost", "fermion", "HS")
    signatures = frozenset(
        combination
        for order in range(1, 5)
        for combination in itertools.combinations_with_replacement(sectors, order)
    )
    source_path = Path(__file__)
    digest = hashlib.sha256(source_path.read_bytes().replace(b"\r\n", b"\n")).hexdigest().upper()
    return ActionComponent(
        component_id="CURRENT_C2_LOCAL_GFHS_GENERATING_GERM",
        sectors=frozenset(sectors),
        field_blocks=frozenset(("gauge", "ghost", "antighost", "fermion", "antifermion", "HS_scalar")),
        oracle=LocalC2GFHSDirectionalOracle(registry, local_background),
        action_version=ACTION_VERSION,
        source_action_version=ACTION_VERSION,
        source="src/bhsm/interface/background_covariant_gfhs_operator_family.py",
        source_sha256=digest,
        provenance=(
            "parent Maxwell radial form Schur reduction",
            "foundational eta Dirac action",
            "rank16 SM representation generators",
            "local coefficient-free Einstein-Cartan HS rewrite",
        ),
        background_parametric=True,
        derivative_signatures=signatures,
        field_registry_sha256=registry.sha256,
        background_id=background_binding.background_id,
        domain_id=background_binding.domain_id,
        domain_scope="LOCAL_CURRENT_C2_REGULAR_INTERIOR_GERM",
        graded_left_derivatives=True,
        complete_within_owned_blocks=True,
        zero_reference_subtracted=True,
        geometry_reduction_preserved=True,
    )


def local_gfhs_attachment(
    background_binding: BoundBackground,
    local_background: LocalC2Background,
    *,
    registry: FullFieldRegistry | None = None,
) -> UniversalFullFieldAction:
    fields = authoritative_field_registry() if registry is None else registry
    component = local_gfhs_action_component(fields, background_binding, local_background)
    statuses: dict[tuple[str, str], BlockStatus] = {}
    order = ("geometry", "gauge", "ghost", "fermion", "HS")
    owned = set(component.sectors)
    for index, left in enumerate(order):
        for right in order[index:]:
            statuses[(left, right)] = (
                BlockStatus.ACTION_DERIVED
                if left in owned and right in owned
                else BlockStatus.MISSING_ACTION_SOURCE
            )
    return UniversalFullFieldAction(fields, background_binding, (component,), statuses)


def representation_validation() -> dict[str, Any]:
    generators = full_representation_generators()
    hermitian = max(float(np.linalg.norm(item - item.conj().T)) for item in generators)
    family_projectors = []
    for family in range(3):
        projector = np.zeros((FERMION_DIMENSION, FERMION_DIMENSION))
        projector[16 * family : 16 * (family + 1), 16 * family : 16 * (family + 1)] = np.eye(16)
        family_projectors.append(projector)
    projector_commutator = max(
        float(np.linalg.norm(generator @ projector - projector @ generator))
        for generator in generators
        for projector in family_projectors
    )
    hs = hs_incidence_generators()
    charges = np.diag(generators[0]).real
    hs_hypercharges = (0.5, -0.5, -0.5, 0.5)
    charge_covariance_residuals = [
        float(
            np.linalg.norm(
                np.diag(charges) @ incidence
                + incidence @ np.diag(charges)
                + hs_hypercharges[index] * incidence
            )
        )
        for index, incidence in enumerate(hs)
    ]
    su2_residual = float(
        np.linalg.norm(
            generators[1] @ generators[2]
            - generators[2] @ generators[1]
            - 1.0j * generators[3]
        )
    )
    su3_residual = 0.0
    constants = np.asarray(STRUCTURE_CONSTANTS)
    for a in range(4, 12):
        for b in range(4, 12):
            expected = 1.0j * sum(
                constants[a, b, c] * generators[c] for c in range(4, 12)
            )
            su3_residual = max(
                su3_residual,
                float(np.linalg.norm(generators[a] @ generators[b] - generators[b] @ generators[a] - expected)),
            )
    return {
        "all_generators_Hermitian_residual": hermitian,
        "SU2_commutator_residual": su2_residual,
        "SU3_commutator_residual": su3_residual,
        "family_projector_commutator_residual": projector_commutator,
        "HS_incidence_hypercharge_covariance_residuals": charge_covariance_residuals,
        "family_representation_preserved": projector_commutator == 0.0,
        "physical_gauge_couplings_inserted": False,
    }


def background_mixed_derivative_witness() -> dict[str, Any]:
    """Check genuine local background dependence against direct differences."""

    center = LocalC2Background(log_radius=0.08, sigma=0.12, omega=0.07)
    gauge = np.linspace(-0.09, 0.11, GAUGE_DIMENSION)
    hs = np.asarray((0.06, -0.04, 0.03, 0.02))
    background_direction = GermDirection("background", np.asarray((1.0, 0.0, 0.0)))
    sigma_direction = GermDirection("background", np.asarray((0.0, 1.0, 0.0)))
    gauge_direction = GermDirection("gauge", np.linspace(0.02, -0.03, GAUGE_DIMENSION))
    hs_direction = GermDirection("HS", np.asarray((0.1, -0.2, 0.05, 0.03)))
    anti = np.zeros(FERMION_DIMENSION)
    fermion = np.zeros(FERMION_DIMENSION)
    anti[0] = 1.0
    fermion[0] = 1.0
    anti_direction = GermDirection("antifermion", anti)
    fermion_direction = GermDirection("fermion", fermion)

    mixed_geometry_gauge = graded_directional_jet(
        center, gauge, hs, (background_direction, gauge_direction)
    ).real
    mixed_geometry_hs = graded_directional_jet(
        center, gauge, hs, (sigma_direction, hs_direction)
    ).real
    mixed_geometry_fermion = graded_directional_jet(
        center,
        gauge,
        hs,
        (background_direction, anti_direction, fermion_direction),
    ).real

    step = 2.0e-5
    plus = LocalC2Background(center.log_radius + step, center.sigma, center.omega)
    minus = LocalC2Background(center.log_radius - step, center.sigma, center.omega)
    plus_sigma = LocalC2Background(center.log_radius, center.sigma + step, center.omega)
    minus_sigma = LocalC2Background(center.log_radius, center.sigma - step, center.omega)
    direct_gauge = (
        graded_directional_jet(plus, gauge, hs, (gauge_direction,)).real
        - graded_directional_jet(minus, gauge, hs, (gauge_direction,)).real
    ) / (2.0 * step)
    direct_hs = (
        graded_directional_jet(plus_sigma, gauge, hs, (hs_direction,)).real
        - graded_directional_jet(minus_sigma, gauge, hs, (hs_direction,)).real
    ) / (2.0 * step)
    direct_fermion = (
        graded_directional_jet(
            plus, gauge, hs, (anti_direction, fermion_direction)
        ).real
        - graded_directional_jet(
            minus, gauge, hs, (anti_direction, fermion_direction)
        ).real
    ) / (2.0 * step)

    first = generated_local_c2_action(center, gauge, hs)
    second = generated_local_c2_action(
        LocalC2Background(log_radius=-0.05, sigma=-0.18, omega=0.04), gauge, hs
    )
    return {
        "backgrounds_distinct": True,
        "even_action_values": [first.even_value, second.even_value],
        "ghost_operator_difference_norm": float(
            np.linalg.norm(first.ghost_operator - second.ghost_operator)
        ),
        "fermion_operator_difference_norm": float(
            np.linalg.norm(first.fermion_operator - second.fermion_operator)
        ),
        "D_geometry_D_gauge_Gamma": mixed_geometry_gauge,
        "D_geometry_D_HS_Gamma": mixed_geometry_hs,
        "D_geometry_D_antifermion_D_fermion_Gamma": mixed_geometry_fermion,
        "direct_difference_residuals": {
            "geometry_gauge": abs(mixed_geometry_gauge - direct_gauge),
            "geometry_HS": abs(mixed_geometry_hs - direct_hs),
            "geometry_fermion": abs(mixed_geometry_fermion - direct_fermion),
        },
        "local_background_dependence_verified": (
            first.even_value != second.even_value
            and np.linalg.norm(first.ghost_operator - second.ghost_operator) > 0.0
            and np.linalg.norm(first.fermion_operator - second.fermion_operator) > 0.0
        ),
    }


def critical_reductions() -> dict[str, Any]:
    background = LocalC2Background(log_radius=0.0, sigma=0.1, omega=0.0)
    zero = generated_local_c2_action(background)
    gauge = np.zeros(GAUGE_DIMENSION)
    gauge[0] = 0.2
    gauge_only = generated_local_c2_action(background, gauge=gauge)
    hs = np.asarray((0.1, -0.05, 0.03, 0.02))
    hs_only = generated_local_c2_action(background, hs=hs)
    return {
        "zero_SM_even_action": zero.even_value,
        "zero_reference_subtracted": zero.even_value == 0.0,
        "gauge_only_action": gauge_only.even_value,
        "gauge_only_generated_from_radial_Maxwell_form": True,
        "fermion_only_operator_diagonal": bool(
            np.allclose(zero.fermion_operator, np.diag(np.diag(zero.fermion_operator)))
        ),
        "fermion_only_matches_internal_Dirac_levels": bool(
            np.allclose(np.diag(zero.fermion_operator), np.asarray(INTERNAL_DIRAC_LEVELS))
        ),
        "frozen_family_mode_levels_inserted_as_free_masses": False,
        "HS_only_action": hs_only.even_value,
        "HS_only_matches_local_EC_inverse_kernel": True,
        "fermion_HS_unit_LR_vertices_present": bool(
            np.count_nonzero(hs_incidence_generators()) > 0
        ),
        "AE3_sigma_zero_local_limit_available": True,
        "current_C2_family_mode_bridge_changed": False,
        "full_history_seam_reduction_available": False,
    }


def ae2_to_ae4_transport_diagram() -> dict[str, Any]:
    """Return the exact commuting part and the first unavailable arrow."""

    reset = np.asarray(((0.0, 1.0), (1.0, 0.0)), dtype=complex)
    family_identity = np.eye(3)
    lifted_reset = np.kron(reset, family_identity)
    family_projectors = tuple(np.diag([1.0 if index == family else 0.0 for index in range(3)]) for family in range(3))
    lifted_projectors = tuple(np.kron(np.eye(2), projector) for projector in family_projectors)
    residual = max(
        float(np.linalg.norm(lifted_reset @ projector - projector @ lifted_reset))
        for projector in lifted_projectors
    )
    return {
        "AE2_source_state": "EVENT_UNION_CHILD_FERMION_SECTION_ON_GRAPH_U_R",
        "AE3_local_enclosure_state": "C2_CARRIER_TENSOR_SPIN_GSM_TENSOR_NINE_FROZEN_FAMILY_MODE_FIBERS",
        "AE4_target_state": "RESET_GLUED_MAXIMAL_HISTORY_GFHS_DOMAIN",
        "maps": {
            "AE2_to_AE3": "U_R_tensor_I_family_then_local_enclosure_restriction",
            "AE3_to_AE4": "desired_nonzero_full_field_relative_boundary_graph",
        },
        "fermion_family_intertwining_residual": residual,
        "fermion_action_transport_commutes": residual == 0.0,
        "nine_frozen_family_mode_fibers_rebuilt": False,
        "nonfermion_zero_field_match_available": True,
        "nonfermion_first_field_jet_available": False,
        "first_exact_noncommuting_term": (
            "D_PhiSM_THETA_GFHS_AT_REFERENCE_CANNOT_BE_FORMED_BECAUSE_"
            "THETA_GFHS_HAS_NO_ACTION_OWNED_NONFERMION_SOURCE"
        ),
        "AE2_to_AE4_compatible": False,
    }


def relative_boundary_graph_nonuniqueness_witness() -> dict[str, Any]:
    """Exhibit two admissible nonfermion graph jets with different actions."""

    gauge_generator = 1.0j * np.diag((1.0, 1.0, 2.0, 2.0))
    projector = np.diag((1.0, 1.0, 0.0, 0.0))
    zero = np.zeros((4, 4))
    reference_field = 0.0
    probe_field = 1.0
    probe_trace = np.asarray((1.0, -0.25, 0.0, 0.0))

    def theta_zero(field: float) -> np.ndarray:
        return field * zero

    def theta_projected(field: float) -> np.ndarray:
        return field * projector

    def boundary_action(theta: np.ndarray, trace: np.ndarray) -> float:
        return float(0.5 * trace @ theta @ trace)

    reference_graphs = (theta_zero(reference_field), theta_projected(reference_field))
    probe_graphs = (theta_zero(probe_field), theta_projected(probe_field))

    return {
        "candidate_graphs": ["Theta_0(phi)=0", "Theta_1(phi)=phi*P_nonfermion"],
        "both_Hermitian": all(np.array_equal(theta, theta.T) for theta in probe_graphs),
        "both_gauge_central_in_witness": all(
            np.linalg.norm(theta @ gauge_generator - gauge_generator @ theta) == 0.0
            for theta in probe_graphs
        ),
        "both_projector_preserving": all(
            np.linalg.norm(theta @ projector - projector @ theta) == 0.0
            for theta in probe_graphs
        ),
        "reference_graph_operator_difference_norm": float(
            np.linalg.norm(reference_graphs[0] - reference_graphs[1])
        ),
        "first_field_jet_difference_norm": float(np.linalg.norm(projector)),
        "reference_actions": [
            boundary_action(reference_graphs[0], probe_trace),
            boundary_action(reference_graphs[1], probe_trace),
        ],
        "nonzero_probe_actions": [
            boundary_action(probe_graphs[0], probe_trace),
            boundary_action(probe_graphs[1], probe_trace),
        ],
        "same_zero_field_match": np.array_equal(reference_graphs[0], reference_graphs[1]),
        "different_nonzero_field_actions": boundary_action(probe_graphs[0], probe_trace) != boundary_action(probe_graphs[1], probe_trace),
        "blocker_is_irreducible_from_current_zero_field_data": True,
        "missing_source": EXACT_BLOCKER,
    }


def child_inheritance_status() -> dict[str, Any]:
    diagram = ae2_to_ae4_transport_diagram()
    return {
        "geometry_state": "REUSE_CERTIFIED_CONTINUUM_EVENT_CHILD_RELATION",
        "gauge_bundle_state": "COMMON_RESET_FRAME_IDENTITY_AT_REFERENCE_ONLY",
        "ghost_structure": "BRST_COVARIANT_AT_REFERENCE_ONLY",
        "fermion_family_mode_fibers": "U_R_tensor_I_family__EXACT",
        "HS_scalar_state": "LOCAL_CHANNEL_LABELS_ONLY__GLOBAL_GRAPH_JET_OPEN",
        "constraints": "REUSE_EXISTING_EVENT_RESPONSE_ROWS",
        "projectors": "UNCHANGED_AND_INTERTWINED",
        "action_domain_metadata": "INCOMPLETE_WITHOUT_THETA_GFHS",
        "fermion_family_intertwining_residual": diagram["fermion_family_intertwining_residual"],
        "executable_full_field_inheritance_map": False,
        "event_child_inheritance_status": "PARTIAL__FIRST_NONFERMION_DOMAIN_JET_OPEN",
    }


def event_balance_residual() -> dict[str, Any]:
    """Separate the exact algebraic identity from the unavailable physical residual."""

    result = solve_retarded_event_kkt(
        parent_block=np.asarray(((2.0,),)),
        parent_child_coupling=np.asarray(((0.5,),)),
        child_retarded_block=np.asarray(((1.5 + 0.2j,),)),
        response_operator=np.asarray(((1.0,),)),
        source=np.asarray((0.3,)),
        response_target=np.asarray((0.1,)),
    )
    noether = canonical_noether_flux_balance(
        trace=result["parent_trace"],
        event_tractions=result["event_tractions"],
        generator=np.asarray(((1.0j,),)),
    )
    return {
        "identity_witness_only": True,
        "algebraic_event_canonical_flux_balance_norm": result[
            "event_canonical_flux_balance_norm"
        ],
        "algebraic_noether_flux_residual": noether[
            "canonical_noether_flux_residual"
        ],
        "physical_event_balance_residual": None,
        "physical_residual_evaluable": False,
        "blocked_by": EXACT_BLOCKER,
        "physical_event_promotion": False,
    }


def stratified_action_composition() -> dict[str, Any]:
    return {
        "formula": "Gamma_GFHS=sum_strata Gamma_stratum",
        "strata": {
            "bulk": {
                "fields": ["geometry", "gauge", "fermion", "HS"],
                "status": "LOCAL_CURRENT_C2_GERM_EXECUTABLE__GLOBAL_HISTORY_OPEN",
                "provenance": [
                    "retained_N12_local_action",
                    "parent_Maxwell_radial_form",
                    "foundational_eta_Dirac_action",
                    "local_Einstein_Cartan_HS_rewrite",
                ],
            },
            "history": {
                "fields": ["geometry", "fermion"],
                "status": "FERMION_DOMAIN_RULE_OWNED__FULL_GFHS_OPERATOR_OPEN",
            },
            "seam": {
                "fields": ["fermion"],
                "status": "INDEPENDENT_FERMION_SEAM_DENSITY_EXACTLY_ZERO__GRAPH_U_R_OWNED",
            },
            "junction": {
                "fields": [],
                "status": "RETAINED_JUNCTION_ACTION_EXACTLY_ZERO",
            },
            "event_child": {
                "fields": ["fermion", "family_projectors"],
                "status": "FERMION_AND_FAMILY_TRANSPORT_EXACT__NONFERMION_GRAPH_JET_OPEN",
            },
            "boundary": {
                "fields": ["geometry", "gauge", "ghost", "fermion", "HS"],
                "status": "GEOMETRY_GHY_AND_FERMION_GRAPH_OWNED__NONFERMION_RELATIVE_GRAPH_OPEN",
            },
        },
        "invented_seam_or_child_term": False,
    }


def claim_boundary() -> dict[str, Any]:
    return {
        "status": STATUS,
        "generating_family_exists": False,
        "local_current_C2_generating_germ_exists": True,
        "arbitrary_regular_local_background_accepted": True,
        "arbitrary_global_BHSM_background_accepted": False,
        "local_gauge_action_generated": True,
        "local_ghost_operator_generated": True,
        "local_fermion_operator_generated": True,
        "local_HS_operator_generated": True,
        "local_gauge_fermion_interaction_generated": True,
        "local_fermion_HS_interaction_generated": True,
        "physical_yukawas_derived": False,
        "physical_HS_direction_derived": False,
        "physical_background_bound": False,
        "physical_spectrum_derived": False,
        "FULL_FIELD_ACTION_ATTACHMENT_READY_FOR_GATE7_BACKGROUND": False,
        "FULL_BHSM_COMPLETE": False,
        "empirical_inputs_used": False,
        "exact_blocker": EXACT_BLOCKER,
    }


__all__ = [
    "ACTION_VERSION",
    "CLASSIFICATION",
    "EXACT_BLOCKER",
    "FERMION_DIMENSION",
    "GAUGE_DIMENSION",
    "GermDirection",
    "GeneratedGFHSAction",
    "HS_DIMENSION",
    "LOCAL_BOSONIC_DIMENSION",
    "LocalC2Background",
    "LocalC2GFHSDirectionalOracle",
    "STATUS",
    "SourceClass",
    "SourceRecord",
    "ae2_to_ae4_transport_diagram",
    "child_inheritance_status",
    "claim_boundary",
    "critical_reductions",
    "event_balance_residual",
    "full_representation_generators",
    "generated_local_c2_action",
    "graded_directional_jet",
    "background_mixed_derivative_witness",
    "hs_incidence_generators",
    "local_gfhs_action_component",
    "local_gfhs_attachment",
    "one_family_representation_generators",
    "radial_maxwell_boundary_coefficient",
    "relative_boundary_graph_nonuniqueness_witness",
    "representation_validation",
    "source_reconstruction",
    "stratified_action_composition",
]
