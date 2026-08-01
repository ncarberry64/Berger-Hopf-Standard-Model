"""Canonical BHSM v10.1 Relational Envelopment Holism doctrine.

The author doctrine is stored separately from mathematical interpretations so
that repository code cannot silently promote an ontology statement to a
derived theorem or alter the author's wording.
"""

from __future__ import annotations

from enum import Enum
import hashlib
import json
from typing import Any


VERSION = "v10.1"
SPRINT = "bhsm-relational-envelopment-holism-v10-1"
SOURCE_V10_SHA = "39378a144eda922ecec98e71d710bf515709f937"
FOUNDATION_VERDICT = "BHSM_RELATIONAL_ENVELOPMENT_HOLISM_DOCTRINE_INTEGRATED"
PRIMARY_VERDICT = (
    "BHSM_RELATIONAL_ENVELOPMENT_PARENT_ACTION_CONSTRAINTS_"
    "CONSTRUCTED_CONDITIONALLY"
)
ACTION_LIMIT_VERDICT = (
    "BHSM_CURRENT_PARENT_ACTION_DOES_NOT_DERIVE_ALL_RELATIONAL_"
    "ENVELOPMENT_AXIOMS"
)
NEXT_EXACT_OBJECT = (
    "COVARIANT_ACTION_DERIVED_NORMAL_RADION_BUOYANCY_FUNCTIONAL_WITH_"
    "GLOBAL_CONSTRAINT_AND_LOCAL_ENVELOPMENT_BACKREACTION"
)
EXPECTED_DOCTRINE_SHA256 = "f981a6501526a3ff324cbf5cb4f1e26b1f7d3ecd0c7b2759c200f6aa1ee184b0"


class DoctrineStatus(str, Enum):
    AUTHOR_AXIOM = "AUTHOR_AXIOM"
    AUTHOR_ONTOLOGY = "AUTHOR_ONTOLOGY"
    HARD_ARCHITECTURAL_CONSTRAINT = "HARD_ARCHITECTURAL_CONSTRAINT"
    DERIVED = "DERIVED"
    DERIVED_CONDITIONAL = "DERIVED_CONDITIONAL"
    STRUCTURAL_POSTULATE = "STRUCTURAL_POSTULATE"
    CANDIDATE = "CANDIDATE"
    PROXY_ONLY = "PROXY_ONLY"
    INVALIDATED = "INVALIDATED"
    OPEN = "OPEN"
    BLOCKED_EXACT_OBJECT_PROVED = "BLOCKED_EXACT_OBJECT_PROVED"


# Do not alter these strings without explicit author authorization.  This is
# the exact semantic JSON object supplied in the v10.1 campaign brief.
AUTHOR_DOCTRINE: dict[str, Any] = {
    "project": "Berger-Hopf Standard Model (BHSM)",
    "paradigm": "Relational Envelopment Holism",
    "foundational_axiom": "The whole determines the permitted local differentials, and the local differentials continually reshape the whole.",
    "physical_axioms": {
        "gravity": {
            "concept": "Topological Buoyancy",
            "mechanism": "Radial density gradient across the S^3 x M_4 manifold where local geometry balances against global cosmic tension.",
            "energy_space_scaling": {
                "high_energy_compact": "Sinks closer toward the 4D core due to local curvature deformation.",
                "low_energy_diffuse": "Sits higher on the 3D hypersurface boundary.",
            },
            "relational_rule": "Gravitational attraction is radial equilibrium minimizing combined buoyancy potential across the unified background rather than a force mediated by independent particles.",
        },
        "time_and_entropy": {
            "status": "Non-Fundamental / Scale-Dependent Artifacts",
            "concept": "Spacetime Hypersurface Integrity",
            "mechanism": "Space-time is treated as a single, continuous 3D surface. Local entropy is merely a scale-dependent observation of microscopic geometric breathing.",
            "scale_analogy": "Local Brownian fluctuations appear disordered at microscopic resolution, but represent ordered energy redistribution when viewed from the master cosmic scale.",
            "master_conservation": "Total topological information and energy are strictly conserved on the cosmic level; built-in arrows of thermodynamic decay are explicitly avoided.",
        },
        "antimatter_and_particle_identity": {
            "status": "Relational Boundary Complementarity",
            "concept": "Unified Envelopment Topology",
            "mechanism": "Matter and antimatter are not distinct particle species or time-reversed states; they are identical underlying spacetime enclosures.",
            "relational_properties": "Distinction lies entirely in the relative orientation and phase alignment of boundary properties (e.g., the eta triality-spinor field) with respect to the local environment.",
            "neutrino_identity": "Neutrinos are propagation-supported envelopes without a stationary rest state; Dirac vs. Majorana distinctions are replaced by relational phase orientations at the interaction vertex.",
        },
    },
    "integration_target": "Use these axioms as hard constraints when formulating 8D field equations, boundary conditions, and global conserved quantities in BHSM Extended Parent Action v2.",
}


