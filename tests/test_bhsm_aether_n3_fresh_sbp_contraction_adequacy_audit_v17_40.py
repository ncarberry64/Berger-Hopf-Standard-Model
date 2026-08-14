from bhsm.interface.aether_n3_fresh_sbp_contraction_adequacy_audit_v17_40 import (
    completion_payload,
    contraction_adequacy_audit,
)


def test_contraction_chain_strictly_descends():
    assert contraction_adequacy_audit()[
        "all_six_metrics_strictly_decrease_at_every_pass"
    ]


def test_contraction_adequacy_audit_validates():
    assert completion_payload()["validation_passed"]
