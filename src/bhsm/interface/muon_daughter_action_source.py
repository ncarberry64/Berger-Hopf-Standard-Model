"""Daughter-current tensor and supplied-domain first jet of the owned action.

The charged/neutral injections and all 24 gauge/Higgs vertices are inherited.
No W-mass formula, V-A fit, external state, or outgoing domain is selected.
"""
from __future__ import annotations

import numpy as np

from .muon_owned_static_charged_current import owned_static_charged_current
from .muon_magnetic_open_lepton_vertex import canonical_open_field_vertices
from .muon_piecewise_euclidean_action import FAMILY_INDICES


def daughter_tensor(right, returned, left):
    """C_abcd (nu_mu†_a mu_b)(e†_c nu_e_d), with literal left placement."""
    r, g, l = (np.asarray(x, complex) for x in (right, returned, left))
    n = len(r)
    if (r.shape != (n, 2, 4) or g.shape != (n, n)
            or l.shape != (n, 4, 2) or not n
            or any(not np.isfinite(x).all() for x in (r, g, l))):
        raise ValueError('complete finite right/return/literal-left maps required')
    return np.einsum('aij,ab,bkl->ijkl', r, g, l)


def daughter_tensor_first(right, returned, left, dright, dreturned, dleft):
    """All three product contacts; dleft is not replaced by dright†."""
    return (daughter_tensor(dright, returned, left)
            + daughter_tensor(right, dreturned, left)
            + daughter_tensor(right, returned, dleft))


def quotient_trace_return_first(operator, inclusion, trace,
                                operator_first, inclusion_first, trace_first):
    """G=P A^-1 P^T and its full supplied-coordinate first derivative.

    A=Q^T K Q and P=T Q. The real coefficient maps use analytic transposes.
    All dQ/dT contacts are retained. Their physical moving-domain values
    still must be supplied; this function does not assert they vanish.
    """
    k, q, t, dk, dq, dt = (np.asarray(x, complex) for x in
        (operator, inclusion, trace, operator_first, inclusion_first, trace_first))
    if (k.ndim != 2 or k.shape[0] != k.shape[1] or q.ndim != 2
            or q.shape[0] != len(k) or t.ndim != 2 or t.shape[1] != len(k)
            or dk.shape != k.shape or dq.shape != q.shape or dt.shape != t.shape
            or any(not np.isfinite(x).all() for x in (k, q, t, dk, dq, dt))):
        raise ValueError('compatible finite original operator/domain/trace jets required')
    a = q.T @ k @ q
    da = dq.T @ k @ q + q.T @ dk @ q + q.T @ k @ dq
    p, dp = t @ q, dt @ q + t @ dq
    u = np.linalg.solve(a, p.T)
    du = np.linalg.solve(a, dp.T - da @ u)
    return dict(returned=p @ u, returned_first=dp @ u + p @ du,
                original_response=q @ u,
                original_response_first=dq @ u + q @ du,
                reduced_equation_residual=a @ u - p.T,
                physical_retarded_domain_admitted=False)


def owned_daughter_vertices_first(H, *, radius, lapse, H_first,
                                  radius_first, lapse_first,
                                  family=1, out_family=2):
    """Real-parameter derivative of H-selected weak-major spin injections.

    Includes both charged/neutral moving bases, At/N, Ai/R and the fixed-Y
    Higgs vertices. Domain/trace/source contacts belong in the return jet.
    The wall current angular normalization remains one.
    """
    h, dh = np.asarray(H, complex), np.asarray(H_first, complex)
    scalars = np.asarray([radius, lapse, radius_first, lapse_first])
    if (h.shape != (2,) or dh.shape != (2,) or not np.isfinite(h).all()
            or not np.isfinite(dh).all() or np.linalg.norm(h) == 0
            or not np.isrealobj(scalars) or not np.isfinite(scalars).all()
            or min(radius, lapse) <= 0 or family not in (0, 1, 2)
            or out_family not in (0, 1, 2)):
        raise ValueError('actual nonzero H and real positive metric with jets required')
    owned = owned_static_charged_current(np.eye(24), h, radius=radius,
                                        lapse=lapse, family=family, out_family=out_family)
    length = np.linalg.norm(h)
    e = h / length
    de = dh / length - e * np.vdot(e, dh).real / length
    zero = np.zeros((2, 2), complex)
    eye = np.eye(2)
    dj = np.vstack((np.c_[de[0]*eye, zero], np.c_[de[1]*eye, zero], np.c_[zero, zero]))
    dn = np.vstack((de[1].conjugate()*eye, -de[0].conjugate()*eye, zero))
    v = canonical_open_field_vertices(radius, lapse)
    allv = np.concatenate((v['gauge'].reshape(20, 18, 18), v['scalar']))
    dv = np.zeros_like(allv)
    dv[:4] = -lapse_first / lapse * allv[:4]
    dv[8:20] = -radius_first / radius * allv[8:20]
    derivatives = []
    for f, keyj, keyn in ((family, 'right_charge_injection', 'right_neutral_injection'),
                          (out_family, 'left_charge_injection', 'left_neutral_injection')):
        fi = FAMILY_INDICES[f]
        a, da = allv[:, fi][:, :, fi], dv[:, fi][:, :, fi]
        j, n = owned[keyj], owned[keyn]
        derivatives.append((n.conj().T @ a @ dj + n.conj().T @ da @ j + dn.conj().T @ a @ j,
                            dj.conj().T @ a @ n + j.conj().T @ da @ n + j.conj().T @ a @ dn))
    return dict(right=owned['charged_current_right_vertices'],
                left=owned['charged_current_left_vertices'],
                right_first=derivatives[0][0], left_first=derivatives[1][1],
                charged_injection_first=dj, neutral_injection_first=dn,
                physical_external_modes_or_LSZ_selected=False)


def daughter_bilinear_sources(right, left, *, muon, neutrino, electron, antineutrino):
    """Open-field source factors for explicitly supplied spinor columns.

    The antineutrino is the outgoing v column of nu_e, not a new singlet.
    These complex amplitude factors are not classical real expectation currents.
    """
    r, l = np.asarray(right, complex), np.asarray(left, complex)
    vectors = [np.asarray(x, complex) for x in (muon, neutrino, electron, antineutrino)]
    if (r.ndim != 3 or r.shape[1:] != (2, 4) or l.shape != (len(r), 4, 2)
            or not np.isfinite(r).all() or not np.isfinite(l).all()
            or any(v.shape != (n,) or not np.isfinite(v).all()
                   for v, n in zip(vectors, (4, 2, 4, 2)))):
        raise ValueError('explicit compatible open daughter spinors required')
    mu, nu, el, anti = vectors
    return dict(muon_neutrino=np.einsum('i,aij,j->a', nu.conj(), r, mu),
                electron_antineutrino=np.einsum('i,aij,j->a', el.conj(), l, anti))
