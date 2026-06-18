from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


BRANCH = "bhsm-theorem-level-boundary-action-derivation-v1"
STATUS = "theorem_scaffold_candidate"

ALLOWED_STATUSES = {
    "STRUCTURAL_CANDIDATE",
    "DIAGNOSTIC_SUPPORTED",
    "PARTIALLY_DERIVED",
    "DERIVED_CONDITIONAL",
    "OPEN",
}

VERDICT_LABELS = [
    "THEOREM_LEVEL_BOUNDARY_ACTION_DERIVATION_SCAFFOLD_COMPLETE",
    "BHSM_BOUNDARY_AXIOM_LEDGER_CREATED",
    "BHSM_BOUNDARY_THEOREM_STATEMENTS_CREATED",
    "BHSM_BOUNDARY_LEMMA_LEDGER_CREATED",
    "BHSM_BOUNDARY_PROOF_OBLIGATION_LEDGER_CREATED",
    "BHSM_BOUNDARY_NON_TAUTOLOGY_AUDIT_CREATED",
    "BOUNDARY_ACTION_DERIVATION_REMAINS_OPEN",
    "FULL_HESSIAN_PROOF_REMAINS_OPEN",
    "CLOSURE_SPECTRUM_THEOREM_REMAINS_OPEN",
    "FINITE_ALGEBRA_THEOREM_REMAINS_OPEN",
    "CHARGE_ANOMALY_THEOREM_REMAINS_OPEN",
    "FULL_SM_DERIVATION_NOT_CLAIMED",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]

REQUIRED_STATUS_LANGUAGE = (
    "This document does not claim that the Standard Model is fully derived. It "
    "begins the theorem-level derivation program for BHSM by separating "
    "assumptions, candidate axioms, lemmas, theorem statements, and open proof "
    "obligations. The boundary action, full Hessian, closure spectrum, finite "
    "algebra, and charge/anomaly bridge remain candidate until their proof "
    "obligations are discharged."
)


@dataclass(frozen=True)
class AxiomRecord:
    code: str
    name: str
    statement: str
    status: str
    role: str
    discharge_condition: str
    downstream_dependencies: tuple[str, ...]


@dataclass(frozen=True)
class TheoremRecord:
    code: str
    name: str
    assumptions: tuple[str, ...]
    conclusion: str
    proof_sketch: str
    status: str
    missing_proof_obligations: tuple[str, ...]


@dataclass(frozen=True)
class LemmaRecord:
    code: str
    name: str
    statement: str
    proof_sketch: str
    status: str
    dependencies: tuple[str, ...]
    linked_prior_gate: str


@dataclass(frozen=True)
class ProofObligationRecord:
    code: str
    name: str
    status: str
    blocking_assumptions: tuple[str, ...]
    required_evidence: str
    possible_falsifier: str
    downstream_impact: str


@dataclass(frozen=True)
class NonTautologyRow:
    step: str
    claim: str
    risk_of_circularity: str
    imported_structure: str
    current_status: str
    required_fix: str


