# BHSM v14.65 — Self-Adjoint Boundary Triple and Reduced Heat-Semigroup Closure

## Executive result

v14.65 constructs the exact reduced continuum object requested by v14.64.
The two-cap envelopment incidence diamond is realized as four finite magnetic
intervals joined at the four strata

\[
M_8,\quad M_{5,+},\quad M_{5,-},\quad M_4.
\]

The edge operator is

\[
P_e=-D_e^2+m^2,
\qquad
D_e=\partial_x-iA_e,
\]

with integrated edge phase

\[
\alpha_e=\int_e A_e\,dx.
\]

At every stratum vertex the domain imposes continuity of the field and
conservation of outward covariant flux.  In boundary-triple notation,

\[
A\Gamma_0+B\Gamma_1=0.
\]

The exact finite-dimensional self-adjoint-extension criterion is satisfied:

\[
\operatorname{rank}(A\;B)=8,
\qquad
AB^*=BA^*.
\]

The boundary Green form vanishes on the declared domain.  Therefore the
reduced magnetic diamond defines a genuine self-adjoint continuum operator;
the v14.64 issue is not an absence of any possible self-adjoint boundary
correspondence.

**This does not yet close the physical BHSM operator.**  It closes a rigorous
reduced theorem class in which the tangential operators on each stratum have
been replaced by scalar interval propagation.

## Exact DtN / Weyl function

For an edge of length \(\ell\), positive resolvent parameter \(\kappa\), and
integrated phase \(\alpha\), solving

\[
(-D_x^2+\kappa^2)u=0
\]

gives the exact endpoint Dirichlet-to-Neumann matrix

\[
M_e(\kappa)=
\kappa
\begin{pmatrix}
\coth(\kappa\ell)&-e^{-i\alpha}\operatorname{csch}(\kappa\ell)\\
-e^{i\alpha}\operatorname{csch}(\kappa\ell)&\coth(\kappa\ell)
\end{pmatrix}.
\]

Summing edge contributions at common vertices gives the four-stratum Weyl
matrix.  The implementation verifies:

* Hermiticity;
* positivity at positive resolvent parameter;
* covariance under vertex rephasing;
* invariance of the one diamond holonomy.

Thus v14.65 provides the exact reduced DtN mechanism rather than a guessed
finite coupling matrix.

## Exact reduction to a magnetic circle

There is also a decisive restriction.  Every vertex in the minimal diamond
has degree two.  Standard continuity plus Kirchhoff matching therefore makes
the scalar graph unitarily equivalent to one circle whose circumference is

\[
L=\ell_{8+}+\ell_{+4}+\ell_{-4}+\ell_{8-}
\]

and whose only gauge-invariant connection datum is

\[
\Phi
=\alpha_{8+}+\alpha_{+4}-\alpha_{-4}-\alpha_{8-}
\pmod{2\pi}.
\]

The exact spectrum is

\[
\lambda_n
=
\left(\frac{2\pi n+\Phi}{L}\right)^2+m^2,
\qquad n\in\mathbb Z.
\]

Consequently, two very different assignments of the four edge lengths with
the same total \(L\) and the same \(\Phi\) are exactly isospectral in this
minimal scalar realization.

This is a useful obstruction, not a failure of the boundary-triple program:

\[
\boxed{
\text{scalar degree-two matching is too small to retain independent }M_8/M_5/M_4\text{ dynamics.}
}
\]

The full BHSM correspondence must therefore use operator-valued tangential
Weyl functions and/or dynamic Wentzell/KKT boundary degrees of freedom.

## Heat-semigroup branch is exact in the reduced class

For the predeclared heat branch,

\[
\Theta(t;\Phi)=\operatorname{Tr}e^{-tP_\Phi},
\]

the momentum representation is

\[
\Theta(t;\Phi)
=e^{-m^2t}\sum_{n\in\mathbb Z}
\exp\!\left[-t\left(\frac{2\pi n+\Phi}{L}\right)^2\right].
\]

Poisson summation gives the equivalent winding representation

\[
\Theta(t;\Phi)
=
\frac{L}{\sqrt{4\pi t}}e^{-m^2t}
\sum_{k\in\mathbb Z}
\exp\!\left[-\frac{L^2k^2}{4t}\right]e^{ik\Phi}.
\]

The code checks the two forms directly to numerical precision.

The relative determinant against the zero-holonomy branch is closed exactly
for \(m>0\):

\[
\boxed{
\log\frac{\det_\zeta P_\Phi}{\det_\zeta P_0}
=
\log\frac{\cosh(mL)-\cos\Phi}{\cosh(mL)-1}.
}
\]

