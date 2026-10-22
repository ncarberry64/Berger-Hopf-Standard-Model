"""Action-normalized local deformation information, never a forced detection."""
import numpy as np

def assess_envelope(data,engine,parameters,baseline_jacobian,predictions,physics):
    if not physics['allowed_physics_models'].get('r1_boundary_conditional'):
        return {'status':'NOT_ADMITTED','reasons':physics.get('reasons',[])}
    massratio=parameters['mass_msun']/engine.ref_mass
    center=np.asarray(parameters['center_mas'])+(data.epochs-data.t0)[:,None]*np.asarray(parameters['proper_motion_mas_yr'])+engine.parallax
    x=(predictions[:,:4].reshape(data.n,2,2)-center[:,None,:])/engine.theta
    args=(massratio,parameters['shear'],parameters['compact_quad'],parameters['convergence'],parameters['flux_ratio'])
    p0,g0,H0=engine.potential(x,*args)
    A=np.eye(2)-H0
    columns=[]
    for j in range(3):
        bc=np.eye(3)[j]
        p,g,H=engine.potential(x,*args,boundary=bc)
        p-=p0;g-=g0;H-=H0
        dx=np.linalg.solve(A,g[...,None])[...,0]
        # Symmetric directional derivative of the base Hessian, with an
        # annulus-relative step. This differentiates a unit response; it
        # never injects an enlarged physical scalar boundary state.
        scale=np.maximum(np.linalg.norm(dx,axis=-1),1e-100)
        h=1e-4*np.linalg.norm(x,axis=-1)/scale
        hp=engine.potential(x+h[...,None]*dx,*args)[2]
        hm=engine.potential(x-h[...,None]*dx,*args)[2]
        DH=(hp-hm)/(2*h[...,None,None])
        logs=np.trace(np.linalg.solve(A,H+DH),axis1=-2,axis2=-1)
        col=np.column_stack([(dx*engine.theta).reshape(data.n,4),logs[:,0]-logs[:,1],(p[:,0]-p[:,1])*engine.time])
        columns.append(data.whiten(col.ravel()))
    S=np.column_stack(columns)
    # The axial component is a nuisance, matching the finite-family paper.
    N=np.column_stack([baseline_jacobian,S[:,2]])
    norms=np.linalg.norm(N,axis=0);keep=norms>max(np.max(norms),1)*1e-12
    U,s,V=np.linalg.svd(N[:,keep]/norms[keep],full_matrices=False)
    rank=int(np.sum(s>s[0]*1e-8))
    R=S[:,:2]-U[:,:rank]@(U[:,:rank].T@S[:,:2])
    ur,sr,vr=np.linalg.svd(R,full_matrices=False)
    envelope_rank=int(np.sum(sr>max(sr[0],1)*1e-8))
    cap=physics['boundary_state']['amplitude_norm_max']
    best_snr=float(cap*sr[0]);worst_snr=float(cap*sr[-1])
    residual=data.whiten((data.observations-predictions).ravel())
    estimate=np.linalg.pinv(R,rcond=1e-8)@residual
    status='UNRESOLVED' if best_snr<1 or envelope_rank<2 else 'INFORMATION_AVAILABLE'
    return {'status':status,'boundary_amplitude_cap':cap,'cap_definition':'uniform sufficient retained-action admission bound; not a selected astrophysical amplitude',
       'rank':envelope_rank,'nuisance_rank':rank,'projected_singular_values_per_boundary_amplitude':sr.tolist(),
       'unconstrained_local_amplitude_estimate':estimate.tolist(),
       'unconstrained_estimate_inside_admitted_ball':bool(np.linalg.norm(estimate)<=cap),
       'maximum_admitted_local_snr':best_snr,'worst_orientation_admitted_local_snr':worst_snr,
       'all_admitted_states_below_unit_snr':bool(best_snr<1),
       'interpretation':'Local GLS information after source/lens and axial profiling. Outside-cap unconstrained estimates are not physical R1 state measurements. No horizon/detection claim.',
       'normalization':'unit L2 scalar Dirichlet amplitudes; one metric response; same supplied covariance',
       'derivative_accuracy':'symmetric base-Hessian directional derivative at relative annulus step1e-4'}
