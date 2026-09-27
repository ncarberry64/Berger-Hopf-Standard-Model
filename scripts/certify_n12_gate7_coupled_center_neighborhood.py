"""Local Banach certificate for the declared coupled center equations.

This certifies a replacement neighborhood, not the former full history tube
and not an unproved identification of its shooting rows with boundary values.
"""
import argparse
import json
from pathlib import Path
import time
import numpy as np
from flint import arb, arb_mat, ctx
import solve_n12_gate7_fiber_constrained_center as s
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from bhsm.interface.physical_hs_value import restore_balls
from checkpoint_n12_gate7_66d_tangent_binding import digest, encoded
from diagnose_n12_gate7_eight_reaction_center import block, identity


def load(path):
    with np.load(path) as z:
        return {k[:-6]:restore_balls(z[k],z[k[:-6]+'_rad_q'])
                for k in z.files if k.endswith('_mid_q')}


def hull(z, matrices, radius):
    result=[]
    for i,v in enumerate(z):
        extent=max(sum((abs(M[i,j]).upper() for j in range(M.ncols())),arb(0)).upper()
                   for M in matrices)*radius
        result.append(v+arb(0,extent.upper()))
    return np.array(result,dtype=object)


def jacobian(problem,pl,pr,pm,L):
    jl,jr,jm=[s.matrix(p['derivative']) for p in (pl,pr,pm)]
    h=problem['h'];I=identity(99)
    dl=-I-jl*(h/6)-jm*(I/2+jl*(h/8))*(2*h/3)
    dr=I-jr*(h/6)-jm*(I/2-jr*(h/8))*(2*h/3)
    J=arb_mat(125,125);R=problem['R'];test=problem['test']
    c0=s.matrix(pl['DC'])*block(L,range(98),range(26))
    c1=s.matrix(pr['DC'])*block(R,range(98),range(99))
    hl,hr=test*dl*L,test*dr*R
    gf=arb_mat(1,98,list(pl['covector']))*block(L,range(98),range(26))/arb(1e-7)
    for j in range(26):gf[0,j]-=L[98,j]/arb(1e-7)
    for i in range(25):
        for j in range(26):J[i,j]=c0[i,j]/problem['scales'][0,i]
        for j in range(99):J[25+i,26+j]=c1[i,j]/problem['scales'][1,i]
    for i in range(74):
        for j in range(26):J[50+i,j]=hl[i,j]
        for j in range(99):J[50+i,26+j]=hr[i,j]
    for j in range(26):J[124,j]=gf[0,j]
    return J


def certificate(J,center_J,residual,radius):
    proposal=center_J.inv();R=arb_mat(125,125,[v.mid() for v in proposal.entries()])
    RF=R*residual;D=identity(125)-R*J
    Y=max(abs(v).upper() for v in RF.entries())
    Z=max(sum((abs(D[i,j]).upper() for j in range(125)),arb(0)).upper() for i in range(125))
    image=(Y+Z*radius).upper()
    return dict(Y_upper=str(Y.fmpq()),Z_upper=str(Z.fmpq()),
        Y_diagnostic=float(Y),Z_diagnostic=float(Z),image_radius_upper=str(image.fmpq()),
        image_radius_diagnostic=float(image),radius_exact=str(radius.fmpq()),
        contraction=bool(Z<1),strict_self_map=bool(image<radius),
        unique_root_in_declared_box=bool(Z<1 and image<radius)),R


