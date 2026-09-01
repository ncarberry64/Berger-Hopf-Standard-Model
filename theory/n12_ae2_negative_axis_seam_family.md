# N12 AE2 negative-axis seam family

Status: `AE2_TWO_SIDED_COVARIANT_SEAM_ENCLOSED_PARAMETRICALLY_ON_FULL_NEGATIVE_REAL_RESOLVENT_AXIS`.

The retained scalar/de Rham and factorized product-Dirac comparison theorems
are parametric in every neutral negative probe

`z=-kappa^2`, `kappa>0`.

For a scalar/de Rham channel on the certified child core,

`kappa tanh(kappa T)<=M_child<=K coth(KT)`,

where `K=sqrt(kappa^2+Vmax)`.  For a product-Dirac channel, every
zero-extended trial of length `0<L<=T` gives

`0<=M_child<=1/L+S+(S^2+kappa^2)L/3`.

Choosing

`Lstar=min(T,sqrt(3/(S^2+kappa^2)))`

is action-admissible and improves the high-probe bound to

`M_child<=S+(2/sqrt(3))*sqrt(S^2+kappa^2)`

whenever the unconstrained optimum lies inside the certified core.  Thus the
product bound grows as `O(kappa)`, not the `O(kappa^2)` artifact of using the
entire short core for every probe.

Unitary covariant pullback through `U_R` preserves the value intervals and
operator-norm first/mixed jet bounds.  Hence the corrected two-sided child
load is broadly enclosed on the full negative real resolvent axis.  The
parameter remains a neutral resolvent variable and is not momentum squared.

The pointwise low-probe jet majorants are intentionally not used to infer
infrared divergence; the retained compact-source Volterra/source-Dini theorem
already gives the canonical low-energy trace control.  The independent
high-energy trace-norm theorem also remains closed.

These broad comparison intervals do not decide the nonlinear heat spectral
trace or its sign, because they retain the unknown future load and are far too
wide.  The next object is an actual joint finite-history operator or a much
sharper trace-functional enclosure uniform over the action-owned reset fiber.
No interval midpoint may be promoted as a physical value.

`FULL_BHSM_COMPLETE=false`.
