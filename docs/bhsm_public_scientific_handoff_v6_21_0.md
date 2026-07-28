# BHSM public scientific handoff v6.21.0

## 1. Purpose

This document is the shortest evidence-based route into the Berger-Hopf
Standard Model (BHSM) repository. It freezes the scientific state at v6.20
and separates what is derived, adopted, numerically validated, rejected, and
still under construction. It is a review guide, not a new scientific theorem.

## 2. One-paragraph BHSM hypothesis

BHSM investigates whether an internal Berger-Hopf geometry, its boundary
structure, and its admissible modes can organize features associated with
four-dimensional fields, flavor, generations, interactions, and scale. The
working hypothesis is that geometric spectra, bundle data, boundary
conditions, and constrained action responses may replace some otherwise
independent inputs. Each step is treated as a separate evidence obligation.
A suggestive pattern, numerical agreement, or internal artifact is not
automatically a physical derivation.

## 3. Repository evidence model

BHSM uses several evidence layers:

- **Artifacts:** machine-readable records under `artifacts/` preserve inputs,
  outputs, status, provenance, and blockers.
- **Source provenance:** action coefficients and formulas are traced to
  repository declarations rather than silently imported.
- **Deterministic materializers:** generated artifacts are reproduced
  byte-for-byte by explicit scripts or audit tools.
- **Focused tests:** symbolic identities, numerical residuals, domains,
  status boundaries, and artifact determinism are tested near the relevant
  construction.
- **Claim boundaries:** [CLAIMS.md](../CLAIMS.md) separates supported
  statements from unsupported upgrades.
- **Frozen predictions:** [Markdown](frozen_predictions.md) and
  [JSON](frozen_predictions.json) records have fixed integrity hashes.
- **External data:** PDG, CERN, CMS, and other measurements are comparison or
  computational-validation data unless a source explicitly states otherwise.
  They are not hidden fitting inputs.

The [artifact index](../ARTIFACT_INDEX.md) connects machine-readable evidence
to the corresponding source and doctrine.

## 4. What is currently derived

Repository-supported derived consequences include:

- an executable artifact/provenance interface and deterministic audit layer;
- multiple exact geometric, spectral, boundary, action, and constrained
  variation results on their stated assumptions and domains;
- the critical scalar-wall fold and its static branch geometry;
- the v6.18 nonhomogeneous threading response

  ```text
  Pi_perp S_Sigma = -tau (pi chi_1/16) Pi_perp q;
  ```

- the result that no explicit energy threshold is required for that derived
  threading response;
- a nonempty dynamic threading domain with zero unresolved threading traces
  after the homogeneous resting selection;
- the v6.20 action-derived radial measure

  ```text
  dmu_rad = N_0 a_0^4 dt = pi sin^4(pi t/4) dt;
  ```

- the v6.20 critical lapse--Weyl principal bulk block

  ```text
  L_Apsi^crit =
  [
    0                  6 kappa_1/a_0^2
    6 kappa_1/a_0^2   12 kappa_1/a_0^2
  ].
  ```

The threading response is derived, and the lapse--Weyl principal block is
derived. These are constrained results, not a completed four-dimensional
physical action or kinetic classification.

## 5. What is adopted

BHSM distinguishes adopted inputs from derived consequences:

- standard mathematical and physical identities may be **Adopted from
  established physics/mathematics** with explicit conventions;
- the source-free homogeneous threading choice `C_Sigma=0` is an **Adopted
  BHSM axiom**;
- proposed correspondences between mathematical structures and physical
  sectors are **BHSM identifications** until independently derived or tested;
- the provisional intrinsic B1 construction and several parent/action
  selections remain conditional inputs, not universal consequences.

Adoption keeps a construction available for testing. It does not promote the
adopted statement to a theorem.

## 6. What has been rejected by calculation

The repository records negative results rather than hiding them:

- canonical normalization rejects the proposed exponential wall-coupling
  rule;
- the available minimal matter operator has zero light-heavy coupling;
- the minimal well-posed action contains no junction mixing term;
- pointwise zero threading overconstrains a dynamical fold;
- seam slide is not an exact symmetry of the stored action and observable
  data;
- an explicit energy threshold is unnecessary for the derived threading
  response because the source vanishes when `D_mu q=0`.

These rejections apply to the tested constructions. They do not prove that
every conceivable extension is impossible.

## 7. Current fold derivation chain

The focused v6.11-v6.20 development can be read as:

