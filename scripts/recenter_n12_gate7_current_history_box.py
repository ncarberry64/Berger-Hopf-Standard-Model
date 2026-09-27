"""Evaluate a fresh history-flow box at the frozen current node-13 base.

Only this new box is evaluated. Frozen endpoint/history packets are read-only.
"""
import argparse
import json
from pathlib import Path
import time
import numpy as np
from flint import arb,arb_mat,ctx
import solve_n12_gate7_fiber_constrained_center as s
from certify_n12_gate7_coupled_center_neighborhood import load
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from checkpoint_n12_gate7_66d_tangent_binding import digest,encoded,FIXED
from bhsm.interface.arb_eigenpair_inclusion import verify_eigenpair_box


def recentered_eigenline(original):
    """Propose on the matrix midpoint, then prove the full new matrix box."""
    def evaluate(hessian,midpoint,reference):
        centered=np.array([v.mid() for v in hessian.flat],dtype=object).reshape(hessian.shape)
        vector,lam,gap,residual=original(centered,midpoint,reference)
        p=[v.mid() for v in vector];norm=sum((v*v for v in p),arb(0)).sqrt()
        p=[(v/norm).mid() for v in p];l=lam.mid();n=len(p)
        H=arb_mat(hessian[37:,37:].tolist());J=arb_mat(n+1,n+1)
        for i in range(n):
            for j in range(n):J[i,j]=H[i,j].mid()-(l if i==j else 0)
            J[i,n]=-p[i];J[n,i]=p[i]
        inv=J.inv();R=arb_mat(n+1,n+1,[v.mid() for v in inv.entries()])
        P=arb_mat(n,1,p);f=H*P-P*l
        F=arb_mat(n+1,1,f.entries()+[(P.transpose()*P)[0,0]/2-arb(1)/2])
        step=R*F
        for factor in (2,4,8,16):
            radii=[factor*abs(v).upper()+arb(2)**-400 for v in step.entries()]
            proposal=np.array([p[i]+arb(0,radii[i]) for i in range(n)],dtype=object)
            eigen=l+arb(0,radii[n])
            check=verify_eigenpair_box(hessian[37:,37:],proposal,eigen)
            if check['validation_passed']:
                return proposal,eigen,gap,residual
        error=ArithmeticError('fresh matrix-box normalized eigenpair inclusion failed')
        error.eigenpair_inclusion=check
        raise error
    return evaluate


def calculate(out,radius,descriptor_radius):
    ctx.prec=512;out.mkdir(parents=True,exist_ok=False)
    base=s.BASE/'gate7_coupled_fiber_center_20260927'
    center=load(base/'neighborhood/arrays.npz')['left_state_domain']
    with np.load(s.ROOT/FIXED) as z:
        weights=np.array([arb(float(v)) for v in z['state_weights']],dtype=object)
        reference=z['branch_reference']
    r=arb(radius);rs=arb(descriptor_radius)
    box=np.array([v+arb(0,r if i<98 else rs) for i,v in enumerate(center)],dtype=object)
    start=time.monotonic()
    print('Evaluating NEW current history box',radius,descriptor_radius,flush=True)
    report=dict(state_radius=radius,descriptor_radius=descriptor_radius,
        center_SHA256=digest(base/'neighborhood/arrays.npz'),frozen_derivatives_rerun=False,
        source_SHA256={p.relative_to(s.ROOT).as_posix():digest(p) for p in (
            Path(__file__),Path(s.__file__),Path(s.action.__file__),
            s.ROOT/FIXED,base/'neighborhood/arrays.npz',base/'uniform_inputs/report.json',
            s.ROOT/'src/bhsm/interface/arb_eigenpair_inclusion.py',
            s.ROOT/'src/bhsm/interface/physical_hs_value.py')},
        floating_gap_diagnostics_used_as_certificate=False,
        Gate7_closed=False,FULL_BHSM_COMPLETE=False)
    original=s.action._eigenline
    s.action._eigenline=recentered_eigenline(original)
    try:
        point=s.point(box,weights,reference,np.eye(99))
        save_arrays(out/'arrays.npz',dict(domain=box,center=center,rate=point['rate'],
            derivative=point['derivative'],covector=point['covector'],DC=point['DC']))
        report.update(status='NEW_CURRENT_HISTORY_FLOW_BOX_EVALUATED',
            eigenpair=point['eigenpair_proof'],descriptor_rate_positive=bool(point['rate'][98]>0),
            descriptor_rate=str(point['rate'][98]),
            arrays_SHA256=digest(out/'arrays.npz'))
    except (ArithmeticError,ValueError,ZeroDivisionError) as exc:
        report.update(status='NEW_BOX_ENCLOSURE_ATTEMPT_FAILED',error_type=type(exc).__name__,error=str(exc))
        if hasattr(exc,'eigenpair_inclusion'):report['eigenpair_attempt']=exc.eigenpair_inclusion
    finally:
        s.action._eigenline=original
    (out/'report.json').write_bytes(encoded(report))
    print(report['status'],report.get('error',report.get('descriptor_rate')),round(time.monotonic()-start,2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True)
    p.add_argument('--radius',default='1/36893488147419103232')
    p.add_argument('--descriptor-radius',default='1/1267650600228229401496703205376')
    a=p.parse_args();calculate(a.out,a.radius,a.descriptor_radius)
