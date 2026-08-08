# BHSM v14.59 — Exact Berger-Dirac Blocks, Fiber Symmetry, and Regular-Cap Nonuniqueness

## Primary verdict

`BHSM_V14_59_THE_EXACT_HOMOGENEOUS_BERGER_DIRAC_BLOCKS_REPLACE_THE_ROUND_ONLY_SPECTRAL_BASELINE_AND_PROVE_A_REAL_ANISOTROPIC_NONCOMMUTING_MECHANISM_BUT_AXISYMMETRY_PRESERVES_A_U1_SELECTION_RULE_AND_THE_REGULAR_CHILD_CAP_DTN_IS_NOT_DETERMINED_BY_SEAM_DATA`

v14.59 performs the next exact operator step after the round-collar baseline.
It implements the homogeneous Dirac operator on every finite SU(2) isotypical
block, specializes it to the Berger family, identifies its first zero-mode
crossing, and constructs the corresponding finite-block nonzero-mode
projector.

It also proves a completion-critical negative result: even after imposing a
regular center condition, common seam data do not determine the child cap
Dirichlet-to-Neumann map. The interior stationary background is indispensable.

No physical mass, mass splitting, PMNS or CKM matrix, coupling, absolute scale,
lifetime, cross section, or complete particle spectrum is emitted.

## 1. Exact homogeneous Dirac blocks

For the left-invariant metric whose orthonormal Lie-algebra frame has inverse
lengths \(a,b,c>0\), define

\[
C=\frac12\left(\frac{ab}{c}+\frac{bc}{a}+\frac{ca}{b}\right).
\]

On the spin-\(j=n/2\) representation, with angular momentum matrices
\(J_x,J_y,J_z\), the exact finite block used here is

\[
D_n=C I+2a\,\sigma_z\otimes J_z
       +2b\,\sigma_y\otimes J_y
       +2c\,\sigma_x\otimes J_x.
\]

This is the matrix form of the homogeneous-space Dirac restriction. Each
internal eigenvalue of \(D_n\) contributes an additional isotypical
multiplicity factor \(n+1\) to the full spectrum.

For the round sphere, \(a=b=c=1/R\). The block spectrum becomes

\[
\underbrace{-\frac{n+1/2}{R},\ldots,-\frac{n+1/2}{R}}_{n\ \text{times}},
\qquad
\underbrace{\frac{n+3/2}{R},\ldots,\frac{n+3/2}{R}}_{n+2\ \text{times}}.
\]

Across adjacent blocks this reproduces the usual round spectrum
\(\pm(k+3/2)/R\) with multiplicity \((k+1)(k+2)\) for each sign.

## 2. Berger specialization and exact first zero mode

Use

\[
h_\beta=R^2(\sigma_1^2+\sigma_2^2+\beta^2\sigma_3^2),
\]

so

\[
a=b=\frac1R,
\qquad
c=\frac1{\beta R}.
\]

The \(n=1\) block has exact eigenvalues

\[
\frac{\beta-4}{2R},
\qquad
\frac{\beta^2+4}{2\beta R}
\quad\text{(double)},
\qquad
\frac{\beta+4}{2R}.
\]

Therefore the first block crossing occurs exactly at

\[
\boxed{\beta=4}.
\]

The internal kernel is one-dimensional; the full isotypical zero-mode
multiplicity is two because the \(n=1\) representation has dimension two.

At the historical frozen diagnostic

\[
\beta_{\rm fr}=1.157054135733433,
\]

the \(n=1\) block is strictly gapped. The package constructs the exact finite
spectral projector onto the nonzero subspace. This is only the spinor part of a
physical zero-mode projector; gauge, metric, ghost, seam, and collective modes
remain open.

## 3. Real noncommutativity, but an exact fiber-U(1) obstruction

The Berger derivative is

\[
\partial_\beta D_n
=
\frac{1-2/\beta^2}{2R}I
-
\frac{2}{\beta^2R}\sigma_x\otimes J_x.
\]

For \(n\ge1\), generally

\[
[D_n(\beta_1),D_n(\beta_2)]\ne0,
\qquad
[D_n,\partial_\beta D_n]\ne0.
\]

Thus a time-dependent Berger deformation can generate a genuine
noncommuting ordered exponential. This is a real action-compatible source of
nontrivial monodromy, not a hand-inserted flavor matrix.

However every Berger block commutes with the same fiber generator

\[
K_x=I\otimes J_x+\frac12\sigma_x\otimes I:
\qquad
[D_n(\beta),K_x]=0.
\]

