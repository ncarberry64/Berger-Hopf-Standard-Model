from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'audits'))
from flint import arb
from bhsm_baton_zoo_photon_quotient_compatibility import functional_error_bound


def test_equation_certificate_propagates_nonzero_functional():
    # A=2I, G=(1,0), U=(1,0), residual=(.02,.04), coercivity=2.
    # The exact functional may move by at most sqrt(.02^2+.04^2)/2.
    bound=functional_error_bound(arb(1),[.02,.04],arb(2))
    assert bound > arb(.02236) and bound < arb(.02237)
    assert arb(1)-bound > 0


def test_uncertain_or_unconditioned_case_is_not_certified():
    import pytest
    assert not arb(1)-functional_error_bound(arb(1),[4.],arb(2)) > 0
    with pytest.raises(ValueError):
        functional_error_bound(arb(1),[0.],arb(0))
