"""Actual finite-reference longitudinal and Ward current applications.

The weak Lorenz term projects against two smooth temporal ghost bubbles.
It is not replaced by the full pointwise divergence norm.  The central
U(1) construction below uses the exact scalar Casimir and the existing
radial/temporal coefficient maps; no small eigenvector is selected or
deleted.  A bounded high-shell Rayleigh quotient of this finite reference
does not establish an obstruction for an on-shell, BRST-quotiented Pauli
observable.  Its external-Euler Ward terms are retained explicitly.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import numpy as np

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from .muon_profile_preserving_phase_sample import load_profile_preserving_phase, profile_preserving_lepton_sample
from .muon_parent_positive_brst_ghost import smooth_ghost_temporal_values, ghost_radial_values
from .muon_parent_retarded_hypercharge import WALL
from .muon_changing_coupled_open_current import positive_factor_open_vertices
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from .muon_parent_maxwell_corrected_retarded import higgs_u2_real_representation
from .muon_source_directed_temporal_green import source_product_temporal_values
from .muon_profile_preserving_phase_sample import profile_preserving_raw_sample
from .muon_parent_positive_coupled_field import corrected_positive_parent_reference,VOLUME
from .muon_parent_mean_causal_action import MAXWELL_TO_CAP
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet


def central_longitudinal_vector(derivatives, harmonic, radial_profile=0):
    """Literal independent angular gradient, normalized by its Casimir."""
    E=np.asarray(derivatives)
    if E.shape!=(3,20,20) or not np.isrealobj(E) or not np.isfinite(E).all():
        raise ValueError('complete retained real odd derivative maps required')
    if type(harmonic)is not int or not 0<=harmonic<20 or radial_profile not in (0,1):
        raise ValueError('owned harmonic and radial profile required')
    gradient=E[:,:,harmonic]
    casimir=float(np.sum(gradient*gradient))
    if casimir<=0:raise ValueError('nonconstant scalar harmonic required')
    x=np.zeros(1200)
    for axis in range(3):
        start=400*radial_profile+80*(axis+2)+60
        x[start:start+20]=gradient[axis]/np.sqrt(casimir)
    return x,casimir


def leading_central_projection(one_form_gram, derivatives, labels):
    """Recover the actual weighted angular projection from Casimir blocks.

    For a central ghost, its Gram is exactly q*Qangular+Qtime_radial.
    This follows from sum E_i^T E_i=qI and d²eta=0, rather than an
    extrapolation of numerical eigenvalues. The remaining Gram and action
    coefficients are evaluated below with the original full matrices.
    """
    G=np.asarray(one_form_gram)
    if G.shape!=(1120,1120) or not np.isrealobj(G) or not np.isfinite(G).all():
        raise ValueError('actual complete one-form Gram required')
    carriers=[next(i for i,l in enumerate(labels)if l[0]==n)for n in(1,3)]
    ids=lambda h:np.array([800+80*j+60+h for j in range(4)])
    matrices=[G[np.ix_(ids(h),ids(h))]for h in carriers]
    Q=(matrices[1]-matrices[0])/12
    Qtr=matrices[0]-3*Q
    if np.linalg.eigvalsh((Q+Q.T)/2)[0]<=0:
        raise ArithmeticError('actual leading ghost pairing is not positive')
    d=[];unprojected=[]
    for radial in range(2):
        vector,q=central_longitudinal_vector(derivatives,carriers[0],radial)
        d.append(G[ids(carriers[0])]@vector[:1120]/np.sqrt(q))
        unprojected.append(float(vector[:1120]@G@vector[:1120]))
    d=np.array(d).T
    w=np.linalg.solve(Q,-d)
    residual=np.array(unprojected)+np.einsum('ij,ij->j',d,w)
    if np.min(residual)<=0:raise ArithmeticError('leading independent projection residual is not positive')
    return dict(angular_ghost_pairing=Q,time_radial_ghost_pairing=Qtr,
        leading_independent_ghost_pairing=d,leading_ghost_coefficients=w,
        unprojected_angular_Gram=np.array(unprojected),remaining_angular_Gram=residual,
        carrier_indices=carriers,central_coordinate_indices=ids)


def direct_weighted_central_coefficients(phase,*,quadrature_order=6):
    """Evaluate the leading projection and current without Casimir subtraction.

    Only metric coefficients enter these leading angular Gram/action terms.
    The central generator commutes with every retained gauge coefficient,
    so no child connection profile is dropped from a noncentral term.  The
    direct positive integrands avoid subtracting large temporal ghost-Gram
    terms to recover their small angular coefficient.
    """
    L=abs(float(phase['receipt']['span']));rep=phase['representation']
    z,w=np.polynomial.legendre.leggauss(quadrature_order)
    times=np.r_[(z+1)*L/4,(z+3)*L/4];weights=np.tile(w*L/4,2)
    ghosts=smooth_ghost_temporal_values(times,L);radial=ghost_radial_values(rep['rho'])
    wall=ghost_radial_values([WALL])[0,:,0]
    Q=np.zeros((4,4));d=np.zeros((4,2));ind=np.zeros((2,2));kinetic=np.zeros(2)
    snapshots=[];normalization=0.;T=higgs_u2_real_representation()['real_generators'][3]
    for k,(u,weight)in enumerate(zip(times,weights)):
        t=float(u-L if phase['receipt']['side']=='incoming'else u)
        raw=profile_preserving_raw_sample(phase,t)['raw_fields']
        # Connection values are immaterial to this central leading metric
        # integral. The exact material geometry is shared by both owners.
        ref=corrected_positive_parent_reference(raw,rep,coordinate_time=t)
        b=2*min(u/L,1-u/L);bp=2/L if u<L/2 else-2/L
        for j,(metric,dens,rw)in enumerate(zip(ref['positive_metric_coefficients'],ref['positive_two_form_densities'],ref['radial_weights'])):
            gs=metric[3];p=radial[j,:,0];pr=radial[j,:,1]
            gp=np.array([ghosts[k,a,0]*p[r]for a in range(2)for r in range(2)])
            xx=b*p;ww=weight*rw
            Q+=ww*gs*np.outer(gp,gp);d+=ww*gs*np.outer(gp,xx);ind+=ww*gs*np.outer(xx,xx)
            e,r,_,_,beta=dens
            kinetic+=ww*(e*(bp*p-beta*b*pr)**2+r*(b*pr)**2)*MAXWELL_TO_CAP
        geo=intrinsic_m4_weight_jet(12,raw[:37],raw[37:74],raw[74:98],source_value=raw[98],source_rate=raw[99])
        N,R,ws=[geo[key].value for key in('induced_lapse','R4','wS')]
        kinetic+=weight*(2*ws/VOLUME)*np.sum((T@raw[-8:-4])**2)*(b*wall)**2
        normalization+=weight*N*b*b
        snapshots.append((N,R,b,ghosts[k,:,0].copy()))
    coefficients=np.linalg.solve(Q,-d)
    remaining=np.empty(2);current_coefficients=np.zeros(2)
    # Evaluate the projection residual directly, not as ind-d^T Q^-1 d.
    for k,(u,weight)in enumerate(zip(times,weights)):
        t=float(u-L if phase['receipt']['side']=='incoming'else u)
        raw=profile_preserving_raw_sample(phase,t)['raw_fields'];ref=corrected_positive_parent_reference(raw,rep,coordinate_time=t)
        N,R,b,g=snapshots[k]
        if k==0:remaining[:]=0.
        for j,(metric,rw)in enumerate(zip(ref['positive_metric_coefficients'],ref['radial_weights'])):
            p=radial[j,:,0];gp=np.array([g[a]*p[r]for a in range(2)for r in range(2)])
            residual=b*p+gp@coefficients
            remaining+=weight*rw*metric[3]*residual**2*MAXWELL_TO_CAP
        gpwall=np.array([g[a]*wall[r]for a in range(2)for r in range(2)])
        hwall=b*wall+gpwall@coefficients
        current_coefficients+=weight*N*b*b*hwall/R/normalization
    charge=lepton_unit_trace_gauge_representation()['generators'][3]
    current_norms=current_coefficients**2*np.sum(abs(charge)**2)
    if min(remaining)<=0:raise ArithmeticError('direct remaining angular Gram must be positive')
    return dict(angular_ghost_pairing=Q,leading_independent_ghost_pairing=d,
        leading_ghost_coefficients=coefficients,remaining_angular_Gram=remaining,
        direct_action_limits=kinetic,direct_current_coefficients=current_coefficients,
        direct_current_squared_norm_limits=current_norms,
        time_radial_ghost_pairing=None,unprojected_angular_Gram=np.diag(ind),
        chronological_times=times,positive_coordinate_quadrature=weights)


def central_gauge_current_ward_point(raw,operator,*,eta,eta_rate,external_value,external_rate):
    """Evaluate the full18 value/time Ward placements, retaining Euler terms.

    The spatial coefficient of E_i eta is -i alpha_i G/R on both
    sides of deltaD=[D,eta].  The reported value/time part includes the
    Higgs commutator and proper lapse once.  The external Euler contact
    is not discarded or interpreted as an on-shell zero.
    """
    raw=np.asarray(raw);N=float(operator['N']);R=float(operator['R4'])
    if raw.shape!=(268,)or not np.isrealobj(raw)or not np.isfinite(raw).all()or min(N,R)<=0:
        raise ValueError('same actual full raw268 and positive geometry required')
    if not np.isfinite([eta,eta_rate,external_value,external_rate]).all():
        raise ValueError('actual finite source/external temporal maps required')
    G=lepton_unit_trace_gauge_representation()['generators'][3]
    T=higgs_u2_real_representation()['real_generators'][3]
    v=positive_factor_open_vertices(R,N)
    deltaH=-float(eta)*(T@raw[-8:-4])
    supplied=float(eta_rate)*v['gauge'][0,3]+np.einsum('c,cij->ij',deltaH,v['scalar'])
    B=operator['W']+operator['Omega_tau']
    commutator=(B@G-G@B)*float(eta)+G*float(eta_rate)/N
    Aexternal=np.eye(18)*float(external_rate)/N+B*float(external_value)
    product_action=G*float(eta_rate*external_value+eta*external_rate)/N+B@G*float(eta*external_value)
    external_contact=G@Aexternal*float(eta)
    alpha=lepton_current_hilbert_representation()['alpha']
    spatial_supplied=v['gauge'][2:,3]
    spatial_commutator=-1j*alpha@G/R
    return dict(supplied_value_time_source=supplied,commutator_value_time_source=commutator,
        source_identity_residual=supplied-commutator,
        product_action=product_action,external_Euler_contact=external_contact,
        external_ward_residual=product_action-external_contact-supplied*float(external_value),
        spatial_source_identity_residual=spatial_supplied-spatial_commutator,
        spatial_product_derivative_coefficient=spatial_commutator*float(external_value),
        external_Euler_contact_dropped=False,physical_on_shell_annihilation_proved=False)


def retained_longitudinal_current_application(side,*,repository=ROOT):
    """Consume actual stored action/current and apply the central direction."""
    if side not in ('incoming','outgoing'):raise ValueError('explicit retained arm required')
    root=Path(repository);folder=root/'artifacts/muon_parent_positive_coupled_temporal_20261011/run_1'
    receipt=json.loads((folder/'result.json').read_text(encoding='utf8'));refs=dict(receipt['input_hashes'])
    refs[(folder/'result.json').relative_to(root).as_posix()]=sha256((folder/'result.json').read_bytes()).hexdigest()
    def read(name):
        path=folder/name;data=path.read_bytes();rec=receipt.get('array_archives',receipt.get('numerical_files'))[name]
        if sha256(data).hexdigest()!=rec['sha256']or len(data)!=rec['bytes']:
            raise ValueError('stored action/current changed: '+name)
        refs[path.relative_to(root).as_posix()]=rec['sha256']
        with np.load(path,allow_pickle=False)as f:return{k:f[k].copy()for k in f.files}
    action=read(side+'_action.npz');hilbert=read(side+'_hilbert.npz');images=read(side+'_images.npz')
    angular=retained_full_q_angular_space(root);E=angular['derivative_matrices'];labels=angular['harmonic_labels']
    K=action['coupled_action_Hessian'];G=hilbert['coupled_action_Gram'];one=hilbert['one_form_Gram_per_kappa']
    J=images['canonical_full18_current_source_image'];B=one[800:]
    subtractive=leading_central_projection(one,E,labels)
    phase=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'else
        'artifacts/muon_inherited_finite_normal_phase_20261011/run_1',repository=root);refs.update(phase['input_hashes'])
    projection=direct_weighted_central_coefficients(phase)
    projection['carrier_indices']=subtractive['carrier_indices'];projection['central_coordinate_indices']=subtractive['central_coordinate_indices']
    w=projection['leading_ghost_coefficients'];records=[];vectors=[];currents=[]
    for radial in range(2):
        for harmonic,label in enumerate(labels):
            z,q=central_longitudinal_vector(E,harmonic,radial);ids=projection['central_coordinate_indices'](harmonic)
            z[ids]+=w[:,radial]/np.sqrt(q)
            norm=float(z@G@z);energy=float(z@K@z);current=np.einsum('hfij,f->hij',J,z)
            # Also evaluate the EXACT finite-shell weak Lorenz-null graph.
            finite=z.copy();finite[ids]=np.linalg.solve(B[np.ix_(ids-800,ids)],-B[ids-800]@(z[:1120]-np.eye(1120)[:,ids]@z[ids]))
            actual_lorenz=B@finite[:1120]
            fcur=np.einsum('hfij,f->hij',J,finite)
            records.append(dict(radial_profile=radial,harmonic=harmonic,level=int(label[0]),casimir=q,
                leading_graph_Gram=norm,leading_graph_action=energy,leading_graph_Rayleigh=energy/norm,
                leading_graph_current_squared_norm=float(np.sum(abs(current)**2)),
                exact_finite_Lorenz_residual=float(np.linalg.norm(actual_lorenz)),
                exact_finite_Lorenz_current_norm=float(np.linalg.norm(fcur)),
                exact_finite_Lorenz_Rayleigh=float(finite@K@finite/(finite@G@finite))))
            vectors.append(z);currents.append(current)
    limits=[]
    for radial in range(2):
        r1=next(r for r in records if r['radial_profile']==radial and r['level']==1)
        r3=next(r for r in records if r['radial_profile']==radial and r['level']==3)
        def constant(key):return(15*r3[key]-3*r1[key])/12
        gram=projection['remaining_angular_Gram'][radial];energy=projection['direct_action_limits'][radial]
        limits.append(dict(radial_profile=radial,angular_Gram_limit=gram,action_limit=energy,
            Rayleigh_limit=energy/gram,current_squared_norm_limit=projection['direct_current_squared_norm_limits'][radial],
            subtractive_stored_Gram_consistency=constant('leading_graph_Gram'),
            subtractive_stored_action_consistency=constant('leading_graph_action'),
            subtractive_stored_current_consistency=constant('leading_graph_current_squared_norm'),
            dependence='G=G_infinity+G_1/[n(n+2)], K=K_infinity+K_1/[n(n+2)] on the exact central Casimir graph',
            coefficient_scope='direct same-owner positive weighted integrands and quadrature; no outward producer or continuum enclosure'))
    L=abs(phase['receipt']['span']);z,gw=np.polynomial.legendre.leggauss(6)
    times=np.r_[(z+1)*L/4,(z+3)*L/4];weights=np.tile(gw*L/4,2)
    ghosts=smooth_ghost_temporal_values(times,L);radial_wall=ghost_radial_values(np.array([WALL]))[0,:,0]
    trial=source_product_temporal_values(times,L)['value'];ward=[];overlaps=[]
    for k,u in enumerate(times):
        t=float(u-L if side=='incoming'else u);sample=profile_preserving_lepton_sample(phase,t)
        b=2*min(u/L,1-u/L);bp=2/L if u<L/2 else-2/L
        eta=sum(w[j,0]*ghosts[k,j//2,0]*radial_wall[j%2]for j in range(4))
        etat=sum(w[j,0]*ghosts[k,j//2,1]*radial_wall[j%2]for j in range(4))
        result=central_gauge_current_ward_point(sample['sample']['raw_fields'],sample['operator'],
            eta=eta,eta_rate=etat,external_value=b,external_rate=bp)
        ward.append(result)
        hwall=b*radial_wall[0]+eta
        overlaps.append(weights[k]*sample['operator']['N']*b*hwall*trial[k]/sample['operator']['R4'])
    arrays=dict(leading_central_directions=np.array(vectors),canonical_current_images=np.array(currents),
        central_angular_ghost_pairing=projection['angular_ghost_pairing'],
        central_time_radial_ghost_pairing_subtractive_diagnostic=subtractive['time_radial_ghost_pairing'],
        central_angular_ghost_pairing_subtractive_diagnostic=subtractive['angular_ghost_pairing'],
        leading_ghost_coefficients=w,remaining_angular_Gram=projection['remaining_angular_Gram'],
        chronological_times=times,current_time_overlaps=np.sum(overlaps,axis=0))
    for key in ('supplied_value_time_source','commutator_value_time_source','source_identity_residual',
        'product_action','external_Euler_contact','external_ward_residual','spatial_source_identity_residual'):
        arrays[key]=np.array([r[key]for r in ward])
    if any(sha256((root/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise ValueError('consumed owner changed')
    return dict(arrays=arrays,metadata=dict(classification='EVALUATED_RETAINED_CENTRAL_LONGITUDINAL_REFERENCE_AND_WARD_CURRENT',
        side=side,input_hashes=refs,channel_records=records,exact_Casimir_limits=limits,
        source_identity_residual_norm=float(np.linalg.norm(arrays['source_identity_residual'])),
        external_ward_residual_norm=float(np.linalg.norm(arrays['external_ward_residual'])),
        spatial_source_identity_residual_norm=float(np.linalg.norm(arrays['spatial_source_identity_residual'])),
        external_Euler_contact_norm=float(np.linalg.norm(arrays['external_Euler_contact'])),
        current_time_overlaps_norm=float(np.linalg.norm(arrays['current_time_overlaps'])),
        endpoint_source_contact='both ghost bubbles and their rates vanish; external tent vanishes; no endpoint term omitted',
        exact_gauge_orbit_identified_with_projected_longitudinal_channel=False,
        physical_current_on_shell_annihilation_proved=False,uniform_reference_n_squared_coercivity_proved=False,
        full_starting_shell_Pauli_bound=None,physical_signed_soft_Pauli=None,
        error_scope='exact algebraic Casimir/channel construction, evaluated stored finite action and represented clock; no upstream outward, full temporal quotient or physical matching certificate'))
