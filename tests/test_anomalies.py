from anomalies import anomalies_cancel, anomaly_residuals, anomaly_screen


def test_one_generation_anomalies_cancel_exactly():
    residuals = anomaly_residuals()

    assert residuals == {
        "SU3_SU3_U1": 0,
        "SU2_SU2_U1": 0,
        "gravity_gravity_U1": 0,
        "U1_U1_U1": 0,
    }
    assert anomalies_cancel()


def test_anomaly_screen_is_derived_and_auditable():
    screen = anomaly_screen()

    assert screen.status == "derived"
    assert all(value == "0" for value in screen.outputs.values())
    assert screen.assumptions

