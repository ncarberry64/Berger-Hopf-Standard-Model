from __future__ import annotations

import json
from pathlib import Path


BRANCH = "bhsm-sm-low-energy-limit-derivation-gate-v1"
STATUS = "candidate_only"

DERIVATION_STATUSES = [
    "already_candidate_derived",
    "partially_derived",
    "preserved_as_input",
    "open_derivation_obligation",
    "failed_or_limited_candidate",
    "connected_extension_only",
]

VERDICT_LABELS = [
    "SM_LOW_ENERGY_LIMIT_DERIVATION_GATE_COMPLETE",
    "SM_INPUT_DEPENDENCY_AUDIT_COMPLETE",
    "LOCAL_SM_LAYER_STILL_PRESERVED_AS_INPUT",
    "BHSM_REPLACEMENT_BY_DERIVATION_REMAINS_OPEN",
    "BOUNDARY_PRIMITIVES_FOR_SM_DERIVATION_CATALOGED",
    "SM_REPRESENTATION_DERIVATION_OBLIGATIONS_LISTED",
    "FULL_REPLACEMENT_CLAIM_NOT_ALLOWED",
    "FROZEN_PREDICTIONS_UNCHANGED",
    "OFFICIAL_PREDICTIONS_UNCHANGED",
]

TARGET_CLASSIFICATIONS = {
    "Three-generation discrete skeleton": "partially_derived",
    "Fermion mode ledger": "partially_derived",
    "Local SM gauge group": "preserved_as_input",
    "B, L, T3 labels": "preserved_as_input",
    "Hypercharge assignments": "preserved_as_input",
    "Full chiral field content": "preserved_as_input",
    "Gauge coupling ratio 1:2:7": "partially_derived",
    "Gauge group derivation": "open_derivation_obligation",
    "Higgs/scalar decoupling": "open_derivation_obligation",
    "Mass numerical closure": "failed_or_limited_candidate",
    "Collective-curvature/dark matter": "connected_extension_only",
}

SM_INPUT_DEPENDENCIES = [
    ("B", "O_q = 3B - L and target degree law", True, "SM representation label", "preserved_as_input", "derive B as topological sector counter", "B-L/topological sector count", "boundary operators remain downstream of SM labels"),
    ("L", "O_q = 3B - L", True, "SM representation label", "preserved_as_input", "derive L as topological sector counter", "B-L/topological sector count", "lepton/quark split remains imported"),
    ("T3", "O_j = -4T3 + 2(3B)(1/2 - T3)", True, "weak-isospin input", "preserved_as_input", "derive T3 as boundary-interface eigenvalue", "weak interface orientation", "base coefficient remains SM-fed"),
    ("Y", "hypercharge and electric charge screens", True, "SM charge assignment", "preserved_as_input", "derive admissible U(1) boundary phase closure", "boundary phase closure", "hypercharge remains imported"),
    ("Q", "Q = T3 + Y/2", True, "SM charge relation", "preserved_as_input", "derive electric charge from boundary closure", "boundary closure eigenvalue", "electric charge remains downstream"),
    ("SU(3)_c", "local color gauge factor", True, "local gauge input", "preserved_as_input", "derive color algebra from boundary automorphisms", "three-channel internal degeneracy", "local color remains input"),
    ("SU(2)_L", "local weak gauge factor", True, "local gauge input", "preserved_as_input", "derive weak algebra from interface channels", "two-state boundary orientation", "weak layer remains input"),
    ("U(1)_Y", "hypercharge gauge factor", True, "local gauge input", "preserved_as_input", "derive U(1) from boundary phase closure", "admissible phase closure", "trace/U(1) layer remains input"),
    ("fermion chirality", "chiral multiplet ledger", True, "SM chiral structure", "preserved_as_input", "derive chirality from boundary orientation/asymmetry", "boundary orientation", "mirror exclusion remains conditional"),
    ("left/right multiplets", "field content ledger", True, "SM multiplet input", "preserved_as_input", "derive L/R split from boundary domain", "boundary domain asymmetry", "field content remains imported"),
    ("color triplet/singlet split", "quark/lepton branch structure", True, "SM representation input", "preserved_as_input", "derive from active three-channel degeneracy", "color channel automorphism", "sector split remains imported"),
    ("weak doublet/singlet split", "T3 and chirality use", True, "SM representation input", "preserved_as_input", "derive from boundary interface orientation", "two-state interface orientation", "weak split remains imported"),
    ("Higgs doublet", "Yukawa and electroweak screens", True, "SM scalar input", "preserved_as_input", "derive from boundary deformation mode", "boundary deformation mode", "scalar sector remains scaffolded"),
    ("Yukawa coupling layer", "mass hierarchy screens", True, "SM free-parameter layer", "failed_or_limited_candidate", "derive collective threshold mass law", "collective curvature fixed point", "mass numerical closure remains open"),
    ("CKM", "mixing screens", True, "SM empirical mixing structure", "open_derivation_obligation", "derive interface kernels", "boundary interface kernel", "mixing remains structural candidate"),
    ("PMNS", "effective neutrino extension", True, "effective extension input/comparison", "open_derivation_obligation", "derive conjugate-cover kernels", "boundary interface kernel", "neutrino mixing remains candidate"),
    ("anomaly cancellation", "hypercharge consistency checks", True, "SM consistency condition", "preserved_as_input", "derive from boundary closure consistency", "global boundary closure", "anomaly cancellation remains downstream"),
]

