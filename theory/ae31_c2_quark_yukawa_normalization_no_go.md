# AE3.1 quark Yukawa normalization non-identifiability

The current-C2 quark sector now has the frozen up/down family operators,
their exact scale-free response identities, the allowed intrinsic-M4 gauge
contractions, and the common left-handed charged-current kernel.  It does not
yet have the two scalar source variations that turn those response operators
into action-owned Yukawa operators.

Write the most general positive sector-normalized pair compatible with the
present diagonal response attachment as

```text
Y_u(c_u) = c_u J_u^dagger T_u R_u,
Y_d(c_d) = c_d J_d^dagger T_d R_d.
```

Every within-sector normalized eigenvalue is independent of its sector
constant:

```text
y_u,i/y_u,heavy = t_u,i/t_u,heavy,
y_d,i/y_d,heavy = t_d,i/t_d,heavy.
```

Consequently the Jacobian of all four nontrivial normalized shapes with
respect to `(log c_u,log c_d)` is the `4 x 2` zero matrix.  It has rank zero
and normalization nullity two.  A continuum of distinct `(c_u,c_d)` pairs
therefore gives exactly the same attached response shapes and the same
parameter-free sum rules.

Cross-sector information does not disappear:

```text
y_u,heavy/y_d,heavy = c_u/c_d.
```

That ratio changes across the indistinguishable family.  The current response
data therefore fixes neither the relative up/down normalization nor either
absolute normalization.

## Provenance exclusions

The charged-lepton coefficient has an explicit owner:

```text
sqrt(2) kappa_H tau^2 (beta_l tau / Tr P_l).
```

No matching current parent variation has been derived for the up and down
intrinsic-M4 LR--Higgs vertices.  Gauge invariance permits the two operator
classes but does not copy the charged-lepton number into them.

The historical `beta_u,beta_d,kappa_u,kappa_d` entries cannot fill this gap.
They are conditional family-slot bridge or boundary-matrix objects obtained
from a different functional variation.  The later Einstein--Cartan result
explicitly confirms that they are not canonical quark Yukawa coefficients.
Its auxiliary unit LR vertex also cannot supply a global normalization because
the retained zero mode is outside the global EC stationary action domain.
The middle-up factor `1/2` remains an unpromoted conditional dressing output.

The exact missing objects are the trace- and domain-fixed projections of

```text
P_u delta^3 S_parent/(delta bar(Q_L) delta H_tilde delta u_R) P_u,
P_d delta^3 S_parent/(delta bar(Q_L) delta H       delta d_R) P_d.
```

Only those action variations, or a proved equivalent operator identity, may
fix `c_u` and `c_d`.  Quark masses may test the result afterward but cannot
select it.

Promoted:

- `CURRENT_AE31_QUARK_YUKAWA_NORMALIZATION_NONIDENTIFIABILITY_DERIVED = TRUE`;
- normalization nullity is exactly two for current within-sector data;
- the missing parent variations are explicitly identified.

Not promoted:

- numerical `c_u` or `c_d`;
- action-owned up/down Yukawa or mass operators;
- physical quark poles or CKM mixing.

`FULL_BHSM_COMPLETE = FALSE`.
