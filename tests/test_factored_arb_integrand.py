from pathlib import Path
import sys
import sympy as sp
import numpy as np
import pytest
from flint import arb,ctx
from bhsm.interface.factored_arb_integrand import factored_local_algebra,use_factored_integrand
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import certify_n12_gate7_accepted_replay_center_outward_74d as parent


def test_complete_bulk_and_inertia_are_symbolically_identical():
    z=sp.symbols('c a b cp ap bp lc la lb n np beta betap',real=True)
    c,a,b,cp,ap,bp,lc,la,lb,n,npj,beta,betap=z
    r,a0,b0,cf,sf,potential,localization=sp.symbols('r a0 b0 cf sf potential localization',positive=True)
    C=r*sp.exp(c);A=a0*sp.exp(a);B=b0*sp.exp(b);N=sp.exp(n)
    hc=(lc-beta*cp-betap)/N;ha=(la-beta*ap)/N;hb=(lb-beta*bp)/N
    adm=hc**2+3*ha**2+3*hb**2-(hc+3*ha+3*hb)**2
    xeta=1/C**2+cf/A**2+sf/B**2-(-beta/N)**2
    gravity=3*A**3*B**3/C*N*(npj*(ap+bp)+ap**2+bp**2+3*ap*bp)
    algebraic=N*C*A**3*B**3*(3/A**2+3/B**2-potential-localization*(xeta/2+xeta**4/8)+adm/2)
    inertia=C*A**3*B**3*localization*(1+xeta**3)/N
    bulk2,inertia2=factored_local_algebra(z,r,a0,b0,cf,sf,potential,localization,sp.exp)
    assert sp.simplify(sp.expand(gravity+algebraic-bulk2))==0
    assert sp.simplify(sp.expand(inertia-inertia2))==0


def test_context_preserves_original_and_rejects_changed_state_and_precision():
    original=parent._integrand;before=ctx.prec;ctx.prec=256
    state=np.zeros(parent.STATE)
    try:
        with use_factored_integrand(parent,state):
            for node in (0,47,95):
                expected=original(state,node,0)
                actual=parent._integrand(state,node,0)
                assert expected.bulk.d[0].overlaps(actual.bulk.d[0])
                assert expected.inertia.d[0].overlaps(actual.inertia.d[0])
            changed=state.copy();changed[0]=1
            with pytest.raises(RuntimeError,match='state'):
                parent._integrand(changed,0,0)
            ctx.prec=192
            with pytest.raises(RuntimeError,match='precision'):
                parent._integrand(state,0,0)
            raise LookupError('exercise restoration')
    except LookupError:
        pass
    finally:
        ctx.prec=before
    assert parent._integrand is original


def test_actual_fifth_order_local_jets_overlap_at_frozen_binary64_constants():
    original=parent._integrand;before=ctx.prec;ctx.prec=256
    state=np.zeros(parent.STATE)
    rng=np.random.default_rng(409)
    # The physical graph supplies Arb legs. Float-only leaves would perform
    # unbounded binary64 products before interacting with an Arb value.
    legs=[np.array([arb(float(v)) for v in rng.normal(size=13)/8],dtype=object) for _ in range(5)]
    try:
        expected=original(state,42,5,legs)
        with use_factored_integrand(parent,state):
            actual=parent._integrand(state,42,5,legs)
        for left,right in ((expected.bulk,actual.bulk),(expected.inertia,actual.inertia)):
            assert len(left.d)==32
            assert all(a.overlaps(b) for a,b in zip(left.d,right.d))
    finally:
        ctx.prec=before
