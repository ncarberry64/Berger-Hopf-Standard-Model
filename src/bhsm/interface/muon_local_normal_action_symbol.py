"""Frozen chronological action density on the proper normal trace.

This applies the full local quadratic action to Fourier variations,
retaining every x/y equation and four named central radial frames.
It is a constant-coefficient application of a reached chronological
germ, not the time-dependent physical E0/event-domain operator.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_birth_finite_normal_boundary_action import load_completed_finite_normal_cell
from .muon_birth_chronological_normal_inertia import true_legendre_normal_trial
from .muon_birth_trace_enriched_action import generic_coordinate_lift
from .muon_birth_phase_continuation import _compressed_npz


def chronological_frequency_polynomial(hessian, dynamic_count):
    """Literal Fourier quadratic density, ordered (x,y), for v=i*omega*x.

    Axx=Lxx+i*omega*(Lxv-Lvx)+omega^2*Lvv,
    Axy=Lxy-i*omega*Lvy, Ayx=Lyx+i*omega*Lyv, Ayy=Lyy.
    For real symmetric L this is Hermitian at real omega. No integrated
    endpoint DtN or numerical duration enters this density identity.
    """
    H=np.asarray(hessian)
    n=int(dynamic_count);m=len(H)-2*n
    if (not np.isrealobj(H)or n<1 or m<1 or H.shape!=(2*n+m,)*2
            or not np.isfinite(H).all()):
        raise ValueError('complete finite real (x,v,y) action Hessian required')
    H=H.astype(float);xi=np.arange(n);vi=n+xi;yi=np.arange(2*n,2*n+m)
    ids=np.r_[xi,yi]
    A0=H[np.ix_(ids,ids)]
    A1=np.zeros_like(A0);A2=np.zeros_like(A0)
    A1[:n,:n]=H[np.ix_(xi,vi)]-H[np.ix_(vi,xi)]
    A1[:n,n:]=-H[np.ix_(vi,yi)];A1[n:,:n]=H[np.ix_(yi,vi)]
    A2[:n,:n]=H[np.ix_(vi,vi)]
    return dict(constant=A0,imaginary_linear=A1,quadratic=A2)


def frozen_normal_frequency_jet(hessian, normal_trace, frames, *, lapse):
    """Solve the complete bordered action polynomial through omega^2.

    The trace amplitude is one, all frame coefficients are zero. Coefficients
    z0,z1,z2 obey K0 z0=b, K0 z1=-i K1 z0,
    K0 z2=-i K1 z1-K2 z0. They are Taylor coefficients, not derivatives.
    For the action sign S2=1/2 integral dt(I_t*n_dot^2-R_t*n^2),
    R_t=-A_eff(0), I_t=[omega^2]A_eff; I_tau=l*I_t, R_tau=R_t/l.
    Original rows and frame reactions are retained, even when nonzero.
    """
    bnormal=np.asarray(normal_trace,float);C=np.asarray(frames,float)
    n=len(bnormal);p=chronological_frequency_polynomial(hessian,n);dim=len(p['constant'])
    if (C.ndim!=2 or C.shape[1]!=dim or not np.isfinite(C).all()
            or not np.isfinite(bnormal).all()or not np.isfinite(lapse)or lapse<=0):
        raise ValueError('finite same-field normal, named frames and positive clock required')
    T=np.vstack((np.r_[bnormal,np.zeros(dim-n)],C))
    K0=np.block([[p['constant'],T.T],[T,np.zeros((len(T),len(T)))]])
    K1=np.zeros_like(K0);K2=np.zeros_like(K0)
    K1[:dim,:dim]=p['imaginary_linear'];K2[:dim,:dim]=p['quadratic']
    row=np.max(abs(K0),axis=1)
    if np.any(row==0):raise np.linalg.LinAlgError('literal local bordered row is unbound')
    scale=1/np.sqrt(row);balanced=scale[:,None]*K0*scale[None,:]
    def solve(rhs):return scale*np.linalg.solve(balanced,scale*rhs)
    rhs=np.zeros(len(K0));rhs[dim]=1.
    z0=solve(rhs);z1=solve(-1j*K1@z0);z2=solve(-1j*K1@z1-K2@z0)
    response=np.array([-z0[dim],-z1[dim],-z2[dim]],complex)
    full=np.column_stack((z0,z1,z2))
    residual=np.column_stack((K0@z0-rhs,K0@z1+1j*K1@z0,
                              K0@z2+1j*K1@z1+K2@z0))
    # Removing ONLY the explicitly displayed frame reactions from a row
    # would hide a finite-representation failure. Export those rows intact.
    original=np.column_stack((p['constant']@z0[:dim]+T[0]*z0[dim],
        p['constant']@z1[:dim]+1j*p['imaginary_linear']@z0[:dim]+T[0]*z1[dim],
        p['constant']@z2[:dim]+1j*p['imaginary_linear']@z1[:dim]+p['quadratic']@z0[:dim]+T[0]*z2[dim]))
    return dict(action_polynomial_constant=p['constant'],action_polynomial_imaginary_linear=p['imaginary_linear'],
        action_polynomial_quadratic=p['quadratic'],bordered_constant=K0,bordered_imaginary_linear=K1,
        bordered_quadratic=K2,normal_and_frame_rows=T,response_taylor_coefficients=response,
        solution_taylor_coefficients=full,bordered_row_residual=residual,
        original_action_row_residual=original,frame_reaction_coefficients=full[dim+1:],
        normal_and_frame_constraint_coefficients=T@full[:dim],
        static_coordinate_action_pairing=float(response[0].real),
        coordinate_restoring_density=float(-response[0].real),
        coordinate_low_frequency_inertia=float(response[2].real),
        proper_restoring_density=float(-response[0].real/lapse),
        proper_low_frequency_inertia=float(lapse*response[2].real),
        response_imaginary_residue_max=float(np.max(abs(response.imag))),
        response_linear_coefficient_abs=float(abs(response[1])),
        balanced_constant_condition=float(np.linalg.cond(balanced)),
        original_Lyy_retained=True,spectral_directions_removed=0,
        local_density_identity='S2=1/2 int dt(I_t n_dot^2-R_t n^2); A_eff(omega)=omega^2 I_t-R_t+...',
        proper_clock_identity='d_tau=l d_t; A_tau(omega_tau)=A_t(l omega_tau)/l',
        physical_local_R_I_or_drive_c_selected=False)


def local_chronological_normal_symbol(phase_directory, *, repository=ROOT):
    """Bind saved full action, its proper normal and literal central frames."""
    a=load_completed_finite_normal_cell(phase_directory,repository=repository)
    rep=a['representation'];raw=a['raw'];H=a['arrays']['stage_action_hessian'][0]
    g=a['arrays']['stage_action_gradient'][0]
    c=generic_coordinate_lift(rep['gauge_labels']);n=c['x_count'];m=c['y_count']
    kinetic=true_legendre_normal_trial(H,raw,rep)
    labels=rep['gauge_labels']
    Ar=[j for j,i in enumerate(c['dynamic_gauge_indices'])
        if labels[i]['field']=='A_rho'and labels[i]['internal']==3]
    if len(Ar)!=4:raise ValueError('all four retained enriched central radial coordinates required')
    frames=np.zeros((4,n+m));frames[np.arange(4),38+np.array(Ar)]=1.
    stored=frozen_normal_frequency_jet(H,kinetic['proper_normal_trace'],frames,lapse=kinetic['induced_lapse'])
    # The exact quadratic form of a stored real matrix uses its symmetric
    # part. This is an explicit action-pairing identity, not regularization.
    quadratic=frozen_normal_frequency_jet((H+H.T)/2,kinetic['proper_normal_trace'],frames,
                                        lapse=kinetic['induced_lapse'])
    return dict(base=a,stored=stored,quadratic=quadratic,stored_action_hessian=H,
        quadratic_action_hessian=(H+H.T)/2,antisymmetric_producer_rounding=H-H.T,
        stored_action_gradient=g,proper_normal_trace=kinetic['proper_normal_trace'],
        named_central_radial_frame=frames,induced_lapse=kinetic['induced_lapse'],
        actual_base_primal_Euler_time_derivative_not_computed=True)


def materialize_local_chronological_normal_symbol(phase_directory,output, *, repository=ROOT):
    root=Path(repository);out=Path(output);out=out if out.is_absolute()else root/out
    if out.exists():raise FileExistsError('preserve earlier local density applications')
    a=local_chronological_normal_symbol(phase_directory,repository=root)
    arrays={k:v for k,v in a.items()if isinstance(v,np.ndarray)};rows={}
    for name in ('stored','quadratic'):
        b=a[name];arrays.update({name+'_'+k:v for k,v in b.items()if isinstance(v,np.ndarray)})
        rows[name]={k:v for k,v in b.items()if not isinstance(v,np.ndarray)}
        for key in ('bordered_row_residual','original_action_row_residual','frame_reaction_coefficients'):
            rows[name][key+'_max']=float(np.max(abs(b[key])))
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    refs=dict(a['base']['input_hashes'])
    for name in ('muon_local_normal_action_symbol','muon_birth_finite_normal_boundary_action',
                 'muon_birth_chronological_normal_inertia','muon_birth_trace_enriched_action'):
        p='src/bhsm/interface/'+name+'.py';refs[p]=sha256((root/p).read_bytes()).hexdigest()
    md=dict(classification='EVALUATED_FULL_FIELD_FROZEN_CHRONOLOGICAL_NORMAL_ACTION_SYMBOL',
        input_hashes=refs,numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        side=a['base']['receipt']['side'],action_parameters=a['base']['receipt']['action_parameters'],
        induced_lapse=a['induced_lapse'],dynamic_count=len(a['proper_normal_trace']),algebraic_count=40,
        applications=rows,antisymmetric_producer_rounding_max=float(np.max(abs(a['antisymmetric_producer_rounding']))),
        representation_frame='all four named central A_rho coordinate slices; original rows and reactions retained',
        frozen_density_not_endpoint_DtN_divided_by_duration=True,
        scope='constant-coefficient local quadratic germ of the reached full chronological action, not its time-varying E0/event boundary reduction',
        time_varying_base_connection_and_domain_not_frozen_physically=True,
        negative_incoming_pairing_not_identified_as_event_drive=True,
        physical_delta_impedance_identity_or_formation_c_or_Pauli_selected=False,
        error_scope='binary64 complete stored action polynomial solves; producer rounding, frozen-coefficient and continuum/domain errors not rigorously enclosed')
    (out/'result.json').write_text(json.dumps(md,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return md


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phase-directory',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(materialize_local_chronological_normal_symbol(a.phase_directory,a.output),sort_keys=True))
