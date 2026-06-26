# Neutrino Dirac-Majorana Basis and Scale Theorem

Phase Three-I audits whether the BHSM neutral kernel `K_nu` can be interpreted
as a physical neutrino mass matrix or production interaction.

## Finding

`K_nu` remains a BHSM boundary/operator source. PMNS charged-current target
labels may be used in collider-interface mode, but that does not promote
`neutral_operator_kernel_BH`.

A physical neutrino mass or interaction term requires:

- a physical basis map `U_nu`;
- a dimensional scale `Lambda_nu`;
- a Dirac or Majorana convention.

None of these gates is closed by existing artifacts.

## Status

```text
K_nu_status = BOUNDARY_OPERATOR_SOURCE_ONLY
basis_status = PARTIAL_FOR_PMNS_TARGET_LABELS
scale_status = OPEN
dirac_majorana_status = OPEN
promotes_neutral_kernel = false
feynrules_ready = false
ufo_ready = false
```

No empirical neutrino masses or PDG values are inserted.