The derivative commutes with \(K_x\) as well. Axisymmetric Berger motion thus
preserves an exact U(1) selection rule. It can split levels and create
noncommuting evolution inside symmetry sectors, but it cannot by itself supply
an unrestricted three-channel wake.

The missing ingredient remains a nonuniform moving seam with transverse shape
harmonics whose action-selected amplitudes and phases break this common U(1).

## 4. Regular-center data do not determine the cap DtN map

Consider the reduced regular radial problem

\[
-u''+[\kappa^2+\varepsilon h(r)]u=0,
\qquad
u(0)=1,
\qquad
u'(0)=0,
\]

on \([0,L]\), with

\[
h(r)=\left(\frac rL\right)^2\left(1-\frac rL\right)^2.
\]

The profile vanishes at both endpoints. The unperturbed and perturbed problems
therefore share the same boundary potential value and the same regular-center
domain. Their DtN values are

\[
m(\varepsilon)=\frac{u_\varepsilon'(L)}{u_\varepsilon(L)}.
\]

The exact first variation at \(\varepsilon=0\) is

\[
\boxed{
m'(0)=
\frac{\int_0^L h(r)\cosh^2(\kappa r)\,dr}
     {\cosh^2(\kappa L)}>0.
}
\]

Hence two smooth interior profiles with identical endpoint data have different
Weyl m-functions and different child DtN maps.

This is the decisive cap result:

\[
\boxed{
\text{seam metric + tangential spectrum + regular center}
\not\Rightarrow
\text{unique child DtN map}.
}
\]

The cap warp factors and background fields must be obtained from the full
stationary action. Selecting a cap because its DtN sign or spectrum matches a
wanted particle result would violate the no-retuning rule.

## 5. Hindsight 20/20

### Validated

- Exact homogeneous SU(2) Dirac blocks are computationally available.
- The block construction reproduces the complete round spectrum.
- The first Berger zero mode occurs at stretch four in the \(n=1\) block.
- The frozen diagnostic Berger value is not at that crossing.
- A time-dependent Berger modulus gives genuinely noncommuting Dirac blocks.
- Berger axisymmetry preserves an exact fiber U(1).
- A regular-center condition does not uniquely determine the cap DtN map.
- The finite spinor nonzero-mode projector is explicit and stable.

### Invalidated

- Treating the round spinor spectrum as the physical anisotropic spectrum.
- Assuming that regularity at the cap center uniquely fixes the DtN map without
  solving the interior background.
- Treating one Berger modulus as a complete three-flavor mixing mechanism.
- Calling a finite spinor kernel projector the complete gauge-fixed projector.
- Choosing a cap-domain sign based on desired phenomenology.

### Reclassified

- Berger anisotropy is a genuine monodromy seed, but not the complete flavor
  source.
- The physical cap problem is a bulk stationary-background problem, not a
  boundary-condition preference.
- Zero-mode removal is partly computable in the spinor sector but remains a
  direct-sum gauge/metric/ghost/seam construction globally.

### Open

- cohomogeneity-one parent and child stationary solutions;
- regular cap warp factors selected by the unified action;
- common self-adjoint gauge-fixed domain;
- metric, gauge, ghost, seam, and collective zero-mode projectors;
- three transverse moving-seam shape derivatives;
- full relative heat-kernel and determinant control;
- action-selected nesting ratio and absolute scale;
- converged physical periodic BVP and blinded neutrino kill screen;
- physical masses, mixing matrices, couplings, widths, confinement, and all
  remaining completion observables.

## Completion status

BHSM is not physically complete. The exact next object is

`COHOMOGENEITY_ONE_ACTION_STATIONARY_PARENT_CHILD_BACKGROUND_WITH_REGULAR_CAP_WARP_FACTORS_COMPLETE_GAUGE_METRIC_GHOST_ZERO_MODE_PROJECTOR_AND_THREE_NONUNIFORM_MOVING_SEAM_SHAPE_DERIVATIVES_SOLVED_SIMULTANEOUSLY_IN_THE_NO_RETUNING_BVP`

Frozen predictions and official prediction logic are unchanged. USB remains
untouched.

## Mathematical references

- J. Kling and D. Schueth, *On the Dirac Spectrum of Homogeneous 3-Spheres*,
  Journal of Geometric Analysis 32, 275 (2022), especially the finite-block
  homogeneous Dirac construction.
- Y.-L. Fang, M. Levitin, and D. Vassiliev, *Spectral analysis of the Dirac
  operator on a 3-sphere*, Operators and Matrices 12 (2018), 501–527,
  including generalized Berger operator formulas and spectral asymmetry.
