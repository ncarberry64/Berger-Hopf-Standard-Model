"""Complete reached homogeneous field cotangent of the fixed n0 heat core.

This extends the fixed-Y mean mass readout to its metric, measure and U2
connection terms.  The numerical Dirichlet core and cutoff probes remain
explicit; the whole stratified native heat/Pauli functional is not replaced.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import eigh

from .muon_native_product_factor_graph import (
    _finite, _source_core_samples, _family_shell_heat_forms,
    lepton_unit_trace_gauge_representation, finite_common_family_intrinsic_operator,
)
from .muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian,lepton_current_hilbert_representation
from .muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from .muon_parent_gauge_geometry_correction import finite_common_iterate_at_time
from .muon_parent_retarded_hypercharge import WALL,regular_radial_basis
from .muon_parent_maxwell_full_weak import FIELD_ORDER,M


def corrected_joint_mean_heat_cotangent(response, *, time_nodes, quadrature_order,
        parameter, integrate_cutoff=True, family_indices=(1,2)):
    """Apply f'(lambda) u†(delta K-lambda delta Gram)u on raw228.

    DeltaA=-(deltaN/N²)(du+Omega_t*u)+deltaOmega_t*u/N+deltaW*u.
    The Haar-current Gram is Ndt*2pi², after the owned R4^(3/2)
    density rescaling.  Consequently the measure contact is
    (deltaN/N)(|Au|²-lambda|u|²), counted once with the operator term.
    """
    nodes=_finite(time_nodes,'joint heat nodes',real=True)
    if nodes.ndim!=1 or len(nodes)<3 or np.any(np.diff(nodes)<=0):raise ValueError('increasing heat core nodes required')
    if nodes[0]<response['time_shift'] or nodes[-1]>0:raise ValueError('no joint heat extrapolation')
    if type(quadrature_order) is not int or quadrature_order<2:raise ValueError('quadrature order>=2 required')
    p=float(parameter)
    if not np.isfinite(p) or p<=0:raise ValueError('positive explicit cutoff/heat probe required')
    families=tuple(family_indices)
    if not families or len(set(families))!=len(families) or any(type(f) is not int or f not in (0,1,2) for f in families):
        raise ValueError('distinct retained families0..2 required')
    samples=_source_core_samples(response['coefficients'],response['representation'],response['reference'],nodes,
        np.ones((len(nodes),8)),quadrature_order)
    rep=response['representation'];generators=lepton_unit_trace_gauge_representation()['generators']
    alpha=lepton_current_hilbert_representation()['alpha']
    mass_basis=fixed_y_higgs_hamiltonian(np.array([[1,0],[0,1],[1j,0],[0,1j]],complex))
    radial,_=regular_radial_basis(np.array([WALL]),rep['radial_order'])
    omega_variation=np.zeros((60,4,18,18),complex)
    for j,label in enumerate(rep['gauge_labels']):
        field=FIELD_ORDER.index(label['field'])
        if field==0:omega_variation[j,0]=radial[0,label['radial']]*generators[label['internal']]
        elif field>=2:omega_variation[j,field-1]=radial[0,label['radial']]*generators[label['internal']]
    mechanical_W=sum(-1j*alpha[a]@generators[c]*M[a,c] for a in range(3) for c in range(4))
    geometry=[]
    for s in samples:
        t=nodes[s['cell']]+s['x']*s['h']
        data=finite_common_iterate_at_time(t,response['coefficients'],rep,response['reference'],rho=np.array([WALL]))
        geo=intrinsic_m4_weight_jet(12,data['q'],data['qdot'],data['m'],source_value=data['normal'],source_rate=data['normal_rate'])
        operator=finite_common_family_intrinsic_operator(t,response['coefficients'],rep,response['reference'])
        geometry.append((geo,operator['H']))
    rows={}
    for family in families:
        fiber=np.array([2*family,2*family+1,6+2*family,7+2*family,12+2*family,13+2*family])
        zero=_family_shell_heat_forms(samples,len(nodes),None,fiber)
        eig=zero['eigenvalues'];ev=np.zeros((6*len(nodes),len(eig)),complex);ev[zero['interior']]=zero['vectors']
        spectral=-np.exp(-p*eig)/eig if integrate_cutoff else -p*np.exp(-p*eig)
        loads=[]
        for s,(geo,H) in zip(samples,geometry):
            i,x,h=s['cell'],s['x'],s['h'];u=(1-x)*ev[6*i:6*(i+1)]+x*ev[6*(i+1):6*(i+2)]
            du=(ev[6*(i+1):6*(i+2)]-ev[6*i:6*(i+1)])/h
            N,R=s['N'],s['R'];omega=s['Omega_t'][np.ix_(fiber,fiber)];W=s['W'][np.ix_(fiber,fiber)]
            temporal=du+omega@u;Au=temporal/N+W@u
            mass=fixed_y_higgs_hamiltonian(H[None])[0][np.ix_(fiber,fiber)]
            delta=np.zeros((228,6,len(eig)),complex)
            dN=geo['induced_lapse'].gradient;dR=geo['R4'].gradient;dlam=geo['mechanical_connection_lambda'].gradient
            spin_spatial=W-mass;mechanical=mechanical_W[np.ix_(fiber,fiber)]/R
            delta[:100]=-dN[:,None,None]*temporal[None]/N**2-dR[:,None,None]*(spin_spatial@u)[None]/R+dlam[:,None,None]*(mechanical@u)[None]
            ov=omega_variation[:,:,fiber][:,:,:,fiber]
            delta[100:160]=np.einsum('jkl,li->jki',ov[:,0],u)/N
            for a in range(3):
                gaugeW=-1j*np.einsum('kl,jlm->jkm',alpha[a][np.ix_(fiber,fiber)],ov[:,a+1])/R
                delta[100:160]+=np.einsum('jkl,li->jki',gaugeW,u)
            delta[220:224]=np.einsum('bkl,li->bki',mass_basis[:,fiber][:,:,fiber],u)
            diagonal=2*np.einsum('ki,bki->bi',Au.conj(),delta).real
            gram_measure=(np.sum(abs(Au)**2,axis=0)-eig*np.sum(abs(u)**2,axis=0))
            diagonal[:100]+=dN[:,None]/N*gram_measure[None]
            loads.append(s['weight']*(diagonal@spectral))
        load=np.array(loads)
        rows[str(family)]=dict(inherited_family=('heavy','middle','light')[family],weighted_raw228_cotangent=load,
            constant_raw228_cotangent=np.sum(load,axis=0),spectral_minimum=float(eig[0]),
            generalized_eigen_residual_relative=zero['generalized_eigen_residual_relative'])
    t=np.array([nodes[s['cell']]+s['x']*s['h'] for s in samples])
    return dict(families=rows,coefficient_time_samples=t,response_time_samples=t-response['time_shift'],
        raw_coordinate_order='geometry100,gauge_value60,gauge_rate60,Hreal4,Hrate4',parameter=p,
        cutoff_integral_to_infinity=integrate_cutoff,
        spectral_derivative='fprime(lambda)*u_dagger(deltaK-lambda deltaGram)u',
        operator_variation='deltaA=-(deltaN/N²)(du+Omega_t*u)+deltaOmega_t*u/N+deltaW*u',
        measure_variation='(deltaN/N)(|Au|²-lambda|u|²), included once',
        raw_gauge_rate_and_H_rate_cotangents_exact_zero='this reached Hamiltonian product core depends on field values; geometry velocity jets remain retained',
        full228_reached_homogeneous_operator_cotangent=True,positive_Haar_density_applied_once=True,
        complete_stratified_native_heat_or_Pauli_evaluated=False)


def joint_heat_target_to_mean_descriptor(target, action_samples):
    """Bind raw operator cotangents to the SAME action's trace restriction."""
    from .muon_parent_mean_causal_action import mean_coordinate_lift
    # Full216 coordinates and raw228 coordinates share the retained labels.
    labels=action_samples['raw_gauge_labels'] if 'raw_gauge_labels' in action_samples else None
    if labels is None:raise ValueError('actual mean gauge coordinate labels required for heat target binding')
    P=mean_coordinate_lift(labels)['lift'];Q=action_samples['lift_to_full_mean']
    ordered=tuple(target['families']);raw=np.stack([target['families'][f]['weighted_raw228_cotangent'] for f in ordered],axis=2)
    reduced=np.einsum('ia,tiF->taF',P@Q,raw)
    return dict(target_times=target['response_time_samples'],target_loads=reduced,family_order=ordered,
        density_reapplied=False,all_reached_geometry_gauge_scalar_cotangents_retained=True)