def axiom_ledger() -> dict[str, AxiomRecord]:
    records = [
        AxiomRecord(
            "AX-BH-1",
            "Berger-Hopf boundary geometry",
            "The boundary state space admits Hopf fiber/base coordinates with Berger deformation and admissible boundary sections.",
            "STRUCTURAL_CANDIDATE",
            "Defines the geometric arena for the boundary theorem program.",
            "Construct the boundary state space from a geometric Berger-Hopf action.",
            ("THM-BH-1", "THM-BH-5"),
        ),
        AxiomRecord(
            "AX-BH-2",
            "Hopf fiber phase closure",
            "Admissible boundary states must be globally single-valued under Hopf fiber phase identification.",
            "DIAGNOSTIC_SUPPORTED",
            "Sources the phase closure functional and local stiffness.",
            "Derive global single-valuedness from admissible boundary sections.",
            ("THM-BH-1",),
        ),
        AxiomRecord(
            "AX-BH-3",
            "Boundary orientation involution",
            "The boundary admits a Z2 orientation-reversal involution whose minimal nontrivial balanced representation has eigenvalues (+1,-1).",
            "DIAGNOSTIC_SUPPORTED",
            "Sources the orientation pair and candidate weak-interface grading.",
            "Derive the involution from Berger-Hopf boundary geometry.",
            ("THM-BH-2", "THM-BH-6"),
        ),
        AxiomRecord(
            "AX-BH-4",
            "Cyclic channel closure",
            "The boundary admits a minimal nontrivial cyclic channel closure beyond the orientation pair, with candidate order 3.",
            "DIAGNOSTIC_SUPPORTED",
            "Sources the cyclic channel branch.",
            "Derive order 3 from boundary automorphism, phase closure, or stability.",
            ("THM-BH-3", "THM-BH-6"),
        ),
        AxiomRecord(
            "AX-BH-5",
            "Fourth-order topographic stability",
            "The low-energy boundary stability operator is fourth order and has the schematic stable form L_T = nabla^2 - B nabla^4 or an equivalent stable convention.",
            "PARTIALLY_DERIVED",
            "Provides the branch-count and stability scaffold.",
            "Derive the operator from the underlying geometric variational principle.",
            ("THM-BH-4", "THM-BH-5"),
        ),
        AxiomRecord(
            "AX-BH-6",
            "Excess-sector gap",
            "Closure sectors outside the reference/orientation/cyclic low-energy budget are gapped or composite under the candidate low-energy Hessian.",
            "DIAGNOSTIC_SUPPORTED",
            "Separates low-energy branches from excess sectors.",
            "Derive the excess gap from the full Hessian spectrum.",
            ("THM-BH-4", "THM-BH-6"),
        ),
        AxiomRecord(
            "AX-BH-7",
            "Finite-algebra bridge",
            "Low-energy closure spaces V_d generate finite endomorphism blocks End(C^d).",
            "DERIVED_CONDITIONAL",
            "Links closure dimensions to finite algebra blocks.",
            "Prove the physical boundary channel space equals the closure space V_d.",
            ("THM-BH-7",),
        ),
        AxiomRecord(
            "AX-BH-8",
            "Charge bridge",
            "The finite boundary algebra/projector bridge supplies C, ell, sigma, w and therefore T3, Y, Q through the existing audited formulas.",
            "DIAGNOSTIC_SUPPORTED",
            "Links projector algebra to charge operators.",
            "Derive C, ell, sigma, w from boundary geometry without importing SM labels.",
            ("THM-BH-8",),
        ),
        AxiomRecord(
            "AX-BH-9",
            "Anomaly bridge",
            "The resulting charge/hypercharge skeleton satisfies the already-audited one-generation anomaly cancellation diagnostic.",
            "DIAGNOSTIC_SUPPORTED",
            "Checks downstream consistency of the charge skeleton.",
            "Derive anomaly cancellation from global boundary consistency.",
            ("THM-BH-8",),
        ),
    ]
    for record in records:
        if record.status not in ALLOWED_STATUSES:
            raise ValueError(f"invalid axiom status: {record.status}")
    return {record.code: record for record in records}


