# BHSM v6.4.0 parent-action polarization, localization, and stability

## Primary result

`BHSM_GLOBAL_POLARIZATION_AND_PRINCIPAL_STABILITY_ARCHITECTURE_DERIVED_CONDITIONALLY`

The selected G2 reduction supplies an exact complex polarization on the
four-dimensional boundary, and the frozen P1 geometry supplies an exact
Berger splitting of the inherited Hopf connection coefficients. The
constraint-reduced tensor, connection, scalar, and first-order principal
sectors are healthy in a declared positive-coefficient domain.

The frozen parent action does not contain a first-order matter term. It
therefore does not derive the odd wall coefficient, does not dynamically
select the G2/SU(3) section, and does not fix every connection transfer or
normal-mode spectrum. Those facts prevent the stronger proposed
all-action-derived result.

## G2 complex polarization

For the established G2 cross product on the seven-dimensional carrier and a
unit vector `u`, define

`J_u(v)=u cross v`.

The exact cross-product identity is

`J_u^2=-I+u tensor u`.

Thus `J_u^2=-I` on `u`-perpendicular. With
`Q=I-u tensor u`,

`Pi_10=(Q-iJ_u)/2`,

`Pi_01=(Q+iJ_u)/2`.

The implementation verifies idempotence, orthogonality, completeness on the
six-plane, complex conjugation, and complex ranks three and three. Reversing
`u` exchanges the projectors. Scalar-wall sign reversal alone does not.

## Globalization and topology

Let

`E_7=P_G2 x_7 R^7`

over the selected M4 boundary. A unit section of its sphere bundle reduces
the G2 principal bundle to the SU(3) stabilizer of `u`. Since the bundle rank
is seven and the base dimension is four, the first section obstruction would
lie in `H^7(M4)`, which vanishes. A nowhere-zero section therefore exists on
the declared M4 base.

After the reduction, overlap transition functions lie in SU(3), preserve
`J_u`, and patch the two projectors covariantly. Complex conjugation exchanges
the `3` and `conjugate(3)` bundles, so the latter is antiparticle data rather
than an independent vectorlike copy.

This proves existence and compatibility, not dynamic selection. Extending the
section through the full bulk is conditional on extending the SU(3)
reduction; the four-dimensional obstruction argument alone does not prove
that extension.

The same polarization occurs on all three family projectors conditional on
the exact v6.2 triality isomorphisms carrying the common G2 reduction and
section. The family count remains three.

## First-order matter action

The symmetry-compatible candidate is

`S_F=integral sqrt|g| <Psi,[C_BHSM+M(sigma,beta,n)]Psi>`.

Its configuration space, Clifford bundle, inner product, Lorentzian adjoint,
and maximal-isotropic cut-domain condition are inherited from v6.3. It is a
BHSM-native first-order action and is not declared to be a physical bulk
Dirac parent law.

The lowest-order wall-odd representation-scalar term is

`y_sigma sigma Gamma_star`.

It is covariant, Hermitian for real `y_sigma`, family universal when the same
coefficient acts on `P_0,P_1,P_2`, compatible with `Y_BH`, and odd across the
wall. The even `y_beta beta` term cannot by itself produce a sign-changing
localization mass. A naked linear orientation `n` has no SU(3)-invariant
contraction and is rejected.

The frozen P1/B1 action has no `Psi` action, so `y_sigma` remains an
independent dimensionless primitive if this minimal extension is adopted.
Neither normalization nor the existing bosonic coefficients fixes it.

## Chiral normal mode

For

`sigma(rho)=sigma_0 tanh(rho/delta)`

and `nu=y_sigma sigma_0 delta>0`, the selected normal equation has

`f(rho)=N sech(rho/delta)^nu`,

where

`N^2=Gamma(nu+1/2)/(delta sqrt(pi) Gamma(nu))`.

The complete-line index is one when the asymptotic mass changes from negative
to positive. There is one normalizable selected-chirality profile and no
normalizable opposite profile. For `nu=1`, the implementation verifies unit
norm, vanishing odd-wall overlap, and
`integral sigma^2 |f|^2=sigma_0^2/3`.

This result applies to every selected slot and family only after adopting the
minimal first-order extension and its declared domain. It is not a derivation
of `y_sigma` from the frozen bosonic parent action.

## Connection localization and transfer

The exact representation traces remain

`I1_raw=10/3`, `I2=2`, `I3=2`, `eta_Y=3/5`.

