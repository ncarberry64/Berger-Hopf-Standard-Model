# BHSM v6.7.0: boundary matter dynamics and neutral response

Primary result:
`BHSM_BOUNDARY_MATTER_VARIATION_DERIVED_CONDITIONALLY_DOMAIN_AND_NEUTRAL_RESPONSE_OPEN`.

This sprint starts from protected `main` merge commit
`134cb35ce20b31d5eb59fa43ec8bf49ec4fc0ea1`. That commit merged PR #166
without rebasing, squashing, force-pushing, or deleting its scientific branch.
The v6.6 scientific commit
`2657962928826e0cb74c56a1a6170cc8f07d7f04` remains in the ancestry.

## Result in one paragraph

The adopted v6.6 boundary invariant can be varied consistently. It supplies
matter and adjoint equations, a scalar-wall source, representation currents,
a minimal boundary stress tensor, and functional Berger, polarization, and
junction sources. Canonical normalization leaves `y_sigma` as one explicit
dimensionless primitive. The Green boundary form is also explicit, but the
present action contains no projector, unitary endpoint map, APS cut, or bag
angle that chooses one self-adjoint junction domain. On the reduced normal
problem the admissible maximal-isotropic domains therefore form a `U(1)`
family. Using the actual nonlinear v6.1.7 upper and lower B1 cap profiles, a
declared diagnostic domain has one zero mode and a positive compact gap, with
finite-difference and shooting agreement. The available minimal light sector
has three degenerate zero modes and no light-heavy coupling, so its Schur
complement is zero: it produces neither a nontrivial `K_prop` nor a relative
`L/E` phase. This is a constructive null result, not a fitted phenomenology.

## Adopted action and coefficient status

The frozen working action is

```text
S_v6.7 = S_P1 + S_GHY + S_B1 + S_F,partial,

S_F,partial
  = integral_M4 sqrt(-h)
    <Psi,[C_BHSM + y_sigma sigma Gamma_star]Psi>.
```

`S_F,partial` is an adopted BHSM action invariant. It is not derived from
P1, GHY, B1, FR topology, or a higher-dimensional parent action. The kinetic
coefficient of `C_BHSM` is canonically normalized to one. A rescaling of
`Psi` changes the kinetic term, inner product, currents, and scalar source
together, so it cannot remove the relative coefficient `y_sigma` after that
normalization. This sprint introduces no additional dimensional scale and no
sector-dependent Yukawa parameter.

The declared working conventions are Lorentzian signature `(-,+,+,+)` on
M4, outward cap normal with separately tracked junction orientation,
boundary measure `sqrt(-h) d4x`, and normalized cap measure
`a(rho)^4 d rho`. Three triality projectors carry the same `y_sigma`.

## Independent variation

Treating `Psi` and its adjoint as independent variables gives

```text
(C_BHSM + y_sigma sigma Gamma_star) Psi = 0,

barPsi (C_BHSM^adj
        + y_sigma sigma Gamma_star^adj) = 0.
```

The scalar source derived from the adopted invariant is

```text
J_sigma = y_sigma <barPsi,Gamma_star Psi>.
```

It has the wall parity required by the scalar equation. Equal occupation of
the three triality copies gives a factor three; occupation itself is not
fixed. Consequently, a profile or fold shift is possible but its coefficient
is not numerically derived.

Connection variation gives the representation currents

```text
J_SU3^(mu,a) = <barPsi,Gamma^mu T_SU3^a Psi>,
J_Sp1^(mu,i) = <barPsi,Gamma^mu T_Sp1^i Psi>,
J_U1^mu      = <barPsi,Gamma^mu Y_BH Psi>.
```

Their covariant conservation is conditional on the matter equations and the
declared connection representation. The existing charge and anomaly ledgers
are preserved. No full low-energy G2 current is introduced.

Metric variation contains the symmetric kinetic stress, measure variation,
spin-connection variation, and the wall term. Schematically,

```text
T_F,munu
 = (i/4) barPsi Gamma_(mu <->D_nu) Psi
   - h_munu L_F
   + declared C_BHSM improvement terms.
```

It enters the B1 junction equation. Normal displacement also couples through
`T_F^{mu nu} K_mu nu`, scalar response, and variation of the junction domain.
These are action-level source functionals; their numerical shift cannot be
closed until the complete `C_BHSM`, occupied state, and domain are fixed.

Variation with respect to the Berger field and polarization section is
functional:

