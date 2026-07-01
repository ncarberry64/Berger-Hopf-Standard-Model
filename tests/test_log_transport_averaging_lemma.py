from fractions import Fraction

from bhsm.interface.action_lemmas import (
    energy_excess_identity,
    log_transport_minimizer,
    prove_log_transport_averaging,
    quadratic_log_energy,
)


def test_abstract_minimizer_is_exactly_one_over_n():
    minimizer = log_transport_minimizer(Fraction(1), 16)
    assert minimizer == (Fraction(1, 16),) * 16
    assert quadratic_log_energy(minimizer) == Fraction(1, 16)
    report = prove_log_transport_averaging(16)
    assert report["status"] == "ARTIFACT_BACKED_MATHEMATICAL_LEMMA"
    assert report["minimizer_per_channel"] == "1/16"


def test_sum_of_squares_energy_excess_is_nonnegative():
    values = (Fraction(0), Fraction(1, 2), Fraction(1, 2))
    assert energy_excess_identity(values) > 0

