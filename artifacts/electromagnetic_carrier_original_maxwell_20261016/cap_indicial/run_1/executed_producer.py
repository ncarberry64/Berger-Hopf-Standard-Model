"""Actual retained-real cap leading coefficients and complete n0/n2 curl.

No history integration, new physical radial state, gauge quotient or full
native/outgoing domain is selected. Existing source profiles stay unchanged.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import numpy as np

from em_coexact_cap_domain_20261016 import coexact_indicial_data, coexact_radial_jacobi


def real(a):
    a = np.asarray(a)
    if not np.isfinite(a).all() or (np.iscomplexobj(a) and np.any(a.imag != 0)):
        raise ValueError('actual real germ required without projection')
    return a.real.copy()


def run(repository, output):
    repo, out = Path(repository).resolve(), Path(output).resolve()
    sys.path[:0] = [str(repo/'src'), str(repo/'scripts')]
    from bhsm.interface.electromagnetic_carrier_original_maxwell import even_angular_space
    from bhsm.interface.muon_intrinsic_scalar_discretization import (
        real_scalar_basis_transform, real_scalar_basis_labels, scalar_angular_derivative_matrices)
    from bhsm.interface.muon_matched_mechanical_source import epsilon
    from bhsm.interface.muon_holomorphic_normal_geometry import (
        holomorphic_geometry_rows, _geometry_variables, _fields, anchored_holomorphic_chart)
    from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
    from bhsm.interface.muon_birth_inherited_finite_normal_phase import affine_geometry_germ
    from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0
    from bhsm.interface.muon_parent_maxwell_full_weak import M, FIELD_ORDER
    from bhsm.interface.muon_parent_retarded_hypercharge import ALPHA, WALL
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm_real_full_d5_combined_eta_open_form_20261016 import PHASES, radial_representation, sample_coefficients

    transform = real_scalar_basis_transform(2)
    labels = real_scalar_basis_labels(2)
    ids = np.array([i for i, label in enumerate(labels) if label[0] % 2 == 0])
    ea = np.array([np.linalg.solve(transform, a@transform)[np.ix_(ids, ids)]
                   for a in scalar_angular_derivative_matrices(2)])
    if np.max(abs(ea.imag)) > 1e-14:
        raise ArithmeticError('real scalar derivative representation changed')
    ea = ea.real
    nh = len(ids)
    curl30 = 2*np.eye(3*nh)
    for i in range(3):
        for k in range(3):
            curl30[i*nh:(i+1)*nh, k*nh:(k+1)*nh] += np.einsum('j,jab->ab', epsilon()[i,:,k], ea)
    gradient30 = np.vstack(ea)
    curl120 = np.kron(curl30, np.eye(4))
    gradient120 = np.kron(gradient30, np.eye(4))
    casimir = -sum(a@a for a in ea)
    expected_casimir = np.diag([labels[i][0]*(labels[i][0]+2) for i in ids])
    space = even_angular_space()
    seed = space['mode_coefficients'].transpose(1,2,0).reshape(4,3*nh).T
    seed_eigenvalues = np.array([2,2,-2,-2])
    angular_errors = {
        'curl_Hermitian':float(np.max(abs(curl30-curl30.T))),
        'curl_gradient':float(np.max(abs(curl30@gradient30))),
        'gradient_Gram_Casimir':float(np.max(abs(gradient30.T@gradient30-expected_casimir))),
        'Casimir_source_labels':float(np.max(abs(casimir-expected_casimir))),
        'all_four_seed_curl':float(np.max(abs(curl30@seed-seed*seed_eigenvalues))),
        'source_angular_reconstruction':space['reconstruction_defect'],
    }
    eigenvalues = np.linalg.eigvalsh(curl120)
    expected_eigenvalues = np.repeat([-2.,0.,2.,4.], [12,36,12,60])
    angular_errors['full120_spectrum'] = float(np.max(abs(eigenvalues-expected_eigenvalues)))
    if max(angular_errors.values()) > 2e-12:
        raise ArithmeticError('actual angular control failed: '+str(angular_errors))
    arrays = dict(curl30=curl30,curl120=curl120,gradient30=gradient30,
                  gradient120=gradient120,angular_eigenvalues=eigenvalues,
                  source_four_mode_coefficients=seed)
    records, pins = [], {}
    rho = np.geomspace(1e-2, 1e-6, 9)
    for side, path in PHASES.items():
        phase = load_profile_preserving_phase(path, repository=repo)
        pins.update(phase['input_hashes'])
        time = phase['receipt']['span']/2
        rep = radial_representation(phase['representation'], rho)
        c, sample = sample_coefficients(phase, time, rep)
        raw = sample['raw_fields']
        geo = holomorphic_geometry_rows(raw[:100], rho, differentiate=False)
        density = real([[row[key].value for key in ('electric','radial','angular','shift')]
                        for row in geo['rows']])
        q,v,m,delta,dr,wall,_ = _geometry_variables(raw[:100], differentiate=False)
        chart = anchored_holomorphic_chart(delta.value)
        C0 = float(real((q[0]+sum(q[1:13])).exp().value))*RADIUS0
        N0 = float(real(sum(m[:12]).exp().value))
        eta = float(real(wall.value))/WALL
        slope_f = 1+2*chart['coefficients'][0]+6*chart['coefficients'][1]
        common3 = float(real(8*np.pi**4*C0**5*slope_f**2*eta**3/(3*chart['normalization'])))
        predicted_r4 = common3*N0
        predicted_e4 = common3*C0**2*eta**2/N0
        e,r,d,shift = density.T
        radframe,R = real(c['radial_coframe']),real(c['radius'])
        gauge = real(c['gauge_connection_material'])
        profile_h = real(c['mechanical_profile'])[:,0]-1
        own_h = real([row['connection_lambda'].value-1 for row in geo['rows']])
        independent_gauge = real(np.einsum('rjfac,j->rfac', rep['gauge_basis'], raw[100:180])[:,0])
        radial_functions = []
        for radial_index in range(4):
            j = next(j for j,label in enumerate(rep['gauge_labels']) if label['radial']==radial_index)
            label = rep['gauge_labels'][j]
            radial_functions.append(rep['gauge_basis'][:,j,0,FIELD_ORDER.index(label['field']),label['internal']])
        radial_functions = real(np.array(radial_functions).T)
        def stable_h(germ):
            qq,vv,mm,_,_,ww,_ = _geometry_variables(germ[:100], differentiate=False)
            hs=[]
            for rr in rho:
                ff = _fields(12,qq,vv,mm,(rr/WALL)*ww)
                aa,bb = ff['A'].value,ff['B'].value
                hs.append(-bb*bb/(aa*aa+bb*bb))
            return real(hs),float(real(ww.value))/WALL
        own_stable_h,_=stable_h(raw)
        if side=='outgoing':
            parent=affine_geometry_germ(phase['arrays']['initial_pair'][0],time)
            refs=[affine_geometry_germ(x,time) for x in phase['arrays']['reference_pair']]
            hp,etap=stable_h(parent);hrp,etarp=stable_h(refs[0]);hrc,etarc=stable_h(refs[1])
            stable_profile_h=hp-hrp+hrc
            predicted_profile_h2=-(etap**2-etarp**2+etarc**2)
        else:
            stable_profile_h=own_stable_h
            predicted_profile_h2=-eta**2
        # The stable expression is an algebraic cancellation diagnostic only.
        # The actual full A above remains the unmodified literal owner value.
        stable_gauge=independent_gauge.copy()
        stable_gauge[:,2:]+=M[None]*stable_profile_h[:,None,None]
        scalar_checks = dict(
            rho2_angular_over_radial=rho**2*d/r,
            radius_over_radial_coframe_rho=R/(radframe*rho),
            radial_leading_ratio=r/rho**4/predicted_r4,
            angular_leading_ratio=d/rho**2/predicted_r4,
            electric_leading_ratio=e/rho**4/predicted_e4,
            shift_over_rho=shift/rho,
            total_gauge_max=np.max(abs(gauge),axis=(1,2)),
            total_gauge_over_old_admissible_power=np.max(abs(gauge),axis=(1,2))/rho**ALPHA,
            mechanical_profile_minus_one=profile_h,
            mechanical_profile_minus_one_over_rho2=profile_h/rho**2,
            stable_mechanical_profile_over_predicted_rho2=stable_profile_h/(predicted_profile_h2*rho**2),
            own_lambda_minus_one=own_h,
            inherited_profile_increment=profile_h-own_h,
            independent_gauge_max=np.max(abs(independent_gauge),axis=(1,2)),
            all_four_unchanged_radial_functions=radial_functions,
            literal_vs_stable_total_gauge_max=np.max(abs(gauge-stable_gauge),axis=(1,2)))
        prefix = side+'_'
        arrays[prefix+'rho'] = rho
        arrays[prefix+'geometry100'] = raw[:100]
        arrays[prefix+'gauge_connection_material'] = gauge
        arrays[prefix+'density_e_r_d_shift'] = density
        arrays.update({prefix+k:value for k,value in scalar_checks.items()})
        relative_limit_errors = {k:float(abs(value[-1]-1)) for k,value in scalar_checks.items()
                                 if k.endswith('ratio') or k=='rho2_angular_over_radial'}
        records.append(dict(side=side,coordinate_time=time,normal98=float(raw[98]),
            normal99=float(raw[99]),chi_per_rho=eta,C0=C0,N0=N0,
            f_chi_at_origin=float(real(slope_f)),predicted_radial_rho4_coefficient=predicted_r4,
            predicted_electric_rho4_coefficient=predicted_e4,
            predicted_composed_mechanical_rho2_coefficient=predicted_profile_h2,
            last_stable_mechanical_asymptotic_error=float(abs(scalar_checks['stable_mechanical_profile_over_predicted_rho2'][-1]-1)),
            all_four_radial_function_last_values=radial_functions[-1].tolist(),
            independent_gauge_max_last=float(scalar_checks['independent_gauge_max'][-1]),
            inherited_profile_increment_last=float(scalar_checks['inherited_profile_increment'][-1]),
            literal_vs_stable_total_gauge_max=float(np.max(scalar_checks['literal_vs_stable_total_gauge_max'])),
            finite_radius_ratio_errors=relative_limit_errors,
            total_gauge_max_first_last=[float(scalar_checks['total_gauge_max'][0]),float(scalar_checks['total_gauge_max'][-1])],
            component='same real saved midpoint and complete original inherited/source profile',
            source_profile_or_primal_replaced=False))
    for p,h in pins.items():
        if sha256((repo/p).read_bytes()).hexdigest()!=h:
            raise RuntimeError('phase operand changed during application: '+p)
    for module in list(sys.modules.values()):
        filename = getattr(module,'__file__',None)
        if filename:
            p = Path(filename).resolve()
            if p.is_relative_to(repo/'src/bhsm') and p.suffix=='.py':
                pins[p.relative_to(repo).as_posix()] = sha256(p.read_bytes()).hexdigest()
    helper = Path(__file__).with_name('em_coexact_cap_domain_20261016.py')
    local_sources={p.name:sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),helper)}
    out.mkdir(parents=True,exist_ok=False)
    _compressed_npz(out/'application.npz', arrays)
    (out/'executed_producer.py').write_bytes(Path(__file__).read_bytes())
    result=dict(classification='ACTUAL_REAL_CAP_LEADING_COEXACT_COMPONENT_NOT_GLOBAL_DOMAIN',
        angular_errors=angular_errors,
        full120_curl_multiplicities={'minus2':12,'zero':36,'plus2':12,'plus4':60},
        gradient_image_dimension=36,gradient_constant_kernel_dimension=4,
        coexact_curl_squared4_dimension=24,coexact_curl_squared16_dimension=60,
        coexact_indicial=[coexact_indicial_data(4),coexact_indicial_data(16)],
        actual_real_phase_checks=records,source_and_input_sha256=dict(sorted(pins.items())),
        local_source_sha256=local_sources,
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        old_ALPHA_or_inherited_four_profiles_changed=False,
        Gauss_longitudinal_or_temporal_constraints_removed=False,
        full_moving_strong_domain_proved=False,common_native_operator_identified=False,
        physical_radial_convergence_or_terminal_derivative_passed=False,
        original_coupled_corrections_applied=0,physical_muon_moment=None)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8')
    print(json.dumps(dict(angular_errors=angular_errors,phase_checks=records),indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repository',required=True)
    ap.add_argument('--output',required=True)
    a=ap.parse_args()
    run(a.repository,a.output)
