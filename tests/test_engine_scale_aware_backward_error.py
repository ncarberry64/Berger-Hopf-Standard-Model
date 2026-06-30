from bhsm.interface.engine_invariants import build_engine_invariant_report


def test_scale_aware_errors_remain_inside_declared_gate():
    report = build_engine_invariant_report()
    tolerance = report["metrics"]["tolerance"]
    assert report["metrics"]["max_roundtrip_scale_aware_error"] <= tolerance
    assert report["metrics"]["max_lorentz_relative_backward_error"] <= tolerance

