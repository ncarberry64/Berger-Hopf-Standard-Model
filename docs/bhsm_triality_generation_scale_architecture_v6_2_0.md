# BHSM v6.2.0 triality, generation, and volume-scale architecture

Primary result:

`BHSM_TRIALITY_GENERATION_AND_VOLUME_SCALE_ARCHITECTURE_DERIVED_CONDITIONALLY`.

This sprint combines exact established representation theory and sphere
geometry with explicitly labeled BHSM identifications. It does not alter the
frozen numerical prediction set or fit masses, couplings, CKM, PMNS, or
cosmological data.

Independently reproduced secondary result:

`BHSM_SCALAR_WALL_LEADING_CUSP_ACTION_REPRODUCED`.

## Constructive classification

- **Adopted from established mathematics:** Spin(8) triality, the
  triality-fixed compact G2 subgroup, its SU(3) stabilizer branching, and the
  unit-sphere volume formula.
- **Adopted BHSM axiom:** the upper fold sheet is spacetime-facing, the lower
  sheet is core-facing, G2 acts as a consistency constraint, and the
  Berger-sphere deformation is the geometric translation of effective Higgs
  language.
- **Derived consequence:** exact family projectors, the no-double-counting
  Fourier intertwiner, conditional common branching, the color projector,
  the leading scalar-wall cusp, and exact volume identities.
- **Numerically validated:** the regulated cusp action on both coupled fold
  sheets and its mesh/tolerance convergence.
- **Needs empirical or global test:** sheet admissibility, physical
  representation normalization, transport observables, and scale-transfer
  factors.
- **Rejected by calculation:** a nine-generation product architecture and
  the flat-kink `27/35` target as a compact-cap completion theorem.

## Scalar-wall cubic cusp

The action diagnostic uses the Lorentzian reduced sign already fixed in
v6.1.5. It includes two identical caps and one B1 junction. With
`q5=Z5/kappa1=1`, `C_partial/kappa1=1/2`, and a maximally symmetric
four-volume regulator,

```text
Vol4(X)=Vol4(1) X^-2.
```

Dividing the complete action by `Vol4(1)`, the vacuum cap density is

```text
Gamma0(X)=3 ell-(3/4)sin(4 ell)-6/X,
ell=asin(X^-1/2).
```

The `-6X` term is the single oriented B1 term
`-12 C_partial X`. The exact critical expansion is

```text
Gamma0(2+d)-Gamma0(2)
  = d^3/16-3d^4/32+O(d^5).
```

The v6.1.7 fold gives `d=tau chi1 r+O(r^2)`. Its exact shape derivative
identity is

```text
nu1=chi1 u1'(rhoJ)^2/4=3 chi1^3/4.
```

Therefore

```text
Gamma_tau-Gamma_c
  = tau (nu1/12) r^3+O(r^4),

nu1/12=9.138890145035...
```

The coupled numerical cap solutions approach this coefficient on both
sheets as `r` decreases. Reversing the scalar sign leaves the action
unchanged. Euclidean continuation reverses the overall action sign but not
the cubic power, coefficient magnitude, sheet antisymmetry, or scalar-sign
degeneracy.

The compact scalar contribution relative to the vacuum cap at the same
`X,mu` begins at fourth order because branch solvability makes the quadratic
eigenvalue residual `O(r^2)`. The full analytic fourth-order coefficient
still needs the gravity, junction, domain, normalization, and constraint
projection. A fitted fourth-order number is not frozen.

The old flat-wall `27/35` target is retained only as an uncompactified
diagnostic. It is rejected as a compact-cap completion target because the
compact B1 problem has a leading geometric cubic cusp. The direct compact
moment remains

```text
C_direct=(G5/Z5) 21.690130229412.
```

## Spacetime sheet axiom

The following is adopted rather than inferred from the local cap equations:

```text
tau=+1: upper, spacetime-facing sheet
tau=-1: lower, core-facing sheet
```

