"""Lower independently broadcast contraction axes without changing their pairing."""
from contextlib import contextmanager
import hashlib,inspect
import numpy as np
from bhsm.interface.prescribed_arb_action_jet import affine_action_contraction

PARENT_CONTRACTION_SHA256='ED7727A5841EA5A44A964034C8B65CD7A229DCFB08EF3A4FE04DF1DD42C88EE3'


def independent_legs(raw_legs,state_dimension):
    legs=[np.asarray(v,dtype=object) for v in raw_legs]
    if not legs or any(v.ndim<2 or v.shape[0]!=state_dimension or min(v.shape)==0 for v in legs):
        raise ValueError('nonempty state-by-batch contraction legs required')
    rank=max(v.ndim-1 for v in legs);positions=[]
    for value in legs:
        shape=(1,)*(rank-value.ndim+1)+value.shape[1:]
        active=[i for i,n in enumerate(shape) if n!=1]
        if len(active)>1:
            raise ValueError('a leg couples multiple broadcast axes')
        positions.extend(active)
    if positions!=sorted(set(positions)):
        raise ValueError('shared or reordered broadcast axes require explicit reconciliation')
    shape=np.broadcast_shapes(*(v.shape[1:] for v in legs))
    return [v.reshape(state_dimension,-1) for v in legs],shape


@contextmanager
def use_independent_contraction_axes(module):
    original=module._contracted_action
    if hashlib.sha256(inspect.getsource(original).encode()).hexdigest().upper()!=PARENT_CONTRACTION_SHA256:
        raise RuntimeError('parent contraction changed')
    def contracted(state,raw_legs,dense_maps):
        legs,shape=independent_legs(raw_legs,module.STATE)
        return affine_action_contraction(module,state,dense_maps,*legs).reshape(shape)
    module._contracted_action=contracted
    try:yield
    finally:module._contracted_action=original
