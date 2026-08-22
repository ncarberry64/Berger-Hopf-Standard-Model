# Local continuum Galerkin flow from the certified N12 child

This lemma concerns only the existing retained Euler--Dirac flow in the fixed
action-coordinate neighborhood already certified at N12. It introduces no
new trajectory, selector, or physical acceptance condition.

Let \(X_E=H^1_q\times L^2_v\times H^1_m\) be the existing mixed energy space,
let \(P_M^G\) be the trace-compatible action-orthogonal Galerkin projector,
and let \(V_M\) denote the retained Euler--Dirac vector field at cutoff \(M\).
The established source-restricted decomposition gives

\[
 \|(I-P_M^G)V(Y)\|_{X_E}
 \leq \varepsilon_{ED}(M)
 \leq \frac{4C_{ED}^G}{\sqrt M}
\]

on the certified action ball. The noncompact principal/pole block is included
in the existing indicial inverse, and the four direct configuration traces
have zero tail. Thus this estimate is not obtained by discarding a principal
term.

The finite-core Jacobi bound supplies a Lipschitz majorant \(L\) for the
vector field on the same ball. If \(Y_M\) and \(Y_N\) are two retained
Galerkin solutions with initial action-graph discrepancy \(a\), Duhamel and
Gronwall give, while both remain in the ball,

\[
 \|Y_N(t)-I_{M,N}Y_M(t)\|_{X_E}
 \leq e^{Lt}a+\frac{e^{Lt}-1}{L}\varepsilon_{ED}(M).
\]

The action-derived inverse-square continuum correction supplies \(a\), and
the already-selected proof cutoff supplies \(\varepsilon_{ED}(M)\). At the
certified positive duration, the resulting bound plus the vector-field path
bound is strictly smaller than the existing action-ball radius. Hence the
nested Galerkin flows are Cauchy in \(X_E\) on this interval and define the
unique local continuum retained child flow there.

This closes only the local anchor segment. It does not imply recurrence,
ordered-event return, global eta/Dirac invariance, or a physical readout. To
extend the maximal-flow dichotomy, one still needs either an a priori
strong-space bound with uniform eta/Dirac margins or a finite analytic cover
of the actual admissible continuum orbit segment. Numerical trajectory
sampling cannot replace that estimate.
