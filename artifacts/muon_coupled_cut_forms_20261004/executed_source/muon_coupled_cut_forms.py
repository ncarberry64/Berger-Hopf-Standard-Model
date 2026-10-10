"""Source-reached cut blocks for the muon exterior assembly.

These are local Dirac-form densities on the retained cut, not an exterior
resolvent or a finite replacement for the stratified heat operator.  The
independent W/p representation preserves the large correlated projection
derivatives without subtracting large quadratic forms to recover p.
"""
from __future__ import annotations

import numpy as np

from bhsm.interface.muon_radial_inclusion_action import nodal_jets


class ExteriorActionUnavailable(RuntimeError):
    """A prescribed exterior action has not been materialized."""


def source_frame(contact, corrected):
    """Independent image of the actual 32 source columns, in Haar pairing."""
    xi = {}
    gram = np.zeros((32, 32), complex)
    for n in (1, 3):
        raw = contact[f'Xi_A_unit_n{n}'][:, :, corrected['source_image_probe_columns']]
        flat = raw.transpose(1, 3, 4, 0, 2).reshape(-1, 32)
        xi[n] = flat.reshape(64, n + 1, n + 1, 32)
        gram += flat.conj().T @ flat
    ev, U = np.linalg.eigh(gram)
    # A separated numerical image quotient, not a regularized inverse.
    threshold = 1e-12 * ev[-1]
    keep = ev > threshold
    S = U[:, keep] / np.sqrt(ev[keep])[None, :]
    basis = {n: np.einsum('omki,ij->omkj', a, S) for n, a in xi.items()}
    receipt = dict(rank=int(sum(keep)), eigenvalues=ev.tolist(), threshold=float(threshold),
                   smallest_retained=float(ev[keep][0]),
                   largest_discarded_absolute=float(np.max(abs(ev[~keep]))),
                   orthonormality_residual=float(np.linalg.norm(S.conj().T @ gram @ S - np.eye(sum(keep)))),
                   quotient_scope='numerically separated actual source image; no continuum tail theorem',
                   arbitrary_diagonal_added=False)
    return xi, basis, gram, S, receipt


def radial_grid(geometry, order, cells=None):
    """Cellwise Gauss grid; interfaces are never crossed by one polynomial."""
    selected = np.arange(len(geometry['rho']) - 1) if cells is None else np.array(cells)
    x, w = np.polynomial.legendre.leggauss(order)
    widths = np.diff(geometry['rho'])[selected]
    points = (geometry['rho'][selected, None] + widths[:, None] * (x + 1) / 2).ravel()
    weights = (widths[:, None] * w / 2).ravel()
    return points, np.repeat(selected, order), weights


def endpoint_scalars(geometry, contact, endpoint, radial, rates, points, cells):
    """Extend the already extracted endpoint action ONLY in rho at this cut."""
    j = nodal_jets(geometry, points, cells)
    nu, C, r, z = (j[k] for k in ('proper_lapse', 'C_rho', 'base_radius', 'proper_shift_rho'))
    nr, Cr, rr, zr = (j[k + '_r'] for k in ('proper_lapse', 'C_rho', 'base_radius', 'proper_shift_rho'))
    x = (points - geometry['rho'][cells]) / np.diff(geometry['rho'])[cells]
    def interp(key):
        a = endpoint[key].mean(axis=1)
        return a[cells] * (1 - x) + a[cells + 1] * x
    Ct, rt = interp('action_C_tau_nodes'), interp('action_r_tau_nodes')
    m = endpoint['endpoint_lapse_rate_point'].mean(axis=1)
    k = np.arange(1, 13)
    Lnu = (np.cos(2 * points[:, None] * k) - (-1.)**k) @ m
    I, Idot, H = rates['I'], rates['Idot'], rates['H']
    nb, Rb = (float(geometry[k][0, -1]) for k in ('proper_lapse', 'base_radius'))
    u = np.sin(points / 2) / np.sqrt(I * (nu / nb) * (r / Rb)**3)
    logu = -Idot / (2 * I) - Lnu / 2 - 3 * rt / (2 * r) + 1.5 * H
    lr = -nr / (2 * nu) - 3 * rr / (2 * r) + .5 / np.tan(points / 2)
    h0 = (Ct / C + 3 * rt / r - z * (Cr / C + 3 * rr / r) - zr) / (2 * nu)
    h4 = (nr / nu + 3 * rr / r) / (2 * C)
    eta = -.5 / (C * np.tan(points / 2))
    # Stable same-action expression, including all correlated time changes.
    a0 = (-Idot / (2 * I) - Lnu / 2 + 1.5 * H + Ct / (2 * C)
          - z * Cr / (2 * C) - zr / 2 + z * nr / (2 * nu)
          - .5 * z / np.tan(points / 2)) / nu
    hatnodes = contact['spinor_probe_hat_nodes']
    hat = hatnodes[cells] * (1 - x) + hatnodes[cells + 1] * x
    hatr = np.diff(hatnodes)[cells] / np.diff(geometry['rho'])[cells]
    Tb = float(contact['T_b'])
    p = Tb * hat / r
    pr = Tb * (hatr / r - hat * rr / r**2)
    pt = (-H / 2 - rt / r) * p
    volume = 2 * np.pi**2 * nu * C * r**3
    cauchy = volume / nu
    return dict(points=points, cells=cells, nu=nu, C=C, r=r, z=z, u=u, p=p,
                pr=pr, pt=pt, h0=h0, h4=h4, eta=eta, a0=a0,
                bg=-j['B'] / (j['A'] * np.hypot(j['A'], j['B'])),
                logu=logu, Lnu=Lnu, Ct=Ct, rt=rt, lr=lr,
                volume=volume, cauchy=cauchy,
                logvolume=Lnu + Ct / C + 3 * rt / r,
                logcauchy=Ct / C + 3 * rt / r,
                logp=-H / 2 - rt / r,
                normal_cancellation=lr / C + h4 + eta)


