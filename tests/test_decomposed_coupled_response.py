"""Check the decomposition against explicit perturbed coupled matrices."""
from itertools import product
import numpy as np
import pytest
from flint import arb,arb_mat,ctx
from bhsm.interface.decomposed_coupled_response import CoupledDefectBound


def test_actual_coupled_matrices_and_solutions_are_enclosed():
    previous=ctx.prec;ctx.prec=256
    try:
        # H0-lambda0*I=diag(0,2), p0=(1,0); R is the exact inverse of J0.
        J0=arb_mat([[0,0,-1],[0,2,0],[1,0,0]])
        R0=J0.inv();R=np.array(R0.entries(),dtype=object).reshape(3,3)
        r=np.array([arb(1)/128,arb(1)/64,arb(1)/256])
        # A state-dependent Hessian increment with entries bounded by 1/256.
        S=np.array([arb(0),(r[0]+r[1])/512,(r[0]+r[1])/256])
        bound=CoupledDefectBound(np.full((3,3),arb(0)),R,r,S)
        w=np.array([arb(1)/8,arb(2),arb(1)/16]);V=bound.apply(w)
        e=np.array([arb(1)/8,-arb(1)/4,arb(1)/16]);z=np.array([arb(1)/2,arb(0),-arb(1)/4])
        box,proof=bound.enclose(z,e)
        for signs in product((-1,1),repeat=3):
            dp=np.array([signs[0]*r[0],signs[1]*r[1]]);dl=signs[2]*r[2]
            for s in (-1,1):
                J=arb_mat(J0.tolist())
                for i,j in product(range(2),repeat=2):J[i,j]+=s*arb(1)/256-(dl if i==j else 0)
                for i in range(2):J[i,2]-=dp[i];J[2,i]+=dp[i]
                D=arb_mat([[1,0,0],[0,1,0],[0,0,1]])-R0*J
                direct=[sum((abs(D[i,j]).upper()*w[j] for j in range(3)),arb(0)).upper() for i in range(3)]
                assert all(a<=b for a,b in zip(direct,V))
                # error=R*b+(I-RJ)*error, with R*b represented by e.
                error=(R0*J).solve(arb_mat(3,1,list(e)))
                assert all(box[i].contains(z[i]+error[i,0]) for i in range(3))
        assert proof['physical_domain_radii_changed'] is False
    finally:ctx.prec=previous


def test_unproved_decomposition_rejects_noncontraction():
    bound=CoupledDefectBound([[arb(1),arb(0)],[arb(0),arb(1)]],
        [[arb(1),arb(0)],[arb(0),arb(1)]],[arb(1),arb(1)],[arb(0),arb(0)])
    with pytest.raises(ArithmeticError,match='strict decomposed'):
        bound.enclose([arb(0),arb(0)],[arb(1),arb(1)])
