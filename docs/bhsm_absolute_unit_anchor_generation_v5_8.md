# BHSM Absolute Unit-Anchor Generation v5.8

Status: `BHSM_ABSOLUTE_UNIT_ANCHOR_NOT_GENERATED`.

BHSM v5.8 audits whether the merged v5.4-v5.7 construction derives an absolute length `ell_star` or mass `M_star` from BHSM-native geometry, action, topology, boundary data, or a primordial compact state. It does not use measured particle masses, Standard Model scales, CMB/Hubble data, a Planck length, or cosmological fitting.

## Primordial Compact-State Candidate

The candidate initial state is a compact normalized Berger-Hopf boundary cell `Sigma_B` with collar or turning layer `[0,rho_star]`, orientation outward, and metric

```text
g(L) = L^2 g_hat
```

where `g_hat` is dimensionless and `L` is the global size modulus. The v5.7 scalar/topographic state is retained:

```text
sigma_scale = 1/2
M_BH/M_star = 1/2
R_BH/ell_star = 2
```

The white-hole-like language is interpretive: the mathematical object is an outward-oriented compact-to-expanding initial boundary configuration. It does not add an equation that fixes `L`.

## Scale-Modulus Audit

Under global rescaling,

```text
g -> lambda^2 g
L -> lambda L
ell_star -> lambda ell_star
M_star -> M_star/lambda
```

the current normalized action preserves a continuous size modulus. The reduced scale action is

```text
S_eff(L) = S_hat[sigma_scale=1/2]
dS_eff/dL = 0
d2S_eff/dL2 = 0
```

All positive `L` are equivalent in the current reduced model. `L=0` is excluded as degenerate geometry, and `L -> infinity` is a flat direction rather than a bounded finite minimum.

## Invariant Assessment

The serious candidates do not fix an absolute unit:

- `R_0=L R_hat` rescales with `L`.
- `V_0=L^3 V_hat` rescales with `L`.
- `A_0=L^2 A_hat` rescales with `L`.
- `rho_star=1` is a normalized coordinate convention.
- `lambda_n=lambda_hat_n/L^2` does not fix `L` without an absolute eigenvalue theorem.
- Hopf/topological numbers are dimensionless.
- regularity, finite action, and smooth turning-surface constraints are homogeneous in the present action.

Redshift can transport a BHSM-native initial scale after it exists. Redshift does not generate `ell_star`.

The CMB and relic matter are physical on-shell relics, not virtual. The only virtual/effective language applies to late-time boundary/topographic response memory.

## Propagation Status

Because `M_star` is not fixed, the following remain conditional maps rather than physical-unit outputs:

```text
D_phys = M_BH D_hat
L_gauge,phys = M_BH^2 L_gauge,hat
H_ST,phys = M_BH^2 H_ST,hat
G_phys = M_BH^-2 H_hat^-1
```

BHSM v5.8 does not derive particle masses by multiplying dimensionless entries by `M_BH`. The mass operator remains a separate theorem.

## Open Construction Target

The missing ingredient is a BHSM-native scale-modulus action source: a nonlinear backreaction theorem, absolute action quantum, boundary tension, absolute spectral eigenvalue, or primordial regularity condition capable of selecting a finite nonzero `L`.

Command:

```bash
python -m bhsm.interface absolute-unit-anchor-status --format markdown
```
