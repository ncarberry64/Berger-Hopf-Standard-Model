"""Current temporal force-source contraction from frozen normal/reset data."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb, arb_mat, ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from evaluate_n12_gate7_current_contractions import packet, scalar, SHARED, LOCAL, FRAME, BASE
from checkpoint_n12_gate7_66d_tangent_binding import restore, bound, encoded, digest
from differentiate_n12_gate7_fiber_constrained_center import save_arrays
from bhsm.interface.aether_forward_c2_descriptor_cover import metric_data
from bhsm.interface.temporal_action_residual import descriptor_euler_residual, temporal_source

POINT=BASE/'gate7_current_formation_stationarity_20260927/run1'


def block(a, rows, cols):
    return arb_mat([[a[i,j] for j in cols] for i in rows])


def calculate(out):
    ctx.prec=512
    if out.exists():raise ValueError('new output directory required')
    sr,z=packet(SHARED);lr,l=packet(LOCAL);fr,f=packet(FRAME);pr,p=packet(POINT)
    for folder in (LOCAL,FRAME,POINT):
        path=(folder/'arrays.npz').relative_to(ROOT).as_posix()
        if digest(ROOT/path)!=sr['source_SHA256'][path]:raise ValueError('mixed-base packet '+path)
    Y=restore(z,'current_raw_state');Q=restore(f,'Q66_current_raw')
    QA=restore(f,'Q66_current');weights=restore(f,'action_coordinate_weights')
    qw,zw,*_=metric_data()
    owned_weights=list(qw)+list(zw)
    if any(weights[i,0]!=arb(float(w)) for i,w in enumerate(owned_weights)):
        raise ValueError('owner raw/action coordinate conversions differ')
    g=restore(l,'local_action_gradient_raw')
    psi=restore(z,'selected_eigenline');h=restore(z,'hard_response')
    s=restore(z,'current_descriptor')[0,0];lam=restore(z,'selected_eigenvalue')[0,0]
    scalars=restore(z,'internal_scalars');b=scalars[1,0];norm=scalars[4,0]
    Dn=restore(z,'local_internal_internal_first');F=restore(z,'local_internal_residual')
    Fn=restore(z,'local_internal_internal_jacobian');Fx=restore(z,'local_internal_input_partial')
    dF=Fn*Dn+Fx
    ds=restore(z,'current_descriptor_first_66')
    dl=block(Dn,[61],range(66));db=block(Dn,[123],range(66))
    dp=block(Dn,range(61),range(66));dh=block(Dn,range(62,123),range(66))
    v=block(Y,range(37,74),[0]);dv=block(Q,range(37,74),range(66))
    rawG=arb_mat((s*v).tolist()+(b*psi+s*h).tolist())
    rawDG=arb_mat((v*ds+s*dv).tolist()+(psi*db+b*dp+h*ds+s*dh).tolist())
    G=arb_mat(98,1,[weights[i,0]*rawG[i,0] for i in range(98)])
    DG=arb_mat(98,66,[weights[i,0]*rawDG[i,j] for i in range(98) for j in range(66)])
    reconstructed_norm=(G.transpose()*G)[0,0].sqrt()
    dnorm=G.transpose()*DG/norm
    rawrate=rawG/norm;drawrate=(rawDG-rawrate*dnorm)/norm
    saved=restore(z,'augmented_rate');savedfirst=restore(z,'augmented_rate_first_66')
    replays=dict(norm=arb_mat([[reconstructed_norm-norm]]),
        normalized_rate=arb_mat(98,1,[G[i,0]/norm-saved[i,0] for i in range(98)]),
        normalized_rate_first=arb_mat(98,66,[weights[i,0]*drawrate[i,j]-savedfirst[i,j] for i in range(98) for j in range(66)]),
        state=Y-restore(l,'current_incoming_state_raw'))
    E=descriptor_euler_residual(s=s,lam=lam,b=b,psi=psi,hard=h,norm=norm,
        eigen_residual=block(F,range(61),[0]),hard_residual=block(F,range(62,123),[0]),
        ds=ds,dlam=dl,db=db,dpsi=dp,dhard=dh,dnorm=dnorm,
        deigen_residual=block(dF,range(61),range(66)),dhard_residual=block(dF,range(62,123),range(66)))
    # Reconstruct the stored H and rhs from their exact owner-defined blocks;
    # this independently contracts H*G_z-s*rhs before using the short identity.
    H=block(Fn,range(61),range(61))+arb_mat([[lam if i==j else 0 for j in range(61)] for i in range(61)])
    rhs=(H-lam*arb_mat(np.eye(61,dtype=int).tolist()))*h+b*psi-block(F,range(62,123),[0])
    direct=(H*(b*psi+s*h)-s*rhs)/norm
    replays['Euler_direct_short']=direct-E['value']
    gm=block(g,range(74,98),[0])
    C=restore(p,'E1_constraints');DC=restore(p,'E1_constraint_J')
    dgm=block(DC,range(24),range(98))*QA
    for i in range(24):
        for j in range(66):dgm[i,j]*=weights[74+i,0]
    replays['multiplier_constraint_value']=arb_mat(24,1,[gm[i,0]-weights[74+i,0]*C[i,0] for i in range(24)])
    pi=block(g,range(37,74),[0])
    attached_time=restore(l,'local_action_value')[0,0]-(pi.transpose()*v)[0,0]
    replays['attached_time_energy']=arb_mat([[attached_time+C[24,0]]])
    nu=s/norm;dnu=(ds-nu*dnorm)/norm
    source=temporal_source(qdim=37,euler_residual=E['value'],deuler_residual=E['first'],
        multiplier_gradient=gm,multiplier_gradient_first=dgm,velocity=v,velocity_first=dv,
        multiplier_arc_rate=block(rawrate,range(74,98),[0]),
        multiplier_arc_first=block(drawrate,range(74,98),range(66)),clock=nu,clock_first=dnu)
    if not all(v.contains(0) for m in replays.values() for v in m.entries()):
        raise ArithmeticError('frozen owner/coordinate replay failed')
    arrays={**{'Euler_'+k:v for k,v in E.items()},**{'source_'+k:v for k,v in source.items()},
        **{'replay_'+k:v for k,v in replays.items()},
        'source_Q66_at_fixed_arc_and_time':source['state'].transpose()*Q,
        'attached_terminal_momentum_pullback_66':pi.transpose()*block(Q,range(37),range(66)),
        'attached_terminal_time_covector':arb_mat([[attached_time]]),
        'coordinate_clock':arb_mat([[nu]]),'coordinate_clock_first_66':dnu}
    out.mkdir(parents=True)
    save_arrays(out/'arrays.npz',arrays)
    sources=[Path(__file__),ROOT/'src/bhsm/interface/temporal_action_residual.py',
             ROOT/'src/bhsm/interface/aether_forward_c2_descriptor_cover.py',
             ROOT/'scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py',
             ROOT/'scripts/derive_n12_gate7_formation_stationarity_inputs.py',
             ROOT/'src/bhsm/interface/current_incoming_formation_family.py',
             ROOT/'scripts/evaluate_n12_gate7_current_contractions.py']
    for folder in (SHARED,LOCAL,FRAME,POINT):sources.extend([folder/'arrays.npz',folder/'report.json'])
    report=dict(status='CURRENT_TEMPORAL_ACTION_RESIDUAL_AND_FIRST_SOURCE_CONTRACTED',
        base_commit='d77e0b2a77b5fe93b0602aee78149e1343cb0101',
        existing_obligation='Projected same-action force; classical action endpoint/residual representation',
        exact_consumed_term='[pi*dq+(L-pi*v)*dt]_ends + integral source*(dY_arc,dt_arc) d_arc',
        force_accounting='Attached-action endpoints + attached-action residual integral + signed heat-minus-zeta contraction. Do not mix the classical-only time covector from the prior packet into this representation.',
        coordinates='State sources are raw (q37,v37,m24) dual covectors; 66 first columns use the frozen action-metric Q66; t is coordinate time',
        smaller_representation='Current source and its 66 first derivatives from frozen normal equations; no new action Hessian or stored trajectory',
        owner_identities=dict(H='raw 61x61 velocity/multiplier Hessian',
            normal='(H-lambda I)psi=0; (H-lambda I)h+b psi=rhs',
            clock='dt/d_arc=s/norm_G, with its actual sign',
            rate='G_raw=(s*v,b*psi+s*h); rate_raw=G_raw/norm_G',
            residual='(H*(b*psi+s*h)-s*rhs)/norm_G',
            first37='D_arc pi-(dt/d_arc)*L_q',last24='D_arc L_m',
            on_fiber='s^2*h/norm_G plus explicitly retained solve residuals'),
        Euler_residual=bound(E['value']),Euler_residual_first=bound(E['first']),
        selected_fiber_term=bound(E['selected_fiber_term']),
        off_fiber_and_solve_terms=bound(E['off_fiber_and_solve_terms']),
        state_source=bound(source['state']),state_source_first=bound(source['state_first']),
        time_source=bound(source['time']),time_source_first=bound(source['time_first']),
        fixed_time_Q66_source=bound(arrays['source_Q66_at_fixed_arc_and_time']),
        attached_terminal_time_covector=scalar(attached_time),
        coordinate_clock=scalar(nu), replays={k:bound(v) for k,v in replays.items()},
        source_is_pointwise=True,uniform_source_enclosure=None,integrated_force=None,
        delta_time_endpoint_not_assumed_zero=True,
        exact_Euler_Lagrange_stationarity_not_assumed=True,
        selected_descriptor_replaced_by_zero=False,
        current_rate_modified=False,new_action_or_history_producer_calls=0,
        q66=None,Gate7_closed=False,FULL_BHSM_COMPLETE=False,
        source_SHA256={p.relative_to(ROOT).as_posix():digest(p) for p in sources},
        arrays_SHA256=digest(out/'arrays.npz'))
    (out/'report.json').write_bytes(encoded(report))
    for obj in (z,l,f,p):obj.close()
    print(json.dumps({k:report[k] for k in ['status','Euler_residual','Euler_residual_first','state_source','time_source','fixed_time_Q66_source']},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);calculate(p.parse_args().out)
