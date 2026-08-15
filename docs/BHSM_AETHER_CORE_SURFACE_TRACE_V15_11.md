# BHSM v15.11 core--surface trace theorem

The retained reciprocal attachment action fixes the regular-side compactified
core-compatibility equations without a fitted norm:

\[
\mathcal M_A=(\upsilon|_B,I_W|_B)=0,
\qquad I_W=\upsilon I_C,
\]

with bounded \(I_C\).  Both half-character terms then vanish as
\(\sqrt{\upsilon}I_C\).  Because the inherited wall incidence is
\(I_W=\operatorname{id}_5(g_5)\), this zero set is metric-incidence rank loss,
not a nondegenerate regular boundary state.

## Positive-capacity obstruction

Let \(A(s)\) be the transverse area density of a regular collar and

\[
R_B=\int \frac{ds}{A(s)},\qquad \operatorname{Cap}(B)=R_B^{-1}.
\]

For \(q_D=-\lambda_D\log\upsilon\), Cauchy--Schwarz gives the sharp bound

\[
E_{\rm Haar}\geq
\frac{\lambda_D^2}{2}\operatorname{Cap}(B)
\log^2\!\left(\frac{\upsilon_{\rm in}}{\upsilon_{\rm out}}\right).
\]

A smooth nondegenerate codimension-one parent surface has positive capacity,
so \(\upsilon_{\rm out}\to0\) costs infinite regular action.  Restricting the
condition to the outermost layer does not remove this obstruction.  A
zero-capacity escape requires geometric degeneration or removal of the set and
therefore has no ordinary codimension-one trace.  It is a domain/reconstruction
transition, not a regular solution.

In Haar depth the endpoint is \(q_D=+\infty\).  The retained free principal
operator is limit-point there, supplies no self-adjoint extension parameter,
and has zero Green flux on its \(L^2\) domain.  Terminal data therefore do not
create passage.

## Pullback to v15.9 and v15.10

The full nonlinear v15.9 eta continuation is computed on the regular
\(\upsilon=1\) background, and the retained action has no eta-to-support source.
Consequently every layer, at every continued radius, has
\(I_W/I_C=1\), so eta concentration does not dynamically select a
core-compatible outer surface.

The v15.10 A/B/C completions share the same \(\sigma=0\), \(\upsilon=1\)
parent.  The pullback of \(\mathcal M_A\) therefore has

\[
\frac{\partial\mathcal M_A}{\partial(\alpha,r,\gamma)}=(0,0,0).
\]

Core matching as presently derived cannot resolve their nonuniqueness.
The equation \(F_\alpha=0\) is neither necessary nor sufficient for the core
trace; it remains an early response diagnostic.

## Scientific conclusion

The author's outer-layer principle determines a compatibility closure but not
a dynamical transfer law.  Surface passage, persistence, and de-envelopment
cannot be continued within the retained action because there is no core-side
trace module or nonzero conservative cross-stratum flux block.  The smallest
new foundational object is:

`ACTION_OWNED_PREGEOMETRIC_CORE_BOUNDARY_HILBERT_CORRESPONDENCE_WITH_NONZERO_CONSERVATIVE_TRANSFER_BLOCK_AND_VARIATIONAL_COUPLING_TO_THE_REGULAR_SUPPORT_SIGMA_METRIC_HOPF_RESPONSE_JET`

Adding such a structure would change the underlying physical assumptions.  It
has not been adopted or disguised as a derived BHSM term.  Thus
`FULL_BHSM_COMPLETE` remains false for a genuine mathematical obstruction, not
an administrative gap.

## Hindsight 20/20

Validated: reciprocal incidence closure; positive-capacity Haar obstruction;
limit-point endpoint; v15.9 and v15.10 pullback no-go.

Invalidated: an outer-layer-only regular limit evades the Haar barrier;
eta concentration supplies the missing surface; terminal Dirichlet data
produces passage; \(F_\alpha=0\) is core matching.

Reclassified: lack of spacetime is reconstruction-rank loss in the regular
closure; surface capacity is the exact bulk/interface discriminator; the
core--surface principle is compatibility data rather than transfer dynamics.

Open: the exact foundational object displayed above.
