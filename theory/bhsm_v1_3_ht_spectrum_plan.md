# BHSM v1.3 H_T Spectrum Plan

Branch: `bhsm-v1.3-ht-spectrum`

Objective: attack the largest remaining Standard-Model-equivalence blocker:
the full twisted Dirac / `H_T` spectrum.

This plan does not change frozen v1.0/v1.1 predictions, constants, tolerances,
mode ledgers, or branch outputs.

## Current H_T Status

The current repository contains a finite-basis and lower-bound program for the
topographic stability operator `H_T`. The no-extra-light-state theorem remains
open.

Current status to preserve:

- Level 2 finite-basis `H_T` proxy exists.
- Spectral lower-bound scaffold exists.
- Basis-convergence audit exists.
- Formal sufficient theorem scaffold exists.
- `theorem_complete` remains `False`.

## Existing Proxy / Scaffold Modules

Relevant modules already present:

- `src/twisted_dirac.py`
- `src/ht_operator.py`
- `src/spectral_gap.py`
- `src/spectral_bounds.py`
- `src/positivity.py`
- `src/theorem_scaffold.py`
- `src/scalar_decoupling.py`

Relevant notebooks and reports:

- `notebooks/06_twisted_dirac_ht_spectrum.ipynb`
- `notebooks/09_twisted_dirac_level2_operator.ipynb`
- `notebooks/10_spectral_lower_bound_program.ipynb`
- `notebooks/11_basis_convergence_ht_bound.ipynb`
- `theory/ht_no_extra_light_theorem_scaffold.md`
- `theory/proof_gap_report.md`

## Required Mathematical Target

The main spectral target is:

```text
H_T|_{H_perp} >= (4 pi^2 v)^2
```

Equivalently, in the dimensionless Hopf-gap normalization already used in the
repository:

```text
H_T|_{H_perp} >= mu_H = 64 pi^5
```

## Required Zero-Mode Target

The protected-family target is:

```text
dim ker D_twist = 3
```

The complement `H_perp` must exclude exactly these protected chiral zero modes
and must not contain additional light mirror or scalar/topographic states.

## Near-Term Goals

1. Derive a Berger twisted Dirac eigenvalue formula or rigorous lower bound.
2. Separate protected zero modes from the complement without relying only on
   finite-basis projection.
3. Prove or bound the first complement eigenvalue of the twisted Dirac square.
4. Integrate the positive-semidefinite curvature/profile condition:

```text
V_profile|_{H_perp} >= 0
```

5. Compare the analytic or semi-analytic lower bound to the current Level 2
   finite-basis result.
6. Keep all failures explicit and preserve `theorem_complete=False` until the
   full assumptions are proven.

## Non-Goals

- No retuning of `a`, `S`, mode ledgers, tolerances, `Z_virt`, or frozen
  predictions.
- No changes to `BHSM_BARE_V1` or `BHSM_DRESSED_V1_CANDIDATE`.
- No claim that the `H_T` theorem is complete unless the full analytic or
  sufficient spectral proof is implemented.
- No replacement of the v1.1 public release package.

## First Technical Task

Start with a representation-aware symbolic/analytic inventory of the Level 2
twisted Dirac matrix terms:

- diagonal Berger/spin-connection contribution;
- Hopf twist contribution;
- boundary/chirality contribution;
- sector-coupling terms;
- protected zero-mode projection;
- PSD profile contribution.

Then classify which terms admit direct analytic lower bounds and which still
depend on finite-basis estimates.

## v1.3A Term Inventory Status

Status: `IMPLEMENTED`

BHSM v1.3A inventories and classifies the Level 2 `H_T` operator terms for
analytic-bound development. It does not prove the full no-extra-light-state
theorem, and `theorem_complete` remains `False`.

Generated reports:

- `theory/ht_level2_term_inventory.md`
- `theory/ht_level2_term_inventory.json`
- `theory/ht_bound_classification_report.md`
- `theory/ht_bound_classification_report.json`
- `manuscript/v1_3a_ht_term_inventory_note.md`
- `notebooks/23_ht_term_inventory.ipynb`

Current classifications:

- `berger_dirac_kinetic`: `DIAGONAL_EXACT`
- `hopf_twist`: `SIGN_INDEFINITE_BOUNDED`
- `boundary_term`: `SIGN_INDEFINITE_BOUNDED`
- `chirality_term`: `SIGN_INDEFINITE_BOUNDED`
- `sector_coupling`: `OFF_DIAGONAL_BOUNDED`
- `heat_lift`: `PSD_EXACT`
- `psd_profile`: `PSD_EXACT`
- `zero_complement_projector`: `FINITE_BASIS_ONLY`