def calculate(center,jac,out,radius,reuse=None):
    ctx.prec=512;radius=arb(radius)
    if not radius>0 or not radius.rad().is_zero():raise ValueError('exact positive dyadic radius required')
    problem=s.load_problem();c=load(center/'arrays.npz');j=load(jac/'arrays.npz')
    if reuse is not None:
        frozen=json.loads((reuse/'report.json').read_bytes())
        if (frozen['graph']['radius_exact']!=str(radius.fmpq())
                or digest(center/'arrays.npz') not in frozen['source_SHA256'].values()
                or digest(jac/'arrays.npz') not in frozen['source_SHA256'].values()):
            raise ValueError('cached neighborhood input/domain mismatch')
        for name in ('left','right','midpoint'):
            if digest(reuse/(name+'.npz'))!=frozen['local_derivative_SHA256'][name]:
                raise ValueError('cached uniform derivative changed')
            if digest(reuse/(name+'.json'))!=frozen['local_eigenpair_SHA256'][name]:
                raise ValueError('cached uniform eigenpair proof changed')
    leftpoint=load(jac/'left_endpoint.npz')
    L=problem['L'];Lf=arb_mat(L.tolist())
    # Exact rational phase proposal, subsequently verified by the fiber row.
    for i in range(98):Lf[i,25]=leftpoint['rate'][i].mid()
    Lf[98,25]=0
    z0=hull(c['left_endpoint'],[L,Lf],radius)
    z1=hull(c['right_endpoint'],[problem['R']],radius)
    if reuse is not None:
        frozen_domains=load(reuse/'arrays.npz')
        z0=frozen_domains['left_state_domain'];z1=frozen_domains['right_state_domain']
    points=[]
    for name,z in [('left',z0),('right',z1)]:
        start=time.monotonic()
        if reuse is None:
            p=s.point(z,problem['w'],problem['reference'],np.eye(99))
            save_arrays(out/(name+'.npz'),{k:p[k] for k in ('rate','derivative','covector','DC')})
            (out/(name+'.json')).write_bytes(encoded(p['eigenpair_proof']))
        else:
            for ext in ('.npz','.json'):(out/(name+ext)).write_bytes((reuse/(name+ext)).read_bytes())
        points.append(load(out/(name+'.npz')))
        print(name,'uniform local derivative',round(time.monotonic()-start,2),flush=True)
    # Signed mean-value HS incidence avoids the dependency loss of subtracting
    # two separately evaluated endpoint rate boxes. Uniform endpoint DF is
    # already certified on convex supersets of both parameter charts.
    jl,jr=[s.matrix(p['derivative']) for p in points]
    il=identity(99)/2+jl*(problem['h']/8)
    ir=identity(99)/2-jr*(problem['h']/8)
    left_incidence=[il*M for M in (L,Lf)];right_incidence=ir*problem['R']
    zm=[]
    for i,v in enumerate(c['midpoint']):
        width=max(sum((abs(M[i,j]).upper() for j in range(26)),arb(0)).upper() for M in left_incidence)
        width+=sum((abs(right_incidence[i,j]).upper() for j in range(99)),arb(0)).upper()
        zm.append(v+arb(0,(width*radius).upper()))
    zm=np.array(zm,dtype=object)
    if reuse is not None:
        # Reuse the original bound incidence domain with its unchanged inputs,
        # not a slightly widened reconstruction from serialized coefficients.
        zm=frozen_domains['midpoint_state_domain']
    start=time.monotonic()
    if reuse is None:
        pm=s.point(zm,problem['w'],problem['reference'],np.eye(99))
        save_arrays(out/'midpoint.npz',{k:pm[k] for k in ('rate','derivative','covector','DC')})
        (out/'midpoint.json').write_bytes(encoded(pm['eigenpair_proof']))
    else:
        for ext in ('.npz','.json'):(out/('midpoint'+ext)).write_bytes((reuse/('midpoint'+ext)).read_bytes())
    pm=load(out/'midpoint.npz')
    print('midpoint uniform local derivative',round(time.monotonic()-start,2),flush=True)
    J=jacobian(problem,*points,pm,L);Jf=jacobian(problem,*points,pm,Lf)
    residual=s.matrix(c['residual'])
    graph,R=certificate(J,s.matrix(j['J125']),residual,radius)
    fixed,Rf=certificate(Jf,s.matrix(j['Jfixed125']),residual,radius)
    save_arrays(out/'arrays.npz',dict(J_graph_box=J,J_fixed_box=Jf,
        graph_preconditioner=R,fixed_preconditioner=Rf,left_phase_chart=Lf,
        left_state_domain=z0,right_state_domain=z1,midpoint_state_domain=zm))
    report=dict(status='LOCAL_COUPLED_CENTER_NEIGHBORHOOD_CERTIFIED' if
        graph['unique_root_in_declared_box'] and fixed['unique_root_in_declared_box'] else 'LOCAL_CENTER_BOUND_OPEN',
        graph=graph,fixed_label=fixed,
        formula='T(x)=x-R F(x); Y=||R F(0)||_inf; Z=sup||I-R DF(box)||_inf; Y+Z r<r and Z<1.',
        root_scope='25 constraints at each endpoint, 74 owned projected HS rows, left selected-descriptor fiber equation.',
        fixed_label_scope='Constant exact phase-chart direction enclosed by the corrected C2 flow; descriptor label fixed to corrected s13. This is a local action/fiber chart, not an asserted nonlinear flow-orbit equivalence.',
        boundary_equation_equivalence_proved=False,full99_shooting_zero_claimed=False,
        old_physical_tube_covered=False,local_replacement_radius_only=True,
        midpoint_enclosure='Signed HS incidence and endpoint mean-value DF on the convex parameter box, composed before row support.',
        reused_uniform_certificate_SHA256=digest(reuse/'report.json') if reuse is not None else None,
        inverse_proposal_center_may_differ=True,
        source_SHA256={str(p):digest(p) for p in (center/'arrays.npz',jac/'arrays.npz',
            jac/'left_endpoint.npz',Path(__file__),Path(s.__file__))},
        local_derivative_SHA256={name:digest(out/(name+'.npz')) for name in ('left','right','midpoint')},
        local_eigenpair_SHA256={name:digest(out/(name+'.json')) for name in ('left','right','midpoint')},
        arrays_SHA256=digest(out/'arrays.npz'),
        Gate7_closed=False,FULL_BHSM_COMPLETE=False,tolerances_changed=False)
    (out/'report.json').write_bytes(encoded(report));print(json.dumps(report['graph']),flush=True)
    print(report['status'],flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--center',type=Path,required=True)
    p.add_argument('--jacobian',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--radius',default='1/1532495540865888858358347027150309183618739122183602176')
    p.add_argument('--reuse-derivatives',type=Path)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);calculate(a.center,a.jacobian,a.out,a.radius,a.reuse_derivatives)


if __name__=='__main__':main()