```text
static scalar-wall fold and physical tangent
  -> promotion exposes an endpoint/threading constraint problem
  -> two-cap action/domain audit isolates the threading trace
  -> pointwise zero threading is rejected for a dynamical fold
  -> induced constrained response supplies the nonconstant trace
  -> C_Sigma=0 removes the source-free homogeneous constant
  -> dynamic threading domain is nonempty, unresolved trace count is zero
  -> critical lapse-Weyl principal Hessian and radial measure are derived
  -> covariant gauge-quotiented X-metric tangent is still absent
  -> complete Schur complement and fold kinetic sign remain unresolved
```

Static branch geometry and the principal constrained Hessian are available.
The chain does not supply a physical fold mass or dynamical stability result.

## 8. Exact current frontier

The exact active construction target is

```text
T_mu_nu^(X) (x,x')
  = delta hbar_mu_nu[X] (x) / delta X(x') evaluated at X=2,

delta R_4[T^(X)] = tau chi_1 q.
```

`T_mu_nu^(X)` must be defined after quotienting four-dimensional
diffeomorphisms and declaring the regulated physical M4 domain. A scalar
curvature variation is one contraction of a symmetric metric variation. It
does not uniquely determine all tensor components, a gauge representative,
boundary data, or an adjoint domain.

This one object is needed to fix:

- the complete mixed lapse--Weyl source;
- the remaining B1/matcher scalar conditions;
- the actual and adjoint domains and kernels;
- source compatibility;
- separation from the recorded Einstein-frame Weyl term;
- the constrained Schur complement and final kinetic sign.

Therefore `T_mu_nu^(X)` is active, the fold kinetic sign is unresolved, and
no physical mass claim is supported.

## 9. Model-wide active construction targets

Independent major targets include:

- parent/core action selection and normalization;
- the physical M4 metric tangent and boundary domain;
- the fold kinetic Schur complement;
- normalized gauge actions and action-derived couplings;
- charged-current source normalization and the CKM exponent;
- neutral operator/action normalization and physical unit map;
- an absolute dimensionful scale bridge;
- independent mode and generation selection;
- empirical falsification against new observations.

Progress on one target does not silently close another.

## 10. What BHSM does not claim

BHSM does not presently claim:

- empirical validation or replacement of the Standard Model;
- a complete derivation of the Standard Model;
- a complete physical BHSM or four-dimensional action;
- action-derived physical particle masses or neutrino masses;
- physical `Delta m^2`;
- action-derived physical gauge couplings or CKM exponent;
- a positive, ghost, null, tachyon, or nonlinear-stability classification of
  the fold;
- collider-production or FeynRules/UFO/MadGraph readiness;
- CERN, CMS, or institutional endorsement;
- cosmological production or white-hole dynamics.

## 11. Reviewer reproduction path

Use Python 3.10 or newer. From a clean checkout:

```bash
python -m pip install -e .
make reviewer-smoke
python -m bhsm.interface --help
python -m bhsm.interface registry
python -m bhsm.interface physics-status --format markdown
python tools/audit_public_readiness.py
python tools/audit_forbidden_claims.py
python tools/audit_bhsm_status.py
python tools/audit_frozen_prediction_integrity.py
python tools/verify_precision.py
```

Without `make`, run:

```bash
python -m pytest -q tests/test_engine_invariant_preservation.py tests/test_engine_physics_status_separation.py
```

The expected smoke result is three passing tests. Full setup, optional
dependencies, and runtime-gated workflows are in
[QUICKSTART.md](../QUICKSTART.md) and the
[reviewer reproduction guide](reviewer_reproduction_guide.md).

## 12. How to submit critique

Use the repository's
[research/claim review template](../.github/ISSUE_TEMPLATE/research-source.yml)
for a theorem, formula, source, artifact, or status objection. Identify the
specific claim, repository evidence, mathematical or computational objection,
reproduction steps, expected status change, and any use of measured input.

Use the [bug template](../.github/ISSUE_TEMPLATE/bug-report.yml) for
reproducible software defects. Security vulnerabilities should follow
[SECURITY.md](../SECURITY.md) and should not be disclosed in a public issue.
Contribution expectations are in [CONTRIBUTING.md](../CONTRIBUTING.md).

## 13. Citation and license

Citation metadata are in [CITATION.cff](../CITATION.cff). The verified DOI is
[10.5281/zenodo.20663419](https://doi.org/10.5281/zenodo.20663419).
GitHub's latest published release is `v1.1.0` (2026-06-26); the DOI resolves
to an older Zenodo archival snapshot whose stored version label is `v1.2.0`
(2026-06-12). No release, tag, DOI, or deposit is created by this handoff.

The repository is publicly viewable and reviewable; reuse is governed by
[LICENSE.md](../LICENSE.md). The license file is unchanged by this public
readiness handoff.
