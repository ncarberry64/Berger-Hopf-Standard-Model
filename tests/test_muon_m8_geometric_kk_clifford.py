"""Independent MP64 geometric controls, not physical BHSM backgrounds."""
from __future__ import annotations

import os
from pathlib import Path
import sys
import unittest

import mpmath as mp
import numpy as np

from bhsm.interface.muon_m8_geometric_kk_clifford import JET_ORDER, m8_geometric_kk_clifford_jets
from bhsm.interface.muon_m8_m5_geometric_coefficients import FIELD_NAMES, m8_m5_geometric_coefficient_jets


REPOSITORY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY/"src"))
from bhsm.interface.completion.foundational_dirac_spin_glue_v14_45 import dirac_gamma_matrices
from bhsm.interface.muon_local_source_jet import source_spin_frame


def owned_gamma5_base():
    # Same exact owner/formula as full_d5_localized_lepton_trace():30-33.
    gamma = source_spin_frame(np.array(dirac_gamma_matrices()))["gamma_LR"]
    chirality = 1j*gamma[0]@gamma[1]@gamma[2]@gamma[3]
    return np.array([gamma[0], 1j*chirality, gamma[1], gamma[2], gamma[3]])


def _mp_profile(t, chi, x, y):
    def dec(value): return mp.mpf(value)
    parameters = ((".12", ".03", ".07", ".02", "-.04", ".015"),
                  ("-.07", ".04", "-.03", ".01", ".02", "-.012"),
                  (".24", ".09", ".13", ".06", "-.05", ".023"),
                  ("-.19", "-.02", ".08", "-.03", ".04", "-.017"))
    values = []
    for index, row in enumerate(parameters):
        a, b, c, p, q, r = [dec(value) for value in row]
        logv = a+b*t+c*chi+dec(".013")*(index+1)*t*chi
        logv += x*(p+dec(".01")*t+dec(".007")*(index+1)*chi)
        logv += y*(q+dec(".009")*chi+1j*dec(".003")*(index+1)*t)
        logv += x*y*(r+dec(".005")*t*chi)
        values.append(mp.exp(logv))
    beta = dec(".16")+dec(".03")*t-dec(".04")*chi
    beta += x*(dec(".02")+dec(".01")*chi)+y*(dec("-.03")+dec(".006")*t)
    beta += x*y*(dec(".011")+dec(".004")*t*chi)
    return tuple(values)+(beta,)


def _mp_fields(x, y):
    t, chi = mp.mpf(".17"), mp.mpf(".29")
    values = _mp_profile(t, chi, x, y)
    def dlog(index, axis):
        return (mp.diff(lambda tt: mp.log(_mp_profile(tt, chi, x, y)[index]), t)
                if axis == 0 else mp.diff(lambda cc: mp.log(_mp_profile(t, cc, x, y)[index]), chi))
    return dict(zip(("N", "C", "A", "B", "beta"), values),
        np=dlog(0, 1), cp=dlog(1, 1), ap=dlog(2, 1), bp=dlog(3, 1),
        la=dlog(2, 0), lb=dlog(3, 0), lc=dlog(1, 0),
        betap=mp.diff(lambda cc: _mp_profile(t, cc, x, y)[4], chi))


def _mp_jets(fun):
    zero = mp.mpf(0)
    return dict(value=fun(zero, zero),
        x=mp.diff(lambda x: fun(x, zero), zero),
        y=mp.diff(lambda y: fun(zero, y), zero),
        xy=mp.diff(lambda x: mp.diff(lambda y: fun(x, y), zero), zero))


def _to_numpy(value):
    return np.array(value.tolist(), complex) if isinstance(value, mp.matrix) else complex(value)


def control_coefficients():
    with mp.workdps(64):
        fields = {name: {key: _to_numpy(value) for key, value in _mp_jets(
            lambda x, y, name=name: _mp_fields(x, y)[name]).items()} for name in FIELD_NAMES}
        f = _mp_fields(0, 0)
        L = mp.sqrt(f["A"]**2+f["B"]**2)
        return m8_m5_geometric_coefficient_jets(fields,
            fiber_radius_value=complex(L), fiber_log_value=complex(mp.log(L)))


