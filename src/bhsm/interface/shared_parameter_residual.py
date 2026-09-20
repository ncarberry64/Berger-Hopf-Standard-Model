"""Common-parameter polynomial residuals and a certified linear solve tail.

No physical equation or action derivative is supplied by this module. In
particular, a contraction for one bordered matrix is not a contraction for
the stacked nonlinear BHSM graph.
"""
from flint import arb, arb_mat


def validate_groups(groups, dimension):
    covered = []
    for start, stop, norm in groups:
        if not 0 <= start < stop <= dimension or norm not in ('interval', 'box', 'euclidean'):
            raise ValueError('valid product-ball groups required')
        if norm == 'interval' and stop != start + 1:
            raise ValueError('interval group must be scalar')
        covered.extend(range(start, stop))
    if covered != list(range(dimension)):
        raise ValueError('groups must cover all shared parameters once')


def linear_support(coefficients, groups):
    """Upper bound for absolute linear support on the complete product ball."""
    validate_groups(groups, len(coefficients))
    result = arb(0)
    for start, stop, norm in groups:
        values = [abs(x).upper() for x in coefficients[start:stop]]
        result += (sum((v*v for v in values), arb(0)).sqrt()
                   if norm == 'euclidean' else sum(values, arb(0)))
    return result.upper()


def affine_dot_polynomial(left, right):
    """A^T B represents dot(A[1,theta],B[1,theta]) without coordinate hulls.

    The same parameter occurs in both operands. Symmetric cross terms are
    added before absolute values in quadratic_support.
    """
    if left.nrows() != right.nrows() or left.ncols() != right.ncols():
        raise ValueError('matching affine models required')
    return left.transpose()*right


def quadratic_support(coefficients, groups):
    """Outward bound for |[1,theta]^T C [1,theta]| on product unit balls."""
    size = coefficients.nrows()
    if size != coefficients.ncols() or size < 2:
        raise ValueError('square affine-product coefficient matrix required')
    n = size-1
    validate_groups(groups, n)
    linear = [coefficients[0, i+1]+coefficients[i+1, 0] for i in range(n)]
    # Symmetrization preserves the exact scalar polynomial. Even when two
    # interval coefficients are dependent, interval addition is an enclosure;
    # uncertainty is never silently identified or canceled.
    sym = [[(coefficients[i+1, j+1]+coefficients[j+1, i+1])/2
            for j in range(n)] for i in range(n)]
    inner = [linear_support(row, groups) for row in sym]
    return (abs(coefficients[0, 0]).upper()+linear_support(linear, groups)
            +linear_support(inner, groups)).upper()


class PolynomialMatrix:
    """Sparse polynomial with shared parameter IDs and Arb coefficient matrices.

    Keys are sorted tuples, e.g. (0,0,2) means theta_0^2 theta_2.
    Every monomial is retained. An operation-size cap fails rather than
    dropping high-order terms. Equal keys are combined before taking ranges.
    """
    def __init__(self, terms, rows, cols, parameters):
        if rows < 1 or cols < 1 or parameters < 1:
            raise ValueError('positive dimensions required')
        self.rows, self.cols, self.parameters = rows, cols, parameters
        self.terms = {}
        for key, value in terms.items():
            if tuple(sorted(key)) != key or any(not 0 <= i < parameters for i in key):
                raise ValueError('canonical common-parameter monomial required')
            if value.nrows() != rows or value.ncols() != cols:
                raise ValueError('coefficient shape mismatch')
            if not all(x.is_finite() for x in value.entries()):
                raise ValueError('finite coefficients required')
            if any(not x.is_zero() for x in value.entries()):
                self.terms[key] = value

    def __add__(self, other):
        if (self.rows, self.cols, self.parameters) != (other.rows, other.cols, other.parameters):
            raise ValueError('polynomial shape mismatch')
        terms = dict(self.terms)
        for key, value in other.terms.items():
            terms[key] = terms[key]+value if key in terms else value
        return PolynomialMatrix(terms, self.rows, self.cols, self.parameters)

    def __matmul__(self, other):
        if self.cols != other.rows or self.parameters != other.parameters:
            raise ValueError('shared polynomial product shape mismatch')
        if len(self.terms)*len(other.terms) > 100000:
            raise ValueError('bounded calculation exceeded polynomial product cap')
        terms = {}
        for left, a in self.terms.items():
            for right, b in other.terms.items():
                key = tuple(sorted(left+right))
                value = a*b
                terms[key] = terms[key]+value if key in terms else value
        return PolynomialMatrix(terms, self.rows, other.cols, self.parameters)

    def absolute_entry_bounds(self):
        # |theta_i|<=1 follows from every allowed product group. This fallback
        # is conservative; it does not claim an optimal polynomial support.
        result = arb_mat(self.rows, self.cols)
        for value in self.terms.values():
            for i in range(self.rows):
                for j in range(self.cols):
                    result[i, j] += abs(value[i, j]).upper()
        return result

    def transpose(self):
        return PolynomialMatrix({k: v.transpose() for k, v in self.terms.items()},
                                self.cols, self.rows, self.parameters)

    def scaled(self, scalar):
        """Multiply by one shared scalar polynomial, without making a box."""
        if (scalar.rows, scalar.cols, scalar.parameters) != (1, 1, self.parameters):
            raise ValueError('shared scalar polynomial required')
        if len(self.terms)*len(scalar.terms) > 100000:
            raise ValueError('bounded calculation exceeded polynomial product cap')
        terms = {}
        for left, a in self.terms.items():
            for right, b in scalar.terms.items():
                key = tuple(sorted(left+right))
                value = a*b[0, 0]
                terms[key] = terms[key]+value if key in terms else value
        return PolynomialMatrix(terms, self.rows, self.cols, self.parameters)

    def __neg__(self):
        return PolynomialMatrix({k: -v for k, v in self.terms.items()},
                                self.rows, self.cols, self.parameters)

    def __sub__(self, other):
        return self + (-other)


