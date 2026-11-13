"""Source controls for the original M8 S3 bolt, not a physical state solve.

This consumes saved real snapshots and the actual original left-Maurer
Spin16 expression. It does not choose an internal twist, native carrier,
outgoing domain or matching coefficient. All prior files remain unchanged.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys

import mpmath as mp
import numpy as np


INPUT_SHA = '9a132366d729c85ea1d83815a5482fbf6352b117507e9f447abb4c3b7534739d'
ROOT = Path(__file__).resolve().parents[1]


def maximum(a):
    return float(np.max(abs(a)))


def original_archive(base):
    relative = 'stable_time6_run_1/changing_forms.npz'
    path = base / relative
    pins = {}
    if path.exists():
        raw = path.read_bytes()
        pins[relative] = sha256(raw).hexdigest()
    else:
        recipe_path = base / 'exact_archive_reconstruction.json'
        recipe = json.loads(recipe_path.read_bytes())[relative]
        pins['exact_archive_reconstruction.json'] = sha256(recipe_path.read_bytes()).hexdigest()
        parts = []
        for part in recipe['chunks']:
            value = (base / part['path']).read_bytes()
            if len(value) != part['bytes'] or sha256(value).hexdigest() != part['sha256']:
                raise ValueError('Changed preserved exact input chunk')
            pins[part['path']] = part['sha256']
            parts.append(value)
        raw = b''.join(parts)
    if sha256(raw).hexdigest() != INPUT_SHA:
        raise ValueError('Exact original time6 real snapshots required')
    return raw, pins


def expected(n):
    v = [-(n + 1.5)] * ((n + 1) * (n + 2))
    if n:
        v += [-(n + .5)] * (n * (n + 1))
        v += [n + .5] * (n * (n + 1))
    v += [n + 1.5] * ((n + 1) * (n + 2))
    return np.sort(np.tile(v, 4))  # Spin16, not new physical copies.


def quaternion_components(q, pauli):
    return np.r_[np.array([np.trace(s @ q) / (2j) for s in pauli]), np.trace(q) / 2]


def evaluate(repository):
    root = Path(repository).resolve()
    sys.path.insert(0, str(root / 'src'))
    from bhsm.interface.muon_original_m8_geometric_expression import (
        original_m8_clifford, original_left_maurer_coefficient_maps)
    from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace
    from bhsm.interface.muon_intrinsic_scalar_discretization import (
        scalar_angular_derivative_matrices, scalar_section_labels, scalar_basis_values)
    from bhsm.interface.muon_holomorphic_normal_geometry import _geometry_variables, _fields
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.aether_post_cut_nonround_lorentzian_cap_v15_48 import RADIUS0

    base = root / 'artifacts/muon_real_changing_gauge_transport_20261016'
    raw, input_pins = original_archive(base)
    with np.load(BytesIO(raw), allow_pickle=False) as z:
        states = {side: z[side + '_radial32_raw'].copy() for side in ('incoming', 'outgoing')}
        times = {side: z[side + '_radial32_temporal_coordinate_time'].copy() for side in states}
    arrays = {}
    actual_records = []
    # MP64 evaluates the original elementary coframe independently of Jet
    # implementation. Proper arclength is integrated, not equated to chi.
    with mp.workdps(64):
        radius0 = mp.mpf(343) / 5
        radius0 = radius0 ** (mp.mpf(1) / 6)
        for side, raws in states.items():
            if not np.isrealobj(raws) or not np.isfinite(raws).all():
                raise ValueError('Saved actual real raw snapshots required')
            arrays[side + '_raw'] = raws
            arrays[side + '_coordinate_times'] = times[side]
            for index, raw_state in enumerate(raws):
                rr = [mp.mpf(float(a)) for a in raw_state[:100]]
                q, m = rr[:37], rr[74:98]
                a0 = radius0 * mp.exp(q[0] + sum(q[1:13]))
                n0 = mp.exp(sum(m[:12]))
                u2 = -8 * sum(j*j*q[j] for j in range(1, 13))
                w2, b2 = 4*sum(q[13:25]), 4*sum(q[25:37])
                c2, a2 = u2+w2, u2+b2-mp.mpf(1)/2
                br2 = u2-b2-mp.mpf(1)/6-c2/3
                n2 = -8*sum(j*j*m[j-1] for j in range(1, 13))
                beta1 = 4*sum(m[12:])

                def coframe(x):
                    u = sum(q[j]*mp.cos(4*j*x) for j in range(1, 13))
                    w = mp.sin(2*x)**2 * sum(q[13+j]*mp.cos(4*j*x) for j in range(12))
                    b = mp.sin(2*x)**2 * sum(q[25+j]*mp.cos(4*j*x) for j in range(12))
                    radius = radius0*mp.exp(q[0])
                    return (radius*mp.exp(u+w), radius*mp.exp(u+b)*mp.cos(x),
                        radius*mp.exp(u-b)*mp.sin(x),
                        mp.exp(sum(m[j-1]*mp.cos(4*j*x) for j in range(1, 13))),
                        mp.sin(4*x)*sum(m[12+j]*mp.cos(4*j*x) for j in range(12)))

                qj, vj, mj, *_ = _geometry_variables(raw_state[:100], differentiate=False)
                steps = []
                for text in ('0.01', '0.005', '0.0025'):
                    chi = mp.mpf(text)
                    C, A, B, N, beta = coframe(chi)
                    r = mp.quad(lambda x: coframe(x)[0], [0, chi])
                    f = _fields(12, qj, vj, mj, type(qj[0]).constant(float(chi), 0))
                    owned = [f[k].value for k in ('C', 'A', 'B', 'N', 'beta')]
                    literal = [C, A, B, N, beta]
                    # mp str is retained for cancellation-sensitive endpoint limits.
                    limits = dict(C_minus_a0_over_chi2=(C/a0-1)/chi**2,
                        A_minus_a0_over_chi2=(A/a0-1)/chi**2,
                        B_minus_r_over_chi2=(B/r-1)/chi**2,
                        N_minus_n0_over_chi2=(N/n0-1)/chi**2,
                        beta_over_r=beta/r)
                    target = dict(C_minus_a0_over_chi2=c2, A_minus_a0_over_chi2=a2,
                        B_minus_r_over_chi2=br2, N_minus_n0_over_chi2=n2,
                        beta_over_r=beta1/a0)
                    steps.append(dict(chi=text, proper_r=mp.nstr(r, 45),
                        owned_vs_MP_max_entry_scaled=max(float(abs(complex(a)-complex(b))/max(1,abs(complex(a)),abs(complex(b)))) for a,b in zip(owned,literal)),
                        endpoint_ratios={k: mp.nstr(v, 45) for k,v in limits.items()},
                        endpoint_limit_errors={k: mp.nstr(abs(v-target[k]), 45) for k,v in limits.items()}))
                actual_records.append(dict(side=side, time_index=index, coordinate_time=float(times[side][index]),
                    bolt_radius_a0=mp.nstr(a0, 45), center_lapse_n0=mp.nstr(n0, 45),
                    exact_endpoint_limits={k: mp.nstr(v, 45) for k,v in target.items()}, steps=steps))

    full = full_d5_localized_lepton_trace()
    # The existing geometric constructor takes 0,chi,u123, not 0,123,chi.
    gamma = original_m8_clifford(full['gamma5D_particle'][[0, 4, 1, 2, 3]])
    arrays['actual_Gamma8_original'] = gamma
    angular_records = []
    for n in range(5):
        labels = scalar_section_labels(n)
        E = original_left_maurer_coefficient_maps(scalar_angular_derivative_matrices(n), labels)
        offset = sum((k+1)**2 for k in range(n))
        h = (n+1)**2
        E = E[:, offset:offset+h, offset:offset+h]
        I = np.eye(h)
        G = np.array([np.kron(g, I) for g in gamma])
        normal = sum(np.kron(gamma[a+5], E[a]) for a in range(3))
        K = -G[1] @ (normal + 1.5*G[5]@G[6]@G[7])
        alpha = G[0]@G[1]
        eig = np.linalg.eigvalsh(K)
        arrays[f'n{n}_K'] = K
        arrays[f'n{n}_spectrum'] = eig
        arrays[f'n{n}_left_v_angular'] = E
        # These coefficient identities imply all-u-frequency anticommutation,
        # rather than checking only one chosen tangential harmonic.
        wu_coefficients = [G[0]@G[a] for a in (2,3,4)] + [1.5j*G[0]@G[2]@G[3]@G[4]]
        angular_records.append(dict(scalar_v_PW_level=n, full_Spin16_width=16*h,
            Hermitian_defect=maximum(K-K.conj().T), spectrum_error=maximum(eig-expected(n)),
            alpha_K_anticommutator=maximum(alpha@K+K@alpha),
            full_u_coefficient_K_commutator=max(maximum(w@K-K@w) for w in wu_coefficients),
            full_u_coefficient_alpha_anticommutator=max(maximum(w@alpha+alpha@w) for w in wu_coefficients),
            minimum_radial_positive_square=float(np.min(eig*(eig+1))),
            expected_spectrum=expected(n).tolist()))

    pauli = np.array([[[0,1],[1,0]],[[0,-1j],[1j,0]],[[1,0],[0,-1]]],complex)
    xyz = np.array([[0,0,0,1],[1,2,3,4],[-2,1,3,1],[3,-4,1,-2],[0,1,0,0]],float)
    xyz /= np.linalg.norm(xyz,axis=1)[:,None]
    points = xyz[:,3,None,None]*np.eye(2)+1j*np.einsum('pa,aij->pij',xyz[:,:3],pauli)
    phi = scalar_basis_values(points, 1)
    E = original_left_maurer_coefficient_maps(scalar_angular_derivative_matrices(1),scalar_section_labels(1))
    dpoints = np.array([(phi@E[a])[:,1:].reshape(-1,2,2).conj()/np.sqrt(2) for a in range(3)])
    omega = gamma[5]@gamma[6]@gamma[7]@gamma[1]
    pp, pm = (np.eye(16)+omega)/2,(np.eye(16)-omega)/2
    J = np.array([gamma[a+5]@gamma[1]@pp for a in range(3)])

    def frame(q):
        x=quaternion_components(q,pauli)
        return pm+(x[3]*np.eye(16)+sum(x[a]*gamma[a+5]@gamma[1] for a in range(3)))@pp

    frame_records=[]
    for p,q in enumerate(points):
        S=frame(q);dS=[];literal=[]
        for a in range(3):
            dx=quaternion_components(dpoints[a,p],pauli)
            d=(dx[3]*np.eye(16)+sum(dx[b]*gamma[b+5]@gamma[1] for b in range(3)))@pp
            dS.append(d)
            for step in (1e-3,3e-4,1e-4):
                def at(t):return frame(q@(np.cos(t)*np.eye(2)-1j*np.sin(t)*pauli[a]))
                fd=(at(-2*step)-8*at(-step)+8*at(step)-at(2*step))/(12*step)
                literal.append(dict(axis=a+1,step=step,absolute_error=maximum(fd-d)))
        contact=sum(gamma[a+5]@S.conj().T@dS[a] for a in range(3))
        target=1.5*gamma[1]+1.5*gamma[5]@gamma[6]@gamma[7]
        arrays[f'point{p}_S']=S;arrays[f'point{p}_source_dS']=np.array(dS)
        frame_records.append(dict(quaternion_index=p,unitary_defect=maximum(S.conj().T@S-np.eye(16)),
            tangent_Gamma_commutator=max(maximum(S@gamma[a]-gamma[a]@S) for a in(0,2,3,4)),
            source_left_vector_field_identity=max(maximum(dpoints[a,p]+1j*q@pauli[a]) for a in range(3)),
            exact_connection_identity=maximum(contact-target),
            exact_frame_derivative_identity=maximum(np.array(dS)+np.array([S@j for j in J])),
            literal_right_multiplication_controls=literal))

    sources = [Path(__file__).resolve(), root/'src/bhsm/interface/muon_original_m8_geometric_expression.py',
        root/'src/bhsm/interface/muon_holomorphic_normal_geometry.py',
        root/'src/bhsm/interface/muon_m8_m5_geometric_coefficients.py',
        root/'src/bhsm/interface/aether_post_cut_nonround_lorentzian_cap_v15_48.py',
        root/'src/bhsm/interface/muon_intrinsic_scalar_discretization.py',
        root/'src/bhsm/interface/muon_full_d5_localized_lepton_trace.py']
    # Preserve both primary mathematical owners and every consumed bhsm
    # Python dependency. The explicit producer is part of the same root.
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if name.startswith('bhsm') and p and Path(p).is_relative_to(root) and Path(p).suffix=='.py':
            sources.append(Path(p).resolve())
    pins = {p.relative_to(root).as_posix(): sha256(p.read_bytes()).hexdigest() for p in set(sources)}
    input_pins={(base.relative_to(root)/p).as_posix():h for p,h in input_pins.items()}
    result = dict(classification='ORIGINAL_M8_GEOMETRIC_S3_BOLT_SOURCE_CONTROLS',
        exact_input_archive_sha256=INPUT_SHA, exact_input_chunk_pins=input_pins,source_pins=pins,
        actual_real_orbit_asymptotic_records=actual_records,angular_records=angular_records,
        unitary_polar_frame_records=frame_records,
        normal_slice_dimension=4,surviving_orbit='S3_u', collapsed_orbit='S3_v',
        all_spin16_retained=True,tangential_u_spectrum_not_cut_off_in_theorem=True,
        finite_control_v_scalar_cutoff=4, bounded_twist_not_assigned_zero_as_physical_input=True,
        form_placement='local real geometric plus_product A=Dtau+W only',
        lorentz_positive_square_ellipticity_claimed=False,
        full_native_statistics_or_stratified_operator_selected=False,
        global_outgoing_or_physical_derivative_claimed=False, coupled_corrections=0,
        normalized_physical_spin_states=None,muon_magnetic_moment=None)
    return result,arrays,_compressed_npz


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--repository',default=str(ROOT));parser.add_argument('--output',required=True)
    args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('Preserve every prior source-control result')
    result,arrays,archive=evaluate(args.repository);out.mkdir(parents=True)
    archive(out/'controls.npz',arrays)
    result['numerical_sha256']=sha256((out/'controls.npz').read_bytes()).hexdigest()
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(numerical_sha256=result['numerical_sha256'],actual_records=len(result['actual_real_orbit_asymptotic_records']),angular_records=len(result['angular_records']))))
