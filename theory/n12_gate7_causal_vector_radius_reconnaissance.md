# Gate-7 causal vector-radius reconnaissance

The finite reset-to-stop shadow equation is causal.  A defect source on seam
`j` affects only later nodes `i>j`; its block Green derivative is strictly
lower triangular.  Collapsing this structure into one global Euclidean
`Y,Z1,Z2` maximum is therefore a sufficient proof coordinate, not a native
requirement of the retained action.

Let `c=A(-d)` be the stored signed linear Green correction and write the
exact correction as `e=c+delta`.  At node `j`, separate the quadratic source
without decorrelating it:

`0.5 D2f[c,c] + D2f[c,delta] + 0.5 D2f[delta,delta]`.

With causal block norms `G[i,j]`, directional curvature `Hd[j]`, mixed
curvature `Hm[j]`, and transverse curvature `Ht[j]`, the center-level vector
radius is the explicit recursion

`r_delta[i] = sum_(j<i) G[i,j] * (`

`  0.5 Hd[j] c[j]^2 + Hm[j] c[j] r_delta[j]`

`  + 0.5 Ht[j] r_delta[j]^2 )`.

There is no circular dependency at a fixed node.  This is the finite
Volterra form of the same Green/Krawczyk theorem and adds no physical
condition, selector, endpoint, or scale.

On the retained 48-node center, the recursion stays finite.  The linear
correction peaks at `3.4869031403256367e-6`; the generated nonlinear radius
peaks at the terminal node at `1.3397010452979786e-8`; and the total radius
peaks at `3.4871815769281147e-6`.  The terminal nonlinear radius decomposes
as

- directional: `2.3898597275570165e-9`;
- mixed: `2.7088578501864906e-9`;
- transverse quadratic: `8.29829287523628e-9`.

These are calibrated-center reconnaissance values.  The curvature source
and macro Green maps do not yet carry between-seam outward interval
authority, and the resulting 48 radii have not yet been compared with every
first-hit and physical-domain margin.  Therefore this result does not certify
the exact history or close Gate 7.

It does retire two unproductive proof coordinates: the isotropic ambient
curvature maximum and a single global Euclidean radii polynomial.  The live
theorem is now the outward cellwise version of the displayed triangular
recursion followed by the existing finite first-hit/domain transfer.