def deterministic_json(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def doctrine_bytes() -> bytes:
    return deterministic_json(AUTHOR_DOCTRINE).encode("utf-8")


def doctrine_sha256() -> str:
    return hashlib.sha256(doctrine_bytes()).hexdigest()


def _record(
    *,
    name: str,
    exact_author_text: Any,
    mathematical_translation: str,
    action_location: str | None,
    current_status: DoctrineStatus,
    qualification_status: str,
    required_proof: str,
    falsification_condition: str,
    downstream_dependencies: list[str],
    forbidden_promotions: list[str],
) -> dict[str, Any]:
    return {
        "name": name,
        "exact_author_text": exact_author_text,
        "mathematical_translation": mathematical_translation,
        "action_location": action_location,
        "current_status": current_status.value,
        "qualification_status": qualification_status,
        "required_proof": required_proof,
        "falsification_condition": falsification_condition,
        "downstream_dependencies": downstream_dependencies,
        "forbidden_promotions": forbidden_promotions,
        "source_provenance": {
            "kind": "author-supplied campaign doctrine",
            "version": VERSION,
            "source_v10_sha": SOURCE_V10_SHA,
            "canonical_doctrine_sha256": doctrine_sha256(),
        },
    }


def doctrine_records() -> list[dict[str, Any]]:
    axioms = AUTHOR_DOCTRINE["physical_axioms"]
    return [
        _record(
            name="relational_envelopment_holism",
            exact_author_text=AUTHOR_DOCTRINE["foundational_axiom"],
            mathematical_translation="closed cosmos -> admissible local solution space, with local total stress returned to the global constraints",
            action_location="complete stratified variational problem",
            current_status=DoctrineStatus.AUTHOR_AXIOM,
            qualification_status="HARD_ARCHITECTURAL_CONSTRAINT",
            required_proof="GLOBAL_LOCAL_SOLUTION_AND_BACKREACTION_FIXED_POINT_THEOREM",
            falsification_condition="no admissible complete action can implement reciprocal global/local constraint closure",
            downstream_dependencies=["all physical orbit and scale theorems"],
            forbidden_promotions=["derived law of nature", "empirical validation"],
        ),
        _record(
            name="topological_buoyancy",
            exact_author_text=axioms["gravity"],
            mathematical_translation="covariant normal/radion Euler-Lagrange balance with a calculated energy-depth sign",
            action_location="metric/radion variation plus GHY, collar, stress, and global constraints",
            current_status=DoctrineStatus.STRUCTURAL_POSTULATE,
            qualification_status="OPEN_ACTION_DERIVATION",
            required_proof="COVARIANT_RADIAL_BUOYANCY_FUNCTIONAL",
            falsification_condition="the complete action has no stable covariant normal balance or gives the opposite derived ordering",
            downstream_dependencies=["charged orbit", "global scale", "weak-field gravity"],
            forbidden_promotions=["new phenomenological force", "replacement of gravity before weak-field recovery"],
        ),
        _record(
            name="time_entropy_and_cosmic_conservation",
            exact_author_text=axioms["time_and_entropy"],
            mathematical_translation="reversible closed-system action plus explicit subsystem coarse graining and covariant constraint/flux conservation",
            action_location="parent Hamiltonian/covariant phase space and boundary flux ledger",
            current_status=DoctrineStatus.AUTHOR_ONTOLOGY,
            qualification_status="OPEN_ACTION_DERIVATION",
            required_proof="GLOBAL_HAMILTONIAN_OR_QUASILOCAL_CONSERVATION_THEOREM_AND_COARSE_GRAINING_MAP",
            falsification_condition="fundamental action requires irreducible dissipation or topological degree changes without boundary/singularity events",
            downstream_dependencies=["entropy", "measurement", "cosmic scale"],
            forbidden_promotions=["coordinate integral of T00 as cosmic energy", "entropy solved by analogy"],
        ),
        _record(
            name="matter_antimatter_boundary_complementarity",
            exact_author_text=axioms["antimatter_and_particle_identity"],
            mathematical_translation="involutive conjugation/orientation map on physical orbit classes preserving stress and reversing additive charges",
            action_location="eta plus intrinsic M4 gauge/fermion/current sectors",
            current_status=DoctrineStatus.OPEN,
            qualification_status="OPEN_PHYSICAL_EQUIVALENCE",
            required_proof="ETA_BOUNDARY_COMPLEMENTARITY_INVOLUTION_WITH_FULL_GAUGE_REPRESENTATION_DATA",
            falsification_condition="no involution can preserve spectrum/stress while producing observed conjugate charges and vertices",
            downstream_dependencies=["antiparticle dictionary", "annihilation", "neutrino vertex observables"],
            forbidden_promotions=["deletion of antiparticle fields", "orientation-only physical equivalence"],
        ),
        _record(
            name="neutrino_relational_identity",
            exact_author_text=axioms["antimatter_and_particle_identity"]["neutrino_identity"],
            mathematical_translation="near-null propagation orbit with three monodromy sectors and a weak-current vertex projector",
            action_location="dynamic orbit and intrinsic weak-current pullback",
            current_status=DoctrineStatus.AUTHOR_ONTOLOGY,
            qualification_status="OPEN_PHYSICAL_EQUIVALENCE",
            required_proof="NEUTRINO_VERTEX_PHASE_OBSERVABLE_MAP",
            falsification_condition="derived BHSM observables cannot express Dirac/Majorana-sensitive processes or conflict with a solved monodromy sector",
            downstream_dependencies=["PMNS", "Delta m2 unit bridge", "neutrinoless double beta decay"],
            forbidden_promotions=["primitive static rest mass", "claim that Dirac/Majorana experiments are irrelevant"],
        ),
    ]


def hard_architectural_invariants() -> list[dict[str, str]]:
    statements = [
        "No isolated particle ontology.",
        "No passive nondynamical background.",
        "No independent gravity mediator.",
        "No fundamental irreversible entropy term without explicit author authorization.",
        "No separate matter/antimatter core ontology without first exhausting boundary complementarity.",
        "No primitive static neutrino rest-mass assignment.",
        "No local arbitrary mass scale if a global scale theorem remains available.",
        "No measured flavor or mass inputs inside theorem derivations.",
        "No change to frozen predictions.",
        "No physical CKM or PMNS matrix without action-owned orbit pullbacks.",
    ]
    return [
        {"invariant": statement, "status": DoctrineStatus.HARD_ARCHITECTURAL_CONSTRAINT.value}
        for statement in statements
    ]


def constraint_ledger() -> dict[str, Any]:
    records = doctrine_records()
    statuses = {status.value for status in DoctrineStatus}
    required = {
        "name", "exact_author_text", "mathematical_translation", "action_location",
        "current_status", "qualification_status", "required_proof", "falsification_condition",
        "downstream_dependencies", "forbidden_promotions", "source_provenance",
    }
    validation = {
        "canonical_doctrine_hash_stable": doctrine_sha256() == EXPECTED_DOCTRINE_SHA256,
        "record_schema_complete": all(set(row) == required for row in records),
        "statuses_recognized": all(row["current_status"] in statuses for row in records),
        "qualifications_recognized": all(
            row["qualification_status"] in {
                "HARD_ARCHITECTURAL_CONSTRAINT", "OPEN_ACTION_DERIVATION", "OPEN_PHYSICAL_EQUIVALENCE"
            }
            for row in records
        ),
        "author_axioms_not_derived": all(
            row["current_status"] != DoctrineStatus.DERIVED.value
            for row in records
            if row["name"] in {
                "relational_envelopment_holism", "topological_buoyancy",
                "time_entropy_and_cosmic_conservation",
                "matter_antimatter_boundary_complementarity",
                "neutrino_relational_identity",
            }
        ),
        "hard_invariant_count": len(hard_architectural_invariants()) == 10,
    }
    return {
        "artifact": "BHSM_relational_envelopment_constraint_ledger_v10_1",
        "version": VERSION,
        "sprint": SPRINT,
        "source_v10_sha": SOURCE_V10_SHA,
        "canonical_doctrine_sha256": doctrine_sha256(),
        "status_vocabulary": sorted(statuses),
        "doctrine_records": records,
        "hard_architectural_invariants": hard_architectural_invariants(),
        "validation": validation,
        "validation_passed": all(validation.values()),
        "foundation_verdict": FOUNDATION_VERDICT,
    }
