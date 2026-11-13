"""Coherent accounting of independently evaluated hadronic Pauli components.

Frozen spectral centers are never replaced by the sensitivity quadratures.
The published four-current application has a separate metrology approximation,
not an invented exact mass derivative. This is a finite-order component ledger.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from numpy.polynomial.laguerre import laggauss
from numpy.polynomial.legendre import leggauss

from .muon_calibrated_hvp_spectral import (
    delta_alpha_had_spacelike, leading_hvp_pauli, load_alphaqed26_spectrum,
)
from .muon_calibrated_hvp_higher import (
    next_to_leading_hvp_pauli, nlo_photonic_kernel_log_endpoint,
    one_loop_lepton_delta_alpha,
)
from .muon_calibrated_hvp_nnlo import (
    _approximate_kernel, next_to_next_to_leading_hvp_pauli,
    retained_nnlo_coefficients,
)

PINNED = {
    'LO': ('artifacts/muon_calibrated_hvp_spectral_20261010/run_3/hvp_spectral.json',
           '171190c21dd1e249394ce6931c8daa69a2d44a29ddf1e6f6a90f38806bad3fc3'),
    'NLO': ('artifacts/muon_calibrated_hvp_higher_20261010/run_3/hvp_higher.json',
            '2c6a7adc1e81faf748d745ae6994e54ed81232044d99441af4a9ffd430380849'),
    'NNLO': ('artifacts/muon_calibrated_hvp_nnlo_20261010/run_3/hvp_nnlo.json',
             'dde237cf01cf4de92121bba1d5000560d378fdd2773313bcad75c06077e24eb5'),
    'HLbL': ('artifacts/muon_calibrated_hlbl_projection_20261010/input/published_projection.json',
             'c77cecadb13f258d771a8ce2e6e3c9c6383d8caaf2a50cfeedb2c921030efbc4'),
    'config': ('artifacts/muon_calibrated_pauli_20261009/inputs.json',
               '0b614ab6f26d169ca04a4878f767f78eb3668484840867e46aebbebf186369da'),
}


def _record(root, path):
    raw = (root / path).read_bytes()
    return dict(path=path, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def _pinned(root, name):
    path, expected = PINNED[name]
    record = _record(root, path)
    if record['sha256'] != expected:
        raise ValueError('frozen hadronic input identity mismatch: ' + name)
    return json.loads((root / path).read_bytes()), record


def coherent_spectral_sum(rows):
    """Sum signed common error rows before taking either covariance norm."""
    if not rows:
        raise ValueError('at least one evaluated spectral row required')
    statistical = [np.asarray(r['statistical_error_vector'], float) for r in rows]
    systematic = [np.asarray(r['systematic_error_vector'], float) for r in rows]
    for vectors in (statistical, systematic):
        if (vectors[0].ndim != 1 or any(v.shape != vectors[0].shape for v in vectors)
                or any(not np.isfinite(v).all() for v in vectors)):
            raise ValueError('finite aligned spectral uncertainty vectors required')
    values = [float(r['value']) for r in rows]
    if not all(math.isfinite(v) for v in values):
        raise ValueError('finite evaluated centers required')
    st = np.sum(statistical, axis=0)
    sy = np.sum(systematic, axis=0)
    return dict(value=sum(values), statistical_vector=st.tolist(), systematic_vector=sy.tolist(),
                statistical_standard_uncertainty=float(np.linalg.norm(st)),
                systematic_standard_uncertainty=float(np.linalg.norm(sy)),
                standard_uncertainty=float(np.hypot(np.linalg.norm(st), np.linalg.norm(sy))))


def central_log_derivative(evaluate, mass, *, steps=(1e-4, 1e-5)):
    """Numerical d/dm via central log steps; refinement is not an enclosure."""
    mass = float(mass)
    if not math.isfinite(mass) or mass <= 0 or not callable(evaluate):
        raise ValueError('positive finite mass and evaluated kernel callable required')
    records = []
    for step in steps:
        h = float(step)
        if not math.isfinite(h) or h <= 0 or h >= 0.1:
            raise ValueError('finite log steps in (0,0.1) required')
        up = float(evaluate(mass * math.exp(h)))
        down = float(evaluate(mass * math.exp(-h)))
        if not math.isfinite(up) or not math.isfinite(down):
            raise ValueError('mass derivative consumed nonfinite kernel value')
        records.append(dict(log_step=h, upper_value=up, lower_value=down,
                            derivative_per_GeV=(up-down)/(2*h*mass)))
    if len(records) < 2:
        raise ValueError('at least two log steps required for refinement comparison')
    return dict(value=records[-1]['derivative_per_GeV'], steps=records,
                absolute_refinement_difference=abs(records[-1]['derivative_per_GeV']
                                                   - records[-2]['derivative_per_GeV']),
                method='[f(m exp(h))-f(m exp(-h))]/(2 h m)',
                error_scope='finite-difference refinement estimate, not exact derivative or rigorous enclosure')


def primitive_gradient(config, *, derivative_alpha, derivative_muon,
                       derivative_electron, derivative_tau):
    """Pull HVP derivatives back through the retained six-input mass map."""
    uncertainty = config['uncertainty_and_correlations']
    expected = ['G_F_GeV_minus2', 'm_h_GeV', 'm_tau_GeV', 'm_mu_GeV', 'm_e_GeV']
    if uncertainty['consumer_order'] != expected:
        raise ValueError('retained consumer Jacobian order changed')
    jac = np.asarray(uncertainty['consumer_vs_primitive_jacobian'], float)
    if jac.shape != (5, 6) or not np.isfinite(jac).all():
        raise ValueError('finite five-by-six consumer Jacobian required')
    coefficients = np.asarray([derivative_alpha, derivative_muon,
                               derivative_electron, derivative_tau], float)
    if not np.isfinite(coefficients).all():
        raise ValueError('finite evaluated HVP derivatives required')
    consumer = np.array([0., 0., derivative_tau, derivative_muon, derivative_electron])
    result = consumer @ jac
    inverse_alpha = float(config['primary_measurements']['alpha_inverse_0']['value'])
    if not math.isfinite(inverse_alpha) or inverse_alpha <= 0:
        raise ValueError('positive selected inverse alpha required')
    if uncertainty['primitive_order'][0] != 'alpha_inverse_0':
        raise ValueError('inverse-alpha primitive order changed')
    result[0] -= derivative_alpha / inverse_alpha**2
    return result.tolist()


def _mass_applications(spectrum, alpha, muon, electron, tau, *, fine=False):
    """The existing same-spectrum kernels, with no shifted spectral fit."""
    def lo(m):
        return leading_hvp_pauli(spectrum, alpha, m, order=32)['value']

    def nlo(m, e, t):
        return next_to_leading_hvp_pauli(spectrum, alpha, m, e, t,
                    order=48 if fine else 32, spectral_order=32 if fine else 12,
                    endpoint_v=48, kernel_decimal_precision=110)['NLO_HVP']['value']

    def nnlo(m, e):
        return next_to_next_to_leading_hvp_pauli(spectrum, alpha, m, e,
                    order=40 if fine else 24, spectral_order=16 if fine else 8,
                    double_order=32 if fine else 24, endpoint_v=40)['NNLO_HVP']['value']

    return {'muon': {'LO':lo, 'NLO':lambda m:nlo(m,electron,tau),
                            'NNLO':lambda m:nnlo(m,electron)},
            'electron': {'NLO':lambda e:nlo(muon,e,tau), 'NNLO':lambda e:nnlo(muon,e)},
            'tau': {'NLO':lambda t:nlo(muon,electron,t)}}


def nnlo_ultraviolet_tail_estimate(spectrum, alpha, muon, electron, *,
                                 order=24, spectral_order=8, double_order=32):
    """Apply the omitted constant-R five-flavor tail to every NNLO kernel.

    delta h(Q)=alpha*(11/3)/(3*pi)*log(1+Q/1e12). Its insertion is evaluated
    with the published approximate/exact kernels, including both 6c2 lines.
    This nominal asymptotic model is separate from the frozen centers and
    is not a full-QCD upper bound, a new data row or a quadrature enclosure.
    """
    a = float(alpha); m = float(muon); me = float(electron)
    if not all(math.isfinite(x) and x > 0 for x in (a, m, me)):
        raise ValueError('positive finite coupling and pole masses required')
    coefficients = retained_nnlo_coefficients(me/m)
    names = ['6a','6b','6bll','6c1','6c3','6c4','6d']
    values = np.zeros(7)
    z, w = leggauss(order)
    middle = -math.log(1-(math.sqrt(5)-1)/2)
    edges = sorted([0., middle, 1., 2., 4., 8., 16., 32., 40.])
    for low, high in zip(edges[:-1], edges[1:]):
        for v, weight in zip((low+high)/2+(high-low)/2*z, (high-low)/2*w):
            end = math.exp(-v); x = -math.expm1(-v); Q = m*m*x*x/end
            row = delta_alpha_had_spacelike(spectrum, Q, a, order=spectral_order)
            h = row['value']; dh = row['tail_asymptotic_estimate']
            le = one_loop_lepton_delta_alpha(Q, me, a)
            lm = one_loop_lepton_delta_alpha(Q, m, a)
            k4 = nlo_photonic_kernel_log_endpoint(float(v), decimal_precision=110)
            factors = np.array([(a/math.pi)**3*_approximate_kernel(x,end,coefficients[n])*end
                                for n in names[:3]] +
                               [(a/math.pi)**2*(k4-2*math.pi/a*end*lm)*end,
                                3*a/math.pi*end*end*le,
                                3*a/math.pi*end*end*lm,a/math.pi*end*end])*weight
            squared = 2*h*dh+dh*dh
            cubed = 3*h*h*dh+3*h*dh*dh+dh**3
            values += factors*np.array([dh,dh,dh,squared,squared,squared,cubed])
    classes = dict(zip(names, map(float, values)))
    nodes, weights = laggauss(double_order)
    if 2*max(nodes) > math.log(np.finfo(float).max)-2*math.log(m):
        raise ValueError('tail quadrature exceeds finite arithmetic')
    A=1855-188*math.pi**2; B=988*math.pi**2-9765; C=24*(435-44*math.pi**2)
    factor=(a/math.pi)**2/(2*(32*math.pi**2-315))
    value=0.
    for v, weight in zip(nodes, weights):
        left = delta_alpha_had_spacelike(spectrum,m*m*math.exp(v),a,order=spectral_order)
        hl=left['value']; dl=left['tail_asymptotic_estimate']
        for vp, wp in zip(nodes, weights):
            zz=math.exp(-vp)
            right=delta_alpha_had_spacelike(spectrum,m*m*math.exp(v+vp),a,order=spectral_order)
            hr=right['value']; dr=right['tail_asymptotic_estimate']
            value += factor*weight*wp*(A*zz+B*zz**2+C*zz**3)*(hl*dr+dl*hr+dl*dr)
    classes['6c2']=value
    return dict(value=sum(classes.values()),classes=classes,
                sum_absolute_classes=sum(abs(x) for x in classes.values()),
                spectral_cutoff_s_GeV2=1e12,constant_R=11/3,
                photon_tail_formula='delta h(Q)=alpha*(11/3)/(3*pi)*log1p(Q/1e12)',
                outer_order=order,spectral_order=spectral_order,double_order=double_order,
                meaning='nominal omitted five-flavor constant-R ultraviolet model; not a rigorous bound',
                added_to_frozen_centers=False)


def calibrated_hadronic_ledger(root, *, progress=None):
    """Bind pinned runs, evaluate shared metrology gradients and make ledger."""
    root = Path(root)
    packets = {}; records = []
    for name in PINNED:
        packets[name], record = _pinned(root, name)
        records.append(record)
        if name in ('LO','NLO','NNLO'):
            path = PINNED[name][0].replace('/run_3/', '/run_4/')
            replay = _record(root,path)
            if replay['sha256'] != record['sha256']:
                raise ValueError('frozen independent hadronic replay mismatch: '+name)
            records.append(replay)
    config = packets['config']; hlbl = packets['HLbL']
    alpha = 1/config['primary_measurements']['alpha_inverse_0']['value']
    muon = config['selected_consumer_values']['m_mu_GeV']['value']
    electron = config['selected_consumer_values']['m_e_GeV']['value']
    tau = config['primary_measurements']['tau_mass']['value']
    rows = {'LO':packets['LO']['LO_HVP'],
            'NLO':packets['NLO']['application']['NLO_HVP'],
            'NNLO':packets['NNLO']['application']['NNLO_HVP']}
    hvp = coherent_spectral_sum(list(rows.values()))
    input_dir = root/'artifacts/muon_calibrated_hvp_spectral_20261010/input'
    spectrum = load_alphaqed26_spectrum(input_dir)
    source = json.loads((input_dir/'provenance.json').read_bytes())
    for item in source['input_records']:
        records.append(_record(root, str((input_dir/item['path']).relative_to(root)).replace('\\','/')))
    provenance_paths = ['artifacts/muon_calibrated_hvp_spectral_20261010/input/provenance.json',
                        'artifacts/muon_calibrated_hvp_higher_20261010/input/provenance.json',
                        'artifacts/muon_calibrated_hvp_nnlo_20261010/input/provenance.json',
                        'artifacts/muon_calibrated_hvp_nnlo_20261010/input/coefficients.json']
    provenance_records = [_record(root, path) for path in provenance_paths]
    expected_hashes = [packets['LO']['input_provenance_sha256'],
                       packets['NLO']['kernel_provenance_sha256'],
                       packets['NNLO']['kernel_provenance_sha256'],
                       packets['NNLO']['coefficient_sha256']]
    for record, expected in zip(provenance_records, expected_hashes):
        if record['sha256'] != expected:
            raise ValueError('frozen spectral provenance changed: '+record['path'])
    records += provenance_records
    for name, filename in [('LO','muon_calibrated_hvp_spectral.py'),
                           ('NLO','muon_calibrated_hvp_higher.py'),
                           ('NNLO','muon_calibrated_hvp_nnlo.py')]:
        rec = _record(root,'src/bhsm/interface/'+filename)
        if rec['sha256'] != packets[name]['producer_source_sha256']:
            raise ValueError('frozen spectral producer changed: '+name)
        records.append(rec)
    applications = _mass_applications(spectrum,alpha,muon,electron,tau)
    fine = _mass_applications(spectrum,alpha,muon,electron,tau,fine=True)
    derivatives = {}
    masses = dict(muon=muon,electron=electron,tau=tau)
    for particle, classes in applications.items():
        derivatives[particle] = {}
        for order_name, application in classes.items():
            if progress:
                progress('mass sensitivity '+particle+' '+order_name)
            record = central_log_derivative(application,masses[particle])
            refined = central_log_derivative(fine[particle][order_name],masses[particle],
                                            steps=(1e-4,1e-5))
            record['quadrature_refined_derivative'] = refined
            record['absolute_quadrature_refinement_difference'] = abs(record['value']-refined['value'])
            record['selected_derivative_per_GeV'] = refined['value']
            derivatives[particle][order_name] = record
    d_alpha = sum(power*rows[name]['value']/alpha for name,power in [('LO',2),('NLO',3),('NNLO',4)])
    d_masses = {p:sum(r['selected_derivative_per_GeV'] for r in orders.values())
                for p,orders in derivatives.items()}
    gradient = primitive_gradient(config,derivative_alpha=d_alpha,
                                  derivative_muon=d_masses['muon'],
                                  derivative_electron=d_masses['electron'],
                                  derivative_tau=d_masses['tau'])
    if progress:
        progress('NNLO ultraviolet tail application')
    tail = nnlo_ultraviolet_tail_estimate(spectrum,alpha,muon,electron)
    hvp_sigma = hvp['standard_uncertainty']; hlbl_sigma = hlbl['published_standard_uncertainty']
    logarithm_factor = 2*alpha/math.pi*math.log(muon/electron)
    uncertainties = np.asarray(config['uncertainty_and_correlations']['primitive_standard_uncertainties'])
    input_gradient = np.asarray(gradient)
    return dict(
        classification='CALIBRATED_PHYSICAL_HADRONIC_COMPONENT_LEDGER_THROUGH_HVP_NNLO_PLUS_HLBL_LO',
        evaluated_subtotal=hvp['value']+hlbl['projected_value'],
        HVP_subtotal=hvp['value'],HLbL_projection=hlbl['projected_value'],
        HVP_order_centers={name:row['value'] for name,row in rows.items()},
        spectral_statistical_vector=hvp['statistical_vector'],
        spectral_systematic_vector=hvp['systematic_vector'],
        spectral_statistical_standard_uncertainty=hvp['statistical_standard_uncertainty'],
        spectral_systematic_standard_uncertainty=hvp['systematic_standard_uncertainty'],
        spectral_standard_uncertainty=hvp_sigma,
        gradient_order=config['uncertainty_and_correlations']['primitive_order'],
        selected_input_gradient=gradient,
        HVP_consumer_gradient=dict(derivative_alpha=d_alpha,derivative_m_mu_GeV=d_masses['muon'],
                                  derivative_m_e_GeV=d_masses['electron'],derivative_m_tau_GeV=d_masses['tau']),
        component_mass_derivatives=derivatives,
        metrology_derivative_scope=dict(
            included='HVP LO/NLO/NNLO only; same input spectrum held fixed',
            alpha_partial_by_order={name:power*rows[name]['value']/alpha for name,power in [('LO',2),('NLO',3),('NNLO',4)]},
            alpha_scaling='exact powers 2/3/4 at fixed masses and frozen current spectrum',
            mass_method='central logarithmic differences h=1e-4,1e-5 with separate kernel/quadrature refinement',
            consumer_vs_primitive_jacobian=config['uncertainty_and_correlations']['consumer_vs_primitive_jacobian'],
            primitive_standard_uncertainties=uncertainties.tolist(),
            illustrative_independent_primitive_standard_uncertainty=float(np.linalg.norm(input_gradient*uncertainties)),
            input_standard_uncertainty_upper_over_correlations=float(abs(input_gradient)@uncertainties),
            physical_primitive_covariance=None,
            HLbL_exact_selected_input_gradient=None,
            HLbL_gradient_omission_is_not_zero=True,
            HLbL_nearby_metrology_allowance=hlbl['nearby_metrology_approximation'],
            no_GF_or_Higgs_dependence='these retained minimal hadronic kernels do not consume GF or Higgs mass; no general native zero follows'),
        errors=dict(
            spectral_covariance_scope=source['uncertainty'],
            spectral_rows_combined_coherently=True,
            HLbL_publication_standard_uncertainty=hlbl_sigma,
            HVP_HLbL_cross_covariance=None,
            cross_source_covariance_status='not supplied; two-current and four-current fits may share experimental inputs',
            combined_marginal_standard_uncertainty_range=[abs(hvp_sigma-hlbl_sigma),hvp_sigma+hlbl_sigma],
            combined_range_meaning='Cauchy covariance range from supplied marginal standard uncertainties; not a probability interval or rigorous observable bound',
            undressing_absolute_estimate=sum(row['undressing_error_estimate'] for row in rows.values()),
            undressing_meaning='source conservative absolute estimates; not additional independent statistical rows',
            numerical_refinement={name:packets[name]['numerical_verification'] for name in rows},
            UV_tail_LO=packets['LO']['tail'],
            UV_tail_NLO=dict(value=packets['NLO']['application']['source_ultraviolet_tail_asymptotic_estimate'],
                            classes=packets['NLO']['application']['source_ultraviolet_tail_class_estimates'],
                            meaning='source constant-R asymptotic model; not upper bound'),
            UV_tail_NNLO=tail,
            NNLO_kernel_approximation_estimate=packets['NNLO']['application']['kernel_approximation_error_estimate'],
            NNLO_kernel_error_meaning=packets['NNLO']['application']['kernel_error_meaning'],
            omitted_NNLO_tau_estimate=packets['NNLO']['application']['omitted_tau_NNLO_error_estimate'],
            HLbL_metrology_approximation_allowance=hlbl['nearby_metrology_approximation']['generous_sensitivity_allowance_estimate'],
            HLbL_metrology_approximation_is_rigorous_bound=False,
            next_order_hadronic_estimates=dict(
                HLbL_NLO_leading_electron_log=dict(value=hlbl['projected_value']*logarithm_factor,
                     multiplier=logarithm_factor,formula='2*alpha/pi*log(m_mu/m_e)',
                     source='https://arxiv.org/html/1403.7512v2',equation='8',
                     source_full_NLO_estimate=3e-11,source_model_uncertainty=2e-11,
                     caveat='RG leading-log estimate using current published LO center, not an evaluated full NLO tensor projection or error enclosure; source Eq9 used older LO input',
                     added_to_evaluated_subtotal=False),
                HVP_N3LO=dict(value=None,reason='no evaluated O(alpha^5) kernel supplied; observed NNLO enhancement does not justify a geometric error bound')),
            strict_all_orders_lower_threshold=source['threshold_and_regions']['strict_all_orders_inclusive_threshold'],
            estimates_form_joint_enclosure=False),
        consumed_inputs=records,
        source_normalization=source['spectrum_normalization'],
        source_domain=source['threshold_and_regions'],
        source_nominal_comparison=packets['LO']['source_nominal_comparison'],
        HLbL_source_application=hlbl,
        overlap=dict(pure_leptonic_QED='excluded from all hadronic centers',
                     neutral_Higgs='separate minimal topology, not included here',
                     HVP_HLbL='connected two-current and connected four-current projections counted separately',
                     HVP_inclusive_radiation=packets['NNLO']['application']['overlap'],
                     HLbL_short_distance=hlbl['overlap']['light_pseudoscalar_poles'],
                     extra_BHSM_native='additional interface/formation/nonminimal-current/kernel corrections require their own disjoint matched applications'),
        producer_source=_record(root,'src/bhsm/interface/muon_calibrated_hadronic_ledger.py'),
        measured_anomaly_used=False,measured_g_used=False,SM_total_used=False,
        complete_native_remainder=False,complete_a_mu=None,complete_g_mu=None,
        action_selected=False,Gate7_closed=False,rigorous_observable_enclosure=False)
