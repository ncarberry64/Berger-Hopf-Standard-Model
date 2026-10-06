"""Family jets on the retained charged-lepton source images.

These are action/source coefficients, NOT heat of a compressed operator.
The geometric heavy-family mass scale kappa is left symbolic. The native
photon body and Pauli-weighted odd heat coefficient are not supplied here.
"""
from decimal import Decimal,localcontext
import numpy as np
from bhsm.interface.muon_owned_connection_application import charged_embedding

MASS_RATIOS={
    'r_e':'0.000297291064564924397291856041345',
    'r_mu':'0.0600744709326097750329819901387',
    'Delta_r':'0.059777179868044850635690134097355',
    'sum_r':'0.060371761997174699430273846180045',
    'difference_squared':'0.00360885367585590662756562359254775'}


def coefficients(source,owned,mixed,child):
    """Actual complete source, typed mass maps and geometric fixed-frame jets."""
    V=source['V_complete'];Xi=source['Xi_complete']
    ni,no=V.shape[-1],V.shape[-2]
    Ti=np.block([[np.zeros((ni//2,ni//2)),np.eye(ni//2)],
                 [np.eye(ni//2),np.zeros((ni//2,ni//2))]])
    To=source['gamma0_output']
    S=np.eye(no,dtype=complex)[:,source['retained_output_indices']]
    # Saved canonical B_H=i partial_tau-H: B_H,s=-kappa Delta_r T.
    mass_B=-To@S;mass_cov=-S
    mixed_B=np.einsum('oi,aoj->aij',mass_B.conj(),V)+np.einsum('aoi,oj->aij',V.conj(),mass_B)
    mixed_cov=np.einsum('oi,aoj->aij',mass_cov.conj(),Xi)+np.einsum('aoi,oj->aij',Xi.conj(),mass_cov)
    E=mixed['external_n0_test_frame_E0']
    gamma=np.einsum('aoi,ij->aoj',V,E)
    retained=gamma[:,source['retained_output_indices']]
    previous=mixed['Gamma_s_unit_source_fermion_boson_external'].transpose(1,0,2)
    gamma_bar=gamma.conj().transpose(0,2,1)
    # A bare current/mass-generator composition. The native squaring-partner
    # identification is NOT inferred from this matrix operation.
    gamma_bar_mass=np.einsum('aeo,oj->aej',gamma_bar,-To)
    Ip=owned['charged_input_embedding']
    Op=charged_embedding(source['output_labels'],owned['output_labels'])
    if np.linalg.norm(Ip.conj().T@Ip-np.eye(ni))>1e-12 or np.linalg.norm(Op.conj().T@Op-np.eye(no))>1e-12:
        raise ValueError('physical charged field-coordinate embeddings are not isometric')
    tau_i=Ip@Ti@Ip.conj().T
    index={tuple(x):j for j,x in enumerate(owned['output_labels'])}
    incidence=np.zeros((len(index),len(owned['input_labels'])),complex)
    for j,x in enumerate(owned['input_labels']):incidence[index[tuple(x)],j]=1
    mass_i=incidence@tau_i
    bg=owned['full_weak_background_unit_action']
    # The saved owned array is H_background; B_H background=-H_background.
    C_bg=mass_i.conj().T@bg+bg.conj().T@mass_i
    C_mass=mass_i.conj().T@mass_i
    actual_V=np.einsum('oi,aij,jk->aok',Op,V,Ip.conj().T)
    contact=-(np.einsum('oi,aoj->aij',mass_i.conj(),actual_V)+
              np.einsum('aoi,oj->aij',actual_V.conj(),mass_i))
    family_gram=owned['effective_family_Gram']
    ratios=np.diag([float(MASS_RATIOS['r_mu']),float(MASS_RATIOS['r_e']),1.])
    family_mass_commutator=family_gram@ratios-ratios@family_gram
    # Exact family-central extension of the actual source and its source image.
    central=max(np.linalg.norm(np.kron(v,np.eye(3))@np.kron(np.eye(ni),ratios)-
        np.kron(np.eye(no),ratios)@np.kron(v,np.eye(3))) for v in V)
    data=dict(mass_tau_input=Ti,mass_tau_output=To,charged_incidence=S,
        B_H_mass_jet_per_kappa_Delta_r=mass_B,D_cov_mass_jet_per_kappa_Delta_r=mass_cov,
        K_sb_canonical_per_kappa_Delta_r=mixed_B,K_sb_covariant_per_kappa_Delta_r=mixed_cov,
        typed_input_embedding=Ip,typed_output_embedding=Op,weak_incidence=incidence,
        weak_mass_tau=tau_i,weak_V_complete=actual_V,weak_K_sb_per_kappa_Delta_r=contact,
        weak_mass_background_form=C_bg,weak_mass_squared_form=C_mass,
        weak_mass_background_output=bg@tau_i,
        Gamma_s_complete=gamma,Gamma_bar_complete=gamma_bar,
        Gamma_bar_B_mass_generator=gamma_bar_mass,
        fixed_child_Gram=child['child_M_test_Gram'],fixed_effective_family_Gram=family_gram,
        source_M_s=np.zeros_like(child['child_M_test_Gram']),source_M_sb=np.zeros_like(child['child_M_test_Gram']))
    proof=dict(complete_photon_shape=list(V.shape),actual_weak_photon_shape=list(actual_V.shape),
        family_centrality_residual=float(central),fixed_family_Gram_mass_commutator=float(np.linalg.norm(family_mass_commutator)),
        canonical_covariant_source_residual=float(np.linalg.norm(np.einsum('oi,aij->aoj',To,V)-Xi)),
        canonical_covariant_mass_residual=float(np.linalg.norm(To@mass_B-mass_cov)),
        canonical_mass_matches_saved=float(np.linalg.norm(Ti-mixed['mass_generator'])),
        saved_open_pair_source_residual=float(np.linalg.norm(retained-previous)),
        complete_open_pair_source_norm=float(np.linalg.norm(gamma)),
        bare_upper_mass_composition_norm=float(np.linalg.norm(gamma_bar_mass)),
        direct_canonical_K_sb_norm=float(np.linalg.norm(mixed_B)),
        direct_covariant_K_sb_norm=float(np.linalg.norm(mixed_cov)),
        direct_typed_weak_K_sb_norm=float(np.linalg.norm(contact)),
        weak_mass_background_form_norm=float(np.linalg.norm(C_bg)),
        neutrino_mass_block_norm=float(np.linalg.norm(tau_i[np.array([x[3]==0 for x in owned['input_labels']])])),
        source_coordinate='b_A amplitude, beta=T_b b, A_Q=sqrt(2) beta; not physical transfer t',
        D_sb='zero at fixed geometry/domain/current source and fixed external test columns',
        local_M_s='zero in fixed geometric source/test frame',local_M_sb='zero in same frame',
        native_M_s=None,native_M_sb=None,moving_external_column_jets=None,
        no_action_index_in_vertex=True,no_measured_mass=True,
        mass_scale='kappa=M_heavy in geometric inverse-clock units remains symbolic; no GeV conversion installed')
    return data,proof


def polynomial_family_check(C_bg,C_mass):
    """Endpoint/integral check of actual squared-form COEFFICIENTS, not heat.

    Delta K = kappa Delta_r a_bg C_bg + kappa^2 Delta(r^2) C_mass.
    a_bg is the supplied point's owned mechanical connection coefficient.
    No numerical kappa, background point, spectral shift or length is chosen.
    """
    from flint import arb,ctx
    ctx.prec=192
    e,mu=map(arb,[MASS_RATIOS['r_e'],MASS_RATIOS['r_mu']]);d=mu-e
    # Two-node Gauss, exact for this affine mass derivative. It is not a
    # family quadrature of the native mixed heat/Pauli functional.
    nodes=[(1-1/arb(3).sqrt())/2,(1+1/arb(3).sqrt())/2]
    const=sum((d/2 for _ in nodes),arb(0))
    quad=sum((d*(e+d*x) for x in nodes),arb(0))
    direct=mu*mu-e*e
    if not (const-d).contains(0) or not (quad-direct).contains(0):
        raise ArithmeticError('polynomial divided-difference check failed')
    with localcontext() as c:
        c.prec=80
        ee,mm=map(Decimal,[MASS_RATIOS['r_e'],MASS_RATIOS['r_mu']])
        exact=str(mm*mm-ee*ee)
        rounded=Decimal(MASS_RATIOS['difference_squared'])
        discrepancy=abs(Decimal(exact)-rounded)
        rounding_limit=Decimal(5)*Decimal(10)**(rounded.as_tuple().exponent-1)
        if discrepancy>rounding_limit:raise ArithmeticError('supplied squared difference inconsistent with retained decimal inputs')
    def encode(x):return dict(arb=str(x),interval=[float(x.lower()),float(x.upper())])
    endpoint1=float(d)*C_bg;endpoint2=float(direct)*C_mass
    integrated1=float(const)*C_bg;integrated2=float(quad)*C_mass
    return dict(endpoint_coefficient_kappa_background=endpoint1,
        endpoint_coefficient_kappa_squared=endpoint2,
        integral_coefficient_kappa_background=integrated1,
        integral_coefficient_kappa_squared=integrated2),dict(
        classification='ACTUAL_FINITE_ACTION_FORM_POLYNOMIAL_CHECK_NOT_NATIVE_HEAT_QUADRATURE',
        ratios=MASS_RATIOS,Delta_r=encode(d),difference_squared=encode(direct),
        integral_mass_squared_coefficient=encode(quad),difference_squared_from_exact_retained_decimals=exact,
        supplied_squared_difference_retained=True,supplied_decimal_rounding_consistent=True,
        nodes=[encode(x) for x in nodes],weights=['1/2','1/2'],
        endpoint_minus_integral_kappa_background=encode(const-d),endpoint_minus_integral_kappa_squared=encode(quad-direct),
        array_comparison_norm=float(np.linalg.norm(endpoint1-integrated1)+np.linalg.norm(endpoint2-integrated2)),
        numerical_heat_length=None,native_heat_quadrature=None,kappa_numerical=None,
        scope='Arb arithmetic encloses polynomial coefficients of supplied decimal ratios; matrices binary64 canonical angular coefficients; no continuum or physical-input bound')