The weakest analytic block is `zero_complement_projector`, because the full
action-level statement `dim ker D_twist = 3` and the infinite-dimensional
complement decomposition remain open. The weakest matrix term is
`sector_coupling`, whose current control is finite-basis Gershgorin / min-max
rather than an infinite-basis operator-norm bound.

## v1.3B Sector-Coupling Bound Status

Status: `IMPLEMENTED`

BHSM v1.3B isolates the Level 2 sector-coupling perturbation:

```text
K_sector = D_full^dagger D_full - D_0^dagger D_0
```

where `D_0` disables `sector_coupling` and
`offdiag_boundary_coupling`. The audit computes finite spectral,
Frobenius, row-sum, Weyl, and relative-bound estimates on the protected
finite-basis complement.

Generated reports:

- `theory/sector_coupling_bound_report.md`
- `theory/sector_coupling_bound_report.json`
- `manuscript/v1_3b_sector_coupling_bound_note.md`
- `notebooks/24_sector_coupling_bounds.ipynb`

Baseline result:

- Required Dirac lower bound: `0.8038064161349437`
- Base complement lower bound before sector coupling: `1.4641`
- Full complement lower bound with sector coupling: `1.463040025299567`
- Sector-coupling spectral norm: `0.4720872031830534`
- Weyl lower bound: `0.9920127968169465`
- Classification: `NORM_BOUND_SUFFICIENT`

Robustness result:

- Cases scanned: `72`
- All finite-basis cases pass: `True`
- All norm bounds sufficient: `False`
- Classification set:
  `NORM_BOUND_SUFFICIENT`,
  `NORM_BOUND_INSUFFICIENT_BUT_FINITE_BASIS_PASSES`

This improves the sector-coupling audit but does not complete the theorem:
some larger/perturbed finite-basis cases pass by direct spectrum while the
conservative norm bound is insufficient. Those cases remain finite-basis
evidence, not analytic proof.

## v1.3C Structured Sector-Coupling Bound Status

Status: `IMPLEMENTED`

BHSM v1.3C analyzes additional structure in the Level 2 sector-coupling block.
At the Dirac-matrix level the coupling:

- connects distinct charged sectors only;
- preserves `k`, `j`, Hopf charge `q`, and chirality;
- vanishes on the protected zero-mode coordinate block;
- is sparse in the finite basis;
- is block-banded after ordering by `(k,j,chirality)`;
- is finite-rank only at fixed `k_max`, not certified finite-rank as
  `k_max -> infinity`.

Generated reports:

- `theory/structured_sector_coupling_bound.md`
- `theory/structured_sector_coupling_bound.json`
- `manuscript/v1_3c_structured_sector_bound_note.md`
- `notebooks/25_structured_sector_coupling_bounds.ipynb`

The structured finite-basis relative-bound diagnostic computes:

```text
a_K = ||B^{-1/2} K_sector B^{-1/2}||
```

on the protected complement. Baseline result:

- `a_K`: `0.015621013485509948`
- Structured lower bound: `1.4412292741558648`
- Required Dirac lower bound: `0.8038064161349437`
- Classification: `RELATIVE_BOUND_CANDIDATE`

Robustness result:

- Cases scanned: `84`
- All structured finite-basis bounds sufficient: `True`
- All finite-basis gaps pass: `True`
- All classifications remain `RELATIVE_BOUND_CANDIDATE`

This strengthens finite-basis and semi-analytic sector-coupling control, but it
does not complete the theorem. The bound must still be made uniform in the
infinite-basis limit and paired with a full proof of the zero-mode/complement
decomposition.

## v1.3D Uniform Relative-Bound Status

Status: `IMPLEMENTED`

BHSM v1.3D tests whether the structured sector-coupling relative-bound
certificate remains stable as `k_max` increases.

Generated reports:

- `theory/uniform_relative_bound_report.md`
- `theory/uniform_relative_bound_report.json`
- `manuscript/v1_3d_uniform_relative_bound_note.md`
- `notebooks/26_uniform_relative_bounds.ipynb`

Scan definition:

- `k_max = 4, 6, 8, 10, 12, 16, 20, 24, 32`
- `a = alpha^{-1}/(12*pi^2), 1.0, 0.573`
- baseline plus v1.3B sector-coupling perturbations

Result:

- Scan rows: `108`
- Classification: `UNIFORM_BOUND_CANDIDATE`
- All rows pass the required Dirac lower bound: `True`
- All `b_K` values remain zero: `True`
- Max `a_K`: `0.03095889839310559`
- Minimum structured lower bound: `1.418773076862654`
- Minimum finite-basis lower bound: `1.4599918132873242`
- Maximum mode-block bandwidth: `2`

