# BHSM v15.30 — compact trace response jet and locality audit

## Exact effective jet

For the identity round-`S7` trace,

```text
sigma_0 = chi/pi - sin(2 chi)/(2 pi) - 1/2,
a^2 U_0'(sigma_0(chi)) = (8/pi) sin(2 chi).
```

Series inversion at the median surface gives

```text
a^2 U_0'(sigma) = -8 sigma + (2 pi^2/3) sigma^3 + O(sigma^5).
```

The normalized trace therefore fixes the quadratic and quartic shape of the
effective material response in this class.  It does not fix the overall
sigma-action normalization.

## Formation mixed source

One fixed sigma-only potential cannot make every v15.9 trace profile
stationary.  At the common value `sigma=0`, the identity profile requires
zero force while a formed profile requires a nonzero force.  The leading
missing reduced source is exact:

```text
S_q(chi) = 4 q sin(chi) [11 cos(chi)^2 + 5]/(3 pi) + O(q^2).
```

This closes the effective response jet and localizes the missing interaction,
but it does not license insertion of `U_q(sigma)` into the parent action.
`q`, the cumulative trace, and the branchwise inverse are reduced/global
objects; a state-dependent action would be circular.

## Provenance boundary

The coefficient-free square `|d sigma-alpha_eta|^2/2` can enforce the trace
relation under fixed boundary data, but it has zero on-shell skin energy and
does not generate material tension.  A unique local, gauge-covariant
eta–sigma parent term with the required mixed source is not selected by the
present axioms.  The historical independent sigma field is therefore not yet
identified with the trace, and `FULL_BHSM_COMPLETE` remains false.

## Exact next dependency

```text
LOCAL_GAUGE_COVARIANT_PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_OF_THE_ETA_SIGMA_MIXED_SOURCE_WITH_EVENT_DOMAIN_ACTIVATION_AND_COMPLETE_CONSTRAINT_REDUCTION
```