BOUNDARY_PRIMITIVES = [
    ("Hopf fiber winding", "fiber charge q and cyclic phase", "operationally_tested"),
    ("Berger base winding", "base index j and branch structure", "operationally_tested"),
    ("boundary orientation", "candidate source of chirality and sign", "candidate_primitive"),
    ("chirality from boundary orientation/asymmetry", "possible replacement for imported chirality", "needs_derivation"),
    ("color from active three-channel internal degeneracy", "possible SU(3)-like channel source", "needs_derivation"),
    ("weak isospin from two-state boundary interface orientation", "possible SU(2)-like channel source", "needs_derivation"),
    ("hypercharge from admissible boundary phase closure", "possible U(1)_Y source", "needs_derivation"),
    ("B-L from topological sector count", "possible replacement for B and L labels", "needs_derivation"),
    ("generation from zero + two nonzero topographic branches", "candidate generation-count source", "operationally_tested"),
    ("Higgs/scalar from boundary deformation mode", "possible scalar representation source", "speculative"),
    ("gauge group from automorphism/action algebra of admissible boundary channels", "possible local gauge derivation route", "needs_derivation"),
    ("anomaly cancellation from boundary closure consistency", "possible anomaly-free ledger route", "needs_derivation"),
]

REPLACEMENT_OBLIGATIONS = [
    "Derive chirality from Berger-Hopf boundary orientation or topographic asymmetry.",
    "Derive color triplicity and SU(3)-like channel algebra from boundary automorphisms.",
    "Derive weak doublet/singlet structure from boundary interface orientation.",
    "Derive U(1) hypercharge assignments from admissible boundary phase closure.",
    "Derive B and L as topological sector counters rather than imported labels.",
    "Derive T3 as a boundary-interface eigenvalue rather than an SM input.",
    "Derive electric charge Q = T3 + Y/2 from boundary closure.",
    "Derive anomaly cancellation from global boundary consistency.",
    "Derive Higgs/scalar representation from boundary deformation mode.",
    "Derive three generations from fourth-order topographic stability with full Hessian proof.",
    "Derive the fermion mode ledger without importing B,L,T3.",
    "Recover the local SM Lagrangian as a low-energy effective limit.",
    "Derive or constrain gauge coupling normalization beyond active-generator counting.",
    "Derive the collective curvature threshold mass law.",
    "Recover CKM and PMNS as interface kernels.",
]


