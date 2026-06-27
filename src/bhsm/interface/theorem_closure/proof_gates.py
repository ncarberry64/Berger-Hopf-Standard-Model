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

CP_O_INT_PROOF_GATE_DEFINITIONS = (
    ("CP01", "formal theorem statement exists"),
    ("CP02", "CP O_int domain is defined"),
    ("CP03", "CP O_int codomain is defined"),
    ("CP04", "field representation is defined"),
    ("CP05", "Lorentz structure is defined"),
    ("CP06", "gauge/sector admissibility is defined"),
    ("CP07", "interaction/action term is defined"),
    ("CP08", "phase attachment rule is defined"),
    ("CP09", "coupling normalization is defined"),
    ("CP10", "callable implementation exists"),
    ("CP11", "input/output schema exists"),
    ("CP12", "artifact source exists"),
    ("CP13", "provenance chain exists"),
    ("CP14", "no empirical derivation inputs are used"),
    ("CP15", "no PDG/reference values are theorem inputs"),
    ("CP16", "no calibration values are theorem inputs"),
    ("CP17", "consistency tests pass"),
    ("CP18", "registry update proposal is generated"),
    ("CP19", "formula registry update is generated"),
    ("CP20", "claim policy is updated"),
    ("CP21", "theorem blocker artifact records the result"),
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


def build_cp_o_int_proof_gates(
    evidence: Mapping[str, bool],
    evidence_text: Mapping[str, str] | None = None,
    limitations: Mapping[str, str] | None = None,
) -> tuple[ProofGateResult, ...]:
    """Build the 21 focused CP O_int gates with fail-closed defaults."""

    evidence_text = evidence_text or {}
    limitations = limitations or {}
    return tuple(
        ProofGateResult(
            gate_id=gate_id,
            name=name,
            required=True,
            passes=bool(evidence.get(gate_id, False)),
            evidence=evidence_text.get(gate_id, "No supporting evidence supplied."),
            limitations=limitations.get(gate_id, "" if evidence.get(gate_id, False) else "Required CP O_int proof object is absent."),
        )
        for gate_id, name in CP_O_INT_PROOF_GATE_DEFINITIONS
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
