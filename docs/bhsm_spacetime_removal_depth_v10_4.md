# BHSM v10.4 Spacetime-Removal Depth

## Result

The strongest existing-action candidate is

\[
q_V=-\frac18\log\frac{d\mu_G}{d\mu_{\bar G}}.
\]

It does not supply an independent physical depth mode after constraint
reduction. The exact verdict is

`BHSM_PROPER_VOLUME_DEFICIT_HAS_NO_INDEPENDENT_PHYSICAL_SCALAR_AFTER_CONSTRAINT_REDUCTION`.

## Covariance boundary

The ratio of metric volume forms is a scalar only when both metrics live on
the same parent manifold and are compared through one explicit pullback. Under
a simultaneous diffeomorphism it transforms as a scalar. In fixed-background
perturbation theory, however,

\[
\delta_\xi q_V=-\frac18\bar\nabla_A\xi^A,
\]

so a raw local determinant suppression is not gauge invariant. A compact
integrated volume may be invariant when boundary flux vanishes, but it is a
global observable rather than local core depth.

## Exact ADM reduction

For the P1 homogeneous metric with logarithmic radii
`(u4,u2,u1)` and multiplicities `(4,2,1)`,

\[
q_V=-\frac18(4\delta u_4+2\delta u_2+\delta u_1)
    =-\frac78\delta\rho,
\]

where

\[
\rho=\frac{4u_4+2u_2+u_1}{7},\quad
\beta=u_1-u_2,\quad
\gamma=u_2-u_4.
\]

The exact DeWitt kinetic form already derived in v6.0.9--v6.0.10 becomes

\[
\mathbb G_{\rho\beta\gamma}=
\begin{pmatrix}
-42&0&0\\
0&6/7&4/7\\
0&4/7&12/7
\end{pmatrix}.
\]

The shape eigenvalues are `4/7` and `2`. The negative `rho` direction belongs
to the lapse/Hamiltonian first-class constraint chain; it is not promoted to a
propagating ghost. With lapse included, the four configuration variables have
eight-dimensional phase space. The primary constraint `p_N=0` and secondary
Hamiltonian constraint `C_H=0` leave four physical phase-space dimensions,
or two shape configurations. The physical projection of `q_V` into that
shape space is therefore exactly zero.

Vertical-only breathing produces `q_V=-3 delta beta/8` before volume
compensation and is overlap with the existing core/Hopf mode, not a third
mode. In an Einstein-frame volume-compensated variation `rho=0`, `q_V=0`
while a healthy shape mode may remain. The second positive M8 anisotropy shape
is not a volume-removal observable and is not relabeled `q_D`.

## Core domain

For `rho_V>0`, `q_V` is finite. It becomes large but finite in a
nondegenerate high-depletion region. At `rho_V=0`, it diverges and the current
inverse-metric Einstein action is outside its domain. Coordinate lapse collapse
or determinant zero is not treated as core physics. A degenerate or stratified
transition requires a different well-posed geometric action.

## Minimal-extension decision

The campaign compares constrained volume forms, unimodular decomposition,
independent measures, core-support order parameters, stratified degenerate
transitions, non-Riemannian/topological forms, and parent-measure composites.
Some provide only global or auxiliary data; others introduce genuinely new
geometric configuration spaces, kinetics, potentials, junction data, and
continuous coefficients. None strictly dominates under the current action and
author axioms. No field or parameter is adopted.

Campaign verdict:

`BHSM_MINIMAL_GEOMETRIC_DEPTH_EXTENSION_REQUIRES_AUTHOR_SELECTION`.

Exact next object:

`AUTHOR_SELECTION_OF_MINIMAL_GEOMETRIC_DEPTH_EXTENSION_CONFIGURATION_AND_ACTION`.