The v6.0.9 P1 reduction gives the exact Hopf connection matrix

`K=8 pi^2 kappa1 diag(L2^4 L1,L2^4 L1,L2^2 L1^3)`.

Hence

`tau_nested/tau_transverse=(L1/L2)^2=exp(2 beta)`.

The geometric coefficients are equal in the round limit and split under
Berger deformation. They remain positive for positive
`kappa1,L1,L2`.

This derives a Sp(1)/nested-U(1) geometric split. It does not derive the SU(3)
color transfer, the physical boundary overlap, or equality of transfer
factors. No arbitrary localizing function is added, and the rejected `1:2:7`
trace pattern is not restored.

The physical dependency remains

`1/g_i^2=tau_i I_i`.

Algebra normalization, representation trace, geometric mode norm,
polarization, collar overlap, boundary matching, and RG transport remain
separate.

## Gravity normalization

In the same bookkeeping convention,

`C4=C_partial,intrinsic+Z_g N_g`.

Only after reduction may one impose the physical correspondence
`C4=Mbar_Pl^2/2`. The provisional intrinsic `C_partial`, bulk tensor transfer,
and connection transfers arise from distinct unresolved sources.
`Z_g=Z_A,i` is not assumed.

## Berger–Higgs kinetic and mass structures

For fields `(sigma,beta)`, the retained off-shell P1 shape metric gives

`G_sigma_sigma=Z_sigma`,

`G_beta_beta=(6/7)Z_Berger`,

`G_sigma_beta=0`

at `sigma=0`. The last result follows from the retained Z2 symmetry and
`p1-p2=0`, not from conflating the fields.

For orientation motion,

`Tr(M^-1 dM M^-1 dM)=8 sinh(beta)^2 |dn|^2`,

up to the positive reduction prefactor. Orientation stiffness is positive in
the Berger phase and vanishes in the round phase.

The retained scalar mass matrix is diagonal at this order, but both diagonal
signs remain coefficient-dependent and higher-order mixing is open. A unique
Higgs-like scalar eigenmode is therefore not claimed.

The conditional electroweak connection mass matrix in basis
`(W1,W2,W3,B)` has two equal charged eigenvalues, one massive neutral
eigenvalue, and exactly one neutral null direction proportional to
`g1 W3+g2 B`. This is the `Q_em` direction. The separate SU(3) block remains
unbroken. No measured W, Z, Higgs, or coupling value is used.

## Constraint-reduced spectrum

After removing lapse, shift, longitudinal gauge directions, matching
multipliers, and normal-coordinate gauge:

- the tensor principal kinetic terms are positive for
  `kappa1>0,C_partial>0`;
- transverse connection terms are positive when every `tau_i I_i>0`;
- scalar kinetic terms are positive for
  `Z_sigma>0,Z_Berger>0`;
- the first-order matter principal problem is symmetric hyperbolic with
  vanishing boundary flux on the declared maximal-isotropic domain.

These are principal-sector statements. Tensor normal modes, cap leakage,
junction bending, scalar mass signs, the complete connection boundary
spectrum, and the full coupled first-order spectrum remain unsolved. No gauge
zero mode is inverted in the Schur reduction.

## Spacetime branch

The upper branch is admissible in the tested positive-coefficient principal
sectors. The lower branch has the same retained local highest-derivative
matrices after consistent orientation tracking. Therefore:

`BHSM_LOCAL_PRINCIPAL_SYMBOLS_SHEET_SYMMETRIC`.

Local principal symbols do not uniquely select the upper sheet. The
spacetime-facing interpretation remains an adopted global envelopment axiom
pending global continuation and causal-orientation tests.

## Absolute scale and scalar-wall action

The refined symbolic relation is

`L_i^2=Xi_i 2/(g_i^2 Mbar_Pl^2)`,

with

`Xi_i=(Z_g/Z_A,i)/(N_geom,i I_i)`.

The Sp(1) and nested-U(1) geometric pieces are derived, while SU(3), boundary
overlaps, and relative `Z` factors remain independent. No numerical absolute
scale or mass is emitted.

The scalar-wall result

`Gamma_tau-Gamma_c=tau(nu1/12)r^3+O(r^4)`

with `nu1/12=9.138890145035` is preserved. The total order-`r^4`
coefficient and its fixed/moving-domain equality remain open.

## Next construction gate

`V6_4_0_FIRST_ORDER_PARENT_COEFFICIENT_CONNECTION_TRANSFER_AND_FULL_SPECTRUM_OPEN`
