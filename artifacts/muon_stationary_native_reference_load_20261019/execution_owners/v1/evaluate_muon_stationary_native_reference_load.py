"""Consume a freshly evaluated native component; never rerun prior solves."""
from __future__ import annotations
import os
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
from pathlib import Path
from hashlib import sha256
import argparse,json,platform,sys
import numpy as np
import scipy

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
from bhsm.interface.muon_stationary_native_reference_load import (
    lorentz_load, original_operator_checks, FREQUENCY_PANELS,
)
from bhsm.interface.muon_coupled_reference_replacement import MULTIPLIER_ROWS
from bhsm.interface.retained_response.finite_time_response import write_npz


def summary(g,area,active,held):
    m=g[MULTIPLIER_ROWS];a=area[MULTIPLIER_ROWS]
    outside=m-a*np.dot(a,m)/np.dot(a,a)
    return dict(original150_max=float(np.max(abs(g[:150]))),
        geometry62_max=float(np.max(abs(g[:62]))),
        multiplier24_max=float(np.max(abs(m))),
        multiplier_outside_area_max=float(np.max(abs(outside))),
        active52_max=float(np.max(abs(g[62+active]))),
        held_radial_wall32_max=float(np.max(abs(g[62+held]))),
        Higgs4_max=float(np.max(abs(g[146:150]))),
        complete_physical_residual=None)


