"""Actual finite incoming field/current algebra for the prepared BHSM pair.

Uses the retained action's full18 representation and fixed-Y vertices.
Physical u/v packet sections, common background and constraints remain explicit
operands. No old enclosure geometry or free-space vacuum is inserted.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import importlib.util
import json
import sys

PAIR_RECEIPT_SHA256='4eb26ad104914e6d78cd686157aecbad83e8bb376e642eb514430377d35fe369'
PAIR_PACKET_SHA256='20db0b3b1a5cb09be1979b0fb24027bbb70f713d4001bd8c50e9807137a136d3'


def current_algebra(annihilators, pair_density):
    """Exact field coefficient operators eta=(a_up,a_down,b_up^dag,b_down^dag)."""
    import numpy as np
    eta=np.asarray([annihilators[0],annihilators[1],
                    annihilators[2].conj().T,annihilators[3].conj().T])
    rho=np.asarray(pair_density,complex)
    reference=np.diag([0.,0.,1.,1.])
    B=np.asarray([[eta[i].conj().T @ eta[j]-reference[i,j]*np.eye(16)
                   for j in range(4)]for i in range(4)])
    first=np.einsum('ab,ijba->ij',rho,B)
    second=np.empty((4,4,4,4),complex)
    for i,j,k,l in np.ndindex((4,4,4,4)):
        second[i,j,k,l]=np.trace(rho @ B[i,j] @ B[k,l])
    return dict(field_coefficient_operators4x16x16=eta,
                bilinear_difference_operators4x4x16x16=B,
                bilinear_difference_expectation4x4=first,
                ordered_bilinear_product_expectation4x4x4x4=second,
                ordered_bilinear_connected4x4x4x4=second-np.einsum('ij,kl->ijkl',first,first),
                finite_field_reference_contraction4x4=reference)


def apply_incoming_packet_current(*, particle_modes, antiparticle_modes,
        canonical_Hamiltonian_vertices, pair_density, annihilators, metadata):
    """Apply an actually supplied common-background packet to original vertices.

    Psi(x)=U_s(x)*a_s+V_s(x)*b_s^dagger in the inherited full18 LR frame.
    Vertices are supplied dHcan/d(field), not an inserted QED coupling.
    Outputs are finite excitation differences, not absolute continuum Wick
    values or a completed metric/scalar/gauge constraint solve.
    """
    import numpy as np
    required=('benchmark_id','action_owner','background_owner','Cauchy_domain_owner',
              'particle_mode_owner','antiparticle_mode_owner','vertex_owner')
    if any(not isinstance(metadata.get(k),str)or not metadata[k]for k in required):
        raise ValueError('same-action collider packet/background/vertex provenance required')
    if metadata['benchmark_id']!='BHSM_NEW_COLLIDER_ELECTRON_POSITRON_TO_MUON_ANTIMUON_V1':
        raise ValueError('another run cannot provide this collider preparation')
    u,v,V=(np.asarray(a,complex)for a in (particle_modes,antiparticle_modes,canonical_Hamiltonian_vertices))
    if u.ndim!=3 or u.shape[1:]!=(18,2)or v.shape!=u.shape:
        raise ValueError('both actual full18 two-spin packet sections are required')
    if V.ndim!=4 or V.shape[0]!=len(u)or V.shape[2:]!=(18,18):
        raise ValueError('same-point full18 original Hamiltonian field vertices required')
    if any(not a.size or not np.isfinite(a).all()for a in (u,v,V)):
        raise ValueError('finite nonempty physical packet/current operands required')
    if np.max(abs(V-V.conj().swapaxes(-1,-2)))>2e-10*max(1.,float(np.max(abs(V)))):
        raise ValueError('Hermitian real-field Hamiltonian vertices required')
    F=np.concatenate((u,v),axis=2)
    K=np.einsum('pai,plab,pbj->plij',F.conj(),V,F)
    algebra=current_algebra(annihilators,pair_density)
    first=algebra['bilinear_difference_expectation4x4']
    second=algebra['ordered_bilinear_product_expectation4x4x4x4']
    j=np.einsum('plij,ij->pl',K,first)
    jj=np.einsum('paij,pbkl,ijkl->pab',K,K,second)
    field=np.einsum('pai,iuv->pauv',F,algebra['field_coefficient_operators4x16x16'])
    field_mean=np.einsum('uv,pavu->pa',np.asarray(pair_density),field)
    return dict(field_operators=field,field_expectation=field_mean,
                Hamiltonian_vertex_expectation=j,
                ordered_Hamiltonian_vertex_product=jj,
                connected_Hamiltonian_vertex_product=jj-j[:,:,None]*j[:,None,:],
                compressed_packet_vertices=K,
                full_constraint_solution_admitted=False)


def validate_action_packet_Cauchy_Gram(*, particle_modes,antiparticle_modes,quadrature):
    """CAR orthonormality on the actual complete represented Cauchy section.

    Weights belong to the canonical chi Haar pairing, supplied with its domain.
    This does not substitute a local point Gram for a global Cauchy pairing.
    """
    import numpy as np
    u,v,w=(np.asarray(a)for a in (particle_modes,antiparticle_modes,quadrature))
    if u.ndim!=3 or u.shape[1:]!=(18,2)or v.shape!=u.shape or w.shape!=(len(u),):
        raise ValueError('complete full18 packet modes and matching Cauchy quadrature required')
    if not np.isrealobj(w)or not np.isfinite(w).all()or np.any(w<=0):
        raise ValueError('positive action-owned complete Cauchy weights required')
    F=np.concatenate((u,v),axis=2)
    defect=np.einsum('p,pai,paj->ij',w,F.conj(),F)-np.eye(4)
    residual=float(np.max(abs(defect)))
    if not np.isfinite(residual)or residual>2e-10:
        raise ValueError('the complete Cauchy CAR Gram fails')
    return dict(complete_Cauchy_Gram_residual=residual,
                positive_frequency_family_trajectory_or_constraints_proved=False)


def construct_action_packet_sections(*, value_map, spatial_derivative_map,
        H, R4, gauge_connection, particle_coefficients, antiparticle_coefficients,
        Cauchy_quadrature):
    """Construct incoming fields and their Dirac time jets from supplied modes.

    The existing original action, rather than a flat/free packet formula,
    supplies the time derivative. The caller supplies a complete background
    basis and two spin columns in each selected spectral charge sector.
    No spectral coefficients, profile or background are selected here.
    """
    import numpy as np
    from bhsm.interface.muon_native_dirac_hamiltonian import canonical_lepton_hamiltonian_maps
    F,D,Cu,Cv=(np.asarray(a,complex)for a in
              (value_map,spatial_derivative_map,particle_coefficients,antiparticle_coefficients))
    if F.ndim!=3 or F.shape[1]!=18 or Cu.shape!=(F.shape[2],2)or Cv.shape!=Cu.shape:
        raise ValueError('same-action complete spatial basis and actual two-spin spectral coefficients required')
    application=canonical_lepton_hamiltonian_maps(value_map=F,spatial_derivative_map=D,
        H=H,R4=R4,gauge_connection=gauge_connection)
    U,V=F@Cu,F@Cv
    gram=validate_action_packet_Cauchy_Gram(particle_modes=U,antiparticle_modes=V,
                                          quadrature=Cauchy_quadrature)
    return dict(particle_modes=U,antiparticle_modes=V,
        particle_spatial_derivatives=np.einsum('paik,ks->pais',D,Cu),
        antiparticle_spatial_derivatives=np.einsum('paik,ks->pais',D,Cv),
        particle_proper_time_first=-1j*application['hamiltonian_map']@Cu,
        antiparticle_proper_time_first=-1j*application['hamiltonian_map']@Cv,
        Cauchy_Gram_application=gram,
        full_background_constraints_or_spectral_selection_proved=False)


def original_material_Gauss_source(*, particle_modes,antiparticle_modes,
        canonical_spatial_density,pair_density,annihilators,normalization_owner,
        test_functions=None,quadrature=None):
    """Actual lepton contribution delta S_l/dA_t in the retained four channels.

    S_l=integral dt dOmega N[chi^dag i*d_tau chi-chi^dag Hcan chi].
    dHcan/dA_t=-i*G_c/N, hence delta S_l/dA_t=dOmega*chi^dag(iG_c)chi.
    The N factor cancels once. The supplied canonical spatial density must
    include the caller's action-owned Haar/field normalization exactly once.
    No EM e, family multiplicity or trace normalization is added here.
    """
    import numpy as np
    from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
    if not isinstance(normalization_owner,str)or not normalization_owner:
        raise ValueError('explicit same-action canonical field/spatial-density normalization owner required')
    u,v=(np.asarray(a,complex)for a in (particle_modes,antiparticle_modes))
    density=np.asarray(canonical_spatial_density)
    if u.ndim!=3 or u.shape[1:]!=(18,2)or v.shape!=u.shape or density.shape!=(len(u),):
        raise ValueError('full18 physical U/V sections and matching canonical spatial density required')
    if not np.isrealobj(density)or not np.isfinite(density).all()or np.any(density<=0):
        raise ValueError('positive finite original action canonical spatial density required')
    if not np.isfinite(u).all()or not np.isfinite(v).all():
        raise ValueError('finite actual physical packet sections required')
    generators=lepton_unit_trace_gauge_representation()['generators']
    F=np.concatenate((u,v),axis=2)
    K=np.einsum('pai,cab,pbj->pcij',F.conj(),1j*generators,F)
    mean=current_algebra(annihilators,pair_density)['bilinear_difference_expectation4x4']
    source=density[:,None]*np.einsum('pcij,ij->pc',K,mean)
    if np.max(abs(source.imag))>2e-10*max(1.,float(np.max(abs(source)))):
        raise ArithmeticError('a real material gauge variation must have a real source')
    result=dict(lepton_material_At_action_source_density=source.real,
        channel_order='unitTr16 H1,H2,H3,HY',normalization_owner=normalization_owner,
        full_Gauss_constraint_or_total_radial_source_evaluated=False,
        central_radial_reduction='For the literal X=dot(A_r)-partial_r(A_t)+[A_t,A_r] and positive electric action, the central radial-only Maxwell variation is +partial_r(q). Thus partial_r(q)=-this_lepton_action_source-other_action_sources, only after their actual common-domain densities and angular/interface terms are supplied.')
    if (test_functions is None)!=(quadrature is None):
        raise ValueError('weak tests and their original quadrature must be supplied together')
    if test_functions is not None:
        tests,w=np.asarray(test_functions,complex),np.asarray(quadrature)
        if tests.ndim!=3 or tests.shape[0]!=len(u)or tests.shape[2]!=4 or w.shape!=(len(u),):
            raise ValueError('tests need (points,tests,4) and matching original quadrature')
        if not np.isrealobj(w)or not np.isfinite(w).all()or np.any(w<=0)or not np.isfinite(tests).all():
            raise ValueError('finite weak tests and positive original quadrature required')
        result['lepton_material_At_weak_action_load']=np.einsum('p,ptc,pc->t',w,tests.conj(),source)
    return result


def run(repository,preparation,output):
    import numpy as np
    root,prep,out=(Path(p).resolve()for p in (repository,preparation,output))
    out.mkdir(parents=True,exist_ok=False)
    rp=prep/'result.json'
    if sha256(rp.read_bytes()).hexdigest()!=PAIR_RECEIPT_SHA256:
        raise ValueError('immutable collider pair receipt changed')
    r=json.loads(rp.read_text(encoding='utf8')); pp=prep/r['artifact']['path']
    if sha256(pp.read_bytes()).hexdigest()!=PAIR_PACKET_SHA256:
        raise ValueError('immutable collider pair packet changed')
    spec=importlib.util.spec_from_file_location('pinned_collider_preparation',prep/'executed_producer.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    sys.path[:0]=[str(root/'src'),str(root)]
    from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation,fixed_y_higgs_hamiltonian
    from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    with np.load(pp,allow_pickle=False)as data:rho=data['pair_Fock_density16'].copy()
    ops=module.annihilators(4);algebra=current_algebra(ops,rho)
    eta=algebra['field_coefficient_operators4x16x16']
    B=algebra['bilinear_difference_operators4x4x16x16']
    rep=lepton_current_hilbert_representation()
    generators=lepton_unit_trace_gauge_representation()['generators']
    temporal=-1j*generators
    spatial=-1j*np.einsum('aij,cjk->acik',rep['alpha'],generators)
    scalar=fixed_y_higgs_hamiltonian(np.array([[1,0],[0,1],[1j,0],[0,1j]],complex))
    Pe=np.diag([0.,0.,1.]);Pmu=np.diag([0.,1.,0.])
    def full_family(P):
        z=np.zeros((18,18),complex)
        z[:12,:12]=np.kron(np.eye(2),np.kron(P,np.eye(2)))
        z[12:,12:]=np.kron(P,np.eye(2));return z
    F_e,F_mu=full_family(Pe),full_family(Pmu)
    vertices=np.concatenate((temporal,spatial.reshape(12,18,18),scalar))
    vertex_hermiticity=float(np.max(abs(vertices-vertices.conj().swapaxes(-1,-2))))
    familycomm=float(max(np.max(abs(V@F_e-F_e@V))for V in vertices))
    field_mean=np.einsum('ab,iba->i',rho,eta)
    component_rhos=[]
    for s in range(2):
        for t in range(2):
            state=(1<<s)|(1<<(2+t));rs=np.zeros((16,16),complex);rs[state,state]=1
            component_rhos.append(rs)
    component_tensors=np.asarray([current_algebra(ops,rs)['ordered_bilinear_product_expectation4x4x4x4']
                                for rs in component_rhos])
    second=algebra['ordered_bilinear_product_expectation4x4x4x4']
    qf=current_algebra(ops,np.eye(16)/16)
    # This is an exact second-order CAR calculation, including aa and b^dag b^dag
    # terms in Psi^dag V Psi; no anomalous term is discarded before multiplication.
    quartic_res=float(np.max(abs(second-component_tensors.mean(axis=0))))
    qfdef=float(np.max(abs(second-qf['ordered_bilinear_product_expectation4x4x4x4'])))
    charge_operator=-(B[0,0]+B[1,1]+B[2,2]+B[3,3])
    charge_mean=float(np.trace(rho@charge_operator).real)
    charge_var=float(np.trace(rho@charge_operator@charge_operator).real-charge_mean**2)
    qfchargevar=float(np.trace((np.eye(16)/16)@charge_operator@charge_operator).real)
    diagnostic=dict(
        original_action_vertex_Hermiticity_residual=vertex_hermiticity,
        original_material_Gauss_vs_Hamiltonian_vertex_numerator_residual=float(np.max(abs(1j*generators+temporal))),
        original_action_electron_family_invariance_residual=familycomm,
        exact_field_expectation_even_pair_maximum=float(np.max(abs(field_mean))),
        exact_pair_total_charge=charge_mean,exact_pair_total_charge_variance=charge_var,
        mean_covariance_quasifree_total_charge_variance=qfchargevar,
        all_256_ordered_current_products_vs_exact_Slater_mixture_residual=quartic_res,
        all_256_ordered_current_products_vs_mean_covariance_quasifree_maximum=qfdef,
        current_bilinear_adjoint_residual=float(np.max(abs(B.conj().swapaxes(-1,-2)-B.swapaxes(0,1)))),
        original_action_full18_current_Gram_identity_residual=float(np.max(abs(rep['Gram']-np.eye(18)))))
    if max(v for k,v in diagnostic.items()if 'quasifree'not in k)>1e-14:
        raise ArithmeticError('action/operator-valued pair current calculation failed')
    if qfdef!=.25 or qfchargevar!=1.:
        raise ArithmeticError('the exact/non-Gaussian current countercheck changed')
    eqs=dict(
        original_full18_evolution='i partial_tau chi=Hcan chi; chi=R4^(3/2)*psi',
        actual_round_slice_Hcan='-i alpha^a(E_a+Omega_a)/R4+(3/2)gamma5/R4+M_fixedY(H)-i Omega_tau',
        incoming_operator_field='chi_hat(x)=sum_s U_s(x)*a_s+V_s(x)*b_s^dagger',
        bilinear_difference='J_V(x)=sum_ij (F(x)^dagger V(x)F(x))_ij B_ij; F=[U_up,U_down,V_up,V_down]',
        first_moment='mean(B)=diag(1/2,1/2,-1/2,-1/2); mean(chi_hat)=0 by even parity',
        Hamiltonian_vertices='delta Hcan/dA_t=(-i G_c)/N; delta Hcan/dA_i=(-i alpha_i G_c)/R4; delta Hcan/dH_r=M_fixedY(basis_r)',
        source_sign='At fixed canonical measure the lepton action variation is -<delta Hcan>; measure/coframe/domain variations must also be included in full metric and event rows.',
        EM_density='rho_Q(x)=-(1/2)*sum_s U_s^dagger U_s+(1/2)*sum_s V_s^dagger V_s, only when U,V are actual Higgs-selected charge -1 Dirac sections and their CAR/antiparticle embedding is bound.',
        total_charge='integral rho_Q=0 for normalized particle and antiparticle sections; this does not imply rho_Q(x)=0.',
        head_on_charge_dipole='For normalized packets centered at z_e=-separation/2 and z_p=+separation/2, integral z*rho_Q=separation; this moment uses only declared centers, not a chosen packet shape.',
        shared_Gauss='delta S_total/dA_t=delta S_gauge/dA_t+delta S_H/dA_t+delta S_lepton/dA_t=0, including interface normal flux on the actual Cauchy domain.',
        original_material_Gauss_lepton_source='delta S_lepton/dA_t^c = canonical_spatial_density*(1/2)*sum_s[U_s^dagger*(iG_c)*U_s-V_s^dagger*(iG_c)*V_s]; G_c are the ORIGINAL unitTr16 H1,H2,H3,HY matrices. No extra e, trace factor or family multiplicity. N*dHcan/dA_t cancels N once.',
        original_central_radial_sign='X=dot(A_r)-partial_r(A_t)+[A_t,A_r], q=M*k*X. For the radial-only central reduction, the Maxwell A_t Euler term is +partial_r(q), so partial_r(q)=-lepton_material_action_source-other_actual_action_sources. General angular/interface loads remain in the full Gauss equation.',
        packet_energy='Each physical packet must be a section in the selected particle/antiparticle spectral subspace of the same action Dirac Cauchy problem, with central-energy expectation E_beam and the declared opposite incoming momentum/center data.',
        width_separation='Width and separation constrain moments of the supplied sections; these moments do not select their spectral coefficients, phases, polarizations or transverse homogeneous fields.')
    src=root/'src/bhsm/interface'
    def cite(name,needle,after=15):
        path=src/name;raw=path.read_bytes();lines=raw.decode('utf8').splitlines()
        matches=[i for i,line in enumerate(lines)if needle in line]
        if len(matches)!=1:raise ValueError('unique source anchor required '+name+' '+needle)
        i=matches[0];return dict(path=str(path),sha256=sha256(raw).hexdigest(),first_line=i+1,last_line=min(len(lines),i+after+1))
    sources=dict(
        canonical_full18_action=cite('muon_native_dirac_hamiltonian.py','def canonical_lepton_hamiltonian_maps(',37),
        canonical_current_representation=cite('muon_native_dirac_hamiltonian.py','def lepton_current_hilbert_representation(',33),
        literal_vertices=cite('muon_magnetic_open_lepton_vertex.py','def canonical_open_field_vertices(',29),
        original_unit_trace_charge_normalization=cite('muon_native_product_factor_graph.py','def lepton_unit_trace_gauge_representation(',16),
        original_radial_curvature_sign=cite('muon_parent_maxwell_full_weak.py','X = at[..., 1, :]-ar[..., 0, :]+_bracket(At, Ar)',5),
        H_selected_charged_injection=cite('muon_magnetic_open_lepton_vertex.py','def charged_dirac_injection(',31),
        native_spatial_trial_scope=cite('muon_primal_intrinsic_lepton_operator.py','def primal_intrinsic_lepton_operator(',13),
        old_constant_angular_basis=cite('muon_primal_intrinsic_lepton_operator.py','value_map=np.eye(18)[None]',8),
        common_raw_background_required=cite('muon_primal_intrinsic_lepton_operator.py',"if raw.shape!=(228,)",9),
        scalar_action_requires_fields=cite('muon_intrinsic_higgs_weak_action.py','def higgs_action(',16),
        old_conformal_constraint_domain=cite('aether_semiclassical_conformal_constraint_v15_38.py','def conformal_constraint_contract(',30),
        old_constraint_solver_inputs=cite('aether_semiclassical_conformal_constraint_v15_38.py','def solve_conformal_hamiltonian_constraint(',34),
        conditional_Higgs_scale=cite('ae31_c2_intrinsic_m4_lepton_action.py','def conditional_higgs_saddle(',23),
        incomplete_physical_poles=cite('ae31_c2_intrinsic_m4_lepton_action.py','def first_variation_and_pole_gate(',26),
        no_implicit_H_background=cite('muon_intrinsic_higgs_weak_action.py','No function chooses a physical Higgs background',5))
    packet=out/'original_full18_vertices_and_exact_pair_incoming_field_current.npz'
    _compressed_npz(packet,dict(**algebra,original_unit_trace_gauge_generators4x18x18=generators,
        original_temporal_Hamiltonian_vertex_numerators4x18x18=temporal,
        original_material_At_action_vertices_iG4x18x18=1j*generators,
        original_spatial_Hamiltonian_vertex_numerators3x4x18x18=spatial,
        original_fixed_Y_Higgs_vertices4x18x18=scalar,
        original_alpha3x18x18=rep['alpha'],original_Gram18=rep['Gram'],
        original_fixed_family_Y3=rep['family_Y'],electron_family_projector18=F_e,
        muon_family_projector18=F_mu,exact_pair_density16=rho,
        exact_total_charge_operator16=charge_operator,component_current_products4x4x4x4x4=component_tensors))
    result=dict(
        classification='EXECUTED_ORIGINAL_ACTION_FULL18_VERTEX_COEFFICIENTS_AND_EXACT_INCOMING_OPERATOR_FIELD_CURRENT_ALGEBRA_WITH_PHYSICAL_PACKET_BACKGROUND_OPEN',
        benchmark_id=r['benchmark_id'],immutable_preparation=dict(path=str(rp),sha256=PAIR_RECEIPT_SHA256,packet_sha256=PAIR_PACKET_SHA256),
        actual_evaluations=diagnostic,equations=eqs,
        output_scope='Actual retained action vertices and exact finite prepared field/current operators were evaluated. No physical U/V packet section or incoming Maxwell/Higgs/metric Cauchy field was supplied or claimed evaluated.',
        operand_roles=dict(
            controllable_preparation='Beam energy, width/spread, separation, timing, polarization and explicitly selected packet family describe the preparation; they do not modify BHSM action coefficients.',
            dynamical_unknowns='The common metric/extrinsic curvature, gauge connection/canonical flux and Higgs/scalar fields respond through the original coupled constraints and evolution. Their sourced residuals cannot be removed by setting the prepared local current to zero.',
            independent_homogeneous_preparation='Incoming radiative/transverse Cauchy data and boundary/asymptotic preparation remain independent state data until chosen or supplied. They are not automatically a zero exterior.',
            mathematical_controls='Quadrature, represented basis and numerical tolerances approximate the owned domain and equations; they are not new physical closure terms.',
            physical_residual='A nonzero sourced Gauss/action residual can be the expected signal of an unevaluated physical current or field variable, or of an incorrect zero-source/background assumption. The finite identities here do not require that physical residual to vanish.'),
        existing_background_routes_checked=[
            'The intrinsic lepton constructor consumes actual H, R4, gauge connection, value and spatial-derivative maps; it selects no stationary background.',
            'The raw228 primal operator consumes the earlier common enclosure fields and uses a constant-angular invariant trial subspace, not a localized two-beam spatial eigenbasis.',
            'The v15.38 conformal constraint solver assumes a particular conformal S7 metric, time-symmetric scalar eta/sigma and normalized FR source. Its callable signature has no electron/positron packet or full18 CAR-current operand; its selected branch is not this collider preparation.',
            'The old Higgs stationary branch uses an explicitly non-action-derived universal GeV calibration and does not solve the new common Einstein/gauge/Higgs/matter constraints. It was not imported.'],
        smallest_actual_missing_input_and_solve=dict(
            preparation='One common collision Cauchy preparation/domain: its background matter/geometry and incoming radiation/asymptotic boundary condition, together with spectral packet coefficients or an explicitly selected experimental packet family. E_beam, width and separation alone fix finitely many moments, not a Cauchy section.',
            constraint='For that supplied preparation, solve the original coupled Hamiltonian/momentum/gauge constraints with the nonzero local packet gauge/Higgs currents and interface fluxes. Setting every bosonic field to an old vacuum or a zero current from <psi>=0 would violate this source application.',
            spectral='On that same regular geometry/domain, build the full18 Dirac spatial/Cauchy operator and its actual particle/antiparticle subspaces; insert supplied packet coefficients, normalize in the complete action Cauchy Gram, and apply these exported original vertices.',
            unselected_freedom='Even for fixed packet charge, Gauss constrains the divergence/longitudinal momentum and its boundary flux. It does not select transverse homogeneous/radiative Cauchy data; they belong to the external preparation. No such fields were set to zero.',
            no_new_BHSM_equation_required_for_this_obstruction=True),
        executable_apis=dict(
            Gauss_source='original_material_Gauss_source(U,V,canonical_spatial_density,rho,annihilators,normalization_owner,tests=None,quadrature=None) returns all four original material A_t action-cotangent source densities and optionally their actual weak loads. It retains distributed density and supplies no net-charge-to-local-zero substitution.',
            packet='construct_action_packet_sections(F,D,H,R4,Omega,Cu,Cv,Cauchy_quadrature) synthesizes U/V and spatial derivatives from supplied same-action basis coefficients, checks the full Cauchy CAR Gram, and executes original canonical_lepton_hamiltonian_maps for both Dirac proper-time first jets. It supplies no default spectral coefficients.',
            current='apply_incoming_packet_current(U,V,canonical_Hamiltonian_vertices,rho,annihilators,metadata) constructs actual operator field, exact current mean and ordered/connected two-current products on supplied physical packet/background maps.',
            pairing='validate_action_packet_Cauchy_Gram(U,V,quadrature) enforces the complete represented canonical CAR pairing, with no replacement by point-fiber Gram.',
            convention='Pure component current applications may be averaged on a common observable/background. Wick of the mean covariance is rejected by the exact two-current tensor.'),
        preserved=dict(head_on_equal_central_energy=True,zero_impact_parameter=True,unpolarized_pair=True,
            numerical_energy_width_separation_profile_unselected=True,muon_pair_is_output_readout=True,
            all_other_outgoing_action_coupled_zoo_preserved=True,measured_mass_or_coupling_fitting=False,
            QED_amplitude_substituted=False,old_C2_geometry_or_history_spliced=False,
            odd_field_mean_used_as_classical_commuting_spinor_source=False),
        source_citations=sources,artifact=dict(path=packet.name,sha256=sha256(packet.read_bytes()).hexdigest()),
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        physical_collider_incoming_Cauchy_fields_or_scattering_prediction_admitted=False)
    serialized=json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n'
    (out/'result.json').write_text(serialized,encoding='utf8',newline='\n')
    (out/'executed_producer.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(path=str(out/'result.json'),sha256=sha256(serialized.encode()).hexdigest(),
                         packet_sha256=result['artifact']['sha256'],actual_evaluations=diagnostic)))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository',type=Path,required=True)
    parser.add_argument('--preparation',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();run(args.repository,args.preparation,args.output)
