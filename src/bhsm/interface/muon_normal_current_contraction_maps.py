"""Exact external-test reduction of the reached normal current covectors.

All contractions are complex bilinear coefficient contractions. Only the
owned spinor injection contains an adjoint; the literal current left map
is not replaced by the conjugate of its right map. Each displayed dyad
can be consumed before the spectral kernel, without an external tensor.
"""
from __future__ import annotations
import numpy as np

from .muon_changing_normal_current_readout import _finite, _normal_second_evaluation
from .muon_intrinsic_normal_coordinate_readout import _evaluation
from .muon_intrinsic_covariant_open_current_jet import normal_coordinate_first_momentum_lift, round_spatial_spin_connection
from .muon_native_product_factor_graph import lepton_unit_trace_gauge_representation
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation, fixed_y_higgs_hamiltonian
from .muon_magnetic_open_lepton_vertex import charged_dirac_injection, PAULI
from .muon_intrinsic_higgs_weak_action import retained_higgs_spin_charge_representation


def _commutator_dual(terms, connection):
    """Tr B[Omega,M]=Tr[B,Omega]M, with literal row/column order."""
    answer = []
    for coefficient, left, right in terms:
        answer.append((coefficient, left @ connection, right))
        answer.append((-coefficient, left, connection @ right))
    return answer


def _grad_dual(terms, i, values, derivatives, connection):
    return [(c, l, r, derivatives[i]) for c, l, r in terms] + [
        (c, l, r, values) for c, l, r in _commutator_dual(terms, connection[i])]


def _hessian_dual(terms, i, j, values, derivatives, hessian, connection, frame):
    result = [(c, l, r, hessian[i, j]) for c, l, r in terms]
    result += [(c, l, r, derivatives[j]) for c, l, r in _commutator_dual(terms, connection[i])]
    result += [(c, l, r, derivatives[i]) for c, l, r in _commutator_dual(terms, connection[j])]
    result += [(c, l, r, values) for c, l, r in _commutator_dual(
        _commutator_dual(terms, connection[i]), connection[j])]
    result += [(c, l, r, values) for c, l, r in _commutator_dual(terms, frame)]
    return result


def _bundle(terms, *, input_harmonic=None):
    coefficient, left, right = [], [], []
    for c, l, r, h in terms:
        coefficient.append(c)
        left.append((l[:, None] * h[None, :]).ravel())
        right.append(r if input_harmonic is None else
            (r[:, None] * input_harmonic[None, :]).ravel())
    c, l, r = np.asarray(coefficient, complex), np.asarray(left, complex), np.asarray(right, complex)
    return dict(coefficients=c, left_tests=l, right_tests=r,
        tensor_weight=np.einsum('t,to,ti->oi', c, l, r),
        adjoint_of_literal_left_imposed=False)


def _combine(bundles):
    c = np.concatenate([a['coefficients'] for a in bundles])
    l = np.concatenate([a['left_tests'] for a in bundles])
    r = np.concatenate([a['right_tests'] for a in bundles])
    return dict(coefficients=c, left_tests=l, right_tests=r,
        tensor_weight=np.einsum('t,to,ti->oi', c, l, r),
        adjoint_of_literal_left_imposed=False)


