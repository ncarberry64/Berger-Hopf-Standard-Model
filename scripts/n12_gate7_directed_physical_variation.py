"""Complete physical variations evaluated on supplied weighted directions.

Retains the original D3/D4 contractions and both coupled variations. Interval
input directions are allowed; the verified point check uses their midpoints.
This helper alone establishes neither quotient frames nor global contraction.
"""
import json
import numpy as np
from flint import arb, arb_mat
from bhsm.interface import centered_coupled_variation_residual as signed
from bhsm.interface.componentwise_weighted_response import enclose_response_rows as enclose_response
from bhsm.interface.ball_factored_arb_integrand import use_ball_factored_integrand
from bhsm.interface import coupled_physical_normalization_derivative as normalization


def checked_directions(directions):
    directions = np.asarray(directions, dtype=object)
    if (directions.ndim != 2 or directions.shape[0] != 99 or directions.shape[1] == 0
            or not all(isinstance(v, arb) and v.is_finite() for v in directions.flat)):
        raise ValueError('finite nonempty Arb directions with 99 weighted rows required')
    return directions.copy()


def evaluate_uniform(engine,source,directions):
    p=engine.p;cert=p.values.cert;inverse=engine.inverse
    directions=checked_directions(directions);count=directions.shape[1]
    paired=source['paired'];full=paired['full'];eigenbox=paired['eigenbox']
    _,weights,_,reference,_=p.values.operands()
    original_solve=cert._verified_solve;original_eigenline=cert._eigenline
    calls=[];residuals=[];proofs=[]

    def solve(matrix,rhs):
        if matrix.nrows()!=62 or matrix.ncols()!=62 or rhs.nrows()!=62:
            raise ArithmeticError('retained coupled bordered system required')
        if not calls:
            if rhs.ncols()!=1:raise ArithmeticError('physical response must be first')
            calls.append('PAIRED_PHYSICAL_RESPONSE')
            return arb_mat(62,1,list(source['response']))
        if len(calls)>=3 or rhs.ncols()!=count:
            raise ArithmeticError('exactly one eigenline and one response variation required')
        enclosed,residual,proof=inverse.enclose_columns(paired['rm'],
            np.array(rhs.entries(),dtype=object).reshape(62,count),paired['radii'],paired['variation'])
        residuals.append(residual);proofs.append(proof)
        calls.append('EIGENLINE_VARIATION' if len(calls)==1 else 'RESPONSE_VARIATION')
        return arb_mat(62,count,list(enclosed.flat))

    try:
        cert._verified_solve=solve
        cert._eigenline=lambda *args:(eigenbox[:61],eigenbox[-1],arb(0),arb(0))
        with p.df.sparse.use_optimized_mixed(cert),use_ball_factored_integrand(cert,full):
            result=cert._rate_enclosure(full,source['raw_domain'][98],weights,reference,directions)
        if len(calls)!=3 or result.derivative.shape!=(99,count):
            raise ArithmeticError('complete physical first variation required')
        if not all(isinstance(v,arb) and v.is_finite() for v in result.derivative.flat):
            raise ArithmeticError('nonfinite uniform physical derivative')
        if not all(a.overlaps(b) for a,b in zip(result.value,source['old_rate'],strict=True)):
            raise ArithmeticError('paired physical value and derivative evaluation disagree')
        return result.derivative,np.stack(residuals),proofs
    finally:
        cert._verified_solve=original_solve;cert._eigenline=original_eigenline


def refine_directions(engine,source,directions):
    """Recompute and retain the original D3/D4 contractions and both variations.

    The caller must have loaded paired physical inputs through the endpoint or
    actual-midpoint uniform derivative producer and must bind this helper and
    the normalization implementation in its numerical evidence.
    """
    p=engine.p;cert=p.values.cert;count=directions.shape[1]
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
        old,residual,_=evaluate_uniform(engine,source,directions)
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
    dc=np.array([[arb(float(qw[i]))*directions[37+i,k]/arb(float(weights[37+i]))
                  for k in range(count)] for i in range(37)],dtype=object)
    ds=directions[98].copy()
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


