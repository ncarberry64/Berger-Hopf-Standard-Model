"""Local coupled constraint / HS / selected-descriptor center solve.

The frozen Jacobian is a Newton preconditioner only. Every accepted iterate
reevaluates the nonlinear retained action, normalized selected line and rate.
No endpoint is projected after solving, and no binary64 eigenvalue supplies s.
"""
import os
for _name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_name] = '1'
import argparse
import io
import json
from pathlib import Path
import sys
import time

import numpy as np
from flint import arb, arb_mat, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'src')]
import certify_n12_gate7_accepted_replay_center_outward_74d as action
import audit_n12_gate7_within_seam_constraint_center_obstruction as constraints
from bhsm.interface import sparse_arb_mixed_jets as sparse
from bhsm.interface import ball_factored_arb_integrand as factored
from bhsm.interface.physical_hs_value import verified_eigenline, rational_balls
from checkpoint_n12_gate7_66d_tangent_binding import FIXED, PHYSICAL, amat, digest, encoded

BASE = ROOT/'artifacts/flagship_integration'


def matrix(a):
    a = np.asarray(a, dtype=object)
    return arb_mat(*a.shape, list(a.flat))


def array(a):
    return np.array(a.entries(), dtype=object).reshape(a.nrows(), a.ncols())


def mid(a):
    return np.array([float(v.mid()) for v in np.asarray(a).flat]).reshape(np.shape(a))


def norm(a):
    return sum((v*v for v in np.asarray(a).flat), arb(0)).sqrt()


def action_value(state):
    terms = [action._integrand(state, i, 0) for i in range(action.POINTS)]
    bulk = sum((t.bulk.d[0] for t in terms), arb(0))
    inertia = sum((t.inertia.d[0] for t in terms), arb(0))
    return (bulk-arb(0.25/(2.0*action.HOPF_ORBIT_VOLUME**2))/inertia
            +action._boundary(state, 0)[1].d[0])


def point(z, weights, reference, directions=None):
    """Outward nonlinear point evaluation using the existing eigenpair proof."""
    state = z[:98]/weights
    if directions is not None:
        # Preserve W^-1 direction conversion in Arb inside the rate owner.
        directions=np.array([arb(v) for v in np.asarray(directions).flat],dtype=object).reshape(np.shape(directions))
    checks = []
    selected = {}
    original = action._eigenline
    with sparse.use_optimized_mixed(action), factored.use_ball_factored_integrand(action, state):
        with verified_eigenline(action, checks, expected_index=24, normalize_proposal_center=True):
            verified = action._eigenline
            def retain(*args):
                result = verified(*args)
                selected['psi'], selected['lambda'] = result[:2]
                return result
            action._eigenline = retain
            try:
                rate = action._rate_enclosure(state, z[98], mid(weights), reference, directions)
            finally:
                action._eigenline = verified
        value = action_value(state)
        covector = None
        if directions is not None:
            psi=np.r_[np.full(37,arb(0),dtype=object),selected['psi']]
            legs=np.full((98,98),arb(0),dtype=object)
            for j in range(98):legs[j,j]=1/weights[j]
            covector=np.asarray(action._contracted_action(
                state,[psi[:,None],psi[:,None],legs],rate.action_jets.dense_maps),dtype=object).reshape(98)
    assert action._eigenline is original
    jets = rate.action_jets
    velocity = state[37:74]
    energy = sum((v*g for v,g in zip(velocity,jets.gradient_arb[37:74])),arb(0))-value
    c = np.r_[jets.gradient_arb[74:], energy]
    H, g = jets.hessian_arb, jets.gradient_arb
    energy_row = []
    for j in range(98):
        v = sum((velocity[i]*H[37+i,j] for i in range(37)),arb(0))
        if j<37 or j>=74: v -= g[j]
        energy_row.append(v/weights[j])
    dc = np.vstack((H[74:]/weights[None,:],np.array(energy_row,dtype=object)))
    return dict(rate=rate.value, derivative=rate.derivative, covector=covector,
                constraints=c, DC=dc, eigenvalue=selected['lambda'],
                eigenpair_proof=checks[0], state=state,
                rate_radius_upper=float(norm(np.array([v.rad() for v in rate.value])).upper()))


def load_problem():
    with np.load(ROOT/FIXED) as z:
        states=z['projected_states'][13:15]
        weights=z['state_weights']; reference=z['branch_reference']
        descriptors=z['independent_signed_descriptors'][13:15]
    with np.load(ROOT/PHYSICAL) as z:
        B=z['endpoint_physical_tangent_action'][13:15]
        jl,jr=z['endpoint_augmented_Jacobian_action'][13:15]
        jm=z['midpoint_augmented_Jacobian_action'][13]
    frames=[]; scales=[]
    for state in states:
        c,s,_=constraints._constraint_geometry(state,weights)
        frames.append(c);scales.append(s)
    # Frozen normal coordinates fix the 73 left physical parameters. This is
    # a chart choice, not a new boundary condition or an action modification.
    normal=frames[0].T
    L=np.zeros((99,26));L[:98,:25]=normal;L[98,25]=1e-7
    R=np.eye(99);R[98,98]=1e-7
    test=np.zeros((74,99));test[:73,:98]=B[1].T;test[73,98]=1e6
    h=0.25; eye=np.eye(99)
    dl=-eye-h*jl/6-2*h*jm@(eye/2+h*jl/8)/3
    dr=eye-h*jr/6-2*h*jm@(eye/2-h*jr/8)/3
    J=np.zeros((125,125))
    J[:25,:25]=frames[0]@normal
    J[25:50,26:124]=frames[1]
    J[50:124,:26]=test@dl@L;J[50:124,26:]=test@dr@R
    with np.load(BASE/'gate7_fiber_covector_20260927/arrays.npz') as z:
        g=np.array([float(arb(str(v))) for v in z['gradient_action_mid_q'].flat])
    J[124,:25]=g@normal/1e-7;J[124,25]=-1
    w=np.array([arb(float(v)) for v in weights],dtype=object)
    endpoints=np.array([np.r_[np.array([arb(float(v)) for v in s])*w,arb(float(d))]
                        for s,d in zip(states,descriptors)],dtype=object)
    return dict(z=endpoints,w=w,reference=reference,L=amat(L),R=amat(R),
                test=amat(test),scales=amat(np.array(scales)),J=amat(J),h=arb(1)/4,
                normal=normal)


