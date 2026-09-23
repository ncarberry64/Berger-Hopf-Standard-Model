# Eigenpair contraction with signed affine action derivatives

For the reduced symmetric action Hessian H(x), use the normalized eigenpair
equations F(x,p,lambda)=(H(x)p-lambda*p, (p^T p-1)/2). The physical input domain
remains the frozen affine tube x=x0+u*l+E*t, |l|<=rL, ||t||2<=rT. These physical
trial radii are distinct from the auxiliary eigenpair proposal radii below.

Choose fixed exact dyadic centers p0, lambda0 and a fixed exact dyadic matrix R.
The Newton map is T_x(y)=y-R*F(x,y), y=(p,lambda). All entries of R are fixed over
the input domain and proposal box. No floating inverse is used as a proof.

The uniform center residual is bounded by applying the complete third-action
contraction with R's left rows, p0, and each signed affine input direction before
taking absolute values. Include the actual center residual R*F(x0,p0,lambda0).
For any collection of directional contractions dL,dT, the bound is

    rL*sup|dL| + rT*sqrt(sum_j sup|dT_j|^2).

This follows from the mean-value identity along the affine segment and
Cauchy-Schwarz for the transverse ball. The retained action evaluator includes
all quadrature contributions, the global inertia reciprocal, and the boundary.
Its inertia must have a positive enclosure on the entire segment hull, ensuring
the action is smooth there. All signed output and input contractions precede
interval hulls; separately bounding raw matrix entries would lose correlations.

Let r=(r_p,r_lambda)>0 be exact proposal radii and D0 enclose I-R*J(x0,p0,lambda0).
To bound the state-dependent Jacobian variation, use the same complete
third-action contractions with the vector leg v ranging over |v_j|<=r_p,j.
Call the resulting row bounds S_i. They bound the radius-weighted row sum of
R*(H(x)-H(x0)) without first forming an uncorrelated Hessian-entry enclosure.

The remaining p/lambda variation has row bound

    N_i = 2*r_lambda*sum_j |R_ij|*r_p,j
          + |R_i,n|*sum_j r_p,j^2.

The factor two includes both the varying-lambda diagonal block and the
varying-vector last column. The final term bounds the normalization row.
Thus the weighted Jacobian row bound and image bound are

    V_i = sum_j |D0_ij|*r_j + S_i + N_i,
    image_i <= Y_i+V_i.

Strict inequalities Y_i+V_i<r_i and V_i<r_i for every row prove self-inclusion
and a uniform contraction in the radius-weighted infinity norm. Decisions use
outward rational margins, not rounded display ratios. If a proposal fails,
enlarging only its failed eigenpair coordinates from the computed image bounds
is permitted, but the complete variation must be recomputed on the new box.
This never changes rL, rT, the action, or the physical domain.

Banach's theorem gives one normalized real eigenpair in the proposal box for
each actual x in the affine tube. The contraction also implies that R*J, and
therefore both R and J, are nonsingular. For a symmetric H at a normalized
eigenpair, nonsingularity of J implies that the selected eigenvalue is simple.

Index transfer requires a separate argument, not a floating spectral label.
An independently normalized, oriented, index-24 point witness at x0 must lie
inside the new proposal box. Uniqueness identifies the new fixed point there
with that witness. The common uniform contraction and smooth action imply
continuous dependence of the fixed point on x. The affine tube is connected;
its ordered symmetric eigenvalues are continuous. The selected index cannot
change without a repeated eigenvalue, which would make J singular. Hence the
point's index 24 persists over this tube. Orientation must also remain positive
against the original stored reference throughout the entire proposal box.

These conclusions require the complete action/domain bindings, the positive
inertia bound, point-witness containment, every contraction inequality, and an
independent numerical repeat. A residual diagnostic or pure row-bound fixture
alone establishes none of them. This is still a selected endpoint action-mode
certificate, not an enclosure of the physical field, its bordered response or
derivatives, actual HS midpoint domains, the physical quotient, or Gate7.
