"""Outward heat contractions of a finite positive generalized pencil.

No eigensolve, spectral-frame differentiation, or mixed operator tensor.
This dense kernel is for small/condensed retained blocks. A large realization
should supply the equivalent trace contractions through its existing sparse
or transfer backend; it must retain the interior spectral contribution.
"""
from flint import arb, arb_mat
from bhsm.interface.gate7_current_action import checked


def identity(n):
    return arb_mat([[int(i == j) for j in range(n)] for i in range(n)])


def trace_product(a, b):
    n = a.nrows()
    checked(a, n, n, 'trace left'); checked(b, n, n, 'trace right')
    return sum((a[i, j]*b[j, i] for i in range(n) for j in range(n)), arb(0))


def positive_form(form):
    """Sufficient interval LDL test, without changing the supplied form."""
    n = form.nrows()
    checked(form, n, n, 'positive form')
    for i in range(n):
        for j in range(i):
            if not (form[i, j].contains(form[j, i]) and form[j, i].contains(form[i, j])):
                raise ValueError('identical symmetric form entries required')
    L = identity(n); pivots = []
    for i in range(n):
        pivot = form[i, i]-sum((L[i, k]**2*pivots[k] for k in range(i)), arb(0))
        if not pivot > 0:
            raise ValueError('positive form not enclosed by this LDL chart')
        pivots.append(pivot)
        for j in range(i+1, n):
            L[j, i] = (form[j, i]-sum((L[j, k]*L[i, k]*pivots[k]
                                      for k in range(i)), arb(0)))/pivot
    return pivots


class HeatPencil:
    """Gamma=-Tr E1(ell^2 M^-1 K)/2 on a positive quotient.

    Both K and M are retained; using K alone is a different action.
    Every contraction encloses the finite supplied pencil. Completeness of
    grading, quotient, domain, tails and contacts belongs to the caller's
    action realization, not to this arithmetic routine.
    """
    def __init__(self, K, M, heat_length=1):
        self.n = K.nrows()
        if self.n < 1:
            raise ValueError('nonempty quotient pencil required')
        checked(M, self.n, self.n, 'M')
        positive_form(K); positive_form(M)
        self.a = arb(heat_length)**2
        if not arb(heat_length) > 0:
            raise ValueError('positive heat length required')
        self.M = M
        self.A = M.solve(K)
        self.exponential = (-self.a*self.A).exp()
        # X A = exp(-a A); solve on the transpose, without an explicit inverse.
        self.Q = self.A.transpose().solve(self.exponential.transpose()).transpose()/2
        checked(self.Q, self.n, self.n, 'heat cotangent')

    def first_operator(self, K_d, M_d):
        checked(K_d, self.n, self.n, 'K_d'); checked(M_d, self.n, self.n, 'M_d')
        return self.M.solve(K_d-M_d*self.A)

    def first(self, K_d, M_d):
        return trace_product(self.Q, self.first_operator(K_d, M_d))

    def directional_cotangent(self, K_d, M_d):
        """D f'(A)[A_d] via one block exponential, valid without commuting jets."""
        E = self.first_operator(K_d, M_d)
        block = arb_mat(2*self.n, 2*self.n)
        for i in range(self.n):
            for j in range(self.n):
                block[i, j] = block[self.n+i, self.n+j] = -self.a*self.A[i, j]
                block[i, self.n+j] = -self.a*E[i, j]
        exponential = block.exp()
        Lexp = arb_mat(self.n, self.n,
                      [exponential[i, self.n+j] for i in range(self.n) for j in range(self.n)])
        rhs = Lexp/2-self.Q*E
        DQ = self.A.transpose().solve(rhs.transpose()).transpose()
        checked(DQ, self.n, self.n, 'directional heat cotangent')
        return E, DQ

    def mixed_direction(self, K_p, M_p):
        """Bind one direction for streaming output rows without a mixed-base cache."""
        E_p, DQ_p = self.directional_cotangent(K_p, M_p)
        mass_p = arb_mat(M_p.tolist())
        def contract(K_b, M_b, K_bp, M_bp):
            for name, value in [('K_bp', K_bp), ('M_bp', M_bp)]:
                checked(value, self.n, self.n, name)
            E_b = self.first_operator(K_b, M_b)
            E_bp = self.M.solve(K_bp-M_bp*self.A-M_b*E_p-mass_p*E_b)
            pair = trace_product(DQ_p, E_b)
            contact_mass = trace_product(self.Q, E_bp)
            return dict(value=pair+contact_mass, pair=pair, mixed_and_mass=contact_mass)
        return contract

    def mixed(self, K_b, M_b, K_p, M_p, K_bp, M_bp):
        """Pair plus genuine mixed term, including both moving-mass terms.

        A_bp=M^-1(K_bp-M_bp A-M_b A_p-M_p A_b).
        Use mixed_direction(K_p,M_p) to stream all 66 output contractions
        of a single H/B input direction with one block exponential.
        """
        return self.mixed_direction(K_p, M_p)(K_b, M_b, K_bp, M_bp)
