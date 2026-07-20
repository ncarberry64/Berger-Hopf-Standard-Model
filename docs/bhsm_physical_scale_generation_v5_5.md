# BHSM Physical-Scale Generation v5.5

Primary result: `BHSM_PHYSICAL_SCALE_GENERATED_CONDITIONALLY`.

BHSM v5.5 extends the v5.4 unified symbolic action by isolating the scale
sector and testing the minimal viable sources of a physical mass/energy scale.
No measured particle mass, electroweak input, cosmology input, Standard Model
calibration, W calibration, CKM fit, neutrino limit, or rare-B observable is
used.

## Scale Inventory

The current action contains several objects that can carry scale information:

- boundary radius `R_BH`
- Berger squashing ratios
- collar coordinate `rho`
- metric normalization `h_rho`
- curvature invariants of `h_rho`
- normalized boundary volume
- scalar/topographic amplitudes
- symbolic potential coefficients
- kinetic and Hessian eigenvalues
- open running objects `Z_i(mu,rho)` and `rho_i(mu)`

The audit separates relative geometric data from absolute units. Mode numbers,
eigenvalue ratios, sector weights, dimensionless curvature, and normalized
volume are not physical mass scales without an explicit conversion mechanism.

## Candidate Assessment

### Geometric Radius

`M_BH proportional to 1/R_BH` is dimensionally coherent only after `R_BH` is
fixed. A free radius or a declared `rho_*` does not constitute scale generation.
This candidate remains a useful form but is not selected as the primary
mechanism.

### Scalar/Topographic Vacuum

The strongest current mechanism is a scale order parameter in the v5.4
scalar/topographic and scale sector:

```text
U_scale(sigma) = 1/4 beta_scale sigma^4 - 1/2 alpha_scale sigma^2
```

The stationary equation is:

```text
dU_scale/dsigma = beta_scale sigma^3 - alpha_scale sigma = 0
```

For symbolic conditions `alpha_scale>0` and `beta_scale>0`, the branches are:

```text
sigma = 0
sigma = +/- sqrt(alpha_scale / beta_scale)
```

The zero branch is unstable and the nonzero branch has Hessian
`2 alpha_scale`, so the nonzero magnitude is conditionally stable.

### Spectral Mechanism

Kinetic and Hessian spectra can propagate a scale:

```text
M_n^2 = M_*^2 lambda_n_hat
```

However, a dimensionless eigenvalue does not create `M_*`. The spectral route is
therefore a propagation map, not the primary scale source.

### Dynamical Transmutation

No artifact-backed beta function, determinant anomaly, or stationary effective
action exists in the current repository. Dimensional transmutation is not
claimed.

## Selected Mechanism

The selected architecture is:

```text
SCALAR_TOPOGRAPHIC_SCALE_VACUUM_WITH_UNRESOLVED_UNIT_ANCHOR
```

The generated dimensionless branch is:

```text
M_BH / M_* = sqrt(alpha_scale / beta_scale)
```

Equivalently:

```text
R_BH = ell_* / sqrt(alpha_scale / beta_scale)
M_* = hbar c / ell_*
```

`hbar=c=1` may be used as a unit convention, not as a BHSM prediction. The
absolute unit anchor `M_*` or `ell_*` remains open unless derived by a later
action theorem.

## Propagation Into BHSM

Once the symbolic scale exists, it can enter existing operators as:

- fermion operator: `D_phys = M_BH D_hat`
- gauge operator: `L_i,phys = M_BH^2 L_i,hat`
- scalar/topographic spectrum: `m_phi,n^2 = M_BH^2 omega_phi,n^2`
- boundary spectrum: `M_n^2 = M_BH^2 lambda_n_hat`
- charged current: dimensionful current normalization may use powers of
  `M_BH`, but `g_ch` remains open
- neutral response: stiffness and curvature maps may use powers of `M_BH`,
  but physical eV/GeV neutrino masses remain blocked
- propagators: `G_phys = M_BH^-2 H_hat^-1` after domain and zero-mode gates
  close

This propagation does not derive gauge couplings, fermion masses, neutral
eV/GeV masses, rare-B Wilson coefficients, CKM values, or full BHSM completion.

## Open Gates

- `OPEN_MISSING_ABSOLUTE_UNIT_ANCHOR`
- `OPEN_MISSING_SCALE_POTENTIAL_ACTION_SOURCE`
- `OPEN_MISSING_PHYSICAL_SCALE_GENERATION_FOR_NUMERIC_UNITS`
- `OPEN_MISSING_GAUGE_COUPLING_ACTION_ATTACHMENT`
- `OPEN_MISSING_ALPHA_I_ACTION_DERIVATION`
- `OPEN_MISSING_G2_BH_ACTION_SOURCE`
- `OPEN_MISSING_CKM_COEFFICIENT_VALUE_SOURCE`
- `CKM_EXPONENT_NOT_DERIVED`
- `OPEN_MISSING_NEUTRAL_SCALE`
- `OPEN_MISSING_NEUTRAL_ACTION_NORMALIZATION`
- `OPEN_MISSING_CHARGED_CURRENT_NORMALIZATION`
- `OPEN_MISSING_NEUTRAL_RESPONSE_NORMALIZATION`
- `OPEN_MISSING_NONLINEAR_UNIFIED_SOLUTION`
- `FULL_BHSM_NOT_COMPLETE`

## Claim Boundary

BHSM v5.5 conditionally generates a nonzero scale branch from the symbolic v5.4
scalar/topographic scale sector. It does not emit a numeric eV/GeV scale or
particle masses because the absolute unit anchor and coefficient provenance
remain open.

Command:

```bash
python -m bhsm.interface physical-scale-generation-status --format markdown
```
