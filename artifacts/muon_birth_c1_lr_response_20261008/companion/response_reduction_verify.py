#!/usr/bin/env python3
"""Exact finite controls for consumed same-domain response reductions.

Run with Python's standard library only. All arithmetic is Fraction arithmetic,
including first and mixed derivatives. The four-dimensional nonsymmetric test
matrices are CONTROL_ONLY supplied data, not physical BHSM operators. No Higgs
profile, incoming LR embedding, covariance, or physical family member is supplied.

Six controls compare independent constructions:
  * direct response subtraction against a left/right extension pairing;
  * direct elimination against the carrier-coordinate Schur correction;
  * forward-mode exact differentiation against the stationary pairing, including
    moving left/right domain pullbacks and a nonzero omitted-pullback witness;
  * direct forced block solve against reduced forcing and its derivative;
  * direct mixed differentiation of a reduced scalar action against the mixed
    Hessian Schur term, with a nonzero false-cancellation witness;
  * direct differentiation of an inverse-seam readout against its lifted adjoint.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
import json


@dataclass(frozen=True)
class Jet:
    """v + x*dx + c*dc + x*c*dxc, with x*x=c*c=0 (no factorials)."""

    v: F
    dx: F = F(0)
    dc: F = F(0)
    dxc: F = F(0)

    @staticmethod
    def coerce(other):
        return other if isinstance(other, Jet) else Jet(F(other))

    def __add__(self, other):
        b = self.coerce(other)
        return Jet(self.v+b.v, self.dx+b.dx, self.dc+b.dc, self.dxc+b.dxc)

    __radd__ = __add__

    def __neg__(self):
        return Jet(-self.v, -self.dx, -self.dc, -self.dxc)

    def __sub__(self, other):
        return self + (-self.coerce(other))

    def __rsub__(self, other):
        return self.coerce(other) + (-self)

    def __mul__(self, other):
        b = self.coerce(other)
        return Jet(
            self.v*b.v,
            self.dx*b.v+self.v*b.dx,
            self.dc*b.v+self.v*b.dc,
            self.dxc*b.v+self.dx*b.dc+self.dc*b.dx+self.v*b.dxc,
        )

    __rmul__ = __mul__

    def reciprocal(self):
        if self.v == 0:
            raise ZeroDivisionError("Jet inverse has zero constant term")
        return Jet(
            1/self.v,
            -self.dx/self.v**2,
            -self.dc/self.v**2,
            2*self.dx*self.dc/self.v**3-self.dxc/self.v**2,
        )

    def __truediv__(self, other):
        return self * self.coerce(other).reciprocal()

    def __rtruediv__(self, other):
        return self.coerce(other) * self.reciprocal()


def matrix(rows):
    return [[x if isinstance(x, Jet) else F(x) for x in row] for row in rows]


def shape(a):
    if not a or not a[0] or any(len(row) != len(a[0]) for row in a):
        raise ValueError("Nonempty rectangular matrix required")
    return len(a), len(a[0])


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def zeros(n, m):
    return [[F(0) for _ in range(m)] for _ in range(n)]


def tr(a):
    return [list(row) for row in zip(*a)]


def add(a, b):
    if shape(a) != shape(b):
        raise ValueError("Addition shape mismatch")
    return [[x+y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def neg(a):
    return [[-x for x in row] for row in a]


def sub(a, b):
    return add(a, neg(b))


def mul(a, b):
    if shape(a)[1] != shape(b)[0]:
        raise ValueError("Multiplication shape mismatch")
    return [[sum((x*y for x, y in zip(row, col)), F(0)) for col in tr(b)] for row in a]


def base_scalar(x):
    return x.v if isinstance(x, Jet) else x


def inv(a):
    n, m = shape(a)
    if n != m:
        raise ValueError("Square inverse required")
    work = [list(row)+ident for row, ident in zip(a, eye(n))]
    for col in range(n):
        pivot = next((row for row in range(col, n) if base_scalar(work[row][col]) != 0), None)
        if pivot is None:
            raise ValueError("Singular supplied matrix")
        work[col], work[pivot] = work[pivot], work[col]
        scale = work[col][col]
        work[col] = [x/scale for x in work[col]]
        for row in range(n):
            if row == col:
                continue
            scale = work[row][col]
            work[row] = [x-scale*y for x, y in zip(work[row], work[col])]
    return [row[n:] for row in work]


def hcat(a, b):
    if len(a) != len(b):
        raise ValueError("Horizontal concatenation mismatch")
    return [ar+br for ar, br in zip(a, b)]


def vcat(a, b):
    if shape(a)[1] != shape(b)[1]:
        raise ValueError("Vertical concatenation mismatch")
    return [list(row) for row in a+b]


def blocks(l, n):
    return (
        [row[:n] for row in l[:n]],
        [row[n:] for row in l[:n]],
        [row[:n] for row in l[n:]],
        [row[n:] for row in l[n:]],
    )


def schur(l, n):
    d, c, b, a = blocks(l, n)
    return sub(d, mul(mul(c, inv(a)), b))


def extensions(l, n):
    _d, c, b, a = blocks(l, n)
    ai = inv(a)
    er = vcat(eye(n), neg(mul(ai, b)))
    elt = hcat(eye(n), neg(mul(c, ai)))
    return tr(elt), er


def components(a, component="v"):
    return [[getattr(x, component) if isinstance(x, Jet) else (x if component == "v" else F(0))
             for x in row] for row in a]


def jet_matrix(a, dot):
    return [[Jet(x, dx=y) for x, y in zip(ar, dr)] for ar, dr in zip(a, dot)]


def max_abs(a):
    return max(abs(x) for row in a for x in row)


def equal(actual, expected, name):
    residual = sub(actual, expected)
    if max_abs(residual) != 0:
        raise AssertionError(name+": "+str(residual))
    return "0"


def pairing(a, b):
    if shape(a) != shape(b):
        raise ValueError("Pairing shape mismatch")
    return sum((x*y for ar, br in zip(a, b) for x, y in zip(ar, br)), F(0))


def require_nonzero(a, name):
    value = max_abs(a)
    if value == 0:
        raise AssertionError(name+" did not expose its intended missing contribution")
    return str(value)


def main():
    n = 2
    lc = matrix([[5, 1, -1, 1], [-2, 4, 2, 0], [1, 2, 4, 1], [0, 1, -1, 3]])
    v = matrix([["1/3", "-1/4", "1/2", 0], ["2/5", "1/6", "-1/3", "1/5"],
                [0, "1/7", "1/4", "-1/6"], ["1/5", 0, "1/8", "1/3"]])
    lf = add(lc, v)
    if max_abs(sub(mul(lc, v), mul(v, lc))) == 0:
        raise AssertionError("The supplied full matrices unexpectedly commute")
    if max_abs(sub(lc, tr(lc))) == 0 or max_abs(sub(lf, tr(lf))) == 0:
        raise AssertionError("Nonsymmetric controls required")
    lce, rce = extensions(lc, n)
    lfe, rfe = extensions(lf, n)
    direct_r = sub(schur(lf, n), schur(lc, n))
    reports = []

    reports.append({
        "control": "same_domain_response_difference",
        "exact_max_residual": equal(direct_r, mul(mul(tr(lce), v), rfe), "response difference"),
        "construction": "direct Schur difference versus left-carrier/right-full pairing",
    })

    j = vcat(zeros(n, len(lc)-n), eye(len(lc)-n))
    w = mul(mul(tr(lce), v), rce)
    vbi = mul(mul(tr(lce), v), j)
    vib = mul(mul(tr(j), v), rce)
    vii = mul(mul(tr(j), v), j)
    ac = blocks(lc, n)[3]
    reduced_r = sub(w, mul(mul(vbi, inv(add(ac, vii))), vib))
    reports.append({
        "control": "carrier_coordinate_correction",
        "exact_max_residual": equal(direct_r, reduced_r, "carrier-coordinate correction"),
        "first_pairing_omitted_interior_correction_max": require_nonzero(sub(direct_r, w), "interior correction"),
    })

    # Moving maps preserve the boundary coordinate and move its interior lift.
    tl = matrix([[1, 0, 0, 0], [0, 1, 0, 0], ["1/5", 0, 1, "1/7"], [0, "-1/6", 0, 1]])
    rt = matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, "1/8", 1, 0], ["1/9", 0, "-1/5", 1]])
    tld = matrix([[0, 0, 0, 0], [0, 0, 0, 0], ["1/3", "1/4", 0, "1/6"], [0, "-1/7", "1/8", 0]])
    rtd = matrix([[0, 0, 0, 0], [0, 0, 0, 0], ["-1/4", 0, "1/6", 0], ["1/3", "1/5", 0, "-1/8"]])
    # Pullbacks preserving boundary coordinates make the response invariant to
    # pure interior reparameterization; to test moving trace normalization too,
    # vary the boundary blocks rather than counting that invariance as evidence.
    tld[0][0], tld[0][1], tld[1][0] = F(1, 6), F(-1, 8), F(1, 9)
    rtd[0][1], rtd[1][0], rtd[1][1] = F(1, 7), F(-1, 5), F(1, 10)
    native_dot = matrix([[0, "1/3", "-1/4", 0], ["1/5", 0, 0, "1/7"],
                         ["1/8", 0, "1/2", "-1/6"], [0, "1/9", "1/10", "-1/3"]])
    pulled_jet = mul(mul(tr(jet_matrix(tl, tld)), jet_matrix(lf, native_dot)), jet_matrix(rt, rtd))
    pulled, pulled_dot = components(pulled_jet), components(pulled_jet, "dx")
    ep_l, ep_r = extensions(pulled, n)
    direct_schur_dot = components(schur(pulled_jet, n), "dx")
    paired_dot = mul(mul(tr(ep_l), pulled_dot), ep_r)
    frozen_dot = mul(mul(tr(tl), native_dot), rt)
    frozen_paired = mul(mul(tr(ep_l), frozen_dot), ep_r)
    reports.append({
        "control": "moving_domain_response_derivative",
        "exact_max_residual": equal(direct_schur_dot, paired_dot, "moving-domain derivative"),
        "omitted_moving_pullback_max_error": require_nonzero(sub(direct_schur_dot, frozen_paired), "moving pullback"),
        "construction": "Jet Gaussian elimination versus stationary extension pairing",
    })

    native_force = matrix([[1], ["2/3"], ["-1/4"], ["3/5"]])
    native_force_dot = matrix([["1/3"], ["-1/5"], ["2/7"], ["1/9"]])
    force_jet = mul(tr(jet_matrix(tl, tld)), jet_matrix(native_force, native_force_dot))
    force, force_dot = components(force_jet), components(force_jet, "dx")
    _d, c, _b, a = blocks(pulled, n)
    _dd, cd, _bd, ad = blocks(pulled_dot, n)
    fb, fi = force[:n], force[n:]
    fbd, fid = force_dot[:n], force_dot[n:]
    ai = inv(a)
    ri = mul(ai, fi)
    effective_force = sub(fb, mul(c, ri))
    effective_force_dot = sub(sub(fbd, mul(cd, ri)), mul(mul(c, ai), sub(fid, mul(ad, ri))))
    direct_solution = mul(inv(pulled_jet), force_jet)
    reduced_force_jet = jet_matrix(effective_force, effective_force_dot)
    reduced_solution = mul(inv(schur(pulled_jet, n)), reduced_force_jet)
    reports.append({
        "control": "forced_affine_elimination",
        "value_exact_max_residual": equal(components(direct_solution[:n]), components(reduced_solution), "forced boundary value"),
        "derivative_exact_max_residual": equal(components(direct_solution[:n], "dx"), components(reduced_solution, "dx"), "forced boundary derivative"),
    })

    # A(x,c,h)=(4+x)h^2/2-(1+2x+3c+5xc)h+7xc.
    # Its scalar stationary branch is h=j/a. No physical branch is represented.
    x, cv = Jet(F(0), dx=F(1)), Jet(F(0), dc=F(1))
    aa, jj = 4+x, 1+2*x+3*cv+5*x*cv
    hstar = jj/aa
    reduced_action = 7*x*cv-jj*jj/(2*aa)
    fixed_partial_x = hstar*hstar/2-(2+5*cv)*hstar+7*cv
    direct_mixed = F(23, 4)  # A_xc at fixed h=1/4, calculated from A itself.
    axh, ahc, hh = F(-7, 4), F(-3), F(4)
    mixed_schur = direct_mixed-axh*ahc/hh
    if reduced_action.dx != fixed_partial_x.v:
        raise AssertionError("Scalar first-variation envelope identity failed")
    if reduced_action.dxc != mixed_schur or fixed_partial_x.dc != mixed_schur:
        raise AssertionError("Scalar mixed Schur identity failed")
    if reduced_action.dxc == direct_mixed:
        raise AssertionError("False scalar cancellation was not detected")
    reports.append({
        "control": "scalar_envelope_mixed_counterexample",
        "first_variation_exact_residual": "0",
        "mixed_variation_exact_residual": "0",
        "reduced_first_derivative": str(reduced_action.dx),
        "reduced_mixed_derivative": str(reduced_action.dxc),
        "fixed_scalar_partial_mixed_derivative": str(direct_mixed),
        "omitted_scalar_response_error": str(direct_mixed-reduced_action.dxc),
    })

    load = matrix([[3, "1/3"], ["1/3", 2]])
    load_dot = matrix([["1/4", 0], [0, "-1/6"]])
    g = matrix([["2/3", "-1/5"], ["1/7", "3/4"]])
    seam_jet = add(schur(pulled_jet, n), jet_matrix(load, load_dot))
    seam, seam_inv = components(seam_jet), inv(components(seam_jet))
    observed = pairing(g, inv(seam_jet))
    ws = neg(mul(mul(tr(seam_inv), g), tr(seam_inv)))
    lifted = mul(mul(ep_l, ws), tr(ep_r))
    contracted = pairing(lifted, pulled_dot)+pairing(ws, load_dot)
    if observed.dx != contracted:
        raise AssertionError("Nested inverse-seam cotangent failed")
    reports.append({
        "control": "nested_inverse_seam_cotangent",
        "exact_residual": "0",
        "construction": "Jet full inverse readout versus lifted adjoint plus returned-load contact",
    })

    print(json.dumps({
        "scope": "CONTROL_ONLY_EXACT_FINITE_SUPPLIED_MATRICES",
        "arithmetic": "stdlib Fraction, exact first/mixed square-free jets",
        "physical_incoming_L_or_V_supplied": False,
        "common_first_order_LR_embedding_established": False,
        "physical_CAR_verdict": None,
        "controls_passed": len(reports),
        "controls": reports,
    }, indent=2))


if __name__ == "__main__":
    main()