```text
delta_beta S_F
 = <barPsi,(partial_beta C_BHSM)Psi>
   + (partial_beta ln measure) L_F,

delta_u S_F
 = (I-u tensor u)
   <barPsi,(delta_u C_BHSM)Psi>.
```

The explicit wall mass has no direct beta dependence. A numerical Berger or
polarization source must not be invented without the missing operator terms.

## Green form and self-adjoint domains

Integration by parts for a first-order operator produces a boundary Green
form

```text
B(phi,psi) = <phi, J_n psi>_junction.
```

For the reduced normal signature-`(1,1)` model used by the deterministic
audit,

```text
J_n = diag(1,-1).
```

A maximal isotropic line can be represented by

```text
v_theta = (1, exp(i theta))/sqrt(2),
v_theta^dagger J_n v_theta = 0.
```

Thus the reduced self-adjoint extensions form a `U(1)` family. The matter
action determines the Green form but supplies no junction projector, endpoint
unitary, APS spectral cut, or bag angle. It therefore does not select a
unique member of that family.

This distinction follows the standard theory of first-order elliptic
boundary problems and self-adjoint Dirac-type extensions:

- [Bär and Ballmann, boundary value problems for elliptic first-order operators](https://arxiv.org/abs/1101.1196)
- [Bär and Bandara, boundary value problems for general first-order elliptic operators](https://arxiv.org/abs/1906.08581)
- [Brüning and Lesch, self-adjoint boundary conditions for Dirac-type operators](https://arxiv.org/abs/math/9905181)
- [Djakov and Mityagin, one-dimensional Dirac operators with regular boundary conditions](https://arxiv.org/abs/1108.0344)

The proof-qualified domain result is
`BHSM_BOUNDARY_DOMAIN_REMAINS_ONE_ADDITIONAL_ACTION_AXIOM`.

## Actual nonlinear B1 cap spectrum

The sprint imports the nonlinear v6.1.7 continuation solutions rather than a
`tanh` surrogate. For each fold sheet and scalar sign it reconstructs

```text
a(rho), sigma(rho), cap length, junction position, and curvature.
```

On that actual profile it tests the staggered rectangular operator

```text
A = d/d rho + y_sigma sigma_B1(rho)
```

with a declared maximal-isotropic reduced domain. The rectangular index is
one. Its selected chirality has one zero mode; the opposite block has none.
Both upper and lower cap profiles have a positive first massive level in the
tested domain.

The squared-partner cross-check solves

```text
A A^dagger
 = -d^2/d rho^2 + m(rho)^2 + m'(rho)
```

with the corresponding declared endpoint conditions. Mesh refinement is
monotone in the first gap, and the first three massive levels agree with the
shooting calculation at the documented diagnostic accuracy.

This is an actual-profile spectral diagnostic, but it is not the complete
physical B1 spectrum. Missing pieces include the full angular Clifford
operator, curvature and spin-connection terms, Berger and polarization
terms, and the junction-domain term selected by an action. Determinants and
spectral actions also require an explicit domain and regularization; standard
heat-kernel machinery does not choose them:

- [Vassilevich, heat-kernel expansion user’s manual](https://arxiv.org/abs/hep-th/0306138)
- [Fukaya et al., domain-wall fermions and the APS index](https://arxiv.org/abs/1710.03379)
- [Fukaya et al., physicist-friendly reformulation of the APS index](https://arxiv.org/abs/1910.01987)
- [Trefethen, *Spectral Methods in MATLAB*](https://people.maths.ox.ac.uk/trefethen/pdetext.html)

Both diagnostic sheets remain regular and admissible. Their gap difference
does not select a global spacetime-facing branch.

## Family and vectorlike classification

For the declared domain, the normal operator has one selected zero mode and
no near-zero opposite-chirality partner. This remains domain conditional; it
is not a global no-doubling theorem.

Tensoring the selected mode with the three triality projectors produces three
identical copies. Family universality is thereby preserved. Neither FR
topology nor this repeated spectrum proves that no additional family sector
exists in the complete operator.

## Neutral Schur reduction

Write a Hermitian compact operator in light-heavy blocks:

```text
H =
  [ H_LL  H_LH ]
  [ H_HL  H_HH ].
```

For spectral parameter `lambda`, the Feshbach-Schur reduction is

```text
H_eff(lambda)
 = H_LL
   - H_LH (H_HH-lambda)^(-1) H_HL.
```

The construction and its Hermiticity are standard:

- [Dusson, Sigal, and Stamm, the Feshbach-Schur map and perturbation theory](https://arxiv.org/abs/2105.02058)

In the available minimal BHSM operator the retained light block consists of
three degenerate zero modes, and no representation-allowed
propagation-activated light-heavy coupling has been derived. Therefore

```text
H_LL = 0,
H_LH = 0,
K_prop,light = 0.
```

The Schur correction vanishes. A nonzero Hermitian matrix could be inserted
symbolically, but that would not be a derivation.

The massive transverse compact eigenvalues are constant vacuum spectral
levels. If they are propagated directly, they have the operational role of
mass-squared. Relabeling them “geometric” does not make them a
propagation-supported response. The minimal zero mode has no rest pole, but
also no relative neutral phase. Thus the adopted action remains insufficient
to settle the broader zero-rest-mass doctrine.

The proof-qualified neutral result is
`BHSM_NEUTRAL_PROPAGATION_RESPONSE_NOT_GENERATED_BY_AVAILABLE_MINIMAL_OPERATOR`.

## Neutral eigenbasis and polarization

Because the three retained light modes are degenerate, the neutral
eigenbasis is not unique. The structural identity

```text
U_PMNS = U_l^dagger U_neutral U_nu
```

is retained, but no PMNS matrix is fitted or inserted.

The available normal spectrum is independent of the `G2/SU3` polarization
section. A finite determinant diagnostic is consequently flat in that
section, with zero tangent Hessian and degenerate `u` and `-u`. This does not
show that the full `C_BHSM` determinant is flat; its polarization dependence
has not yet been constructed.

## Connection, scalar, and fold forward links

A normalized constant-profile overlap equals one and generates no
tree-level nonuniversal connection correction. It does not restore the
earlier `1:2:7` representation trace ratio as a physical coupling theorem.

The scalar-Berger kinetic block remains positive in the declared symbolic
coefficient domain, its Hessian is symmetric, and the `Q_em` null direction
is preserved. The physical matter-corrected Schur complement stays open.
No equality `Z_g=Z_A` is assumed.

The scalar-wall cusp

```text
Gamma_tau - Gamma_c = tau A r^3 + O(r^4),
A = 9.138890145035
```

is preserved. The classical zero-mode matter action vanishes on shell in the
minimal diagnostic. Occupation and determinant terms remain
domain/regularization dependent, so no total order-`r^4` coefficient is
claimed.

## Forward diagnostic

The preregistered code-level observable is

```text
R_gap
 = lambda_1,upper / lambda_1,lower
 = 1.03426465747
```

for `r=0.01`, `q5=1`, `G5/Z5=1`, `y_sigma=1`, 321 grid points, and the
declared diagnostic domain. It uses no measured input and is not fitted. It
is coefficient-, discretization-, and domain-dependent, so it is not a
physical prediction. Its regression tolerance is `5e-4` under the recorded
setup.

## Classification

Derived:

- independent matter and adjoint Euler-Lagrange equations;
- scalar and representation-current source functionals;
- minimal metric stress and Green boundary form;
- the reduced `U(1)` family of maximal-isotropic domains;
- the minimal light-heavy Schur reduction.

Numerically validated:

- upper/lower diagnostics on the nonlinear v6.1.7 B1 cap profiles;
- one selected zero mode and a positive compact gap;
- mesh convergence and finite-difference/shooting agreement;
- the declared sheet gap-ratio regression.

Rejected:

- unique domain selection by the present adopted invariant;
- a nontrivial `K_prop` from the available minimal light sector;
- dynamic polarization from the available normal spectrum;
- global branch selection by the diagnostic gap difference.

Conditional or still requiring new construction:

- the adopted boundary matter invariant and primitive `y_sigma`;
- the complete covariant `C_BHSM`;
- an action-selected junction domain;
- occupation and determinant prescriptions;
- propagation-activated light-heavy coupling;
- the full constrained matter/geometry spectrum;
- dynamic polarization, absolute scale, and empirical confrontation.

## Reproduction

```bash
python scripts/materialize_boundary_matter_dynamics_neutral_response_v6_7_0.py
python -m pytest -q tests/test_bhsm_boundary_matter_dynamics_neutral_response_v6_7_0.py
python -m bhsm.interface boundary-matter-neutral-response-status --format markdown
```

Active next construction:
`V6_7_0_EXPLICIT_C_BHSM_JUNCTION_DOMAIN_AND_PROPAGATING_HEAVY_MODE_COUPLING_REQUIRED`.
