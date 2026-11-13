"""Independent MP64 literal two-source checks; off-shell algebraic controls."""
from __future__ import annotations

import unittest

import mpmath as mp
import numpy as np

from bhsm.interface.muon_normalized_seam_schur_jets import (
    KEYS, normalized_seam_schur_jets,
)


def control_inputs():
    """Noncommuting, moving, independently analytic left/right maps.

    These deterministic coefficient arrays are control data, not a BHSM
    physical field, domain or assigned coupling.
    """
    rng = np.random.default_rng(140451569)
    nf, nt = 5, 2
    def matrix(shape, scale):
        return scale * (rng.normal(size=shape) + 1j * rng.normal(size=shape))
    K = {key: matrix((nf, nf), .09) for key in KEYS}
    K["value"] += np.diag([2.1, 2.6, 3.2, 3.7, 4.3])
    B = {key: matrix((nt, nf), .07) for key in KEYS}
    B["value"] += np.c_[np.eye(nt), np.zeros((nt, nf-nt))]
    C = {key: matrix((nf, nt), .08) for key in KEYS}
    C["value"] += np.r_[np.eye(nt), np.zeros((nf-nt, nt))]
    rho = dict(value=np.array(.73+.11j), x=np.array(.08-.04j),
               y=np.array(-.05+.03j), xy=np.array(.019+.021j))
    M = {key: matrix((nt, nt), .15) for key in KEYS}
    M["value"] += np.array([[.3+.1j, .42-.13j], [-.21+.17j, -.4+.2j]])
    return K, B, C, rho, M


def _mp_array(a):
    a = np.asarray(a)
    def number(v):
        return mp.mpc(mp.mpf(float(np.real(v))), mp.mpf(float(np.imag(v))))
    if a.ndim == 0:
        return number(a)
    return mp.matrix([[number(v) for v in row] for row in a])


def literal_full_seam_solution(inputs):
    """Direct full-seam inverse, not the implemented bare-border identity."""
    coeff = [{key: _mp_array(jet[key]) for key in KEYS} for jet in inputs]
    nf, nt = inputs[0]["value"].shape[0], inputs[1]["value"].shape[0]
    def evaluate(jet, x, y):
        return jet["value"] + x*jet["x"] + y*jet["y"] + x*y*jet["xy"]
    def solve(x, y):
        K, B, C, rho, M = [evaluate(jet, x, y) for jet in coeff]
        action = K - rho*C*M*B
        q = mp.zeros(nf+nt)
        for i in range(nf):
            for j in range(nf):
                q[i,j] = action[i,j]
            for j in range(nt):
                q[i,nf+j] = C[i,j]
        for i in range(nt):
            for j in range(nf):
                q[nf+i,j] = B[i,j]
        rhs = mp.zeros(nf+nt, nt)
        for i in range(nt):
            rhs[nf+i,i] = 1
        return q**-1 * rhs
    return solve


def mp_literal_jets(solve, rows, columns):
    out = {key: np.empty((rows, columns), complex) for key in KEYS}
    zero = mp.mpf(0)
    v = solve(zero, zero)
    for i in range(rows):
        for j in range(columns):
            out["value"][i,j] = complex(v[i,j])
            out["x"][i,j] = complex(mp.diff(lambda x: solve(x, zero)[i,j], zero))
            out["y"][i,j] = complex(mp.diff(lambda y: solve(zero, y)[i,j], zero))
            out["xy"][i,j] = complex(mp.diff(
                lambda x: mp.diff(lambda y: solve(x,y)[i,j], zero), zero))
    return out