def evaluate(problem, x):
    z0=problem['z'][0]+array(problem['L']*arb_mat(26,1,x.entries()[:26])).ravel()
    z1=problem['z'][1]+array(problem['R']*arb_mat(99,1,x.entries()[26:])).ravel()
    p0=point(z0,problem['w'],problem['reference'])
    p1=point(z1,problem['w'],problem['reference'])
    h=problem['h']
    zm=(z0+z1)/2+h*(p0['rate']-p1['rate'])/8
    pm=point(zm,problem['w'],problem['reference'])
    hs=z1-z0-h*(p0['rate']+4*pm['rate']+p1['rate'])/6
    scaled=[p0['constraints'][i]/problem['scales'][0,i] for i in range(25)]
    scaled += [p1['constraints'][i]/problem['scales'][1,i] for i in range(25)]
    scaled += (problem['test']*arb_mat(99,1,list(hs))).entries()
    scaled += [(p0['eigenvalue']-z0[98])/arb(1e-7)]
    return arb_mat(125,1,scaled),dict(left=p0,right=p1,midpoint=pm,z0=z0,z1=z1,zm=zm,hs=hs)


def calculate(out, iterations):
    ctx.prec=512
    problem=load_problem();x=arb_mat(125,1);J=problem['J'];inverse=J.inv()
    log=[];previous=None;previous_x=None
    for k in range(iterations+1):
        start=time.monotonic();res,data=evaluate(problem,x)
        diagnostic=dict(iteration=k,residual_norm_upper=float(norm(res.entries()).upper()),
            constraint_left=float(norm(res.entries()[:25]).upper()),
            constraint_right=float(norm(res.entries()[25:50]).upper()),
            shooting_reduced=float(norm(res.entries()[50:124]).upper()),
            fiber_left_physical=float(abs(data['left']['eigenvalue']-data['z0'][98]).upper()),
            fiber_right_physical=float(abs(data['right']['eigenvalue']-data['z1'][98]).upper()),
            shooting_full=float(norm(data['hs']).upper()))
        log.append(diagnostic)
        print(json.dumps({**diagnostic,'seconds':round(time.monotonic()-start,2)}),flush=True)
        # Keep an inspectable current iterate even if interrupted. No frozen
        # scientific artifact is overwritten by this work directory.
        arrays={}
        for name,v in [('coordinates',array(x)),('left_endpoint',data['z0']),
                       ('right_endpoint',data['z1']),('midpoint',data['zm']),
                       ('residual',array(res)),('shooting_full',data['hs'])]:
            m,r=rational_balls(v);arrays[name+'_mid_q']=m;arrays[name+'_rad_q']=r
        buffer=io.BytesIO();np.savez_compressed(buffer,**arrays)
        (out/'arrays.npz').write_bytes(buffer.getvalue())
        report=dict(status='COUPLED_FIBER_CONSTRAINT_HS_CENTER_ITERATE',iterations=log,
            equations='25 left constraints +25 right constraints +74 frozen-test HS rows +left fiber row',
            unknowns='25 left constraint-normal coordinates +left descriptor +98 right action-state +right descriptor',
            left_physical_parameters='73 frozen left chart coordinates held fixed',
            fiber_row_inside_solve=True,post_solve_projection=False,raw_eigenvalue_as_descriptor=False,
            center_root_certified=False,current_Jacobian_certified=False,
            boundary_rows_separately_imposed=False,
            boundary_scope='The seven reaction components belong to the owned 74 HS rows. Independent nonlinear boundary-value equivalence is not assumed.',
            Newton_preconditioner='Frozen first derivative; optional secant inverse updates are proposals only.',
            endpoint_eigenpair_proofs=[data[n]['eigenpair_proof'] for n in ('left','right','midpoint')],
            source_SHA256={str(p.relative_to(ROOT)):digest(p) for p in (
                ROOT/FIXED,ROOT/PHYSICAL,Path(__file__),Path(action.__file__),Path(factored.__file__),
                BASE/'gate7_fiber_covector_20260927/arrays.npz')},
            arrays_SHA256=digest(out/'arrays.npz'),tolerances_changed=False,
            Gate7_closed=False,FULL_BHSM_COMPLETE=False)
        (out/'report.json').write_bytes(encoded(report))
        if k==iterations or diagnostic['residual_norm_upper']<1e-60:break
        # Inverse good-Broyden update retains signed secant dependence. It
        # changes a numerical solver proposal, never a proof tolerance.
        if previous is not None:
            step=x-previous_x;y=res-previous;By=inverse*y
            row=step.transpose()*inverse;denom=(row*y)[0,0]
            if not denom.contains(0):inverse=inverse+(step-By)*row/denom
        previous=arb_mat(125,1,[v.mid() for v in res.entries()]);previous_x=x
        update=inverse*res
        x=arb_mat(125,1,[(x[i,0]-update[i,0]).mid() for i in range(125)])
    return report


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--iterations',type=int,default=12);args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=False);calculate(args.out,args.iterations)


if __name__=='__main__':main()