def lemma_ledger() -> dict[str, LemmaRecord]:
    records = [
        LemmaRecord(
            "LEM-BH-1",
            "Phase second-variation lemma",
            "S_phase(d,2pi/d+epsilon)=d^2 epsilon^2 + O(epsilon^4).",
            "Expand 2-2cos(d epsilon) at epsilon=0.",
            "DERIVED_CONDITIONAL",
            ("AX-BH-2",),
            "phase_closure_second_variation.md",
        ),
        LemmaRecord(
            "LEM-BH-2",
            "Orientation quadratic lemma",
            "For R=diag(s_i+epsilon_i), s_i^2=1, the finite orientation surrogate has quadratic part 4 sum epsilon_i^2 + lambda_trace (sum epsilon_i)^2.",
            "Taylor expand (r_i^2-1)^2 around s_i=+/-1.",
            "DERIVED_CONDITIONAL",
            ("AX-BH-3",),
            "orientation_involution_second_variation.md",
        ),
        LemmaRecord(
            "LEM-BH-3",
            "Cyclic phase lemma",
            "For order n cyclic closure, |exp(i n epsilon)-1|^2 = n^2 epsilon^2 + O(epsilon^4).",
            "Apply the phase expansion with d replaced by n.",
            "DERIVED_CONDITIONAL",
            ("AX-BH-4",),
            "cyclic_channel_second_variation.md",
        ),
        LemmaRecord(
            "LEM-BH-4",
            "Endomorphism block lemma",
            "End(C^d)=M_d(C), with d=1 giving C.",
            "Use the standard finite-dimensional complex endomorphism algebra identity.",
            "DERIVED_CONDITIONAL",
            ("AX-BH-7",),
            "finite_boundary_algebra_source_gate.md",
        ),
        LemmaRecord(
            "LEM-BH-5",
            "Projector-to-primitive lemma",
            "The previously audited finite boundary algebra supplies central projectors and orientation grading that map into C, ell, sigma, w.",
            "Use the existing projector/integer primitive bridge.",
            "DIAGNOSTIC_SUPPORTED",
            ("AX-BH-7", "AX-BH-8"),
            "boundary_integer_charge_hypercharge_bridge.md",
        ),
        LemmaRecord(
            "LEM-BH-6",
            "Charge formula lemma",
            "The existing bridge maps C, ell, sigma, w to T3, Y, Q.",
            "Apply the audited integer primitive formulas.",
            "DIAGNOSTIC_SUPPORTED",
            ("AX-BH-8",),
            "boundary_integer_charge_hypercharge_bridge.md",
        ),
        LemmaRecord(
            "LEM-BH-7",
            "Anomaly diagnostic lemma",
            "The existing one-generation diagnostic anomaly sums vanish under the audited charge/hypercharge assignment.",
            "Use the already audited anomaly sums and Witten parity check.",
            "DIAGNOSTIC_SUPPORTED",
            ("AX-BH-9", "LEM-BH-6"),
            "boundary_integer_anomaly_closure_gate.md",
        ),
    ]
    for record in records:
        if record.status not in ALLOWED_STATUSES:
            raise ValueError(f"invalid lemma status: {record.status}")
    return {record.code: record for record in records}


def theorem_ledger() -> dict[str, TheoremRecord]:
    records = [
        TheoremRecord(
            "THM-BH-1",
            "Phase closure functional",
            ("AX-BH-2", "LEM-BH-1"),
            "A local finite surrogate for phase mismatch is S_phase(d,theta)=|exp(i d theta)-1|^2, with second variation H_phase(d)=2d^2.",
            "Given global phase closure, use the finite mismatch norm and Lemma BH-1.",
            "DERIVED_CONDITIONAL",
            ("PO-BH-2",),
        ),
        TheoremRecord(
            "THM-BH-2",
            "Orientation involution block",
            ("AX-BH-3", "LEM-BH-2"),
            "The minimal balanced nontrivial diagonal representation is diag(+1,-1), with candidate second variation H_orientation=8I+2 lambda_trace J.",
            "Assume the involution and expand the finite diagonal surrogate.",
            "DERIVED_CONDITIONAL",
            ("PO-BH-3",),
        ),
        TheoremRecord(
            "THM-BH-3",
            "Cyclic channel block",
            ("AX-BH-4", "LEM-BH-3"),
            "The minimal nontrivial cyclic channel beyond the orientation pair is represented by order 3, with H_cyclic(3)=18.",
            "Assume order-3 closure and apply the cyclic phase lemma.",
            "DERIVED_CONDITIONAL",
            ("PO-BH-4",),
        ),
        TheoremRecord(
            "THM-BH-4",
            "Topographic/excess separation",
            ("AX-BH-5", "AX-BH-6"),
            "The Hessian separates low-energy reference/orientation/cyclic branches from excess higher/composite branches.",
            "Use the fourth-order stability scaffold and excess gap condition.",
            "DIAGNOSTIC_SUPPORTED",
            ("PO-BH-5", "PO-BH-6"),
        ),
        TheoremRecord(
            "THM-BH-5",
            "Hessian projector decomposition",
            ("THM-BH-1", "THM-BH-2", "THM-BH-3", "THM-BH-4"),
            "The candidate Hessian admits H = mu_ref P_ref + mu_orient P_orient + mu_cyclic P_cyclic + mu_excess P_excess if sectors are orthogonal.",
            "Combine the candidate blocks and require orthogonal/completing projectors.",
            "OPEN",
            ("PO-BH-7",),
        ),
        TheoremRecord(
            "THM-BH-6",
            "Closure spectrum selection",
            ("THM-BH-5",),
            "The diagnostic low-energy closure dimensions are {1,2,3}.",
            "Map selected projectors to reference, orientation, and cyclic closure sectors.",
            "OPEN",
            ("PO-BH-8",),
        ),
        TheoremRecord(
            "THM-BH-7",
            "Finite algebra bridge",
            ("THM-BH-6", "AX-BH-7", "LEM-BH-4"),
            "The selected low-energy endomorphism blocks are C, M2(C), and M3(C).",
            "Apply the finite endomorphism block lemma to d=1,2,3.",
            "DERIVED_CONDITIONAL",
            ("PO-BH-9",),
        ),
        TheoremRecord(
            "THM-BH-8",
            "Charge/anomaly skeleton",
            ("THM-BH-7", "AX-BH-8", "AX-BH-9", "LEM-BH-5", "LEM-BH-6", "LEM-BH-7"),
            "The BHSM boundary theorem chain diagnostically reproduces the Standard Model charge/hypercharge and one-generation anomaly skeleton.",
            "Use the finite algebra bridge, primitive bridge, charge formulas, and anomaly diagnostic.",
            "DIAGNOSTIC_SUPPORTED",
            ("PO-BH-10", "PO-BH-11"),
        ),
    ]
    for record in records:
        if record.status not in ALLOWED_STATUSES:
            raise ValueError(f"invalid theorem status: {record.status}")
    return {record.code: record for record in records}


