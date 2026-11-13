"""Exact local LR/CAR reduction controls; no physical incoming value is supplied.

Uses only Gaussian rational arithmetic. The coefficientwise identities are
verified on complete linear/quadratic bases, so these checks are symbolic
identities for the stated two-quadrature local subspace, not random samples.
The source-defined Dirac gamma convention is (+---). The physical complete
E1 kernel, incoming Higgs, domain/response pullback, covariance and rank stay
unevaluated. Run: python car_reduction_verify.py
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json


@dataclass(frozen=True)
class QComplex:
    re: F = F(0)
    im: F = F(0)

    @staticmethod
    def of(value):
        return value if isinstance(value, QComplex) else QComplex(F(value), F(0))

    def __add__(self, other):
        other = QComplex.of(other)
        return QComplex(self.re + other.re, self.im + other.im)

    __radd__ = __add__

    def __neg__(self):
        return QComplex(-self.re, -self.im)

    def __sub__(self, other):
        return self + -QComplex.of(other)

    def __rsub__(self, other):
        return QComplex.of(other) + -self

    def __mul__(self, other):
        other = QComplex.of(other)
        return QComplex(self.re * other.re - self.im * other.im,
                        self.re * other.im + self.im * other.re)

    __rmul__ = __mul__

    def conjugate(self):
        return QComplex(self.re, -self.im)


ZERO = QComplex()
ONE = QComplex.of(1)
II = QComplex(F(0), F(1))


def mat(rows):
    return [[QComplex.of(x) for x in row] for row in rows]


def zeros(n):
    return [[ZERO for _ in range(n)] for _ in range(n)]


def eye(n):
    return mat([[int(i == j) for j in range(n)] for i in range(n)])


def add(a, b):
    return [[x+y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def scale(z, a):
    return [[z*x for x in ar] for ar in a]


def mul(a, b):
    return [[sum((a[i][k]*b[k][j] for k in range(len(b))), ZERO)
             for j in range(len(b[0]))] for i in range(len(a))]


def conjugate(a):
    return [[x.conjugate() for x in ar] for ar in a]


def adjoint(a):
    return [list(ar) for ar in zip(*conjugate(a))]


def trace(a):
    return sum((a[i][i] for i in range(len(a))), ZERO)


def blocks(a, b, c, d):
    return [ar+br for ar, br in zip(a, b)] + [cr+dr for cr, dr in zip(c, d)]


def direct(a, b):
    assert len(a) == len(b)
    z = zeros(len(a))
    return blocks(a, z, z, b)


def hermitian_basis(n):
    out = []
    for i in range(n):
        a = zeros(n)
        a[i][i] = ONE
        out.append(a)
    for i in range(n):
        for j in range(i+1, n):
            a = zeros(n)
            a[i][j] = a[j][i] = ONE
            out.append(a)
            a = zeros(n)
            a[i][j], a[j][i] = II, -II
            out.append(a)
    return out


def run():
    checks = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    i2, z2 = eye(2), zeros(2)
    sigmas = (mat([[0, 1], [1, 0]]),
              mat([[0, -II], [II, 0]]),
              mat([[1, 0], [0, -1]]))
    beta = direct(i2, scale(-1, i2))
    gamma = [beta] + [blocks(z2, s, scale(-1, s), z2) for s in sigmas]
    gamma5 = scale(II, mul(mul(mul(gamma[0], gamma[1]), gamma[2]), gamma[3]))
    check("source_gamma5_is_offdiagonal_in_Dirac_basis", gamma5 == blocks(z2, i2, i2, z2))
    check("source_gamma0_is_not_chirality_grading", mul(beta, gamma5) == scale(-1, mul(gamma5, beta)))
    br, bi = beta, scale(II, mul(beta, gamma5))
    check("both_owned_scalar_quadratures_are_Hermitian", adjoint(br) == br and adjoint(bi) == bi)
    check("real_quadrature_square_is_identity", mul(br, br) == eye(4))
    check("imaginary_quadrature_square_is_identity", mul(bi, bi) == eye(4))
    check("quadrature_anticommutator_is_zero", add(mul(br, bi), mul(bi, br)) == zeros(4))
    check("quadrature_Hilbert_Schmidt_Gram_is_4I", trace(mul(br, br)) == QComplex.of(4)
          and trace(mul(bi, bi)) == QComplex.of(4) and trace(mul(br, bi)) == ZERO)

    # V/sqrt(2) changes Dirac to chiral coordinates. Exact sandwiches use V/2.
    v = blocks(i2, i2, scale(-1, i2), i2)
    transport = lambda a: scale(F(1, 2), mul(mul(adjoint(v), a), v))
    check("normalized_chiral_basis_is_unitary", mul(adjoint(v), v) == scale(2, eye(4)))
    check("chiral_gamma5_has_left_right_eigenvalues", transport(gamma5) == direct(scale(-1, i2), i2))
    check("real_mass_bilinear_is_LR_offdiagonal", transport(br) == blocks(z2, i2, i2, z2))
    check("imaginary_mass_bilinear_has_conjugate_LR_entries", transport(bi) == blocks(z2, scale(II, i2), scale(-II, i2), z2))

    # Physical electromagnetic charge is the same on L and R, by source owner.
    ql = scale(-1, eye(4))
    check("LR_scalar_quadratures_preserve_physical_charge", all(mul(ql, b) == mul(b, ql) for b in (br, bi)))
    # Misusing Dirac gamma0 as the grading of a schematic LR matrix gives an
    # anti-Hermitian product. This is a basis/tensor-factor error, not a zero LR action.
    wrong = mul(beta, gamma5)
    check("schematic_LR_gamma0_multiplication_would_spuriously_erase_action",
          add(wrong, adjoint(wrong)) == zeros(4) and br != zeros(4))

    g = blocks(zeros(4), eye(4), eye(4), zeros(4))
    charge = direct(eye(4), scale(-1, eye(4)))
    tangents = [direct(a, scale(-1, conjugate(a))) for a in hermitian_basis(4)]
    check("complete_local_muon_affine_tangent_has_16_basis_elements", len(tangents) == 16)
    check("all_basis_tangents_obey_CAR_and_charge", all(
        adjoint(x) == x and mul(mul(g, conjugate(x)), adjoint(g)) == scale(-1, x)
        and mul(charge, x) == mul(x, charge) for x in tangents))
    for label, b in (("real", br), ("imaginary", bi)):
        delta = direct(b, zeros(4))
        projected = scale(F(1, 2), add(delta, scale(-1, mul(mul(g, conjugate(delta)), adjoint(g)))))
        expected = direct(scale(F(1, 2), b), scale(F(-1, 2), conjugate(b)))
        check(label+"_ordered_particle_lift_projects_to_nonzero_CAR_odd_kernel", projected == expected and projected != zeros(8))
        check(label+"_CAR_projection_preserves_all_16_tangent_pairings", all(
            trace(mul(x, delta)).re == trace(mul(x, projected)).re for x in tangents))
        x = direct(b, scale(-1, conjugate(b)))
        check(label+"_quadrature_detects_itself", trace(mul(x, delta)) == QComplex.of(4))
        even = direct(b, conjugate(b))
        check(label+"_incorrect_same_sign_Nambu_lift_would_annihilate", all(
            trace(mul(x, even)).re == 0 for x in tangents))

    # Leibniz coefficient checks for t = b*m + delta(m). The finite local map
    # is real linear in (Re(t),Im(t)); the Gram above proves its injectivity.
    local = lambda z: add(scale(z.re, br), scale(z.im, bi))
    for z in (ONE, II):
        for dz in (ONE, II):
            for measure_jet in (F(0), F(1)):
                check("local_Leibniz_"+str(len(checks)),
                      local(measure_jet*z+dz) == add(scale(measure_jet, local(z)), local(dz)))

    # General first-variation cancellation criterion: derivatives of moving
    # pullbacks cannot be inferred from a zero base mismatch. Counterexample
    # uses F(t)=t*beta, F(0)=0 but F'(0)=beta, entirely exact.
    check("base_matched_form_does_not_prove_directional_matching", zeros(4) != br)

    return {
        "schema": "BHSM_INCOMING_LR_LOCAL_CAR_REDUCTION_EXACT_CONTROLS_V1",
        "source_commit": "ad750077f1a3138418a2dc4ee65f7c50236b5608",
        "arithmetic": "EXACT_GAUSSIAN_RATIONAL; COMPLETE_LINEAR_AND_QUADRATIC_COEFFICIENT_BASES",
        "scope": "POINTWISE_FIXED_ORTHONORMAL_FRAME_INTRINSIC_CHARGED_MUON_LR_BILINEAR_ONLY",
        "new_algebra": {
            "combined_complex_coefficient": "t_alpha=b_alpha*m_mu+delta_alpha(m_mu)",
            "Dirac_basis_bilinear": "B(t)=Re(t)*beta+Im(t)*i*beta*gamma5",
            "chiral_basis_bilinear": "B(t)=[[0,t*I2],[conjugate(t)*I2,0]]",
            "squared_identity": "B(t)^2=abs(t)^2*I4",
            "pointwise_operator_norm": "norm(B(t))=abs(t)",
            "local_row_real_span": "rank_R rows(Re(t_alpha),Im(t_alpha)) <= 2 at fixed point/frame",
            "charged_CAR_projection": "diag(B(t)/2,-conjugate(B(t))/2) for the ordinary ordered covariance derivative lift",
            "local_annihilator_criterion": "zero iff t_alpha=0 in the stated local subspace",
            "fixed_phase_rank_one_condition": "Only if all supplied t_alpha are real multiples of one common nonzero complex phase",
            "domain_response_rank_bound_inferred": False,
        },
        "checks_passed": len(checks),
        "checks": checks,
        "physical_incoming_Higgs_or_jet_evaluated": False,
        "physical_complete_E1_kernel_evaluated": False,
        "physical_complete_CAR_verdict": None,
        "physical_minimal_moment_rank": None,
        "physical_muon_anomaly": None,
        "physical_member_or_covariance_selected": False,
        "continuum_smoothing_tail_or_uniform_lambda_enclosure": False,
    }


if __name__ == "__main__":
    payload = run()
    # No timestamps or external state enter deterministic controls.
    text = json.dumps(payload, indent=2, sort_keys=True)+"\n"
    if len(__import__('sys').argv) == 2:
        Path(__import__('sys').argv[1]).write_text(text, encoding="utf-8")
    else:
        print(text, end="")
