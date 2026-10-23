"""Curvature-memory application on one actual retained REAL finite phase.

This adds a Wilson/Volterra readout, not another source/profile/history solve.
The old one-cell represented outgoing interval is not the current complex
trial0000, and is not promoted to a physical outgoing continuation.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import numpy as np
from scipy.integrate import solve_ivp

REPO = Path(r'C:\Users\carbe\Downloads\BHSM_muon_parent_maxwell_worktree_20261001')
sys.path.insert(0, str(REPO / 'src'))
from bhsm.interface.muon_profile_preserving_phase_sample import (
    load_profile_preserving_phase, profile_preserving_raw_sample,
    profile_preserving_lepton_sample,
)
from bhsm.interface.muon_birth_inherited_finite_normal_phase import affine_geometry_germ
from bhsm.interface.muon_intrinsic_m4_normal_pullback import intrinsic_m4_weight_jet
from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
from bhsm.interface.muon_parent_maxwell_full_weak import M
from bhsm.interface.muon_matched_mechanical_source import epsilon

PHASE = 'artifacts/muon_inherited_finite_normal_phase_20261011/run_1'


def deterministic_npz(path, arrays):
    with ZipFile(path, 'w', compression=ZIP_DEFLATED, compresslevel=6) as archive:
        for name in sorted(arrays):
            buf = BytesIO()
            np.lib.format.write_array(buf, np.asarray(arrays[name]), allow_pickle=False)
            info = ZipInfo(name + '.npy', date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            archive.writestr(info, buf.getvalue(), compress_type=ZIP_DEFLATED, compresslevel=6)


def _rate(raw):
    out = np.zeros_like(raw)
    out[:37] = raw[37:74]
    out[98] = raw[99]
    return out


def _weights(raw):
    return intrinsic_m4_weight_jet(12, raw[:37], raw[37:74], raw[74:98],
        source_value=raw[98], source_rate=raw[99])


class ActualFiniteConnection:
    """Literal inherited wall connection and analytic interpolation time jet.

    At the wall, the actual inherited profile contributes
    lambda_parent-lambda_child-lambda_refparent+lambda_refchild; the intrinsic
    connection also contributes lambda_child-1. Their exact sum cancels the
    child coefficient once. All three surviving affine first germs are kept.
    Three full original-owner readouts independently check this simplification.
    """
    def __init__(self, phase):
        self.phase = phase
        self.rep = phase['representation']
        self.count = len(self.rep['gauge_labels'])
        self.trace = np.asarray(self.rep['wall_trace_map'])
        self.generators = higgs_u2_real_representation()['complex_generators']
        self.initial_pair = phase['arrays']['initial_pair']
        self.refs = phase['arrays']['reference_pair']
        self.span = float(phase['receipt']['span'])
        if phase['receipt']['steps'] != 1 or self.span <= 0:
            raise ValueError('this new application pins the declared positive one-cell phase')
        for key in ('initial_pair', 'reference_pair', phase['stage_key']):
            if not np.isrealobj(phase['arrays'][key]):
                raise ValueError('actual real finite phase required; complex clipping is forbidden')

    def __call__(self, t):
        sample = profile_preserving_raw_sample(self.phase, float(t))
        child = sample['raw_fields']; child_rate = sample['raw_coordinate_time_derivative']
        parents = [affine_geometry_germ(self.initial_pair[0], t),
                   affine_geometry_germ(self.refs[0], t),
                   affine_geometry_germ(self.refs[1], t)]
        lambdas = [_weights(x)['mechanical_connection_lambda'] for x in parents]
        lam = lambdas[0].value-lambdas[1].value+lambdas[2].value-1
        lam_rate = sum(sign * (jet.gradient @ _rate(raw)[:100])
            for sign, jet, raw in zip((1, -1, 1), lambdas, parents))
        values = np.einsum('fcj,j->fc', self.trace, child[100:100+self.count])
        rates = np.einsum('fcj,j->fc', self.trace, child_rate[100:100+self.count])
        values[2:] += M*lam
        rates[2:] += M*lam_rate
        connection = np.einsum('fc,cij->fij', values, self.generators)
        derivative = np.einsum('fc,cij->fij', rates, self.generators)
        return dict(connection=connection, derivative=derivative,
            component_values=values, component_time_derivatives=rates)


def evaluate(output):
    phase = load_profile_preserving_phase(PHASE, repository=REPO)
    app = ActualFiniteConnection(phase)
    T = app.span
    checks = []
    for sigma in (0., .5, 1.):
        t = T*sigma
        original = profile_preserving_lepton_sample(phase, t)
        fast = app(t)
        op = original['operator']
        checks.append(dict(sigma=sigma, induced_lapse=float(op['N']),
            quotient_radius=float(op['R4']),
            full_original_wall_connection_max_difference=float(np.max(abs(
                fast['component_values']-op['total_wall_connection']))),
            analytic_interpolation_vs_stored_spatial_rate_max_difference=float(np.max(abs(
                fast['component_time_derivatives'][2:]
                -op['total_wall_spatial_connection_coordinate_rate'])))))

    first = app(0.)
    A0 = first['connection'][2:].copy()

    def unpack(y):
        return y[:4].reshape(2, 2), y[4:16].reshape(3, 2, 2), y[16:28].reshape(3, 2, 2)

    def rhs(sigma, y):
        delta, _, _ = unpack(y)
        U = np.eye(2)+delta
        x = app(T*sigma)
        At, A = x['connection'][0], x['connection'][2:]
        dA = x['derivative'][2:]
        comm = At@A-A@At
        adj = U.conj().T
        return T*np.concatenate(((-At@U).ravel(),
            (adj@dA@U).ravel(), (adj@comm@U).ravel()))

    # Store U-I directly: nonzero tiny temporal/noncommuting components must
    # not be rounded away by subtracting an identity after integration.
    y0 = np.zeros(28, complex)
    solutions = []
    for rtol, atol in ((8e-12, 1e-25), (3e-13, 1e-27)):
        s = solve_ivp(rhs, (0., 1.), y0, method='DOP853', rtol=rtol,
            atol=atol, dense_output=True)
        if not s.success:
            raise RuntimeError(s.message)
        solutions.append(s)
    fine = solutions[-1]
    delta, time_memory, comm_memory = unpack(fine.y[:, -1])
    U = np.eye(2)+delta
    last = app(T)
    A1 = last['connection'][2:]
    # Compensated direct connection subtraction includes the initial
    # connection, not an assumed zero initial A. U0=I is a fundamental
    # propagator identity and does not select an event/birth bundle map.
    direct = (U.conj().T@(A1-A0)@U + delta.conj().T@A0
              + A0@delta + delta.conj().T@A0@delta)
    memory = time_memory+comm_memory
    enclosure = []
    arrays = dict(initial_connection=A0, final_connection=A1,
        fundamental_wilson_delta=delta, direct_initial_subtracted_connection=direct,
        time_derivative_memory=time_memory, temporal_commutator_memory=comm_memory,
        volterra_connection_memory=memory,
        direct_minus_volterra=direct-memory)
    spatial_norm = []; comm_norm = []; temporal_norm = []
    for nodes in (16, 32):
        v, w = np.polynomial.legendre.leggauss(nodes)
        times = (v+1)/2; weights = w/2
        terms = []; dterms = []; cterms = []; curved = []; anti = []
        for sigma in times:
            d, _, _ = unpack(fine.sol(float(sigma)))
            Up = np.eye(2)+d; x = app(T*sigma)
            At, A = x['connection'][0], x['connection'][2:]
            dtA = x['derivative'][2:]; comm = At@A-A@At
            Ft = dtA+comm
            Fab = np.empty((3,3,2,2),complex)
            for a in range(3):
                for b in range(3):
                    Fab[a,b] = (A[a]@A[b]-A[b]@A[a]
                        +2*np.einsum('c,cij->ij',epsilon()[a,b],A))
            adj = Up.conj().T
            dterms.append(adj@dtA@Up); cterms.append(adj@comm@Up)
            terms.append(adj@Ft@Up); curved.append(Fab)
            anti.append(np.max(abs(x['connection']+x['connection'].conj().swapaxes(-1,-2))))
            if nodes == 32:
                spatial_norm.append(np.linalg.norm(Fab))
                comm_norm.append(np.linalg.norm(comm))
                temporal_norm.append(np.linalg.norm(At))
        quad = T*np.einsum('p,paij->aij',weights,terms)
        dq = T*np.einsum('p,paij->aij',weights,dterms)
        cq = T*np.einsum('p,paij->aij',weights,cterms)
        arrays[f'gl{nodes}_sigma']=times
        arrays[f'gl{nodes}_volterra_memory']=quad
        arrays[f'gl{nodes}_time_derivative_memory']=dq
        arrays[f'gl{nodes}_temporal_commutator_memory']=cq
        if nodes == 32:
            arrays['gl32_spatial_curvature']=np.array(curved)
        enclosure.append(dict(nodes=nodes,
            DOP853_memory_max_difference=float(np.max(abs(quad-memory))),
            antihermitian_connection_max_defect=float(max(anti))))
    pins = dict(phase['input_hashes'])
    for name in ('muon_profile_preserving_phase_sample',
            'muon_intrinsic_m4_normal_pullback','muon_birth_inherited_finite_normal_phase',
            'muon_inherited_intrinsic_lepton_operator','muon_exact_material_response',
            'muon_intrinsic_higgs_gauge_action','muon_parent_maxwell_full_weak'):
        path='src/bhsm/interface/'+name+'.py'
        pins[path]=sha256((REPO/path).read_bytes()).hexdigest()
    result=dict(classification='ACTUAL_RETAINED_REAL_FINITE_PHASE_CURVATURE_MEMORY_APPLICATION',
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        input_hashes=dict(sorted(pins.items())), consumed_phase=PHASE,
        coordinate_interval=[0.,T], represented_cells=1,
        original_owner_checks=checks,
        fundamental_wilson_delta_norm=float(np.linalg.norm(delta)),
        temporal_connection_norm_max=float(max(temporal_norm)),
        spatial_nonabelian_curvature_norm_max=float(max(spatial_norm)),
        temporal_commutator_curvature_norm_max=float(max(comm_norm)),
        time_derivative_memory_norm=float(np.linalg.norm(time_memory)),
        nonzero_temporal_commutator_memory_norm=float(np.linalg.norm(comm_memory)),
        initial_connection_norm=float(np.linalg.norm(A0)),
        direct_initial_subtracted_connection_norm=float(np.linalg.norm(direct)),
        volterra_connection_memory_norm=float(np.linalg.norm(memory)),
        direct_vs_volterra_max_difference=float(np.max(abs(direct-memory))),
        DOP853_tolerance_refinement_max_difference=float(np.max(abs(
            solutions[0].y[:,-1]-solutions[1].y[:,-1]))),
        GL16_GL32_memory_max_difference=float(np.max(abs(
            arrays['gl16_volterra_memory']-arrays['gl32_volterra_memory']))),
        integration_checks=enclosure,
        unitary_fundamental_propagator_defect=float(np.max(abs(U.conj().T@U-np.eye(2)))),
        derivative_formula='d_t(U^dagger A_a U)=U^dagger(d_t A_a+[A_t,A_a])U; homogeneous material b=0',
        spatial_curvature_formula='F_ab=[A_a,A_b]+2 epsilon_ab^c A_c in retained right frame',
        scope='one actual historical real finite interpolation and affine parent/reference first germs; not a continuous Euler solution',
        actual_profile_or_source_campaign_restarted=False,
        current_complex_trial0000_consumed=False,
        original_spin_or_scalar_terms_erased=False,
        zero_initial_connection_substituted=False,
        physical_outgoing_continuation_evaluated=False,
        physical_outgoing_energy_field_derivative_gate_passed=False,
        physical_two_spin_normalizations=None,muon_magnetic_moment=None,
        coupled_matching_corrections=0,
        precision_scope='binary64 integration and refinement comparisons; no outward continuum enclosure',
        caveat='Volterra transports a supplied initial connection and supplied curvature; it does not determine an uncomputed future curvature/source.')
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    deterministic_npz(output/'application.npz',arrays)
    result['application_sha256']=sha256((output/'application.npz').read_bytes()).hexdigest()
    (output/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:result[k]for k in ('volterra_connection_memory_norm',
        'nonzero_temporal_commutator_memory_norm','direct_vs_volterra_max_difference',
        'GL16_GL32_memory_max_difference','DOP853_tolerance_refinement_max_difference',
        'spatial_nonabelian_curvature_norm_max','original_owner_checks')},sort_keys=True),flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True)
    evaluate(ap.parse_args().output)
