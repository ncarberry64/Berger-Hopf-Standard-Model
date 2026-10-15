"""Actual nonzero-background intrinsic neutral-H E1 potential through order4.

Reuses saved positive fermion forms, full spin/family matrices, temporal
connection and fixed-Y intrinsic mass vertices. It does not compute a
physical Higgs quartic or replace the supplied numerical cutoff by native c.
Degeneracy is handled by a matrix Taylor expansion around the scalar
temporal term, never by splitting or deleting a spin eigenline.
"""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction
from math import factorial
import argparse
import json
import os
import sys
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'


def _weights():
    pts=list(range(-4,5))
    a=[[Fraction(k**j) for k in pts]+[Fraction(24 if j==4 else 0)] for j in range(9)]
    for i in range(9):
        p=next(j for j in range(i,9) if a[j][i]);a[i],a[p]=a[p],a[i]
        q=a[i][i];a[i]=[v/q for v in a[i]]
        for j in range(9):
            if j!=i:
                q=a[j][i];a[j]=[v-q*w for v,w in zip(a[j],a[i])]
    return [row[-1] for row in a]


def evaluate(repository,output):
    import numpy as np
    import mpmath as mp
    from scipy.special import exp1
    from scipy.linalg import eigvalsh
    root,out=Path(repository).resolve(),Path(output).resolve()
    if out.exists():raise FileExistsError('Preserve earlier scientific applications.')
    sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian
    from bhsm.interface.muon_magnetic_mixed_green import family_fiber_indices
    folder='artifacts/muon_magnetic_mixed_green_20261011/run_3'
    receipt_rel=folder+'/result.json'
    receipt=json.loads((root/receipt_rel).read_bytes())
    c=float(receipt['common_cutoff_probe']);sqrtc=np.sqrt(c)
    if c<=0:raise ValueError('Recorded positive cutoff probe required.')
    scalar_rel=folder+'/scalar_sources.npz'
    if sha256((root/scalar_rel).read_bytes()).hexdigest()!=receipt['array_archives']['scalar_sources.npz']['sha256']:
        raise ValueError('Original intrinsic vertices changed.')
    with np.load(root/scalar_rel,allow_pickle=False) as z:
        fields={s:z[s+'_raw_fields'].copy() for s in ('incoming','outgoing')}
        vertices={(s,f):z[s+f'_family_{f}_bare_scalar_mass_vertices'].copy()
                  for s in fields for f in range(3)}
    spaces={r['side']:{sector:r[sector+'_harmonic_labels'] for sector in ('odd','even')}
            for r in receipt['records']}
    for side in fields:
        if set(map(tuple,spaces[side]['odd'])) & set(map(tuple,spaces[side]['even'])):
            raise ValueError('Odd/even saved labels overlap; no independent-sector sum allowed.')
    pins={receipt_rel:sha256((root/receipt_rel).read_bytes()).hexdigest(),
          scalar_rel:sha256((root/scalar_rel).read_bytes()).hexdigest()}
    weights=[float(w) for w in _weights()]
    records=[];arrays={};groups={}
    order=12

    def coefficients(t):
        with mp.workdps(85):
            x=mp.mpf(float(t))
            return np.array([float(mp.e1(x))]+[float((-1)**n*mp.exp(-x)*sum(
                mp.binomial(n-1,j)*mp.factorial(j)/x**(j+1) for j in range(n))/mp.factorial(n))
                for n in range(1,order+1)])

    def series(S0,S1,S2,coef):
        dim=len(S0);zero=np.zeros_like(S0)
        power=[np.eye(dim,dtype=complex)]+[zero.copy() for _ in range(4)]
        pieces=[]
        for n in range(1,order+1):
            power=[sum((power[k-j]@S for j,S in enumerate((S0,S1,S2)) if j<=k),zero.copy())
                   for k in range(5)]
            pieces.append(np.array([np.trace(v) for v in power])*coef[n]/2)
        pieces=np.array(pieces)
        cumulative=np.cumsum(pieces,axis=0)
        cumulative[:,0]+=len(S0)*coef[0]/2
        return cumulative*np.array([factorial(k) for k in range(5)]),pieces

    def literal_remainder(u,S0,S1,S2,coef):
        # E1(t)I+E1'(t)S(u) is degree<=2 and has exactly zero D4.
        # Evaluate the remaining literal matrix function pointwise, without
        # using the polynomial-in-u coefficient recursion checked above.
        S=S0+u*S1+u*u*S2;power=S@S
        value=coef[2]*np.trace(power)/2
        for n in range(3,order+1):
            power=power@S;value+=coef[n]*np.trace(power)/2
        return value

    def tagged_fourth(S0,S1,S2,coef):
        # Keep the numbers of linear vertices and quadratic contacts as
        # independent word tags. In particular the mixed term is never
        # obtained by subtracting the dominant two-contact contribution.
        keys=[(a,b) for a in range(5) for b in range(3) if a+2*b<=4]
        zero=np.zeros_like(S0)
        power={key:zero.copy() for key in keys};power[(0,0)]=np.eye(len(S0),dtype=complex)
        finalkeys=((4,0),(2,1),(0,2));pieces=[]
        for n in range(1,order+1):
            power={(a,b):power[(a,b)]@S0
                +(power[(a-1,b)]@S1 if a else zero)
                +(power[(a,b-1)]@S2 if b else zero) for a,b in keys}
            pieces.append([12*coef[n]*np.trace(power[key]) for key in finalkeys])
        return np.array(pieces)

    for side in ('incoming','outgoing'):
        arrays[side+'_actual_raw_fields']=fields[side]
        groups[side]={sector:[] for sector in ('odd','even')}
        for family in range(3):
            rel=folder+f'/{side}_family_{family}_fermion_operators.npz'
            blob=(root/rel).read_bytes()
            if sha256(blob).hexdigest()!=receipt['array_archives'][Path(rel).name]['sha256']:
                raise ValueError('Actual saved intrinsic fermion operators changed.')
            pins[rel]=sha256(blob).hexdigest()
            with np.load(root/rel,allow_pickle=False) as z:
                for sector,harmonics in (('odd',20),('even',35)):
                    if len(spaces[side][sector])!=harmonics:raise ValueError('Saved harmonic labels changed.')
                    prefix=side+f'_family_{family}_'
                    A=z[prefix+'A_'+sector].copy();P=z[prefix+'P_'+sector].copy()
                    if A.shape!=(6*harmonics,6*harmonics) or P.shape!=A.shape:
                        raise ValueError('Complete saved six-component family/spin fiber required.')
                    B=np.kron(np.eye(harmonics),vertices[(side,family)][1])
                    # Check the stored vertex against the literal native H
                    # mass map at the actual nonzero background, independently
                    # of the saved mixed-Green source or its tent multiplier.
                    hr=fields[side][260:264]
                    actualH=np.array([hr[:2]+1j*hr[2:]])
                    shift=np.array([[0.,1.]],complex)
                    ids=family_fiber_indices(family)
                    mass0=fixed_y_higgs_hamiltonian(actualH)[0][np.ix_(ids,ids)]
                    mass1=fixed_y_higgs_hamiltonian(actualH+shift)[0][np.ix_(ids,ids)]
                    native_vertex_error=float(np.max(abs(mass1-mass0-vertices[(side,family)][1])))
                    V=A.conj().T@B+B.conj().T@A;Q=2*B.conj().T@B
                    shiftedA=A+np.kron(np.eye(harmonics),mass1-mass0)
                    native_factor_shift_error=float(np.max(abs(shiftedA-A-B)))
                    native_positive_shift=shiftedA.conj().T@shiftedA-A.conj().T@A
                    native_positive_jet_error=float(np.max(abs(native_positive_shift-V-Q/2)))
                    temporal=P-A.conj().T@A
                    mu2=float(np.mean(np.diag(temporal).real))
                    temporal_error=float(np.max(abs(temporal-mu2*np.eye(len(A)))))
                    if mu2<=0 or temporal_error>1e-12*mu2:
                        raise ValueError('Saved scalar temporal term must be retained explicitly.')
                    t=c*mu2
                    # Sterbenz subtraction preserves the stored P baseline:
                    # do not rebuild P from A and silently replace its epoch.
                    S0=c*(P-mu2*np.eye(len(P)))
                    S1=sqrtc*V;S2=Q/2
                    coef=coefficients(t)
                    cumulative,pieces=series(S0,S1,S2,coef)
                    derivative=cumulative[-1]
                    tagged=tagged_fourth(S0,S1,S2,coef)
                    splitvalues=np.sum(tagged,axis=0)
                    split=dict(four_first_variation_vertices=splitvalues[0].real,
                        mixed_vertices_and_contacts=splitvalues[1].real,
                        two_second_variation_contacts=splitvalues[2].real)
                    rho=4.5
                    norm=lambda x:float(np.linalg.norm(x,2))
                    # Hermitian coefficient row/Frobenius bounds avoid using
                    # a nearly degenerate eigensystem as a source filter.
                    bound=lambda x:float(np.sqrt(np.linalg.norm(x,1)*np.linalg.norm(x,np.inf)))
                    sizeS=bound(S0)+rho*bound(S1)+rho*rho*bound(S2)
                    radius=t/2;ratio=sizeS/radius
                    if ratio>=1:raise ArithmeticError('Actual matrix Taylor disk is unresolved.')
                    Mbound=np.exp(-(t-radius))/(t-radius)
                    gamma_tail=len(P)*Mbound*ratio**(order+1)/(2*(1-ratio))
                    fourth_tail=24*gamma_tail/rho**4
                    checks=[]
                    for h in (1.,.5):
                        values=[literal_remainder(h*k,S0,S1,S2,coef) for k in range(-4,5)]
                        fd=np.dot(weights,values)/h**4
                        checks.append(dict(step_u=h,literal_E1_fourth_real=float(fd.real),
                            imaginary_rounding_residual=float(abs(fd.imag)),
                            fourth_relative_error=float(abs(fd-derivative[4])/max(abs(derivative[4]),1e-300))))
                    # Independent eigenspectrum evaluation checks that the
                    # pointwise matrix series equals the literal E1 action.
                    literal_actions=[]
                    for u in (0.,1.,-1.):
                        mat=t*np.eye(len(P))+S0+u*S1+u*u*S2
                        eig=eigvalsh(mat)
                        if eig[0]<=0:raise ArithmeticError('Literal finite variation left positive domain.')
                        literal=float(np.sum(exp1(eig))/2)
                        point=(len(P)*coef[0]+coef[1]*np.trace(S0+u*S1+u*u*S2))/2+literal_remainder(u,S0,S1,S2,coef)
                        literal_actions.append(dict(u=u,action=literal,
                            matrix_series_absolute_discrepancy=float(abs(literal-point))))
                    name=f'{side}_family_{family}_{sector}'
                    for key,value in dict(A=A,P=P,neutral_intrinsic_vertex=B,
                        first_positive_form=V,second_positive_form=Q,
                        scaled_S0=S0,scaled_S1=S1,scaled_S2=S2,
                        derivative_series_partial_sums=cumulative,
                        Taylor_order_contributions=pieces,
                        fourth_by_order_and_linear_quadratic_word_counts=tagged,
                        dimensionless_u_derivatives=derivative,
                        original_H_component_derivatives=derivative*c**(np.arange(5)/2),
                        canonical_real_phi_derivatives=derivative*(c/2)**(np.arange(5)/2)).items():
                        arrays[name+'_'+key]=value
                    row=dict(side=side,family=family,angular_sector=sector,
                        exact_saved_harmonic_labels=spaces[side][sector],
                        harmonic_count=harmonics,fiber_count=6,matrix_dimension=len(A),
                        actual_H_norm=float(np.linalg.norm(fields[side][260:264])),
                        temporal_connection_antiHermitian_factor_norm=float(np.linalg.norm((A-A.conj().T)/2)),
                        material_temporal_term=mu2,scaled_scalar_center=t,
                        saved_P_vs_literal_factor_temporal_max_error=temporal_error,
                        native_fixed_Y_mass_map_vertex_max_error=native_vertex_error,
                        native_literal_Hshift_unit_step_factor_max_error=native_factor_shift_error,
                        native_literal_Hshift_unit_step_positive_form_jet_max_error=native_positive_jet_error,
                        positive_form_source_noncommutator_norm=float(np.linalg.norm((t*np.eye(len(P))+S0)@S1-S1@(t*np.eye(len(P))+S0))),
                        dimensionless_u_derivatives_real=derivative.real.tolist(),
                        original_H_component_derivatives_real=(derivative*c**(np.arange(5)/2)).real.tolist(),
                        canonical_real_phi_derivatives_real=(derivative*(c/2)**(np.arange(5)/2)).real.tolist(),
                        fourth_contributions=split,
                        tagged_fourth_vs_total_absolute_discrepancy=float(abs(np.sum(splitvalues)-derivative[4])),
                        series_order8_to12_fourth_absolute_change=float(abs(cumulative[-1,4]-cumulative[7,4])),
                        maximum_imaginary_trace_rounding_residual=float(np.max(abs(derivative.imag))),
                        analytic_matrix_series_radius=radius,source_u_disk_radius=rho,
                        uniform_source_norm_bound=sizeS,uniform_source_norm_over_series_radius=ratio,
                        analytic_E1_series_trace_remainder_upper=gamma_tail,
                        analytic_fourth_u_remainder_upper=fourth_tail,
                        literal_E1_fd_checks=checks,literal_eigenaction_checks=literal_actions,
                        assigned_cutoff_probe=c,physical_native_cutoff_evaluated=False)
                    records.append(row);groups[side][sector].append(derivative)
                    print(json.dumps(dict(side=side,family=family,sector=sector,
                        quartic_u=float(derivative[4].real),FD=checks,tail=fourth_tail),sort_keys=True),flush=True)
    for name in (
        'muon_magnetic_mixed_green','muon_intrinsic_higgs_positive_green',
        'muon_magnetic_open_lepton_vertex','muon_native_dirac_hamiltonian',
        'muon_primal_intrinsic_lepton_operator','ae31_c2_intrinsic_m4_lepton_action',
        'ae4_stratified_dirac_zeta_induced_owner'):
        rel='src/bhsm/interface/'+name+'.py';pins[rel]=sha256((root/rel).read_bytes()).hexdigest()
    sums={side:{sector:np.sum(values,axis=0).real.tolist() for sector,values in spaces_.items()}
          for side,spaces_ in groups.items()}
    result=dict(classification='ACTUAL_NONZERO_BACKGROUND_INTRINSIC_NEUTRAL_HIGGS_REACHED_FACTOR_E1_TEST_FUNCTIONAL_THROUGH_FOURTH_ORDER',
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),input_hashes=pins,
        records=records,three_family_sum_in_each_saved_space_dimensionless_derivatives=sums,
        declared_source='Background neutral intrinsic slot ReH2 varied by constant h at fixed saved cell coefficients; all original Yukawa/spin/temporal/gauge matrices retained.',
        literal_operator_family='P(h)=P_saved+h(A_dagger B+B_dagger A)+h^2 B_dagger B, B=I_harmonic tensor original neutral intrinsic fixed-Y mass vertex.',
        field_parameter_conventions='u=sqrt(c_probe)*h, canonical real radial phi=sqrt(2)*h; rawH kth derivative=c_probe^(k/2)*u derivative; canonicalphi extra2^(-k/2).',
        scalar_vertices_tent_factor='No3/4 factor: this is constant background-coefficient variation, not the separate boson-tent fluctuation whose mixed vertex contains int b^3/int b^2.',
        supertrace_weight_per_explicit_family_fiber=-1,
        angular_domain='Separate saved odd n1+n3 (20) and even n0+n2+n4 (35) spaces. Exact receipt labels are disjoint Peter-Weyl levels, not nested refinements. Each space has its own complete three-family sum; the two spaces are not combined into a physical determinant.',
        odd_and_even_label_intersection_empty=True,
        quantum_statistics_scope='w=-1 fermion E1 test functional on reached positive factor graph. This does not embed the factors in graded P_cycle or identify a complete integrated physical determinant.',
        temporal_domain='Original frozen coefficient Dirichlet tent fermion cell; no temporal differential complement constructed.',
        no_extra_spin_family_or_chirality_multiplicity_inserted=True,
        temporal_connection_not_removed=True,degenerate_spin_modes_not_split_or_deleted=True,
        method='Noncommuting matrix Taylor E1 around actual scalar temporal center, through power12 with separate per-order contributions; no simple-spectrum assumption.',
        fourth_contact_bookkeeping='Direct ordered-word count tags (4linear,0quadratic),(2linear,1quadratic),(0linear,2quadratic), including arbitrary baseline powers. Mixed contacts are not extracted by subtracting larger quartics.',
        literal_FD_subtraction='Only f(t)I+f_prime(t)S(u), polynomial degree<=2, is analytically removed before fourth finite difference. No quartic or higher coefficient is subtracted or fitted.',
        literal_FD_method='Compensated pointwise E1 matrix-series action through power12 with analytic remainder, independent of polynomial-in-u coefficient extraction; separate direct eigenspectrum E1 action checks at u=0,+1,-1.',
        bounds_are_outward_interval_certificate=False,
        error_scope='Analytic series/Cauchy formulas evaluated in binary64 with85digit scalar coefficients rounded tobinary64; source assembly/eigensystem/input/continuum/physical completion uncertainty not enclosed.',
        scalar_Hessian_or_calibrated_lambda_value_consumed_by_new_calculation=False,
        independent_measured_input_or_fitted_coefficient_added=False,
        classical_scope='AE31 local Higgs action retains positive symbolic lambda_H; AE4 selects one induced owner and retires independent Wilson owners. Neither is replaced by a new coefficient choice here.',
        physical_Higgs_kinetic_Z=None,physical_lambda_H=None,physical_nu_squared=None,
        relative_zeta_eta_and_full_stratified_loop_completion_included=False,
        physical_outgoing_E_B_derivative_evaluated=False,physical_two_spin_normalization=None,
        physical_muon_moment=None,coupled_matching_corrections_applied=0,
        completed_source_D5_profile_campaign_replayed=False)
    out.mkdir(parents=True)
    _compressed_npz(out/'actual_intrinsic_neutral_pencils.npz',arrays)
    result['array_archive_sha256']=sha256((out/'actual_intrinsic_neutral_pencils.npz').read_bytes()).hexdigest()
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256((out/'result.json').read_bytes()).hexdigest()),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();evaluate(a.repository,a.output)
