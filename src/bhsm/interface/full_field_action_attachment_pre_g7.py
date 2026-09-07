"""Fail-closed, background-parametric full-field action attachment.

This module is an attachment layer, not a new BHSM action.  It gives one
deterministic field registry, one background authority contract, and one
matrix-free action-composition interface.  A sector is callable only when an
action-owned directional oracle has been supplied for it.  Historical
response matrices are deliberately ineligible as action components.

The retained N12 local geometry action is the only current numerical action
component installed by :func:`current_pre_g7_attachment`.  The current common
gauge/fermion/HS work specifies a regulated functional and evaluates response
seeds, but does not implement the interacting, current-domain operator family
needed to evaluate that functional on arbitrary fields and backgrounds.
Consequently all missing GFHS sectors fail closed.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence

import numpy as np

from bhsm.interface.aether_jax_full_local_action import (
    MDIM,
    QDIM,
    STATE_DIMENSION,
    action_value,
)
from bhsm.interface.universal_brst_quotient import (
    BRSTPhysicalQuotient,
    build_brst_physical_quotient,
)
from bhsm.interface.universal_momentum_map import ActionMomentumMap
from bhsm.interface.universal_physical_action_expansion import (
    DirectionalActionOracle,
    JaxDirectionalActionOracle,
)


Array = np.ndarray
ACTION_VERSION = "BHSM-AE-2.0.0"
ATTACHMENT_STATUS = "FULL_FIELD_ACTION_ATTACHMENT_FRAMEWORK_READY_GFHS_OPERATOR_FAMILY_OPEN"
DERIVATIVE_CONVENTION = "ORDERED_LEFT_DERIVATIVES_WITH_KOSZUL_EXCHANGE_SIGN"
SECTOR_ORDER = ("geometry", "gauge", "ghost", "fermion", "HS")
_PHYSICAL_BINDING_TOKEN = object()


class BackgroundState(str, Enum):
    UNBOUND_BACKGROUND = "UNBOUND_BACKGROUND"
    CERTIFIED_MATHEMATICAL_BACKGROUND = "CERTIFIED_MATHEMATICAL_BACKGROUND"
    PHYSICAL_BACKGROUND = "PHYSICAL_BACKGROUND"


class BlockStatus(str, Enum):
    ACTION_DERIVED = "ACTION_DERIVED"
    STRUCTURAL_ZERO = "STRUCTURAL_ZERO"
    BACKGROUND_GATED = "BACKGROUND_GATED"
    MISSING_ACTION_SOURCE = "MISSING_ACTION_SOURCE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class Statistics(str, Enum):
    BOSONIC = "BOSONIC"
    FERMIONIC = "FERMIONIC"


class MissingActionSourceError(RuntimeError):
    """Raised when a requested variation has no same-action owner."""


@dataclass(frozen=True)
class FieldBlock:
    name: str
    sector: str
    dimension: int
    start: int
    stop: int
    statistics: Statistics
    coordinate_role: str
    source: str
    labels: tuple[str, ...]
    coordinate_labels: tuple[str, ...]
    background_dependency: str

    @property
    def parity(self) -> int:
        return int(self.statistics is Statistics.FERMIONIC)

    @property
    def slice(self) -> slice:
        return slice(self.start, self.stop)

    def metadata(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "sector": self.sector,
            "dimension": self.dimension,
            "slice": [self.start, self.stop],
            "statistics": self.statistics.value,
            "coordinate_role": self.coordinate_role,
            "source": self.source,
            "labels": list(self.labels),
            "coordinate_labels": list(self.coordinate_labels),
            "background_dependency": self.background_dependency,
        }


@dataclass(frozen=True)
class FullFieldRegistry:
    blocks: tuple[FieldBlock, ...]
    realization_id: str
    formal_mode_multiplicities: tuple[tuple[str, int], ...]

    def __post_init__(self) -> None:
        cursor = 0
        names: set[str] = set()
        for block in self.blocks:
            if block.name in names:
                raise ValueError("field block names must be unique")
            if block.dimension < 0 or block.start != cursor or block.stop != cursor + block.dimension:
                raise ValueError("field blocks must be contiguous and correctly dimensioned")
            if len(block.coordinate_labels) != block.dimension or len(set(block.coordinate_labels)) != block.dimension:
                raise ValueError("every field coordinate requires one unique deterministic label")
            names.add(block.name)
            cursor = block.stop

    @property
    def dimension(self) -> int:
        return self.blocks[-1].stop if self.blocks else 0

    @property
    def sha256(self) -> str:
        payload = json.dumps(self.metadata(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode("utf-8")).hexdigest().upper()

    def block(self, name: str) -> FieldBlock:
        for block in self.blocks:
            if block.name == name:
                return block
        raise KeyError(name)

    def sector_blocks(self, sector: str) -> tuple[FieldBlock, ...]:
        return tuple(block for block in self.blocks if block.sector == sector)

    def restriction(self, name: str) -> Array:
        block = self.block(name)
        result = np.zeros((block.dimension, self.dimension), dtype=float)
        result[:, block.slice] = np.eye(block.dimension)
        return result

    def projector(self, name: str) -> Array:
        restriction = self.restriction(name)
        return restriction.T @ restriction

    def coordinate_projector(self, name: str, coordinate_labels: Sequence[str]) -> Array:
        """Return a square projector onto named coordinates within one block."""

        block = self.block(name)
        requested = tuple(coordinate_labels)
        if len(set(requested)) != len(requested):
            raise ValueError("coordinate projector labels must be unique")
        positions = {label: block.start + index for index, label in enumerate(block.coordinate_labels)}
        if any(label not in positions for label in requested):
            raise KeyError("coordinate projector label is not registered in the selected block")
        result = np.zeros((self.dimension, self.dimension), dtype=float)
        for label in requested:
            result[positions[label], positions[label]] = 1.0
        return result

    def embed(self, name: str, coordinates: Array) -> Array:
        block = self.block(name)
        value = np.asarray(coordinates)
        if value.shape != (block.dimension,):
            raise ValueError(f"{name} coordinates have the wrong dimension")
        result = np.zeros(self.dimension, dtype=value.dtype)
        result[block.slice] = value
        return result

    def direction_parity(self, direction: Array, *, tolerance: float = 0.0) -> int:
        value = np.asarray(direction)
        if value.shape != (self.dimension,):
            raise ValueError("full-field direction has the wrong dimension")
        parities = {
            block.parity
            for block in self.blocks
            if np.any(np.abs(value[block.slice]) > tolerance)
        }
        if len(parities) > 1:
            raise ValueError("a graded direction must have homogeneous parity")
        return next(iter(parities), 0)

    def active_sectors(self, value: Array, *, tolerance: float = 0.0) -> tuple[str, ...]:
        state = np.asarray(value)
        if state.shape != (self.dimension,):
            raise ValueError("full-field state has the wrong dimension")
        return tuple(dict.fromkeys(
            block.sector
            for block in self.blocks
            if np.any(np.abs(state[block.slice]) > tolerance)
        ))

    def active_blocks(self, value: Array, *, tolerance: float = 0.0) -> tuple[str, ...]:
        state = np.asarray(value)
        if state.shape != (self.dimension,):
            raise ValueError("full-field state has the wrong dimension")
        return tuple(
            block.name
            for block in self.blocks
            if np.any(np.abs(state[block.slice]) > tolerance)
        )

    def metadata(self) -> dict[str, Any]:
        return {
            "realization_id": self.realization_id,
            "dimension": self.dimension,
            "ordering": [block.name for block in self.blocks],
            "blocks": [block.metadata() for block in self.blocks],
            "formal_mode_multiplicities": dict(self.formal_mode_multiplicities),
            "physical_discretization_claimed": False,
            "projector_interface_ready": True,
        }


def authoritative_field_registry(
    *,
    gauge_modes: int = 1,
    ghost_modes: int = 1,
    fermion_modes: int = 1,
    hs_modes: int = 1,
) -> FullFieldRegistry:
    """Return the deterministic retained-fiber registry.

    The four mode counts are explicit realization parameters.  Their default
    value of one means one formal basis element per retained internal fiber;
    it is useful for interface tests but is not a physical discretization.
    Internal ranks (12 gauge generators, 48 Weyl species, four HS channels)
    come from the retained bundle/superdeterminant ledgers.
    """

    modes = {
        "gauge": int(gauge_modes),
        "ghost": int(ghost_modes),
        "fermion": int(fermion_modes),
        "HS": int(hs_modes),
    }
    if any(value < 1 for value in modes.values()):
        raise ValueError("all formal field mode multiplicities must be positive")
    if modes["gauge"] != modes["ghost"]:
        raise ValueError("gauge and ghost realizations must use the same mode multiplicity")

    geometry_labels = (
        ("scale",)
        + tuple(f"u_{index}" for index in range(1, QDIM // 3 + 1))
        + tuple(f"w_{index}" for index in range(QDIM // 3))
        + tuple(f"v_{index}" for index in range(QDIM // 3))
    )
    velocity_labels = tuple(f"dot_{name}" for name in geometry_labels)
    multiplier_labels = (
        tuple(f"lapse_{index}" for index in range(1, MDIM // 2 + 1))
        + tuple(f"shift_{index}" for index in range(MDIM // 2))
    )
    gauge_fiber = ("U1_Y",) + tuple(f"SU2_{index}" for index in range(1, 4)) + tuple(
        f"SU3_{index}" for index in range(1, 9)
    )

    def mode_labels(prefix: str, count: int, fiber: Sequence[str]) -> tuple[str, ...]:
        return tuple(
            f"mode_{mode}:{prefix}:{coordinate}"
            for mode in range(count)
            for coordinate in fiber
        )

    fermion_fiber = (
        tuple(f"Q_L:{color}:{weak}" for color in ("r", "g", "b") for weak in ("up", "down"))
        + ("L_L:nu", "L_L:charged")
        + tuple(f"u_c:{color}" for color in ("r", "g", "b"))
        + tuple(f"d_c:{color}" for color in ("r", "g", "b"))
        + ("e_c", "nu_c")
    )
    fermion_labels = tuple(
        f"mode_{mode}:family_{family}:{coordinate}"
        for mode in range(modes["fermion"])
        for family in range(3)
        for coordinate in fermion_fiber
    )
    antifermion_labels = tuple(f"bar:{label}" for label in fermion_labels)
    hs_fiber = ("up", "down", "charged_lepton", "neutrino")
    definitions = (
        ("geometry", "geometry", QDIM, Statistics.BOSONIC, "DYNAMICAL", "aether_sobolev_galerkin_pencil_lift_v15_81:lift_low_state", ("N12", "configuration"), geometry_labels, "GATE7_REALIZATION"),
        ("geometry_velocity", "geometry", QDIM, Statistics.BOSONIC, "VELOCITY", "aether_sobolev_galerkin_pencil_lift_v15_81:generalized_lagrangian", ("N12", "velocity"), velocity_labels, "GATE7_REALIZATION"),
        ("constraint_multiplier", "geometry", MDIM, Statistics.BOSONIC, "MULTIPLIER", "aether_sobolev_galerkin_pencil_lift_v15_81:generalized_lagrangian", ("N12", "lapse_then_shift"), multiplier_labels, "GATE7_REALIZATION"),
        ("gauge", "gauge", 12 * modes["gauge"], Statistics.BOSONIC, "DYNAMICAL", "aether_common_quantum_superdeterminant_v15_96:graded_operator_ledger.gauge_transverse", ("U1", "SU2", "SU3", "mode_outer_internal_inner"), mode_labels("gauge", modes["gauge"], gauge_fiber), "CURRENT_DOMAIN_BASIS_AND_BACKGROUND"),
        ("ghost", "ghost", 12 * modes["ghost"], Statistics.FERMIONIC, "GHOST", "aether_nonabelian_derham_response_v16_04:full_oneform_ghost_matrices", ("U1", "SU2", "SU3", "mode_outer_internal_inner"), mode_labels("ghost", modes["ghost"], gauge_fiber), "GAUGE_CONDITION_AND_CURRENT_DOMAIN"),
        ("antighost", "ghost", 12 * modes["ghost"], Statistics.FERMIONIC, "ANTIGHOST", "aether_nonabelian_derham_response_v16_04:full_oneform_ghost_matrices", ("U1", "SU2", "SU3", "independent_left_coordinate"), mode_labels("antighost", modes["ghost"], gauge_fiber), "GAUGE_CONDITION_AND_CURRENT_DOMAIN"),
        ("fermion", "fermion", 48 * modes["fermion"], Statistics.FERMIONIC, "DYNAMICAL", "BHSM_aether_hybrid_standard_model_bundle_v15_53:chiral_bundle.multiplets", ("family_outer_multiplet_inner", "left_Weyl", "nu_c_included_rank16"), fermion_labels, "SPIN_DOMAIN_AND_CURRENT_BACKGROUND"),
        ("antifermion", "fermion", 48 * modes["fermion"], Statistics.FERMIONIC, "INDEPENDENT_CONJUGATE", "BHSM_aether_hybrid_standard_model_bundle_v15_53:chiral_bundle.multiplets", ("family_outer_multiplet_inner", "ordered_left_derivative", "nu_c_included_rank16"), antifermion_labels, "SPIN_DOMAIN_AND_CURRENT_BACKGROUND"),
        ("HS_scalar", "HS", 4 * modes["HS"], Statistics.BOSONIC, "AUXILIARY_OR_DYNAMICAL_AFTER_HESSIAN", "aether_hs_channel_normalization_v16_02:hs_channel_normalization.channel_basis", ("up", "down", "charged_lepton", "neutrino", "mode_outer_channel_inner"), mode_labels("HS", modes["HS"], hs_fiber), "SAME_ACTION_SADDLE_AND_HS_HESSIAN"),
    )
    cursor = 0
    blocks: list[FieldBlock] = []
    for name, sector, dimension, statistics, role, source, labels, coordinate_labels, dependency in definitions:
        blocks.append(FieldBlock(
            name=name,
            sector=sector,
            dimension=dimension,
            start=cursor,
            stop=cursor + dimension,
            statistics=statistics,
            coordinate_role=role,
            source=source,
            labels=labels,
            coordinate_labels=coordinate_labels,
            background_dependency=dependency,
        ))
        cursor += dimension
    return FullFieldRegistry(
        tuple(blocks),
        realization_id=(
            "FORMAL_ONE_BASIS_ELEMENT_PER_RETAINED_FIELD_FIBER"
            if all(value == 1 for value in modes.values())
            else "PARAMETRIC_FINITE_LAYOUT_REQUIRES_REALIZATION_AUTHORITY"
        ),
        formal_mode_multiplicities=tuple(modes.items()),
    )


def _array_sha256(value: Array) -> str:
    array = np.ascontiguousarray(np.asarray(value))
    descriptor = f"{array.dtype.str}|{array.shape}|".encode("ascii")
    return hashlib.sha256(descriptor + array.tobytes()).hexdigest().upper()


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


@dataclass(frozen=True)
class BoundBackground:
    state: BackgroundState
    action_version: str
    background_id: str | None = None
    domain_id: str | None = None
    geometry_background_sha256: str | None = None
    field_registry_sha256: str | None = None
    domain_sha256: str | None = None
    metric_tetrad_sha256: str | None = None
    authority_path: str | None = None
    authority_sha256: str | None = None
    provenance: tuple[str, ...] = ()
    verified_source_sha256: tuple[tuple[str, str], ...] = ()
    _physical_binding_token: object | None = None

    @property
    def physical(self) -> bool:
        return (
            self.state is BackgroundState.PHYSICAL_BACKGROUND
            and self._physical_binding_token is _PHYSICAL_BINDING_TOKEN
        )

    def require_physical(self) -> None:
        if not self.physical:
            raise RuntimeError("physical promotion requires a hash-validated Gate-7 authority")

    def require_state(self, state: Array) -> None:
        self.require_physical()
        value = np.asarray(state)
        if value.ndim != 1 or value.size < STATE_DIMENSION:
            raise RuntimeError("evaluated field state does not contain the retained geometry background")
        if _array_sha256(value[:STATE_DIMENSION]) != self.geometry_background_sha256:
            raise RuntimeError("evaluated geometry does not match the bound physical background")

    def metadata(self) -> dict[str, Any]:
        return {
            "state": self.state.value,
            "action_version": self.action_version,
            "background_id": self.background_id,
            "domain_id": self.domain_id,
            "geometry_background_sha256": self.geometry_background_sha256,
            "field_registry_sha256": self.field_registry_sha256,
            "domain_sha256": self.domain_sha256,
            "metric_tetrad_sha256": self.metric_tetrad_sha256,
            "authority_path": self.authority_path,
            "authority_sha256": self.authority_sha256,
            "provenance": list(self.provenance),
            "verified_source_sha256": dict(self.verified_source_sha256),
            "physical_promotion_allowed": self.physical,
        }


class FullFieldBackgroundBinder:
    """Bind mathematical centers or strict future Gate-7 authority artifacts."""

    def __init__(
        self,
        action_version: str = ACTION_VERSION,
        *,
        trusted_authority_path: str | Path | None = None,
        trusted_authority_sha256: str | None = None,
    ) -> None:
        self.action_version = action_version
        self._trusted_authority_path = (
            Path(trusted_authority_path).resolve() if trusted_authority_path is not None else None
        )
        self._trusted_authority_sha256 = (
            trusted_authority_sha256.upper() if trusted_authority_sha256 is not None else None
        )
        if (self._trusted_authority_path is None) != (self._trusted_authority_sha256 is None):
            raise ValueError("trusted Gate-7 authority path and hash must be configured together")
        if self._trusted_authority_sha256 is not None and (
            len(self._trusted_authority_sha256) != 64
            or any(character not in "0123456789ABCDEF" for character in self._trusted_authority_sha256)
        ):
            raise ValueError("trusted Gate-7 authority hash must be a SHA-256 digest")

    def unbound(self) -> BoundBackground:
        return BoundBackground(BackgroundState.UNBOUND_BACKGROUND, self.action_version)

    def bind_mathematical(
        self,
        state: Array,
        *,
        background_id: str,
        domain_id: str,
        provenance: tuple[str, ...],
    ) -> BoundBackground:
        value = np.asarray(state)
        if value.ndim != 1 or not np.all(np.isfinite(value)) or not provenance:
            raise ValueError("finite mathematical state and provenance are required")
        return BoundBackground(
            state=BackgroundState.CERTIFIED_MATHEMATICAL_BACKGROUND,
            action_version=self.action_version,
            background_id=background_id,
            domain_id=domain_id,
            geometry_background_sha256=_array_sha256(value),
            provenance=provenance,
        )

    def bind_physical(
        self,
        state: Array,
        authority_path: str | Path,
        *,
        registry: FullFieldRegistry,
        source_root: str | Path,
    ) -> BoundBackground:
        """Bind only the explicit future authority contract.

        The authority JSON must set both ``Gate7_closed`` and
        ``physical_background_authorized`` to true and must bind the exact
        action version, background/domain identifiers, and state digest.
        """

        if self._trusted_authority_path is None or self._trusted_authority_sha256 is None:
            raise RuntimeError("no trusted Gate-7 authority is configured")
        value = np.asarray(state)
        if value.shape != (STATE_DIMENSION,) or not np.all(np.isfinite(value)):
            raise ValueError("finite retained 98-coordinate Gate-7 geometry background is required")
        path = Path(authority_path).resolve()
        if path != self._trusted_authority_path:
            raise ValueError("Gate-7 authority path is not the configured trust anchor")
        actual_digest = _file_sha256(path)
        if actual_digest != self._trusted_authority_sha256:
            raise ValueError("Gate-7 authority hash mismatch")
        payload = json.loads(path.read_text(encoding="utf-8"))
        required = {
            "artifact": "BHSM_N12_GATE7_PHYSICAL_BACKGROUND_AUTHORITY",
            "schema_version": 1,
            "validation_passed": True,
            "Gate7_closed": True,
            "physical_background_authorized": True,
            "action_version": self.action_version,
            "background_state_sha256": _array_sha256(value),
            "field_registry_sha256": registry.sha256,
        }
        for key, expected in required.items():
            if payload.get(key) != expected:
                raise ValueError(f"Gate-7 authority contract rejected field: {key}")
        background_id = payload.get("background_id")
        domain_id = payload.get("domain_id")
        provenance = payload.get("provenance")
        if not isinstance(background_id, str) or not background_id:
            raise ValueError("Gate-7 authority background_id is required")
        if not isinstance(domain_id, str) or not domain_id:
            raise ValueError("Gate-7 authority domain_id is required")
        if not isinstance(provenance, list) or not provenance:
            raise ValueError("Gate-7 authority provenance is required")
        domain_digest = payload.get("domain_sha256")
        metric_digest = payload.get("metric_tetrad_sha256")
        if not all(
            isinstance(item, str)
            and len(item) == 64
            and all(character in "0123456789abcdefABCDEF" for character in item)
            for item in (domain_digest, metric_digest)
        ):
            raise ValueError("Gate-7 authority domain and metric/tetrad hashes are required")
        dependency_hashes = payload.get("source_sha256")
        if not isinstance(dependency_hashes, dict) or not dependency_hashes:
            raise ValueError("Gate-7 authority source_sha256 ledger is required")
        domain_artifact = payload.get("domain_artifact")
        metric_artifact = payload.get("metric_tetrad_artifact")
        realization_artifact = payload.get("field_registry_realization_artifact")
        if not all(isinstance(item, str) for item in (domain_artifact, metric_artifact, realization_artifact)):
            raise ValueError("Gate-7 authority domain, metric, and registry-realization paths are required")
        if dependency_hashes.get(domain_artifact, "").upper() != domain_digest.upper():
            raise ValueError("Gate-7 authority domain hash is not bound to its source artifact")
        if dependency_hashes.get(metric_artifact, "").upper() != metric_digest.upper():
            raise ValueError("Gate-7 authority metric/tetrad hash is not bound to its source artifact")
        realization_digest = payload.get("field_registry_realization_sha256")
        if dependency_hashes.get(realization_artifact, "").upper() != str(realization_digest).upper():
            raise ValueError("Gate-7 authority registry realization is not bound to its source artifact")
        root = Path(source_root).resolve()
        for relative, expected_digest in dependency_hashes.items():
            if not isinstance(relative, str) or not isinstance(expected_digest, str):
                raise ValueError("Gate-7 authority source hash ledger is malformed")
            dependency = (root / relative).resolve()
            try:
                dependency.relative_to(root)
            except ValueError as error:
                raise ValueError("Gate-7 authority dependency escapes source_root") from error
            if not dependency.is_file() or _file_sha256(dependency) != expected_digest.upper():
                raise ValueError(f"Gate-7 authority dependency hash mismatch: {relative}")
        return BoundBackground(
            state=BackgroundState.PHYSICAL_BACKGROUND,
            action_version=self.action_version,
            background_id=background_id,
            domain_id=domain_id,
            geometry_background_sha256=required["background_state_sha256"],
            field_registry_sha256=registry.sha256,
            domain_sha256=domain_digest.upper(),
            metric_tetrad_sha256=metric_digest.upper(),
            authority_path=str(path),
            authority_sha256=actual_digest,
            provenance=tuple(str(item) for item in provenance),
            verified_source_sha256=tuple(
                sorted((str(relative), str(digest).upper()) for relative, digest in dependency_hashes.items())
            ),
            _physical_binding_token=_PHYSICAL_BINDING_TOKEN,
        )


@dataclass(frozen=True)
class ActionComponent:
    component_id: str
    sectors: frozenset[str]
    field_blocks: frozenset[str]
    oracle: DirectionalActionOracle
    action_version: str
    source_action_version: str
    source: str
    source_sha256: str
    provenance: tuple[str, ...]
    background_parametric: bool
    derivative_signatures: frozenset[tuple[str, ...]]
    field_registry_sha256: str
    background_id: str | None
    domain_id: str | None
    domain_scope: str
    domain_coverage_source: str | None = None
    domain_coverage_sha256: str | None = None
    version_transition_source: str | None = None
    version_transition_sha256: str | None = None
    graded_left_derivatives: bool = False
    complete_within_owned_blocks: bool = False
    zero_reference_subtracted: bool = False
    geometry_reduction_preserved: bool = False
    empirical_input_used: bool = False
    response_object_only: bool = False

    def __post_init__(self) -> None:
        if not self.component_id or not self.sectors or not self.field_blocks or not self.provenance:
            raise ValueError("component identity, sectors, field blocks, and provenance are required")
        if len(self.source_sha256) != 64 or any(
            character not in "0123456789abcdefABCDEF" for character in self.source_sha256
        ):
            raise ValueError("component source hash is required")
        if not self.derivative_signatures:
            raise ValueError("component derivative signatures are required")
        for signature in self.derivative_signatures:
            if not 1 <= len(signature) <= 4 or not set(signature) <= set(self.sectors):
                raise ValueError("component derivative signature is outside its owned sectors")
            index = {sector: position for position, sector in enumerate(SECTOR_ORDER)}
            if tuple(sorted(signature, key=index.__getitem__)) != signature:
                raise ValueError("component derivative signatures must use canonical sector order")
        if self.sectors.intersection(("ghost", "fermion")) and not self.graded_left_derivatives:
            raise ValueError("components containing odd fields require a graded left-derivative oracle")
        if self.source_action_version != self.action_version and not (
            self.version_transition_source
            and self.version_transition_sha256
            and len(self.version_transition_sha256) == 64
        ):
            raise ValueError("cross-version action components require an explicit transition certificate")
        if self.empirical_input_used:
            raise ValueError("empirical-input action components are forbidden")
        if self.response_object_only:
            raise ValueError("response objects cannot be registered as action components")
        if "geometry" not in self.sectors and not (
            self.zero_reference_subtracted and self.geometry_reduction_preserved
        ):
            raise ValueError("nongeometry components must certify zero-reference subtraction")


class FullFieldComponentFactory(Protocol):
    """The missing same-domain GFHS owner must satisfy this protocol."""

    def build_action_component(
        self, registry: FullFieldRegistry, background: BoundBackground
    ) -> ActionComponent: ...


class FullFieldGaugeGeneratorProvider(Protocol):
    """Action/domain owner for the complete gauge orbit and gauge condition."""

    @property
    def gauge_condition_id(self) -> str: ...

    @property
    def provenance(self) -> tuple[str, ...]: ...

    @property
    def action_version(self) -> str: ...

    @property
    def background_id(self) -> str: ...

    @property
    def domain_id(self) -> str: ...

    @property
    def field_registry_sha256(self) -> str: ...

    def tangent_constraints(
        self, registry: FullFieldRegistry, background: BoundBackground
    ) -> Array: ...

    def gauge_generators(
        self, registry: FullFieldRegistry, background: BoundBackground
    ) -> Array: ...

    def gauge_condition_derivative(
        self, registry: FullFieldRegistry, background: BoundBackground
    ) -> Array: ...


class _EmbeddedGeometryOracle:
    def __init__(self, registry: FullFieldRegistry) -> None:
        self._registry = registry
        self._oracle = JaxDirectionalActionOracle(action_value)
        self._geometry_stop = registry.block("constraint_multiplier").stop
        layout = tuple(
            (block.name, block.dimension, block.start, block.stop)
            for block in registry.blocks[:3]
        )
        expected = (
            ("geometry", QDIM, 0, QDIM),
            ("geometry_velocity", QDIM, QDIM, 2 * QDIM),
            ("constraint_multiplier", MDIM, 2 * QDIM, STATE_DIMENSION),
        )
        if layout != expected or self._geometry_stop != STATE_DIMENSION:
            raise RuntimeError("retained geometry registry no longer matches the N12 action")

    def _extract(self, value: Array) -> Array:
        array = np.asarray(value)
        if array.shape != (self._registry.dimension,):
            raise ValueError("full-field vector has the wrong dimension")
        if np.iscomplexobj(array) and np.any(array[:self._geometry_stop].imag != 0.0):
            raise ValueError("retained N12 geometry coordinates and directions must be real")
        return np.asarray(array[:self._geometry_stop], dtype=float)

    def value(self, state: Array) -> float:
        return self._oracle.value(self._extract(state))

    def derivative(self, state: Array, directions: Sequence[Array]) -> float:
        return self._oracle.derivative(
            self._extract(state), tuple(self._extract(direction) for direction in directions)
        )


def koszul_permutation_sign(parities: Sequence[int], permutation: Sequence[int]) -> int:
    """Return the sign from exchanging odd ordered left derivatives."""

    parity = tuple(int(value) for value in parities)
    order = tuple(int(value) for value in permutation)
    if any(value not in (0, 1) for value in parity) or sorted(order) != list(range(len(parity))):
        raise ValueError("binary parities and a valid permutation are required")
    inversions = 0
    for left in range(len(order)):
        for right in range(left + 1, len(order)):
            if order[left] > order[right] and parity[order[left]] and parity[order[right]]:
                inversions += 1
    return -1 if inversions % 2 else 1


class UniversalFullFieldAction:
    """One additive action with guarded, matrix-free ordered derivatives."""

    def __init__(
        self,
        registry: FullFieldRegistry,
        background: BoundBackground,
        components: Sequence[ActionComponent],
        block_status: Mapping[tuple[str, str], BlockStatus],
        structural_zero_provenance: Mapping[tuple[str, str], tuple[str, ...]] | None = None,
    ) -> None:
        self.registry = registry
        self.background = background
        self.components = tuple(components)
        self.block_status = dict(block_status)
        self.structural_zero_provenance = dict(structural_zero_provenance or {})
        if any(component.action_version != background.action_version for component in self.components):
            raise ValueError("all action components must share the bound action version")
        if any(component.field_registry_sha256 != registry.sha256 for component in self.components):
            raise ValueError("all action components must share the exact field registry")
        block_names = {block.name for block in registry.blocks}
        for component in self.components:
            if not set(component.field_blocks) <= block_names:
                raise ValueError("action component names an unregistered field block")
            block_sectors = {registry.block(name).sector for name in component.field_blocks}
            if block_sectors != set(component.sectors):
                raise ValueError("action component sector and field-block ownership differ")
        expected_pairs = {
            (left, right)
            for left_index, left in enumerate(SECTOR_ORDER)
            for right in SECTOR_ORDER[left_index:]
        }
        if set(self.block_status) != expected_pairs:
            raise ValueError("quadratic block status must contain exactly the fifteen canonical pairs")
        if background.physical:
            if background.field_registry_sha256 != registry.sha256:
                raise ValueError("physical background and action registry hashes differ")
            if registry.realization_id == "FORMAL_ONE_BASIS_ELEMENT_PER_RETAINED_FIELD_FIBER":
                raise ValueError("formal field registry cannot back a physical action")
        owned = self._owned_sectors()
        for pair, status in self.block_status.items():
            normalized = self._normalized_signature(pair)
            required_blocks = {
                block.name for block in registry.blocks if block.sector in set(pair)
            }
            block_owners = [
                component
                for component in self.components
                if normalized in component.derivative_signatures
                and required_blocks <= set(component.field_blocks)
                and component.complete_within_owned_blocks
            ]
            if status is BlockStatus.ACTION_DERIVED and not block_owners:
                raise ValueError(f"ACTION_DERIVED block lacks a component signature: {pair}")
            if status in (BlockStatus.ACTION_DERIVED, BlockStatus.STRUCTURAL_ZERO) and not set(pair) <= set(owned):
                raise ValueError(f"owned block classification lacks sector action owners: {pair}")
            if status is BlockStatus.STRUCTURAL_ZERO and not self.structural_zero_provenance.get(pair):
                raise ValueError(f"STRUCTURAL_ZERO block lacks action/BRST provenance: {pair}")

    def _check_state(self, state: Array) -> Array:
        value = np.asarray(state)
        if value.shape != (self.registry.dimension,) or not np.all(np.isfinite(value)):
            raise ValueError("finite full-field state with registry dimension required")
        return value

    def _owned_sectors(self) -> frozenset[str]:
        return frozenset().union(*(component.sectors for component in self.components))

    def _owned_blocks(self) -> frozenset[str]:
        return frozenset().union(*(component.field_blocks for component in self.components))

    @staticmethod
    def _normalized_signature(sectors: Sequence[str]) -> tuple[str, ...]:
        index = {sector: position for position, sector in enumerate(SECTOR_ORDER)}
        return tuple(sorted(sectors, key=index.__getitem__))

    def _require_value_coverage(self, state: Array) -> None:
        missing = set(self.registry.active_blocks(state)) - set(self._owned_blocks())
        if missing:
            raise MissingActionSourceError(
                "nonzero fields have no same-action owner: " + ", ".join(sorted(missing))
            )

    def value(self, state: Array) -> float:
        value = self._check_state(state)
        if self.background.physical:
            self.background.require_state(value)
        self._require_value_coverage(value)
        return float(sum(component.oracle.value(value) for component in self.components))

    def derivative(self, state: Array, directions: Sequence[Array]) -> float | complex:
        value = self._check_state(state)
        if self.background.physical:
            self.background.require_state(value)
        self._require_value_coverage(value)
        if not 1 <= len(directions) <= 4:
            raise ValueError("directional derivative order must be between one and four")
        requested: list[str] = []
        requested_blocks: set[str] = set()
        for direction in directions:
            vector = self._check_state(direction)
            self.registry.direction_parity(vector)
            active = self.registry.active_sectors(vector)
            if len(active) > 1:
                raise ValueError("each directional argument must lie in one registered sector")
            if not active:
                return 0.0
            requested.append(active[0])
            requested_blocks.update(self.registry.active_blocks(vector))
        signature = self._normalized_signature(requested)
        eligible = [
            component
            for component in self.components
            if signature in component.derivative_signatures
            and requested_blocks <= set(component.field_blocks)
        ]
        if not eligible:
            if len(signature) == 2:
                pair = (signature[0], signature[1])
                if self.block_status[pair] is BlockStatus.STRUCTURAL_ZERO:
                    return 0.0
            raise MissingActionSourceError(
                "requested derivative has no same-action component signature: "
                + "-".join(signature)
            )
        result = sum(component.oracle.derivative(value, directions) for component in eligible)
        if not np.isfinite(result):
            raise ArithmeticError("non-finite full-field action derivative")
        return result

    def s1(self, state: Array, direction: Array) -> float | complex:
        return self.derivative(state, (direction,))

    def s2(self, state: Array, first: Array, second: Array) -> float | complex:
        return self.derivative(state, (first, second))

    def s3(self, state: Array, first: Array, second: Array, third: Array) -> float | complex:
        return self.derivative(state, (first, second, third))

    def s4(self, state: Array, first: Array, second: Array, third: Array, fourth: Array) -> float | complex:
        return self.derivative(state, (first, second, third, fourth))

    def require_physical_promotion(self, state: Array | None = None) -> None:
        self.background.require_physical()
        if state is None:
            raise RuntimeError("physical promotion requires the exact evaluated full-field state")
        self.background.require_state(self._check_state(state))
        if set(self._owned_blocks()) != {block.name for block in self.registry.blocks}:
            raise RuntimeError("physical promotion requires action owners for every full-field block")
        all_signatures = {
            self._normalized_signature(signature)
            for order in range(1, 5)
            for signature in itertools.combinations_with_replacement(SECTOR_ORDER, order)
        }
        owned_signatures = {
            signature
            for component in self.components
            for signature in component.derivative_signatures
        }
        if not all_signatures <= owned_signatures:
            raise RuntimeError("physical promotion requires S1/S2/S3/S4 coverage for every sector signature")
        for component in self.components:
            if (
                not component.background_parametric
                or component.background_id != self.background.background_id
                or component.domain_id != self.background.domain_id
                or component.domain_scope != "RESET_GLUED_MAXIMAL_HISTORY"
                or not component.complete_within_owned_blocks
            ):
                raise RuntimeError("physical promotion requires full-history background/domain-bound action components")
            verified = dict(self.background.verified_source_sha256)
            if verified.get(component.source) != component.source_sha256.upper():
                raise RuntimeError("physical promotion requires authority-verified component source hashes")
            if (
                not component.domain_coverage_source
                or verified.get(component.domain_coverage_source)
                != str(component.domain_coverage_sha256).upper()
            ):
                raise RuntimeError("physical promotion requires verified domain-coverage certificates")
            if component.source_action_version != component.action_version and (
                not component.version_transition_source
                or verified.get(component.version_transition_source)
                != str(component.version_transition_sha256).upper()
            ):
                raise RuntimeError("physical promotion requires an authority-verified action-version transition")
        incomplete = [
            f"{left}-{right}"
            for (left, right), status in self.block_status.items()
            if status not in (BlockStatus.ACTION_DERIVED, BlockStatus.STRUCTURAL_ZERO)
        ]
        if incomplete:
            raise RuntimeError("full-field physical promotion blocked by S2 blocks: " + ", ".join(incomplete))

    def metadata(self) -> dict[str, Any]:
        return {
            "action_version": self.background.action_version,
            "background": self.background.metadata(),
            "components": [
                {
                    "component_id": component.component_id,
                    "sectors": sorted(component.sectors),
                    "field_blocks": sorted(component.field_blocks),
                    "source_action_version": component.source_action_version,
                    "source": component.source,
                    "source_sha256": component.source_sha256,
                    "provenance": list(component.provenance),
                    "background_parametric": component.background_parametric,
                    "empirical_input_used": component.empirical_input_used,
                    "derivative_signatures": [list(item) for item in sorted(component.derivative_signatures)],
                    "graded_left_derivatives": component.graded_left_derivatives,
                    "zero_reference_subtracted": component.zero_reference_subtracted,
                    "geometry_reduction_preserved": component.geometry_reduction_preserved,
                    "domain_scope": component.domain_scope,
                    "complete_within_owned_blocks": component.complete_within_owned_blocks,
                    "domain_coverage_source": component.domain_coverage_source,
                    "version_transition_source": component.version_transition_source,
                }
                for component in self.components
            ],
            "derivative_orders": [1, 2, 3, 4],
            "derivative_convention": DERIVATIVE_CONVENTION,
            "dense_S3_or_S4_tensor_formed": False,
        }


def current_quadratic_block_status() -> dict[tuple[str, str], BlockStatus]:
    result: dict[tuple[str, str], BlockStatus] = {}
    for left_index, left in enumerate(SECTOR_ORDER):
        for right in SECTOR_ORDER[left_index:]:
            result[(left, right)] = BlockStatus.MISSING_ACTION_SOURCE
    return result


def current_pre_g7_attachment(
    background: BoundBackground | None = None,
    *,
    registry: FullFieldRegistry | None = None,
) -> UniversalFullFieldAction:
    fields = authoritative_field_registry() if registry is None else registry
    bound = FullFieldBackgroundBinder().unbound() if background is None else background
    geometry = ActionComponent(
        component_id="RETAINED_N12_LOCAL_GEOMETRY_ACTION",
        sectors=frozenset(("geometry",)),
        field_blocks=frozenset(("geometry", "geometry_velocity", "constraint_multiplier")),
        oracle=_EmbeddedGeometryOracle(fields),
        action_version=ACTION_VERSION,
        source_action_version=ACTION_VERSION,
        source="src/bhsm/interface/aether_jax_full_local_action.py",
        source_sha256=_file_sha256(Path(__file__).with_name("aether_jax_full_local_action.py")),
        provenance=(
            "96-point retained expression",
            "analytic S0-S2 authority:aether_n3_exact_full_local_action_jet_v17_60",
        ),
        background_parametric=True,
        derivative_signatures=frozenset(("geometry",) * order for order in range(1, 5)),
        field_registry_sha256=fields.sha256,
        background_id=bound.background_id,
        domain_id=bound.domain_id,
        domain_scope="LOCAL_N12_KERNEL",
        complete_within_owned_blocks=True,
        geometry_reduction_preserved=True,
    )
    return UniversalFullFieldAction(
        fields,
        bound,
        (geometry,),
        current_quadratic_block_status(),
    )


@dataclass(frozen=True)
class PreparedBRSTInterface:
    background: BoundBackground

    def build(self, *args: Any, **kwargs: Any) -> BRSTPhysicalQuotient:
        if self.background.state is BackgroundState.UNBOUND_BACKGROUND:
            raise RuntimeError("BRST quotient requires at least a mathematical background binding")
        for key, expected in (
            ("action_version", self.background.action_version),
            ("background_id", self.background.background_id),
        ):
            supplied = kwargs.pop(key, expected)
            if supplied != expected:
                raise ValueError(f"BRST {key} does not match the bound background")
            kwargs[key] = expected
        return build_brst_physical_quotient(*args, **kwargs)

    def build_from_provider(
        self,
        constant_symbol: Array,
        linear_symbol: Array,
        registry: FullFieldRegistry,
        provider: FullFieldGaugeGeneratorProvider,
    ) -> BRSTPhysicalQuotient:
        if self.background.state is BackgroundState.UNBOUND_BACKGROUND:
            raise RuntimeError("BRST quotient requires at least a mathematical background binding")
        identity = (
            provider.action_version,
            provider.background_id,
            provider.domain_id,
            provider.field_registry_sha256,
        )
        expected = (
            self.background.action_version,
            self.background.background_id,
            self.background.domain_id,
            registry.sha256,
        )
        if identity != expected:
            raise ValueError("gauge-generator provider identity does not match the bound action")
        constraints = np.asarray(provider.tangent_constraints(registry, self.background))
        generators = np.asarray(provider.gauge_generators(registry, self.background))
        residual = np.linalg.norm(constraints @ generators)
        scale = max(1.0, np.linalg.norm(constraints) * np.linalg.norm(generators))
        if residual > 1.0e-10 * scale:
            raise ValueError("gauge generators are not tangent to the constraint surface")
        return self.build(
            constant_symbol,
            linear_symbol,
            constraints,
            generators,
            provider.gauge_condition_derivative(registry, self.background),
            gauge_condition_id=provider.gauge_condition_id,
            provenance=provider.provenance,
        )


@dataclass(frozen=True)
class PreparedMomentumSymbolInterface:
    background: BoundBackground

    def build(
        self,
        inverse_metric: Array,
        *,
        chart_id: str,
        provenance: tuple[str, ...],
    ) -> ActionMomentumMap:
        if self.background.state is BackgroundState.UNBOUND_BACKGROUND:
            raise RuntimeError("momentum symbol requires at least a mathematical background binding")
        return ActionMomentumMap(
            inverse_metric=inverse_metric,
            action_version=self.background.action_version,
            background_id=str(self.background.background_id),
            chart_id=chart_id,
            provenance=provenance,
            derived_from_frozen_background=False,
        )

    def build_conditional_s2_contraction(
        self,
        action: UniversalFullFieldAction,
        state: Array,
        covector: Array,
        momentum_lifted_directions: Sequence[Array],
    ) -> dict[str, Any]:
        """Contract S2 with caller lifts; this is not yet a physical symbol."""

        if self.background.state is BackgroundState.UNBOUND_BACKGROUND:
            raise RuntimeError("quadratic symbol requires a bound mathematical background")
        if action.background != self.background:
            raise ValueError("action and momentum-symbol interface must share one background binding")
        momentum = np.asarray(covector)
        if momentum.ndim != 1 or not np.all(np.isfinite(momentum)):
            raise ValueError("finite momentum covector required")
        directions = tuple(np.asarray(direction) for direction in momentum_lifted_directions)
        matrix = np.empty((len(directions), len(directions)), dtype=complex)
        for row, first in enumerate(directions):
            for column, second in enumerate(directions):
                matrix[row, column] = action.s2(state, first, second)
        if self.background.physical:
            action.require_physical_promotion(state)
        return {
            "covector": momentum,
            "quadratic_symbol": np.real_if_close(matrix),
            "action_version": self.background.action_version,
            "background_id": self.background.background_id,
            "physical_symbol_derived": False,
            "classification": "BACKGROUND_PARAMETRIC_S2_CONTRACTION__MOMENTUM_LIFT_PROVIDER_OPEN",
            "momentum_lift_caller_supplied_but_not_action_certified": True,
        }


@dataclass(frozen=True)
class PreparedReplacementSaddleInterface:
    action: UniversalFullFieldAction

    def stationarity_covector(self, state: Array) -> Array:
        """Materialize S1; missing full-field sources propagate fail-closed."""

        basis = np.eye(self.action.registry.dimension)
        return np.asarray([self.action.s1(state, direction) for direction in basis])

    def projected_stationarity(self, state: Array, constraint_jacobian: Array) -> dict[str, Any]:
        from bhsm.interface.constraint_projected_replacement_saddle import projected_force

        return projected_force(self.stationarity_covector(state), constraint_jacobian)

    def require_physical_solution(self, state: Array) -> None:
        self.action.require_physical_promotion(state)


@dataclass(frozen=True)
class PreparedHSDirectionInterface:
    action: UniversalFullFieldAction

    def hessian(self, state: Array) -> Array:
        """Return the same-action HS block or fail if its owner is absent."""

        block = self.action.registry.block("HS_scalar")
        basis = np.eye(block.dimension)
        directions = tuple(self.action.registry.embed("HS_scalar", row) for row in basis)
        result = np.empty((block.dimension, block.dimension), dtype=complex)
        for row, first in enumerate(directions):
            for column, second in enumerate(directions):
                result[row, column] = self.action.s2(state, first, second)
        return np.real_if_close(result)

    def physical_direction_status(self) -> str:
        return "OPEN__REQUIRES_CERTIFIED_SADDLE_QUOTIENT_SCHUR_BLOCK_AND_ISOLATED_HS_EIGENSPACE"


def response_artifact_rejection_witness() -> dict[str, Any]:
    """Record why the current common objects establish Case B."""

    return {
        "decision": "CASE_B",
        "free_zero_background_superdeterminant_seed": "regulated_superdeterminant_seed(scale_log)",
        "interacting_operator_family_expression": "P_cycle[Phi;A,H,Psi]",
        "interacting_operator_family_machine_readable": False,
        "current_domain_background_dependence_machine_readable": False,
        "response_seeds_are_action_components": False,
        "smallest_missing_action_source": (
            "EXECUTABLE_CURRENT_DOMAIN_BACKGROUND_PARAMETRIC_GRADED_GENERATING_"
            "FUNCTIONAL_GAMMA_GFHS[B;A,c,cbar,psi,psibar,H]_WITH_HISTORY_SEAM_"
            "DOMAIN_AND_DIRECTIONAL_JETS_THROUGH_ORDER_FOUR"
        ),
        "required_lower_level_owner": (
            "BACKGROUND_COVARIANT_STRATIFIED_DIRAC_AND_SQUARED_OPERATOR_FAMILY_"
            "WITH_GAUGE_FIXING_GHOST_HS_SOURCE_CONTACT_AND_REGULATOR_DATA"
        ),
        "manual_response_matrix_splicing": "INVALIDATED",
    }


__all__ = [
    "ACTION_VERSION",
    "ATTACHMENT_STATUS",
    "DERIVATIVE_CONVENTION",
    "ActionComponent",
    "BackgroundState",
    "BlockStatus",
    "BoundBackground",
    "FieldBlock",
    "FullFieldBackgroundBinder",
    "FullFieldComponentFactory",
    "FullFieldGaugeGeneratorProvider",
    "FullFieldRegistry",
    "MissingActionSourceError",
    "PreparedBRSTInterface",
    "PreparedHSDirectionInterface",
    "PreparedMomentumSymbolInterface",
    "PreparedReplacementSaddleInterface",
    "Statistics",
    "UniversalFullFieldAction",
    "authoritative_field_registry",
    "current_pre_g7_attachment",
    "current_quadratic_block_status",
    "koszul_permutation_sign",
    "response_artifact_rejection_witness",
]
