"""Spin-summed measured-mass decay of the complete reached local tensor.

The contact tensor is not replaced by a scalar V-A fit.  Its applicability
as a physical low-energy local operator and finite radiative corrections
remain separate from this explicit three-body phase-space application.
"""
from __future__ import annotations
import numpy as np
from numpy.polynomial.legendre import leggauss

PAULI=np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
SOURCE='https://doi.org/10.1103/PhysRevD.87.052003'


def _spherical_rule(order):
    z,w=leggauss(order);phi=2*np.pi*np.arange(2*order)/(2*order)
    x=np.sqrt(1-z*z)
    n=np.array([[xj*np.cos(p),xj*np.sin(p),zj]for xj,zj in zip(x,z)for p in phi])
    weights=np.repeat(w/(4*order),2*order)
    return n,weights


def _charged_density(energy,momentum,mass,charge):
    spatial=np.einsum('pi,ijk->pjk',momentum,PAULI)
    identity=np.eye(2)[None]*energy[:,None,None]
    off=(-charge)*mass*np.eye(2)[None]*np.ones((len(energy),1,1))
    return np.concatenate((np.concatenate((identity-spatial,off),axis=2),
                           np.concatenate((off,identity+spatial),axis=2)),axis=1)


def tensor_tree_decay_rate(tensor,*,muon_mass_GeV,electron_mass_GeV,
                           radial_order=48,angular_order=3,muon_charge=1,
                           temporal_coefficients=None,action_energy_unit=None,
                           relative_angular_order=None):
    """Integrate the full positive/negative muon on-shell contact decay.

    C_abcd multiplies (nu_mu^dagger_a mu_b)(e^dagger_c nu_e_d).
    C is interpreted in GeV^-2 here; equivalently a dimensionless action
    C/E_kappa^2 gives the returned rate divided by E_kappa^4.
    Positive muon uses the conjugate operator and v completeness with
    negative mass offdiagonals.  The initial spin is averaged once.
    """
    C=np.asarray(tensor,complex);M,m=map(float,(muon_mass_GeV,electron_mass_GeV))
    if (C.shape!=(2,4,4,2)or not np.isfinite(C).all()or
        not np.isfinite([M,m]).all()or not 0<=m<M or muon_charge not in(-1,1)
        or not isinstance(radial_order,int)or radial_order<4
        or not isinstance(angular_order,int)or angular_order<3):
        raise ValueError('complete finite contact tensor, measured ordered masses and convergent quadrature required')
    mu=M*np.block([[np.eye(2),-muon_charge*np.eye(2)],[-muon_charge*np.eye(2),np.eye(2)]])/2
    coefficient=np.einsum('abcd,efgh,bf->acdegh',C,C.conj(),mu,optimize=True)
    if temporal_coefficients is not None:
        coefficients=np.asarray(temporal_coefficients,complex)
        if (coefficients.ndim!=5 or coefficients.shape[1:]!=C.shape or
            not np.isfinite(coefficients).all()or action_energy_unit is None or
            not np.isfinite(action_energy_unit)or action_energy_unit<=0):
            raise ValueError('same tensor temporal coefficients and explicit positive action unit required')
    elif action_energy_unit is not None:
        raise ValueError('action unit only applies to an explicit temporal symbol')
    normals,weights=_spherical_rule(angular_order)
    # SO(3) orientation is a polynomial in three final momenta, hence
    # degree3.  Integrate all Euler angles, and separately the neutrino
    # relative polar angle.  Frequency depends only on that relative
    # cosine; a degree14 temporal tensor requires degree30 spin square.
    relative_order=(2 if temporal_coefficients is None else len(coefficients)+1)
    if relative_angular_order is not None:relative_order=relative_angular_order
    if not isinstance(relative_order,int)or relative_order<2:raise ValueError('explicit relative angular quadrature required')
    z,zw=leggauss(relative_order);phi=2*np.pi*np.arange(2*angular_order)/(2*angular_order)
    directions=[];qhat=[];aw=[]
    for normal,weight in zip(normals,weights):
        sine=np.sqrt(1-normal[2]**2)
        e_theta=np.array([normal[2]*normal[0]/sine,normal[2]*normal[1]/sine,-sine])
        e_phi=np.array([-normal[1]/sine,normal[0]/sine,0.])
        for cosine,relative_weight in zip(z,zw):
            for p in phi:
                directions.append(normal)
                qhat.append(-cosine*normal+np.sqrt(1-cosine*cosine)*(np.cos(p)*e_theta+np.sin(p)*e_phi))
                aw.append(weight*relative_weight/(4*angular_order))
    n=np.array(directions);q=np.array(qhat);aw=np.array(aw)
    y,yw=leggauss(radial_order);y=(y+1)/2;yw=yw/2;smax=(M-m)**2
    rates=[];imag=[];lowest=[]
    for v in y:
        s=smax*(1-v*v);jacobian=2*smax*v
        Ee=(M*M+m*m-s)/(2*M);p=np.sqrt(max(0,Ee*Ee-m*m));Eq=M-Ee
        b=-n;dot=np.sum(b*q,axis=1);root=np.sqrt(s)
        En=Eq/2+p*dot/2;Ea=Eq-En
        pn=root*q/2+((Eq-root)*dot/2+p/2)[:,None]*b
        pa=p*b-pn
        rho_n=En[:,None,None]*np.eye(2)-np.einsum('pi,ijk->pjk',pn,PAULI)
        rho_a=Ea[:,None,None]*np.eye(2)-np.einsum('pi,ijk->pjk',pa,PAULI)
        rho_e=_charged_density(np.full(len(n),Ee),p*n,m,muon_charge)
        if temporal_coefficients is None:
            amplitudes=np.einsum('acdegh,pea,pgc,pdh->p',coefficient,rho_n,rho_e,rho_a,optimize=True)
        else:
            frequency=(M-En)/action_energy_unit
            current=np.einsum('pk,kabcd->pabcd',frequency[:,None]**np.arange(len(coefficients)),coefficients)
            node_coefficient=np.einsum('pabcd,pefgh,bf->pacdegh',current,current.conj(),mu,optimize=True)
            amplitudes=np.einsum('pacdegh,pea,pgc,pdh->p',node_coefficient,rho_n,rho_e,rho_a,optimize=True)
        averaged=np.sum(aw*amplitudes)
        rates.append(jacobian*p*averaged.real/(128*np.pi**3*M*M))
        imag.append(abs(averaged.imag));lowest.append(float(np.min(amplitudes.real)))
    rate=float(yw@rates)
    if rate<0:raise ArithmeticError('negative spin-summed contact decay rate')
    x=(m/M)**2
    phase=1-8*x+8*x**3-x**4-12*x*x*np.log(x)if x else 1.
    return dict(tree_rate_GeV_for_tensor_GeV_minus2=rate,
        tree_rate_coefficient_GeV5=rate,
        rate_per_muon_mass_fifth=rate/M**5,
        physical_masses_GeV=np.array([M,m]),muon_charge=muon_charge,
        quadrature_radial_order=radial_order,quadrature_angular_order=angular_order,
        quadrature_relative_angular_order=relative_order,
        integrated_radial_nodes=y,integrated_radial_weights=yw,
        integrated_rate_density=np.array(rates),
        maximum_spin_sum_imaginary_residual=max(imag),
        minimum_sample_spin_sum=min(lowest),
        exact_massive_VA_phase_factor=phase,
        VA_unit_coefficient_analytic_rate=M**5*phase/(1536*np.pi**3),
        phase_space='dGamma=ds*p/(128*pi^3*M^2)*angular_average(spin_summed_|M|^2); initial spin average1/2',
        external_convention='matched on-shell masses and normalized local chiral Dirac spin sums; point current angular integral already1',
        source=SOURCE,source_equations='Muon lifetime normalization Eq.(1); explicit independent spin sums and factored two-body phase space',
        physical_local_operator_domain_identified=False,physical_radiative_correction_completed=False,
        physical_unit_selected=False,physical_F2=None)


