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

The harmonic-energy audit reopens the origin of a noncentral observable without
changing this result. Pulling the already-stored Berger scalar eigenvalues
back through the family/mode labels gives a diagonal noncentral spectral
stiffness. It is not part of the family-blind dynamic composition above.
However, on the one common current-C2 radius its positive monotone energy
orders `(0,0)` below the excited modes, whereas the frozen ledger calls
`(0,0)` the heaviest slot. Its zero-mode displacement is also zero. The
spectral seed is therefore real, but it is not the missing physical mass
operator.

The separate historical Hopf-base branch is also retained: its decreasing
heat-semigroup weight `exp[-L/(4 pi)]` has the correct frozen role ordering and
uses no lepton mass input. It remains a conditional corpus candidate because
its response time, scale/lift, insertion, and equivalence to the v14.54
parent-relative mass contract have not been attached to current AE3 C2.

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

The exact owner is now narrower:

```text
ONE_SAME_CURRENT_C2_NORMALIZED_MANIFESTATION_MAP_INTO_AN_ACTION_ENERGY_
DOMAIN_PLUS_THE_COMPLETE_PARENT_RELATIVE_ENERGY_OR_FERMION_POLE_FUNCTIONAL_
AND_ANY_ACTION_SELECTED_STATE_DEPENDENT_LOCALIZATION_SCALE
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
The dedicated no-fit test is
`artifacts/action_extension/BHSM_AE3_FAMILY_HARMONIC_ENERGY_PULLBACK_AUDIT.json`.
