import hashlib
import json

from bhsm.interface.reset_charge_carrier_dependency_cycle_adjudication import (
    CG_CLASS,
    EDGE_CLASSES,
    EXACT_NEXT_OBJECT,
    GE_CLASS,
    HJ_CLASS,
    INC_CLASS,
    LOOP_CLASS,
    claim_boundary,
    constrained_primitive_form,
    cycle_analysis,
    cyclic_components,
    dependency_edges,
    dependency_nodes,
    downstream_status,
    feedback_vertex_sets,
    minimum_primitive_set,
    owner_question,
    primitive_candidates,
    recovery_ledger,
    route_classifications,
    targeted_recovery_matrix,
)
from scripts.materialize_reset_charge_carrier_dependency_cycle_adjudication import (
    TARGET,
    build_payload,
    deterministic_json,
    main,
)


def test_required_dependency_graph_is_complete_and_every_edge_is_typed():
    nodes = dependency_nodes()
    edges = dependency_edges()
    ids = {node.id for node in nodes}
    required = {
        "reset_graph", "nonfermion_Ls", "moving_variation", "tangent_domain", "theta",
        "generator_xi", "hamiltonian", "reference", "event_mode_charge",
        "available_charge", "child_seam_charge", "envelopment_increment", "rho_hold",
        "energetic_carrier", "actual_stabilizer", "physical_projectors",
        "event_child_incidence", "active_response", "reduced_reset", "beta", "graph_jets",
        "S1", "S2", "S3", "S4", "full_attachment",
    }
    assert required <= ids
    assert len(ids) == len(nodes)
    assert all(edge.source in ids and edge.target in ids for edge in edges)
    assert all(edge.classification in EDGE_CLASSES for edge in edges)
    assert {edge.classification for edge in edges} == EDGE_CLASSES


def test_tarjan_computes_one_true_reset_charge_carrier_scc():
    result = cycle_analysis()
    cycles = cyclic_components()
    assert result["cycle_exists"]
    assert result["cyclic_component_count"] == 1
    assert len(cycles) == 1
    active = set(cycles[0])
    assert len(active) == 25
    assert {
        "reset_graph", "moving_variation", "tangent_domain", "theta", "generator_xi",
        "hamiltonian", "event_mode_charge", "available_charge", "rho_hold",
        "energetic_carrier", "event_child_incidence", "physical_projectors",
        "boundary_HJ", "global_envelopment", "full_attachment",
    } <= active


def test_minimum_feedback_vertex_cut_is_computed_not_described():
    cuts = feedback_vertex_sets()
    assert cuts
    assert len(cuts[0]) == 2
    assert all(len(cut) == 2 for cut in cuts)
    assert all("reset_graph" in cut for cut in cuts)
    assert any(set(cut) == {"reset_graph", "energetic_carrier"} for cut in cuts)
    assert cyclic_components(cuts[0]) == []
    assert cyclic_components([])


def test_one_coupled_functional_is_one_physical_primitive_not_one_node_cut():
    result = minimum_primitive_set()
    candidate = primitive_candidates()[0]
    assert result["cardinality"] == 1
    assert result["set"] == ["P-A*"]
    assert not result["zero_primitive_set_sufficient"]
    assert result["one_object_sufficient"]
    assert candidate["id"] == "P-A*"
    assert candidate["rank"] == 1
    assert candidate["cycle_breaking"]
    assert candidate["scientifically_sufficient"] is True
    assert {"reset_graph", "nonfermion_Ls", "moving_variation", "energetic_carrier"} <= set(candidate["resolves"])
    assert all(not row["cycle_breaking"] for row in primitive_candidates()[2:])


def test_deep_owner_routes_are_classified_without_promotion():
    routes = route_classifications()
    assert routes["CA_to_GA"]["classification"] == CG_CLASS == "CG3"
    assert routes["CA_to_GA"]["operative_map"] is None
    assert routes["global_envelopment"]["classification"] == GE_CLASS == "GE3"
    assert not routes["global_envelopment"]["synthetic_coefficients_reused"]
    assert routes["boundary_HJ"]["classification"] == HJ_CLASS == "HJ3"
    assert routes["boundary_HJ"]["owned_principal_function"] is None
    assert routes["event_child_incidence"]["classification"] == INC_CLASS == "INC3"
    assert not routes["event_child_incidence"]["Cauchy_data_sufficient_for_moving_graph"]
    assert all(not row["breaks_cycle"] for row in routes.values())


