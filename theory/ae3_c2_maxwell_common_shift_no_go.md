# AE3 current-C2 Maxwell common-shift no-go

The current parent gauge Hessian has the normalized lowest-mode residues

```text
Z_s=1,
Z_t=0.590609601652908.
```

Consider any finite correction proportional to the same local covariant
operator in the action-selected Lorentzian metric,

```text
delta S = (delta_Z/4) integral F_munu F^munu.
```

It shifts the temporal and spatial Maxwell coefficients equally:

```text
Z_t -> Z_t+delta_Z,
Z_s -> Z_s+delta_Z.
```

Therefore

```text
(Z_s+delta_Z)-(Z_t+delta_Z)=Z_s-Z_t
                            =0.409390398347092.
```

No finite common shift, including a conventional matter wavefunction
renormalization or a renormalization-scale change of that same `F^2` operator,
can produce one exact Maxwell residue. A large positive common shift can make
the ratio approach one, but cannot make it equal one at finite residue.

This theorem is deliberately scoped. It does not exclude curvature-dependent
form factors, boundary/Wentzell terms, collar terms, or a different
action-selected exterior/DtN domain. Such a contribution must satisfy

```text
delta_Z_t-delta_Z_s=Z_s-Z_t
                   =0.409390398347092
```

in the same normalization. The current action has not yet selected one of
those operator classes or supplied its coefficient, so the equation is a
target, not a fit prescription.

Consequently a common local matter-loop residue cannot unlock the photon
chain. The structural neutral charge direction survives, but a normalized
Lorentzian photon propagator, electroweak pole rotation, and muon `F2(0)` remain
downstream of a genuinely noncommon action/domain contribution.

Promoted:

- `CURRENT_C2_COMMON_COVARIANT_F2_SHIFT_NO_GO_DERIVED = TRUE`;
- the exact required anisotropic residue difference.

Not promoted:

- exclusion of every quantum or boundary repair;
- one Maxwell residue or a normalized photon propagator;
- electroweak pole mixing or the muon magnetic moment.

`FULL_BHSM_COMPLETE = FALSE`.
