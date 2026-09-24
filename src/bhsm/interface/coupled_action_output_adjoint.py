"""Differentiate the complete fixed-input action graph and physical readout.

Formal first jets compute derivatives, not neighborhood enclosures. Arb
coefficients enclose the supplied anchor matrices. The returned adjoint is an
exact midpoint proposal with an explicitly retained anchor defect.
"""
from flint import arb, arb_mat


class FirstJet:
    def __init__(self, value, derivative):
        self.c, self.a = value, derivative

    def __add__(self, other):
        if isinstance(other, FirstJet):
            return FirstJet(self.c+other.c, self.a+other.a)
        return FirstJet(self.c+arb(other), self.a)

    __radd__ = __add__

    def __neg__(self):
        return FirstJet(-self.c, -self.a)

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, other):
        if isinstance(other, FirstJet):
            return FirstJet(self.c*other.c, self.a*other.c+other.a*self.c)
        return FirstJet(self.c*arb(other), self.a*arb(other))

    __rmul__ = __mul__

    def reciprocal(self):
        if self.c.contains(0):
            raise ArithmeticError('anchor reciprocal crosses zero')
        return FirstJet(1/self.c, -self.a/self.c**2)

    def __truediv__(self, other):
        return self * (other.reciprocal() if isinstance(other, FirstJet) else 1/arb(other))

    def sqrt(self):
        if not self.c > 0:
            raise ArithmeticError('anchor physical norm is not positive')
        root = self.c.sqrt()
        return FirstJet(root, self.a/(2*root))


def dot(left, right):
    return sum((a*b for a, b in zip(left, right, strict=True)), arb(0))


def matvec(matrix, vector):
    n = matrix.nrows()
    count = vector[0].a.ncols()
    values = arb_mat(len(vector), count+1,
                    [v.c if j == 0 else v.a[0, j-1] for v in vector for j in range(count+1)])
    product = matrix*values
    return [FirstJet(product[i, 0], arb_mat(1, count, [product[i, j+1] for j in range(count)]))
            for i in range(n)]


def linearize(H, H_u, configuration, configuration_u, reduced_weights,
              descriptor, descriptor_u, output, centers, descriptor_jet):
    """Return J=D_U G and l=D_U[output*F_u] for all four coupled blocks.

    H is the raw reduced action Hessian, H_u its full input-direction
    derivative. descriptor_jet(p,h,pu,hu) supplies c,R,c_u,R_u and their
    complete U derivatives from the retained third/fourth action contractions.
    All input-state, source and descriptor parameters are held fixed here.
    Sources f,f_u are independent of U, so their constants need not be
    supplied to differentiate G. No source is dropped in residual evaluation.
    """
    n = H.nrows()
    dimension = 4*(n+1)
    if (H.ncols() != n or (H_u.nrows(), H_u.ncols()) != (n, n)
            or len(centers) != dimension or len(output) != len(configuration)+n+1):
        raise ValueError('complete action matrices, solve centers and physical output required')
    if len(reduced_weights) != n or not callable(descriptor_jet):
        raise ValueError('complete descriptor derivative callback and metric required')
    U = [FirstJet(arb(c), arb_mat(1, dimension, [arb(i == j) for j in range(dimension)]))
         for i, c in enumerate(centers)]
    p, lam = U[:n], U[n]
    h, b = U[n+1:2*n+1], U[2*n+1]
    pu, gamma = U[2*n+2:3*n+2], U[3*n+2]
    hu, bu = U[3*n+3:4*n+3], U[4*n+3]
    Hp, Hh, Hpu, Hhu = [matvec(H, v) for v in (p, h, pu, hu)]
    Hup, Huh = matvec(H_u, p), matvec(H_u, h)
    alpha = dot(p, Hup)
    rows = [Hp[i]-lam*p[i] for i in range(n)]+[(dot(p, p)-1)/2]
    rows += [Hh[i]-lam*h[i]+b*p[i] for i in range(n)]+[dot(p, h)]
    rows += [Hpu[i]-lam*pu[i]+gamma*p[i]+Hup[i]-alpha*p[i]
             for i in range(n)]+[dot(p, pu)]
    rows += [Hhu[i]-lam*hu[i]+bu*p[i]+Huh[i]-alpha*h[i]+b*pu[i]
             for i in range(n)]+[dot(p, hu)+dot(pu, h)]
    J = arb_mat(dimension, dimension, [v for row in rows for v in row.a.entries()])

    c, remainder, cu, ru = descriptor_jet(p, h, pu, hu)
    if any(not isinstance(v, FirstJet) or v.a.ncols() != dimension for v in (c, remainder, cu, ru)):
        raise ValueError('complete scalar descriptor first jets required')
    s, su = arb(descriptor), arb(descriptor_u)
    constant = lambda v: FirstJet(arb(v), arb_mat(1, dimension))
    N = [constant(s*x) for x in configuration]+[reduced_weights[i]*(b*p[i]+s*h[i]) for i in range(n)]
    Nu = [constant(su*x+s*y) for x, y in zip(configuration, configuration_u)]
    Nu += [reduced_weights[i]*(bu*p[i]+b*pu[i]+su*h[i]+s*hu[i]) for i in range(n)]
    delta, deltau = b*c+s*remainder, bu*c+b*cu+su*remainder+s*ru
    norm = dot(N, N).sqrt()
    readout = dot(output, Nu+[deltau])/norm-dot(output, N+[delta])*dot(N, Nu)/(norm*norm*norm)
    return J, readout.a, readout.c


def adjoint_proposal(jacobian, output_gradient):
    solved = jacobian.transpose().solve(output_gradient.transpose()).transpose()
    proposal = arb_mat(solved.nrows(), solved.ncols(), [v.mid() for v in solved.entries()])
    defect = output_gradient-proposal*jacobian
    if any(not v.is_finite() for matrix in (proposal, defect) for v in matrix.entries()):
        raise ArithmeticError('finite full coupled anchor adjoint required')
    return proposal, defect
