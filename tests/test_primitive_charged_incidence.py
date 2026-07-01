from bhsm.interface.primitive_charged_incidence import build_primitive_charged_incidence_report


def test_exact_primitive_incidence_spine():
    report = build_primitive_charged_incidence_report()
    assert report["omega_trace"]["omega_ch"] == [3, 6, 12]
    assert report["omega_trace"]["total_incidence_trace"] == 21
    assert report["rho_gcd"]["rho_ch"] == 3
    assert report["rho_gcd"]["primitive_incidence"] == [1, 2, 4]
    assert report["official_predictions_modified"] is False
    assert report["frozen_predictions_modified"] is False