def _unit_lepton_mass6(H):
    """Unit Yukawa Taylor coefficient on weak2*spin2 plus right spin2."""
    h=np.asarray(H,complex);result=np.zeros((6,6),complex)
    result[:4,4:]=np.kron(h[:,None],np.eye(2));result[4:,:4]=result[:4,4:].conj().T
    return result


def _stored_frobenius_upper(value, axis=None):
    """Outward norm of stored binary64 entries under IEEE basic arithmetic.

    The gamma_(4N+16) bound covers component products/additions and any
    sequential or pairwise reduction; it excludes how entries were made.
    These core arrays are far from overflow and subnormal square scales.
    """
    z=np.asarray(value,complex);size=z.size if axis is None else int(np.prod([z.shape[a] for a in axis]))
    floor=np.sqrt(np.finfo(float).tiny)
    if any(np.any((abs(part)>0)&(abs(part)<floor)) for part in (z.real,z.imag)):
        raise ValueError('stored norm has subnormal square products outside the relative-error proof')
    squares=z.real*z.real+z.imag*z.imag;s=np.sum(squares,axis=axis)
    eps=np.finfo(float).eps;gamma=(4*size+16)*eps/(1-(4*size+16)*eps)
    if np.any(~np.isfinite(s)) or np.any((s==0)&(np.max(abs(z),axis=axis)>0)):
        raise ValueError('stored norm outside the supported finite normal square scale')
    return np.nextafter(np.sqrt(s/(1-gamma)),np.inf)


