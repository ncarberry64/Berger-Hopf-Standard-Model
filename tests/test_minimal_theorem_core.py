from bhsm.interface.science_hardening import minimal_theorem_core


def test_minimal_core_has_explicit_noninflated_statuses():
    report = minimal_theorem_core()
    assert report["full_completion_claimed"] is False
    assert len(report["core_items"]) >= 13
    statuses = {row["name"]: row["status"] for row in report["core_items"]}
    assert statuses["Charged Omega_f operators"] == "STRUCTURALLY_INTEGRATED_NOT_ACTION_DERIVED"
    assert statuses["CKM exponent"] == "OPEN_MISSING_ACTION_DERIVATION"

