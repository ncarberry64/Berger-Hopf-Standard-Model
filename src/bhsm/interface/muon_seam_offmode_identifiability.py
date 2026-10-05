"""A source-directed identifiability witness, never a native operator entry.

No value of the symbolic completion coordinate lambda is selected. The
scalar witness h=p/u is mathematical test data, not a new physical profile.
The inherited normalized mode and source amplitudes are read, not rebuilt.
"""
from fractions import Fraction
import numpy as np
from bhsm.interface.muon_matched_mechanical_source import product_tensor


def conjugate_harmonic(a, n):
    """Conjugate phi_nmk=sqrt(n+1)*conj(D_mk), in the saved convention."""
    labels = np.arange(n, -n-1, -2)
    phase = (-1.) ** ((labels[:, None]-labels[None, :])//2)
    return a[..., ::-1, ::-1].conj()*phase


def scalar_product(g, f, ng, ns, nt):
    """Full connected product, with leading axes broadcast explicitly."""
    return np.einsum('uvijkl,...ij,...kl->...uv',
                     product_tensor(ng, ns, nt), g, f, optimize=True)


def unit_higgs_coefficients():
    """H1=w*(0,1), in the same sigma1 section as the saved sources.

    D_mk=(-1)^((m-k)/2)*phi_n,-m,-k/sqrt(n+1). These are
    representation coefficients; no Higgs amplitude or Yukawa is chosen.
    """
    h = np.zeros((2, 2, 2), complex)
    h[0, 1, 0] = -1/np.sqrt(2)
    h[1, 0, 0] = 1/np.sqrt(2)
    return h


def higgs_identity_residuals(h, rotation):
    """Focused fundamental/adjoint matching, not a repeat of carrier rows."""
    pauli = np.array([[[0, 1], [1, 0]], [[0, -1j], [1j, 0]],
                      [[1, 0], [0, -1]]], complex)
    residual = 0.0
    for nt in (0, 2):
        hh = np.array([[scalar_product(h[c], conjugate_harmonic(h[d], 1),
                                       1, 1, nt) for d in range(2)]
                       for c in range(2)])
        expected = (np.eye(2)[:, :, None, None]/2 if nt == 0 else
                    -np.einsum('acd,aij->cdij', pauli, rotation[:, 2])/2)
        residual = max(residual, float(np.linalg.norm(hh-expected)))
    norm = sum(scalar_product(conjugate_harmonic(h[c], 1), h[c], 1, 1, 0)
               for c in range(2))
    tail = sum(scalar_product(conjugate_harmonic(h[c], 1), h[c], 1, 1, 2)
               for c in range(2))
    return dict(fundamental_adjoint_residual=residual,
                unit_higgs_norm_residual=float(np.linalg.norm(norm-1)),
                unit_higgs_connected_norm_residual=float(np.linalg.norm(tail)))


def radial_witness(weights, volume, u, p, b, mu4):
    """Direct p*(p-b*u) contraction; exact bound for frozen binary inputs.

    This certifies the dyadic sum, not quadrature, continuum history or the
    adopted normalized-mode identity. No old normalization is re-evaluated.
    """
    u, p = np.asarray(u), np.asarray(p)
    if np.any((p != 0) & (u <= 0)):
        raise ValueError('witness division would be undefined on source support')
    h = np.divide(p, u, out=np.zeros_like(p), where=p != 0)
    chi = p-b*u
    frac = lambda x: Fraction.from_float(float(x))
    exact = sum((frac(w)*frac(v)*frac(pv)*(frac(pv)-frac(b)*frac(uv))
                 for w, v, uv, pv in zip(weights, volume, u, p)), Fraction(0))/frac(mu4)
    nominal = float(exact)
    lo, hi = nominal, nominal
    if frac(lo) > exact:
        lo = float(np.nextafter(lo, -np.inf))
    if frac(hi) < exact:
        hi = float(np.nextafter(hi, np.inf))
    direct = float(np.dot(weights*volume, p*chi)/mu4)
    return dict(h=h, chi=chi, eta=nominal, eta_interval=np.array([lo, hi]),
                exact_eta_numerator=str(exact.numerator),
                exact_eta_denominator=str(exact.denominator),
                direct_binary64_eta=direct,
                h_max=float(np.max(np.abs(h))))


def forward_unit_higgs(left, h):
    """H1^dagger Pi_L Xi; keep n0,n2,n4, all spin and source columns."""
    out = {}
    for ns, val in left.items():
        for nt in range(abs(ns-1), ns+2, 2):
            z = out.setdefault(nt, np.zeros((4, nt+1, nt+1, val.shape[-1]), complex))
            for c in range(2):
                z += scalar_product(conjugate_harmonic(h[c], 1),
                                    val[:, c].transpose(0, 3, 1, 2),
                                    1, ns, nt).transpose(0, 2, 3, 1)
    return out


def reverse_unit_higgs(wall, h):
    """H1 times the full wall image; keep n1,n3,n5 without pruning."""
    out = {}
    for ns, val in wall.items():
        for nt in range(abs(ns-1), ns+2, 2):
            z = out.setdefault(nt, np.zeros((4, 2, nt+1, nt+1, val.shape[-1]), complex))
            for c in range(2):
                z[:, c] += scalar_product(h[c], val.transpose(0, 3, 1, 2),
                                         1, ns, nt).transpose(0, 2, 3, 1)
    return out


def apply_spin(g, values):
    return {n: np.einsum('st,t...->s...', g, a) for n, a in values.items()}


def evaluated_witness(basis, gamma0, eta, h, radial, weights, volume, mu4):
    """Proposed mixed derivative per lambda and per Y,H amplitude.

    Forward outputs are Euler duals, not selected physical e_R states.
    The reverse is the Dirac-bar dual; its radial factor chi is saved
    separately. A full reverse function/kernel is not necessary here.
    """
    pl = np.diag([1., 1., 0., 0.])  # inherited LR order, not normal K polarization
    full_left = {n: np.einsum('st,tcmkj->scmkj', pl,
                             x.reshape(4, 16, n+1, n+1, -1)[:, 6:8])
                 for n, x in basis.items()}
    forward_h = forward_unit_higgs(full_left, h)
    e45 = {n: -eta*x for n, x in forward_h.items()}
    # Test directions Gamma0*H^dagger*Pi_L Xi live in the correct bar dual.
    wall_test = apply_spin(gamma0, forward_h)
    bar_test = apply_spin(gamma0, wall_test)
    hwall = reverse_unit_higgs(bar_test, h)
    left_hwall = apply_spin(pl, hwall)
    reverse = apply_spin(np.linalg.inv(gamma0), left_hwall)
    reverse = {n: -x for n, x in reverse.items()}
    forward_pair = np.zeros((12, 12), complex)
    reverse_pair = np.zeros_like(forward_pair)
    for n, x in e45.items():
        y = apply_spin(gamma0, {n: x})[n]
        forward_pair += mu4*wall_test[n].reshape(-1, 12).conj().T@y.reshape(-1, 12)
    # Same geometric volume pairing. The n5 reverse is evaluated and saved,
    # including its cancellation on this particular matched-image test.
    # That cancellation is not a general propagation/tail theorem.
    scalar = float(np.dot(weights*volume, radial['chi']*radial['p']))
    for n, x in basis.items():
        y = apply_spin(gamma0, {n: reverse[n]})[n]
        input_doublet = x.reshape(4, 16, n+1, n+1, -1)[:, 6:8]
        reverse_pair += scalar*input_doublet.reshape(-1, 12).conj().T@y.reshape(-1, 12)
    return dict(left=full_left, forward_h=forward_h, e45=e45,
                wall_test=wall_test, reverse=reverse,
                forward_pair=forward_pair, reverse_pair=reverse_pair,
                reverse_bar_pairing_residual=float(np.linalg.norm(
                    forward_pair.conj().T-reverse_pair)),
                unit_higgs_projected_source_norm=float(np.sqrt(sum(
                    np.linalg.norm(x)**2 for x in forward_h.values()))))
