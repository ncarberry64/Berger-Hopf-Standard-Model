import hashlib

from scripts.materialize_ae4_current_c2_terminal_hs_jet_transport import (
    TARGET,
    build_payload,
    main,
)


def test_full_current_c2_terminal_hs_jet_transport_is_fail_closed():
    payload = build_payload()
    boundary = payload["claim_boundary"]
    rows = payload["negative_axis_terminal_HS_jet_transport_rows"]
    assert payload["validation_passed"]
    assert boundary["AE4_CURRENT_C2_TERMINAL_HS_JET_TRANSPORT_LAW_DERIVED"]
    assert not boundary["AE4_CURRENT_C2_TERMINAL_HS_JETS_DERIVED"]
    assert not boundary[
        "AE4_CURRENT_C2_MAXIMAL_HISTORY_RETARDED_HS_CALDERON_BLOCK_DERIVED"
    ]
    assert all(
        abs(row["terminal_first_jet_sensitivity_s"]) > 0.99
        for channel in rows.values()
        for row in channel.values()
    )
    assert not payload["scientific_result"][
        "existing_covariant_geometry_jet_bounds_reclassified_as_HS_jets"
    ]


def test_materialized_terminal_hs_jet_transport_is_deterministic():
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
