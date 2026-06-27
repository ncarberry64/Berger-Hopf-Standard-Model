"""Machine-readable BHSM prediction registry and run semantics."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Iterable


class PredictionStatus(str, Enum):
    CALIBRATION_ANCHOR = "CALIBRATION_ANCHOR"
    CALIBRATION_ANCHOR_NOT_INDEPENDENT_PREDICTION = (
        "CALIBRATION_ANCHOR_NOT_INDEPENDENT_PREDICTION"
    )
    MODEL_PREDICTION_GIVEN_CALIBRATION = "MODEL_PREDICTION_GIVEN_CALIBRATION"
    FROZEN_INTERNAL_PREDICTION = "FROZEN_INTERNAL_PREDICTION"
    REFERENCE_COMPARISON_ONLY = "REFERENCE_COMPARISON_ONLY"
    UPPER_LIMIT_COMPARISON = "UPPER_LIMIT_COMPARISON"
    OPEN_THEOREM_REQUIRED = "OPEN_THEOREM_REQUIRED"
    DISABLED_UNTIL_RUNTIME_VALIDATED = "DISABLED_UNTIL_RUNTIME_VALIDATED"
    EXCLUDED_FROM_MINIMAL_COLLIDER_INTERFACE = "EXCLUDED_FROM_MINIMAL_COLLIDER_INTERFACE"
    RUNTIME_PARAMETER_ONLY = "RUNTIME_PARAMETER_ONLY"
    UNKNOWN_OR_UNREGISTERED = "UNKNOWN_OR_UNREGISTERED"


@dataclass(frozen=True)
class PredictionRegistryEntry:
    particle_key: str
    display_name: str
    sector: str
    quantity: str
    unit: str
    default_status: PredictionStatus
    allowed_statuses: tuple[PredictionStatus, ...]
    geometry_required: bool
    calibration_allowed: bool
    can_be_calibration_anchor: bool
    independent_prediction_allowed: bool
    comparison_kind: str | None
    reference_key: str | None
    source_type: str
    source_artifacts: tuple[str, ...]
    theorem_status: str
    runtime_required: bool
    excluded_reason: str | None
    claim_boundary: str
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["default_status"] = self.default_status.value
        payload["allowed_statuses"] = [status.value for status in self.allowed_statuses]
        payload["source_artifacts"] = list(self.source_artifacts)
        payload["notes"] = list(self.notes)
        return payload


@dataclass(frozen=True)
class PredictionRunConfig:
    anchor_particle: str | None
    particles: tuple[str, ...]
    include_open_theorem_entries: bool = False
    output_format: str = "json"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PredictionRunResult:
    particle_key: str
    status: PredictionStatus
    prediction: dict[str, Any] | None = None
    comparison: dict[str, Any] | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "particle_key": self.particle_key,
            "status": self.status.value,
            "prediction": self.prediction,
            "comparison": self.comparison,
            "warnings": list(self.warnings),
        }


@dataclass
class PredictionRegistry:
    entries: dict[str, PredictionRegistryEntry]
    registry_name: str = "BHSM Prediction Registry"
    version: str = "0.1"
    release_basis: str = "BHSM v1.1.0 plus Python interface v0.1"

    def get(self, particle_key: str) -> PredictionRegistryEntry | None:
        return self.entries.get(particle_key)

    def require(self, particle_key: str) -> PredictionRegistryEntry:
        entry = self.get(particle_key)
        if entry is None:
            raise KeyError(particle_key)
        return entry

    def list_entries(self) -> list[PredictionRegistryEntry]:
        return [self.entries[key] for key in sorted(self.entries)]

    def select_by_status(self, statuses: Iterable[PredictionStatus]) -> list[PredictionRegistryEntry]:
        selected = set(statuses)
        return [entry for entry in self.list_entries() if entry.default_status in selected]

    def to_dict(self) -> dict[str, Any]:
        return {
            "registry_name": self.registry_name,
            "version": self.version,
            "release_basis": self.release_basis,
            "entries": [entry.to_dict() for entry in self.list_entries()],
            "status_taxonomy": [status.value for status in PredictionStatus],
            "calibration_policy": "Calibration anchors are not independent predictions in the same run.",
            "upper_limit_policy": "Electron-neutrino comparison is upper-limit based by default.",
            "runtime_validation_policy": "Disabled software gates remain disabled until live external validation passes.",
            "forbidden_claims": [
                "W is independently predicted when W is the calibration anchor.",
                "Electron-neutrino mass is centrally measured.",
                "BHSM is empirically validated by the registry.",
                "BHSM is officially CERN integrated.",
                "BHSM has a validated UFO model.",
                "BHSM has passed MadGraph validation.",
                "BHSM has exported the complete 4D Lagrangian.",
                "Open-theorem vertices are production-ready.",
            ],
            "allowed_claims": [
                "BHSM provides a Python prediction registry interface.",
                "The registry separates calibration, prediction, comparison, blocker, and runtime-gate statuses.",
                "The W boson can be used as a calibration anchor.",
                "Electron-neutrino comparison is upper-limit based by default.",
                "CKM/PMNS source matrices can be exposed as existing BHSM internal prediction artifacts.",
            ],
        }


def _entry(
    key: str,
    display: str,
    sector: str,
    quantity: str,
    status: PredictionStatus,
    claim: str,
    *,
    unit: str = "dimensionless",
    geometry: bool = False,
    calibration: bool = False,
    anchor: bool = False,
    independent: bool = False,
    comparison: str | None = None,
    reference: str | None = None,
    source_type: str = "BHSM artifact",
    artifacts: tuple[str, ...] = (),
    theorem: str = "NOT_APPLICABLE",
    runtime: bool = False,
    excluded: str | None = None,
    allowed: tuple[PredictionStatus, ...] | None = None,
) -> PredictionRegistryEntry:
    return PredictionRegistryEntry(
        key, display, sector, quantity, unit, status, allowed or (status,), geometry,
        calibration, anchor, independent, comparison, reference, source_type,
        artifacts, theorem, runtime, excluded, claim,
    )


def default_prediction_registry() -> PredictionRegistry:
    """Build the source-traced v0.1 registry without external data access."""

    entries = [
        _entry("W_boson", "W boson", "electroweak_vector", "mass", PredictionStatus.CALIBRATION_ANCHOR,
               "W may calibrate the geometric-to-physical scale; when used as anchor it is not an independent prediction.",
               unit="GeV/c^2", geometry=True, calibration=True, anchor=True, comparison="central_value",
               reference="W_boson", source_type="runtime/reference input",
               allowed=(PredictionStatus.CALIBRATION_ANCHOR, PredictionStatus.CALIBRATION_ANCHOR_NOT_INDEPENDENT_PREDICTION, PredictionStatus.REFERENCE_COMPARISON_ONLY)),
        _entry("electron_neutrino", "Electron neutrino", "effective_neutrino_extension", "mass", PredictionStatus.MODEL_PREDICTION_GIVEN_CALIBRATION,
               "Electron-neutrino comparison is upper-limit based unless a vetted central reference is supplied.",
               unit="GeV/c^2", geometry=True, comparison="upper_limit", reference="electron_neutrino",
               source_type="interface model output", allowed=(PredictionStatus.MODEL_PREDICTION_GIVEN_CALIBRATION, PredictionStatus.UPPER_LIMIT_COMPARISON)),
        _entry("CKM_matrix_BHSM", "BHSM CKM matrix", "charged_current_quark", "mixing_matrix", PredictionStatus.FROZEN_INTERNAL_PREDICTION,
               "The BHSM CKM source matrix is an internal artifact; external comparison remains separate.", comparison="optional_matrix_reference",
               artifacts=("artifacts/CKM_no_fit_operator_output_v1.json",)),
        _entry("PMNS_matrix_BHSM", "BHSM PMNS matrix", "charged_current_lepton", "mixing_matrix", PredictionStatus.FROZEN_INTERNAL_PREDICTION,
               "The BHSM PMNS source matrix is internal; the physical neutrino mass/basis theorem remains separate.", comparison="optional_matrix_reference",
               artifacts=("artifacts/PMNS_no_fit_operator_output_v1.json",)),
        _entry("charged_boundary_response_matrix", "Charged boundary response", "charged_boundary", "interaction_matrix", PredictionStatus.OPEN_THEOREM_REQUIRED,
               "Boundary source matrix with an open X_ch field theorem.", theorem="OPEN_MISSING_FIELD_REPRESENTATION",
               artifacts=("artifacts/BHSM_x_ch_charged_boundary_response_theorem_v1_1.json", "artifacts/BHSM_x_ch_minimal_action_closure_v0_8.json"), excluded="X_ch field representation is open"),
        _entry("neutral_operator_kernel_BH", "Neutral operator kernel", "neutral", "operator_kernel", PredictionStatus.OPEN_THEOREM_REQUIRED,
               "Boundary/operator seed with an open physical neutrino map.", theorem="OPEN_MISSING_PHYSICAL_BASIS",
               artifacts=("artifacts/BHSM_neutrino_dirac_majorana_basis_scale_theorem_v1_1.json", "artifacts/BHSM_neutrino_basis_scale_minimal_action_closure_v0_8.json"), excluded="physical neutrino basis map is open"),
        _entry("cp_holonomy_phase_attachment", "CP holonomy phase attachment", "cp_holonomy", "interaction_attachment", PredictionStatus.OPEN_THEOREM_REQUIRED,
               "Artifact-backed phase plus symbolic O_int candidate; action source remains open.", theorem="OPEN_MISSING_ACTION_SOURCE",
               artifacts=("artifacts/BHSM_cp_holonomy_o_int_attachment_theorem_v1_1.json", "artifacts/BHSM_cp_o_int_minimal_action_closure_v0_8.json"), excluded="O_int action source is open"),
        _entry("minimal_collider_interface_subset", "Minimal collider-interface subset", "collider_interface", "bounded_lagrangian_subset", PredictionStatus.REFERENCE_COMPARISON_ONLY,
               "Bounded CKM/PMNS collider-interface subset only; not the complete BHSM 4D Lagrangian.",
               artifacts=("artifacts/BHSM_minimal_bounded_lagrangian_subset_v1_2.json",),
               allowed=(PredictionStatus.MODEL_PREDICTION_GIVEN_CALIBRATION, PredictionStatus.REFERENCE_COMPARISON_ONLY)),
        _entry("feynrules_minimal_model", "Minimal FeynRules model", "software_gate", "software_readiness", PredictionStatus.DISABLED_UNTIL_RUNTIME_VALIDATED,
               "The .fr model remains disabled until live Wolfram/FeynRules validation passes.", runtime=True,
               source_type="software gate artifact", artifacts=("artifacts/BHSM_phase_three_k_gate_status_v1_3.json",)),
        _entry("ufo_export", "UFO export", "software_gate", "software_readiness", PredictionStatus.DISABLED_UNTIL_RUNTIME_VALIDATED,
               "UFO readiness remains false until real export and loadability pass.", runtime=True,
               source_type="software gate artifact", artifacts=("artifacts/BHSM_feynrules_to_ufo_export_contract_v1_3.json",)),
        _entry("madgraph_smoke_test", "MadGraph smoke test", "software_gate", "software_readiness", PredictionStatus.DISABLED_UNTIL_RUNTIME_VALIDATED,
               "MadGraph readiness remains false until a real smoke test passes.", runtime=True,
               source_type="software gate artifact", artifacts=("artifacts/BHSM_madgraph_smoke_outcome_v1_6.json",)),
    ]
    return PredictionRegistry({entry.particle_key: entry for entry in entries})
