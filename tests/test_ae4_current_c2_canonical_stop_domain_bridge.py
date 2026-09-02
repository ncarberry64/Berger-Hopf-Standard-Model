import hashlib

from bhsm.interface.ae4_current_c2_canonical_stop_domain_bridge import (
    canonical_stop_domain_bridge,
)
from scripts.materialize_ae4_current_c2_canonical_stop_domain_bridge import (
    TARGET,
    build_payload,
    main,
)


def test_canonical_stop_bridge_is_fail_closed_if_any_owner_is_missing():
    arguments = {
        "exact_stop_certified": True,
        "stop_transverse": True,
        "first_hit_interval_certified": True,
        "open_stop_stratum_derived": True,
        "endpoint_domain_owned": True,
        "canonical_stop_uses_friedrichs": True,
    }
    assert canonical_stop_domain_bridge(**arguments)[
        "canonical_stop_branch_available"
    ]
    arguments["stop_transverse"] = False
    result = canonical_stop_domain_bridge(**arguments)
    assert not result["canonical_stop_branch_available"]
    assert result["terminal_domain"] == "OPEN"
    assert result["independent_finite_terminal_load_required"] is None


def test_existing_stop_selects_friedrichs_without_erasing_endpoint_motion():
    payload = build_payload()
    result = payload["scientific_result"]
    boundary = payload["claim_boundary"]
    assert payload["validation_passed"]
    assert result["stop_reaching_reset_stratum"] == "NONEMPTY_OPEN_72_DIMENSIONAL"
    assert result["finite_terminal_load_and_its_HS_jets_needed_on_stop_branch"] is False
    assert result["moving_stop_and_bulk_HS_variations_still_needed"] is True
    assert result["event_branch_child_Weyl_family_status"] == "OPEN_UNCHANGED"
    assert boundary["AE4_CURRENT_C2_CANONICAL_STOP_FRIEDRICHS_ENDPOINT_SELECTED"]
    assert not boundary["AE4_CURRENT_C2_STOP_MATCHED_OPERATOR_PATH_EVALUATED"]


def test_materialized_canonical_stop_domain_bridge_is_deterministic():
    main()
    first = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    main()
    second = hashlib.sha256(TARGET.read_bytes()).hexdigest()
    assert first == second