def temporal_charged_current_series(coefficients,quotient_lift,joint_trace_map,
        right_vertices,left_vertices,*,maximum_frequency,terms=8):
    """Source-contracted temporal series and uniform grouped remainder.

    A^-1=(I+X)^-1 A0^-1, X=omega X1+omega^2 X2.  It is enough
    that ||X^2||<1 even when the nonnormal ||X|| exceeds1.  Every original
    field/current source is retained; no pole or eigenmode compression.
    Bounds below are evaluated binary estimates of the stated exact
    matrix inequality, excluding solve/power/norm production rounding.
    """
    if not all(np.isrealobj(x)for x in(quotient_lift,joint_trace_map)):
        raise ValueError('the inherited real trace maps must be real before conversion')
    C=np.asarray(coefficients,complex);Q=np.asarray(quotient_lift,float)
    T=np.asarray(joint_trace_map,float);R=np.asarray(right_vertices,complex)
    L=np.asarray(left_vertices,complex);w=float(maximum_frequency)
    if (C.shape!=(3,84,84)or Q.shape!=(84,80)or T.shape!=(24,84)
        or R.shape!=(24,2,4)or L.shape!=(24,4,2)or not np.isfinite(w)
        or w<0 or not isinstance(terms,int)or terms<2 or terms%2
        or any(not np.isfinite(v).all()for v in(C,Q,T,R,L))):raise ValueError('complete current maps and even source-series order required')
    P=np.array([Q.T@c@Q for c in C]);X=np.array([np.linalg.solve(P[0],p)for p in P[1:]])
    left=R.reshape(24,8).T@T@Q;rhs=Q.T@T.T@L.reshape(24,8)
    base=np.linalg.solve(P[0],rhs)
    square=np.array([X[0]@X[0],X[0]@X[1]+X[1]@X[0],X[1]@X[1]])
    rho2=sum(w**(k+2)*np.linalg.norm(v,2)for k,v in enumerate(square))
    if rho2>=1:raise ArithmeticError('same-pencil grouped temporal expansion has not reached a contraction')
    result=np.zeros((2*terms-1,8,8),complex);power=np.eye(80)[None]
    result[0]=left@base
    for j in range(1,terms):
        nxt=np.zeros((len(power)+2,80,80),complex)
        for k,p in enumerate(power):
            nxt[k+1]+=p@X[0];nxt[k+2]+=p@X[1]
        power=nxt
        for k,p in enumerate(power):result[k]+=(-1)**j*left@p@base
    tail=(np.linalg.norm(left,2)+w*np.linalg.norm(left@X[0],2)+w*w*np.linalg.norm(left@X[1],2))*rho2**(terms//2)/(1-rho2)*np.linalg.norm(base)
    first=sum(w**k*np.linalg.norm(result[k])for k in range(1,len(result)))
    return dict(temporal_current_coefficients=result.reshape(len(result),2,4,4,2),
        temporal_operator_X_coefficients=X,
        maximum_frequency=w,grouped_square_norm_estimate=rho2,
        uniform_tensor_series_tail_estimate=tail,
        uniform_tensor_static_difference_estimate=first+tail,
        source_series_terms=terms,
        exact_matrix_series_identity='sum_j=0..terms-1(-X)^j + X^terms*(I-X)*(I-X^2)^-1 = (I+X)^-1, even terms',
        error_scope='binary estimates of exact finite matrix series inequality; original solve/powers/operator norms and source production not outward enclosed',
        spatial_momentum_remainder_evaluated=False,physical_unit_selected=False)


def tensor_rate_tail_estimate(rate,tensor_tail,*,muon_mass_GeV):
    """Convert a uniform tensor Frobenius error to an absolute rate estimate.

    The spin densities have norms at most M,2Ee,2En,2Ea and their
    product is at most2*M^4.  Integrating p<=M/2 and ds<=M^2 then
    gives Q(deltaC)<=B^2*M^5/(128*pi^3).  Cauchy-Schwarz supplies
    the cross term.  A binary input bound remains a binary estimate;
    no source/solve error or spatial-momentum completion is enclosed.
    """
    v=np.asarray([rate,tensor_tail,muon_mass_GeV],float)
    if not np.isfinite(v).all()or v[0]<0 or v[1]<0 or v[2]<=0:
        raise ValueError('nonnegative rate/tensor tail and positive mass required')
    q=tensor_tail**2*muon_mass_GeV**5/(128*np.pi**3)
    return dict(tail_squared_rate_estimate=q,
        absolute_rate_series_tail_estimate=2*np.sqrt(rate*q)+q,
        error_scope='exact spin-density/phase-space inequality evaluated in binary64, conditional on the supplied tensor bound; upstream source/solve/norm rounding and spatial momentum excluded')


def conditional_decay_unit(rate,*,lifetime_seconds,hbar_GeV_seconds):
    """Solve the executed contact-rate matching equation, conditionally.

    No measured anomaly or magnetic moment enters.  This is the positive
    root of Gamma_measured=C_rate/E_kappa^4, not a V-A tensor replacement.
    """
    v=np.array([rate,lifetime_seconds,hbar_GeV_seconds],float)
    if not np.isfinite(v).all()or np.any(v<=0):raise ValueError('positive rate, lifetime and hbar required')
    observed=hbar_GeV_seconds/lifetime_seconds;scale=(rate/observed)**.25
    return dict(conditional_E_kappa_GeV=scale,measured_rate_GeV=observed,
        reconstructed_rate_GeV=rate/scale**4,
        conditional_log_scale_derivatives=np.array([.25,.25,-.25]),
        matching_equation='E_kappa=(C_rate*tau_mu/hbar)^(1/4)',
        physical_operator_and_radiative_matching_completed=False,
        physical_unit_selected=False)
