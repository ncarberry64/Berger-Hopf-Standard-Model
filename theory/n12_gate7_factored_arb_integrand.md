# Factored evaluation of the retained local integrand

This is an exact algebraic evaluation change, not a new action or a changed
quadrature. The parent integrand source is pinned to
F832ADFAF8599FB591E5F5B91A1DA71F4CCE3F356CF3251386785050206C75F8.

For C=r exp(c), A=a0 exp(a), B=b0 exp(b), N=exp(n), evaluate inverse metric
squares directly as exp(-2c)/r^2, exp(-2a)/a0^2 and exp(-2b)/b0^2.
Collect the volume exponents before differentiating. With hC,hA,hB denoting
the numerators of the three ADM rates, the kinetic expression becomes

    -6 exp(-2n) [hA^2+hB^2+hC(hA+hB)+3 hA hB].

Symbolic tests verify the entire bulk and inertia identities. Tests of the
actual 32 fifth-order local jet coefficients use exact Arb input legs and
the frozen binary64 constants, requiring overlap with the parent graph.
Float-only derivative leaves are unsuitable for this check because the
parent local-variable helper does not automatically convert their products
to interval arithmetic before evaluation.

The implementation preserves the original floating products r*cos, r*sin,
3*cos^2, 3*sin^2, the potential constant, localization and quadrature weights.
It does not replace them by higher-precision trigonometry. Local maps and
affine values are cached only for one exact state and precision. Changing
either fails closed. Boundary evaluation and the global inertia reciprocal
are unchanged; the local inertia is still summed before taking that reciprocal.

The factored campaign prepares original base action jets and the original
eigenline before changing contraction evaluation. It uses a distinct
algorithm fingerprint and cache directory, binding both the backend adapter
and the factorization helper. Earlier physical rows retain their original
provenance and are not silently migrated.

    python scripts/derive_n12_gate7_factored_physical_hessian_errors.py --midpoints 200 --workers 6 --worker-hour-cap 3
    python scripts/derive_n12_gate7_factored_physical_hessian_errors.py --aggregate --midpoints 200

The inherited worker cap, row integrity checks, outward export containment,
complete upper-triangle coverage and failure retention remain applicable.
Two-column timing and full-width row pilots are performance/equivalence
evidence only. They do not constitute all-node physical coverage or Gate 7.
