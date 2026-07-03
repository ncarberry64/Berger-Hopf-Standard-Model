from bhsm.interface.gauge_coframe_hodge.gauge_coframe_basis import audit_gauge_coframe_basis
def test_raw_and_orthonormal_are_distinct(): assert audit_gauge_coframe_basis()["status"]=="OPEN_MISSING_GAUGE_COFRAME_BASIS"
