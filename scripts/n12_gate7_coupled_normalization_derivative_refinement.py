"""Refine an original complete rate variation by canceling its common scale."""
import numpy as np
from flint import arb
from bhsm.interface import coupled_physical_normalization_derivative as normalization


def refine_batch(engine,source,start,stop):
    """Recompute and retain the original D3/D4 contractions and both variations.

    The caller must have loaded paired physical inputs through the endpoint or
    actual-midpoint uniform derivative producer and must bind this helper and
    the normalization implementation in its numerical evidence.
    """
    p=engine.p;cert=p.values.cert;count=stop-start
    original_action=cert._contracted_action;original_inverse=engine.inverse.enclose_columns
    contractions=[];variations=[]

    def action(state,legs,maps):
        result=original_action(state,legs,maps)
        contractions.append((len(legs),np.asarray(result,dtype=object).copy()))
        return result

    def solve(*args,**kwargs):
        result=original_inverse(*args,**kwargs)
        variations.append(result[0].copy())
        return result

    try:
        cert._contracted_action=action;engine.inverse.enclose_columns=solve
        old,residual,_=engine.evaluate_batch(source,start,stop)
    finally:
        cert._contracted_action=original_action;engine.inverse.enclose_columns=original_inverse
    expected=[(3,2),(3,61*3*(count+2)),(3,2*count),(4,2*count)]
    if [(rank,array.size) for rank,array in contractions]!=expected or len(variations)!=2:
        raise ArithmeticError('complete original descriptor contractions and both coupled variations required')
    if any(a.shape!=(62,count) for a in variations):
        raise ArithmeticError('complete selected-line and physical-response variations required')
    cp,remainder=contractions[0][1].reshape(2)
    directional=contractions[1][1].reshape(61,3,count+2)
    dynamic=contractions[2][1].reshape(2*count)
    fourth=contractions[3][1].reshape(count,2)
    dp=variations[0][:61];dh=variations[1][:61];db=variations[1][-1]
    fixed=directional[:,0,count:count+2]
    dcp=np.array([fourth[k,0]+2*sum((dp[i,k]*fixed[i,0] for i in range(61)),arb(0))+dynamic[k]
                  for k in range(count)],dtype=object)
    dr=np.array([fourth[k,1]+2*sum((dp[i,k]*fixed[i,1] for i in range(61)),arb(0))+dynamic[count+k]
                 for k in range(count)],dtype=object)
    full=source['paired']['full'];psi=source['paired']['eigenbox'][:61];response=source['response']
    _,weights,_,_,_=p.values.operands();qw,rw,_,_=cert.metric_data()
    configuration=np.array([arb(float(qw[i]))*full[37+i] for i in range(37)],dtype=object)
    dc=np.full((37,count),arb(0),dtype=object);ds=np.full(count,arb(0),dtype=object)
    for column in range(start,stop):
        if 37<=column<74:dc[column-37,column-start]=arb(float(qw[column-37]))/arb(float(weights[column]))
        if column==98:ds[column-start]=arb(1)
    derivative,proof=normalization.normalized_derivative(configuration,
        [arb(float(v)) for v in rw],psi,response[:61],response[-1],source['raw_domain'][98],cp,remainder,
        dc,dp,dh,db,ds,dcp,dr,coupled_identities_and_variations=True)
    if derivative.shape!=(99,count) or not all(a.overlaps(b) for a,b in zip(derivative.flat,old.flat)):
        raise ArithmeticError('coupled normalization derivative and original formula disagree')
    p.verify_sources(source['binding'])
    return dict(derivative=derivative,original_derivative=old,
        preconditioned_variation_rhs=residual,selected_line_variation=variations[0],response_variation=variations[1],
        descriptor_contractions=np.array([cp,remainder],dtype=object),
        descriptor_contraction_variations=np.stack((dcp,dr))),proof