def classify_target(name: str) -> str:
    return TARGET_CLASSIFICATIONS[name]


def sm_input_dependency_registry() -> list[dict[str, object]]:
    keys = [
        "object",
        "formula_or_usage",
        "uses_sm_input",
        "input_type",
        "bhsm_status",
        "replacement_needed_for_full_derivation",
        "candidate_bhsm_primitive",
        "risk_if_unreplaced",
    ]
    return [dict(zip(keys, row)) for row in SM_INPUT_DEPENDENCIES]


def boundary_primitive_registry() -> list[dict[str, str]]:
    return [
        {"primitive": primitive, "candidate_role": role, "status": status}
        for primitive, role, status in BOUNDARY_PRIMITIVES
    ]


def replacement_obligation_registry() -> list[dict[str, str]]:
    return [
        {"id": f"R{i}", "obligation": obligation, "status": "open_derivation_obligation"}
        for i, obligation in enumerate(REPLACEMENT_OBLIGATIONS, start=1)
    ]


def is_full_replacement_claim_allowed(status: dict) -> bool:
    required = [
        "local_gauge_group_derived",
        "field_content_derived",
        "charge_assignments_derived",
        "masses_mixings_derived",
        "higgs_scalar_derived",
        "anomaly_cancellation_derived",
        "low_energy_lagrangian_recovered",
    ]
    return all(status.get(key) is True for key in required)


def build_results_payload() -> dict:
    derived_or_partial = [
        target
        for target, status in TARGET_CLASSIFICATIONS.items()
        if status in {"already_candidate_derived", "partially_derived"}
    ]
    preserved = [
        target
        for target, status in TARGET_CLASSIFICATIONS.items()
        if status == "preserved_as_input"
    ]
    open_obligations = [
        target
        for target, status in TARGET_CLASSIFICATIONS.items()
        if status == "open_derivation_obligation"
    ]
    failed = [
        target
        for target, status in TARGET_CLASSIFICATIONS.items()
        if status == "failed_or_limited_candidate"
    ]
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "bhsm_replacement_claim_allowed": False,
        "standard_model_fully_derived": False,
        "local_sm_layer_status": "preserved_as_input",
        "replacement_by_derivation_goal": True,
        "core_particle_sector_only": True,
        "collective_curvature_extension_separate": True,
        "derived_or_partially_derived_targets": derived_or_partial,
        "preserved_input_targets": preserved,
        "open_derivation_obligations": open_obligations + REPLACEMENT_OBLIGATIONS,
        "failed_or_limited_candidates": failed,
        "connected_extension_targets": [
            target for target, status in TARGET_CLASSIFICATIONS.items() if status == "connected_extension_only"
        ],
        "verdict_labels": VERDICT_LABELS,
        "notes": [
            "candidate-only",
            "derivation gate audit",
            "BHSM replacement by derivation remains open",
            "local SM layer remains preserved input",
            "collective curvature extension remains separate",
        ],
    }


def _table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    return "\n".join(lines)


def render_gate_markdown() -> str:
    rows = [[target, status] for target, status in TARGET_CLASSIFICATIONS.items()]
    return f"""# SM Low-Energy Limit Derivation Gate

BHSM replacement requires deriving the Standard Model as the low-energy effective limit of BHSM. This has not yet been achieved.

## Derivation Target

BHSM must produce a local infrared effective theory with:

- SU(3)_c x SU(2)_L x U(1)_Y gauge structure,
- chiral fermion multiplets,
- observed hypercharge assignments,
- three generations,
- Higgs/scalar sector,
- Yukawa/mass hierarchy,
- CKM and PMNS mixing,
- anomaly cancellation,
- low-energy coupling normalization.

## Current Target Classification

{_table(["target", "classification"], rows)}

## Guardrail

This derivation gate does not claim that BHSM has derived or replaced the Standard Model. The local SM gauge and representation layer remains a preserved infrared input until the obligations listed in `sm_representation_derivation_obligations.md` are closed.

## Integer Primitive And Finite Algebra Gates

- [Boundary integer charge/hypercharge bridge](boundary_integer_charge_hypercharge_bridge.md)
- [Boundary integer anomaly closure gate](boundary_integer_anomaly_closure_gate.md)
- [Boundary projector algebra gate](boundary_projector_algebra_gate.md)
- [Finite boundary algebra source gate](finite_boundary_algebra_source_gate.md)
- [Boundary automorphism closure origin gate](boundary_automorphism_closure_origin_gate.md)
- [Admissible boundary closure spectrum gate](admissible_boundary_closure_spectrum_gate.md)
"""


