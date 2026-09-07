import hashlib

from scripts.materialize_ae4_current_c2_green_image_partition_reconciliation import (
    DATA,
    TARGET,
    build_payload,
    main,
)


def test_current_center_recovers_bhsm_native_green_image_partition():
    payload = build_payload()
    assert payload["validation_passed"]
    assert payload["authority_reconciliation"]["partition_is_BHSM_native"]
    assert not payload["historical_recovery"][
        "historical_numerical_values_current_authority"
    ]
    assert payload["current_center_instantiation"]["nonzero_post_reset_nodes"] == 370
    assert payload["coarse_obstruction_localization"][
        "absolute_longitudinal_projection_upper"
    ] < 0.002
    assert payload["coarse_obstruction_localization"][
        "transverse_projection_lower"
    ] > 0.99
    assert not payload["authority_reconciliation"][
        "green_image_anisotropic_route_obstructed"
    ]


def test_green_partition_artifact_is_deterministic():
    main()
    first = (hashlib.sha256(TARGET.read_bytes()).hexdigest(), hashlib.sha256(DATA.read_bytes()).hexdigest())
    main()
    second = (hashlib.sha256(TARGET.read_bytes()).hexdigest(), hashlib.sha256(DATA.read_bytes()).hexdigest())
    assert first == second
