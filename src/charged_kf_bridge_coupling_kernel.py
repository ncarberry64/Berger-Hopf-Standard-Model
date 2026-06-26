from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from typing import Dict, Tuple

import charged_kf_generator as kf
import charged_stiffness_action_selector as selector


PUBLIC_STATUS = "structural architecture integrated conditional; numerical closure open"

STATUS_TABLE = {
    "charged_Kf_bridge_coupling_kernel_v1": "COMPLETED_BRIDGE_COUPLING_AUDIT",
    "charged_Kf_tridiagonal_bridge_topology": "DERIVED_CONDITIONAL_ON_E3_LADDER_AND_TANGENT_ADJACENCY",
    "E3_reference_ladder_bridge": "DERIVED_CONDITIONAL_ON_RANK_THREE_CLOSURE_LADDER",
    "zero_defect_tangent_bridge": "DERIVED_CONDITIONAL_ON_ZERO_DEFECT_TANGENT_ADJACENCY",
    "beta_f_reference_bridge_topology": "DERIVED_CONDITIONAL_ON_E3_LADDER",
    "beta_f_reference_bridge_magnitude": "OPEN_LOCALIZABLE",
    "beta_f_minimal_1_over_21_ansatz": "STRONGLY_SUPPORTED_CANDIDATE",
    "kappa_f_tangent_bridge_topology": "DERIVED_CONDITIONAL_ON_ZERO_DEFECT_TANGENT_ADJACENCY",
    "kappa_f_inverse_tangent_stiffness_form": "STRONGLY_SUPPORTED_CANDIDATE",
    "kappa_f_magnitude": "OPEN_LOCALIZABLE",
    "kappa_f_minimal_1_over_21_ansatz": "STRONGLY_SUPPORTED_CANDIDATE",
    "suppression_bridge_coupling_identification": "OPEN_LOCALIZABLE",
    "cyclic_0_2_bridge": "NOT_ASSUMED_REQUIRES_CYCLIC_E3_ACTION_SOURCE",
    "rho_ch_exact_value": "OPEN_LOCALIZABLE",
    "numerical_closure": "OPEN",
}

FORBIDDEN_DERIVATION_INPUTS = (
    "observed masses",
    "charged-lepton masses",
    "quark masses",
    "CKM",
    "PMNS",
    "neutrino data",
    "measured alpha",
    "empirical target ratios",
    "post-comparison residuals",
)


@dataclass(frozen=True)
class BridgeTopology:
    edge: Tuple[int, int]
    source: str
    status: str
    enabled: bool
    notes: str


@dataclass(frozen=True)
class BridgeMagnitudeCandidate:
    name: str
    formula: str
    value: Fraction | None
    topology_status: str
    magnitude_status: str
    candidate_status: str
    notes: str


@dataclass(frozen=True)
class ReferenceBridgeCandidate:
    sector: str
    Pi_f: Fraction
    beta_0: Fraction
    beta_f: Fraction
    topology_status: str
    magnitude_status: str
    ansatz_status: str


@dataclass(frozen=True)
class TangentBridgeCandidate:
    sector: str
    rho_ch: Fraction
    tangent: Tuple[int, int]
    tangent_norm_sq: Fraction
    kappa_0: Fraction
    kappa_f: Fraction
    topology_status: str
    inverse_stiffness_status: str
    magnitude_status: str
    ansatz_status: str


@dataclass(frozen=True)
class BridgeCouplingKernelVerdict:
    bridge_topology_verdict: str
    bridge_magnitude_verdict: str
    beta_f_open_localizable: bool
    kappa_f_open_localizable: bool
    suppression_bridge_coupling_identification: str
    numerical_closure: str
    theorem_complete: bool


def fraction_string(value: Fraction | None) -> str | None:
    if value is None:
        return None
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _convert(value):
    if isinstance(value, Fraction):
        return fraction_string(value)
    if isinstance(value, tuple):
        return [_convert(item) for item in value]
    if isinstance(value, dict):
        return {key: _convert(item) for key, item in value.items()}
    return value


def bridge_topology(cyclic_source_present: bool = False) -> Tuple[BridgeTopology, ...]:
    rows = [
        BridgeTopology(
            edge=(0, 1),
            source="E3_reference_ladder_bridge",
            status=STATUS_TABLE["E3_reference_ladder_bridge"],
            enabled=True,
            notes="Reference state to first excitation is the E3 ladder bridge.",
        ),
        BridgeTopology(
            edge=(1, 2),
            source="zero_defect_tangent_bridge",
            status=STATUS_TABLE["zero_defect_tangent_bridge"],
            enabled=True,
            notes="First-to-second excitation is the zero-defect tangent adjacency.",
        ),
    ]
    rows.append(
        BridgeTopology(
            edge=(0, 2),
            source="cyclic_E3_closure",
            status=(
                "DERIVED_CONDITIONAL_ON_CYCLIC_E3_ACTION_SOURCE"
                if cyclic_source_present
                else STATUS_TABLE["cyclic_0_2_bridge"]
            ),
            enabled=cyclic_source_present,
            notes="Direct cyclic bridge is absent unless an explicit cyclic E3 action source is supplied.",
        )
    )
    return tuple(rows)


