"""Executable spin/CAR/family preparation for the new e-e+ -> mu-mu+ run.

This binds the user-selected channel and head-on energy-scan protocol.
It does not borrow a C1/E1 geometry, supply a wavepacket/background, insert
a pole mass/coupling, or replace exact pair statistics by a quasifree state.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys


BENCHMARK_ID = 'BHSM_NEW_COLLIDER_ELECTRON_POSITRON_TO_MUON_ANTIMUON_V1'


def annihilators(mode_count):
    """CAR matrices on the bit-ordered finite Fock space."""
    import numpy as np
    operators = []
    for mode in range(mode_count):
        a = np.zeros((2**mode_count, 2**mode_count), complex)
        for state in range(2**mode_count):
            if state & (1 << mode):
                sign = (-1)**((state & ((1 << mode)-1)).bit_count())
                a[state ^ (1 << mode), state] = sign
        operators.append(a)
    return operators


def exact_unpolarized_pair():
    """One electron and one positron, with independent maximally mixed spins.

    Four abstract annihilation modes are e- up/down, e+ up/down. Physical
    continuum wavepacket mode functions and their CAR pairing are separate.
    """
    import numpy as np
    ops = annihilators(4)
    rho = np.zeros((16, 16), complex)
    for electron_spin in range(2):
        for positron_spin in range(2):
            state = (1 << electron_spin) | (1 << (2+positron_spin))
            rho[state, state] = .25
    occupations = [a.conj().T @ a for a in ops]
    N = np.asarray([[np.trace(rho @ ops[j].conj().T @ ops[i])
                     for j in range(4)] for i in range(4)])
    ne = occupations[0]+occupations[1]
    np_ = occupations[2]+occupations[3]
    identity = np.eye(16)
    car = max(float(np.max(abs(a @ b.conj().T+b.conj().T @ a
                  - (identity if i == j else 0))))
              for i, a in enumerate(ops) for j, b in enumerate(ops))
    C = np.block([[np.eye(4)-N, np.zeros((4, 4))],
                  [np.zeros((4, 4)), N.T]])
    gamma = np.block([[np.zeros((4, 4)), np.eye(4)],
                      [np.eye(4), np.zeros((4, 4))]])
    same_species_joint = np.trace(rho @ occupations[0] @ occupations[1])
    wick_joint = N[0, 0]*N[1, 1]-N[0, 1]*N[1, 0]
    values = dict(
        pair_Fock_density16=rho, one_body_occupation4=N,
        canonical_self_dual_covariance8=C, canonical_CAR_conjugation8=gamma,
        incoming_spin_pair_density4=np.eye(4)/4,
        electron_number_operator16=ne, positron_number_operator16=np_,
    )
    diagnostics = dict(
        Fock_CAR_residual=car, density_trace=float(np.trace(rho).real),
        density_minimum_eigenvalue=float(np.linalg.eigvalsh(rho).min()),
        electron_number=float(np.trace(rho @ ne).real),
        positron_number=float(np.trace(rho @ np_).real),
        electron_number_variance=float(np.trace(rho @ (ne-np.eye(16)) @ (ne-np.eye(16))).real),
        positron_number_variance=float(np.trace(rho @ (np_-np.eye(16)) @ (np_-np.eye(16))).real),
        total_charge=float(np.trace(rho @ (np_-ne)).real),
        pair_state_even_parity=True,
        exact_electron_up_down_joint_occupation=float(same_species_joint.real),
        same_covariance_quasifree_up_down_joint_occupation=float(wick_joint.real),
        exact_minus_quasifree_joint_occupation=float((same_species_joint-wick_joint).real),
        self_dual_CAR_residual=float(np.linalg.norm(C+gamma @ C.conj() @ gamma.T-np.eye(8))),
        full_pair_state_is_quasifree=False,
    )
    if max(car, abs(diagnostics['density_trace']-1),
           abs(diagnostics['electron_number']-1), abs(diagnostics['positron_number']-1),
           diagnostics['electron_number_variance'], diagnostics['positron_number_variance'],
           diagnostics['self_dual_CAR_residual']) > 1e-14:
        raise ArithmeticError('exact pair preparation identities failed')
    return values, diagnostics


def validate_beam_mode_embedding(pairing, beam_modes, charge_operator, metadata):
    """Rebind actual supplied beam packets to this exact finite pair state.

    Columns are electron up/down, positron up/down in the action-owned
    positive-frequency annihilation Hilbert space. No embedding is defaulted.
    """
    import numpy as np
    G, W, Q = (np.asarray(a, complex) for a in (pairing, beam_modes, charge_operator))
    required = ('benchmark_id', 'action_identity', 'background_identity', 'Cauchy_domain_identity',
                'positive_frequency_owner', 'wavepacket_preparation_owner', 'family_embedding_owner')
    if any(not isinstance(metadata.get(k), str) or not metadata[k] for k in required):
        raise ValueError('complete physical beam/background/positive-frequency provenance required')
    if metadata['benchmark_id'] != BENCHMARK_ID:
        raise ValueError('a packet from another physical run cannot be spliced into this collider')
    if G.ndim != 2 or G.shape[0] != G.shape[1] or W.shape != (len(G), 4) or Q.shape != G.shape:
        raise ValueError('same action Cauchy pairing, four beam-spin modes and charge operator required')
    if any(not np.isfinite(a).all() for a in (G, W, Q)):
        raise ValueError('finite supplied physical operands required')
    if np.max(abs(G-G.conj().T)) > 1e-12 or np.linalg.eigvalsh(G).min() <= 0:
        raise ValueError('the supplied Dirac Cauchy pairing must be positive Hermitian')
    gram = W.conj().T @ G @ W-np.eye(4)
    charge = Q @ W-W @ np.diag([-1, -1, 1, 1])
    if max(np.max(abs(gram)), np.max(abs(charge))) > 2e-10:
        raise ValueError('beam packets violate the original CAR Gram or charge-sector embedding')
    return dict(beam_Gram_residual=float(np.max(abs(gram))),
                beam_charge_eigenvector_residual=float(np.max(abs(charge))),
                physical_state_complete=False,
                remaining='Same-family projector, energy/trajectory, Hadamard background, coupled constraints and scattering action still require their supplied physical binding.')


def spin_averaged_amplitude_squared(action_amplitude):
    """Contract a supplied 4-final-spin by 4-initial-spin action amplitude."""
    import numpy as np
    M = np.asarray(action_amplitude, complex)
    if M.shape != (4, 4) or not np.isfinite(M).all():
        raise ValueError('full finite action-owned spin-resolved amplitude4x4 required')
    value = np.trace(M @ (np.eye(4)/4) @ M.conj().T)
    if abs(value.imag) > 2e-10 or value.real < -2e-10:
        raise ArithmeticError('spin density contraction is not real nonnegative')
    return float(value.real)


def run(repository, output):
    root, out = Path(repository).resolve(), Path(output).resolve()
    out.mkdir(parents=True, exist_ok=False)
    sys.path[:0] = [str(root/'src'), str(root)]
    import numpy as np
    import sympy as sp
    from bhsm.interface.ae3_family_harmonic_energy_pullback import MODE_ASSIGNMENTS, ROLE_ORDER, slot_projectors
    from bhsm.interface.muon_birth_fermion_state_representation import charge_conjugate_family_projector
    from bhsm.interface.ae31_c2_reset_hadamard_transport import transport_self_dual_covariance
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    pins = {}
    def cite(path, needle, before=2, after=10):
        data = path.read_bytes(); lines = data.decode('utf8').splitlines()
        matches = [i for i, line in enumerate(lines) if needle in line]
        if len(matches) != 1:
            raise ValueError('unique source anchor required '+str(path)+' '+needle)
        i = matches[0]; digest = sha256(data).hexdigest(); pins[str(path)] = digest
        return dict(path=str(path), first_line=max(1, i+1-before), last_line=min(len(lines), i+1+after), sha256=digest)
    if ROLE_ORDER != ('heavy', 'middle', 'light') or MODE_ASSIGNMENTS['charged_lepton'] != ((0, 0), (5, 2), (9, 3)):
        raise ValueError('frozen charged-lepton label map changed')
    frozen_path = root/'artifacts/action_extension/BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json'
    data = frozen_path.read_bytes(); pins[str(frozen_path)] = sha256(data).hexdigest()
    frozen_rows = json.loads(data)['family_mode_C2_instantiation']['rows']
    selected = {role: dict(sector='charged_lepton', slot=ROLE_ORDER.index(role),
                  mode_label=list(MODE_ASSIGNMENTS['charged_lepton'][ROLE_ORDER.index(role)]))
                for role in ('light', 'middle')}
    for row in selected.values():
        matches = [x for x in frozen_rows if x['sector'] == row['sector'] and x['slot'] == row['slot']]
        if len(matches) != 1 or matches[0]['mode_label'] != row['mode_label'] or matches[0]['projector_rank'] != 1:
            raise ValueError('frozen particle-fiber receipt disagrees with explicit selected role map')
    projectors = slot_projectors()
    Pe, Pmu = (projectors[ROLE_ORDER.index(role)].astype(complex) for role in ('light', 'middle'))
    Qe, Qmu = (charge_conjugate_family_projector(P) for P in (Pe, Pmu))
    gamma_family = np.block([[np.zeros((3, 3)), np.eye(3)], [np.eye(3), np.zeros((3, 3))]])
    pair, checks = exact_unpolarized_pair()
    identity8 = np.eye(8)
    car_check = transport_self_dual_covariance(pair['canonical_self_dual_covariance8'], identity8,
        pair['canonical_CAR_conjugation8'], pair['canonical_CAR_conjugation8'], tolerance=1e-12)
    # Identity here only checks canonical Nambu coordinates. It is no physical reset.
    E, me, mm, pe, pm = sp.symbols('E_beam m_e_action m_mu_action p_in p_out', positive=True)
    eta = sp.diag(1, -1, -1, -1)
    pminus, pplus = sp.Matrix([E, 0, 0, pe]), sp.Matrix([E, 0, 0, -pe])
    invariant_s = sp.expand(((pminus+pplus).T @ eta @ (pminus+pplus))[0])
    shell = sp.expand((pminus.T @ eta @ pminus)[0]-me**2).subs(pe**2, E**2-me**2)
    if invariant_s != 4*E**2 or sp.simplify(shell) != 0:
        raise ArithmeticError('local tetrad head-on kinematic identity failed')
    family_checks = dict(
        electron_rank=int(round(np.trace(Pe).real)), muon_rank=int(round(np.trace(Pmu).real)),
        electron_muon_overlap=float(np.linalg.norm(Pe @ Pmu)),
        electron_conjugate_sector_invariance=float(np.linalg.norm(gamma_family @ Qe.conj() @ gamma_family.T-Qe)),
        muon_conjugate_sector_invariance=float(np.linalg.norm(gamma_family @ Qmu.conj() @ gamma_family.T-Qmu)),
    )
    src = root/'src/bhsm/interface'
    citations = dict(
        frozen_role_mode_map=cite(src/'ae3_family_harmonic_energy_pullback.py', 'ROLE_ORDER =', before=7, after=15),
        family_charge_conjugation=cite(src/'muon_birth_fermion_state_representation.py', 'def charge_conjugate_family_projector(', after=12),
        CAR_conjugation_convention=cite(src/'ae31_c2_reset_hadamard_transport.py', '``Gamma(v)=G*conjugate(v)``', before=3, after=6),
        free_retarded_state_scope=cite(src/'muon_birth_fermion_state_representation.py', 'retarded="G_R=', before=5, after=6),
        active_intrinsic_lepton_action=cite(src/'ae31_c2_intrinsic_m4_lepton_action.py', '"action_term": (', after=10),
        momentum_map=cite(src/'universal_momentum_map.py', 'class ActionMomentumMap:', after=28),
        collision_readout=cite(src/'universal_decay_collision.py', 'def two_to_two_differential_cross_section(', after=31),
        angular_readout=cite(src/'universal_decay_collision.py', 'def integrate_two_to_two_cross_section(', after=20),
    )
    pins[str(root/'AGENTS.md')] = sha256((root/'AGENTS.md').read_bytes()).hexdigest()
    arrays = dict(electron_family_projector3=Pe, muon_family_projector3=Pmu,
                  electron_charge_conjugate_family_sector6=Qe, muon_charge_conjugate_family_sector6=Qmu,
                  family_conjugation_matrix6=gamma_family, **pair)
    packet = out/'actual_frozen_family_and_exact_pair_spin_CAR_preparation.npz'
    _compressed_npz(packet, arrays)
    report = dict(
        classification='NEW_TYPED_COLLIDER_PREPARATION_WITH_EXECUTED_FROZEN_FAMILY_AND_EXACT_TWO_PARTICLE_SPIN_CAR_BINDING',
        benchmark_id=BENCHMARK_ID, process='e- + e+ -> mu- + mu+',
        physical_preparation=dict(
            channel_authority='User selected electron-positron collider production of a muon-antimuon pair as the first predictive benchmark.',
            geometry_of_beam_centers='Equal-energy head-on incoming beams; zero transverse impact parameter for the first baseline.',
            energy='External beam-energy scan variable E_beam; no numerical energy or energy grid selected.',
            polarization='Unpolarized baseline assumption, explicitly replaceable: independent I_spin2/2 for each incoming species.',
            old_muon_run_reused_as_collider=False,
        ),
        outgoing_readout=dict(
            target='The muon-antimuon family component is an OUTPUT projection/readout of the action-derived outgoing state.',
            muon_pair_forced_as_only_final_state=False,
            all_other_action_coupled_outgoing_and_radiation_channels_retained=True,
            final_zoo='All other admitted action-coupled fields, particles, radiation and surviving enclosure/geometry degrees remain in the outgoing realization.',
            two_body_kinematic_scope='The displayed opposite outgoing momenta and two-body phase-space helper describe the exclusive two-body muon-pair component when that readout applies; they are not a projection deleting real radiation or other output channels.',
        ),
        selected_family_map=dict(
            frozen_order=list(ROLE_ORDER),
            electron=dict(role='light', **selected['light'], charge_particle=-1, charge_antiparticle=1),
            muon=dict(role='middle', **selected['middle'], charge_particle=-1, charge_antiparticle=1),
            heavy_slot_not_electron=dict(role='heavy', slot=0, mode_label=[0, 0]),
            labels_are_internal_family_modes_not_spatial_Dirac_levels=True,
            mapping_source='Frozen MODE_ASSIGNMENTS/ROLE_ORDER and rank-one slot_projectors, cross-checked against preserved family-fiber rows. No mass screen reordered the slots.',
        ),
        executed=dict(family_checks=family_checks, pair_statistics=checks,
            existing_CAR_validator_event_reality_residual=car_check['event_self_dual_CAR_residual'],
            existing_CAR_validator_order_margin=car_check['event_order_margin'],
            identity_transport_used_only_as_coordinate_CAR_check_not_physical_reset=True,
            native_projector_and_charge_conjugate_constructor_executed=True),
        pair_state_scope=dict(
            exact_preparation='rho_pair=1/4 sum_(s,t) |e-_s,e+_t><e-_s,e+_t| on exactly-one-of-each charge sector.',
            beam_mode_order=['electron_up', 'electron_down', 'positron_up', 'positron_down'],
            CAR_convention='N_ij=<c_j^dagger c_i>; C_sd=diag(I-N,N^T); canonical antiunitary Gamma(v)=G*conjugate(v).',
            one_body_covariance_not_whole_state='N=I4/2 and C_sd=I8/2 have the same two-point data as a quasifree half-occupation state, but the exact pair has <n_eup*n_edown>=0 rather than 1/4. Preserve rho_pair for four-point collision contractions.',
            canonical_Nambu_conjugation_not_full_physical_spinor_charge_conjugation=True,
            family_antiparticle_owner='Q_family=diag(P_family,conjugate(P_family)) from the existing constructor. Full spin/carrier charge-conjugation intertwiners still belong to the supplied physical packet embedding.',
            continuum_Cauchy_state_or_Hadamard_background_selected=False,
        ),
        symbolic_head_on_kinematics=dict(
            frame='Local orthonormal collider tetrad with +--- convention; no global flat geometry inferred.',
            incoming=['(E_beam,0,0,+p_in)', '(E_beam,0,0,-p_in)'],
            equations=['p_in^2=E_beam^2-m_e_action^2', 's=4*E_beam^2',
                       'p_out^2=E_beam^2-m_mu_action^2', 'outgoing central momenta are opposite'],
            threshold='E_beam>=max(m_e_action,m_mu_action) for the displayed two-body channel once physical same-action pole masses and common units are supplied.',
            s_identity_verified=str(invariant_s), incoming_mass_shell_identity_verified=True,
            tetrad_to_coordinate_momentum='Requires a new benchmark background/tetrad and ActionMomentumMap from that action geometry; no old C2 geometry or unowned Minkowski physical map is inserted.',
            dimensionless_axis='x=E_beam/m_mu_action is only a symbolic dimensionless control when the native muon pole is bound. No QED reference curve or empirical mass fixes the BHSM action, scale or packet.',
        ),
        executable_rebind_APIs=dict(
            beam='validate_beam_mode_embedding(G,W,Q,metadata): actual positive Dirac Cauchy pairing, four packet-spin modes, charge operator and explicit new benchmark/background/positive-frequency/family/wavepacket provenance.',
            spin_amplitude='spin_averaged_amplitude_squared(M4x4)=Tr(M*(I4/4)*M^dagger). A physical action-derived amplitude is required; none defaulted.',
            collision_readout='Existing two_to_two_differential_cross_section/integrate_two_to_two_cross_section consume physical same-unit masses and action amplitude; they do not generate the amplitude or prepared Cauchy state.',
            averaging='The matrix contraction already includes 1/4. Pass initial_state_average=1 when its result is consumed, or supply an unaveraged spin sum with initial_state_average=4, never both.',
        ),
        independent_remaining_inputs=[
            'New benchmark regular-stratum collision background/geometry, active domains, action Cauchy pairing and tetrad/momentum map, with coupled constraints and asymptotic/finite-boundary preparation specified.',
            'Electron and positron packet mode functions: spatial/energy spread, separation and encounter timing/overlap, longitudinal profile and phase/coherence data where observable; b=0 and equal central energies do not determine these functions.',
            'Physical positive-frequency/antiparticle embedding and background matter covariance, with Hadamard/renormalization prescription only for state-sensitive contractions that use them; exact pair excitations are not inferred from free retarded propagation.',
            'The native same-domain electron/muon manifestation/pole states, masses and residues in a common action unit. Frozen family labels alone are not those pole modes.',
            'Same-action interacting gauge/Higgs/gravity/matter scattering amplitude or causal encounter solution and final muon pair/outgoing readout; universal phase-space helpers need these operands.',
            'A numerical beam-energy scan range/grid once an owned energy unit and accessible threshold are bound; no phenomenological theory coefficient is fitted.',
        ],
        artifact=dict(path=packet.name, sha256=sha256(packet.read_bytes()).hexdigest()),
        source_citations=citations, input_hashes=pins,
        masses_couplings_or_action_parameters_inserted=False,
        old_C1_E1_or_muon_primal_or_tensor_spliced=False,
        physical_Cauchy_collision_or_cross_section_prediction_admitted=False,
        producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
    )
    serialized=json.dumps(report, sort_keys=True, indent=2, allow_nan=False)+'\n'
    (out/'result.json').write_text(serialized, encoding='utf8', newline='\n')
    (out/'executed_producer.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(result=str(out/'result.json'), sha256=sha256(serialized.encode()).hexdigest(),
        packet_sha256=report['artifact']['sha256'], selected_family_map=report['selected_family_map'],
        pair_statistics=checks)))


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a=p.parse_args()
    run(a.repository, a.output)
