# BHSM v6.3.0 particle, chirality, and anomaly normalization

## Result

Primary status:
`BHSM_CHIRAL_PARTICLE_AND_CONNECTION_ARCHITECTURE_DERIVED_CONDITIONALLY`.

This sprint constructs a conditional three-family chiral connection
architecture from the v6.2 triality carriers. It derives an exact residual
U(1) operator, electromagnetic generator, one- and three-family anomaly
ledgers, and representation traces. It does not establish a physical Dirac
parent law, measured particle masses, measured couplings, or an absolute
unit.

## Representation map

Each triality family carries the v6.2 restriction
`1+1+3+conjugate(3)`. A boundary complex polarization selects `1+3`; the
conjugate polarization is antiparticle data rather than a second set of
particles. Without this choice, `3+conjugate(3)` cannot serve as the two weak
components of one chiral color triplet.

Boundary activity and orientation grades then organize an active
`(3,2)+(1,2)` sector and inactive left-Weyl conjugate singlets. The charged
family has 15 complex slots. An anomaly-neutral singlet can complete 16 slots,
but its presence does not derive a neutrino mass. The same map is repeated on
the three exact triality projectors; the Berger ladder is its Fourier basis,
not another family factor.

The complex polarization is an explicit domain choice. Its derivation from
the global associated bundle remains open.

## BHSM-native chirality

The mathematical first-order collar operator is

`C_BHSM=-i Gamma_n nabla_n+Gamma_* m_B(x)+C_tangential`.

With Hermitian Clifford matrices, define
`K=i Gamma_n Gamma_*` and `Pi_+=(1+K)/2`. On the complete collar the operator
has its ordinary Sobolev self-adjoint domain. On a cut collar, the local
maximal-isotropic boundary condition removes the complementary trace and
satisfies `Pi_+ Gamma_n Pi_+=0`.

For an odd wall profile with opposite asymptotic signs, one `K=+1` normal
profile is square-integrable and the `K=-1` solution is not. The representative
`m_B=tanh(x)` profile is `sech(x)/sqrt(2)` and has unit norm. This is a
conditional localization theorem for the displayed BHSM-native action. It is
not an assumption of a physical bulk Dirac law.

## Residual U(1) and electromagnetism

In the standard convention `Q_em=T_n+Y_BH`, the exact commuting operator is

`Y_BH=-I/2+(2/3)P_C+S_sigma/2-(P_w S_sigma)/2`.

It equals one half of the older doubled-hypercharge ledger. The nested U(1)
integer alone is insufficient because it does not distinguish color and
boundary activity. With `Y(Phi)=1/2`, the lower vacuum component is neutral,
and the surviving generator agrees exactly with the boundary charge
operator.

No continuous U(1) is supplied by the G2 centralizer of the retained SU(3);
the residual U(1) therefore remains a boundary connection whose parent
normalization must be action-derived.

## Exact anomaly ledger

For the left-Weyl multiplets
`Q_L, u_c, d_c, L_L, e_c` and optional neutral `nu_c`, exact rational
arithmetic gives

- `SU(3)^3: 2-1-1=0`;
- `SU(3)^2 U(1)=0`;
- `Sp(1)^2 U(1)=0`;
- `U(1)^3=0`;
- `gravity^2 U(1)=0`.

There are four weak doublets per family after color multiplicity, so the
global Sp(1) parity is even. Three families have twelve doublets and all local
coefficients remain zero. The optional neutral singlet changes none of these
results.

## Connection normalization and the 1:2:7 test

The representation traces are

`I1_raw=10/3`, `I2=2`, `I3=2`, and `eta_Y=3/5`,

so the canonically normalized abelian trace is also `2`. The raw integer ratio
is `5:3:3`, and the normalized ratio is `1:1:1`. Consequently:

`BHSM_1_2_7_CANDIDATE_REJECTED_BY_REPRESENTATION_TRACE`.

The 1:2:7 pattern can survive only if a separate geometric or localization
transfer is derived from the action. It is not a representation-incidence
theorem.

## Family mass and absolute scale

The exact family operator is

`M_f=sum_k m_fk P_k+M_mix`,

with `M_mix` required to commute with every gauge representation projector.
The triality and Berger descriptions are related by the exact discrete
Fourier map. Existing mode ledgers and frozen dimensionless ratio screens are
attached read-only; they are not used as derivation inputs. No absolute mass
is derived.

For each retained connection,

`Xi_i=(Z_g/Z_Ai)/(N_geom_i I_i)`,

and a symbolic length can be written
`L_i^2=2 Xi_i/(g_i^2 Mbar_Pl^2)`. The action-derived transfer factors are
still open, so no numerical length, mass, or coupling follows.

## Scalar-wall ledgers

At the retained v6.2 truncation, the singlet wall amplitude and Berger radial
mode remain distinct quadratic coordinates because `p1-p2=0`. Higher-order
mixing is open. The order-`r^4` action decomposition and constraint-reduced
mixed Hessian architecture are recorded, but their full coefficients,
fixed/moving-domain comparison, spectrum, and one-light-scalar question are
not closed.

## Claim boundary

Derived:

- exact U(1), electromagnetic, anomaly, and representation-trace ledgers;
- the conditional collar zero-mode theorem for the displayed operator;
- a gauge-compatible three-projector family mass architecture;
- rejection of 1:2:7 as a representation-trace ratio.

Conditional:

- physical interpretation of the retained SU(3), Sp(1), and U(1) connections;
- the global complex polarization;
- the odd collar mass coupling and boundary domain;
- all scale-transfer factors.

Open:

- parent-action derivation of the polarization and first-order coupling;
- a complete global no-fourth-family index theorem;
- observed particle identification and measured spectra;
- full order-`r^4` projection and the complete constrained mixed Hessian.

No frozen prediction or official prediction logic is changed.
