# AE3 same-C2 Lorentzian gauge/ghost frequency Hessian

## Result

The same-action, same-background continuous-frequency quadratic gauge/ghost
operator is now derived at the current `C2` enclosure.  It does **not** yield
one Lorentzian Maxwell residue on the retained smooth parent trace domain.
The mismatch is recorded without a field rescaling, fitted coefficient, or
metric-cone adjustment.

The source is the owned parent term

```text
S_A = (K_F5/4) integral_M5 W Tr_16(F_MN F^MN),
K_F5/K_G5 = R_F^2/2,
W = (1-4 sigma^2)(1+X_eta^3).
```

At a current-C2 frozen slice let `r_b=R4`, `rho=2 chi`, and
`r(rho)=r_b sin(rho)`.  For a transverse boundary mode of level `n`, the
regular radial extension satisfies

```text
u'' + (cot(rho) + partial_rho log W) u'
    - n^2/sin(rho)^2 u + q^2 u = 0,
q^2 = (omega r_b)^2.
```

This is a real continuous parameter near `omega=0`; no periodic-cycle
frequency is used.  With `u(pi/2)=1`, its on-shell DtN Hessian is

```text
H_T(omega)/K_F5 = N_T(q^2)/r_b,
N_T(0) = integral W sin(rho)|u'|^2
       + n^2 integral W |u|^2/sin(rho),
-partial_(q^2) N_T(0) = integral W sin(rho)|u|^2.
```

For the lowest current coexact mode, the v16.03 level-zero curl eigenvalue
`+2` is the transverse radial level `n=2`.  The AE3-weighted regular extension
gives

```text
N_T(0)                                      = 1.67955783202127
-partial_(q^2) N_T(0)                      = 0.247990745530776
electric / magnetic radial-weight ratio    = 0.908932991228275
Z_t / Z_s (complete lowest-mode DtN ratio) = 0.590609601652908
```

The last number is strictly below one.  The positive radial-gradient energy
in `N_T(0)` makes the complete DtN mismatch larger than the already strict
electric/magnetic weight mismatch.

## Constraint and ghost sector

The temporal and longitudinal Maxwell coordinates are assembled before the
BRST quotient.  In `(A_0,phi_L)` coordinates their electric block has the
exact gauge null vector `(-i omega,1)`.  A BRST-exact gauge-fixing functional
produces its Faddeev--Popov operator by differentiation along that same null
direction.  Thus the two real unphysical bosonic degrees and one complex
ghost carry weights `+2` and `-2` and cancel on the physical quotient.

This reuses the v16.03 coexact/longitudinal split.  The historical v16.04
periodic first-frequency response is not substituted for the current-C2
continuous-frequency derivative.  Gauge fixing changes neither `Z_t` nor
`Z_s`, so BRST closure cannot repair their mismatch.

## Why the residues fail to match

The obstruction is action- and domain-local:

- electric curvature has radial weight `W R_F r`;
- spatial magnetic curvature has radial weight `W R_F/r`;
- the smooth regular trace domain also contributes positive radial-gradient
  DtN energy;
- `r<r_b` on every interior set of positive measure.

Consequently a nonzero smooth bulk trace obeys

```text
Z_t/Z_s <=
  [integral W sin(rho)|u|^2] /
  [integral W |u|^2/sin(rho)] < 1.
```

No independent `Z_A`, `g`, `g'`, `alpha`, residue, or cone adjustment is
introduced.  An action-derived nonsingular boundary/Wentzell contribution or
another existing-parent domain mechanism would have to remove the mismatch
before electroweak neutral mixing can be promoted.

Therefore

```text
CURRENT_C2_LORENTZIAN_GAUGE_GHOST_FREQUENCY_HESSIAN_DERIVED = TRUE
CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED                = FALSE
CURRENT_C2_NORMALIZED_PHOTON_PROPAGATOR_DERIVED              = FALSE
FULL_BHSM_COMPLETE                                           = FALSE
```

## Reproduction

```bash
python scripts/materialize_ae3_c2_lorentzian_gauge_ghost_hessian.py
python -m pytest tests/test_ae3_c2_lorentzian_gauge_ghost_hessian.py -q
```

The machine-readable result is
`artifacts/action_extension/BHSM_AE3_C2_LORENTZIAN_GAUGE_GHOST_FREQUENCY_HESSIAN.json`.