def field_actions(s, xi, n, radial):
    """Full carrier/angular output, with no block heat or angular compression."""
    G = radial['common_parent_Gamma']
    spin, gauge = radial['angular_spin'], radial['commonA_gauge_unit']
    E = radial[f'angular_E_n{n}']
    gxi = [np.einsum('oi,imkj->omkj', 1j * g, xi) for g in G]
    angular = sum(np.einsum('omkj,vm->ovkj', gxi[a + 1], E[a]) for a in range(3))
    common = np.einsum('oi,imkj->omkj', spin, xi)
    gauged = np.einsum('oi,imkj->omkj', gauge, xi)
    scale = lambda a, f: a[:, None, None, None, None] * f[None]
    DW = (scale(s['u'] * s['a0'], gxi[0]) + scale(s['u'] / s['r'], common + angular)
          + scale(s['u'] * s['bg'], gauged))
    Dp = (scale(s['p'] * s['h0'] + (s['pt'] - s['z'] * s['pr']) / s['nu'], gxi[0])
          + scale(s['p'] * (s['h4'] + s['eta']) + s['pr'] / s['C'], gxi[4])
          + scale(s['p'] / s['r'], common + angular) + scale(s['p'] * s['bg'], gauged))
    return DW, Dp, scale(s['u'] / s['nu'], gxi[0]), scale(s['p'] / s['nu'], gxi[0])


