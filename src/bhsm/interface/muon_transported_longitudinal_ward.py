"""Chronological action transport and localized longitudinal Ward pairing.

All initial C6 columns are transported; no external spinor or CAR state is
chosen.  The Lorentz factor is partial_t/N+i H_can, distinct from the
positive product reference.  The current and localization derivative are
paired before testing the Ward identity.  This application does not assign
a pole, LSZ residue, physical Pauli coefficient, or starting-shell bound.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from .muon_profile_preserving_phase_sample import load_profile_preserving_phase, profile_preserving_lepton_sample
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation, fixed_y_higgs_hamiltonian
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_parent_maxwell_corrected_retarded import higgs_u2_real_representation
from .muon_parent_positive_brst_ghost import smooth_ghost_temporal_values, ghost_radial_values
from .muon_parent_retarded_hypercharge import WALL


def localized_ward_pairing(H0,Hn,T,T_rate,U0,Un,*,lapse,localization,localization_rate):
    """Literal matrix Ward and amputation placements on homogeneous solutions.

    D_L=partial_t/N+iH.  Thus deltaD=T'/N+iHn T-iT H0 and
    d_t(b Un^dagger T U0)=N b Un^dagger deltaD U0+b' Un^dagger T U0.
    This formula permits a non-Hermitian T and distinct complete shell maps.
    """
    H0,Hn,T,Tr,U0,Un=(np.asarray(x,complex)for x in(H0,Hn,T,T_rate,U0,Un))
    n=len(H0);m=len(Hn)
    if (H0.shape!=(n,n)or Hn.shape!=(m,m)or T.shape!=(m,n)or Tr.shape!=T.shape
            or U0.shape!=H0.shape or Un.shape!=Hn.shape
            or any(not np.isfinite(x).all()for x in(H0,Hn,T,Tr,U0,Un))
            or not np.isfinite([lapse,localization,localization_rate]).all()or lapse<=0):
        raise ValueError('complete finite action, source, transport and positive lapse required')
    if max(np.linalg.norm(H0-H0.conj().T),np.linalg.norm(Hn-Hn.conj().T))>2e-12*max(1.,np.linalg.norm(H0),np.linalg.norm(Hn)):
        raise ValueError('Hermitian Lorentz Hamiltonians are required')
    S=Tr/lapse+1j*(Hn@T-T@H0)
    current=lapse*localization*(Un.conj().T@S@U0)
    amputation=localization_rate*(Un.conj().T@T@U0)
    # Differentiate every transported factor, retaining the Euler placements.
    U0r=-1j*lapse*H0@U0;Unr=-1j*lapse*Hn@Un
    derivative=(localization_rate*Un.conj().T@T@U0+
        localization*(Unr.conj().T@T@U0+Un.conj().T@Tr@U0+Un.conj().T@T@U0r))
    return dict(source=S,current=current,localization_amputation=amputation,
        endpoint_derivative=derivative,point_identity_residual=current+amputation-derivative,
        external_Euler_source=U0r/lapse+1j*H0@U0,
        external_adjoint_Euler_source=Unr/lapse+1j*Hn@Un)


def _family_indices(family):
    if family not in(1,2):raise ValueError('explicit paired middle/light family required')
    return np.array([2*family,2*family+1,6+2*family,7+2*family,12+2*family,13+2*family])


def transported_longitudinal_ward_application(side,*,family=1,quadrature_order=12,
        tolerance=2e-12,repository=ROOT):
    """Execute actual C6 and full n1/n3 fundamentals on one corrected cell.

    The pure central gauge orbit includes At=eta' and deltaH=-eta T_H H.
    The independent spatial tent direction lacks these two placements;
    its difference is evaluated, rather than called a gauge direction.
    """
    if side not in('incoming','outgoing')or type(quadrature_order)is not int or quadrature_order<6:
        raise ValueError('owned arm and resolved split quadrature required')
    if not np.isfinite(tolerance)or not 0<tolerance<1e-8:raise ValueError('explicit numerical transport tolerance required')
    root=Path(repository);phase=load_profile_preserving_phase(
        'artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'else
        'artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=root)
    if phase['receipt']['steps']!=1:raise ValueError('this application binds the saved one-cell action')
    refs=dict(phase['input_hashes']);L=abs(float(phase['receipt']['span']));origin=-L if side=='incoming'else 0.
    angular=retained_full_q_angular_space(root);labels=angular['harmonic_labels'];E=np.asarray(angular['derivative_matrices'])
    f=_family_indices(family);rep=lepton_current_hilbert_representation();alpha=rep['alpha'][:,f][:,:,f]
    G=lepton_unit_trace_gauge_representation()['generators'][3][np.ix_(f,f)]
    TH=higgs_u2_real_representation()['real_generators'][3]
    blocks={n:np.array([j for j,a in enumerate(labels)if a[0]==n])for n in(1,3)}
    En={n:E[:,idx][:,:,idx]for n,idx in blocks.items()};dimensions={0:6,1:24,3:96}
    offsets={};start=0
    for n,d in dimensions.items():offsets[n]=slice(start,start+d*d);start+=d*d
    cache={}
    def point(u):
        u=float(u);key=u.hex()
        if key not in cache:
            sample=profile_preserving_lepton_sample(phase,u+origin);op=sample['operator'];H=op['H_can'][np.ix_(f,f)]
            if np.linalg.norm(H-H.conj().T)>1e-11*max(1.,np.linalg.norm(H)):raise ArithmeticError('actual Hamiltonian is not Hermitian')
            cache[key]=dict(sample=sample,H0=H,N=float(op['N']),R=float(op['R4']),
                Hn={n:np.kron(H,np.eye(len(idx)))-1j*sum(np.kron(a,e)for a,e in zip(alpha,En[n]))/op['R4']for n,idx in blocks.items()})
        return cache[key]
    def rhs(u,state):
        p=point(u);out=np.empty_like(state)
        for n,d in dimensions.items():
            H=p['H0']if n==0 else p['Hn'][n];U=state[offsets[n]].reshape(d,d)
            out[offsets[n]]=(-1j*p['N']*H@U).ravel()
        return out
    initial=np.concatenate([np.eye(d,dtype=complex).ravel()for d in dimensions.values()])
    # Split at the owned tent kink; the Hamiltonian itself is the same analytic cell.
    first=solve_ivp(rhs,(0.,L/2),initial,method='DOP853',rtol=tolerance,atol=tolerance/10,dense_output=True)
    second=solve_ivp(rhs,(L/2,L),first.y[:,-1],method='DOP853',rtol=tolerance,atol=tolerance/10,dense_output=True)
    if not first.success or not second.success:raise ArithmeticError('actual homogeneous transport failed')
    def transport(u,n):
        state=(first if u<=L/2 else second).sol(u);d=dimensions[n];return state[offsets[n]].reshape(d,d)
    z,w=np.polynomial.legendre.leggauss(quadrature_order)
    times=np.r_[(z+1)*L/4,(z+3)*L/4];weights=np.tile(w*L/4,2)
    # The interior radial profile is zero at the wall.  The retained wall
    # profile (index1) has unit trace and gives a nonzero current application.
    ghost=smooth_ghost_temporal_values(times,L);pw=float(ghost_radial_values([WALL])[0,1,0]);arrays={};records={}
    if pw==0:raise ArithmeticError('the consumed wall gauge profile must have nonzero trace')
    arrays['chronological_times']=times;arrays['positive_coordinate_quadrature']=weights
    arrays['coordinate_times']=times+origin
    for n,idx in blocks.items():
        nh=len(idx);q=n*(n+2);carrier=np.eye(nh)[:,0];spatial=np.einsum('aij,j->ai',En[n],carrier)
        orbit=np.zeros((6*nh,6),complex);amp=orbit.copy();finite_difference=orbit.copy();point_defects=[];source_defects=[]
        sources=[];currents=[];amps=[];differences=[];fundamentals=[];norms=[]
        for k,(u,weight)in enumerate(zip(times,weights)):
            p=point(u);U0=transport(u,0);Un=transport(u,n);b=2*min(u/L,1-u/L);bp=2/L if u<L/2 else-2/L
            eta=ghost[k,0,0]*pw/np.sqrt(q);et=ghost[k,0,1]*pw/np.sqrt(q)
            T=eta*np.kron(G,carrier[:,None]);Tr=et*np.kron(G,carrier[:,None])
            paired=localized_ward_pairing(p['H0'],p['Hn'][n],T,Tr,U0,Un,lapse=p['N'],localization=b,localization_rate=bp)
            raw=p['sample']['sample']['raw_fields'];hreal=raw[-8:-4]
            dm=fixed_y_higgs_hamiltonian((-eta*(TH@hreal))[:2][None]+1j*(-eta*(TH@hreal))[2:][None])[0][np.ix_(f,f)]
            literal=(et/p['N']*np.kron(G,carrier[:,None])+1j*np.kron(dm,carrier[:,None])+
                eta*sum(np.kron(a@G,der[:,None])for a,der in zip(alpha,spatial))/p['R'])
            source_defects.append(literal-paired['source']);point_defects.append(paired['point_identity_residual'])
            orbit+=weight*paired['current'];amp+=weight*paired['localization_amputation']
            # The independent spatial b-gradient differs from its complete orbit
            # by missing At=b' and missing the required scalar gauge tangent.
            missing_h=b*pw/np.sqrt(q)*(TH@hreal)
            missing_mass=fixed_y_higgs_hamiltonian((missing_h[:2]+1j*missing_h[2:])[None])[0][np.ix_(f,f)]
            difference=-bp*pw/(p['N']*np.sqrt(q))*np.kron(G,carrier[:,None])+1j*np.kron(missing_mass,carrier[:,None])
            finite_difference+=weight*p['N']*b*(Un.conj().T@difference@U0)
            sources.append(literal);currents.append(paired['current']);amps.append(paired['localization_amputation'])
            differences.append(difference);fundamentals.append(Un);norms.append(np.linalg.norm(Un.conj().T@Un-np.eye(6*nh)))
        # b vanishes at both faces. This endpoint value is computed, not dropped.
        endpoint=np.zeros_like(orbit)
        arrays.update({f'n{n}_source':np.array(sources),f'n{n}_current_integrand':np.array(currents),
            f'n{n}_amputation_integrand':np.array(amps),f'n{n}_source_identity_residual':np.array(source_defects),
            f'n{n}_point_Ward_residual':np.array(point_defects),f'n{n}_fundamental':np.array(fundamentals),
            f'n{n}_integrated_orbit_current':orbit,f'n{n}_integrated_localization_amputation':amp,
            f'n{n}_endpoint_contact':endpoint,f'n{n}_integrated_Ward_residual':orbit+amp-endpoint,
            f'n{n}_independent_spatial_tent_missing_At_H_source':np.array(differences),
            f'n{n}_independent_spatial_tent_minus_complete_orbit_current':finite_difference,
            f'n{n}_harmonic_indices':idx})
        if np.linalg.norm(sources)==0:raise ArithmeticError('actual transported wall source unexpectedly vanished')
        records[str(n)]=dict(shell_dimension=6*nh,source_identity_norm=float(np.linalg.norm(source_defects)),
            point_Ward_norm=float(np.linalg.norm(point_defects)),integrated_Ward_norm=float(np.linalg.norm(orbit+amp)),
            orbit_current_norm=float(np.linalg.norm(orbit)),localization_amputation_norm=float(np.linalg.norm(amp)),
            independent_spatial_tent_minus_complete_orbit_current_norm=float(np.linalg.norm(finite_difference)),
            transport_unitarity_defect=max(norms),complete_shell_transported=True)
    arrays['n0_fundamental']=np.array([transport(u,0)for u in times]);arrays['family_indices']=f
    for name in('muon_transported_longitudinal_ward','muon_profile_preserving_phase_sample',
        'muon_native_dirac_hamiltonian','muon_native_product_factor_graph','muon_parent_maxwell_corrected_retarded'):
        path='src/bhsm/interface/'+name+'.py';refs[path]=sha256((root/path).read_bytes()).hexdigest()
    if any(sha256((root/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed action changed')
    return dict(arrays=arrays,metadata=dict(classification='EVALUATED_CHRONOLOGICAL_ACTION_TRANSPORTED_LONGITUDINAL_WARD_PAIRING',
        side=side,family=family,length=L,quadrature_order=quadrature_order,transport_rtol=tolerance,
        retained_radial_wall_profile_index=1,retained_radial_wall_trace=pw,
        transport_rhs_evaluations=first.nfev+second.nfev,input_hashes=refs,shell_records=records,
        external_initial_condition='identity is the fundamental-map coordinate convention, not a physical birth trace or separate prepared state',
        inherited_trace_scope='the matrix identity applies to every inherited right/left trace by multiplication; no bundle birth graph is replaced with an identity',
        derivative_clock='future coordinate t=u-L incoming; t=u outgoing; i partial_t Psi=N Hcan Psi',
        external_localization_derivative_and_both_endpoint_contacts_retained=True,
        positive_reference_substituted_for_Lorentz_operator=False,finite_Lorenz_null_channel_identified_as_pure_gauge=False,
        on_shell_Ward_statement='complete gauge orbit current cancels its explicit localization amputation on homogeneous transported external maps',
        physical_LSZ_or_Pauli_or_starting_shell_bound_proved=False,physical_a_mu=None,physical_g_mu=None,
        error_scope='evaluated same analytic numerical-cell action and full fundamentals; ODE/quadrature diagnostics, not outward producer, continuum or physical matching enclosure'))