No arbitrary cutoff profile appears in this relative reduced result.

## New holonomy-selection mechanism

The nonlocal determinant is not merely a bookkeeping correction.  It creates
a genuine force on the global loop phase:

\[
\frac{\partial}{\partial\Phi}
\log\frac{\det P_\Phi}{\det P_0}
=
\frac{\sin\Phi}{\cosh(mL)-\cos\Phi}.
\]

For a positive single-species prefactor the reduced determinant has a local
minimum at \(\Phi=0\).  Reversing the determinant/statistics sign reverses
that stability conclusion.  In the complete BHSM supertrace, multiple
bosonic, fermionic and ghost sectors must be combined before a physical
holonomy can be selected.

Therefore v14.65 establishes a concrete mechanism by which the loop phase can
become action-selected rather than fitted to CKM or PMNS data, while refusing
to claim that the current reduced witness already fixes the physical phase.

## No-retuning pipeline witness

A synthetic v14.61-style global scale functional is frozen before solving:

\[
0
=8A_8e^{8x}+6A_6e^{6x}+3A_3e^{3x}+Z.
\]

Its unique diagnostic root is computed, frozen geometric edge fractions are
converted into edge lengths, frozen edge connection phases determine the loop
holonomy, and the self-adjoint heat/zeta outputs are then computed with no
later adjustment.

This proves the software/dataflow contract

\[
\text{global BVP}
\to
\text{geometry/holonomy}
\to
\text{self-adjoint operator}
\to
\text{heat/zeta observables}
\]

can be executed without retuning.  Every number in this witness is synthetic
and explicitly nonphysical.

## Hindsight ledger

### Validated

1. A reduced continuum self-adjoint boundary-triple realization exists.
2. Continuity + covariant Kirchhoff matching passes the exact extension
   criterion.
3. The exact magnetic DtN/Weyl matrix is Hermitian, positive at positive
   resolvent parameter, and gauge covariant.
4. The minimal degree-two diamond is exactly a magnetic circle.
5. The heat trace admits matching momentum and winding representations.
6. The relative zeta determinant is closed exactly in the reduced class.
7. The nonlocal determinant supplies an action-owned holonomy force once the
   operator/statistics are fixed.

### Invalidated

1. The minimal scalar Kirchhoff graph can retain independent spectral memory
   of all four stratum lengths.
2. A scalar metric graph is already the full M8/M5/M4 BHSM operator.
3. The loop holonomy necessarily remains a freely inserted flavor parameter.

### Reclassified

1. The unresolved continuum-domain problem is now specifically the
   **operator-valued tangential** domain, not the existence of any
   self-adjoint correspondence realization.
2. The diamond holonomy is a dynamical action variable in the heat/zeta branch.
3. Independent cap/stratum physics must enter through tangential Dirac-Laplace
   blocks, Calderon/Weyl operators, or Wentzell/KKT dynamic seam terms.

### Open

* actual M8 tangential Dirac-Laplace operator;
* actual two M5 cap operators;
* intrinsic M4 fermion/gauge/scalar operator;
* action-derived dynamic seam/Wentzell-KKT coupling;
* physical connection holonomy;
* complete gauge/ghost/zero-mode projectors;
* mixed-dimensional relative heat supertrace;
* physical global stationary parent-child solution and branch exhaustion;
* effective fermion/current operators;
* physical DtN/relative heat bundle;
* frozen no-retuning neutrino kill screen.

## Completion status

`FULL_BHSM_COMPLETE = FALSE`

`MARK_III = NOT_REACHED`

Frozen predictions are unchanged.  Official prediction logic is unchanged.
No physical mass, coupling, CKM/PMNS matrix, CP phase, neutrino splitting, or
cross section is emitted.  USB remains untouched.

## Exact next object

`OPERATOR_VALUED_CALDERON_BOUNDARY_TRIPLE_OR_WENTZELL_KKT_REALIZATION_USING_THE_ACTUAL_M8_M5_PLUS_MINUS_M4_TANGENTIAL_DIRAC_LAPLACE_BLOCKS_ACTION_SELECTED_GLOBAL_ENVELOPMENT_LENGTHS_AND_CONNECTION_HOLONOMY_COMPLETE_GAUGE_GHOST_ZERO_MODE_PROJECTORS_THEN_COMPUTE_THE_FULL_RELATIVE_HEAT_KERNEL_ZETA_FUNCTION_GLOBAL_STATIONARY_BRANCH_AND_RUN_THE_FROZEN_NO_RETUNING_NEUTRINO_KILL_SCREEN`
