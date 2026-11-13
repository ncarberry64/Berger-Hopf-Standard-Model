"""Read-only parity of supplied retained formulas with live original owners.

This does not solve a background, select a state, or certify physical admission.
Writes only its explicitly named JSON receipt alongside this script.
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

sys.dont_write_bytecode = True
import numpy as np
import scipy

REPO = Path(r'C:\Users\carbe\Downloads\BHSM_muon_parent_maxwell_worktree_20261001')
HANDOFF = Path(r'C:\Users\carbe\Downloads\BHSM_CODEX_RESTART_20261018')
PKG = HANDOFF/'extracted/BHSM_field_to_spin_response_20261018'
HPKG = HANDOFF/'extracted/BHSM_higgs_wall_coupled_response_20261017'
sys.path[:0] = [str(REPO), str(REPO/'src'), str(PKG), str(PKG/'dependencies'), str(HPKG)]

from bhsm.interface.muon_native_dirac_hamiltonian import (
    lepton_current_hilbert_representation, canonical_lepton_hamiltonian_maps,
    fixed_y_higgs_hamiltonian,
)
from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from bhsm.interface.muon_intrinsic_higgs_weak_action import higgs_action
from bhsm.interface.muon_baton_zoo_original_validation import independent_original_maxwell_weak
from compatible_source import retained_representation
from finite_time_response import YUKAWA, full18_point
from retained_magnetic_application import wall_data, FRAME
from build_higgs_response import LAM, NU2, C_ORBIT, generators, literal_action, rule24
from action_magnetic_kernel import FieldJet, local_action, local_hessian, curvature, curvature_first, pairing


def mx(a):
    return float(np.max(abs(a)))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def live_higgs_value(raw, q, qd):
    """Scalar action evaluation through the live owner, on supplied maps."""
    wall = wall_data(raw)
    points, weights = rule24()
    y = 2*points
    dy = 2*np.einsum('aij,pj->pai', FRAME, points)
    hr = raw[260:264][None] + y@q[:16].reshape(4, 4).T
    htr = raw[264:268][None] + y@qd[:16].reshape(4, 4).T
    hsr = np.einsum('pah,ih->pai', dy, q[:16].reshape(4, 4))
    h = hr[:, :2] + 1j*hr[:, 2:]
    ht = htr[:, :2] + 1j*htr[:, 2:]
    hs = hsr[:, :, :2] + 1j*hsr[:, :, 2:]
    gauge = wall['connection'][[0, 2, 3, 4]][None] + np.einsum('ph,fch->pfc', y, q[16:].reshape(4, 4, 4))
    gc = higgs_u2_real_representation()['complex_generators']
    omega = np.einsum('pfc,cij->pfij', gauge, gc)
    covariant = np.concatenate((ht[:, None], hs), axis=1) + np.einsum('pfij,pj->pfi', omega, h)
    n, r = wall['lapse'], wall['R4']
    kinetic = np.diag([r**3/n, -n*r, -n*r, -n*r])[None]
    return higgs_action(quadrature=C_ORBIT*weights, kinetic_density=kinetic,
        volume_density=n*r**3, H=h, DH=covariant, J=np.zeros_like(h),
        lambda_H=LAM, nu_squared=NU2)


def maxwell_control():
    """Complex analytic control checks both signs and unconjugated pairing."""
    rng = np.random.default_rng(20261018)
    count = 3
    def field():
        value = lambda shape: .1*(rng.normal(size=shape)+.2j*rng.normal(size=shape))
        return FieldJet(value((count, 5, 4)), value((count, 5, 4)),
                        value((count, 5, 4)), value((count, 3, 5, 4)))
    base, u, v = field(), field(), field()
    densities = np.array([[1.1, .9, 1.3, 1.1*.9/1.3, .07],
                          [1.3, 1.2, 1.4, 1.3*1.2/1.4, -.03],
                          [.8, .7, .9, .8*.7/.9, .09]])
    weights = np.array([.2, .3, .5])
    def original(offset):
        a = base.plus(u, offset)
        return independent_original_maxwell_weak(connection=a.value,
            time_derivative=a.time, radial_derivative=a.radial,
            angular_derivative=a.angular, tests=v.value[:, None],
            tests_time=v.time[:, None], tests_radial=v.radial[:, None],
            tests_angular=v.angular[:, None], metric_densities=densities,
            quadrature=weights)
    exact = original(0)
    step = .125
    fd = (-original(2*step)['original_weak_rows']+8*original(step)['original_weak_rows']
          -8*original(-step)['original_weak_rows']+original(-2*step)['original_weak_rows'])/(12*step)
    action = weights@local_action(base, densities)
    weak = weights@pairing(curvature(base), curvature_first(base, v), densities)
    hessian = weights@local_hessian(base, u, v, densities)
    return dict(classification='CONSTRUCTED_COMPLEX_ANALYTIC_CONTROL',
        action_absolute_difference=float(abs(action-exact['original_action_value'])),
        weak_absolute_difference=mx(weak-exact['original_weak_rows']),
        hessian_vs_live_original_rows_fourth_order_difference=mx(hessian-fd),
        finite_step=step, analytic_conjugation=False, physical_admission=False)


def run():
    gauge, alpha, _ = retained_representation()
    live = lepton_current_hilbert_representation()
    scalar_rep = higgs_u2_real_representation()
    parity = dict(gauge_generators=mx(gauge-lepton_unit_trace_gauge_representation()['generators']),
        alpha=mx(alpha-live['alpha']), family_Y=mx(np.diag(YUKAWA)-live['family_Y']),
        Higgs_complex_generators=mx(generators()[0]-scalar_rep['complex_generators']),
        Higgs_real_generators=mx(generators()[1]-scalar_rep['real_generators']))
    sample_results = []
    input_hashes = {}
    for side in ('incoming', 'outgoing'):
        for label in ('lo', 'q000', 'q001', 'q002', 'q003', 'hi'):
            path = PKG/'inputs'/f'{side}_{label}.npz'
            input_hashes[str(path)] = digest(path)
            with np.load(path, allow_pickle=False) as source:
                raw = source['raw']
            wall, point, _, _ = full18_point(raw)
            geo = intrinsic_m4_weight_jet(12, raw[:37], raw[37:74], raw[74:98],
                source_value=raw[98], source_rate=raw[99])
            connection = np.einsum('fc,cij->fij', wall['connection'][[0, 2, 3, 4]], gauge)
            connection[0] /= wall['lapse']
            h = raw[260:262]+1j*raw[262:264]
            owned = canonical_lepton_hamiltonian_maps(value_map=np.eye(18)[None],
                spatial_derivative_map=np.zeros((1, 3, 18, 18)), H=h[None],
                R4=wall['R4'], gauge_connection=connection[None])
            q = .001*np.sin(np.arange(80)+.31)
            qd = .001*np.cos(np.arange(80)+.17)
            sample_results.append(dict(side=side, sample=label,
                induced_lapse_difference=abs(wall['lapse']-geo['induced_lapse'].value),
                R4_difference=abs(wall['R4']-geo['R4'].value),
                mechanical_lambda_difference=abs(wall['lam']-geo['mechanical_connection_lambda'].value),
                full18_material_time_Hamiltonian_difference=mx(point-wall['lapse']*owned['hamiltonian_map'][0]),
                Higgs_signed_action_absolute_difference=abs(literal_action(raw, q, qd)-live_higgs_value(raw, q, qd))))
    owner_names = ['muon_native_dirac_hamiltonian.py', 'muon_native_product_factor_graph.py',
        'muon_intrinsic_m4_normal_pullback.py', 'muon_intrinsic_higgs_weak_action.py',
        'muon_intrinsic_higgs_gauge_action.py', 'muon_material_higgs_gauge_action.py',
        'muon_parent_gauge_geometry_correction.py', 'ae31_c2_intrinsic_m4_lepton_action.py',
        'ae3_c2_hopf_semigroup_transport.py', 'muon_baton_zoo_original_validation.py']
    owners = {str(REPO/'src/bhsm/interface'/name): digest(REPO/'src/bhsm/interface'/name)
              for name in owner_names}
    dependencies = {str(path): digest(path) for path in sorted((PKG/'dependencies').glob('*.py'))}
    dependencies.update({str(HPKG/'build_higgs_response.py'): digest(HPKG/'build_higgs_response.py')})
    result = dict(classification='LIVE_ORIGINAL_OWNER_PARITY_OF_SOURCE_DERIVED_REIMPLEMENTATIONS',
        source_revision='70e82fd4dbe5f53ff27ae17f6aaac7a4727c1fde',
        source_revision_is_actual_HEAD_assertion=False,
        environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        script_sha256=digest(Path(__file__)), original_owners=owners,
        supplied_dependencies=dependencies, retained_inputs=input_hashes,
        representation_parity=parity, retained_sample_parity=sample_results,
        Maxwell_complex_control=maxwell_control(),
        Higgs_normalization=dict(C_ORBIT=C_ORBIT,
            relation='physical intrinsic S3 Haar volume 2*pi^2 / cap orbit normalization (2*pi^2)^2',
            body_J_zero_scope='classical bosonic-body action only; independent quantum/native load retained'),
        physical_admission=False, background_solve_executed=False,
        all226_or_Maxwell_physical_before_after_evaluated=False,
        NEXT_OPERAND='Integrate reviewed adapters; retain saved response arrays because live-owner differences are roundoff. Complete physical boundary/current/interface/reference equation separately.')
    target = Path(__file__).with_suffix('.json')
    target.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n', encoding='utf-8')
    print(json.dumps(dict(receipt=str(target), representation_parity=parity,
        sample_maxima={key:max(row[key] for row in sample_results) for key in sample_results[0] if key not in ('side', 'sample')},
        Maxwell_complex_control=result['Maxwell_complex_control']), indent=2))


if __name__ == '__main__':
    run()
