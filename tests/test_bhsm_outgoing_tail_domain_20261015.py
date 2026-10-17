from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"audits"))
import numpy as np
from bhsm_baton_zoo_outgoing_tail_domain_20261015 import affine_outgoing_graph_energy_rhs


def test_noncommuting_complex_energy_product_rule_controls():
    rng=np.random.default_rng(20261015)
    def sample(shape):return (rng.normal(size=shape)+1j*rng.normal(size=shape))/4
    Q=[sample((4,4))for _ in range(3)];R=[sample((2,2))for _ in range(3)]
    f=[sample((4,3))for _ in range(3)];r=[sample((2,3))for _ in range(3)]
    dR,dr=affine_outgoing_graph_energy_rhs(Q,R,f,r)
    def fresh(e):
        q,g,b,a=[x[0]+e*x[1]+e*e*x[2]/2 for x in(Q,R,f,r)]
        A,B,C,D=q[:2,:2],q[:2,2:],q[2:,:2],q[2:,2:]
        return C+D@g-g@A-g@B@g,(D-g@B)@a+b[2:]-g@b[:2]
    errors=[]
    for h in(.02,.01,.005):
        plus,minus=fresh(h),fresh(-h)
        error=max(np.max(abs((plus[j]-minus[j])/(2*h)-[dR,dr][j][1]))for j in range(2))
        errors.append(error)
        second=max(np.max(abs((plus[j]-2*fresh(0)[j]+minus[j])/h**2-[dR,dr][j][2]))for j in range(2))
        assert second < 2*h*h
    assert errors[1]<errors[0]/3.9 and errors[2]<errors[1]/3.9


def test_missing_jet_is_rejected_instead_of_zeroed():
    import pytest
    with pytest.raises(ValueError):
        affine_outgoing_graph_energy_rhs([np.eye(4)],[np.eye(2)], [np.ones((4,1))], [np.ones((2,1))])