def test_recovery_ledger_covers_decisive_lineage_and_distinguishes_statuses():
    rows = recovery_ledger()
    assert len(rows) == 6
    assert {row["edge_class"] for row in rows} == {
        "INVALIDATED", "HISTORICAL_HYPOTHESIS", "CONDITIONAL", "OWNER_SEMANTICS", "DERIVED"
    }
    text = " ".join(row["result"] for row in rows)
    assert "selects no self-adjoint junction domain" in text
    assert "synthetic theorem fixture" in text
    assert "no emergence functor" in text
    assert "full physical tensor incidence" in text


def test_targeted_archaeology_matrix_covers_every_requested_priority_concept():
    recovered = {row["concept"] for row in targeted_recovery_matrix()}
    requested = {
        "global envelopment", "trajectory target selection", "encapsulation carrier", "T_core",
        "energy-geometry differential", "SPACETIME_EDGE", "actualization", "Unique Actualization",
        "master reconstruction map", "event basin", "return map", "reconstruction functor",
        "Cauchy reconstruction", "Noether reconstruction", "boundary generating function",
        "Hamilton-Jacobi boundary functional", "principal function", "seam action", "interface action",
        "canonical relation", "Lagrangian correspondence", "normal section", "first-positive return",
        "impedance/core crossing", "event-to-child incidence", "formation map", "persistence map",
        "child reconstruction BVP", "Calderon range", "DtN relation", "Wentzell relation",
        "boundary triple", "action extension", "pregeometry-to-geometry transition",
    }
    assert recovered == requested
    assert all(row["provenance"] and row["disposition"] for row in targeted_recovery_matrix())


def test_LOOP3_primitive_is_constrained_but_not_invented():
    primitive = constrained_primitive_form()
    assert LOOP_CLASS == "LOOP3"
    assert primitive["value"] is None
    assert primitive["minimum_independent_choice_count"] == 1
    assert primitive["free_functional_degrees"] == (
        "ONE_REAL_INVARIANT_FUNCTIONAL_EQUIVALENCE_CLASS__INFINITE_DIMENSIONAL"
    )
    assert "Spin x G_SM" in primitive["domain"]
    assert "R/(canonical exact boundary terms" in primitive["codomain"]
    assert "first F_B jet" in primitive["allowable_nonlinear_order"]
    assert not primitive["implemented"]
    assert not primitive["tuned"]


def test_downstream_N12_and_claim_firewalls_remain_closed():
    status = downstream_status()
    claims = claim_boundary()
    assert status["newly_unlocked_physical_objects"] == []
    assert status["N12_rank_added"] == 0
    assert status["N12_residual_before_time_quotient"] == 67
    assert status["N12_residual_after_time_quotient"] == 66
    assert status["S1"] is status["S2"] is status["S3"] is status["S4"] is None
    assert status["full_field_action_attachment"] is None
    assert not any(claims.values())


def test_exact_next_object_and_single_handoff_question_are_narrow():
    question = owner_question()
    assert EXACT_NEXT_OBJECT.startswith("OWNER_SELECTION_OF_ONE_ACTION_OWNED")
    assert question.count("?") == 1
    assert "carrier embedding" in question
    assert "F_B" in question
    assert "L_s" in question
    assert "fitted data" in question


def test_materializer_is_valid_and_byte_deterministic():
    first_payload = build_payload()
    second_payload = build_payload()
    assert first_payload["validation_passed"]
    assert all(first_payload["validation"].values())
    assert deterministic_json(first_payload) == deterministic_json(second_payload)
    main()
    first_hash = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second_hash = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first_hash == second_hash
    stored = json.loads(TARGET.read_text(encoding="utf-8"))
    assert stored["validation_passed"]
    assert stored["adjudication"]["loop_verdict"] == "LOOP3"