def proof_obligation_ledger() -> dict[str, ProofObligationRecord]:
    records = [
        ("PO-BH-1", "Derive Berger-Hopf boundary state space from geometric action.", ("AX-BH-1",), "A boundary variational construction producing the admissible state space.", "No such boundary state space follows from the action.", "Blocks all theorem-level upgrades."),
        ("PO-BH-2", "Derive Hopf phase closure condition from global single-valuedness and admissible boundary sections.", ("AX-BH-2",), "A global section/holonomy proof of the closure condition.", "Admissible sections need not be single-valued under the candidate phase.", "Blocks phase functional derivation."),
        ("PO-BH-3", "Derive Z2 boundary orientation involution from Berger-Hopf boundary geometry rather than assuming it.", ("AX-BH-3",), "A geometric involution with balanced minimal representation.", "No canonical involution or unbalanced minimal representation.", "Blocks orientation projector."),
        ("PO-BH-4", "Derive order-3 cyclic channel closure from boundary automorphism, phase closure, or stability rather than assuming it.", ("AX-BH-4",), "A non-fitted order-3 closure theorem.", "A competing order is equally natural.", "Blocks cyclic channel projector."),
        ("PO-BH-5", "Derive fourth-order topographic stability operator from the underlying geometric variational principle.", ("AX-BH-5",), "A second-variation/topographic derivation of the fourth-order operator.", "The operator is not fourth order or has unstable sign.", "Blocks branch-count stability."),
        ("PO-BH-6", "Derive excess-sector gap from the full Hessian spectrum.", ("AX-BH-6",), "A spectral gap theorem for excess sectors.", "Higher sectors remain light and fundamental.", "Blocks low-energy closure selection."),
        ("PO-BH-7", "Prove orthogonality/completeness of P_ref, P_orient, P_cyclic, P_excess in the actual Hessian.", ("THM-BH-5",), "Projector algebra and Hessian invariance proof.", "Projectors mix or fail to sum to identity.", "Blocks Hessian decomposition."),
        ("PO-BH-8", "Prove closure spectrum {1,2,3} as a theorem, not as a diagnostic selection.", ("THM-BH-6",), "A first-principles selection theorem.", "A higher primitive closure is also low-energy.", "Blocks closure spectrum theorem."),
        ("PO-BH-9", "Derive finite algebra C_ell direct_sum M3(C)_C and M2(C) direct_sum C_+ direct_sum C_- uniquely or classify alternatives.", ("AX-BH-7", "THM-BH-7"), "A unique finite algebra theorem or controlled alternative classification.", "Another algebra produces the same diagnostics.", "Blocks finite algebra theorem."),
        ("PO-BH-10", "Derive charge/hypercharge operators from the boundary algebra without importing Standard Model labels.", ("AX-BH-8",), "Boundary-native construction of C, ell, sigma, w and charge operators.", "Charge bridge requires imported SM labels.", "Blocks charge theorem."),
        ("PO-BH-11", "Derive anomaly cancellation as a consequence of boundary consistency rather than as a downstream diagnostic.", ("AX-BH-9",), "Global boundary consistency forces anomaly cancellation.", "Anomaly cancellation remains an external check.", "Blocks anomaly theorem."),
        ("PO-BH-12", "Connect the theorem-level boundary derivation to the existing mass/Yukawa/mixing sector without changing frozen predictions.", ("THM-BH-8",), "A compatibility proof with frozen model branches.", "The theorem-level bridge changes official outputs.", "Blocks release-level integration."),
    ]
    return {
        code: ProofObligationRecord(
            code,
            name,
            "OPEN",
            assumptions,
            evidence,
            falsifier,
            impact,
        )
        for code, name, assumptions, evidence, falsifier, impact in records
    }