def evaluate(engine,source,directions):
    p=engine.p;cert=p.values.cert;paired=source['paired']
    directions=checked_directions(directions);count=directions.shape[1]
    _,weights,descriptors,reference,_=p.values.operands()
    raw=directions[:98]/np.array([arb(float(v)) for v in weights])[:,None]
    center=paired['center'];full=paired['full'];psi=paired['eigenbox'][:61];lam=paired['eigenbox'][-1]
    descriptor=source['raw_center'][98] if 'raw_center' in source else arb(float(descriptors[source['index']]))
    if not source['raw_domain'][98].contains(descriptor):raise ArithmeticError('anchor descriptor outside original domain')
    original_solve=cert._verified_solve;point_solutions=[];checks=[]
    def point_solve(matrix,rhs):
        result=original_solve(matrix,rhs)
        point_solutions.append(np.array([v.mid() for v in result.entries()],dtype=object).reshape(result.nrows(),result.ncols()))
        return result
    try:
        cert._verified_solve=point_solve
        with p.df.sparse.use_optimized_mixed(cert),use_ball_factored_integrand(cert,center):
            with p.hs.verified_eigenline(cert,checks,expected_index=24,normalize_proposal_center=True):
                point_directions=np.array([v.mid() for v in directions.flat],dtype=object).reshape(directions.shape)
                point=cert._rate_enclosure(center,descriptor,weights,reference,point_directions)
    finally:cert._verified_solve=original_solve
    if (len(checks)!=1 or not p.proof_valid(checks[0]) or len(point_solutions)!=3
            or [a.shape for a in point_solutions]!=[(62,1),(62,count),(62,count)]):
        raise ArithmeticError('verified anchor and all three original physical solves required')
    print(json.dumps(dict(phase='VERIFIED_POINT_VARIATION_CENTERS',direction_count=count)),flush=True)
    with p.df.sparse.use_optimized_mixed(cert),use_ball_factored_integrand(cert,full):
        maps=cert._arb_action_jets(full).dense_maps
    original_inverse=engine.inverse.enclose_columns;original_action=cert._contracted_action
    qw,rw,_,_=cert.metric_data();calls=[];slopes=None;proofs=[]
    def centered(R,rhs,r,V):
        nonlocal slopes
        which=len(calls)
        if which>=2:raise ArithmeticError('exactly two uniform variations required')
        fixed=point_solutions[which+1]
        if which==0:
            residual,slopes=signed.line_residual(original_action,full,psi,lam,R,fixed,raw,maps)
        else:
            residual=signed.physical_response_residual(original_action,full,psi,lam,
                source['response'][:61],source['response'][-1],calls[0][:61],slopes,
                R,fixed,qw,rw,weights,raw,maps)
        box=np.empty_like(fixed);bounds=[]
        for column in range(count):
            z=fixed[:,column].copy();z[-1]=-z[-1]
            box[:,column],proof=enclose_response(z,residual[:,column],r,V)
            box[-1,column]=-box[-1,column];bounds.append(proof)
        old,_,_=original_inverse(R,rhs,r,V)
        if not all(a.overlaps(b) for a,b in zip(box.flat,old.flat)):
            raise ArithmeticError('centered and zero-center variation enclosures disagree')
        calls.append(box.copy());proofs.append(bounds)
        print(json.dumps(dict(phase='CENTERED_VARIATION',which=which,
            maximum_radius=float(max(v.rad() for v in box.flat)),
            zero_center_maximum_radius=float(max(v.rad() for v in old.flat)))),flush=True)
        return box,residual,bounds
    try:
        engine.inverse.enclose_columns=centered
        arrays,normalization=refine_directions(engine,source,directions)
    finally:engine.inverse.enclose_columns=original_inverse
    if len(calls)!=2:raise ArithmeticError('both centered variations required')
    if not all(a.contains(b) for a,b in zip(arrays['derivative'].flat,point.derivative.flat)):
        raise ArithmeticError('uniform derivative must contain verified point derivative')
    arrays.update(directions=directions,point_directions=point_directions,point_derivative=point.derivative,point_line_center=point_solutions[1],
                  point_response_center=point_solutions[2],raw_domain=source['raw_domain'])
    return arrays,dict(point_eigenpair_checks=checks,centered_bounds=proofs,normalization=normalization)

