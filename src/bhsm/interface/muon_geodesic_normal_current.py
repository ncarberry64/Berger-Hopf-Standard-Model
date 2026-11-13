"""Exact represented geodesic kernels and local graph-vertex matching.

The two directed n0/n1 blocks determine a restricted bilocal kernel. Its
Wilson geodesic derivative is evaluated without replacing a literal
reverse by an adjoint. This is not the full Wigner integral or an exterior
pole amputation. The separate Higgs/charge identity identifies local graph
couplings, and does not subtract a finite tent loop from a continuum loop.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import expm

from .muon_changing_normal_current_readout import _finite
from .muon_intrinsic_normal_coordinate_readout import _evaluation
from .muon_intrinsic_scalar_discretization import scalar_basis_values, real_scalar_basis_transform, real_scalar_basis_labels
from .muon_magnetic_open_lepton_vertex import charged_dirac_injection, PAULI
from .muon_native_dirac_hamiltonian import fixed_y_higgs_hamiltonian, lepton_current_hilbert_representation
from .muon_intrinsic_higgs_weak_action import retained_higgs_spin_charge_representation

VOLUME = 2*np.pi**2


def represented_geodesic_current(constant_forward, constant_reverse, *, radius,
        connection, direction, separation):
    """Apply the actual retained right-coframe Wilson pair at +/-s/2.

    The background coframe connection is angular constant. Along one
    radial round geodesic its pullback is Omega_n ds, so these exponentials
    are its exact parallel maps. Their endpoint placements retain the
    anticommutator in the relative jet; the center jet instead has a
    commutator. Separation is an explicit numerical test parameter.
    """
    C = _finite(constant_forward, 'same-action spin-major n1<-n0 block', (3,24,6))
    B = _finite(constant_reverse, 'literal same-action n0<-n1 block', (3,6,24))
    R = float(_finite(radius, 'actual normal radius', (), real=True))
    s = float(_finite(separation, 'explicit geodesic separation', (), real=True))
    n = _finite(direction, 'geodesic unit direction', (3,), real=True)
    O = _finite(connection, 'actual full C6 right-coframe connection', (3,6,6))
    if R <= 0 or abs(s) >= np.pi*R or abs(float(n@n)-1) > 32*np.finfo(float).eps:
        raise ValueError('positive radius, unique local geodesic and explicit unit direction required')
    if np.max(abs(O+O.conj().transpose(0,2,1))) > 64*np.finfo(float).eps*max(1.,np.max(abs(O))):
        raise ValueError('actual anti-Hermitian spin/gauge connection required')
    sigma = np.einsum('a,aij->ij', n, PAULI)
    points = np.array([expm(-.5j*s*sigma/R), expm(.5j*s*sigma/R)])
    labels = real_scalar_basis_labels(1)
    ids = [j for j,l in enumerate(labels) if l[0] == 1]
    y = (scalar_basis_values(points,1) @ real_scalar_basis_transform(1))[:,ids]
    if np.max(abs(y.imag)) > 64*np.finfo(float).eps:
        raise ArithmeticError('retained real harmonic geodesic evaluation unresolved')
    c, b = C.reshape(3,6,4,6), B.reshape(3,6,6,4)
    kernel = (np.einsum('h,Aihj->Aij', y[0].real, c)+
        np.einsum('h,Aijh->Aij', y[1].real, b))/VOLUME
    On = np.einsum('a,aij->ij', n, O)
    U = expm(s*On/2)
    value, derivative = _evaluation((1,), R)
    K0 = (np.einsum('h,Aihj->Aij',value,c)+np.einsum('h,Aijh->Aij',value,b))/VOLUME
    coordinate = (np.einsum('a,ah,Aihj->Aij',n,derivative,c)-
        np.einsum('a,ah,Aijh->Aij',n,derivative,b))/(2*VOLUME)
    relative = coordinate+(On[None]@K0+K0@On[None])/2
    return dict(raw_bilocal_kernel=kernel, Wilson_bilocal_kernel=U[None]@kernel@U[None],
        coincidence_kernel=K0, exact_represented_relative_first_jet=relative,
        coordinate_relative_first_jet=coordinate,
        Wilson_relative_connection_contact=relative-coordinate,
        endpoint_transport=U, separation=s, direction=n.copy(),
        equation='K_W(X,s)=U(X,x) K(x,y) U(y,X), x=exp_X(+s*n/2), y=exp_X(-s*n/2)',
        angular_coefficient_order='spin-major; full n1/n0 and literal reverse',
        complete_Wigner_or_soft_Pauli_amputation_performed=False,
        geodesic_probe_is_physical_transfer=False, physical_F2=None)


def local_radial_higgs_charge_vertices(H, *, family):
    """Evaluate local overlap COUPLINGS on the same H-selected fiber.

    H=H_base+(h/sqrt(2))*H_base/|H_base| yields the retained fixed-Y radial
    vertex g_h=Y_family/sqrt(2), independently of the matched pole mass.
    It identifies the radial scalar graph already included in the local
    ledger. A same-domain Lorentz propagator/scalar-pole restriction is
    still needed before its continuum Pauli value is a subtraction from
    the evaluated changing finite positive-reference loop.
    """
    h = _finite(H, 'actual Higgs doublet', (2,))
    if type(family) is not int or family not in (1,2) or np.linalg.norm(h) == 0:
        raise ValueError('nonzero actual H and retained middle/light family required')
    u = h/np.linalg.norm(h)
    direction = u/np.sqrt(2)
    J = charged_dirac_injection(h,family=family)['charged']
    M = fixed_y_higgs_hamiltonian(direction[None])[0]
    forward = np.zeros_like(M); forward[:12,12:] = M[:12,12:]
    reverse = np.zeros_like(M); reverse[12:,:12] = M[12:,:12]
    Q = np.zeros((18,18),complex)
    Q[:12,:12] = -np.kron(np.outer(u,u.conj()),np.eye(6))
    Q[12:,12:] = -np.eye(6)
    Y = float(lepton_current_hilbert_representation()['family_Y'][family,family].real)
    gamma0 = retained_higgs_spin_charge_representation()['gamma_Dirac'][0]
    charged = J.conj().T @ M @ J
    return dict(radial_H_direction=direction,
        full_radial_fixed_Y_vertex=M,
        full_LR_forward_vertex=forward, full_LR_reverse_vertex=reverse,
        charged_radial_vertex=charged, fixed_Y=Y, radial_coupling=Y/np.sqrt(2),
        charged_vertex_identity_residual=charged-Y*gamma0/np.sqrt(2),
        full_aligned_charge_generator=Q, charged_charge_generator=J.conj().T@Q@J,
        charged_charge_identity_residual=J.conj().T@Q@J+np.eye(4),
        full_charge_mass_commutator=Q@fixed_y_higgs_hamiltonian(h[None])[0]-fixed_y_higgs_hamiltonian(h[None])[0]@Q,
        local_shared_graph='open lepton/radial-Higgs one-loop with BOTH retained LR vertices; local ledger fixed_yukawa_higgs_pauli g=Y/sqrt(2)',
        photon_VP_overlap_subtracted=False,
        finite_core_or_continuum_overlap_subtracted=False,
        same_local_couplings_evaluated=True,
        same_scalar_pole_and_Lorentz_domain_evaluated=False,
        independent_Yukawa_or_tree_mass_fit_performed=False,
        scalar_Gram_normalization='actual action Gram supplies scalar propagator normalization; no blanket angular-volume multiplier inserted',
        physical_F2=None)
