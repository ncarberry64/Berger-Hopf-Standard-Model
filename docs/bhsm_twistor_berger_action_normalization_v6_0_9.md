# BHSM v6.0.9 Twistor--Berger Action Normalization

Primary result:
`BHSM_TWISTOR_BERGER_ACTION_NORMALIZATION_DERIVED_CONDITIONALLY`.

## Fixed scope

This sprint evaluates only the provisional Lorentzian P1 branch

```text
S_P1=(1/2) integral_M8 sqrt(-G)(kappa1 R-kappa0)+GHY+declared fields,
M8=R_t x S7.
```

P2 and P3 remain a separate correction ledger. The reduced `R_t x S4` base
is diagnostic, not observed spacetime.

## Physical measure and curvature

For `d sigma1=-sigma2 wedge sigma3` cyclically,

```text
Vol(S1)=4 pi L1,                 Vol(S2)=4 pi L2^2,
Vol(S3)=16 pi^2 L2^2 L1,        Vol(S4)=8 pi^2 L4^4/3,
Vol(CP3)=32 pi^3 L4^4 L2^2/3,   Vol(S7)=128 pi^4 L4^4 L2^2 L1/3.
```

The round convention bridge is `L4=L2=L1=R/2`, giving
`Vol(S7)=pi^4 R^7/3` and `R7=42/R^2`. Normalized Haar measure remains distinct:
`dnu_F=dmu_F/Vol(F)`.

The constant-modulus connection-metric curvature is

```text
R7=12/L4^2+2/L2^2-L1^2/(2L2^4)-(2L2^2+L1^2)/L4^4.
```

The reduced connection term is `-(1/4)K_ab F^a F^b`, with

```text
K=(kappa1 Vol(F)/2) diag(L2^2,L2^2,L1^2).
```

It is positive for positive `kappa1,L1,L2`. Canonical components obey
`A_can^a=sqrt(K_aa)A^a`, but anisotropic `K` is not one physical `Sp(1)` or
Standard Model gauge coupling.

## Multiplets, overlaps, and the tower

For normalized-Haar modes, a parent scalar coefficient reduces as

```text
Z_(J,m)=Z_parent Vol(F),
phi_can=sqrt(Z_parent Vol(F)) phi,
g_p,can=g_p I_p Z_parent^(-p/2) Vol(F)^(1-p/2).
```

Cubic Wigner overlaps are products of two `3j` symbols. Charge conservation,
triangle/parity rules, and common intermediate spins give exact cubic and
quartic selection rules. Forbidden channels vanish without tuning.

Above the retained scalar singlet, the exact minimal-scalar vertical gap is

```text
Delta_spec=min(1/(2L2^2)+1/(4L1^2), 2/L2^2),
```

with a channel crossing at `(L1/L2)^2=1/6`. For `E^2<Delta_spec`, tree-level
integration has `||O_H^-1|| <= 1/(Delta_spec-E^2)`. This is controlled only
when energy, source, modulus-rate, connection-curvature, and amplitude ratios
are small. Otherwise the infinite tower remains necessary. No one-loop result
is claimed.

## Moduli and the real blocker

For `u=(ln L4,ln L2,ln L1)`, the ADM/DeWitt matrix is

```text
[[-12,-8,-4],[-8,-2,-2],[-4,-2,0]].
```

In volume/shape variables its volume direction is negative and
lapse-constrained, while the two-dimensional shape block is positive. A full
canonical reduction still needs a declared Weyl frame.

The fixed-lapse spatial potential has two critical ratios:

```text
round:           L1/L4=L2/L4=1,       (kappa0/kappa1)L4^2=15/2,
Jensen-squashed: L1/L4=L2/L4=1/sqrt5, (kappa0/kappa1)L4^2=27/2.
```

The round point is a fixed-lapse minimum and the squashed point a saddle.
Neither is a Lorentzian P1 vacuum: a positive-curvature `R_t x S7` product
cannot satisfy both the lapse/tt and spatial Einstein equations without an
explicit supporting stress background. The declared-field stress has not
been solved. Both lengths also depend on the unfixed primitive ratio
`kappa1/kappa0`, so no absolute unit is generated.

## Outcome

Derived: physical measure, off-shell P1 curvature, connection and canonical
scalar normalization, overlaps, selection rules, spectral gap, conditional
tower bounds, and fixed-lapse stability classification.

Conditional/open: sigma is only a declared-field singlet candidate; the
parent-to-v5 bridge is incomplete; the Lorentzian stress background, fermion
spectrum, physical gauge/particle map, primitive selection, and absolute unit
remain open.

`FULL_BHSM_NOT_COMPLETE`.

Recommended continuation:
`bhsm-p1-lorentzian-background-constraint-closure-v6-0-10`.
