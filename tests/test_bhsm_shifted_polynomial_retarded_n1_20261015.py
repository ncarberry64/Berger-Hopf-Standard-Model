from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"audits"))
"""Small independent algebra checks; no physical BHSM preparation is chosen."""
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import pytest
from flint import acb,acb_mat,arb,ctx


p=Path(__file__).resolve().parents[1]/"audits"/"bhsm_muon_shifted_polynomial_retarded_n1_20261015.py"
spec=spec_from_file_location('shifted_polynomial_consumer',p);m=module_from_spec(spec);spec.loader.exec_module(m)


@pytest.fixture(autouse=True)
def precision():
    old=ctx.prec;ctx.prec=256
    yield
    ctx.prec=old


def scalar(x):return acb_mat([[acb(x)]])


def complex_scalar(real,imag):return acb_mat([[acb(arb(real),arb(imag))]])


def reference_augmented(A,B0,B1,q,z0,h,u=acb(1)):
    """Independent small augmented matrix exponential for a quadratic Q(u)."""
    a,b,c=[x[0,0]for x in q]
    F0=h*B0[0,0]*a+B1[0,0]*b
    F1=h*B0[0,0]*b+2*B1[0,0]*c
    F2=h*B0[0,0]*c
    G=acb_mat([[h*A[0,0],F0,F1,F2],[0,0,0,0],[0,1,0,0],[0,0,2,0]])
    initial=acb_mat([[z0[0,0]],[1],[0],[0]])
    return ((u*G).exp()*initial)[0,0]


def tiny_difference(a,b):assert abs(a-b).upper()<arb('1e-45')


def test_exact_Qdot_shift_retains_nonzero_initial_source_contact():
    A=scalar(0);B0=scalar(3);B1=complex_scalar('.7','-.2')
    q=[scalar(2),scalar(-1),scalar(4)];z0=complex_scalar('.3','.1');h=acb(arb('.02'))
    piece=m.shifted_polynomial_step(A,B0,B1,q,z0,h)
    exact=z0[0,0]+h*B0[0,0]*(2-acb(1)/2+acb(4)/3)+B1[0,0]*3
    tiny_difference(piece['z_end'][0,0],exact)
    tiny_difference(m.polynomial_state(piece,acb(0))['z'][0,0],z0[0,0])
    assert abs(piece['coefficients'][0][0,0]-z0[0,0]).lower()>arb('.1')


def test_complex_nonzero_flow_agrees_with_independent_exponential_and_derivatives():
    A=complex_scalar('.02','-.01');B0=complex_scalar('-.4','.1');B1=complex_scalar('.7','.2')
    q=[scalar(2),scalar(-1),scalar(4)];z0=complex_scalar('.3','.1');h=acb(arb('.02'))
    piece=m.shifted_polynomial_step(A,B0,B1,q,z0,h)
    for u in (acb(0),acb(arb('.4')),acb(1)):
        actual=m.polynomial_state(piece,u);reference=reference_augmented(A,B0,B1,q,z0,h,u)
        tiny_difference(actual['z'][0,0],reference)
        Q=q[0][0,0]+q[1][0,0]*u+q[2][0,0]*u*u
        Qt=(q[1][0,0]+2*q[2][0,0]*u)/h
        exact_rate=A[0,0]*reference+B0[0,0]*Q+B1[0,0]*Qt
        assert abs(actual['zt'][0,0]-exact_rate).upper()<arb('1e-40')
    assert piece['tail']<=arb('1e-50')
    assert piece['order']>2


def test_coefficient_corner_carries_z_and_changes_shifted_w_exactly():
    A=complex_scalar('.02','-.01');B0=scalar(3);B1=complex_scalar('.7','-.2')
    q=[scalar(2),scalar(-1),scalar(4)];z0=complex_scalar('.3','.1');h=acb(arb('.02'))
    first=m.shifted_polynomial_step(A,B0,B1,q,z0,h)
    Qcorner=q[0]+q[1]+q[2]
    nextB1=complex_scalar('-.9','.3');qnext=[Qcorner,scalar(2),scalar(-3)]
    second=m.shifted_polynomial_step(-A,2*B0,nextB1,qnext,first['z_end'],h)
    before=m.polynomial_state(first,acb(1))['z'];after=m.polynomial_state(second,acb(0))['z']
    tiny_difference(before[0,0],after[0,0])
    wbefore=m.horner(first['coefficients'],acb(1))
    expected_shift=wbefore+(B1-nextB1)*Qcorner
    tiny_difference(second['coefficients'][0][0,0],expected_shift[0,0])
    reference=reference_augmented(-A,2*B0,nextB1,qnext,first['z_end'],h)
    tiny_difference(second['z_end'][0,0],reference)
