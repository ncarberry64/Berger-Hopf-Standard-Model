from bhsm.interface.science_hardening import falsification_table


def test_every_claim_has_a_real_falsifier_and_track():
    rows = falsification_table()["rows"]
    assert len(rows) >= 19
    assert {row["track"] for row in rows} == {"ENGINE", "PHYSICS"}
    assert all(row["what_would_falsify_it"] for row in rows)

