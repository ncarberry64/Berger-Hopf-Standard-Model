"""Dependency-preserving residual transport through an acyclic solve graph."""
from flint import arb, arb_mat
from bhsm.interface.shared_parameter_residual import PolynomialMatrix, stack_polynomials


def transport(residuals, defects, output, weights, steps=2):
    """Bound C e for e_i=r_i+sum_{j<=i} E_ij e_j on one shared domain.

    Callers own the complete secant equations and correction-domain inclusion.
    Strict contraction is needed for each diagonal block, not for the raw
    unweighted stack. Off-diagonal amplification is explicitly propagated.
    No statement of physical inclusion is inferred from algebraic solvability.
    """
    count = len(residuals)
    if not count or len(weights) != count or not 1 <= steps <= 8:
        raise ValueError('complete blocks, weights and bounded expansion required')
    p = residuals[0].parameters
    sizes = [r.rows for r in residuals]
    if any(r.cols != 1 or r.parameters != p for r in residuals):
        raise ValueError('one common parameter namespace required')
    if output.ncols() != sum(sizes):
        raise ValueError('complete output pullback required')
    for (i, j), block in defects.items():
        if not 0 <= j <= i < count:
            raise ValueError('acyclic lower-triangular dependency graph required')
        if (block.rows, block.cols, block.parameters) != (sizes[i], sizes[j], p):
            raise ValueError('coupling shape mismatch')
    for n, w in zip(sizes, weights, strict=True):
        if len(w) != n or any(not x.is_finite() or not x > 0 or not x.rad().is_zero() for x in w):
            raise ValueError('positive exact block weights required')

    def block(i, j):
        return defects.get((i, j), PolynomialMatrix({}, sizes[i], sizes[j], p))

    def opnorm(poly, left, right):
        bound = poly.absolute_entry_bounds()
        return max((sum((bound[i, j]*right[j] for j in range(poly.cols)), arb(0))/left[i]).upper()
                   for i in range(poly.rows))

    models, errors, reports = [], [], []
    for i, r in enumerate(residuals):
        diagonal = block(i, i)
        q = opnorm(diagonal, weights[i], weights[i])
        if not q < 1:
            raise ArithmeticError('diagonal secant defect is not a strict contraction')
        rhs = r
        for j in range(i):
            rhs = rhs + block(i, j) @ models[j]
        value, term = PolynomialMatrix({}, sizes[i], 1, p), rhs
        for _ in range(steps):
            value = value + term
            term = diagonal @ term
        # This exact polynomial residual also detects finite-series or upstream
        # model errors. Shared monomials cancel before absolute values.
        defect = rhs + diagonal @ value - value
        radius = defect.absolute_entry_bounds()
        eta = max((radius[k, 0]/weights[i][k]).upper() for k in range(sizes[i]))
        coupling = [opnorm(block(i, j), weights[i], weights[j]) for j in range(i)]
        error = ((eta+sum((a*b for a, b in zip(coupling, errors)), arb(0)))/(1-q)).upper()
        models.append(value)
        errors.append(error)
        reports.append(dict(diagonal_q=q, model_residual=eta,
                            upstream_operator_bounds=coupling, correction_remainder=error))
    projection = PolynomialMatrix({(): output}, output.nrows(), output.ncols(), p)
    projected = projection @ stack_polynomials(*models)
    finite = projected.absolute_entry_bounds()
    bounds, tails = [], []
    for k in range(output.nrows()):
        offset, tail = 0, arb(0)
        for i in range(count):
            tail += errors[i]*sum((abs(output[k, offset+j]).upper()*weights[i][j]
                                   for j in range(sizes[i])), arb(0))
            offset += sizes[i]
        tails.append(tail.upper())
        bounds.append((finite[k, 0]+tail).upper())
    return bounds, dict(blocks=reports, projected_model=projected, projected_tail=tails,
                        physical_secant_and_domain_inclusion_supplied_by_caller=True)
