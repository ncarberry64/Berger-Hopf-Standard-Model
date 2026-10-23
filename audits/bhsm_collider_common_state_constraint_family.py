"""Parameterized common-state constraint algebra using retained BHSM charges.

This constructs finite CAR spatial-complement and one-regional-Gauss families.
They expose what a physical common Cauchy producer must supply. No exterior,
vacuum, old enclosure, physical packet profile, pole or coupling is chosen.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import importlib.util
import json
import sys


PAIR_SHA='4eb26ad104914e6d78cd686157aecbad83e8bb376e642eb514430377d35fe369'


def spatial_extension(pair_density,annihilators,pe,pp,q):
    """Exact finite CAR extension for two region probabilities, not a profile.

    Mode order: e_up in/out, e_down in/out, p_up in/out, p_down in/out.
    An orthogonal unoccupied complement is used only for this algebraic
    certificate; it is not the chosen physical continuum/background state.
    """
    import numpy as np
    if not 0<=pe<=1 or not 0<=pp<=1:raise ValueError('probabilities must lie in [0,1]')
    a=np.asarray(annihilators);beam=[]
    for spin in range(2):beam.append(np.sqrt(pe)*a[2*spin]+np.sqrt(1-pe)*a[2*spin+1])
    for spin in range(2):beam.append(np.sqrt(pp)*a[4+2*spin]+np.sqrt(1-pp)*a[5+2*spin])
    iso=np.zeros((256,16),complex)
    for state in range(16):
        v=np.zeros(256,complex);v[0]=1
        for mode in reversed(range(4)):
            if state&(1<<mode):v=beam[mode].conj().T@v
        iso[:,state]=v
    rho=np.asarray(pair_density,complex)
    pair_bits=[(1<<s)|(1<<(2+t))for s in range(2)for t in range(2)]
    pure=iso[:,pair_bits]
    weights=np.full(4,.25)
    occupation=np.asarray([[(n>>i)&1 for i in range(8)]for n in range(256)])
    m=occupation[:,0]+occupation[:,2]-occupation[:,4]-occupation[:,6]
    global_m=occupation[:,:4].sum(axis=1)-occupation[:,4:].sum(axis=1)
    j=q*m
    prob=(abs(pure)**2)@weights
    mean=float(prob@j);var=float(prob@(j*j)-mean*mean)
    compressed=iso.conj().T@(j[:,None]*iso)
    full_second=iso.conj().T@((j*j)[:,None]*iso)
    defect=full_second-compressed@compressed
    compressed_mean=np.trace(rho@compressed)
    compressed_var=np.trace(rho@compressed@compressed)-compressed_mean**2
    # Exact one-regional-constraint correlation: only charge/flux labels are
    # constructed. This is not a gauge CCR or BRST/Cauchy representation.
    flux_m=np.arange(-2,3);joint=np.zeros((256,5,4),complex)
    for n in range(256):joint[n,int(m[n])+2]=pure[n]
    gauss_coefficient=q*(m[:,None]-flux_m[None,:])
    gauss_joint=gauss_coefficient[:,:,None]*joint
    reduced=(pure*weights[None,:])@pure.conj().T
    correlated_marginal=reduced*(m[:,None]==m[None,:])
    w=np.zeros((8,4))
    for k,p in enumerate((pe,pe,pp,pp)):w[2*k:2*k+2,k]=[np.sqrt(p),np.sqrt(1-p)]
    P=w@w.T
    region=np.diag([1.,0.,1.,0.,1.,0.,1.,0.])
    leakage=(np.eye(8)-P)@region@w
    expected_leak=np.diag([pe*(1-pe)]*2+[pp*(1-pp)]*2)
    checks=dict(
        beam_Fock_isometry_residual=float(np.max(abs(iso.conj().T@iso-np.eye(16)))),
        exact_pair_embedding_density_residual=float(np.max(abs(iso.conj().T@reduced@iso-rho))),
        local_charge_mean=mean,local_charge_variance=var,
        local_charge_mean_formula_residual=float(abs(mean-q*(pe-pp))),
        local_charge_variance_formula_residual=float(abs(var-q*q*(pe*(1-pe)+pp*(1-pp)))),
        compressed_charge_mean_difference=float(abs(compressed_mean-mean)),
        compressed_only_local_charge_variance=float(compressed_var.real),
        lost_second_moment=float(np.trace(rho@defect).real),
        second_moment_loss_minus_variance=float(abs(np.trace(rho@defect)-var)),
        second_moment_compression_defect_minimum_eigenvalue=float(np.linalg.eigvalsh((defect+defect.conj().T)/2).min()),
        infinitesimal_local_phase_leakage_identity_residual=float(np.max(abs(leakage.conj().T@leakage-expected_leak))),
        prepared_pair_global_charge_mean=float(prob@(q*global_m)),
        prepared_pair_global_charge_second_moment=float(prob@((q*global_m)**2)),
        reduced_regional_Gauss_joint_residual=float(np.max(abs(gauss_joint))),
        reduced_regional_Gauss_joint_norm_residual=float(abs(np.sum(abs(joint)**2*weights[None,None,:])-1)),
        bare_matter_marginal_change_after_flux_correlation=float(np.linalg.norm(correlated_marginal-reduced)),
    )
    identities=[v for k,v in checks.items()if k.endswith('residual')or k.endswith('difference')or k=='second_moment_loss_minus_variance']
    if max(identities)>2e-12:raise ArithmeticError('finite spatial/Gauss identity failed')
    arrays=dict(beam_to_spatial8_one_particle_isometry=w,
        beam_to_spatial8_Fock_isometry256x16=iso,exact_pair_pure_components256x4=pure,
        component_weights4=weights,regional_charge_eigenvalues256=j,
        compressed_regional_charge16=compressed,compressed_full_second_moment16=full_second,
        second_moment_compression_defect16=defect,
        regional_flux_integer_labels5=flux_m,
        regional_flux_constant_part5=-q*flux_m,regional_flux_other_load_coefficient5=-np.ones(5),
        exact_reduced_Gauss_correlated_components256x5x4=joint,
        local_phase_leakage8x4=leakage)
    return arrays,checks


def affine_Gauss_cotangent_lift(*,divergence,right_inverse,total_source,homogeneous_flux):
    """Apply D Pi+j=0 with a supplied right inverse and free homogeneous flux.

    Every physical operand is mandatory. L is a coordinate lift, not a selected
    field or minimum-energy prescription. Compatibility and kernel checks
    prevent a missing boundary/zero mode from being silently projected away.
    This routine constructs a cotangent, not a quantum constrained state.
    """
    import numpy as np
    D,L,j,free=(np.asarray(a,complex)for a in(divergence,right_inverse,total_source,homogeneous_flux))
    if D.ndim!=2 or L.shape!=D.T.shape or j.shape[0]!=len(D)or free.shape[0]!=D.shape[1]or j.shape[1:]!=free.shape[1:]:
        raise ValueError('same actual domain/source/flux operator axes required')
    if any(not np.isfinite(a).all()for a in(D,L,j,free)):raise ValueError('finite supplied operands required')
    product=lambda A,B:np.tensordot(A,B,axes=(1,0))
    compatibility=j-product(D,product(L,j));kernel=product(D,free)
    if max(np.max(abs(compatibility)),np.max(abs(kernel)))>2e-10:
        raise ValueError('source compatibility or homogeneous-flux Gauss condition fails')
    pi=-product(L,j)+free
    return dict(canonical_flux=pi,Gauss_residual=product(D,pi)+j,
        field_or_state_selected=False,other_constraints_or_quantum_realization_proved=False)


def run(repository,preparation,output):
    import numpy as np
    import sympy as sp
    root,prep,out=(Path(p).resolve()for p in(repository,preparation,output))
    out.mkdir(parents=True,exist_ok=False);ws=Path(__file__).resolve().parent
    sys.path[:0]=[str(root/'src'),str(root),str(ws)]
    from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
    from bhsm.interface.ae3_family_harmonic_energy_pullback import MODE_ASSIGNMENTS,ROLE_ORDER
    from bhsm.interface.muon_intrinsic_lepton_primal import classical_bosonic_body_source
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    pp=prep/'result.json'
    if sha256(pp.read_bytes()).hexdigest()!=PAIR_SHA:raise ValueError('immutable pair preparation changed')
    old=json.loads(pp.read_text(encoding='utf8'));packet=prep/old['artifact']['path']
    if sha256(packet.read_bytes()).hexdigest()!=old['artifact']['sha256']:raise ValueError('pair packet changed')
    spec=importlib.util.spec_from_file_location('_retained_pair_creation',prep/'executed_producer.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    with np.load(packet,allow_pickle=False)as z:rho=z['pair_Fock_density16'].copy()
    if ROLE_ORDER!=('heavy','middle','light')or MODE_ASSIGNMENTS['charged_lepton'][2]!=(9,3):
        raise ValueError('frozen electron family map changed')
    generators=lepton_unit_trace_gauge_representation()['generators']
    q=complex((1j*generators[3])[16,16])
    if abs(q.imag)>1e-15 or q.real>=0 or abs(q.real*q.real-.3)>1e-15:
        raise ValueError('original unitTr16 right-singlet hypercharge normalization changed')
    q=float(q.real);a=mod.annihilators(8);archives={};records=[]
    for label,pe,pg in [('algebraic_half_half',.5,.5),('algebraic_quarter_threequarter',.25,.75),('algebraic_endpoint',0.,1.)]:
        arrays,checks=spatial_extension(rho,a,pe,pg,q)
        path=out/(label+'.npz');_compressed_npz(path,arrays);archives[path.name]=sha256(path.read_bytes()).hexdigest()
        records.append(dict(label=label,parameters=dict(p_e=pe,p_p=pg),checks=checks))
    p,r,Q,b,c=sp.symbols('p_e p_p q_unitTrY b_other_flux c_classical_flux',real=True)
    mean=Q*(p-r);variance=Q**2*(p*(1-p)+r*(1-r))
    mean_square=sp.expand((c+b+mean)**2+variance)
    minimizer=sp.solve(sp.diff(mean_square,c),c)[0]
    minimum=sp.simplify(mean_square.subs(c,minimizer)-variance)
    if minimum!=0:raise ArithmeticError('classical-flux variance identity failed')
    m=sp.symbols('m_regional',integer=True)
    gauss=sp.simplify((-Q*m-b)+Q*m+b)
    if gauss!=0:raise ArithmeticError('correlated regional Gauss identity failed')
    body=classical_bosonic_body_source(1)
    src=root/'src/bhsm/interface'
    def cite(path,needle,after=13):
        raw=path.read_bytes();lines=raw.decode('utf8').splitlines();hits=[i for i,l in enumerate(lines)if needle in l]
        if len(hits)!=1:raise ValueError('a unique source anchor is required '+needle)
        i=hits[0];return dict(path=str(path),sha256=sha256(raw).hexdigest(),first_line=i+1,last_line=min(len(lines),i+after+1))
    citations=dict(
        original_unit_trace_charge=cite(src/'muon_native_product_factor_graph.py','def lepton_unit_trace_gauge_representation(',16),
        coupled_source_representation=cite(src/'muon_intrinsic_coupled_primal.py',"source_representation='CLASSICAL_BOSONIC_BODY'",5),
        actual_coupled_source=cite(src/'muon_intrinsic_coupled_primal.py',"J_H=classical_bosonic_body_source(",6),
        body_is_not_quantum_load=cite(src/'muon_intrinsic_lepton_primal.py','def classical_bosonic_body_source(',25),
        scalar_quantum_sector_separate=cite(src/'muon_intrinsic_higgs_gauge_action.py','The quantum determinant load is a separate sector.',1),
        parameter_family_vs_physical_solve=cite(src/'muon_intrinsic_coupled_primal.py','def require_physical_solve_binding(',9),
        physical_BRST_scope=cite(src/'ae4_current_c2_stop_gauge_brst_calderon.py',
            '"AE4_CURRENT_C2_PHYSICAL_EVENT_GAUGE_BRST_BLOCK_DERIVED": False',4),
        earlier_finite_difference_scope=cite(ws/'bhsm_collider_incoming_field_current.py',
            'Outputs are finite excitation differences, not absolute continuum Wick',3),
        native_free_retarded_scope=cite(src/'muon_birth_fermion_state_representation.py','retarded="G_R=',4))
    result=dict(
        classification='EXACT_PARAMETERIZED_CAR_SPATIAL_COMPLEMENT_AND_REDUCED_REGIONAL_GAUSS_CONSTRAINT_FAMILY_WITH_COMMON_PHYSICAL_CAUCHY_STATE_OPEN',
        preparation_authority='User-selected e−e+ collider, head-on equal central energy and unpolarized baseline. No numerical energy, width, separation, profile, geometry or incoming radiation is newly selected.',
        immutable_preparation=dict(path=str(pp),sha256=PAIR_SHA,packet_sha256=old['artifact']['sha256']),
        actual_native_coefficients=dict(unitTr16_right_charged_singlet_Y=q,square=q*q,
            derived_square_exact='3/10',coupling_added=False,component_scope='The active right charged-singlet fiber of the frozen light family, full18 indices16,17, supplies the numerical charge normalization. It is not selected as a physical electron pole or a replacement for the full LR packet.'),
        parameter_family=dict(
            p_e='Integral over an arbitrary region D of the action-normalized electron packet density on its actual Cauchy slice; not a chosen width or spatial profile.',
            p_p='Corresponding positron region probability. Up/down spins share an envelope in this declared unpolarized algebraic family.',
            ranges='0<=p_e,p_p<=1',other_load='b_other_flux is retained as a symbolic commuting other-load parameter; full other quantum loads require their supplied operator and state.',
            numerical_points_are_algebraic_certificates_not_physical_beam_preparations=True),
        exact_equations=dict(
            local_mean=str(mean),local_variance=str(variance),
            compression='P J^2 P-(PJP)^2=P J(1-P)J P; it is positive semidefinite for a Hermitian local charge.',
            local_phase_leakage='||(1-P)1_D f||^2=p*(1-p); a finite beam sector with0<p<1 is not invariant under local phase multiplication.',
            smooth_domain_version='For a smooth real gauge parameter g, ||(1-P)g f||^2=<f,g^2 f>-||P g f||^2. A nonzero finite smooth L2 subspace on a connected open region cannot be invariant under all smooth multipliers: powers of a multiplier varying on the support generate arbitrarily many independent functions.',
            classical_flux_minimum='min_c <(c+b_other_flux+J_D)^2>=Var(J_D), attained at c=-b_other_flux-<J_D>. This tests full operator constraint only when that is the intended target; a declared semiclassical mean constraint has a different, weaker requirement.',
            correlated_finite_Gauss='V_G|n>=|n>|flux_label=m(n)>; Phi(m,b)=-q*m-b; (Phi+J_D+b)V_G=0 for arbitrary b.',
            correlated_other_observables='V_G is an isometry. Abstract input observables are preserved under V_G O V_G^dagger, while the bare fermion marginal generally dephases across regional charge sectors. This is not an unchanged bare beam covariance or a demonstrated physical dressing.',
            cotangent_lift='Pi=-L*j+Pi_free, D*L*j=j, D*Pi_free=0; supplied boundary compatibility and all homogeneous flux data are mandatory. Changing the coordinate lift changes the homogeneous representative, not the physical selection.'),
        actual_computations=records,
        symbolic_checks=dict(classical_flux_minimum_identity=str(minimum),correlated_regional_Gauss_identity=str(gauss)),
        original_coupled_consumer_audit=dict(
            source_representation='CLASSICAL_BOSONIC_BODY',
            evaluated_body_source_classification=body['classification'],
            evaluated_body_J_H_max=float(np.max(abs(body['J_H_body']))),
            quantum_induced_H_load_evaluated=body['quantum_induced_H_load']is not None,
            meaning='This derived classical-body zero is correct in its stated scope. It is not the prepared pair current or an action-owned declaration of zero quantum current.',
            target_convention='The supplied coupled routine is classical-body; retained AE4 also has quantum determinant/BRST sectors. No source in this audit declares that a prepared pair may be completed by a mean-field closure alone. We therefore evaluate the mean and quantum constraint distinctions without imposing either new physical closure.'),
        construction_scope=dict(
            smallest_constructed='An exact finite spatial CAR extension of the already prepared pair, and a one-regional-Gauss kernel correlation parameterized by overlap probabilities and an unselected other-load shift.',
            physical_Cauchy_state=False,physical_Maxwell_Higgs_gravity_constraint_solution=False,
            physical_gauge_CCR_or_BRST_representation_selected=False,
            full_field_particle_antiparticle_embedding_selected=False,
            spectral_packet_or_background_selected=False,
            prior_finite_excitation_difference_current_results_remain_valid=True,
            zero_continuum_vacuum_or_exterior_selected=False),
        precise_missing_operands=[
            'A same-action collision Cauchy geometry/domain, canonical spatial pairing and gauge/Higgs data or their coupled constraint solution; no old C2 or v15 vacuum is a substitute.',
            'Actual positive/negative-frequency full18 packet sections and their spatial complement on that domain, with beam energy/width/separation/profile as explicit preparation inputs or selected parameter family.',
            'The action-owned state/source application specifying classical-body, explicitly justified semiclassical expectation, or full quantum/BRST constraint treatment, including induced Higgs/stress loads where used.',
            'For a full quantum target, an actual joint gauge/matter representation/domain and admissible incoming state or dressing, including normal flux and radiative/homogeneous data. The finite flux-label isometry above does not supply the physical CCR, spectrum or boundary condition.',
            'For local interacting products and the magnetic-moment vertex, actual common-domain propagators/current products, subtraction and physical pole/residue extraction. Four prepared modes alone are not the full local field algebra.'
        ],
        free_retarded_qualification='The spatial-complement obstruction does not make a free retarded Green operator depend on a chosen matter covariance. State-independent free propagation and algebraically cancelled contractions retain their existing scope.',
        prediction_scope='No muon magnetic moment, measured mass/coupling calibration, Pauli coefficient, collider rate or full outgoing realization is computed or fitted.',
        no_completed_source_D5_profile_canonical_or_pairing_integration_restarted=True,
        archives=archives,source_citations=citations,
        input_hashes={str(root/'AGENTS.md'):sha256((root/'AGENTS.md').read_bytes()).hexdigest(),
                     str(prep/'executed_producer.py'):sha256((prep/'executed_producer.py').read_bytes()).hexdigest()},
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    text=json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n'
    (out/'result.json').write_text(text,encoding='utf8',newline='\n');(out/'executed_producer.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(path=str(out/'result.json'),sha256=sha256(text.encode()).hexdigest(),
        actual_computations=records,symbolic_checks=result['symbolic_checks'])))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository',required=True);p.add_argument('--preparation',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.repository,a.preparation,a.output)
