import importlib.util
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import pytest
from flint import ctx

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('stored_assembly_certificate',
    ROOT/'scripts/certify_n12_gate7_stored_pullback_assembly.py')
certificate=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(certificate)


def test_covariance_reproduction_rejects_one_bit_difference():
    expected=np.ones((3,2,2))
    certificate._verify_covariance(expected.copy(),expected,'local')
    actual=expected.copy()
    actual[0,0,0]=np.nextafter(actual[0,0,0],np.inf)
    with pytest.raises(RuntimeError,match='differs'):
        certificate._verify_covariance(actual,expected,'local')


def test_algorithm_difference_is_added_to_analytic_rounding_bound():
    previous=ctx.prec
    ctx.prec=512
    try:
        a=np.array([.1,.3])
        b=np.array([.125,.25])
        result=certificate._stored_error(a,b,dict(assembly_error_frobenius_upper=.125))
        difference=result['algorithm_difference_frobenius_upper']
        assert F(result['stored_assembly_error_frobenius_upper'])>=F(difference)+F(.125)
    finally:
        ctx.prec=previous
