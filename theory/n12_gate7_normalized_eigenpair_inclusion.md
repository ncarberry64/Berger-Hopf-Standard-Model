# Inclusion of a proposed normalized eigenpair

Floating eigenvalues may propose a local eigenpair box, but they need not be
assumed to supply a rigorous spectral gap. The independent verifier uses the
equations F(p,l) = (H p - l p, (p^T p - 1)/2) on the proposed box X.

Let z0 be the exact dyadic midpoint of X and let R be the entrywise midpoint
of an Arb inverse of the center Jacobian. R is a fixed matrix. Bound

    T(z0)-z0 = -R F(z0),
    DT(X) = I - R DF(X),
    T(z) = z - R F(z).

For box radii r_i > 0, strict componentwise bounds

    |R F(z0)|_i + sum_j |I-R DF(X)|_ij r_j < r_i

establish self-inclusion. In addition, the maximum weighted derivative row
sum must be strictly less than one. Banach's theorem then supplies one fixed
point in X. The derivative bound also implies R is nonsingular (otherwise
I-R DF would retain eigenvalue one), so the fixed point solves F=0. The same
uniform bounds apply to every fixed real matrix H in the supplied matrix
enclosure; interval dependencies are conservatively included.

An explicit exact target-radius vector may define a smaller box with the same
midpoint inside the supplied Arb balls. This prevents reconstruction of saved
balls from silently enlarging the box being certified: Arb's radius constructor
may round outward. The Jacobian enclosure over the supplied outer balls remains
valid over the smaller target box, and the report records its exact rational
midpoints and radii. Every target radius must be positive, exact, and no larger
than its outer radius.

This proves one normalized real eigenpair inside the proposed box, not an
ordering of the complete spectrum, a physical branch identity, or continuation
between parameter boxes. A failed inclusion test rejects this proof attempt;
it does not prove that the proposed box contains no eigenpair. Existing
physical Hessian certificates acquire no new authority until their actual
eigenpair/matrix enclosures have been checked and their provenance connected.