Canonical-baseline trend summary:

- `a_K`: stable
- `b_K`: stable at zero
- sparsity: increasing
- band width: stable
- structured lower bound: stable
- finite-basis complement lower bound: stable

The scan supports a uniform-bound candidate across tested finite truncations,
but it does not prove the infinite-basis result. Remaining blockers are the
finite-to-infinite upgrade, the full zero-mode/complement split, and the lack
of a compactness or finite-rank theorem for the growing sector-coupling block.

## v1.3E Hilbert-Space Domain Scaffold Status

Status: `IMPLEMENTED`

BHSM v1.3E converts the v1.3D finite uniform-bound evidence into a formal
Hilbert-space/domain theorem scaffold.

Generated reports:

- `theory/hilbert_space_domain_scaffold.md`
- `theory/hilbert_space_domain_scaffold.json`
- `theory/infinite_sector_bound_scaffold.md`
- `theory/infinite_sector_bound_scaffold.json`
- `manuscript/v1_3e_hilbert_space_bound_note.md`
- `notebooks/27_hilbert_space_infinite_bound.ipynb`

Formal basis labels:

```text
e_{k,j,q,chi,sector}
```

with `k >= 0`, `0 <= j <= floor(k/2)`, `q = k - 2j`,
`chi in {-1,+1}`, and `sector in {lepton, up, down}`.

Theorem scaffold status:

- Status: `THEOREM_SCAFFOLD`
- Theorem complete: `False`
- Finite evidence bridge: `UNIFORM_BOUND_CANDIDATE`
- Conservative assumption candidate: `a_K^max = 0.04`, `b_K = 0`
- Candidate diagonal lower bound: `d0 = 1.4641`
- Candidate structured lower bound: `1.405536`
- Required Dirac lower bound: `0.8038064161349437`
- Candidate margin: `0.6017295838650562`

Assumptions A1-A6:

- A1: `K_sector` preserves `(k,j,q,chi)` and only mixes sectors.
- A2: `K_sector` has uniformly bounded mode-block bandwidth.
- A3: `K_sector` is `D0^2`-relative bounded on `H_perp` with
  `a_K <= 0.04`, `b_K = 0`.
- A4: `K_sector` vanishes on protected zero modes.
- A5: the complement projection is well-defined and commutes with the relevant
  block decomposition.
- A6: the diagonal complement lower bound clears the relative-bound
  requirement.

Correct claim:

```text
BHSM v1.3E defines the Hilbert-space/domain assumptions under which the
structured sector-coupling relative bound would extend beyond finite
truncations. It does not prove the full H_T theorem until those assumptions
and the zero-mode/complement split are derived from the complete operator.
```

Recommended v1.3F task: prove or further constrain A5 and A6: the protected
kernel/complement projection and the diagonal complement lower bound on the
infinite Hilbert space.

## v1.3F State Ontology Status

Status: `IMPLEMENTED`

BHSM v1.3F adds a state ontology and particle/mode classification ledger.

Generated reports:

- `theory/bhsm_state_ontology.md`
- `theory/bhsm_state_ontology.json`
- `manuscript/v1_3f_state_ontology_note.md`
- `notebooks/28_state_ontology.ipynb`

Ontology categories:

- `ON_SHELL_SM_PARTICLE`
- `COMPOSITE_QCD_STATE`
- `INTERNAL_BERGER_HOPF_MODE`
- `VIRTUAL_EXCITATION`
- `DRESSING_CONTRIBUTION`
- `HEAVY_LIFTED_STATE`
- `SCREENED_TOPOGRAPHIC_STATE`
- `FORBIDDEN_EXTRA_LIGHT_STATE`
- `OPEN_UNCLASSIFIED`

Correct claim:

```text
BHSM v1.3F clarifies that internal modes and virtual dressing contributions
are not automatically new observable particles. Extra observable light states
remain forbidden unless identified experimentally or lifted/screened by the
H_T/scalar-sector mechanisms.
```

This ontology layer does not change frozen predictions and does not complete
the full `H_T` theorem.

## v1.3G Zero-Mode and Complement-Split Status

Status: `IMPLEMENTED`

BHSM v1.3G formalizes the zero-mode/index and complement-projector scaffold
needed for the `H_T` no-extra-light-state theorem.

Generated reports:

- `theory/zero_mode_index_scaffold.md`
- `theory/zero_mode_index_scaffold.json`
- `theory/complement_projector_report.md`
- `theory/complement_projector_report.json`
- `theory/index_theorem_scaffold_report.md`
- `theory/index_theorem_scaffold_report.json`
- `manuscript/v1_3g_zero_mode_complement_note.md`
- `notebooks/29_zero_mode_complement_split.ipynb`