def coupled_first_variation_residual(H, H_u, source, source_u, psi, eigenvalue,
                                     hard, border, psi_u, line_border, hard_u, border_u):
    """Assemble the actual selected-line/response/axis residual equations.

    H is the raw reduced action Hessian; source is the metric-weighted
    physical response RHS. H_u and source_u use the unchanged physical
    direction. The common polynomial parameter namespace is used in every
    product. This assembles G, not a verified polynomial enclosure of the
    action functions: callers must supply their complete remainders too.
    """
    n, p = psi.rows, psi.parameters
    identity = PolynomialMatrix({(): arb_mat(n, n, [arb(i == j)
        for i in range(n) for j in range(n)])}, n, n, p)
    one = PolynomialMatrix({(): arb_mat(1, 1, [arb(1)])}, 1, 1, p)
    half = PolynomialMatrix({(): arb_mat(1, 1, [arb('0.5')])}, 1, 1, p)
    shifted = H-identity.scaled(eigenvalue)
    slope = psi.transpose() @ H_u @ psi
    return dict(
        eigenline=shifted @ psi,
        eigenline_normalization=(psi.transpose() @ psi-one).scaled(half),
        response=shifted @ hard+psi.scaled(border)-source,
        response_normalization=psi.transpose() @ hard,
        axis_line=shifted @ psi_u+psi.scaled(line_border)+H_u @ psi-psi.scaled(slope),
        axis_line_normalization=psi.transpose() @ psi_u,
        axis_response=shifted @ hard_u+psi.scaled(border_u)+H_u @ hard
                      -hard.scaled(slope)+psi_u.scaled(border)-source_u,
        axis_response_normalization=psi.transpose() @ hard_u+psi_u.transpose() @ hard)


def stack_polynomials(*blocks):
    """Stack equations while retaining the same monomial namespace."""
    if not blocks or any((b.cols, b.parameters) != (blocks[0].cols, blocks[0].parameters) for b in blocks):
        raise ValueError('compatible shared polynomial blocks required')
    rows = sum(b.rows for b in blocks)
    terms = {}
    offset = 0
    for block in blocks:
        for key, value in block.terms.items():
            terms.setdefault(key, arb_mat(rows, block.cols))
            for i in range(block.rows):
                for j in range(block.cols):
                    terms[key][offset+i, j] = value[i, j]
        offset += block.rows
    return PolynomialMatrix(terms, rows, blocks[0].cols, blocks[0].parameters)


