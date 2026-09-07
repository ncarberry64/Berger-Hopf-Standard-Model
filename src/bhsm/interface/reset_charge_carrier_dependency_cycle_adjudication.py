"""Formal reset/charge/carrier dependency-cycle adjudication.

This module turns the Track-2 dependency claim into a typed directed graph,
computes its strongly connected components, and tests the smallest admissible
cycle-breaking hypotheses.  It deliberately does not instantiate the missing
interface functional or assign any downstream charge, carrier, or reset value.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations
from typing import Any, Iterable

from bhsm.interface.reset_correspondence_stationarity_adjudication import (
    interface_functional_deficit,
)


ACTION_VERSION = "BHSM-AE-3.2.14-RESET-CHARGE-CARRIER-CYCLE-ADJUDICATION"
CLASSIFICATION = "RESET_CHARGE_CARRIER_TRUE_CYCLE_ONE_NEW_FUNCTIONAL_PRIMITIVE"
CG_CLASS = "CG3"
GE_CLASS = "GE3"
HJ_CLASS = "HJ3"
INC_CLASS = "INC3"
LOOP_CLASS = "LOOP3"
EXACT_NEXT_OBJECT = (
    "OWNER_SELECTION_OF_ONE_ACTION_OWNED_COVARIANT_FULL_FIELD_INTERFACE_"
    "GENERATING_FUNCTIONAL_WITH_CARRIER_EMBEDDING_RESET_RELATION_AND_FIRST_"
    "MOVING_DOMAIN_VARIATION"
)

EDGE_CLASSES = frozenset(
    {
        "DERIVED",
        "CONDITIONAL",
        "OWNER_SEMANTICS",
        "HISTORICAL_HYPOTHESIS",
        "MISSING",
        "INVALIDATED",
        "REDUNDANT",
    }
)
ACTIVE_EDGE_CLASSES = EDGE_CLASSES - {"INVALIDATED", "REDUNDANT"}


@dataclass(frozen=True)
class Node:
    id: str
    label: str
    status: str


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    classification: str
    reason: str


def dependency_nodes() -> tuple[Node, ...]:
    """Return all required objects plus the three tested deeper authorities."""

    rows = (
        ("interface_functional", "full-field interface generating functional", "MISSING"),
        ("CA_to_GA", "C_A to G_A transition", "OWNER_SEMANTICS"),
        ("global_envelopment", "global-envelopment functional", "CONDITIONAL"),
        ("boundary_HJ", "boundary Hamilton-Jacobi principal function", "CONDITIONAL"),
        ("reset_graph", "F_B-dependent reset graph", "MISSING"),
        ("nonfermion_Ls", "nonfermion L_s", "MISSING"),
        ("moving_variation", "moving-domain first variation", "MISSING"),
        ("tangent_domain", "full event-child tangent domain", "MISSING"),
        ("theta", "complete presymplectic potential", "MISSING"),
        ("generator_xi", "common generator xi", "MISSING"),
        ("hamiltonian", "differentiable Hamiltonian", "MISSING"),
        ("reference", "reference, ensemble, and counterterm", "MISSING"),
        ("mode_projector", "physical event-mode projector", "MISSING"),
        ("event_mode_charge", "event-mode charge", "MISSING"),
        ("retained_charge", "retained outgoing charge ledger", "CONDITIONAL"),
        ("available_charge", "available-mode charge", "MISSING"),
        ("child_seam_charge", "child plus seam charge", "MISSING"),
        ("envelopment_increment", "envelopment increment", "MISSING"),
        ("rho_hold", "rho_hold", "MISSING"),
        ("energetic_carrier", "energetic encapsulation carrier", "MISSING"),
        ("actual_stabilizer", "actual stabilizer", "MISSING"),
        ("physical_projectors", "physical spectral projectors", "MISSING"),
        ("event_child_incidence", "event-to-child incidence", "OWNER_SEMANTICS"),
        ("active_response", "active encapsulation response", "MISSING"),
        ("reduced_reset", "reduced reset", "MISSING"),
        ("beta", "beta", "MISSING"),
        ("graph_jets", "graph jets", "MISSING"),
        ("S1", "S1 action attachment", "MISSING"),
        ("S2", "S2 action attachment", "MISSING"),
        ("S3", "S3 action attachment", "MISSING"),
        ("S4", "S4 action attachment", "MISSING"),
        ("full_attachment", "full-field action attachment", "MISSING"),
    )
    return tuple(Node(*row) for row in rows)


def _edge(source: str, target: str, classification: str, reason: str) -> Edge:
    assert classification in EDGE_CLASSES
    return Edge(source, target, classification, reason)


def dependency_edges() -> tuple[Edge, ...]:
    """Return prerequisite-to-dependent edges with an explicit evidence class."""

    return (
        _edge("interface_functional", "reset_graph", "MISSING", "its F_B Euler-Lagrange equation would select the graph"),
        _edge("interface_functional", "nonfermion_Ls", "MISSING", "its boundary Legendre relation would select L_s"),
        _edge("interface_functional", "energetic_carrier", "MISSING", "embedding stationarity would co-select the carrier"),
        _edge("CA_to_GA", "reset_graph", "OWNER_SEMANTICS", "an operative emergence map could provide geometry and reset data; none is defined"),
        _edge("CA_to_GA", "energetic_carrier", "OWNER_SEMANTICS", "owner ontology says actualization precedes geometry but gives no carrier equation"),
        _edge("global_envelopment", "reset_graph", "CONDITIONAL", "the synthetic KKT architecture could select a reset only after physical inputs are supplied"),
        _edge("reset_graph", "global_envelopment", "MISSING", "physical global envelopment still requires domain, incidence, coefficients, and branch control"),
        _edge("boundary_HJ", "reset_graph", "CONDITIONAL", "a genuine principal function would generate a canonical relation"),
        _edge("reset_graph", "boundary_HJ", "MISSING", "the regional on-shell BVP needs the very event-child domain it is proposed to generate"),
        _edge("reset_graph", "nonfermion_Ls", "CONDITIONAL", "a selected polarized graph determines a member of the nonfermion Lagrangian family"),
        _edge("reset_graph", "moving_variation", "MISSING", "shape differentiation requires F_B as an action configuration argument"),
        _edge("nonfermion_Ls", "tangent_domain", "MISSING", "the tangent space must obey the selected nonfermion boundary relation"),
        _edge("moving_variation", "tangent_domain", "MISSING", "the moving graph derivative supplies its linearized tangent condition"),
        _edge("tangent_domain", "theta", "MISSING", "sector potentials cannot be assembled without one common domain"),
        _edge("full_attachment", "theta", "MISSING", "the complete action attachment is required for the complete boundary potential"),
        _edge("tangent_domain", "generator_xi", "MISSING", "xi must be tangent to the selected event-child domain"),
        _edge("theta", "generator_xi", "MISSING", "a common covariant phase space is needed to identify a Hamiltonian symmetry"),
        _edge("theta", "hamiltonian", "MISSING", "delta H_xi is assembled from the complete potential"),
        _edge("generator_xi", "hamiltonian", "MISSING", "differentiability is a property of the selected generator"),
        _edge("hamiltonian", "event_mode_charge", "MISSING", "the event-mode charge is a mode projection of H_xi"),
        _edge("reference", "event_mode_charge", "MISSING", "the absolute charge requires an ensemble and zero-point prescription"),
        _edge("mode_projector", "event_mode_charge", "MISSING", "a physical projector is required to isolate the initiating mode"),
        _edge("event_mode_charge", "available_charge", "DERIVED", "the bookkeeping subtraction is algebraically fixed once every common charge exists"),
        _edge("retained_charge", "available_charge", "CONDITIONAL", "the retained outgoing ledger would be subtracted only after a common charge exists"),
        _edge("hamiltonian", "child_seam_charge", "MISSING", "child and seam terms require the same differentiable generator"),
        _edge("reference", "child_seam_charge", "MISSING", "the comparison requires the same reference ensemble"),
        _edge("available_charge", "envelopment_increment", "MISSING", "the increment compares available and child-seam charges"),
        _edge("child_seam_charge", "envelopment_increment", "MISSING", "the child-seam charge is the second comparison endpoint"),
        _edge("available_charge", "rho_hold", "MISSING", "rho_hold requires the available energetic quantity"),
        _edge("child_seam_charge", "rho_hold", "MISSING", "rho_hold requires the child/seam energetic response"),
        _edge("envelopment_increment", "rho_hold", "MISSING", "the historical ratio must be rebuilt from a valid charge increment"),
        _edge("rho_hold", "energetic_carrier", "HISTORICAL_HYPOTHESIS", "the historical first-positive energetic crossing was proposed to select the carrier"),
        _edge("energetic_carrier", "actual_stabilizer", "MISSING", "the stabilizer is defined only for the selected physical carrier"),
        _edge("actual_stabilizer", "physical_projectors", "MISSING", "physical spectra are organized into actual stabilizer sectors"),
        _edge("tangent_domain", "physical_projectors", "MISSING", "projectors must act on the common physical domain"),
        _edge("physical_projectors", "mode_projector", "MISSING", "the event-mode projector is one selected physical spectral projector"),
        _edge("energetic_carrier", "event_child_incidence", "OWNER_SEMANTICS", "incidence needs a base carrier and orientation"),
        _edge("physical_projectors", "event_child_incidence", "MISSING", "full incidence must intertwine physical mode sectors"),
        _edge("event_child_incidence", "reset_graph", "MISSING", "full-field incidence would provide the base and bundle transport entering F_B"),
        _edge("energetic_carrier", "active_response", "MISSING", "response is evaluated about the selected carrier"),
        _edge("actual_stabilizer", "active_response", "MISSING", "the active response quotient needs the actual stabilizer"),
        _edge("physical_projectors", "active_response", "MISSING", "the response reduction needs physical projectors"),
        _edge("event_child_incidence", "active_response", "MISSING", "the response must be transported between event and child"),
        _edge("active_response", "reduced_reset", "MISSING", "the reduced reset is induced on the active response quotient"),
        _edge("reset_graph", "reduced_reset", "MISSING", "the reduced reset is a quotient of the full reset"),
        _edge("reduced_reset", "beta", "MISSING", "beta is extracted only after the physical reduced reset is known"),
        _edge("reset_graph", "graph_jets", "MISSING", "jets require the selected graph value"),
        _edge("moving_variation", "graph_jets", "MISSING", "the first graph jet begins with the moving-domain variation"),
        _edge("graph_jets", "S1", "CONDITIONAL", "S1 is the first-order attachment once the physical jet is known"),
        _edge("graph_jets", "S2", "CONDITIONAL", "S2 requires the second physical graph jet"),
        _edge("graph_jets", "S3", "CONDITIONAL", "S3 requires the third physical graph jet"),
        _edge("graph_jets", "S4", "CONDITIONAL", "S4 requires the fourth physical graph jet"),
        _edge("S1", "full_attachment", "CONDITIONAL", "the full attachment contains every earned order"),
        _edge("S2", "full_attachment", "CONDITIONAL", "the full attachment contains every earned order"),
        _edge("S3", "full_attachment", "CONDITIONAL", "the full attachment contains every earned order"),
        _edge("S4", "full_attachment", "CONDITIONAL", "the full attachment contains every earned order"),
        _edge("global_envelopment", "rho_hold", "INVALIDATED", "synthetic witness coefficients cannot define a physical energetic ratio"),
        _edge("retained_charge", "energetic_carrier", "REDUNDANT", "raw retained ledger entries do not independently select a carrier"),
    )


def _active_adjacency(excluded_nodes: Iterable[str] = ()) -> dict[str, list[str]]:
    excluded = set(excluded_nodes)
    adjacency = {node.id: [] for node in dependency_nodes() if node.id not in excluded}
    for edge in dependency_edges():
        if (
            edge.classification in ACTIVE_EDGE_CLASSES
            and edge.source in adjacency
            and edge.target in adjacency
        ):
            adjacency[edge.source].append(edge.target)
    for targets in adjacency.values():
        targets.sort()
    return adjacency


def strongly_connected_components(excluded_nodes: Iterable[str] = ()) -> list[list[str]]:
    """Compute deterministic Tarjan SCCs on scientifically live dependencies."""

    graph = _active_adjacency(excluded_nodes)
    index = 0
    stack: list[str] = []
    on_stack: set[str] = set()
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    components: list[list[str]] = []

    def visit(vertex: str) -> None:
        nonlocal index
        indices[vertex] = lowlink[vertex] = index
        index += 1
        stack.append(vertex)
        on_stack.add(vertex)
        for target in graph[vertex]:
            if target not in indices:
                visit(target)
                lowlink[vertex] = min(lowlink[vertex], lowlink[target])
            elif target in on_stack:
                lowlink[vertex] = min(lowlink[vertex], indices[target])
        if lowlink[vertex] == indices[vertex]:
            component: list[str] = []
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == vertex:
                    break
            components.append(sorted(component))

    for vertex in sorted(graph):
        if vertex not in indices:
            visit(vertex)
    return sorted(components, key=lambda row: (row[0], len(row)))


def cyclic_components(excluded_nodes: Iterable[str] = ()) -> list[list[str]]:
    graph = _active_adjacency(excluded_nodes)
    return [
        component
        for component in strongly_connected_components(excluded_nodes)
        if len(component) > 1 or component[0] in graph[component[0]]
    ]


def feedback_vertex_sets(max_size: int = 3) -> list[list[str]]:
    """Return every minimum node cut that makes the live graph acyclic."""

    candidates = sorted(node.id for node in dependency_nodes())
    for size in range(max_size + 1):
        cuts = [list(combo) for combo in combinations(candidates, size) if not cyclic_components(combo)]
        if cuts:
            return cuts
    return []


def cycle_analysis() -> dict[str, Any]:
    components = strongly_connected_components()
    cycles = cyclic_components()
    cuts = feedback_vertex_sets()
    return {
        "active_edge_classes": sorted(ACTIVE_EDGE_CLASSES),
        "inactive_edge_classes": ["INVALIDATED", "REDUNDANT"],
        "strongly_connected_components": components,
        "cyclic_components": cycles,
        "cyclic_component_count": len(cycles),
        "cycle_exists": bool(cycles),
        "minimum_feedback_vertex_cardinality": len(cuts[0]) if cuts else None,
        "minimum_feedback_vertex_sets": cuts,
        "interpretation": (
            "the operative reset-charge-carrier chain is a true directed cycle; "
            "node cuts diagnose topology but do not themselves constitute physical laws"
        ),
    }


def recovery_ledger() -> list[dict[str, Any]]:
    """Record the decisive full-lineage recovery results."""

    return [
        {
            "route": "v6.10 action-selected junction functional",
            "provenance": "origin/bhsm-action-selected-junction-functional-v6-10-0",
            "result": "current action selects no self-adjoint junction domain; U(1) graph family remains",
            "edge_class": "INVALIDATED",
        },
        {
            "route": "historical boundary-action closure and cyclic monodromy",
            "provenance": "origin/bhsm-boundary-action-closure-candidate and origin/bhsm-primitive-cyclic-monodromy-boundary-action",
            "result": "structural candidates with unproved coefficients, primitive quotient, and physical channel identification",
            "edge_class": "HISTORICAL_HYPOTHESIS",
        },
        {
            "route": "v14.60-v14.61 global envelopment",
            "provenance": "global_envelopment_cap_selection_v14_60.py; full_global_envelopment_v14_61.py",
            "result": "executable synthetic theorem fixture; physical coefficients, operators, domain, incidence, and branch exhaustion remain open",
            "edge_class": "CONDITIONAL",
        },
        {
            "route": "v14.68-v14.69 incidence",
            "provenance": "global_attachment_incidence_curvature_v14_68.py; tensor_differential_incidence_v14_69.py",
            "result": "reduced scalar and common round tensor incidence are derived, but full physical tensor incidence and projectors are not",
            "edge_class": "CONDITIONAL",
        },
        {
            "route": "v15.0-v15.5 pregeometry and master closure",
            "provenance": "aether_reconstruction_v15_0.py through aether_master_closure_v15_5.py",
            "result": "typed reconstruction/actualization ontology exists; no emergence functor is selected, and generator, clock, carrier, and canonical data are unselected",
            "edge_class": "OWNER_SEMANTICS",
        },
        {
            "route": "stationary reset and charge adjudications",
            "provenance": "reset_correspondence_stationarity_adjudication.py; relative_diffeomorphism_generator_charge_adjudication.py",
            "result": "formal momentum balance exists memberwise, but F_B and L_s are not action variables and no common charge domain exists",
            "edge_class": "DERIVED",
        },
    ]


def targeted_recovery_matrix() -> list[dict[str, Any]]:
    """Map every priority archaeology concept to its decisive disposition."""

    groups = (
        (
            ["global envelopment", "trajectory target selection"],
            "v14.60-v14.61 synthetic KKT/envelopment fixtures",
            "CONDITIONAL_NOT_PHYSICAL",
        ),
        (
            ["encapsulation carrier", "T_core", "event basin"],
            "energetic-carrier adjudication and historical envelopment semantics",
            "OWNER_SEMANTICS_NO_SELECTION_LAW",
        ),
        (
            ["energy-geometry differential", "SPACETIME_EDGE"],
            "spacetime-edge ontology and boundary-energy history",
            "ONTOLOGY_OR_DIAGNOSTIC_NOT_AN_OPERATIVE_RESET_GENERATOR",
        ),
        (
            ["actualization", "Unique Actualization", "master reconstruction map", "pregeometry-to-geometry transition"],
            "v15.0-v15.5 pregeometry/master closure",
            "CG3_NO_EMERGENCE_FUNCTOR",
        ),
        (
            ["return map", "formation map", "persistence map", "reconstruction functor"],
            "N12 and v15 reconstruction lineages",
            "FINITE_OR_OWNER_SEMANTICS_NOT_A_FULL_FIELD_ACTION_MAP",
        ),
        (
            ["Cauchy reconstruction", "Noether reconstruction", "child reconstruction BVP"],
            "AE4 retarded and event-child BVP lineages",
            "CONDITIONAL_ON_UNSELECTED_DOMAIN_AND_PHYSICAL_BLOCKS",
        ),
        (
            ["boundary generating function", "Hamilton-Jacobi boundary functional", "principal function"],
            "v6.10 junction variation and current reset-stationarity adjudication",
            "HJ3_CIRCULAR_OR_ABSENT",
        ),
        (
            ["seam action", "interface action", "canonical relation", "Lagrangian correspondence", "normal section"],
            "junction/action-extension/reset-domain lineages",
            "OPTIONAL_OR_CONDITIONAL_NOT_ACTION_SELECTED",
        ),
        (
            ["first-positive return", "impedance/core crossing"],
            "historical AE4 envelopment ratio",
            "CHARGE_DEPENDENT_AND_UNEVALUABLE_AT_AE4R5",
        ),
        (
            ["event-to-child incidence"],
            "v14.68-v14.69 incidence plus v15.4 event algebra",
            "INC3_PARTIAL_ALGEBRA_OWNER_SEMANTICS_ONLY",
        ),
        (
            ["Calderon range", "DtN relation", "Wentzell relation", "boundary triple"],
            "v14.65-v14.69 and AE4 child-boundary lineages",
            "THEOREM_CLASS_OR_REDUCED_BLOCKS_PHYSICAL_DOMAIN_OPEN",
        ),
        (
            ["action extension"],
            "AE1-AE4 registered extensions",
            "SECTORWISE_EXTENSIONS_DO_NOT_ADD_F_B_L_s_OR_CARRIER_EMBEDDING_SLOT",
        ),
    )
    return [
        {"concept": concept, "provenance": provenance, "disposition": disposition}
        for concepts, provenance, disposition in groups
        for concept in concepts
    ]


def route_classifications() -> dict[str, Any]:
    return {
        "CA_to_GA": {
            "classification": CG_CLASS,
            "result": "typed/owner ontology only",
            "operative_map": None,
            "simultaneously_produces_required_data": False,
            "breaks_cycle": False,
        },
        "global_envelopment": {
            "classification": GE_CLASS,
            "result": "still synthetic/conditional",
            "physical_Euler_Lagrange_KKT_executable": False,
            "synthetic_coefficients_reused": False,
            "breaks_cycle": False,
        },
        "boundary_HJ": {
            "classification": HJ_CLASS,
            "result": "equivalent to the missing reset graph and therefore circular",
            "owned_principal_function": None,
            "new_seam_action_created": False,
            "breaks_cycle": False,
        },
        "event_child_incidence": {
            "classification": INC_CLASS,
            "result": "partial algebraic transport plus owner semantics; no full physical functor",
            "base_orientation_spin_bundle_transport_complete": False,
            "Cauchy_data_sufficient_for_moving_graph": False,
            "breaks_cycle": False,
        },
    }


def primitive_candidates() -> list[dict[str, Any]]:
    """Rank the allowed hypotheses by scientific sufficiency."""

    return [
        {
            "id": "P-A*",
            "rank": 1,
            "object": "action-owned covariant full-field interface generating functional varied also in its carrier embedding",
            "resolves": ["reset_graph", "nonfermion_Ls", "moving_variation", "energetic_carrier"],
            "remains_afterward": ["solve its EL/BVP system", "then test xi integrability, reference, spectra, and branch uniqueness"],
            "partially_present": "schematic deficit and sectorwise canonical pairs only; no functional or coefficients",
            "new_physics": True,
            "derivable_from_existing_authority": False,
            "cycle_breaking": True,
            "scientifically_sufficient": True,
        },
        {
            "id": "P-C",
            "rank": 2,
            "object": "action-owned C_A to G_A emergence/envelopment dynamics",
            "resolves": ["geometry", "carrier", "orientation", "scale", "incidence", "canonical_data", "reset_graph"],
            "remains_afterward": ["prove compatibility with the registered stratified action and charge domain"],
            "partially_present": "typed owner ontology and conditional reconstruction classes",
            "new_physics": True,
            "derivable_from_existing_authority": False,
            "cycle_breaking": True,
            "scientifically_sufficient": "HYPOTHETICALLY_BUT_OVERCOMPLETE_AND_UNCONSTRAINED",
        },
        {
            "id": "P-D",
            "rank": 3,
            "object": "environment-conditioned child-boundary Cauchy/Noether map",
            "resolves": ["conditional child BVP", "conditional flux transport"],
            "remains_afterward": ["carrier", "F_B polarization", "reference", "physical projectors"],
            "partially_present": "AE4 retarded domain and theorem-class Calderon/Wentzell blocks",
            "new_physics": True,
            "derivable_from_existing_authority": False,
            "cycle_breaking": False,
            "scientifically_sufficient": False,
        },
        {
            "id": "P-E",
            "rank": 4,
            "object": "action-owned event-to-child incidence/reconstruction functor",
            "resolves": ["base relation", "mode routing", "orientation/spin/bundle transport"],
            "remains_afterward": ["canonical polarization", "energetic carrier law", "reference", "generator"],
            "partially_present": "reduced v14.68 scalar and v14.69 round tensor incidence",
            "new_physics": True,
            "derivable_from_existing_authority": False,
            "cycle_breaking": False,
            "scientifically_sufficient": False,
        },
        {
            "id": "P-B",
            "rank": 5,
            "object": "action-owned physical encapsulation carrier Sigma_enc",
            "resolves": ["carrier locus", "orientation domain"],
            "remains_afterward": ["F_B", "L_s", "first variation", "incidence", "reference", "projectors"],
            "partially_present": "local sigma=0 material interface and historical T_core semantics",
            "new_physics": True,
            "derivable_from_existing_authority": False,
            "cycle_breaking": False,
            "scientifically_sufficient": False,
        },
        {
            "id": "P-F",
            "rank": 6,
            "object": None,
            "resolves": [],
            "remains_afterward": ["all cycle roots"],
            "partially_present": "no other qualifying object recovered",
            "new_physics": None,
            "derivable_from_existing_authority": False,
            "cycle_breaking": False,
            "scientifically_sufficient": False,
        },
    ]


def minimum_primitive_set() -> dict[str, Any]:
    return {
        "cardinality": 1,
        "set": ["P-A*"],
        "zero_primitive_set_sufficient": False,
        "one_object_sufficient": True,
        "why": (
            "one generating functional on the joint boundary-field and carrier-embedding configuration space "
            "can supply coupled stationarity equations for the carrier, F_B, L_s, and the first shape variation"
        ),
        "not_a_finite_parameter_count": True,
        "independence_statement": (
            "the existing action has no variation in F_B, L_s, or carrier embedding, so no current equation can select this functional"
        ),
    }


def constrained_primitive_form() -> dict[str, Any]:
    """Reduce P-A* to its narrowest allowed mathematical form without choosing it."""

    prior = interface_functional_deficit()
    return {
        "name": "P-A*",
        "value": None,
        "schematic_not_adopted": (
            "S_enc[F_B,L_s,iota_enc,X_e,X_c;E,sigma]="
            "integral_{Sigma_enc} mu_enc L_enc(j^r F_B,j^r iota_enc,Delta,Pi,A,corner,projectors;E,sigma)"
            "+T_top"
        ),
        "domain": (
            "Spin x G_SM equivariant admissible event/child trace fields, carrier embeddings iota_enc, "
            "orientation-preserving attachment maps F_B, nonfermion Lagrangian relations L_s, "
            "environment E, scale sigma, and compatible finite jets"
        ),
        "codomain": "R/(canonical exact boundary terms and 2*pi topological phase where applicable)",
        "covariance": prior["required_symmetries"],
        "units": prior["dimensional_structure"],
        "locality": prior["locality"],
        "canonical_structure": (
            "a scalar generating functional whose trace variations define a Lagrangian correspondence "
            "and whose embedding/F_B variations give momentum-Noether balance and graph selection"
        ),
        "environmental_dependence": "only through declared covariant boundary/environment data; no fitted observations",
        "scale_dependence": "must use an already-owned scale or explicitly expose any new dimensionful coefficient",
        "conservation_requirements": prior["conserved_constraints"],
        "topology_incidence_requirements": [
            "orientation and spin/bundle lift compatibility",
            "event-child incidence and projector intertwining",
            "holonomy/topological sectors invariant under allowed gauge equivalence",
        ],
        "allowable_nonlinear_order": (
            "unrestricted in field amplitudes subject to covariance and well-posedness; at least first F_B jet, "
            "and at most second geometric/embedding jets unless a higher-order action extension is independently owned"
        ),
        "minimum_derivative_order": prior["minimum_derivative_order"],
        "possible_higher_order": prior["possible_higher_order"],
        "free_functional_degrees": "ONE_REAL_INVARIANT_FUNCTIONAL_EQUIVALENCE_CLASS__INFINITE_DIMENSIONAL",
        "minimum_independent_choice_count": prior["minimum_independent_choice_count"],
        "existing_coefficients_that_are_fixed": prior["existing_normalizations_fix"],
        "unfixed_content": prior["existing_normalizations_do_not_fix"],
        "implemented": False,
        "tuned": False,
    }


def downstream_status() -> dict[str, Any]:
    return {
        "reset": "BLOCKED_AT_UNSELECTED_P-A*",
        "charge": "XI5_CHG4_REF5_MODEE5_ENVH5_DOMH4_AE4R5_UNCHANGED",
        "carrier": "RSP5_UNCHANGED_NO_PHYSICAL_CARRIER_SELECTED",
        "response_space": "BLOCKED_NO_ACTUAL_STABILIZER_OR_PHYSICAL_PROJECTORS",
        "S1": None,
        "S2": None,
        "S3": None,
        "S4": None,
        "full_field_action_attachment": None,
        "newly_unlocked_physical_objects": [],
        "N12_rank_added": 0,
        "N12_residual_before_time_quotient": 67,
        "N12_residual_after_time_quotient": 66,
    }


def owner_question() -> str:
    return (
        "What single covariant action-owned interface generating functional S_enc, if any, governs "
        "the carrier embedding, full-field event-to-child reset map F_B, and nonfermion boundary "
        "relation L_s, so that its first variation selects all three without fitted data?"
    )


def claim_boundary() -> dict[str, bool]:
    return {
        "NEW_INTERFACE_FUNCTIONAL_INVENTED": False,
        "PHYSICAL_RESET_SELECTED": False,
        "COMMON_CHARGE_DEFINED": False,
        "ENERGETIC_CARRIER_SELECTED": False,
        "NEW_N12_EQUATION_COUNTED": False,
        "FROZEN_PREDICTIONS_CHANGED": False,
        "GATE7_PROMOTED": False,
        "FULL_BHSM_COMPLETE": False,
    }


def adjudication_payload() -> dict[str, Any]:
    nodes = dependency_nodes()
    edges = dependency_edges()
    return {
        "action_version": ACTION_VERSION,
        "classification": CLASSIFICATION,
        "graph": {
            "edge_direction": "PREREQUISITE_TO_DEPENDENT",
            "nodes": [asdict(node) for node in nodes],
            "edges": [asdict(edge) for edge in edges],
            "allowed_edge_classes": sorted(EDGE_CLASSES),
        },
        "cycle_analysis": cycle_analysis(),
        "minimum_primitive_set": minimum_primitive_set(),
        "candidate_primitives": primitive_candidates(),
        "recovery": recovery_ledger(),
        "targeted_recovery_matrix": targeted_recovery_matrix(),
        "route_classifications": route_classifications(),
        "loop_verdict": LOOP_CLASS,
        "primitive_constraint": constrained_primitive_form(),
        "downstream": downstream_status(),
        "exact_next_object": EXACT_NEXT_OBJECT,
        "owner_question_for_handoff_only": owner_question(),
        "claim_boundary": claim_boundary(),
    }


__all__ = [
    "ACTION_VERSION", "ACTIVE_EDGE_CLASSES", "CG_CLASS", "CLASSIFICATION",
    "EDGE_CLASSES", "EXACT_NEXT_OBJECT", "GE_CLASS", "HJ_CLASS", "INC_CLASS",
    "LOOP_CLASS", "adjudication_payload", "claim_boundary", "constrained_primitive_form",
    "cycle_analysis", "cyclic_components", "dependency_edges", "dependency_nodes",
    "downstream_status", "feedback_vertex_sets", "minimum_primitive_set",
    "owner_question", "primitive_candidates", "recovery_ledger", "route_classifications",
    "targeted_recovery_matrix",
    "strongly_connected_components",
]
