"""Executable BHSM theorem-closure attempts with strict proof gates."""

from .closure_report import build_theorem_closure_report, evaluate_theorem
from .common import (
    ActionTermCandidate,
    CallableTheorem,
    OperatorDefinition,
    ProofGateResult,
    TheoremClosureReport,
    TheoremClosureResult,
    TheoremStatement,
)
from .cp_o_int import evaluate_cp_o_int_candidate
from .neutrino_basis_scale import evaluate_neutrino_basis_scale_candidate
from .proof_gates import build_proof_gates, promotion_allowed
from .registry_update import build_theorem_registry_update
from .x_ch import evaluate_x_ch_candidate

__all__ = [
    "ActionTermCandidate",
    "CallableTheorem",
    "OperatorDefinition",
    "ProofGateResult",
    "TheoremClosureReport",
    "TheoremClosureResult",
    "TheoremStatement",
    "build_proof_gates",
    "build_theorem_closure_report",
    "build_theorem_registry_update",
    "evaluate_cp_o_int_candidate",
    "evaluate_neutrino_basis_scale_candidate",
    "evaluate_theorem",
    "evaluate_x_ch_candidate",
    "promotion_allowed",
]