def render_dependency_markdown() -> str:
    headers = [
        "object",
        "formula_or_usage",
        "uses_sm_input",
        "input_type",
        "bhsm_status",
        "replacement_needed_for_full_derivation",
        "candidate_bhsm_primitive",
        "risk_if_unreplaced",
    ]
    rows = [[row[h] for h in headers] for row in sm_input_dependency_registry()]
    return f"""# SM Input Dependency Audit

{_table(headers, rows)}

## Conclusion

The strongest current BHSM layer is downstream of the preserved local SM representation data. Replacement by derivation requires moving B, L, T3, chirality, color, weak isospin, and hypercharge from inputs to outputs of the Berger-Hopf/topographic boundary system.
"""


def render_primitives_markdown() -> str:
    rows = [
        [row["primitive"], row["candidate_role"], row["status"]]
        for row in boundary_primitive_registry()
    ]
    return f"""# BHSM Boundary Primitives For SM Derivation

This file catalogs BHSM-native primitives that could eventually replace imported SM representation inputs. It is a roadmap, not a derivation claim.

{_table(["primitive", "candidate_role", "status"], rows)}

No primitive in this file is promoted to full gauge-group derivation.
"""


def render_obligations_markdown() -> str:
    lines = ["# SM Representation Derivation Obligations", ""]
    lines.extend(f"{i}. {obligation}" for i, obligation in enumerate(REPLACEMENT_OBLIGATIONS, start=1))
    lines.append("")
    lines.append("These obligations must be closed before BHSM can claim replacement by derivation.")
    lines.append("")
    lines.append("## Related Diagnostic Gates")
    lines.append("")
    lines.append("- [Boundary integer charge/hypercharge bridge](boundary_integer_charge_hypercharge_bridge.md)")
    lines.append("- [Boundary integer anomaly closure gate](boundary_integer_anomaly_closure_gate.md)")
    lines.append("- [Boundary projector algebra gate](boundary_projector_algebra_gate.md)")
    lines.append("- [Finite boundary algebra source gate](finite_boundary_algebra_source_gate.md)")
    lines.append("- [Boundary automorphism closure origin gate](boundary_automorphism_closure_origin_gate.md)")
    lines.append("- [Admissible boundary closure spectrum gate](admissible_boundary_closure_spectrum_gate.md)")
    return "\n".join(lines) + "\n"


def export_outputs(root: str | Path = ".") -> dict:
    root = Path(root)
    theory = root / "theory"
    theory.mkdir(exist_ok=True)
    payload = build_results_payload()
    files = {
        "sm_low_energy_limit_derivation_gate.md": render_gate_markdown(),
        "sm_input_dependency_audit.md": render_dependency_markdown(),
        "bhsm_boundary_primitives_for_sm_derivation.md": render_primitives_markdown(),
        "sm_representation_derivation_obligations.md": render_obligations_markdown(),
        "sm_low_energy_limit_derivation_results.json": json.dumps(payload, indent=2, sort_keys=True) + "\n",
    }
    for name, content in files.items():
        (theory / name).write_text(content, encoding="utf-8")
    return payload


if __name__ == "__main__":
    export_outputs(Path(__file__).resolve().parents[1])