def lifted_rate_residual(numerator, numerator_u, descriptor_numerator,
                         descriptor_numerator_u, norm, norm_u, rate, rate_u):
    """Keep the common positive norm as an implicit unknown instead of dividing.

    Caller supplies the original N=(s*c,W*(b*psi+s*hard)) and
    delta=cpsi*b+s*remainder and their COMPLETE directional derivatives.
    The physical domain must prove norm>0. That sign is not inferred here.
    """
    return dict(
        norm=norm.scaled(norm)-numerator.transpose() @ numerator,
        rate=rate.scaled(norm)-stack_polynomials(numerator, descriptor_numerator),
        norm_u=norm_u.scaled(norm)-numerator.transpose() @ numerator_u,
        rate_u=rate_u.scaled(norm)+rate.scaled(norm_u)
               -stack_polynomials(numerator_u, descriptor_numerator_u))


def hs_right_column_residual(left_state, right_state, midpoint_state,
                             left_rate, right_rate, endpoint_axis_rate,
                             midpoint_axis, midpoint_axis_rate, trial,
                             step, frozen_pullback, output_projector, unit_trial):
    """Complete original HS midpoint, chain direction, and right output column.

    All physical fields and their axis derivatives are shared polynomials in
    one namespace. No independent midpoint noise or center-shift omission is
    introduced. This assembler does not provide their action remainders.
    """
    def scale(poly, value):
        return PolynomialMatrix({k: v*value for k, v in poly.terms.items()},
                                poly.rows, poly.cols, poly.parameters)
    p = left_state.parameters
    pullback = PolynomialMatrix({(): frozen_pullback}, frozen_pullback.nrows(), frozen_pullback.ncols(), p)
    project = PolynomialMatrix({(): output_projector}, output_projector.nrows(), output_projector.ncols(), p)
    unit = PolynomialMatrix({(): unit_trial}, unit_trial.nrows(), 1, p)
    return dict(
        midpoint_relation=midpoint_state-scale(left_state+right_state, arb('0.5'))
                          -scale(left_rate-right_rate, step/8),
        chain_direction=midpoint_axis-scale(trial, arb('0.5'))+scale(endpoint_axis_rate, step/8),
        projected_right_column=project @ (unit-pullback @ trial
            +scale(pullback @ endpoint_axis_rate, step/6)
            +scale(pullback @ midpoint_axis_rate, 2*step/3)))


def solve_projected_residual(residual, defect, output, weights, steps=2):
    """Bound C e for e=r(theta)+E(theta)e, retaining theta through the solve.

    Finite part: C sum_{k=0}^{m-1} E^k r, combined as a polynomial.
    Tail: sup||C E^m||_{w->infinity} eta/(1-q), where eta bounds r in
    weighted infinity norm and q bounds E. These are caller-owned equations
    on the whole unit parameter box (also covering product unit balls).
    For a nonlinear graph the caller must additionally provide a valid
    secant-defect representation and invariant correction domain.
    """
    n, p = residual.rows, residual.parameters
    if residual.cols != 1 or (defect.rows, defect.cols, defect.parameters) != (n, n, p):
        raise ValueError('complete coupled residual and defect required')
    if output.ncols() != n or len(weights) != n or not 1 <= steps <= 8:
        raise ValueError('compatible projection, weights and bounded steps required')
    if not all(w.is_finite() and w > 0 and w.rad().is_zero() for w in weights):
        raise ValueError('positive exact weights required')
    eb, rb = defect.absolute_entry_bounds(), residual.absolute_entry_bounds()
    q = max((sum((eb[i, j]*weights[j] for j in range(n)), arb(0))/weights[i]).upper()
            for i in range(n))
    if not q < 1:
        raise ArithmeticError('stacked defect is not a proved strict contraction')
    eta = max((rb[i, 0]/weights[i]).upper() for i in range(n))
    identity = arb_mat(n, n, [arb(i == j) for i in range(n) for j in range(n)])
    power = PolynomialMatrix({(): identity}, n, n, p)
    total = PolynomialMatrix({}, n, 1, p)
    for _ in range(steps):
        total = total + power @ residual
        power = power @ defect
    projection = PolynomialMatrix({(): output}, output.nrows(), n, p)
    finite = (projection @ total).absolute_entry_bounds()
    tail = (projection @ power).absolute_entry_bounds()
    error = (eta/(1-q)).upper()
    bounds = [(finite[i, 0]+sum((tail[i, j]*weights[j] for j in range(n)), arb(0))*error).upper()
              for i in range(output.nrows())]
    return bounds, dict(q=q, eta=eta, correction_norm_upper=error,
                        finite_part=finite, projected_tail_operator=tail,
                        shared_parameter_polynomial=projection @ total)