def enabled_topology_edges(cyclic_source_present: bool = False) -> Tuple[Tuple[int, int], ...]:
    return tuple(row.edge for row in bridge_topology(cyclic_source_present) if row.enabled)


def reference_bridge_candidates(beta_0: Fraction = Fraction(1, 21)) -> Tuple[ReferenceBridgeCandidate, ...]:
    return tuple(
        ReferenceBridgeCandidate(
            sector=sector,
            Pi_f=kf.projection_fraction(sector),
            beta_0=beta_0,
            beta_f=beta_0 * kf.projection_fraction(sector),
            topology_status=STATUS_TABLE["beta_f_reference_bridge_topology"],
            magnitude_status=STATUS_TABLE["beta_f_reference_bridge_magnitude"],
            ansatz_status=STATUS_TABLE["beta_f_minimal_1_over_21_ansatz"],
        )
        for sector in kf.CHARGED_SECTORS
    )


def tangent_bridge_candidates(
    rho_ch: int | Fraction,
    kappa_0: Fraction = Fraction(1, 21),
) -> Tuple[TangentBridgeCandidate, ...]:
    rho = Fraction(rho_ch)
    return tuple(
        TangentBridgeCandidate(
            sector=sector,
            rho_ch=rho,
            tangent=kf.EXPECTED_TANGENTS[sector],
            tangent_norm_sq=kf.tangent_norm_sq(sector, rho),
            kappa_0=kappa_0,
            kappa_f=kappa_0 / kf.tangent_norm_sq(sector, rho),
            topology_status=STATUS_TABLE["kappa_f_tangent_bridge_topology"],
            inverse_stiffness_status=STATUS_TABLE["kappa_f_inverse_tangent_stiffness_form"],
            magnitude_status=STATUS_TABLE["kappa_f_magnitude"],
            ansatz_status=STATUS_TABLE["kappa_f_minimal_1_over_21_ansatz"],
        )
        for sector in kf.CHARGED_SECTORS
    )


def bridge_magnitude_candidates() -> Tuple[BridgeMagnitudeCandidate, ...]:
    return (
        BridgeMagnitudeCandidate(
            name="beta_0",
            formula="beta_f = beta_0 Pi_f",
            value=Fraction(1, 21),
            topology_status=STATUS_TABLE["beta_f_reference_bridge_topology"],
            magnitude_status=STATUS_TABLE["beta_f_reference_bridge_magnitude"],
            candidate_status=STATUS_TABLE["beta_f_minimal_1_over_21_ansatz"],
            notes="The 1/21 seed is a minimal ansatz; no explicit bridge action source derives it.",
        ),
        BridgeMagnitudeCandidate(
            name="kappa_0",
            formula="kappa_f = kappa_0 / ||v_f||^2_ch",
            value=Fraction(1, 21),
            topology_status=STATUS_TABLE["kappa_f_tangent_bridge_topology"],
            magnitude_status=STATUS_TABLE["kappa_f_magnitude"],
            candidate_status=STATUS_TABLE["kappa_f_minimal_1_over_21_ansatz"],
            notes="The inverse tangent stiffness form is a strong candidate; the 1/21 seed remains open.",
        ),
    )


def tangent_norm_table() -> Dict[str, Dict[str, str]]:
    rows: Dict[str, Dict[str, str]] = {}
    for rho in kf.RHO_CH_BRANCHES:
        rows[str(rho)] = {
            sector: fraction_string(kf.tangent_norm_sq(sector, rho))  # type: ignore[dict-item]
            for sector in kf.CHARGED_SECTORS
        }
    return rows


def minimal_ansatz_bridge_values(rho_ch: int | Fraction) -> Dict[str, Dict[str, str]]:
    rows: Dict[str, Dict[str, str]] = {}
    for sector in kf.CHARGED_SECTORS:
        beta_f, kappa_f = kf.bridge_values(sector, rho_ch, kf.BRIDGE_RULE_MINIMAL_ANSATZ)
        rows[sector] = {
            "beta_f": fraction_string(beta_f),  # type: ignore[dict-item]
            "kappa_f": fraction_string(kappa_f),  # type: ignore[dict-item]
            "bridge_rule": kf.BRIDGE_RULE_MINIMAL_ANSATZ,
            "bridge_rule_status": kf.bridge_rule_status(kf.BRIDGE_RULE_MINIMAL_ANSATZ),
        }
    return rows


