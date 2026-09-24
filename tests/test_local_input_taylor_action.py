import importlib.util
from pathlib import Path
import sys
import numpy as np
from flint import arb,arb_mat,ctx
from bhsm.interface.shared_action_taylor import TaylorDomain
from bhsm.interface.input_linear_taylor import InputLinearTaylor,input_linear_taylor_action as dense_action
from bhsm.interface.local_input_taylor_action import input_linear_taylor_action as local_action
from bhsm.interface.local_input_taylor_action_fast import input_linear_taylor_action as fast_action
from bhsm.interface.local_input_taylor_action_top import input_linear_taylor_action as top_action


def test_local_input_projection_preserves_global_action_coefficients_and_enclosure():
    path=Path(__file__).resolve().parents[1]/'scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py'
    spec=importlib.util.spec_from_file_location('_local_input_action_parent',path)
    parent=importlib.util.module_from_spec(spec);sys.modules[spec.name]=parent;spec.loader.exec_module(parent)
    ctx.prec=256
    domain=TaylorDomain([(0,1,'interval')],1)
    state=np.array([domain.affine(0,[arb('1e-5') if i==0 else arb(0)]) for i in range(98)],dtype=object)
    positions=[0,37,74]+list(range(1,14))
    inputs=np.array([InputLinearTaylor(domain,arb_mat(1,16,[arb(i==j) for j in positions]),arb_mat(1,16))
                     for i in range(98)],dtype=object)
    for i in range(98):
        if i not in positions: inputs[i]=domain.affine(0)
    point=np.array([arb(0)]*98,dtype=object)
    maps=[parent._dense_mapping(parent._integrand(point,n,0).maps) for n in range(parent.POINTS)]
    left=np.array([arb(i==0) for i in range(98)],dtype=object)
    second=np.array([arb(i==74) for i in range(98)],dtype=object)
    third=np.array([arb(i==37) for i in range(98)],dtype=object)
    for legs in ([inputs],[left,inputs],[left,second,inputs],[left,second,third,inputs]):
        with dense_action(parent): dense=parent._contracted_action(state,legs,maps)
        with local_action(parent): local=parent._contracted_action(state,legs,maps)
        with fast_action(parent): fast=parent._contracted_action(state,legs,maps)
        encode=lambda model:[(str(v.mid().fmpq()),str(v.rad().fmpq()))
                             for v in model.c.entries()+model.a.entries()+[model.r]]
        assert encode(fast)==encode(local)
        with top_action(parent): top=parent._contracted_action(state,legs,maps)
        assert encode(top)==encode(local)
        assert local.c.overlaps(dense.c) and local.a.overlaps(dense.a)
        for theta in (-1,1):
            actual_state=np.array([v.c+theta*v.a[0,0] for v in state],dtype=object)
            for j in (0,1,2,15):
                axis=arb_mat(16,1,[arb(i==j) for i in range(16)])
                direct=list(legs[:-1])+[np.array([arb(i==positions[j]) for i in range(98)],dtype=object)]
                target=parent._contracted_action(actual_state,direct,maps)
                model=local.at_input(axis)
                assert (model.c+theta*model.a[0,0]+arb(0,model.r)).contains(target)

import pytest


@pytest.fixture(autouse=True)
def restore_arb_precision():
    previous = ctx.prec
    try:
        yield
    finally:
        ctx.prec = previous
