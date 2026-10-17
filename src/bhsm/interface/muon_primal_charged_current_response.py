"""Charged-current applications of the actual full assigned-action cells.

The source is a formal fermion bilinear derivative, not a chosen spinor or
CAR state. All midpoint Euler/Gauss rows remain in the solve. The finite
current response is not automatically the low-energy LSZ Fermi coefficient.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from scipy.linalg import solve
from flint import arb,arb_mat,ctx

from .muon_parent_gauge_geometry_correction import ROOT,correction_representation
from .muon_parent_mean_causal_action import mean_coordinate_lift,VOLUME
from .muon_parent_retarded_hypercharge import WALL,ALPHA,regular_radial_basis
from .muon_primal_intrinsic_lepton_operator import primal_intrinsic_lepton_operator


def charged_current_matrices(family=1):
    """HS-normalized Hermitian coordinates of the owned T+/- current.

    X_(a,mu)=sigma_a/√2 tensor P_family tensor sigma_mu/√2 on L_L;
    a=1,2, mu=0..3. (X1+iX2)/√2=T+ tensor P_f tensor sigma_mu/√2.
    They are bilinear coefficient directions, not external LSZ modes.
    """
    if type(family) is not int or family not in (0,1,2):raise ValueError('retained family index0..2 required')
    spin=np.array([np.eye(2),[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
    pf=np.zeros((3,3));pf[family,family]=1
    result=np.zeros((8,18,18),complex)
    for a in range(2):
        for mu in range(4):result[4*a+mu,:12,:12]=np.kron(np.kron(spin[a+1]/np.sqrt(2),pf),spin[mu]/np.sqrt(2))
    return result


def charged_current_action_source(raw,representation,family=1):
    """Differentiate S_chi=chi†(i∂t-N H_can)chi at fixed canonical chi.

    The constant angular carrier is normalized1/√(2pi²), so its intrinsic
    Haar integral is one. N is in the source; no second Haar or N factor is
    inserted in the finite temporal readout. Current Gram I18 is separate
    from an interacting LSZ residue. Material At is counted once.
    """
    app=primal_intrinsic_lepton_operator(raw,representation)
    dN=app['proper_time_Haar_measure_first_jet']/VOLUME
    vertex=-app['N']*app['H_can_raw_first_jet']-dN[:,None,None]*app['H_can']
    X=charged_current_matrices(family)
    traces=np.einsum('aij,rji->ra',X,vertex)
    if np.max(abs(traces.imag))>1e-11*max(1.,float(np.max(abs(traces)))):raise ValueError('Hermitian charged current requires real source cotangents')
    P=mean_coordinate_lift(representation['gauge_labels'])['lift']
    source=traces.real
    return dict(raw_source=source,master_source=P.T@source,current_matrices=X,
        coordinate_time_source_operators=vertex,lepton_application=app,
        source_order='X1 spinI,sigma1,sigma2,sigma3; X2 same; HS normalized',
        constant_angular_Haar_volume_reapplied=False,physical_external_state_selected=False)


def central_gauge_profile_coefficients():
    """Retained analytic radial gauge profiles and derivative coefficients.

    At/Ar both span x^alpha P2. theta=x^(alpha+1),x^(alpha+2) and theta'
    lie in those spaces. This identifies a representable U1 gauge family;
    it does not identify a null direction by a small singular vector.
    """
    x=np.array([.2,.5,.8]);B,_=regular_radial_basis(WALL*x,2)
    theta=x[:,None]**(ALPHA+np.array([1.,2.]))
    derivative=(ALPHA+np.array([1.,2.]))[None,:]*x[:,None]**(ALPHA+np.array([0.,1.]))/WALL
    T=np.linalg.solve(B,theta);D=np.linalg.solve(B,derivative)
    check_x=np.array([.07,.31,.62,.93,1.]);C,_=regular_radial_basis(WALL*check_x,2)
    t_error=float(np.max(abs(C@T-check_x[:,None]**(ALPHA+np.array([1.,2.])))))
    d_error=float(np.max(abs(C@D-(ALPHA+np.array([1.,2.]))[None,:]*check_x[:,None]**(ALPHA+np.array([0.,1.]))/WALL)))
    if max(t_error,d_error)>2e-12:raise ValueError('analytic central gauge profiles must remain in the retained radialband')
    return dict(theta_coefficients=T,radial_derivative_coefficients=D,
        profile_reconstruction_absolute_error=max(t_error,d_error),
        exact_functional_identity='theta=x^(alpha+1),x^(alpha+2); theta_r=(alpha+1)x^alpha/WALL,(alpha+2)x^(alpha+1)/WALL')


def source_midpoint_rows(master_source,step):
    """Derivative of the SAME midpoint equations for a scalar action load."""
    b=np.asarray(master_source,float)
    if b.ndim!=2 or b.shape[0]!=216 or not np.isfinite(b).all() or not np.isfinite(step) or step==0:raise ValueError('finite full x90/v90/y36 source and oriented step required')
    return np.vstack((np.zeros_like(b[:90]),-step*b[:90],b[90:180],b[180:]))


def exact_stored_bordered_pairing(K,forcing,readout,*,precision_bits=192):
    """Arb solve and adjoint identity for the exact supplied binary64 system.

    Matrix/source formation and physical domain errors are excluded. The
    original stored K is converted directly, avoiding rounded preconditioner
    products as a replacement operator.
    """
    if type(precision_bits) is not int or precision_bits<128:raise ValueError('explicit Arb precision>=128 required')
    K=np.asarray(K,float);f=np.asarray(forcing,float);L=np.asarray(readout,float)
    if K.ndim!=2 or K.shape[0]!=K.shape[1] or f.ndim!=2 or f.shape[0]!=len(K) or L.ndim!=2 or L.shape[1]!=len(K):
        raise ValueError('complete stored matrix, forcing and readout required')
    if not all(np.isfinite(a).all() for a in (K,f,L)):raise ValueError('finite stored coefficients required')
    previous=ctx.prec
    try:
        ctx.prec=precision_bits
        A=arb_mat(K.tolist());F=arb_mat(f.tolist());R=arb_mat(L.tolist())
        z=A.solve(F);adj=A.transpose().solve(R.transpose())
        if not all(z[i,j].is_finite() for i in range(z.nrows()) for j in range(z.ncols())):raise RuntimeError('full bordered system not certified invertible')
        forward=R*z;backward=adj.transpose()*F
        overlap=all(forward[i,j].overlaps(backward[i,j]) for i in range(forward.nrows()) for j in range(forward.ncols()))
        if not overlap:raise RuntimeError('exact stored source/adjoint intervals disagree')
        upper=lambda x:float(np.nextafter(float(x.upper()),np.inf)) if not x.is_zero() else 0.
        lower=lambda x:float(np.nextafter(float(x.lower()),-np.inf)) if not x.is_zero() else 0.
        numeric=np.array([[float(z[i,j].mid()) for j in range(z.ncols())] for i in range(z.nrows())])
        errors=np.array([[upper(abs(z[i,j]-arb(float(numeric[i,j])))) for j in range(z.ncols())] for i in range(z.nrows())])
        residual=A*z-F
        return dict(response=numeric,response_export_error_upper=errors,
            paired_current_lower=np.array([[lower(forward[i,j]) for j in range(forward.ncols())] for i in range(forward.nrows())]),
            paired_current_upper=np.array([[upper(forward[i,j]) for j in range(forward.ncols())] for i in range(forward.nrows())]),
            source_adjoint_intervals_overlap=overlap,
            exact_stored_bordered_residual_upper=max(upper(abs(residual[i,j])) for i in range(residual.nrows()) for j in range(residual.ncols())),
            exact_stored_source_adjoint_difference_upper=max(upper(abs(forward[i,j]-backward[i,j])) for i in range(forward.nrows()) for j in range(forward.ncols())),
            precision_bits=precision_bits,physical_action_or_current_source_formation_error_enclosed=False)
    finally:ctx.prec=previous


def bordered_current_response(jacobian,master_source,step,representation,*,frame='temporal'):
    """Retain all306 original rows with2 explicit central-frame constraints.

    Two auxiliary Gauss loads make any incompatibility visible. Their
    reaction is never discarded. No pseudoinverse or eigenvector deletion
    occurs. Comparing named frames tests the consumed current contraction.
    Arithmetic is binary64, not a certified physical gauge quotient.
    """
    J=np.asarray(jacobian,float);b=np.asarray(master_source,float)
    if J.shape!=(306,306) or not np.isfinite(J).all():raise ValueError('actual complete306 midpoint Jacobian required')
    if frame not in ('temporal','radial'):raise ValueError('named temporal or radial central frame required')
    labels=representation['gauge_labels'];coords=mean_coordinate_lift(labels);profiles=central_gauge_profile_coefficients()
    at=[j for j,i in enumerate(coords['At_indices']) if labels[i]['internal']==3]
    ar=[j for j,i in enumerate(coords['dynamic_gauge_indices']) if labels[i]['field']=='A_rho' and labels[i]['internal']==3]
    if len(at)!=3 or len(ar)!=3:raise ValueError('full radial2 central At/Ar coordinates required')
    R=np.zeros((306,2));R[270+24+np.array(at)]=profiles['theta_coefficients']
    C=np.zeros((2,306))
    if frame=='temporal':C[:,270+24+np.array(at)]=profiles['theta_coefficients'].T
    else:C[:,180+38+np.array(ar)]=profiles['radial_derivative_coefficients'].T
    K=np.block([[J,R],[C,np.zeros((2,2))]])
    forcing=source_midpoint_rows(b,step);rhs=np.vstack((-forcing,np.zeros((2,b.shape[1]))))
    row=1/np.maximum(np.max(abs(K),axis=1),np.finfo(float).tiny)
    col=1/np.maximum(np.max(abs(row[:,None]*K),axis=0),np.finfo(float).tiny)
    A=row[:,None]*K*col[None,:]
    response=col[:,None]*solve(A,row[:,None]*rhs,assume_a='gen')
    phase=response[:306];reaction=response[306:]
    eta=np.vstack((phase[:90]/2,phase[180:270],phase[270:]))
    target=step*b.T@eta
    # Exact algebraic transpose of this bordered finite system, not an
    # independently invented advanced endpoint or an instantaneous inverse.
    readout=np.zeros((b.shape[1],308));readout[:,:90]=step*b[:90].T/2
    readout[:,180:270]=step*b[90:180].T;readout[:,270:306]=step*b[180:].T
    adjoint=row[:,None]*solve(A.T,col[:,None]*readout.T,assume_a='gen')
    adjoint_target=adjoint.T@rhs
    original_residual=J@phase+forcing
    all_residual=K@response-rhs
    certified=exact_stored_bordered_pairing(K,rhs,readout)
    return dict(response_unknowns=phase,midpoint_response=eta,auxiliary_Gauss_reaction=reaction,
        paired_current_response=target,adjoint_paired_current_response=adjoint_target,
        original306_residual=original_residual,bordered_residual=all_residual,
        original306_residual_norm=float(np.linalg.norm(original_residual)),
        scaled_bordered_residual_norm=float(np.linalg.norm(row[:,None]*all_residual)),
        auxiliary_Gauss_reaction_norm=float(np.linalg.norm(reaction)),
        frame_condition_residual_norm=float(np.linalg.norm(C@phase)),
        source_adjoint_pairing_absolute_difference=float(np.linalg.norm(target-adjoint_target)),
        balanced_condition_number=float(np.linalg.cond(A)),
        exact_stored_certificate=certified,
        frame=frame,frame_matrix=C,auxiliary_Gauss_column=R,
        central_profiles=profiles,pseudoinverse_used=False,original_Gauss_rows_dropped=False,
        scalar_local_fermi_coefficient_assigned=False,physical_gauge_quotient_certified=False)


def retained_current_response(repository=ROOT):
    """Apply actual sources to the unchanged saved full-action Jacobians."""
    root=Path(repository);base='artifacts/muon_parent_gauge_geometry_correction_20261010';records=[];results=[]
    rep=correction_representation(radial_points=48,cap_points=48,radial_order=2,include_wall_lift=True,include_scalar_mean=True)
    for side in ('incoming','outgoing'):
        folder=root/base/f'full_midpoint_{side}_run_1';raw=(folder/'result.json').read_bytes();receipt=json.loads(raw)
        data=(folder/'application.npz').read_bytes()
        if sha256(data).hexdigest()!=receipt['numerical_sha256']:raise ValueError('actual current background archive changed')
        for name,digest in receipt['input_hashes'].items():
            if sha256((root/name).read_bytes()).hexdigest()!=digest:raise ValueError('same action source changed: '+name)
        records.extend(dict(path=str((folder/name).relative_to(root)).replace('\\','/'),bytes=len(blob),sha256=sha256(blob).hexdigest())
            for name,blob in (('result.json',raw),('application.npz',data)))
        with np.load(folder/'application.npz',allow_pickle=False) as archive:
            a={key:archive[key].copy() for key in archive.files}
        source=charged_current_action_source(a['updated_midpoint_raw'],rep)
        electron=charged_current_action_source(a['updated_midpoint_raw'],rep,family=2)
        family_difference=float(np.linalg.norm(source['raw_source']-electron['raw_source']))
        outputs=[bordered_current_response(a['updated_jacobian'],source['master_source'],receipt['step'],rep,frame=frame)
            for frame in ('temporal','radial')]
        difference=float(np.linalg.norm(outputs[0]['paired_current_response']-outputs[1]['paired_current_response']))
        results.append(dict(side=side,oriented_step=receipt['step'],action_parameters=receipt['action_parameters'],
            raw_fields=a['updated_midpoint_raw'],source=source,applications=outputs,
            charged_family_source_difference=family_difference,
            named_frame_pairing_absolute_difference=difference,
            numerical_background_residual=float(np.linalg.norm(a['updated_residual'])),
            local_g2_over_MW_squared_substituted=False,physical_Fermi_coefficient=None,
            source_profile_scope='one assigned midpoint current load; response operator application, not a selected decay current or lifetime'))
    return dict(classification='EVALUATED_CHARGED_CURRENT_RESPONSE_ON_ACTUAL_FULL_ASSIGNED_ACTION_CELLS',
        input_records=records,arms=results,current_owner='ae31_c2_coexact_su2l_charged_current.weak_charged_representation_ledger',
        unit_generator_identity='H_a=-iT_a/sqrt2; A+=(A1-iA2)/sqrt2 gives Omega_charged=-i(A+T++A-T-)/2',
        current_pairing='HS-normalized formal charged bilinear; canonical current GramI18; constant angular harmonic1/sqrt(2pi²)',
        scale_equation='GF=c_F/E_kappa^2 after the same-action low-energy LSZ decay contraction',
        physical_c_F=None,E_kappa_GeV=None,interacting_LSZ_or_low_energy_local_projection_evaluated=False,
        native_Pauli_evaluated=False,error_scope='binary64 actual finite-action source and bordered solve; residual/reaction/frame differences retained; no continuum or producer-rounding enclosure')