The selection rule requires an enveloped, causal, propagating
four-dimensional observable sector. Locally the upper sheet moves to `X>2`
and the lower sheet to `X<2`, and their cusp signs are opposite. The present
two-derivative principal symbols have the same healthy signs on both sheets;
they do not prove the global selection. Global hyperbolicity,
normalizability, and observable-sector propagation are required tests. The
axiom is falsified if the upper sheet fails those tests or the lower sheet
independently supplies the complete observable sector.

## Berger–Higgs translation

The adopted geometric order parameter uses

```text
M_ab=L2^2 Q_ab+L1^2 P_ab,
P_ab=n_a n_b,
Q_ab=delta_ab-P_ab,
beta=log(L1/L2).
```

The orientation is global adjoint/twistor data:

```text
n^a=z^dagger sigma^a z,
z^dagger z=1,
z~exp(i theta)z.
```

It is not a globally fixed named coframe axis. Locally,

```text
Phi_BH=(v+h)z/sqrt(2),
h=f_beta(beta-beta_star).
```

For constant `f_beta` and origin `beta=0`, `v=f_beta beta_star`. The
connection mass matrix implied by an orientation stiffness `f_n^2` is

```text
(M_A^2)_ab=g^2 f_n^2(delta_ab-n_a n_b).
```

The direction parallel to `n` remains unbroken. It is a geometric U(1)
direction until the representation and connection normalization map is
supplied. The radial Hessian is

```text
m_h^2=V_eff''(beta_star)/f_beta^2.
```

The coefficients `f_beta` and `f_n` must come from the vertical
Einstein/action reduction. No measured electroweak normalization is used.

The existing neutral bulk `sigma` and Berger radial coordinate are not the
same linear mode: the singlet wall has `p1-p2=0` and no direct anisotropic
Berger source. They may mix nonlinearly, but renaming `sigma` as the Berger
amplitude would contradict the v6.1.5 source audit.

## Exact triality family projectors

Let

```text
F=8_v direct_sum 8_s direct_sum 8_c,
T: 8_v -> 8_s -> 8_c -> 8_v,
T^3=1,
omega^2+omega+1=0.
```

Over `Q(omega)`, define

```text
P_k=(1+omega^(-k)T+omega^(-2k)T^2)/3.
```

Exact cyclotomic arithmetic verifies

```text
P_i P_j=delta_ij P_i,
P_0+P_1+P_2=1,
T P_k=omega^k P_k.
```

No floating approximation is used in these algebra tests.

## No generation double counting

The triality sum is 24-dimensional, but each projector has an
eight-dimensional internal rank. The family label is the three-dimensional
`C3` factor. The existing Berger ladder is also a three-dimensional family
label:

```text
reference + excitation_1 + excitation_2.
```

The exact unnormalized `C3` Fourier matrix

```text
F_jk=omega^(-jk)
```

has inverse `F^-1_kj=omega^(jk)/3` and satisfies

```text
F E_k F^-1=P_k,
```

where `E_k` are the three diagonal Berger-slot projectors. Thus the two
triplications are identified, not multiplied. This is conditional on
choosing explicit triality maps between the automorphism-twisted
eight-dimensional carriers. It is not an ordinary Spin(8)-equivariant
identification without including the outer automorphism.

A nine-generation product construction is rejected.

## Triality-fixed G2 and SU(3)

The embedding convention uses the triality-fixed G2 subgroup of Spin(8).
All three twisted eight-dimensional carriers then restrict as

```text
8_v, 8_s, 8_c -> 1+7.
```

Choose the SU(3) subgroup stabilizing a unit imaginary-octonion direction:

```text
7 -> 1 + 3_(1,0) + conjugate(3)_(0,1),
8 -> 1 + 1 + 3 + conjugate(3).
```

The exact dimensions are `1+1+3+3=8`. For the G2 adjoint,