def _cutoff_divided_differences(eigenvalues, parameter, order):
    """Stable g[1],g[2] for g=-exp(-c*x)/x, including repeated poles."""
    lam=eigenvalues;c=parameter
    gx,gw=np.polynomial.legendre.leggauss(order);q=(1-(gx+1)/2)[:,None,None]*lam[None,:,None]+((gx+1)/2)[:,None,None]*lam[None,None,:]
    first=np.sum((gw/2)[:,None,None]*np.exp(-c*q)*(c/q+1/q**2),axis=0)
    # Choose the widest difference for each triple; exact degeneracies use g''/2.
    a,b,d=np.broadcast_arrays(lam[:,None,None],lam[None,:,None],lam[None,None,:])
    values=np.stack((a,b,d));lo=np.argmin(values,axis=0);hi=np.argmax(values,axis=0)
    ii,jj,kk=np.broadcast_arrays(np.arange(len(lam))[:,None,None],np.arange(len(lam))[None,:,None],np.arange(len(lam))[None,None,:])
    indices=np.stack((ii,jj,kk));li=np.take_along_axis(indices,lo[None],axis=0)[0];ui=np.take_along_axis(indices,hi[None],axis=0)[0]
    # If all three coincide, argmin=argmax; that branch does not use the middle index.
    mi=ii+jj+kk-li-ui;mi=np.clip(mi,0,len(lam)-1)
    spread=lam[ui]-lam[li];near=spread<=64*np.finfo(float).eps*np.maximum(1.,lam[ui])
    second=np.zeros_like(spread)
    np.divide(first[mi,ui]-first[li,mi],spread,out=second,where=~near)
    mean=(a+b+d)/3
    second[near]=(-.5*np.exp(-c*mean)*(c*c/mean+2*c/mean**2+2/mean**3))[near]
    return first,second


