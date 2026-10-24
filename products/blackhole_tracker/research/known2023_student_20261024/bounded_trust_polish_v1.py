"""Numerical research: bounded score-based Newton polishing.

No input loader, physical model, data fit or scientific acceptance.  A score
callback and explicit numerical domains are supplied by the caller.  The
algorithm never changes a bound, covariance, likelihood or score tolerance.
"""
import numpy as np
from scipy.linalg import cho_factor,cho_solve


def polish_score(score,state,lower,upper,scales,*,max_iterations=8,
                 score_tolerance=.02,difference_step=1e-4,max_scaled_step=1.):
    """Try to reduce the full scaled projected score at a local optimum.

    An analytical-score finite difference constructs the local Hessian.  No
    Hessian ridge, pseudoinverse, likelihood reweighting or covariance floor is
    substituted. A nonpositive free Hessian remains explicitly unresolved.
    This is not a global-optimization certificate or an interval calculation.
    """
    if any(np.iscomplexobj(x) for x in (state,lower,upper,scales)):
        raise ValueError('Real state, bounds and scales required')
    state,lo,hi,s=[np.asarray(x,dtype=float).copy() for x in (state,lower,upper,scales)]
    if state.ndim!=1 or any(x.shape!=state.shape for x in (lo,hi,s)) or not np.isfinite(state).all() or not np.isfinite(s).all() or np.any(s<=0) or np.any(np.isnan(lo)) or np.any(np.isnan(hi)) or np.any(lo>=hi) or np.any(state<lo) or np.any(state>hi):
        raise ValueError('Finite admitted state, ordered bounds and positive fixed scales required')
    if type(max_iterations)is not int or max_iterations<1 or isinstance(max_scaled_step,(bool,np.bool_)) or not np.isfinite([score_tolerance,difference_step,max_scaled_step]).all() or score_tolerance<=0 or difference_step<=0 or max_scaled_step<=0:
        raise ValueError('Positive explicit effort and numerical tolerances required')
    # A local additive anchor preserves the exact supplied native initial
    # state and removes arbitrary coordinate origin from numerical scaling.
    anchor=state.copy();z=np.zeros_like(state);zl=(lo-anchor)/s;zh=(hi-anchor)/s;ledger=[];trials=[]
    if np.any(np.isfinite(lo)&~np.isfinite(zl)) or np.any(np.isfinite(hi)&~np.isfinite(zh)) or np.any((state>lo)&(zl==0)) or np.any((state<hi)&(zh==0)):
        raise ValueError('Scaled coordinates/bounds must remain representable')
    def native(point):
        x=anchor+s*point
        # Explicit exact face mapping, followed by actual score reevaluation.
        # Native interior states are never silently treated as face points.
        x[point==zl]=lo[point==zl];x[point==zh]=hi[point==zh]
        return x
    def evaluate(point):
        x=native(point)
        if not np.isfinite(x).all() or np.any(x<lo) or np.any(x>hi):raise ValueError('Native evaluated point outside representable box')
        value,g=score(x)
        if np.iscomplexobj(value) or np.iscomplexobj(g):raise FloatingPointError('Real objective and analytical score required')
        g=np.asarray(g,dtype=float)*s
        if not np.isfinite(value) or g.shape!=point.shape or not np.isfinite(g).all():
            raise FloatingPointError('Finite objective and complete full analytical score required')
        return float(value),g
    def projected(point,g):
        # Only actual representable face contact may remove an outward score.
        # An origin-dependent distance tolerance can falsely mark interior
        # points as both faces when coordinates have a large additive offset.
        out=g.copy()
        x=native(point)
        blocked=((x==lo)&(g>0))|((x==hi)&(g<0))
        out[blocked]=0.
        return out,blocked
    status='ITERATION_LIMIT'
    for iteration in range(max_iterations+1):
        value,g=evaluate(z);pg,blocked=projected(z,g);norm=float(np.max(abs(pg)))
        row={'iteration':iteration,'value':value,'scaled_projected_score_max':norm,'state':native(z).tolist()};ledger.append(row)
        if norm<=score_tolerance:status='DECLARED_PROJECTED_SCORE_REACHED';break
        if iteration==max_iterations:break
        take=np.flatnonzero(~blocked)
        H=np.empty((len(take),len(take)));fd=[]
        try:
            for col,j in enumerate(take):
                h=difference_step
                if z[j]-h>=zl[j] and z[j]+h<=zh[j]:
                    plus=z.copy();minus=z.copy();plus[j]+=h;minus[j]-=h
                    hp,hm=(native(plus)[j]-native(z)[j])/s[j],(native(z)[j]-native(minus)[j])/s[j]
                    if hp<=0 or hm<=0:raise FloatingPointError('Finite-difference perturbation is not representable')
                    derivative=(hm/(hp+hm))*((evaluate(plus)[1]-g)/hp)+(hp/(hp+hm))*((g-evaluate(minus)[1])/hm);mode='CENTRAL_ACTUAL_REPRESENTABLE_STEPS'
                else:
                    direction=1. if zh[j]-z[j]>=z[j]-zl[j] else -1.
                    room=(zh[j]-z[j]) if direction>0 else (z[j]-zl[j])
                    h=min(h,room/3.)
                    if not np.isfinite(h) or h<=0:raise FloatingPointError('No representable finite-difference room')
                    one=z.copy();two=z.copy();one[j]+=direction*h;two[j]+=direction*2*h
                    h1=direction*(native(one)[j]-native(z)[j])/s[j];h2=direction*(native(two)[j]-native(z)[j])/s[j]
                    if h1<=0 or h2<=h1:raise FloatingPointError('Distinct finite-difference perturbations are not representable')
                    derivative=direction*((h2/(h2-h1))*((evaluate(one)[1]-g)/h1)-(h1/(h2-h1))*((evaluate(two)[1]-g)/h2));mode='ONE_SIDED_ACTUAL_REPRESENTABLE_STEPS'
                H[:,col]=derivative[take];fd.append({'coordinate':int(j),'scaled_step':float(h),'mode':mode})
            H=(H+H.T)/2.
            if not np.isfinite(H).all():raise FloatingPointError('Nonfinite finite-difference Hessian')
            direction=np.zeros_like(z);factor=cho_factor(H,lower=True,check_finite=True)
            direction[take]=-cho_solve(factor,g[take])
            original_step_norm=float(np.max(np.abs(direction)))
            if original_step_norm>max_scaled_step:
                direction*=max_scaled_step/original_step_norm
            row['original_Newton_scaled_infinity_norm']=original_step_norm
            row['fixed_scaled_trust_step_limit']=float(max_scaled_step)
            row['Newton_direction_uniformly_shortened']=bool(original_step_norm>max_scaled_step)
            row['finite_differences']=fd;row['free_hessian_minimum_eigenvalue']=float(np.linalg.eigvalsh(H).min())
        except (ValueError,FloatingPointError,np.linalg.LinAlgError,RuntimeError) as error:
            row['unresolved_reason']=type(error).__name__+': '+str(error);status='LOCAL_CURVATURE_OR_SCORE_UNRESOLVED';break
        # Keep the true Newton direction and shorten it to the first box face;
        # componentwise clipping of a coupled Newton direction need not descend.
        limit=1.
        for j in take:
            if direction[j]>0:limit=min(limit,(zh[j]-z[j])/direction[j])
            elif direction[j]<0:limit=min(limit,(zl[j]-z[j])/direction[j])
        if not np.isfinite(limit) or limit<=0 or float(g@direction)>=0:
            row['unresolved_reason']='No admissible Newton descent direction';status='BOUNDARY_STEP_UNRESOLVED';break
        accepted=False
        for half in range(40):
            point=np.clip(z+(limit*2.**(-half))*direction,zl,zh);delta=point-z;slope=float(g@delta)
            if not np.isfinite(slope) or slope>=0:continue
            try:
                proposed,gg=evaluate(point);pp,_=projected(point,gg)
            except (ValueError,FloatingPointError,np.linalg.LinAlgError,RuntimeError) as error:
                trials.append({'iteration':iteration,'halvings':half,'state':native(point).tolist(),'error':type(error).__name__+': '+str(error)})
                continue
            candidate_norm=float(np.max(abs(pp)));allowance=32*np.finfo(float).eps*max(1.,abs(value))
            trial={'iteration':iteration,'halvings':half,'state':native(point).tolist(),'value':proposed,'projected_score_max':candidate_norm,'floating_comparison_allowance':float(allowance)}
            trials.append(trial)
            strict_descent=proposed<=value+1e-4*slope
            numerical_tie=abs(proposed-value)<=allowance and candidate_norm<norm
            if strict_descent or numerical_tie:
                row.update(accepted_halvings=half,acceptance='ARMIJO_DESCENT' if strict_descent else 'FLOATING_OBJECTIVE_TIE_AND_LOWER_SCORE',value_after=proposed)
                z=point;accepted=True;break
        if not accepted:status='DESCENT_OR_FLOATING_STEP_UNRESOLVED';break
    value,g=evaluate(z);pg,_=projected(z,g);norm=float(np.max(abs(pg)))
    return {'status':status,'state':native(z),'value':value,'scaled_projected_score_max':norm,
        'native_anchor':anchor.tolist(),'face_mapping':'Actual native equality only; explicit scaled-face mapping to exact native bound is reevaluated. Nonrepresentable interior-to-face scaling rejected.',
        'declared_score_reached':bool(norm<=score_tolerance),'trace':ledger,'all_line_search_trials':trials,
        'qualification':'Numerical local refinement only. Every supplied value, bound and score tolerance unchanged. A small projected score is not a global optimum, adequate observation model, identified quantity or physical-interval certificate.'}