def suppression_bridge_separation() -> Dict[str, object]:
    return {
        "rule_A_suppression_source": "B_supp = I_ch / 21",
        "rule_A_eta_values": {
            "lepton": "20/147",
            "up": "38/147",
            "down": "68/147",
        },
        "bridge_magnitude_source": "OPEN_LOCALIZABLE",
        "status": STATUS_TABLE["suppression_bridge_coupling_identification"],
        "does_suppression_kernel_derive_beta0": False,
        "does_suppression_kernel_derive_kappa0": False,
        "notes": "Rule A derives diagonal suppression; it does not by itself derive beta_0 or kappa_0.",
    }


def verdict() -> BridgeCouplingKernelVerdict:
    return BridgeCouplingKernelVerdict(
        bridge_topology_verdict=STATUS_TABLE["charged_Kf_tridiagonal_bridge_topology"],
        bridge_magnitude_verdict="BRIDGE_MAGNITUDES_OPEN_LOCALIZABLE",
        beta_f_open_localizable=True,
        kappa_f_open_localizable=True,
        suppression_bridge_coupling_identification=STATUS_TABLE[
            "suppression_bridge_coupling_identification"
        ],
        numerical_closure=STATUS_TABLE["numerical_closure"],
        theorem_complete=False,
    )


def _dataclass_rows(rows):
    out = []
    for row in rows:
        item = asdict(row)
        out.append({key: _convert(value) for key, value in item.items()})
    return out


def report_as_dict() -> Dict[str, object]:
    return {
        "id": "PO-BH-charged-Kf-bridge-coupling-kernel-v1",
        "title": "Charged Kf Bridge-Coupling Source Kernel v1",
        "public_status": PUBLIC_STATUS,
        "frozen_predictions_changed": False,
        "official_predictions_changed": False,
        "uses_empirical_derivation_inputs": False,
        "forbidden_derivation_inputs": list(FORBIDDEN_DERIVATION_INPUTS),
        "bridge_rules": {
            "diagonal_only": {
                "name": kf.BRIDGE_RULE_DIAGONAL_ONLY,
                "status": kf.bridge_rule_status(kf.BRIDGE_RULE_DIAGONAL_ONLY),
                "beta_f": "0",
                "kappa_f": "0",
            },
            "minimal_ansatz": {
                "name": kf.BRIDGE_RULE_MINIMAL_ANSATZ,
                "status": kf.bridge_rule_status(kf.BRIDGE_RULE_MINIMAL_ANSATZ),
                "beta_f": "beta_0 Pi_f with beta_0=1/21",
                "kappa_f": "kappa_0/||v_f||^2_ch with kappa_0=1/21",
            },
            "symbolic_open": {
                "name": kf.BRIDGE_RULE_SYMBOLIC_OPEN,
                "status": kf.bridge_rule_status(kf.BRIDGE_RULE_SYMBOLIC_OPEN),
                "beta_f": "OPEN_LOCALIZABLE",
                "kappa_f": "OPEN_LOCALIZABLE",
            },
        },
        "topology": _dataclass_rows(bridge_topology()),
        "enabled_topology_edges": [_convert(edge) for edge in enabled_topology_edges()],
        "cyclic_0_2_enabled_by_default": False,
        "reference_bridge_candidates": _dataclass_rows(reference_bridge_candidates()),
        "tangent_bridge_candidates_by_rho": {
            str(rho): _dataclass_rows(tangent_bridge_candidates(rho))
            for rho in kf.RHO_CH_BRANCHES
        },
        "bridge_magnitude_candidates": _dataclass_rows(bridge_magnitude_candidates()),
        "tangent_norms": tangent_norm_table(),
        "minimal_ansatz_bridge_values_by_rho": {
            str(rho): minimal_ansatz_bridge_values(rho) for rho in kf.RHO_CH_BRANCHES
        },
        "rho_ch_selector_dependency": {
            "source": "charged_stiffness_action_selector_v1",
            "verdict": selector.selector_verdict().verdict,
            "rho_ch_exact_value_status": selector.selector_verdict().rho_ch_exact_value_status,
        },
        "suppression_bridge_separation": suppression_bridge_separation(),
        "statuses": STATUS_TABLE,
        "verdict": {key: _convert(value) for key, value in asdict(verdict()).items()},
        "claim_boundary": (
            "The tridiagonal bridge topology is conditionally sourced by E3 ladder and "
            "zero-defect tangent adjacency; beta_f and kappa_f magnitudes remain open-localizable."
        ),
    }
