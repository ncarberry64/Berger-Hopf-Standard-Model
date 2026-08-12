# BHSM v15.31 — oriented normal-gradient eta–sigma completion candidate

## Local candidate

The exact v15.30 mixed source is generated at leading order by

```text
a^2 U_mix = H(sigma) d_chi(a^2 X_eta)
           = H(sigma) a N^A nabla_A(a^2 X_eta),
```

where the trace fixes

```text
H'(sigma_0(chi)) = -2[11 cos(chi)^2+5]/(21 pi),
H(0)=0.
```

There is no fitted coefficient.  The sigma variation is

```text
delta_sigma U_mix = H'(sigma) d_chi(a^2 X_eta),
```

and it reproduces the full required formation-to-material source through
order `q`.  Integration by parts gives the equivalent bulk expression

```text
-x H'(sigma) N.sigma_gradient - x H(sigma) div(N),
x=a^2 X_eta,
```

up to the explicit boundary divergence.  This uses the existing eta
invariant, material scalar, action-owned core/wall normal, and normal
expansion/extrinsic curvature.

## Orientation and zero limit

`H` is odd.  Under the physical conjugate branch

```text
sigma -> -sigma,  N -> -N,  q -> -q,
```

the normal derivative and `H` both reverse, so the density is invariant.  On
the unoriented identity branch `X_eta` is constant and the term vanishes.
This distinguishes a physical branch reversal from merely renaming the
normal convention.

## Claim boundary

This is the smallest regular local oriented completion found from the exact
source matching.  It is a candidate, not a recovered historical parent-action
term and not a uniqueness theorem over all local invariants.  Matching is
proved through `O(q)`; full nonlinear constraint continuation and event
activation of the independent sigma domain remain open.  BHSM is therefore
not yet complete.

## Exact next dependency

```text
PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_AND_FULL_NONLINEAR_CONSTRAINT_CONTINUATION_OF_THE_ORIENTED_NORMAL_GRADIENT_ETA_SIGMA_COMPLETION
```