```text
14 -> 8_(1,1) + 3_(1,0) + conjugate(3)_(0,1).
```

BHSM adopts G2 as a consistency constraint, not a low-energy gauge group. In
the representation-ordered adjoint basis, the exact projector is

```text
P_color=diag(1_8,0_3,0_conjugate3),
P_coset=1-P_color.
```

The low-energy constraint is `P_coset A_G2=0`. This retains the SU(3)
connection and prevents six unexplained coset vectors from propagating.
Their dynamical mass generation is not claimed.

## Conditional particle-slot ledger

Each `P_k` is paired with the existing family-`k` mode in the neutral,
charged, color-upper, and color-lower ledgers. The two singlet channels are
paired with lepton-sector candidates and the `3+conjugate(3)` reality pair
with colored candidates. Existing Sp(1) upper/lower components and nested
geometric U(1) weights are recorded.

These remain candidate roles. A physical assignment still requires the
physical U(1) projection and normalization, chirality/localization action,
conjugation map, and anomaly check after the final representation map.
Dimension counting alone does not assign observed particle names.

## CKM versus PMNS transport

The structural architecture is

```text
V_CKM=U_u^dagger U_color U_d,
U_color=P exp integral A_SU3,

U_PMNS=U_l^dagger U_neutral U_nu.
```

Colored candidates transport through the retained SU(3) constraint
connection. Lepton candidates are color singlets, while the neutral sector
can accumulate S4 propagation-supported geometric phase. The two matrices
therefore do not arise from one unconstrained overlap operator.

This is a conditional structural separation. No numerical CKM or PMNS
matrix is fitted, and the existing frozen artifacts retain their status.

## Exact volume and scale anchors

From

```text
Vol(S^n)=2 pi^((n+1)/2)/Gamma((n+1)/2)
```

one obtains exactly

```text
Vol(S7)=pi^4/3,
Vol(S4)=8pi^2/3,
Vol(S3)=2pi^2,
Vol(S4)Vol(S3)/Vol(S7)=16,
3Vol(S3)=6pi^2.
```

Thus `6pi^2` is derived as a geometric denominator. The registry weights
`1:2:7` remain candidate spectral residues requiring a
representation/incidence theorem. Physical couplings additionally require
generator trace normalization, connection normalization, boundary transfer,
the surviving U(1) projection, and matching/RG transport.

The symbolic established-normalization correspondence is

```text
C4=Mbar_Pl^2/2,
tau_i I_i=1/g_i^2,
L_i^2=(Z_g/Z_A) 2/(I_i g_i^2 Mbar_Pl^2).
```

No equality `Z_g=Z_A` is assumed and no measured number is inserted. The
BHSM task is to derive `Xi_i=(Z_g/Z_A)/I_i`; no numerical absolute unit is
emitted here.

## Remaining tests

- Global causal and normalizable-spectrum comparison of the two fold sheets.
- Vertical reduction deriving `f_beta`, orientation stiffness, and the
  physical connection normalization.
- Physical U(1), chirality/localization, and anomaly closure for the slot
  map.
- Normalized transport actions for CKM and neutral propagation.
- Representation/incidence theorem for `1:2:7`.
- Gravity/connection transfer factors `Xi_i`.
- Gauge-invariant analytic fourth-order cusp coefficient.
- Full constraint-reduced mixed Hessian.

Historical v6.1–v6.1.7 artifacts retain their original status language.

## Established-input reference

The explicit order-three triality map, the fixed \(G_2\) algebra, and the
displayed \(SU(3)\subset G_2\) block were cross-checked against C. McRae,
[*Exploring Triality Explicitly: Convenient bases for SO(8), Spin(1,7), and
G2*](https://arxiv.org/abs/2502.14016) (2025). The paper is used only for
established representation theory. The family identification, color
constraint, and particle-slot interpretation remain BHSM constructions with
the qualifications stated above.