def run(output):
    if output.exists():raise FileExistsError('preserve completed applications; choose a new run')
    source=ROOT/'artifacts/muon_coupled_reference_replacement_20261019/run_2/coupled_replacement.npz'
    receipt_path=source.with_name('result.json');old=json.loads(receipt_path.read_bytes())
    if sha256(source.read_bytes()).hexdigest()!=old['arrays']['sha256']:
        raise ValueError('completed coupled application identity changed')
    for rel,h in old['input_sha256'].items():
        if sha256((ROOT/rel).read_bytes()).hexdigest()!=h:raise ValueError('ancestry input changed: '+rel)
    with np.load(source,allow_pickle=False) as z:saved={k:z[k].copy() for k in z.files}
    x=saved['provisional_iterate151'];c=1.  # declared numerical coordinate, NOT a physical cutoff choice.
    actual=lorentz_load(x,cutoff=c,points_per_panel=24)
    anchor=lorentz_load(x,cutoff=c,points_per_panel=24,anchor=True)
    actual_check=lorentz_load(x,cutoff=c,points_per_panel=32)
    anchor_check=lorentz_load(x,cutoff=c,points_per_panel=32,anchor=True)
    g=saved['after_known_gradient'];k=saved['after_known_hessian']
    active=saved['original_active52_indices84'].astype(int)
    held=saved['original_held32_indices84'].astype(int)
    area=saved['after_area_gradient_per_gamma']
    consumed=g+actual['gradient'];jac=k+actual['hessian']
    relg=actual['gradient']-anchor['gradient']
    relk=actual['hessian']-anchor['hessian']
    tests={label:original_operator_checks(a['theta'],cutoff=c) for label,a in [('actual',actual),('anchor',anchor)]}
    numerical={}
    for label,a,b in [('actual',actual,actual_check),('anchor',anchor,anchor_check)]:
        numerical[label]=dict(value_24_32_difference=float(abs(a['value']-b['value'])),
            load151_24_32_max=float(np.max(abs(a['gradient']-b['gradient']))),
            Jacobian151_24_32_max=float(np.max(abs(a['hessian']-b['hessian']))),
            cutoff_mixed_24_32_max=float(np.max(abs(a['field_cutoff_mixed']-b['field_cutoff_mixed']))),
            unsymmetrized_native_Hessian_defect=a['heat']['unsymmetrized_hessian_defect'],
            value_frequency_tail=a['heat']['value_tail_upper_bound_finite_input'],
            theta23_gradient_tail_bound=a['heat']['theta23_gradient_tail_entry_bound'],
            theta23_Hessian_tail_bound=a['heat']['theta23_hessian_tail_entry_bound'])
    arrays=dict(input_iterate151=x,known_subtotal_gradient151=g,known_subtotal_Hessian151=k,
        known_plus_native0_gradient151=consumed,known_plus_native0_Hessian151=jac,
        source_relative_gradient151=relg,source_relative_Hessian151=relk,
        area_gradient_per_gamma151=area,active52_indices84=active,held32_indices84=held,
        native0_geometry_rate_momenta37=actual['full_gradient189'][37:74],
        native0_source_rate_momentum1=actual['full_gradient189'][99:100])
    for label,a in [('actual',actual),('anchor',anchor)]:
        arrays.update({label+'_'+key:value for key,value in a.items() if isinstance(value,np.ndarray)})
        arrays.update({label+'_heat_'+key:value for key,value in a['heat'].items() if isinstance(value,np.ndarray)})
    output.mkdir(parents=True)
    numerical_path=output/'native_reference_load.npz';write_npz(numerical_path,arrays)
    pins={source.relative_to(ROOT).as_posix():sha256(source.read_bytes()).hexdigest(),
          receipt_path.relative_to(ROOT).as_posix():sha256(receipt_path.read_bytes()).hexdigest()}
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.') and path and Path(path).resolve().is_relative_to(ROOT):
            p=Path(path).resolve();pins[p.relative_to(ROOT).as_posix()]=sha256(p.read_bytes()).hexdigest()
    for rel in ('scripts/evaluate_muon_stationary_native_reference_load.py',
        'artifacts/muon_adopted_incoming_reference_20261018/adoption_v1.json',
        'artifacts/muon_ideal_collider_preparation_20261016/BHSM_IDEAL_COLLIDER_PREPARATION_V1.json',
        'src/bhsm/interface/muon_owned_native_product_connection.py',
        'src/bhsm/interface/muon_intrinsic_fermion_wick_application.py',
        'src/bhsm/interface/muon_continued_action_dual.py'):
        pins[rel]=sha256((ROOT/rel).read_bytes()).hexdigest()
    record=dict(schema='bhsm.stationary-native-reference-load.v1',
        parent_head='e8477cc02a72e1aba1fa59802191b35a6c9b18a1',
        classification='EVALUATED_NATIVE_CONSTANT_ANGULAR_FERMION_COMPONENT_AND_COMPLETE_FIXED_CUTOFF_TWOJET_ON_SAVED_PROVISIONAL_BACKGROUND',
        input_sha256=pins,arrays=dict(path=numerical_path.name,sha256=sha256(numerical_path.read_bytes()).hexdigest()),
        runtime=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
        executed=dict(operator='A_native=D_tau+W; P_z=(-i*omega+W-z*Omega)(i*omega+W+z*Omega); z:1->-i',
            W='[1.5 gamma5-i alpha^a A_a,total]/R4 + M_Y(H); Omega=At_ref/N_ind',
            domain='H1(R_proper) tensor right-body constant scalar harmonic times full18 Weyl components; stationary trace density, not complete event or collider Cauchy domain',
            native='Gamma0/Tproper=+1/2 integral_R d omega/(2*pi) Tr18 E1(c P_-i(omega))',
            Lorentz_return='L0=-N_ind Gamma0/Tproper; analytic sharp kept, no re-dagger at complex source',
            normalization='unit-normalized S3 harmonic; Haar/R3 Gram cancels in trace; no extra2pi2,R3,charge,GeV unit or pair-mixture weight',
            field_derivative='dTr f(P)=Tr fprime(P)dP; d2Tr f(P)=Tr L_fprime(P)[dP]dP+Tr fprime(P)d2P; both state/weight and vertex/contact derivatives retained',
            inherited_state='no covariance, sea, occupation or20 state contractions selected; native relative-phase/current correspondence and matched state correction remain required',
            cutoff=dict(value=c,status='independent numerical coordinate only; not adopted physical native heat length',
                physical_rule='c=I_total/R_total with required surface and bulk impedances; Dc,D2c not supplied',
                total_chain='g_total=g_fixedc+L_c Dc; K_total=K_fixedc+L_yc tensor Dc+Dc tensor L_cy+L_cc Dc tensor Dc+L_c D2c'),
            frequency_panels=list(FREQUENCY_PANELS),points_per_panel=24,validation_points=32,
            anchor='same geometry/domain/clock/c; Aind=H=0 only inside algebraic anchor evaluation, mechanical connection retained. No physical vacuum or source replacement.'),
        load=dict(full_native0_Lorentz_density=actual['value'],anchor_density=anchor['value'],
            newly_evaluated_source_relative_density=actual['value']-anchor['value'],
            full_native0_load151_max=float(np.max(abs(actual['gradient']))),
            source_relative_load151_max=float(np.max(abs(relg))),
            Higgs_Re2_load=float(actual['gradient'][147]),
            native0_wall_gauge_load_max=float(np.max(abs(actual['gradient'][62:146]))),
            cutoff_cotangent=actual['cutoff_gradient'],cutoff_second=actual['cutoff_hessian'],
            native_geometry_rate_momenta37_max=float(np.max(abs(actual['full_gradient189'][37:74]))),
            native_source_rate_momentum=float(actual['full_gradient189'][99]),
            ambient_lapse=actual['ambient_lapse'],induced_lapse=actual['induced_lapse'],
            active52_native_load_max=float(np.max(abs(actual['gradient'][62+active]))),
            active52_native_Hessian_row_max=float(np.max(abs(actual['hessian'][62+active])))),
        continuation={label:a['heat']['continuation'] for label,a in [('actual',actual),('anchor',anchor)]},
        original_equation_checks=tests,numerical_error_scope=numerical,
        consumed=dict(equation='R_partial=R_known(saved moved iterate)+dL_native0; J_partial=K_known(saved moved iterate)+d2L_native0',
            decomposition='Gamma_replacement=Gamma0_actual+[Gamma_complement_and_domain_and_phase+matched_state_completion-Gamma_retained_local_overlap]; exact ledger, bracket NOT zero',
            source_decomposition='Gamma0_actual=(Gamma0_actual-Gamma0_anchor)+Gamma0_anchor; both evaluated here, neither subtracted twice',
            local_overlap='retained sourced local Maxwell/Higgs matching is a full-dimensional/tower operation; no canonical fraction allocated to n0. Full matched overlap remains explicit in the bracket.',
            classical_twojet='reuse after_known_gradient/Hessian at byte-identical saved moved151 only; original seed52 inverse NOT used',
            no_new_minimization=True,no_coupled_correction=True,changed_background=False),
        residuals_before=summary(g,area,active,held),residuals_after_partial_native=summary(consumed,area,active,held),
        held=dict(beam_preparation='unchanged adopted500MeV/beam,100fm per-axisRMS,centers+-1000fm',
            cap_histories='two successive branches, never beam identities',
            exact_pair_statistics='unchanged unpolarized incoming pair purity1/4; not inserted into closed native trace',
            physical_unit='GF exp(2e)-cF[background,Cauchy incidence,normalized external legs]=0 remains unevaluated. dS/de is separate; saved scale initializer unchanged and unadmitted',
            state_wall_span='20-dimensional point-fiber vertex span distinct from bulk native and higher correlations; no C_plus=occupation assignment',
            endpoint_scope='native local stationary-reference geometry-rate cotangents exported; actual history endpoint/geometry-domain terms not completed',
            previous_nonpasses='old gauge reconstruction7.29e-10/6.33e-10, membrane finite-step9.34e-8, continuum/time errors, previous moved52/Higgs and2e-10 failures retained'),
        physical_guard=2e-10,physical_derivative_admitted=False,complete_physical_residual=None,
        coupled_correction=None,magnetic_readout_or_uncertainty=None,
        NEXT_OPERAND='bind this continued native component to the actual incoming/event stratified domain and physical c with Dc,D2c; evaluate compatible complementary/phase/local-overlap and matched inherited-state contractions at the same fields. Then admit complete derivative before coupled correction and fresh original Maxwell/all226 tests.')
    (output/'result.json').write_text(json.dumps(record,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(output=str(output),load=record['load'],residuals=record['residuals_after_partial_native'],numerical=numerical),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output.resolve())
