"""Exact rational checks independent of numerical optical propagation.

Only Python's standard library is used. These checks verify algebraic pieces
of the derivation; they are not physical or observational validation.
"""
from fractions import Fraction as F
from pathlib import Path
import json


def diagonal(values):
    return [[F(values[i]) if i == j else F(0) for j in range(len(values))]
            for i in range(len(values))]


def offdiag(i, j, n=4):
    b = diagonal([0] * n)
    b[i][j] = b[j][i] = F(1)
    return b


def trace(a):
    return sum(a[i][i] for i in range(len(a)))


def inner(a, b):
    return sum(a[i][j] * b[i][j]
               for i in range(len(a)) for j in range(len(a)))


def sphere_fourth(i, j, k, l):
    return F(int(i == j and k == l) + int(i == k and j == l)
             + int(i == l and j == k), 24)


def integrated_polynomial_product(a, b):
    """Uniform S3 average, before multiplying dimensional sphere volume."""
    return sum(a[i][j] * b[k][l] * sphere_fourth(i, j, k, l)
               for i in range(4) for j in range(4)
               for k in range(4) for l in range(4))


class Polynomial:
    """Small exact multivariate polynomial, sufficient for a SIS identity."""
    dimension = 6  # a_ol, a_ls, a_os, theta_E, beta, cos(2 phi)

    def __init__(self, terms):
        self.terms = {tuple(m): F(c) for m, c in terms.items() if c}

    @classmethod
    def variable(cls, index):
        powers = [0] * cls.dimension
        powers[index] = 1
        return cls({tuple(powers): 1})

    @classmethod
    def coerce(cls, value):
        return value if isinstance(value, cls) else cls({(0,) * cls.dimension: value})

    def __add__(self, other):
        other = self.coerce(other)
        terms = self.terms.copy()
        for m, c in other.terms.items():
            terms[m] = terms.get(m, F(0)) + c
        return Polynomial(terms)

    __radd__ = __add__

    def __neg__(self):
        return Polynomial({m: -c for m, c in self.terms.items()})

    def __sub__(self, other):
        return self + (-self.coerce(other))

    def __rsub__(self, other):
        return self.coerce(other) - self

    def __mul__(self, other):
        other = self.coerce(other)
        terms = {}
        for m1, c1 in self.terms.items():
            for m2, c2 in other.terms.items():
                monomial = tuple(x + y for x, y in zip(m1, m2))
                terms[monomial] = terms.get(monomial, F(0)) + c1 * c2
        return Polynomial(terms)

    __rmul__ = __mul__


def main():
    basis = [diagonal([3, -1, -1, -1])]
    basis += [offdiag(0, i) for i in (1, 2, 3)]
    basis += [diagonal([0, 1, -1, 0]), diagonal([0, 1, 1, -2])]
    basis += [offdiag(i, j) for i, j in ((1, 2), (1, 3), (2, 3))]
    norms = [inner(b, b) for b in basis]
    assert norms == [12, 2, 2, 2, 2, 6, 2, 2, 2]
    assert all(trace(b) == 0 for b in basis)
    assert all(inner(a, b) == 0 for i, a in enumerate(basis)
               for j, b in enumerate(basis) if i != j)
    assert all(integrated_polynomial_product(a, b) == inner(a, b) / 12
               for a in basis for b in basis)
    # N^2 times V(S3) divided by 12 = (6/pi^2 R^3)(2pi^2 R^3)/12.
    assert F(6 * 2, 12) == 1

    # Direct stationary variation of the SIS arrival time, separately on
    # the positive and negative image branches. No optical kernel is used.
    a, b, c, t, beta, angle = [Polynomial.variable(i) for i in range(6)]
    direct_plus = (F(1, 2) * (a - b + c) * t * t
                   + c * t * beta - a * t * (t + beta)) * angle
    direct_minus = (F(1, 2) * (a - b + c) * t * t
                    - c * t * beta - a * t * (t - beta)) * angle
    expected = 2 * t * beta * (a - c) * angle
    assert not (direct_minus - direct_plus - expected).terms
    # Background positive late-minus-early delay is 2 T0 theta_E beta/c.
    # Consequently the fractional response is (a_ol-a_os) cos(2 phi).

    result = {
        "status": "EXACT_RATIONAL_IDENTITIES_VERIFIED",
        "scope": "Algebraic verification, not observational or physical validation",
        "stf4_basis_dimension": len(basis),
        "unnormalized_basis_gram_diagonal": [int(n) for n in norms],
        "all_81_fourth_moment_contractions": "exact Tr(A B)/12",
        "volume_normalization": "N^2 V(S3)/12=1",
        "sis_stationary_delay_polynomial_remainder": "identically zero",
        "sis_fractional_response": "(a_ol-a_os) cos(2 phi)",
        "lens_to_source_shear": "cancels exactly in this declared SIS derivative"
    }
    output = Path(__file__).with_name("exact_identity_receipt.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
