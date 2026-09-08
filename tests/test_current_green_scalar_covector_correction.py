"""Independent rectangular/full comparison for a small polynomial action."""
import importlib
import itertools
import sys
from pathlib import Path

import numpy as np
import pytest
import sympy as sp

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
repair=importlib.import_module('derive_n12_gate7_current_green_scalar_covector_correction')
mixed=importlib.import_module('derive_n12_gate7_current_green_supplemental_mixed_rate')

@pytest.mark.parametrize('weights', [np.array([2.,1.,3.]),np.array([1.,1.,1.])])
def test_adjoint_correction_matches_independent_rectangular_hessian(monkeypatch,weights):
    c=repair.c
    x=sp.symbols('q v m')
    action=(x[0]**2+2*x[1]**2+5*x[2]**2+x[0]*x[1]/5
            +x[0]*x[1]*x[2]/7+x[1]**3/11+x[1]**2*x[2]**2/13+x[0]**2*x[2]**3/17)
    state=np.array([.12,.21,-.08])
    derivatives={}
    for order in range(1,6):
        expressions=[sp.diff(action,*[x[i] for i in indices]) for indices in itertools.product(range(3),repeat=order)]
        derivatives[order]=np.asarray(sp.lambdify(x,expressions,'numpy')(*state),float).reshape((3,)*order)
    def signed(_state,*directions):
        tensor=derivatives[len(directions)]
        output=[];operands=[tensor,list(range(len(directions)))];extra=10
        for index,direction in enumerate(directions):
            value=np.asarray(direction)/weights if np.ndim(direction)==1 else np.asarray(direction)/weights[:,None]
            indices=[index]
            if value.ndim==2:
                indices.append(extra);output.append(extra);extra+=1
            operands.extend((value,indices))
        return np.einsum(*operands,output)
    for name,value in dict(QDIM=1,REDUCED=2,STATE=3,OUTPUTS=4,COORDINATES=3,TRANSVERSE=2,SELECTED=0).items():
        monkeypatch.setattr(c,name,value)
    monkeypatch.setattr(c,'metric_data',lambda:(weights[:1],weights[1:],None,None))
    monkeypatch.setattr(c,'_exact_jet',lambda _:(derivatives[1],derivatives[2]))
    monkeypatch.setattr(c,'_signed',signed)
    basis=np.array([[1.,0.],[0.,1.],[0.,0.]])
    frame=np.array([[.2,.7,0.],[.8,-.1,0.],[-.3,.4,0.],[.05,-.04,1.]])
    monkeypatch.setattr(c,'null_space',lambda _:basis)
    monkeypatch.setattr(c,'_frame',lambda _:frame)
    _,vectors=np.linalg.eigh(derivatives[2][1:,1:]);reference=vectors[:,0].copy()
    directions=frame@basis;descriptor=.31
    full=c._quadratic_row('midpoint',0,state,descriptor,weights,reference,None,np.array([0.,0.,1.]),np.zeros(3),0.,True)['quadratic_tensor']
    rectangular=np.stack([mixed.mixed_rate_map(state,descriptor,weights,reference,directions[:,i],directions)[0] for i in range(2)],axis=1)
    correction=repair.correction(state,descriptor,weights,reference,directions)
    np.testing.assert_allclose(full[:-1],rectangular[:-1],rtol=2e-11,atol=2e-11)
    np.testing.assert_allclose(full[-1]+correction,rectangular[-1],rtol=2e-11,atol=2e-11)
    if np.array_equal(weights,np.ones(3)):
        assert np.array_equal(correction,np.zeros((2,2)))
    else:
        assert np.linalg.norm(full[-1]-rectangular[-1])>1e-5

def test_missing_correction_cannot_be_consumed(monkeypatch,tmp_path):
    monkeypatch.setattr(repair,'WORK',tmp_path)
    with pytest.raises(RuntimeError,match='Current scalar covector correction required'):
        repair.corrected_tensor('midpoint',0)

def test_addition_rounding_keeps_small_lost_correction():
    certificate=importlib.import_module('certify_n12_gate7_current_green_scalar_covector_correction')
    raw=np.array([1.]);delta=np.array([2.**-54]);stored=raw+delta
    assert certificate.addition_error(raw,delta,stored)>=2.**-54
    assert certificate.addition_error(raw,np.zeros(1),raw)==0.
    with pytest.raises(ValueError,match='identical'):
        certificate.addition_error(raw,np.zeros(2),raw)

def test_unverified_correction_certificate_cannot_enable_composition():
    certificate=importlib.import_module('certify_n12_gate7_current_green_scalar_covector_correction')
    with pytest.raises(RuntimeError,match='Complete current'):
        certificate.validate_for_consumption({'validation_passed':False})