def non_tautology_rows() -> tuple[NonTautologyRow, ...]:
    data = [
        ("Hopf phase closure", "single-valued Hopf boundary states", "could restate desired phase closure", "Hopf phase condition", "candidate condition", "derive from global admissible sections"),
        ("Z2 orientation involution", "minimal balanced (+1,-1) pair", "could import weak doublet structure", "orientation pair", "diagnostic supported", "derive involution geometrically"),
        ("order-3 cyclic channel", "minimal cyclic closure of order 3", "could import color triplicity", "cyclic order 3", "diagnostic supported", "derive order 3 from automorphisms/stability"),
        ("finite algebra blocks C, M2(C), M3(C)", "endomorphism blocks from closure spaces", "could choose blocks to match SM", "finite algebra choice", "derived conditional", "prove physical channel space and uniqueness"),
        ("C, ell, sigma, w primitive bridge", "integer primitives from projectors/orientation", "could encode SM labels", "C, ell, sigma, w", "diagnostic supported", "derive primitives from boundary algebra"),
        ("T3, Y, Q formulas", "charge formulas from primitives", "could rewrite SM charge table", "charge formulas", "diagnostic supported", "derive operators boundary-natively"),
        ("anomaly closure", "one-generation anomaly sums vanish", "could be downstream verification only", "SM-like charge skeleton", "diagnostic supported", "derive from boundary consistency"),
        ("closure spectrum {1,2,3}", "selected low-energy closure dimensions", "could be selected to match finite algebra", "closure dimensions", "open theorem", "prove selection from Hessian"),
        ("excess-sector gap", "higher closures gapped/composite", "could suppress unwanted sectors by assumption", "gap condition", "diagnostic supported", "derive from full Hessian spectrum"),
    ]
    return tuple(NonTautologyRow(*row) for row in data)


def open_proof_obligations() -> list[str]:
    return [code for code, record in proof_obligation_ledger().items() if record.status == "OPEN"]


def theorem_chain_dependencies() -> dict:
    return {
        "axioms": list(axiom_ledger()),
        "lemmas": {code: list(record.dependencies) for code, record in lemma_ledger().items()},
        "theorems": {code: list(record.assumptions) for code, record in theorem_ledger().items()},
        "proof_obligations": {code: list(record.blocking_assumptions) for code, record in proof_obligation_ledger().items()},
    }


def is_full_boundary_derivation_complete() -> bool:
    return False


def theorem_status_summary() -> dict:
    return {
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_allowed": False,
        "boundary_action_fully_derived": False,
        "full_hessian_proof_complete": False,
        "closure_spectrum_theorem_complete": False,
        "finite_algebra_theorem_complete": False,
        "charge_anomaly_theorem_complete": False,
        "open_proof_obligations": open_proof_obligations(),
    }


def build_results_payload() -> dict:
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "standard_model_fully_derived": False,
        "bhsm_replacement_claim_allowed": False,
        "boundary_action_fully_derived": False,
        "full_hessian_proof_complete": False,
        "closure_spectrum_theorem_complete": False,
        "finite_algebra_theorem_complete": False,
        "charge_anomaly_theorem_complete": False,
        "axiom_count_minimum": 9,
        "theorem_count_minimum": 8,
        "proof_obligation_count_minimum": 12,
        "open_proof_obligations": open_proof_obligations(),
        "bridges_preserved": {
            "boundary_action_second_variation": True,
            "boundary_action_term_realization": True,
            "boundary_action_hessian_scaffold": True,
            "closure_spectrum_selection": True,
            "finite_boundary_algebra_bridge": True,
            "projector_eigenvalue_bridge": True,
            "charge_hypercharge_bridge": True,
            "anomaly_closure_bridge": True,
        },
        "negative_results": [
            "boundary action not fully derived",
            "full Hessian proof remains open",
            "closure spectrum theorem remains open",
            "finite algebra theorem remains open",
            "charge/anomaly theorem remains open",
            "several structures remain candidate assumptions or diagnostic bridges",
        ],
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "theorem-level scaffold created",
            "assumptions separated from derived lemmas",
            "proof obligations made explicit",
            "non-tautology audit created",
            "no frozen predictions changed",
            "no official predictions changed",
        ],
        "counts": {
            "axioms": len(axiom_ledger()),
            "theorems": len(theorem_ledger()),
            "lemmas": len(lemma_ledger()),
            "proof_obligations": len(proof_obligation_ledger()),
            "non_tautology_rows": len(non_tautology_rows()),
        },
        "theorem_status_summary": theorem_status_summary(),
    }