def normal_current_contraction_maps(*, family_indices, radius, wall_connection, H,
        electric_charge, family):
    """Build the action-bound external maps for all complex spin components.

    C has axes [source,spin6*n1,spin6]; T has
    [source,spin6*(n0+n2),spin6*n1]. Each map is a sum of explicit
    rank-one tests arising from rank-two spin tests or rank-four FW
    commutators. Connection multiplication acts on the full six fibers,
    so a neutral intermediate is not discarded by charged injection.
    """
    if type(family) is not int or family not in (1, 2):
        raise ValueError('explicit middle/light action family required')
    ids = np.asarray(family_indices)
    owned = np.array([2*family, 2*family+1, 6+2*family, 7+2*family, 12+2*family, 13+2*family])
    if ids.dtype.kind not in 'iu' or not np.array_equal(ids, owned):
        raise ValueError('literal complete C6 family injection required')
    R = float(_finite(radius, 'actual normal radius', (), real=True))
    e = float(_finite(electric_charge, 'same measured source charge', (), real=True))
    if min(R, e) <= 0:
        raise ValueError('positive actual radius and independently matched charge required')
    wall = _finite(wall_connection, 'complete actual wall connection', (5, 4), real=True)
    higgs = _finite(H, 'actual Higgs doublet', (2,))
    full = round_spatial_spin_connection(R)['connection'] + np.einsum(
        'ac,cij->aij', wall[2:], lepton_unit_trace_gauge_representation()['generators']) / R
    other = np.setdiff1d(np.arange(18), ids)
    operators = [*full, *lepton_current_hilbert_representation()['alpha'],
        fixed_y_higgs_hamiltonian(higgs[None])[0]]
    if any(np.any(a[np.ix_(ids, other)]) or np.any(a[np.ix_(other, ids)]) for a in operators):
        raise ValueError('the owned action must preserve the supplied complete family')
    omega = full[:, ids][:, :, ids]
    J = np.eye(18)[:, ids].T @ charged_dirac_injection(higgs, family=family)['charged']
    gamma = retained_higgs_spin_charge_representation()['gamma_Dirac']
    alpha = np.array([gamma[0] @ g for g in gamma[1:]])
    y, dy = _evaluation((1,), R)
    z, dz = _evaluation((0, 2), R)
    ddz, epsilon = _normal_second_evaluation(R)
    Q = normal_coordinate_first_momentum_lift(R)['scalar_coordinate_coefficients']
    result = {key: [] for key in ('right_mass_C', 'right_FW_C',
        'Weyl_mass_C', 'Weyl_mass_T', 'Weyl_FW_C', 'Weyl_FW_T')}
    for k in range(3):
        band, comm = [], [[] for _ in range(3)]
        for a in range(2):
            for b in range(2):
                p = PAULI[k, a, b]
                if p == 0:  # literal structural Pauli zero, not a threshold
                    continue
                band.append((p, J[:, b].conj(), J[:, a]))
                for i in range(3):
                    comm[i].append((p, alpha[i, b] @ J.conj().T, J[:, a]))
                    comm[i].append((-p, J[:, b].conj(), J @ alpha[i, :, a]))
        mass = [(c/e, l, r, y) for c, l, r in band]
        fw = [(c*(-1j/(4*e)), l, r, h) for i in range(3)
            for c, l, r, h in _grad_dual(comm[i], i, y, dy, omega)]
        result['right_mass_C'].append(_bundle(mass))
        result['right_FW_C'].append(_bundle(fw))
        result['Weyl_mass_C'].append(_bundle([(2.5*c, l, r, h) for c, l, r, h in mass]))
        result['Weyl_FW_C'].append(_bundle([(3*c, l, r, h) for c, l, r, h in fw]))
        mass_T, fw_T = [], []
        for j in range(3):
            terms = [(c*(-.5/e), l, r, h) for c, l, r, h in
                _grad_dual(band, j, z, dz, omega)]
            mass_T.append(_bundle(terms, input_harmonic=Q[:, j]))
            for i in range(3):
                frame = sum(epsilon[i, j, s] * omega[s] / R for s in range(3))
                terms = [(c*(1j/(8*e)), l, r, h) for c, l, r, h in
                    _hessian_dual(comm[i], i, j, z, dz, ddz, omega, frame)]
                fw_T.append(_bundle(terms, input_harmonic=Q[:, j]))
        result['Weyl_mass_T'].append(_combine(mass_T))
        result['Weyl_FW_T'].append(_combine(fw_T))
    positive = J[:, :2] @ J[:, :2].conj().T
    result.update(charged_injection=J, full_C6_spatial_connection=omega,
        kinetic_residue_energy_weight=positive.T/2,
        kinetic_residue_spin_equation='spin({Z,sigma_A}/2)_k=delta_Ak Tr(Z)/2',
        kinetic_residue_applied=False, action_mass_selected=False,
        current_Gaussian_sign_or_charge_reapplied=False,
        equation='right=m*Cmass+CFW; Weyl=m*(2.5*Cmass+Tmass)+(3*CFW+TFW); SAME-E0 residue added once separately',
        neutral_return_retained=True, full_bilocal_or_physical_Pauli_claimed=False)
    return result


