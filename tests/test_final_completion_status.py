from bhsm.interface.common_16 import build_final_completion_report


def test_final_completion_status_fails_closed() -> None:
    report = build_final_completion_report()
    assert report.status_after == "CONDITIONAL_COMMON_16_GENERATOR_CANDIDATE_CKM_EXPONENT_OPEN"
    assert report.completion_claimed is False
    assert report.provenance.ckm_exponent_final_status == "OPEN_MISSING_CKM_EXPONENT_DERIVATION"