def _table(headers: tuple[str, ...], rows: list[tuple[str, ...]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def render_axioms_markdown() -> str:
    rows = [
        (
            record.code,
            record.name,
            record.status,
            record.role,
            record.discharge_condition,
            ", ".join(record.downstream_dependencies),
        )
        for record in axiom_ledger().values()
    ]
    return "# BHSM Boundary Axiom Ledger\n\n" + _table(
        ("code", "name", "status", "role", "what would discharge it", "downstream dependencies"),
        rows,
    ) + "\n"


def render_theorems_markdown() -> str:
    rows = [
        (
            record.code,
            record.name,
            record.status,
            ", ".join(record.assumptions),
            record.conclusion,
            record.proof_sketch,
            ", ".join(record.missing_proof_obligations),
        )
        for record in theorem_ledger().values()
    ]
    return "# BHSM Boundary Theorem Statements\n\n" + _table(
        ("code", "name", "status", "assumptions", "conclusion", "proof sketch", "missing proof obligations"),
        rows,
    ) + "\n"


def render_lemmas_markdown() -> str:
    rows = [
        (
            record.code,
            record.name,
            record.status,
            record.statement,
            record.proof_sketch,
            ", ".join(record.dependencies),
            record.linked_prior_gate,
        )
        for record in lemma_ledger().values()
    ]
    return "# BHSM Boundary Lemma Ledger\n\n" + _table(
        ("code", "name", "status", "statement", "proof sketch", "dependencies", "linked prior gate"),
        rows,
    ) + "\n"


def render_proof_obligations_markdown() -> str:
    rows = [
        (
            record.code,
            record.name,
            record.status,
            ", ".join(record.blocking_assumptions),
            record.required_evidence,
            record.possible_falsifier,
            record.downstream_impact,
        )
        for record in proof_obligation_ledger().values()
    ]
    return "# BHSM Boundary Proof-Obligation Ledger\n\n" + _table(
        ("code", "name", "status", "blocking assumptions", "required evidence", "possible falsifier", "downstream impact"),
        rows,
    ) + "\n"


def render_non_tautology_markdown() -> str:
    rows = [
        (
            row.step,
            row.claim,
            row.risk_of_circularity,
            row.imported_structure,
            row.current_status,
            row.required_fix,
        )
        for row in non_tautology_rows()
    ]
    return (
        "# BHSM Boundary Non-Tautology Audit\n\n"
        + _table(
            ("step", "claim", "risk of circularity", "imported structure?", "current status", "required fix"),
            rows,
        )
        + "\n\n"
        + "Conclusion: The chain is not yet a complete first-principles derivation because several structures are candidate assumptions or diagnostic bridges. The theorem program makes those assumptions explicit and testable.\n"
    )


def render_main_markdown() -> str:
    return f"""# Theorem-Level Boundary Action Derivation Scaffold

## 1. Motivation

The previous boundary-action gates produced finite diagnostic action terms, second variations, and Hessian projector support. The next step is to organize those diagnostics into theorem statements with explicit assumptions and proof obligations.

## 2. What Previous Gates Established

Previous gates established candidate functionals, local second-variation coefficients, Hessian projectors, a closure-spectrum diagnostic, finite algebra bridges, integer primitive charge formulas, and anomaly diagnostics.

## 3. Why Theorem-Level Derivation Is Now Required

The current chain contains finite diagnostic surrogates. A theorem-level derivation must identify which assumptions are geometric, which lemmas are conditional, and which proof obligations remain open.

## 4. Berger-Hopf Boundary Variables

The theorem program tracks Hopf fiber/base coordinates, Berger deformation, admissible boundary sections, phase/holonomy closure, orientation involution, cyclic closure, topographic stability, and finite channel spaces.

## 5. Axiom Ledger

See [BHSM boundary axiom ledger](bhsm_boundary_axioms.md).

## 6. Candidate Theorem Statements

See [BHSM boundary theorem statements](bhsm_boundary_theorem_statements.md).

## 7. Lemma Chain

See [BHSM boundary lemma ledger](bhsm_boundary_lemma_ledger.md).

## 8. Proof-Obligation Ledger

See [BHSM boundary proof-obligation ledger](bhsm_boundary_proof_obligation_ledger.md).

## 9. Non-Tautology Audit

See [BHSM boundary non-tautology audit](bhsm_boundary_non_tautology_audit.md).

## 10. Boundary Action Derivation Target

Derive the candidate action terms from Berger-Hopf boundary geometry rather than using finite diagnostic surrogates.

## 11. Hessian Derivation Target

Derive the full topographic Hessian and prove the projector decomposition `P_ref`, `P_orient`, `P_cyclic`, and `P_excess`.

## 12. Closure-Spectrum Derivation Target

Upgrade the diagnostic selection `{1,2,3}` to a theorem or classify alternatives.

## 13. Finite-Algebra Derivation Target

Derive the finite algebra bridge and classify possible competing algebraic realizations.

## 14. Charge/Anomaly Bridge

The existing charge/hypercharge and anomaly bridges are preserved as diagnostic downstream checks, not final first-principles derivations.

## 15. Current Theorem Status

Boundary action fully derived: false. Full Hessian proof complete: false. Closure spectrum theorem complete: false. Finite algebra theorem complete: false. Charge/anomaly theorem complete: false.

## 16. What Is Derived

The finite expansion lemmas are conditionally derived from their diagnostic surrogate assumptions. The endomorphism identity is standard conditional on physical channel-space identification.

## 17. What Remains Assumed

Hopf phase closure, orientation involution, order-3 cyclic closure, topographic stability, excess gap, finite algebra physical identification, and charge/anomaly derivation all retain open proof obligations.

## 18. What This Achieves

This sprint turns the boundary-action proof line into a testable theorem scaffold with explicit axioms, theorem statements, lemmas, proof obligations, and non-tautology checks.

## 19. What This Does Not Prove

{REQUIRED_STATUS_LANGUAGE}

It also makes no replacement claim, no full gauge-group derivation claim, and no exclusion claim for higher closures.

## 20. Next Proof Obligations

The open obligations are `PO-BH-1` through `PO-BH-12`.

## Top-Level Candidate Theorem

Theorem BHSM-Boundary-Selection-Candidate: Given a Berger-Hopf boundary with admissible Hopf fiber phase closure, boundary orientation involution, cyclic channel closure, and fourth-order topographic stability, the low-energy boundary Hessian admits a projector decomposition with reference, orientation-pair, cyclic-channel, and excess sectors. Under the candidate finite-algebra bridge, the selected low-energy closure dimensions are `{{1,2,3}}`, generating `End(C)`, `End(C^2)`, and `End(C^3)`, which diagnostically support the Standard Model charge/hypercharge and anomaly skeleton.

## Claim Labels

{chr(10).join(f'- `{label}`' for label in VERDICT_LABELS)}
"""


def export_outputs(root: Path | None = None) -> dict:
    if root is None:
        root = Path(__file__).resolve().parents[1]
    theory = root / "theory"
    payload = build_results_payload()
    outputs = {
        "theorem_level_boundary_action_derivation.md": render_main_markdown(),
        "bhsm_boundary_axioms.md": render_axioms_markdown(),
        "bhsm_boundary_theorem_statements.md": render_theorems_markdown(),
        "bhsm_boundary_lemma_ledger.md": render_lemmas_markdown(),
        "bhsm_boundary_proof_obligation_ledger.md": render_proof_obligations_markdown(),
        "bhsm_boundary_non_tautology_audit.md": render_non_tautology_markdown(),
        "bhsm_boundary_derivation_status.json": json.dumps(payload, indent=2, sort_keys=True) + "\n",
    }
    for name, text in outputs.items():
        (theory / name).write_text(text, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs()
