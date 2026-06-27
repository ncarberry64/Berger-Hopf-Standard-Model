"""Strict proof gates for BHSM theorem promotion."""

from __future__ import annotations

from typing import Mapping

from .common import ProofGateResult

PROOF_GATE_DEFINITIONS = (
    ("G01", "formal theorem statement exists"),
    ("G02", "domain and codomain are defined"),
    ("G03", "operator/action term is defined"),
    ("G04", "callable implementation exists"),
    ("G05", "input/output schema exists"),
    ("G06", "artifact source exists"),
    ("G07", "provenance chain exists"),
    ("G08", "no empirical derivation inputs are used"),
    ("G09", "no reference/PDG values are derivation inputs"),
    ("G10", "consistency checks pass"),
    ("G11", "registry status update is generated"),
    ("G12", "claim policy is explicit"),
    ("G13", "theorem blocker artifact records the attempt"),
    ("G14", "gauge/sector admissibility checks pass"),
    ("G15", "dimensional/unit policy is explicit"),
    ("G16", "calibration policy is explicit"),
    ("G17", "failure modes are documented"),
)


def build_proof_gates(
    evidence: Mapping[str, bool],
    evidence_text: Mapping[str, str] | None = None,
    limitations: Mapping[str, str] | None = None,
) -> tuple[ProofGateResult, ...]:
    """Build all gates; absent evidence fails closed."""

    evidence_text = evidence_text or {}
    limitations = limitations or {}
    return tuple(
        ProofGateResult(
            gate_id=gate_id,
            name=name,
            required=True,
            passes=bool(evidence.get(gate_id, False)),
            evidence=evidence_text.get(gate_id, "No supporting evidence supplied."),
            limitations=limitations.get(gate_id, "" if evidence.get(gate_id, False) else "Required proof object is absent."),
        )
        for gate_id, name in PROOF_GATE_DEFINITIONS
    )


def promotion_allowed(gates: tuple[ProofGateResult, ...]) -> bool:
    return all(gate.passes for gate in gates if gate.required)


def proof_gate_summary(gates: tuple[ProofGateResult, ...]) -> dict[str, object]:
    return {
        "required": sum(gate.required for gate in gates),
        "passed": sum(gate.required and gate.passes for gate in gates),
        "failed": [gate.gate_id for gate in gates if gate.required and not gate.passes],
        "all_required_pass": promotion_allowed(gates),
    }