def endpoint_form(geometry, contact, corrected, radial, endpoint, pairing, rates, order=8):
    """Instantiate amplitude/time-jet local blocks and moving projection."""
    raw, basis, gram, S, frame = source_frame(contact, corrected)
    points, cells, gw = radial_grid(geometry, order)
    s = endpoint_scalars(geometry, contact, endpoint, radial, rates, points, cells)
    mu4 = float(radial['wall_M4'][0, 0])
    gs = float(radial['cut_Cauchy_trace_Gram'][0, 0])
    # Instantaneous norm/overlap certificates are reused, not recomputed.
    T = rates['T']; Ts = rates['Ts']; b = T / mu4; bs = Ts / gs
    Tdot = float(np.dot(gw * s['volume'], s['u'] * s['p'] * (s['logvolume'] + s['logu'] + s['logp'])))
    Tsdot = float(np.dot(gw * s['cauchy'], s['u'] * s['p'] * (s['logcauchy'] + s['logu'] + s['logp'])))
    Gsdot = float(np.dot(gw * s['cauchy'], s['u']**2 * (s['logcauchy'] + 2 * s['logu'])))
    M4dot = 3 * rates['H'] * mu4
    bdot = (Tdot - M4dot * b) / mu4
    bsdot = (Tsdot - Gsdot * bs) / gs
    d = S.shape[1]
    K = np.zeros((4 * d, 4 * d), complex)
    source_index = int(np.flatnonzero(np.diag(gram).real > frame['threshold'])[0])
    e = np.eye(32)[:, source_index]
    c = S.conj().T @ gram @ e
    selected = {}
    decomposition_error = 0.; derivative_omission = 0.
    for n in (1, 3):
        reached = [[], [], [], []]
        for start in range(0, len(points), 32):
            stop = min(start + 32, len(points))
            chunk = {k: v[start:stop] for k, v in s.items()}
            fields = field_actions(chunk, basis[n], n, radial)
            # Factored local form; conjugation is the geometric positive L2
            # pairing in the common frame, not a Spin-boost assumption.
            F = np.concatenate(fields, axis=-1).reshape(stop-start, -1, 4*d)
            K += np.einsum('g,gai,gaj->ij', (gw*s['volume'])[start:stop], F.conj(), F, optimize=True)
            for k, a in enumerate(fields):
                reached[k].append(np.einsum('gomki,i->gomk', a, c))
        DW, Dp, DtW, Dtp = [np.concatenate(a) for a in reached]
        W = s['u'][:, None, None, None] * np.einsum('omki,i->omk', basis[n], c)[None]
        p = s['p'][:, None, None, None] * np.einsum('omki,i->omk', basis[n], c)[None]
        chi = p - b * W
        Dchi = Dp - b * DW - bdot * DtW
        selected.update({f'W_n{n}':W, f'p_n{n}':p, f'chi_n{n}':chi,
                         f'DW_n{n}':DW, f'Dp_n{n}':Dp, f'Dchi_n{n}':Dchi,
                         f'DtauW_n{n}':DtW, f'Dtaup_n{n}':Dtp})
        decomposition_error += float(np.linalg.norm(p - (b * W + chi))**2)
        derivative_omission += float(np.linalg.norm(bdot * DtW)**2)
    unit = np.eye(d)
    Mpp = S.conj().T @ pairing['source_geometric_Gram'] @ S
    M = np.block([[mu4 * unit, T * unit], [T * unit, Mpp]])
    Mspp = float(np.dot(gw * s['cauchy'], s['p']**2))
    Ms = np.block([[gs * unit, Ts * unit], [Ts * unit, Mspp * unit]])
    # Coordinates of (W,chi,W-time,chi-time) -> (W,p,W-time,p-time).
    J = np.block([[unit, -b * unit, np.zeros((d,d)), np.zeros((d,d))],
                  [np.zeros((d,d)),unit,np.zeros((d,d)),np.zeros((d,d))],
                  [np.zeros((d,d)),-bdot * unit,unit,-b * unit],
                  [np.zeros((d,d)),np.zeros((d,d)),np.zeros((d,d)),unit]])
    q_chi = np.concatenate((b * c, c, bdot * c, np.zeros(d)))
    q_wp = J @ q_chi  # Correlated coefficients cancel BEFORE form application.
    exact_wp = np.concatenate((np.zeros(d), c, np.zeros(2*d)))
    rhsK = K @ exact_wp
    rhsM = M @ exact_wp[:2*d]
    source_energy = float(np.vdot(c, rhsK[d:2*d]).real)
    source_mass = float(np.vdot(c, rhsM[d:2*d]).real)
    arrays = dict(points=points,cells=cells,radial_weights=gw,volume_density=s['volume'],
                  Cauchy_density=s['cauchy'],radial_u=s['u'],source_scalar=s['p'],
                  Lnu_direct=s['Lnu'],action_C_tau=s['Ct'],action_r_tau=s['rt'],
                  source_Haar_Gram=gram,independent_source_map=S,source_coordinates=c,
                  local_cut_K_Wp_timejet=K,local_cut_M_Wp=M,local_cut_Cauchy_Wp=Ms,
                  complement_jet_to_Wp=J,source_full_complement_jet=q_chi,
                  source_cancellation_preserved_jet=exact_wp,rhs_K=rhsK,rhs_M=rhsM,**selected)
    receipt = dict(frame=frame,cut='C2_step1222 endpoint_predictor_center',
        source_column=source_index,source_A=source_index//4,input_spin=source_index%4,
        quadrature_order=order,radial_cells=len(geometry['rho'])-1,full_cap=True,
        bulk_projection=dict(B=b,B_tau=bdot,T_tau=Tdot,M4_tau=M4dot),
        temporal_Cauchy_projection=dict(B=bs,B_tau=bsdot,T_tau=Tsdot,G_tau=Gsdot),
        source_local_Dirac_energy_per_tau=source_energy,source_bulk_mass_per_tau=source_mass,
        K_amplitude_block_norms={f'{a}{b_}':float(np.linalg.norm(K[a*d:(a+1)*d,b_*d:(b_+1)*d])) for a in range(2) for b_ in range(2)},
        source_K_rhs_norm=float(np.linalg.norm(rhsK)),source_M_rhs_norm=float(np.linalg.norm(rhsM)),
        mass_smallest_eigenvalue=float(np.linalg.eigvalsh(M)[0]),
        K_Hermitian_relative_residual=float(np.linalg.norm(K-K.conj().T)/np.linalg.norm(K)),
        field_decomposition_residual=float(np.sqrt(decomposition_error)),
        correlated_jet_reconstruction_residual=float(np.linalg.norm(q_wp-exact_wp)),
        action_if_projection_derivative_omitted_norm=float(np.sqrt(derivative_omission)),
        physical_a_mu=None,physical_g_mu=None,heat_evaluations=0,
        inclusion_domain_scope='retained radial candidate local first-order graph; full exterior reset/material/canonical-stop weak domain not promoted',
        error_scope='binary64 nodal-cut local Dirac-form densities; quadrature comparison is not a bound; endpoint/tube/interpolation/continuum errors remain separate')
    return arrays, receipt


def require_exterior_history_action(actions):
    """Assembly stops at the first consumed, non-cut connected action."""
    key = 'connected_history_weak_action'
    if actions.get(key) is None:
        raise ExteriorActionUnavailable(
            'K_ext,chi-chi and its coupled trace action: '
            'integral_Iext <D5,0 chi_i,D5,0 chi_j>_5 d tau + owned seam/domain terms; '
            'M_ext,chi-chi=integral_Iext <chi_i,chi_j>_5 d tau. '
            'The endpoint density is not this inherited-history action.')
    return actions[key]