def project_external_moments(left, right, bundle):
    """Apply literal external tests BEFORE any spectral contraction.

    Left layout [...,external_out,F,B], right [...,F,external_in,B].
    Optional source-axis prefixes are preserved independently.
    """
    L, R = _finite(left, 'actual literal left current moments'), _finite(right, 'actual right current moments')
    l, r = bundle['left_tests'], bundle['right_tests']
    if L.ndim < 3 or R.ndim < 3 or L.shape[-3] != l.shape[1] or R.shape[-2] != r.shape[1]:
        raise ValueError('same external column ordering is required by the tests')
    return dict(left=np.einsum('to,...ofb->...tfb', l, L),
        right=np.einsum('...fjb,tj->...tfb', R, r), coefficients=bundle['coefficients'])


def dyadic_two_green_contraction(left, right, kernel, bundle):
    """Stream a two-Green term; its action sign is supplied by the caller."""
    a = project_external_moments(left, right, bundle)
    K = _finite(kernel, 'same two-Green scalar kernel')
    if K.shape != a['left'].shape[-2:] or K.shape != a['right'].shape[-2:]:
        raise ValueError('same internal spectral axes required')
    return np.einsum('t,...tfb,...tfb,fb->...', a['coefficients'], a['left'], a['right'], K)


def dyadic_three_green_contraction(left, right, direction, kernel, bundle):
    """Stream an ordered insertion, preserving rectangular spectral axes."""
    a = project_external_moments(left, right, bundle)
    D = _finite(direction, 'actual ordered operator insertion')
    K = _finite(kernel, 'same three-Green scalar kernel')
    nt, nb, ns = a['left'].shape[-2], a['left'].shape[-1], a['right'].shape[-2]
    if K.shape != (nt, ns, nb) or D.shape[-2:] != (nt, ns) or a['right'].shape[-1] != nb:
        raise ValueError('both actual rectangular insertion axes required')
    return np.einsum('d,...dtb,...ts,...dsb,tsb->...', a['coefficients'],
        a['left'], D, a['right'], K)


def tensor_covector_application(constant_forward, tangent_forward, maps, *, energy_first=None):
    """Verify/project complete owned external arrays with the SAME maps."""
    C = _finite(constant_forward, 'complete constant source action', (3, 24, 6))
    T = _finite(tangent_forward, 'complete momentum source action', (3, 60, 24))
    project = lambda name, a: np.array([np.einsum('oi,Aoi->A', row['tensor_weight'], a)
        for row in maps[name]]).T
    right_mass, right_fw = project('right_mass_C', C), project('right_FW_C', C)
    weyl_mass = project('Weyl_mass_C', C) + project('Weyl_mass_T', T)
    weyl_fw = project('Weyl_FW_C', C) + project('Weyl_FW_T', T)
    answer = dict(right_symbol=dict(mass_coefficient=right_mass, FW_constant_coefficient=right_fw),
        first_Weyl_symbol=dict(mass_coefficient=weyl_mass, FW_constant_coefficient=weyl_fw))
    if energy_first is not None:
        E = _finite(energy_first, 'actual SAME-frequency nonmagnetic energy derivative', (6, 6))
        residue = np.einsum('ij,ij->', maps['kinetic_residue_energy_weight'], E) * np.eye(3)
        for row in answer.values():
            row['kinetic_residue_constant_coefficient'] = residue
            row['constant_coefficient'] = row['FW_constant_coefficient'] + residue
    return answer
