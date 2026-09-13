# Component bounds from the existing coupled defect proof

This refinement concerns the numerical enclosure of an existing bordered
system. It does not change the retained action, physical domain, preconditioner
or paired eigenpair box, and by itself supplies no physical closure claim.

Suppose the paired family has a fixed preconditioner R, original eigenpair
radius vector r, and the following stored components:

- D0 encloses I - R J0 at the fixed state/eigenpair anchor.
- S bounds the state-dependent Hessian difference, preconditioned by R,
  acting on the lower n coordinates of the radius box r.
- The eigenpair parameters satisfy |delta p_j| <= r_j and
  |delta lambda| <= r_n on the same domain.

S is recovered from the stored signed trial-variation contractions with all
original domain groups. No action contraction is replaced with sampled data.

For any nonnegative error-radius vector w, a bound on |(I-RJ) error| for
|error_j| <= w_j is

\[
\begin{aligned}
B_k(w)={}&\sum_j |D_{0,kj}|w_j
+ S_k\max_{j<n}(w_j/r_j)\\
&+r_n\sum_{j<n}|R_{kj}|w_j
+w_n\sum_{j<n}|R_{kj}|r_j
+|R_{kn}|\sum_{j<n}r_j w_j.
\end{aligned}
\]

All absolute values and arithmetic are rounded outward. The state term has
no last input column. The next two terms distinguish the **fixed domain**
lambda radius from the current error's last-coordinate radius. The last term
is the bottom-row dependence on p. At w = r this reproduces the original
coupled defect decomposition (up to outward rounding).

Recompute q = max B_k(r)/r_k and require q < 1. For an exact center z0 and
the preconditioned residual e = R(b-Jz0), the initial error enclosure is

\[
w^{(0)}=r\frac{\max_k |e_k|/r_k}{1-q}.
\]

Then every finite iteration

\[
w^{(m+1)}_k=\min\{w^{(m)}_k,\ |e_k|+B_k(w^{(m)})\}
\]

is another valid enclosure: the already enclosed error satisfies
error = e + (I-RJ) error. This is enclosure refinement, not an assumed
convergence test or a change to the physical trial radii. The diagnostic uses
32 iterations; validity does not depend on reaching a numerical tolerance.

The simpler component refinement uses the already aggregated V = B(r):
|error_k| <= |e_k| + V_k * initial_weighted_error_bound. The decomposed version
retains the separate dependencies when applying subsequent iterations.

Tests compare the operator bound and enclosed solutions against independently
constructed perturbed bordered matrices with nonzero state, p and lambda
variations. Noncontractive input fails closed. Production use still requires
paired source bindings, independent numerical reproduction and complete
direction coverage; the current diagnostic does not assert those latter
completion conditions.
