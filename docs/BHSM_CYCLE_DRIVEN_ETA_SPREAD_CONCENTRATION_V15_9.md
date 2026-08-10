# BHSM v15.9 — Cycle-driven eta spread-to-concentration bifurcation

## Scientific verdict

`FULL_BHSM_COMPLETE = FALSE`.

The retained degree-one radial eta action has a previously unexploited exact
supercritical bifurcation when the parent radius is allowed to pass through a
cycle-driven critical value. This is an action-derived regular-state
spread-to-concentration transition, not a postulated Aether density and not a
new fluid. It materially advances the formation problem, but it does not yet
construct the Hopf parent-child enclosure or its relative-periodic persistence.

The result corrects the interpretation of the v14.93 fixed-radius theorem.
That theorem is the critical slice of the larger cycle-controlled family: the
quartic coefficient is positive at the crossing, while the quadratic
coefficient changes sign as the parent radius changes. Negative Hessian is one
sufficient spinodal route, not a universal prerequisite for every BHSM
formation mechanism.

## Retained radial action and exact threshold

For the round degree-one ansatz, no field or coefficient is added:

\[
E[f]=\int_0^\pi\!\sin^6\chi
\left(\frac{\kappa_1}{2}X+\frac18X^4\right)d\chi,
\qquad
X=\frac{f'^2+6\sin^2f/\sin^2\chi}{a^2}.
\]

The conformal identity branch is \(f=\chi\). Its exact Hessian in the
\(y_0=\sin\chi\) direction obeys

\[
\frac{E_{ss}(0)}{E_{2,\mathrm{id}}}
=\frac{343}{4\kappa_1a^6}-\frac54,
\qquad
a_c^6=\frac{343}{5\kappa_1}.
\]

It is positive below \(a_c\), zero at \(a_c\), and negative above it.

## Exact Lyapunov–Schmidt branch

Using

\[
f=\chi+q\sin\chi+cq^2\sin\chi\cos\chi+O(q^3),
\]

the order-\(q^2\) complement equation is

\[
-\frac67(108c-19)\sin^7\chi\cos\chi=0,
\]

so \(c=19/108\). Writing \(a^6/a_c^6=1+\alpha q^2+\cdots\), the
order-\(q^3\) kernel projection is

\[
\frac{35\pi}{1152}(45\alpha-23)=0,
\]

and therefore

\[
\frac{a^6}{a_c^6}=1+\frac{23}{45}q^2+O(q^4).
\]

The reduced energy is

\[
\frac{\Delta E}{E_{2,c}}
=-\frac58m q^2+\frac{23}{144}q^4+\cdots,
\qquad m=\frac{a^6}{a_c^6}-1.
\]

Thus the nonuniform branches are supercritical and radially restoring after
the identity loses stability.

## Full radial Euler continuation

The implementation solves the untruncated Euler equation in a pole-regular
sine basis by exact variational Galerkin stationarity. An independent adaptive
collocation BVP with regular Robin pole limits reproduces the same profile.
Representative 12-mode results are:

| \(a^6/a_c^6\) | first amplitude \(q\) | \(C_\eta=\langle j_\eta^2\rangle\) | weighted Euler residual |
|---:|---:|---:|---:|
| 1.001 | 0.0442444940 | 1.012027947 | \(1.6\times10^{-14}\) |
| 1.010 | 0.1402562468 | 1.124330170 | \(1.1\times10^{-13}\) |
| 1.040 | 0.2828262305 | 1.554692120 | \(2.6\times10^{-9}\) |

The degree remains one to floating precision and the coefficient-space radial
Hessian is positive at every tested resolution. The collocation profile at
1.01 differs from the Fourier profile by less than \(10^{-7}\).

For

\[
j_\eta=f'\left(\frac{\sin f}{\sin\chi}\right)^6,
\qquad \langle j_\eta\rangle=1,
\]

the exact local series is

\[
C_\eta=1+\frac{49}{8}q^2+O(q^4)
=1+\frac{2205}{184}m+\cdots.
\]

This is a concentration diagnostic of the retained eta map. It is not a
primitive material density.

## Existing sigma coupling and its provenance boundary

The retained sigma curvature at \(\sigma=0\) is

\[
A_0+g\left(\kappa_1X_\eta+\frac14X_\eta^4\right).
\]

At the critical identity strain, set
\(\alpha=A_0/(g\kappa_1X_c)\) and \(x=X_\eta/X_c\). The normalized curvature
is

\[
F_\alpha(x)=\alpha+x+\frac54x^4.
\]

For the ordinary parent to be stable while the depleted pole can cross zero,
\(-9/4<\alpha<0\). Continuing the actual numerical eta branch gives, for
example, threshold radius ratios 1.0002541333, 1.0137736830, and 1.1233295572
for \(\alpha=-2,-1,-1/4\), respectively.

This is a conditional prediction across the retained action family. The
current action architecture does not select \(\alpha\), so none of these
examples is promoted as the physical BHSM threshold. The coupled
Einstein–eta–sigma branch has not been solved.

This boundary was checked against the full retained lineage rather than
inferred from the local model alone. The v9.0 parent-action record explicitly
classifies `kappa0,kappa1,Zchi,Zsigma,g,A0,G0` as independent theory inputs;
the v6.0.3 threshold operator and v6.1.2 localization analysis retain the same
unselected-coefficient status. No existing Norman/BHSM theorem fixes the ratio.

## Hopf topology firewall

The eta-only Hopf cohomogeneity-one identity Hessian is strictly positive at
every radius. With \(w=\sin^3\chi\cos^3\chi\), it is proportional to

\[
\int w\left[y'^2+3(\cot\chi-\tan\chi)^2y^2
+\frac{294}{\kappa_1a^6+343}
(y'+3(\cot\chi-\tan\chi)y)^2\right]d\chi.
\]

Consequently there is no eta-only Hopf linear bifurcation from the identity
branch. This is a sector theorem, not a global coupled no-go. In particular,
the radial \(S^6\) level surfaces are not identified with the physical
\(S^3\times S^3\) full-preimage seam.

The first non-Killing coexact vector harmonic on \(S^7\) is \(k=2\), with
candidate reduced frequency squared \(21/a^2\). For the explicit field
\(V=x_0(-x_2\partial_{x_1}+x_1\partial_{x_2})\), the exact moments are
\(\langle|V|^2\rangle=1/40\), \(\langle|V|^4\rangle=1/560\), and participation
ratio \(20/7\). Its attachment as a complete constrained ADM mode remains
conditional.

## What is now closed and what is not

Derived here:

- exact cycle-controlled radial threshold and supercritical normal form;
- full Euler branch by two independent numerical methods;
- degree preservation and regular-state concentration;
- conditional local sigma-curvature crossing using the existing coupling;
- eta-only Hopf positivity and its precise scope;
- exact non-Killing \(L=2\) spectrum and moments.

Not derived:

- action selection of the retained sigma coefficient ratio;
- a coupled constraint-solved Einstein–eta–sigma solution on the new branch;
- continuation to a degree-one Hopf parent-child enclosure;
- a common physical self-adjoint domain for that enclosure;
- nested internal-scale decoupling and a stable relative-periodic/Floquet orbit.

The exact next object is

`FULL_HOPF_PARENT_CHILD_EINSTEIN_ETA_SIGMA_CONSTRAINT_CONTINUATION_FROM_THE_ACTION_DERIVED_RADIAL_CONCENTRATION_BRANCH_WITH_ACTION_SELECTED_SIGMA_COEFFICIENT_BRANCH_NESTED_SCALE_AND_RELATIVE_PERIODIC_COMMON_DOMAIN`.

No empirical input, fitted coefficient, new field, preferred frame, or frozen
prediction change is introduced. USB/removable media is not inspected or
touched.
