# AE3 current-C2 coexact gauge form shape

## Derived finite-core form

The exact homogeneous `S3` curl theorem gives the level-zero coexact spectrum

```text
curl_0 = (+2,+2,+2),
coexact dimension = 3,
longitudinal dimension = 0.
```

On the actual nonuniform C2 finite-core geometry, each component therefore
has the form

```text
q[a_T] = integral dt (|partial_t a_T|^2 + 4 R4^-2 |a_T|^2).
```

Using the same birth-retained, far-core-Dirichlet finite elements as the
existing C2 descriptor produces three identical real symmetric generalized
pencils. Their generalized finite-core gap lower bound is strictly positive.
The far node remains a Friedrichs form-core truncation and no inverse is
formed. Coexact projection removes the longitudinal gauge/ghost sector before
the form is assembled.

This is a genuine current-domain gauge-field coordinate form shape. It joins
the previously derived current-C2 hypercharge--fermion source jet on the same
finite-core background.

## Why this is not yet a photon propagator

BHSM already owns the parent Maxwell term and the coefficient relation

```text
K_F5/K_G5 = R_F^2/2.
```

An independent gauge normalization is therefore forbidden. However, the
historical pushforward evidence does not permit one of its closed-cycle
numbers to be attached to this C2 form:

- the static transverse and Gauss derivatives were evaluated;
- a proper-time response was evaluated on the historical cycle;
- those values do not establish a common Lorentzian `F_mn F^mn` coefficient;
- the necessary dynamic `omega^2` response had not yet been evaluated on the
  current C2 background at this artifact's original promotion.

Consequently the differential form, coexact domain, multiplicity, and
finite-core gap are derived, while the physical residue is not. Multiplying
the form by a fitted coefficient or reusing a closed-cycle response would
violate the one-parent-pushforward rule.

The downstream continuous-frequency unit now derives that Hessian and finds
a strict temporal/spatial residue mismatch on the smooth parent trace domain.
The exact missing object has therefore sharpened to

```text
ONE_ACTION_DERIVED_NONSINGULAR_BOUNDARY_OR_WENTZELL_TERM_OR_OTHER_EXISTING_
PARENT_DOMAIN_MECHANISM_THAT_REMOVES_THE_CURRENT_TRANSVERSE_LORENTZ_RESIDUE_
MISMATCH_WITHOUT_A_FREE_COEFFICIENT
```

Only after that mismatch is removed by the action/domain can the coexact form
be promoted to a normalized hypercharge propagator, mixed into the physical
photon, and used by the muon or collision engines. See
`theory/ae3_c2_lorentzian_gauge_ghost_hessian.md`.

`CURRENT_C2_COEXACT_GAUGE_FORM_SHAPE_DERIVED=TRUE`,
`CURRENT_C2_LORENTZIAN_MAXWELL_RESIDUE_DERIVED=FALSE`,
`CURRENT_C2_NORMALIZED_PHOTON_PROPAGATOR_DERIVED=FALSE`, and
`FULL_BHSM_COMPLETE=FALSE`.

## Reproduction

```bash
python scripts/materialize_ae3_c2_coexact_gauge_form.py
python -m pytest tests/test_ae3_c2_coexact_gauge_form.py -q
```

The machine-readable result is
`artifacts/action_extension/BHSM_AE3_C2_COEXACT_GAUGE_FORM_SHAPE.json`.
