# BHSM v15.26: eta-wall orientation to material response

## Result and provenance

The retained v15.25 action cannot activate an exactly zero sigma field because
it has an independent sigma reflection.  The adopted v14.45 eta-bound Dirac
domain supplies a normalized normal zero mode

\[
u_0=N J^{-1/2}\sin f_\eta,
\qquad
\int J|u_0|^2\,ds=1.
\]

Consequently the oriented collar carries the canonical probability one-form

\[
\alpha_\eta=J|u_0|^2ds=N^2\sin^2(f_\eta)ds,
\qquad
\int_{s_-}^{s_+}\alpha_\eta=1.
\]

This result uses the foundational effective eta-bound Dirac structure already
adopted in v14.45.  It is not a derivation from the old bosonic Path-B action.

The minimal coefficient-free completion *candidate* covariantizes the existing
scalar kinetic block:

\[
-\frac{Z_\sigma}{2}(\nabla\sigma)^2
\longrightarrow
-\frac{Z_\sigma}{2}(\nabla\sigma-\alpha_\eta)^2.
\]

It adds no field and no continuous coefficient.  Its variation gives

\[
Z_\sigma\nabla_a(\nabla^a\sigma-\alpha_\eta^a)
-V'_{\rm even}(\sigma)=0,
\]

so its candidate odd scalar source is

\[
\mathcal O_\eta=Z_\sigma\nabla_a\alpha_\eta^a.
\]

The candidate response ground section in the free-response limit is

\[
C_\eta(s)=\int_{s_-}^{s}\alpha_\eta,
\qquad
\sigma_\eta=C_\eta-\frac12,
\]

with fixed endpoint values \((-1/2,+1/2)\).  Orientation reversal maps this
profile to its negative after the collar pullback.  The completed action is
invariant under the diagonal reversal
\((\sigma,\alpha_\eta)\mapsto(-\sigma,-\alpha_\eta)\), but not under either
reflection independently.

This does **not** yet promote the candidate to the physical BHSM action.  On
the collar

\[
\alpha_\eta=dC_\eta,
\qquad
\xi=\sigma-C_\eta,
\qquad
(d\sigma-\alpha_\eta)^2=(d\xi)^2.
\]

The connection therefore has zero curvature and zero closed-loop holonomy.
Its unit integral is open-path endpoint transport, not a nontrivial holonomy.
Without an independently action-derived affine sigma boundary domain, the
candidate is locally a field redefinition and supplies no irreducible bulk
material energy or backreaction.  The rank-one coordinate Gram block below
has the same limitation.

## Analytic control and retained profile

For the v14.45 analytic control, \(\sin f_\eta=\operatorname{sech}(s/\ell_\eta)\),

\[
\alpha_\eta=\frac{1}{2\ell_\eta}\operatorname{sech}^2(s/\ell_\eta)ds,
\qquad
\sigma_\eta=\frac12\tanh(s/\ell_\eta).
\]

It obeys

\[
\ell_\eta\partial_s\sigma_\eta=\frac12-2\sigma_\eta^2
\]

and exactly recovers, after subtracting a constant, the historical normalized
potential

\[
V=-\sigma^2+2\sigma^4,
\quad A_{ST}=-2,
\quad G_{ST}=8.
\]

This BPS polynomial identity is not exact for the retained v13.1
\(p=2+p=8\) numerical eta profile (the best rescaled first-order fit has a
relative residual of about 0.24).  Therefore the historical quartic is retained
as an exact analytic-wall control, not promoted as the full physical
nonlinear potential.

## Moving reduced system

If the solved moving wall has cumulative response \(C_\eta(q,s)\), the new
collective kinetic block is

\[
\frac{Z_\sigma}{2}
(\dot\sigma-C_q\dot q-C_s\dot s)^2.
\]

Its Gram contribution is the positive-semidefinite rank-one outer product

\[
Z_\sigma(-C_q,-C_s,1)^T(-C_q,-C_s,1).
\]

This gives the coordinate Gram block that the candidate would produce, but it
is removed by \(\xi=\sigma-C_\eta\) unless the affine domain or a nonzero
connection curvature is independently physical.  It is therefore not
promoted as the previously missing transfer.  The values \(C_q,C_s\) would in
any case require the constraint-solved moving eta/join boundary-value problem.

## Completion ledger

Validated: the normalized eta zero mode supplies a unit open-path orientation
one-form and a coefficient-free affine response candidate.  The analytic wall
exactly recovers the old normalized quartic.  The exact-gradient candidate is
locally field-redefinition trivial.

Invalidated: treating that quartic as exact for the retained numerical eta
profile, or reporting the completion as already derived from the old bosonic
action.

Closed here: the canonical normalized eta one-form, the analytic quartic
identity, and the field-redefinition audit of the smallest gradient
completion.

Active dependency: derive a non-exact eta/Hopf configuration-space connection,
an action-selected affine sigma domain, or an independently normalized
nonderivative vertex.  The nearest existing non-exact structures were also
audited.  The eta projector curvature is nonzero but is traceless SU(3)
polarization curvature with no gauge-invariant linear singlet scalar and no
fixed physical Yang--Mills normalization.  The relative Z6 holonomy orients
but does not create amplitude and is not action-attached.  The conserved
topological three-current gives
\(d\sigma\wedge j_3=d(\sigma j_3)\) on every regular branch.

The first upstream possibility not killed by these identities is a
distributional \(dj_3\) supplied by an actual fiber-boundary flux at a
reconstruction/topology-change event, paired with a self-adjoint sigma trace
without a free vertex coefficient.  That event flux is not yet present in the
repository.  No physical material skin, particle, Standard Model, or
full-BHSM completion claim is made by this intermediate result.
