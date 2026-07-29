# BHSM v6.30.7 scalar-wall quartic normalization and source audit

## Result

Primary verdict:

`BHSM_CORE_COMPLETION_BLOCKED_BY_UNSELECTED_SCALAR_QUARTIC_INVARIANT`

The frozen provisional parent action contains the scalar quartic term. It is
not a missing term, an integration constant, or a coefficient introduced by
the v6.30.5 reduction. Constant scalar normalization removes redundant
separate descriptions of \(G_5\) and \(Z_5\), but leaves the genuine
dimensionless invariant

\[
\lambda_5=\frac{\kappa_1G_5}{Z_5^2}.
\]

No licensed repository mechanism selects \(\lambda_5\). Tier A therefore
remains blocked. A dimensionless coefficient cannot be absorbed into the
one-universal-dimensionful-scale allowance, so v6.31 is not permitted.

## Parent-action provenance

The earliest parent architecture is commit
`1a8e2bcad6cb892b75bbf4951a67de76dcebff55`, v6.0.2:

\[
U_\sigma
=\frac12A(C_{\rm EG})\sigma^2
+\frac14G(C_{\rm EG})\sigma^4
+O(\sigma^6).
\]

That phase classified the potential as
`ARCHITECTURE_IDENTIFIED_SOURCE_NOT_DERIVED`. It did not derive
\(C_{\rm EG}\), \(G(C_{\rm EG})\), or the stored v5 target value.

Commit `c903a2b6788515196225c0634753826d0e7d241d`, v6.0.5, froze the
provisional Lorentzian parent term

\[
S\supset-\int_{M_8}\sqrt{-G}\,\frac{G_0}{4}\sigma^4.
\]

Its primitive ledger counts \(G_0/Z_\sigma^2\) among five
field-normalization invariants and reports all five as internally unsourced.
The v6.1.5 pushforward

\[
[Z_5,A_5,G_5]
=\operatorname{Vol}(S^3)[Z_\sigma,A_0,G_0]
\]

fixes volume factors but does not select the parent coefficient. The parent
term is therefore present as an independent frozen primitive, while its
deeper geometric sign and value are not derived. This is Outcome D, not the
missing-term Outcome E.

## Full constant field-normalization group

Let

\[
\widehat{\sigma}=c\sigma,\qquad c\in\mathbb R^\times.
\]

Writing the same action in the hatted coordinate gives

\[
\widehat Z_5=\frac{Z_5}{c^2},\qquad
\widehat A_5=\frac{A_5}{c^2},\qquad
\widehat G_5=\frac{G_5}{c^4},\qquad
\widehat\kappa_1=\kappa_1.
\]

Consequently,

\[
\widehat\mu_c=-\frac{\widehat A_5}{\widehat Z_5}=\mu_c,
\qquad
\widehat\lambda_5
=\frac{\widehat\kappa_1\widehat G_5}{\widehat Z_5^2}
=\lambda_5.
\]

The raw transformed Jacobi tangent is \(cu_1\), with inherited KKT norm
\(c^2\). Restoring unit normalization gives

\[
\widehat u_1=\operatorname{sgn}(c)u_1,\qquad
\widehat q=|c|q.
\]

Equivalently, holding the orientation of \(u_1\) fixed gives
\(\widehat q=cq\). The kinetic coefficient and canonical field obey

\[
\widehat k_0=\frac{k_0}{c^2},\qquad
\widehat\varphi
=\sqrt{\widehat k_0}\,\widehat q
=\varphi
\]

in the normalized-mode convention. The projected force and potential
coefficients transform as

\[
\widehat g_3=\frac{g_3}{c^2},\qquad
\widehat V_{E,4}=\frac{V_{E,4}}{c^4},
\]

while

\[
\widehat g_4^{\rm can}
=\frac{\widehat V_{E,4}}{\widehat k_0^2}
=g_4^{\rm can}.
\]

Thus setting \(G_5=1\) would only choose a scalar coordinate; it would not
remove \(\lambda_5\).

## Invariant factorization

The v6.30.5 coefficients become

