"""Original full18 Yukawa/current transfer, without selecting a Cauchy state.

This is a local operator identity and excitation-source application. It does
not turn a four-mode packet into a complete quantum constraint state, or a
classical Grassmann body into a prepared pair source.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys

import numpy as np


def transfer_operators(H):
    """Keep all four original gauge channels and the complex Higgs source.

    M(H) is real-linear. With T_c the original anti-Hermitian Higgs
    representation and G_c its full18 lepton representation,
        [G_c,M(H)] = M(T_c H).
    For i d_tau chi=M chi, d_tau(chi^dag iG_c chi) equals this torque.
    In the full spatial equation this is a covariant divergence, with all
    connection, measure, and interface terms retained by their own owners.
    """
    from bhsm.interface.muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian
    from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation

    h = np.asarray(H, complex)
    if h.ndim != 2 or h.shape[1] != 2 or not len(h) or not np.isfinite(h).all():
        raise ValueError('finite supplied complex Higgs doublets required')
    G = lepton_unit_trace_gauge_representation()['generators']
    T = higgs_u2_real_representation()['complex_generators']
    M = fixed_y_higgs_hamiltonian(h)
    delta_h = np.einsum('cij,pj->pci', T, h)
    scalar = np.asarray([fixed_y_higgs_hamiltonian(delta_h[:, c]) for c in range(4)]).swapaxes(0, 1)
    commutator = G[None] @ M[:, None] - M[:, None] @ G[None]
    basis = np.asarray([[1, 0], [0, 1], [1j, 0], [0, 1j]], complex)
    scalar_vertices = fixed_y_higgs_hamiltonian(basis)
    delta_real = np.concatenate((delta_h.real, delta_h.imag), axis=-1)
    scalar_reconstructed = np.einsum('pcd,dij->pcij', delta_real, scalar_vertices)
    return dict(H=h, gauge_generators=G, Higgs_generators=T, mass=M,
                gauge_H_variations=delta_h, scalar_real_variations=delta_real,
                scalar_vertices=scalar_vertices, mass_torque=commutator,
                Higgs_source_torque=scalar,
                real_scalar_source_torque=scalar_reconstructed,
                current_generators=1j*G)


def excitation_transfer(*, H, particle_modes, antiparticle_modes,
                        bilinear_expectation, canonical_spatial_density):
    """First excitation-source difference; no continuum two-current claim.

    The caller owns all packet/background/state/domain data. The four real
    source components are derivatives of chi^dag M(H) chi; the complex source
    is J=(source_Re + i source_Im)/2, so delta m=2Re(deltaH^dag J).
    Density is applied exactly once. Time/metric factors are not invented.
    """
    app = transfer_operators(H)
    h = app['H']
    u, v, rho = [np.asarray(x, complex) for x in
                 (particle_modes, antiparticle_modes, bilinear_expectation)]
    density = np.asarray(canonical_spatial_density)
    if u.shape != (len(h), 18, 2) or v.shape != u.shape or rho.shape != (4, 4):
        raise ValueError('same-point full18 packet columns and actual bilinear expectation required')
    if (not np.isrealobj(density) or density.shape != (len(h),)
            or not np.isfinite(density).all() or np.any(density <= 0)
            or any(not np.isfinite(x).all() for x in (u, v, rho))):
        raise ValueError('finite packet/state data and positive original canonical density required')
    f = np.concatenate((u, v), axis=-1)
    if not np.allclose(rho, rho.conj().T, rtol=0, atol=1e-13):
        raise ValueError('Hermitian bilinear expectation required')
    def mean(matrices):
        return np.einsum('pai,pcab,pbj,ij->pc', f.conj(), matrices, f, rho)
    torque = density[:, None]*mean(app['mass_torque'])
    vertices = np.broadcast_to(app['scalar_vertices'], (len(h), 4, 18, 18))
    source = density[:, None]*mean(vertices)
    complex_source = (source[:, :2]+1j*source[:, 2:])/2
    scalar_torque = 2*np.real(np.einsum('pci,pi->pc', app['gauge_H_variations'].conj(), complex_source))
    return dict(lepton_gauge_current_transfer=torque,
                real_Higgs_mass_source=source, complex_Higgs_mass_source=complex_source,
                Higgs_source_transfer=scalar_torque,
                transfer_identity_residual=torque-scalar_torque,
                physical_background_or_full_constraint_state_selected=False,
                continuum_Wick_product_or_local_CAR_completeness_claimed=False)


def exact_symbolic_certificate():
    """Prove 16 coefficient identities, for a generic complex family matrix.

    The exact unit-Tr16 normalizations are separately compared with original
    native arrays. The proof has no sampled Higgs field or physical vacuum.
    """
    import sympy as s
    I = s.I
    weak = [s.Matrix([[0, 1], [1, 0]])/2,
            s.Matrix([[0, -I], [I, 0]])/2,
            s.diag(1, -1)/2]
    T = [-I*t/s.sqrt(2) for t in weak]+[-I*s.eye(2)/(2*s.sqrt(s.Rational(10, 3)))]
    G = [s.diag(s.kronecker_product(t, s.eye(6)), s.zeros(6)) for t in T[:3]]
    G += [s.diag(-s.eye(12)/2, -s.eye(6))*(-I/s.sqrt(s.Rational(10, 3)))]
    Y = s.Matrix(3, 3, lambda i, j: s.Symbol(f'Y{i}{j}'))
    def mass(h):
        v = s.kronecker_product(h, s.kronecker_product(Y, s.eye(2)))
        return s.BlockMatrix([[s.zeros(12), v], [v.conjugate().T, s.zeros(6)]]).as_explicit()
    basis = [s.Matrix([1, 0]), s.Matrix([0, 1]), s.Matrix([I, 0]), s.Matrix([0, I])]
    checks = []
    for c in range(4):
        for j, h in enumerate(basis):
            m = mass(h)
            residual = G[c]*m-m*G[c]-mass(T[c]*h)
            nonzero = sum(s.simplify(z) != 0 for z in residual)
            checks.append(dict(gauge_channel=c, real_H_component=j, exact_nonzero_entries=nonzero))
    if any(row['exact_nonzero_entries'] for row in checks):
        raise ArithmeticError('original gauge/Higgs mass transfer does not close')
    from bhsm.interface.muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
    from bhsm.interface.muon_intrinsic_higgs_gauge_action import higgs_u2_real_representation
    ng = lepton_unit_trace_gauge_representation()['generators']
    nt = higgs_u2_real_representation()['complex_generators']
    dg = max(float(np.max(abs(np.array(g, complex)-native))) for g, native in zip(G, ng))
    dt = max(float(np.max(abs(np.array(t, complex)-native))) for t, native in zip(T, nt))
    if max(dg, dt) > 3e-16:
        raise ArithmeticError('exact coefficient proof does not match original representations')
    return dict(coefficient_checks=checks, full_lepton_components=18,
                arbitrary_complex_family_matrix=True, arbitrary_complex_H=True,
                native_generator_match_absolute=dg, native_Higgs_generator_match_absolute=dt,
                physical_H_or_packet_or_vacuum_selected=False)


def run(repository, output):
    root, out = Path(repository).resolve(), Path(output).resolve()
    sys.path[:0] = [str(root/'src'), str(root)]
    sources = [
        root/'src/bhsm/interface/muon_native_dirac_hamiltonian.py',
        root/'src/bhsm/interface/muon_native_product_factor_graph.py',
        root/'src/bhsm/interface/muon_intrinsic_higgs_gauge_action.py',
        root/'src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py',
        root/'src/bhsm/interface/muon_primal_electromagnetic_source.py',
        Path(__file__).resolve()]
    pins = {str(p): sha256(p.read_bytes()).hexdigest() for p in sources}
    proof = exact_symbolic_certificate()
    result = dict(
        classification='EXACT_ORIGINAL_FULL18_GAUGE_HIGGS_SOURCE_TRANSFER_IDENTITY',
        exact_certificate=proof,
        identity='[G_c,M(H)]=M(T_c H), all four original unitTr16 channels and both LR placements',
        local_time_identity='For i*d_tau chi=M(H)*chi: d_tau(chi^dag*iG_c*chi)=chi^dag*[G_c,M(H)]*chi',
        full_equation_requirement='The full covariant spacetime divergence also contains spatial transport, gauge connection, metric-density and moving-boundary terms; none is set to zero here.',
        original_scalar_source_normalization='delta(chi^dag*M(H)*chi)=2Re(deltaH^dag*J); J=(S_Re+i*S_Im)/2',
        source_transfer_rule='Gauge-current divergence and Higgs matter torque exchange; do not demand separate source-free lepton hypercharge continuity.',
        EM_rule='The H-aligned Q_H commutes with M(H); charge-axis derivatives and gauge commutators remain in the full continuity equation. The unitTr16 HY coordinate alone is not physical Q_EM.',
        use='Supplies exact local source-transfer terms for the common-state Gauss/Noether assembly. It does not determine spatial packets, physical constraints, LSZ states, quantum loops or F2(0).',
        physical_Cauchy_state_evaluated=False, physical_magnetic_moment=None,
        coupled_matching_corrections_applied=0, empirical_comparison_performed=False,
        source_D5_profile_canonical_or_pairing_integrations_restarted=False,
        input_sha256=pins)
    if any(sha256(Path(p).read_bytes()).hexdigest() != h for p, h in pins.items()):
        raise RuntimeError('source changed during proof')
    out.mkdir(parents=True, exist_ok=False)
    (out/'result.json').write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False)+'\n', encoding='utf8')
    print(json.dumps(dict(path=str(out/'result.json'),sha256=sha256((out/'result.json').read_bytes()).hexdigest(), exact_coefficient_checks=len(proof['coefficient_checks']))), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    run(args.repository, args.output)
