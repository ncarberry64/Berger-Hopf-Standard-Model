# AE3 family-hierarchy interface theorem

## Result

The presently assembled AE3 maps preserve every already-defined BHSM family
fiber, but their composition cannot derive the observed family mass
hierarchies.

The AE2 reset, AE3 enclosure restriction and smooth localization weight, and
the current-C2 lowest-Weyl quadratic/source piece all have the form

```text
A_nonfamily tensor I3.
```

Products, sums, adjoints, limits, and regulated functions of maps with this
factorization remain family-central. The retained locality and `C3`
equivariance theorem independently gives the same intersection:

```text
Diagonal(3,C) intersect Commutant(C3) = C I3.
```

Thus the current attachments commute with all three rank-one family
projectors and the cyclic family shift. They can carry a BHSM family/mode into
the local enclosure and onward to its existing Standard Model manifestation,
but a mass operator proportional to `I3` cannot have three distinct charged-
lepton singular values. This is a structural obstruction, not an unresolved
normalization.

## Exact missing interface

At least one action-owned returned operator on the current physical domain
must leave the family-central intersection. There are two algebraically
sufficient classes:

1. An action-selected `C3`-breaking but projector-local operator. The existing
   family fibers remain mass eigenstates, but their diagonal returned values
   become distinct.
2. A triality-changing intertwiner that remains `C3`-equivariant but is not
   local in the frozen family projectors. The mass eigenstates are then
   action-selected combinations of the existing fibers, and the manifestation
   map must be transported to that basis.

The examples in the machine certificate prove that each class can support
three distinct singular values. They are interface witnesses only; neither
example is inserted into the BHSM action. Current evidence selects neither
route, and no continuous family coefficient or measured mass is permitted as
an input.

The exact owner is therefore:

```text
ONE_ACTION_OWNED_FAMILY_NONCENTRAL_RETURNED_MASS_OPERATOR_VIA_EITHER_
ACTION_SELECTED_C3_BREAKING_OR_A_TRIALITY_CHANGING_INTERTWINER_ON_THE_
CURRENT_PHYSICAL_DOMAIN
```

This owner applies separately to the charged-lepton, up-quark, down-quark,
and neutrino sections. Only after the returned operators and their physical
poles exist can CKM/PMNS readouts be promoted.

`FAMILY_MASS_HIERARCHY_DERIVED=FALSE`, `CKM_PMNS_DERIVED=FALSE`, and
`FULL_BHSM_COMPLETE=FALSE`.

## Reproduction

```bash
python scripts/materialize_ae3_family_hierarchy_interface.py
python -m pytest tests/test_ae3_family_hierarchy_interface.py -q
```

The machine-readable result is
`artifacts/action_extension/BHSM_AE3_FAMILY_HIERARCHY_INTERFACE.json`.