def _mp_kron(a, b):
    return mp.matrix([[a[i//b.rows, j//b.cols]*b[i%b.rows, j%b.cols]
        for j in range(a.cols*b.cols)] for i in range(a.rows*b.rows)])


def _mp_cliffords(gamma5):
    sigma = (mp.matrix([[0, 1], [1, 0]]), mp.matrix([[0, -1j], [1j, 0]]), mp.matrix([[1, 0], [0, -1]]))
    gamma = [mp.matrix(a.tolist()) for a in gamma5]
    base = [_mp_kron(_mp_kron(a, mp.eye(2)), sigma[0]) for a in gamma]
    vertical = [_mp_kron(_mp_kron(mp.eye(4), 1j*a), sigma[1]) for a in sigma]
    return base, vertical


def _literal_mp_blocks(gamma5):
    # This literal expression differentiates full matrix products from
    # smooth t/chi/source functions. It does not call the tested jet rules.
    base, vertical = _mp_cliffords(gamma5)
    epsilon = {(0, 1, 2): 1, (1, 2, 0): 1, (2, 0, 1): 1,
               (0, 2, 1): -1, (2, 1, 0): -1, (1, 0, 2): -1}
    triples = {(i, mu, nu): base[mu]*base[nu]*vertical[i]
               for i in range(3) for mu in range(5) for nu in range(5) if mu != nu}
    vertical_spin = vertical[0]*vertical[1]*vertical[2]
    def evaluate(x, y):
        t, chi = mp.mpf(".17"), mp.mpf(".29")
        def geom(tt, cc):
            N, C, A, B, beta = _mp_profile(tt, cc, x, y)
            L = mp.sqrt(A*A+B*B)
            return N, C, A, B, beta, L, A*B/L, A*A/(L*L)
        N, C, A, B, beta, L, radius, lam = geom(t, chi)
        dlamt = mp.diff(lambda tt: geom(tt, chi)[7], t)
        dlamchi = mp.diff(lambda cc: geom(t, cc)[7], chi)
        F0 = (dlamt-beta*dlamchi)/(N*radius)
        Fc = dlamchi/(C*radius)
        Fab = -2*lam*(1-lam)/(radius*radius)
        F = {}
        for i in range(3):
            F[i, 0, i+2], F[i, i+2, 0] = F0, -F0
            F[i, 1, i+2], F[i, i+2, 1] = Fc, -Fc
        for (i, a, b), sign in epsilon.items(): F[i, a+2, b+2] = sign*Fab
        KK = mp.zeros(16)
        for index, coefficient in F.items(): KK += (-1j*L/8)*coefficient*triples[index]
        blocks = [KK, (1j/N)*base[0], (1j/C)*base[1]-(1j*beta/N)*base[0]]
        blocks.extend((1j/radius)*a for a in base[2:])
        blocks.extend((1j/L)*a for a in vertical)
        blocks.append((mp.mpf("1.5")*1j/L)*vertical_spin)
        return mp.matrix([a[i, j] for a in blocks for i in range(16) for j in range(16)])
    return evaluate


def run_independent_clifford_controls():
    gamma5 = owned_gamma5_base()
    coefficients = control_coefficients()
    out = m8_geometric_kk_clifford_jets(gamma5_base=gamma5, geometric_coefficients=coefficients)
    with mp.workdps(64):
        expected = _mp_jets(_literal_mp_blocks(gamma5))
    errors = {}
    for key in JET_ORDER:
        blocks = [out["KK"][key], out["time_coordinate_principal"][key], out["chi_coordinate_principal"][key]]
        blocks.extend(out["horizontal_angular_principal"][key])
        blocks.extend(out["vertical_unit_derivative_principal"][key])
        blocks.append(out["vertical_left_MC_spin_body"][key])
        actual = np.array(blocks)
        wanted = np.array(expected[key].tolist(), complex).reshape(actual.shape)
        errors[key] = float(np.max(np.abs(actual-wanted)))
    return dict(MP64_literal_block_errors=errors, clifford5_residual=out["clifford5_residual"],
        clifford8_residual=out["clifford8_residual"],
        ordered_sum_errors=out["full_vs_upper_ordered_KK_residual"],
        normalized_mean_errors={key: float(np.max(np.abs(out["mean_spin_density_cancellation"][key]))) for key in JET_ORDER},
        KK_xy_norm=float(np.linalg.norm(out["KK"]["xy"])),
        nonzero_shift_norm=float(np.linalg.norm(out["chi_coordinate_principal"]["value"]
            -1j*coefficients["original_seven_spatial_coframe_inverse_scales"]["value"][0]*out["gamma8_base"][1])),
        vertical_spin_norm=float(np.linalg.norm(out["vertical_left_MC_spin_body"]["value"])),
        native_graded_or_SM_carrier_selected=out["native_graded_or_SM_carrier_selected"],
        full_physical_outgoing_derivative_pass=out["full_physical_outgoing_derivative_pass"])


class M8GeometricCliffordTests(unittest.TestCase):
    def test_owned_gamma_and_full_clifford_algebra(self):
        out = m8_geometric_kk_clifford_jets(gamma5_base=owned_gamma5_base(), geometric_coefficients=control_coefficients())
        G = out["gamma8_all"]
        eta = [1]+[-1]*7
        for a in range(8):
            for b in range(8):
                target = 2*eta[a]*np.eye(16) if a == b else 0
                # The owned LR frame carries binary64 sqrt(2) rounding;
                # its normal gamma is the four-factor chirality product.
                np.testing.assert_allclose(G[a]@G[b]+G[b]@G[a], target, atol=5e-15, rtol=0)
        self.assertEqual(np.linalg.matrix_rank(G[0]), 16)
        self.assertTrue(out["all_seven_spatial_principal_directions_retained"])
        self.assertFalse(out["vertical_DF_or_spin_set_to_zero"])
        self.assertFalse(out["native_graded_or_SM_carrier_selected"])

    def test_independent_MP64_literal_products_and_all_contacts(self):
        result = run_independent_clifford_controls()
        self.assertLess(max(result["MP64_literal_block_errors"].values()), 3e-14)
        self.assertLess(max(result["ordered_sum_errors"].values()), 3e-15)
        self.assertLess(max(result["normalized_mean_errors"].values()), 3e-15)
        self.assertGreater(result["KK_xy_norm"], .001)
        self.assertGreater(result["nonzero_shift_norm"], .01)
        self.assertGreater(result["vertical_spin_norm"], 1)
        self.assertFalse(result["full_physical_outgoing_derivative_pass"])

    def test_fixed_spin_basis_covariance_without_source_conjugation(self):
        gamma5 = owned_gamma5_base()
        c = control_coefficients()
        original = m8_geometric_kk_clifford_jets(gamma5_base=gamma5, geometric_coefficients=c)
        # Fixed nonunitary basis change is allowed for this Clifford-only
        # construction; no Hilbert/current pairing is being selected.
        S = np.eye(4, dtype=complex)
        S[0, 1], S[1, 3], S[2, 0] = .07+.03j, -.04j, .02
        Si = np.linalg.inv(S)
        moved = m8_geometric_kk_clifford_jets(gamma5_base=np.array([S@g@Si for g in gamma5]), geometric_coefficients=c)
        bigS, bigSi = np.kron(S, np.eye(4)), np.kron(Si, np.eye(4))
        for key in JET_ORDER:
            np.testing.assert_allclose(moved["KK"][key], bigS@original["KK"][key]@bigSi, atol=3e-15, rtol=3e-14)
        self.assertFalse(moved["source_coefficients_conjugated"])

    def test_explicit_frame_contacts_and_algebra_guards(self):
        c = control_coefficients()
        gamma = owned_gamma5_base()
        bad = dict(c, base_frame_order=("0", "1", "2", "3", "chi"))
        with self.assertRaisesRegex(ValueError, "frame"):
            m8_geometric_kk_clifford_jets(gamma5_base=gamma, geometric_coefficients=bad)
        broken = gamma.copy(); broken[2] *= 1.1
        with self.assertRaisesRegex(ValueError, "Clifford"):
            m8_geometric_kk_clifford_jets(gamma5_base=broken, geometric_coefficients=c)
        bad = dict(c, F_full=dict(c["F_full"]))
        bad["F_full"]["xy"] = bad["F_full"]["xy"].copy()
        bad["F_full"]["xy"][0, 0, 0] = .01
        with self.assertRaisesRegex(ValueError, "antisymmetric"):
            m8_geometric_kk_clifford_jets(gamma5_base=gamma, geometric_coefficients=bad)
        bad = dict(c, LF=dict(c["LF"]))
        del bad["LF"]["xy"]
        with self.assertRaisesRegex(ValueError, "explicit"):
            m8_geometric_kk_clifford_jets(gamma5_base=gamma, geometric_coefficients=bad)


if __name__ == "__main__": unittest.main()