def run_independent_controls():
    inputs = control_inputs()
    result = normalized_seam_schur_jets(*inputs)
    with mp.workdps(64):
        expected = mp_literal_jets(literal_full_seam_solution(inputs), 7, 2)
    errors = {key: float(np.max(abs(result["full_seam_border_solution_jet"][key]
                                     - expected[key]))) for key in KEYS}
    rows = {key: float(np.max(abs(result["original_full_seam_border_rows"][key])))
            for key in KEYS}
    bare_rows = {key: float(np.max(abs(result["original_bare_border_rows"][key])))
                 for key in KEYS}
    # These are directly visible safeguards against accidentally implementing
    # a scalar commuting fixture or identifying C with a transposed B.
    K, B, C, rho, M = inputs
    return dict(independent_literal_full_seam_MP64_solution_max_errors=errors,
        original_full_seam_border_rows=rows, original_bare_border_rows=bare_rows,
        independent_left_trace_transpose_difference=float(np.linalg.norm(C["value"]-B["value"].T)),
        noncommuting_mass_contact_norm=float(np.linalg.norm(M["value"]@M["x"]-M["x"]@M["value"])),
        moving_trace_first_norm=float(np.linalg.norm(B["x"])+np.linalg.norm(C["y"])),
        full_field_count=result["full_field_count"], trace_count=result["normalized_trace_count"],
        complement_count=result["complementary_field_count"],
        physical_control_state=False, source_conjugation_used=False)


class NormalizedSeamTests(unittest.TestCase):
    def test_independent_literal_full_seam_MP64(self):
        r = run_independent_controls()
        self.assertLess(max(r["independent_literal_full_seam_MP64_solution_max_errors"].values()), 2e-13)
        self.assertLess(max(r["original_full_seam_border_rows"].values()), 2e-13)
        self.assertLess(max(r["original_bare_border_rows"].values()), 2e-13)
        self.assertGreater(r["independent_left_trace_transpose_difference"], .1)
        self.assertGreater(r["noncommuting_mass_contact_norm"], .01)
        self.assertGreater(r["moving_trace_first_norm"], .1)

    def test_once_only_seam_identity_and_poisson_invariance(self):
        K,B,C,rho,M = control_inputs()
        r = normalized_seam_schur_jets(K,B,C,rho,M)
        for key in KEYS:
            np.testing.assert_array_equal(r["algebraic_Poisson_invariance_rows"][key], 0)
            np.testing.assert_allclose(r["Gamma_full"][key],
                r["Gamma_bulk"][key]-r["rho_M"][key], atol=1e-15, rtol=1e-15)
        self.assertEqual(r["complementary_field_count"], 3)
        self.assertEqual(r["bare_border_factorizations"], 1)
        self.assertEqual(r["full_seam_border_factorizations"], 0)
        # The original full border, rather than a second seam inserted into
        # Gamma_full, is the governing equation.
        bad = r["full_seam_border_solution_jet"]["value"].copy()
        bad[5:] += r["rho_M"]["value"]
        extra_rows = r["full_seam_border_jet"]["value"]@bad
        extra_rows[5:] -= np.eye(2)
        self.assertGreater(np.max(abs(extra_rows)), .1)

    def test_E_H_partial_contact_keeps_inverse_mixed_response(self):
        K,B,C,rho,M = control_inputs()
        # E changes only K, the neutral-H source only M.  Both independent
        # trace maps/density are held as the explicitly declared partial.
        for jet in (K,B,C,rho,M):
            for key in ("x","y","xy"):
                if (jet is K and key == "x") or (jet is M and key == "y"):
                    continue
                jet[key] = np.zeros_like(jet[key])
        r = normalized_seam_schur_jets(K,B,C,rho,M)
        self.assertLess(np.max(abs(r["Gamma_full"]["xy"])), 1e-14)
        g = r["Gamma_full"]; inv = np.linalg.solve(g["value"], np.eye(2))
        mixed = inv@g["x"]@inv@g["y"]@inv + inv@g["y"]@inv@g["x"]@inv
        self.assertGreater(np.linalg.norm(mixed), .001)
        np.testing.assert_array_equal(r["full_field_Poisson"]["y"], 0)

    def test_explicit_contacts_and_unsolved_border_guard(self):
        data = list(control_inputs())
        data[1] = {k:v for k,v in data[1].items() if k != "xy"}
        with self.assertRaisesRegex(ValueError, "explicit value/x/y/xy"):
            normalized_seam_schur_jets(*data)
        K,B,C,rho,M = control_inputs()
        for key in KEYS:
            B[key] = np.zeros_like(B[key])
        with self.assertRaises((np.linalg.LinAlgError, Warning)):
            normalized_seam_schur_jets(K,B,C,rho,M)


if __name__ == "__main__":
    unittest.main()