\[
g_3
=\frac{Z_5}{\kappa_1}
\left(130.140781376473\lambda_5+2368.23593065773\right),
\qquad
\Omega_3=-g_3,
\]

\[
V_{E,4}
=\frac{Z_5^2}{\kappa_1}
\left(260.281562752946\lambda_5+3633.0356624841\right),
\]

\[
g_4^{\rm can}
=\frac1{\kappa_1}
\left(5.84444718718846\lambda_5+81.5773688846122\right).
\]

\(g_3\), \(\Omega_3\), \(V_{E,4}\), \(q\), and \(k_0\) are
normalization-dependent. The dimensionless \(\lambda_5\), the first
canonical interaction's order, and its sign are normalization invariants.
Unit-bearing observables still require scale closure.

## Selection tests

Every licensed candidate was tested:

- Action variation produces \(G_0\sigma^3\), not an equation for \(G_0\).
- \(\mathbb Z_2\) symmetry forbids odd powers but fixes no quartic sign or
  magnitude.
- Regularity, finite profiles, cap exchange, two-cap gluing, and matcher
  consistency constrain fields and boundary data, not the bulk coefficient.
- The stable-wall domain \(A_5<0,G_5>0\) is conditional solution data, not a
  selector.
- A globally bounded pure quartic truncation would require \(G_0>0\), but
  the frozen theory did not adopt global boundedness as a coefficient axiom
  and explicitly records all coefficient signs as unselected.
- The critical mode fixes \(\mu_c=-A_5/Z_5\), not \(\lambda_5\).
- P1 curvature, the connection, the singlet spectrum, and pure-singlet tower
  elimination supply no quartic value.
- The exact-branch cancellation locus is an algebraic consequence, not an
  action-selected input.
- No quantum action or renormalization boundary value exists that selects
  the classical BHSM 1.0 coefficient.

No stable-wall tuning, branch-restoration tuning, Higgs input, mass or VEV
fit, new interaction, cutoff, targeted renormalization condition,
naturalness assumption, empirical inverse, or vacuum subtraction was used.

## Exact branch and local stability

The exact-branch cancellation locus and minimum domain are

\[
\lambda_5^{\rm branch}=-18.1974927890349085,
\qquad
\lambda_5>-13.95809839182684.
\]

Their certified separation is

\[
-13.95809839182684-(-18.1974927890349085)
=4.2393943972080685>0.
\]

The canonical-quartic bracket at the branch locus is approximately
\(-24.776916660145155\). Exact branch restoration and a local quartic
minimum therefore cannot occur at one selected value.

This does not invalidate the isolated critical configuration or the reduced
effective family. The exact branch is not a BHSM 1.0 requirement. Higher
orders at the unselected cancellation locus remain post-1.0.

The only justified local classification is:

- strict quartic minimum for \(\lambda_5>-13.95809839182684\);
- strict quartic maximum below that threshold;
- quartic degeneracy at equality, with no higher-order conclusion here.

No global stability, unique vacuum, tunneling lifetime, physical mass, or
physical scale is claimed.

## Completion impact and hindsight

Tier A is blocked; Tier B and Tier C are not eligible. Unconditional local
stability and v6.31 are not permitted. The exact campaign stop condition is
an unselected dimensionless coefficient.

### Validated

- The v6.30.5 reduced coefficients survive invariant factorization.
- The parent term is present as an independent frozen primitive.
- \(\lambda_5\) is invariant.
- Exact-branch cancellation and local quartic stability are incompatible.

### Invalidated

- \(G_5\) is entirely removable by normalization.
- “Stable wall” selects \(G_5>0\).
- The cancellation locus may be chosen to restore a branch.
- One external dimensionful calibration can absorb \(\lambda_5\).

### Repaired

- The blocker is now stated in \(\lambda_5\), not separate \(G_5,Z_5\).
- Presence of the term is separated from derivation of its coefficient.

### Still open and newly blocked

- An action-derived selector for \(\lambda_5\).
- Unconditional local quartic stability.
- Tier A dimensionless closure and every dependent scale/release gate.

### Moved to post-1.0

- Exact neighboring-branch restoration.
- Higher interactions at its unselected cancellation locus.
- Global vacuum and nonlinear-solution classification.
