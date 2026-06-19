# PO-BH-68 - Weak Double Projection Bridge for `Z_virt^{u,2}`

Current public status: structural architecture integrated conditional; numerical closure open.

This surgical patch connects the actual PO-BH-67 source
`WEAK_DOUBLE_PROJECTION` to the PO-BH-66 two-door virtual-pair theorem. It does
not change frozen predictions, official predictions, mass-ratio outputs, CKM
outputs, PMNS outputs, neutrino outputs, or public prediction files.

## Weak Doublet Space

Define the weak doublet door space:

```text
V_weak = span{door_upper, door_lower}
```

with

```text
dim(V_weak)=2
```

Define the up-sector weak projector:

```text
P_u = diag(1,0)
```

so

```text
rank(P_u)=1
```

Therefore

```text
WEAK_DOUBLE_PROJECTION = rank(P_u) / dim(V_weak) = 1/2
```

## Connection To The Actual Source Path

PO-BH-67 localized the actual dressed-branch path:

```text
build_bhsm_dressed_v1_candidate
  -> pure_fiber_middle_up_rule()
  -> apply_virtual_dressing(model, (rule,))
```

The actual source rule is:

```text
sector = up_quarks
generation = middle
mode = (6,0)
(q,j) = (6,0)
Omega_u = 6
source = WEAK_DOUBLE_PROJECTION
factor = 1/2
```

Because the actual source name is `WEAK_DOUBLE_PROJECTION`, and this patch
identifies that source with the rank-one up projector on the two-dimensional
weak doublet door space, the applicability bridge is conditional but explicit:

```text
Z_virt_u2_applicability: DERIVED_CONDITIONAL
Z_virt_u2_dimension_ratio: DERIVED_CONDITIONAL
legacy_Z_virt_u2_numerical_candidate: SUPERSEDED_BY_WEAK_DOUBLE_PROJECTION_BRIDGE
Z_virt_u2_mass_fit_route: FORBIDDEN_AS_DERIVATION
```

## Guardrails

This bridge uses only the actual source path and weak-doublet projector
identity. It does not use observed quark masses, charm/top, up/top, CKM, PMNS,
neutrino data, measured alpha, or target ratios. It does not alter frozen or
official predictions. The public status remains exactly:

```text
structural architecture integrated conditional; numerical closure open
```

## Remaining Open Work

- derive the full virtual loop/threshold source;
- preserve the distinction between this conditional bridge and numerical
  closure;
- keep `rho_ch`, `eta_l`, `Pi_l`, `alpha_geom`, CKM numerical closure, PMNS
  numerical closure, and neutral/topographic suppression values on their
  existing open tracks.