Target decomposition:

```text
H = ker(D_twist) direct_sum H_perp
```

Target kernel/index:

```text
dim ker(D_twist) = 3
Index(D_twist) = 3
```

Current scaffold result:

- exactly three protected zero-mode candidates are identified;
- finite Level 2 projectors satisfy `P0^2=P0`, `P_perp^2=P_perp`, and
  `P0 P_perp=0`;
- the finite sector-coupling block vanishes on the protected coordinate block;
- the heat lift preserves zero Dirac-squared modes;
- mirror opposite-chirality zero modes remain `OPEN`;
- theorem_complete remains `False`.

Correct claim:

```text
BHSM v1.3G formalizes the zero-mode/index and complement-projector scaffold
needed for the H_T no-extra-light-state theorem. It does not prove the full
index theorem unless the topological and mirror-mode assumptions are derived
from the complete operator.
```

Recommended v1.3H task: attack the diagonal complement lower bound and mirror
mode exclusion in the complete twisted Dirac operator, so assumptions `I1`,
`I3`, `I5`, and the infinite-dimensional projector compatibility can be
upgraded from scaffold/open status.

## v1.3H Diagonal Complement and Mirror-Mode Status

Status: `IMPLEMENTED`

BHSM v1.3H audits the diagonal complement lower bound and mirror-mode
exclusion conditions needed for the `H_T` no-extra-light-state theorem.

Generated reports:

- `theory/diagonal_complement_bound_report.md`
- `theory/diagonal_complement_bound_report.json`
- `theory/mirror_mode_exclusion_report.md`
- `theory/mirror_mode_exclusion_report.json`
- `theory/twisted_dirac_index_audit.md`
- `theory/twisted_dirac_index_audit.json`
- `manuscript/v1_3h_diagonal_mirror_note.md`
- `notebooks/30_diagonal_complement_mirror_audit.ipynb`

Current finite-scaffold result:

- required Dirac lower bound: `0.8038064161349437`;
- finite diagonal coordinate-complement lower bound: `1.4641`;
- first complement mode: `basis_index=18`, `sector=up`, `(k,j,q,chi)=(0,0,0,-1)`;
- diagonal finite scaffold clears the required bound;
- mirror candidates `mirror_lepton`, `mirror_up`, and `mirror_down` are all
  classified as `OPEN_MIRROR_RISK`;
- scaffold index: `3`;
- theorem_complete remains `False`.

Correct claim:

```text
BHSM v1.3H audits the diagonal complement lower bound and mirror-mode
exclusion conditions needed for the H_T no-extra-light-state theorem. It does
not prove the full theorem unless the topological index, mirror exclusion, and
infinite-basis complement bound are derived from the complete twisted Dirac
operator.
```

Recommended v1.3I task: derive or rule out the `OPEN_MIRROR_RISK` candidates
from the full chiral projector, Higgs-selected `U(1)` phase, and sector
boundary functional, or prove the topological index theorem that excludes
opposite-chirality kernel states.

## v1.3I Mirror-Exclusion Derivation Status

Status: `IMPLEMENTED`

BHSM v1.3I audits whether mirror zero modes are excluded by the weak chiral
projector, Higgs-selected `U(1)` boundary phase, and v1.2 sector boundary
functional.

Generated reports:

- `theory/mirror_exclusion_derivation_report.md`
- `theory/mirror_exclusion_derivation_report.json`
- `manuscript/v1_3i_mirror_exclusion_note.md`
- `notebooks/31_mirror_exclusion_derivation.ipynb`

Current channel result:

- `mirror_lepton`: `EXCLUDED` by `EXCLUDED_BY_CHIRAL_PROJECTOR`;
- `mirror_up`: `EXCLUDED` by `EXCLUDED_BY_CHIRAL_PROJECTOR`;
- `mirror_down`: `EXCLUDED` by `EXCLUDED_BY_CHIRAL_PROJECTOR`;
- Higgs-selected `U(1)` phase channel remains `OPEN`;
- sector boundary-functional channel remains `OPEN`;
- scaffold index remains `3`;
- theorem_complete remains `False`.

Correct claim:

```text
BHSM v1.3I audits whether mirror zero modes are excluded by the chiral
projector, Higgs-selected U(1) boundary phase, and v1.2 sector boundary
functional. It does not prove the full H_T theorem unless mirror exclusion,
the index theorem, and the infinite-basis complement bound are all closed.
```

Recommended v1.3J task: attack the remaining `OPEN_ALIGNMENT_GAP` between the
formal sector-labeled zero-mode scaffold and the finite Level 2 coordinate
protected block, or derive the full topological index theorem
`Index(D_twist)=3`.
