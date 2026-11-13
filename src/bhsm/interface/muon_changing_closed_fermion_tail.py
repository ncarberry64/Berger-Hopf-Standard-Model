"""Apply the retained even-Y certificate to the changing chronological target.

Arb certifies the exact stored finite pencil and parity. Primitive norm
bounds include the generalized Gram derivative and affine phase pullback.
Production of entries, quadrature, continuum and matching remain separate.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import eigh
from .muon_native_even_y_remainder_certificate import certify_generalized_even_pencil,even_y_tail_bounds
from .muon_native_mean_core_heat_target import _unit_lepton_mass6,_stored_frobenius_upper
from .muon_profile_preserving_phase_sample import profile_preserving_lepton_sample
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_source_directed_temporal_green import source_product_temporal_values
from .muon_primal_native_phase_adjoint import native_phase_midpoint_map,native_phase_named_border,native_phase_load_rows,chronological_native_phase_jacobian


def changing_heat_tail_application(phase,weak_P0,weak_P1,weak_P2,Gram,mean_load,*,cutoff,quadrature_order=16,precision_bits=192):
    """Enclose higher even-Y finite-target and chronological contact terms."""
    K,C,B,G=(np.asarray(x,complex)for x in (weak_P0,weak_P1,weak_P2,Gram))
    if any(a.shape!=(48,48)for a in (K,C,B,G))or phase['receipt']['steps']!=1:
        raise ValueError('actual complete changing n0/C6 temporal8 pencil required')
    signs=np.tile([1,1,1,1,-1,-1],8)
    lam,U=eigh(K,G)
    constants,certificate=certify_generalized_even_pencil(K,C,B,G,U,lam,signs,precision_bits=precision_bits)
    L=abs(phase['receipt']['span']);z,w=np.polynomial.legendre.leggauss(quadrature_order)
    times=np.concatenate(((z+1)*L/4,(z+3)*L/4));weights=np.tile(w*L/4,2)
    tf=source_product_temporal_values(times,L)
    samples=[];fi=np.array([2,3,8,9,14,15]);S=np.diag([1]*4+[-1]*2)
    for u in times:
        t=float(u-L if phase['receipt']['side']=='incoming'else u)
        op=profile_preserving_lepton_sample(phase,t)['operator']
        A=op['W'][np.ix_(fi,fi)]+op['Omega_tau'][np.ix_(fi,fi)]
        dA=op['W_raw_first_jet'][:,fi][:,:,fi]+op['Omega_tau_raw_first_jet'][:,fi][:,:,fi]
        A=(A+S@A@S)/2;dA=(dA+np.einsum('ij,bjk,kl->bil',S,dA,S))/2
        M=_unit_lepton_mass6(op['H']);dM=np.zeros((268,6,6),complex)
        dM[260:264]=np.array([_unit_lepton_mass6(H)for H in ([1,0],[0,1],[1j,0],[0,1j])])
        if np.any(S@M@S+M)or np.any(np.einsum('ij,bjk,kl->bil',S,dM,S)+dM):
            raise ValueError('action variation lost inherited exact even-Y grading')
        N=op['N'];dN=N*op['proper_time_Haar_measure_first_jet']/op['proper_time_Haar_measure']
        samples.append(dict(t=t,N=N,dN=dN,A=A,dA=dA,M=M,dM=dM))
    from scipy.linalg import cholesky,solve_triangular
    Gt=np.einsum('t,t,ta,tb->ab',weights,np.array([a['N']for a in samples]),tf['value'],tf['value'])
    T=solve_triangular(cholesky(Gt,lower=True).T,np.eye(8),lower=False)
    v=tf['value']@T;vd=tf['coordinate_rate']@T;I=np.eye(6)
    primitives={k:[]for k in ('u','Au','Mu','deltaA','deltaMu','measure','weight')}
    maps=native_phase_midpoint_map(phase['representation']);n=maps['coordinates']['x_count'];node_maps=[]
    reconstructed=[np.zeros((48,48),complex)for _ in range(4)]
    for j,a in enumerate(samples):
        V=np.concatenate([x*I for x in v[j]],axis=1);Vd=np.concatenate([x*I for x in vd[j]],axis=1)
        F0=Vd/a['N']+a['A']@V;Fm=a['M']@V;weight=weights[j]*a['N']
        reconstructed[0]+=weight*(F0.conj().T@F0)
        reconstructed[1]+=weight*(F0.conj().T@Fm+Fm.conj().T@F0)
        reconstructed[2]+=weight*(Fm.conj().T@Fm)
        reconstructed[3]+=weight*(V.conj().T@V)
        dF0=np.einsum('jab,bc->jac',a['dA'],V)-a['dN'][:,None,None]*Vd/a['N']**2
        dFm=np.einsum('jab,bc->jac',a['dM'],V)
        for key,array in (('u',V@U),('Au',F0@U),('Mu',Fm@U)):
            primitives[key].append(_stored_frobenius_upper(array))
        primitives['deltaA'].append(_stored_frobenius_upper(dF0@U,axis=(1,2)))
        primitives['deltaMu'].append(_stored_frobenius_upper(dFm@U,axis=(1,2)))
        primitives['measure'].append(np.nextafter(abs(a['dN']/a['N'])/(1-np.finfo(float).eps),np.inf))
        primitives['weight'].append(weight)
        node=maps['raw_from_phase'].copy()
        node[:,2*n:3*n]+=(a['t']-(-L/2 if phase['receipt']['side']=='incoming'else L/2))*maps['coordinates']['lift'][:,:n]
        node_maps.append(node)
    if any(not np.array_equal(a,b)for a,b in zip(reconstructed,(K,C,B,G))):
        raise ValueError('tail primitives did not reconstruct exact consumed pencil')
    Y=np.diag(lepton_current_hilbert_representation()['family_Y']).real
    tail=even_y_tail_bounds(constants,float(cutoff),float(Y[1]),float(Y[2]),
        {k:np.array(v)for k,v in primitives.items()},precision_bits=precision_bits,grading_preserving_variations=True)
    # Positive arithmetic is widened for dot/sum rounding on stored maps.
    raw=tail['weighted_directional_tail_upper'];phase_upper=sum(abs(m).T@b for m,b in zip(node_maps,raw))
    eps=np.finfo(float).eps;ops=268*len(node_maps)+32
    phase_upper=np.nextafter(phase_upper/(1-ops*eps),np.inf)
    contacts=[]
    chrono=chronological_native_phase_jacobian(phase['arrays']['stage_jacobian'][0],phase['representation'],phase['receipt']['span'])
    F=native_phase_load_rows(mean_load,phase['representation'],chrono['step'])
    for frame in ('temporal','radial'):
        A=native_phase_named_border(chrono['jacobian'],phase['representation'],frame=frame)['matrix']
        rhs=np.concatenate((F.reshape(len(A)-2,-1),np.zeros((2,9))),axis=0)
        row=1/np.maximum(np.max(abs(A),axis=1),np.finfo(float).tiny)
        col=1/np.maximum(np.max(abs(row[:,None]*A),axis=0),np.finfo(float).tiny)
        delta=-col[:,None]*np.linalg.solve(row[:,None]*A*col[None,:],row[:,None]*rhs)
        upper=phase_upper@abs(delta[:-2])
        upper=np.nextafter(upper/(1-(len(A)+16)*eps),np.inf)
        contacts.append(dict(frame=frame,contact_tail_majorant=upper.reshape(3,3),original_response_residual=A@delta+rhs,
            stored_response_amplification_only=True))
    return dict(pencil_certificate=certificate,tail_certificate={k:v for k,v in tail.items()if not isinstance(v,np.ndarray)},
        raw_quadrature_gradient_tail_upper=raw,phase_gradient_tail_upper=phase_upper,contacts=contacts,
        primitive_norms={k:np.array(v)for k,v in primitives.items()},coordinate_times=np.array([a['t']for a in samples]),
        higher_even_Y_filled_zero=False,statistics_factor_applied=False,
        error_scope='Outward exact stored finite-pencil higher-even-Y value/cotangent bounds; field-entry/primitive production, quadrature and adjoint-solve errors remain separate; no native complement or Pauli enclosure.')