def corrected_even_y_paired_heat_cotangent(response, *, time_nodes, quadrature_order,
        parameter, divided_difference_order=64):
    """Evaluate the stable middle-minus-light Y² target and a Y⁴ majorant.

    With the actual H and all other fields held fixed, the normalized
    finite pencil is P(Y)=P0+Y*C+Y²*B.  The retained L/R sign grading
    sends Y to -Y exactly.  P0 is a Taylor coefficient, not a physical
    H=0/background selection.  The coefficient of Y² in Tr E1(cP) is
    Tr g(P0)B + .5 sum g[1](lambda_i,lambda_j)|C_ij|².
    Its full raw228 derivative is evaluated using g[1] and g[2].
    """
    nodes=_finite(time_nodes,'paired heat nodes',real=True);c=float(parameter)
    if nodes.ndim!=1 or len(nodes)<3 or np.any(np.diff(nodes)<=0):raise ValueError('increasing paired heat nodes required')
    if nodes[0]<response['time_shift'] or nodes[-1]>0:raise ValueError('no paired heat extrapolation')
    if type(quadrature_order) is not int or quadrature_order<2:raise ValueError('quadrature order>=2 required')
    if type(divided_difference_order) is not int or divided_difference_order<8:raise ValueError('explicit divided difference order>=8 required')
    if not np.isfinite(c) or c<=0:raise ValueError('positive explicit paired cutoff probe required')
    from scipy.special import exp1
    frame=lepton_current_hilbert_representation();Y=np.diag(frame['family_Y']).real
    difference=Y[1]**2-Y[2]**2
    samples=_source_core_samples(response['coefficients'],response['representation'],response['reference'],nodes,np.ones((len(nodes),8)),quadrature_order)
    rep=response['representation'];fiber=np.array([0,1,6,7,12,13]);alpha=frame['alpha'][:,fiber][:,:,fiber]
    gen=lepton_unit_trace_gauge_representation()['generators'][:,fiber][:,:,fiber]
    mechanical=sum(-1j*alpha[a]@gen[k]*M[a,k] for a in range(3) for k in range(4))
    radial,_=regular_radial_basis(np.array([WALL]),rep['radial_order']);ov=np.zeros((60,4,6,6),complex)
    for j,label in enumerate(rep['gauge_labels']):
        field=FIELD_ORDER.index(label['field']);value=radial[0,label['radial']]*gen[label['internal']]
        if field==0:ov[j,0]=value
        elif field>=2:ov[j,field-1]=value
    records=[];zero_samples=[]
    for s in samples:
        t=nodes[s['cell']]+s['x']*s['h'];data=finite_common_iterate_at_time(t,response['coefficients'],rep,response['reference'],rho=np.array([WALL]))
        geo=intrinsic_m4_weight_jet(12,data['q'],data['qdot'],data['m'],source_value=data['normal'],source_rate=data['normal_rate'])
        op=finite_common_family_intrinsic_operator(t,response['coefficients'],rep,response['reference'])
        W=s['W'].copy();W[:12,12:]=0.;W[12:,:12]=0.
        zero_samples.append(dict(s,W=W));records.append((geo,op['H']))
    zero=_family_shell_heat_forms(zero_samples,len(nodes),None,fiber)
    fullsize=6*len(nodes);K1=np.zeros((fullsize,fullsize),complex);K2=K1.copy()
    for s,(_,H) in zip(zero_samples,records):
        W=s['W'][np.ix_(fiber,fiber)];omega=s['Omega_t'][np.ix_(fiber,fiber)]
        q=W+omega/s['N'];x,h=s['x'],s['h'];eye=np.eye(6)
        A=np.concatenate((-eye/(h*s['N'])+(1-x)*q,eye/(h*s['N'])+x*q),axis=1)
        V=np.concatenate(((1-x)*eye,x*eye),axis=1);MV=_unit_lepton_mass6(H)@V
        ids=slice(6*s['cell'],6*(s['cell']+2))
        K1[ids,ids]+=s['weight']*(A.conj().T@MV+MV.conj().T@A);K2[ids,ids]+=s['weight']*(MV.conj().T@MV)
    K1=K1[np.ix_(zero['interior'],zero['interior'])];K2=K2[np.ix_(zero['interior'],zero['interior'])]
    # Preserve the EXACT owned L/R sign grading through degenerate eigenvalues.
    # A generic full eigensolver may mix equal poles, defeating stored parity.
    left=np.flatnonzero(np.arange(len(zero['K']))%6<4);right=np.flatnonzero(np.arange(len(zero['K']))%6>=4)
    values=[];vectors=np.zeros_like(zero['vectors']);grading=[];offset=0
    for block,sign in ((left,1),(right,-1)):
        value,vector=eigh(zero['K'][np.ix_(block,block)],zero['M'][np.ix_(block,block)])
        vectors[np.ix_(block,np.arange(offset,offset+len(block)))]=vector
        values.extend(value);grading.extend([sign]*len(block));offset+=len(block)
    ordering=np.argsort(values,kind='stable');lam=np.array(values)[ordering];vectors=vectors[:,ordering];grading=np.array(grading)[ordering]
    if lam[0]<=0:raise ValueError('the computed parity-preserving P0 must remain strictly positive')
    zero['eigenvalues']=lam;zero['vectors']=vectors
    zero['generalized_eigen_residual_relative']=float(np.linalg.norm(zero['K']@vectors-(zero['M']@vectors)*lam)/max(1.,np.linalg.norm(zero['K'])*np.linalg.norm(vectors)))
    eigK0=vectors.conj().T@zero['K']@vectors;eigGram=vectors.conj().T@zero['M']@vectors
    dimension=len(lam)
    ev=np.zeros((6*len(nodes),dimension),complex);ev[zero['interior']]=zero['vectors']
    B=np.zeros((dimension,dimension),complex);C=B.copy();evaluations=[]
    for s,(geo,H) in zip(zero_samples,records):
        i,x,h=s['cell'],s['x'],s['h'];u=(1-x)*ev[6*i:6*(i+1)]+x*ev[6*(i+1):6*(i+2)];du=(ev[6*(i+1):6*(i+2)]-ev[6*i:6*(i+1)])/h
        W=s['W'][np.ix_(fiber,fiber)];omega=s['Omega_t'][np.ix_(fiber,fiber)]
        temporal=du+omega@u;Au=temporal/s['N']+W@u;Mu=_unit_lepton_mass6(H)@u
        B+=s['weight']*(Mu.conj().T@Mu);C+=s['weight']*(Au.conj().T@Mu+Mu.conj().T@Au)
        evaluations.append((u,temporal,Au,Mu,W,geo))
    g=-np.exp(-c*lam)/lam;first,second=_cutoff_divided_differences(lam,c,divided_difference_order)
    parity_outer=grading[:,None]*grading[None,:]
    P1_parity_residual=float(np.max(abs(parity_outer*C+C)))
    P2_parity_residual=float(np.max(abs(parity_outer*B-B)))
    if P1_parity_residual!=0 or P2_parity_residual!=0:
        raise RuntimeError('computed Taylor coefficients lost the exact inherited L/R sign parity')
    D=first*C;Z=first*B+np.einsum('ijk,ij,jk->ik',second,C,C,optimize=True)
    Z=(Z+Z.conj().T)/2;D=(D+D.conj().T)/2
    gram_counter=.5*(lam[:,None]*Z+Z*lam[None,:])+.5*(B*g[None,:]+g[:,None]*B)+.5*(C@D+D@C)
    coefficient=float((np.dot(g,np.diag(B).real)+.5*np.sum(first*abs(C)**2)).real)
    Bnorm=float(np.linalg.norm(B,2));Cnorm=float(np.linalg.norm(C,2));gap=float(lam[0]);maximum=float(lam[-1])
    # Each term uses <=gap/4, hence the complex Taylor-circle numerical range has ReP>=gap/2.
    radius=min(gap/(4*Cnorm) if Cnorm else np.inf,np.sqrt(gap/(4*Bnorm)) if Bnorm else np.inf)
    if not np.isfinite(radius) or max(abs(Y[1:]))>=radius:raise ValueError('the actual fixed-Y expansion lies outside the derived circle')
    remainder_factor=(abs(Y[1])/radius)**4/(1-(abs(Y[1])/radius)**2)-(abs(Y[2])/radius)**4/(1-(abs(Y[2])/radius)**2)
    loads=[];bounds=[];norm_inputs=[];primitive_norms=[];mass_unit_basis=np.array([_unit_lepton_mass6(H) for H in ([1,0],[0,1],[1j,0],[0,1j])])
    for s,(u,temporal,Au,Mu,W,geo) in zip(zero_samples,evaluations):
        N,R=s['N'],s['R'];dN=geo['induced_lapse'].gradient;dR=geo['R4'].gradient;dl=geo['mechanical_connection_lambda'].gradient
        dA=np.zeros((228,6,dimension),complex);dMu=dA.copy()
        dA[:100]=-dN[:,None,None]*temporal[None]/N**2-dR[:,None,None]*(W@u)[None]/R+dl[:,None,None]*((mechanical/R)@u)[None]
        dA[100:160]=np.einsum('jkl,li->jki',ov[:,0],u)/N
        for a in range(3):dA[100:160]+=np.einsum('jkl,li->jki',-1j*np.einsum('kl,jlm->jkm',alpha[a],ov[:,a+1])/R,u)
        dMu[220:224]=np.einsum('bkl,li->bki',mass_unit_basis,u)
        Aread=Au@Z+Mu@D;Mread=Mu*g[None,:]+Au@D
        value=2*np.einsum('ki,bki->b',Aread.conj(),dA).real+2*np.einsum('ki,bki->b',Mread.conj(),dMu).real
        measure=float((np.trace(Z@(Au.conj().T@Au))+np.dot(g,np.sum(abs(Mu)**2,axis=0))+np.trace(D@(Au.conj().T@Mu+Mu.conj().T@Au))-np.trace(gram_counter@(u.conj().T@u))).real)
        value[:100]+=dN/N*measure;loads.append(difference*s['weight']*value)
        # Cauchy/semigroup analytic derivative majorant; its norm/eigen inputs are evaluated binary64, not Arb certificates.
        un,an,mn=(_stored_frobenius_upper(v) for v in (u,Au,Mu));da=_stored_frobenius_upper(dA,axis=(1,2));dm=_stored_frobenius_upper(dMu,axis=(1,2))
        measure_abs=np.zeros(228);measure_abs[:100]=np.nextafter(abs(dN/N)/(1-np.finfo(float).eps),np.inf)
        primitive_norms.append(dict(u_Frobenius_upper=un,Au_Frobenius_upper=an,Mu_Frobenius_upper=mn,
            deltaA_Frobenius_upper=da,deltaMu_Frobenius_upper=dm,abs_deltaN_over_N=measure_abs,
            sample_weight=s['weight'],primitive_complex_entry_count=int(u.size)))
        delta0=s['weight']*(2*an*da+measure_abs*(an*an+maximum*un*un))
        delta1=s['weight']*(2*mn*da+2*an*dm+measure_abs*(2*an*mn+Cnorm*un*un))
        delta2=s['weight']*(2*mn*dm+measure_abs*(mn*mn+Bnorm*un*un))
        norm_inputs.append(np.stack((delta0,delta1,delta2),axis=1))
        bounds.append(remainder_factor*dimension*np.exp(-c*gap/2)/(gap/2)*(delta0+radius*delta1+radius*radius*delta2))
    times=np.array([nodes[s['cell']]+s['x']*s['h'] for s in samples]);load=np.array(loads)
    fiber_grading=np.diag([1]*4+[-1]*2);grading_residual=float(np.linalg.norm(fiber_grading@_unit_lepton_mass6(records[0][1])@fiber_grading+_unit_lepton_mass6(records[0][1])))
    return dict(families={'middle_minus_light':dict(weighted_raw228_cotangent=load,constant_raw228_cotangent=np.sum(load,axis=0))},
        coefficient_time_samples=times,response_time_samples=times-response['time_shift'],parameter=c,
        fixed_Y_middle=float(Y[1]),fixed_Y_light=float(Y[2]),fixed_Y_squared_difference=float(difference),
        stable_even_Y_coefficient=coefficient,paired_heat_value_through_Y_squared=difference*coefficient,
        paired_value_Y_fourth_analytic_majorant=float(dimension*exp1(c*gap/2)*remainder_factor),
        weighted_raw228_Y_fourth_majorant=np.array(bounds),Y_circle_radius=radius,
        normalized_P0_eigenvalues=lam,normalized_P1=C,normalized_P2=B,normalized_LR_sign_grading=grading,
        actual_FE_K0=zero['K'],actual_FE_Gram=zero['M'],actual_FE_K1=K1,actual_FE_K2=K2,
        actual_FE_LR_sign_grading=np.where(np.arange(dimension)%6<4,1,-1),
        computed_generalized_eigenvectors=vectors,computed_eigenbasis_K0=eigK0,computed_eigenbasis_Gram=eigGram,
        eigenbasis_K0_minus_diagonal_operator_norm=float(np.linalg.norm(eigK0-np.diag(lam),2)),
        eigenbasis_Gram_minus_identity_operator_norm=float(np.linalg.norm(eigGram-np.eye(dimension),2)),
        eigenbasis_K1_quadrature_congruence_residual=float(np.linalg.norm(C-vectors.conj().T@K1@vectors)),
        eigenbasis_K2_quadrature_congruence_residual=float(np.linalg.norm(B-vectors.conj().T@K2@vectors)),
        exact_stored_P1_odd_parity_residual=P1_parity_residual,exact_stored_P2_even_parity_residual=P2_parity_residual,
        parity_preserving_normalization='separate complete L and R generalized eigenproblems; no mixed degenerate eigenvectors or discarded modes',
        weighted_raw228_Z0_Z1_Z2_norm_majorant_inputs=np.array(norm_inputs),
        stored_primitive_frobenius_norm_upper_inputs=primitive_norms,
        norm_rounding_policy='IEEE gamma_(4N+16) outward bound on exact stored primitive binary64 entries; subnormal square inputs rejected; |deltaN/N| widened outward for division of stored entries; upstream entry production excluded',
        coefficient_normalization='computed generalized-eigen FEGram coordinates; eigen residual is reported; producer/eigenvector rounding is excluded from an exact-stored certificate',
        generalized_eigen_residual_relative=zero['generalized_eigen_residual_relative'],
        P0_spectral_minimum=gap,P1_operator_norm=Cnorm,P2_operator_norm=Bnorm,
        exact_LR_sign_grading_mass_residual=grading_residual,divided_difference_order=divided_difference_order,
        evaluated_norm_inputs_are_numeric_not_certified_outward_bounds=True,
        Taylor_reference_is_not_a_physical_H_zero_selection=True,
        paired_target_formed_without_subtracting_nearly_equal_family_outputs=True,
        complete_native_or_Pauli_evaluated=False)
