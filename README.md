# Berger-Hopf Standard Model

BHSM = Berger-Hopf Standard Model.

This repository is a public research release for the Berger-Hopf Standard
Model project. It contains the frozen BHSM v1.0 executable model framework and
the BHSM v1.1 technical note / preprint package.

The frozen v1.0 baseline is a no-retuning prediction and falsification package:
the canonical geometry, overlap width, charged-sector mode ledger, tolerance
bands, and bare/dressed-candidate outputs are fixed. Post-freeze adjustment of
`a`, `S`, modes, tolerances, or `Z_virt` based on residuals invalidates the
frozen v1.0 prediction set.

## Quickstart

```powershell
python -m pytest -q
```

Current paper-branch test status: `281 passed`.

## Branches and Tag

| Ref | Meaning |
| --- | --- |
| `main` | v1.0 frozen model baseline |
| `bhsm-v1.1-paper` | paper/preprint branch |
| `bhsm-v1.0-freeze` | frozen v1.0 model tag |

## Public Release Contents

- `src/`: executable BHSM audit/model modules.
- `tests/`: pytest coverage for the model, ledgers, scaffolds, and manuscript
  checks.
- `theory/`: machine-readable and manuscript-readable audit ledgers.
- `manuscript/BHSM_v1_technical_note.tex`: v1.1 technical note source.
- `manuscript/BHSM_v1_technical_note.pdf`: built preprint-style PDF.
- `manuscript/BHSM_v1_technical_note_full.md`: unified Markdown manuscript.
- `manuscript/release_checklist.md`: release-readiness checklist.

## v1.2 Development Branch

Branch: `bhsm-v1.2-action-origin`

Purpose: develop the action-origin program for the charged-sector boundary
operators `Omega_f` without changing the frozen v1.0/v1.1 prediction packages.

Status: omega coefficients are derived from an explicit symbolic sector
boundary functional; that functional is reduced from a symbolic parent
internal-action scaffold; minimality and tested-variant uniqueness audits find
the scaffold `UNIQUE_UNDER_BHSM_AXIOMS`.

Current v1.2 branch tests: `310 passed`.

Correct claim: BHSM v1.2 audits whether the parent-action scaffold is minimal
and unique under the current BHSM axioms. It does not claim full uniqueness of
the complete internal action.

## v1.3 Development Branch

Branch: `bhsm-v1.3-ht-spectrum`

Purpose: attack the full twisted Dirac / `H_T` spectrum gap, the largest
remaining Standard-Model-equivalence blocker.

Status: planning branch. Existing Level 2 finite-basis, spectral lower-bound,
and basis-convergence scaffolds are preserved. The v1.3 target is an
analytic or semi-analytic twisted Dirac / `H_T` spectral bound with
`theorem_complete=False` until proven.

### BHSM State Ontology

v1.3F adds a state ontology ledger that distinguishes accepted on-shell SM
particles, QCD composites, internal Berger-Hopf modes, virtual excitations,
dressing contributions, heavy lifted modes, screened topographic states, and
forbidden extra-light states.

Correct claim: internal modes and virtual dressing contributions are not
automatically new observable particles. Extra observable light states remain
forbidden unless experimentally identified or lifted/screened by the
`H_T`/scalar-sector mechanisms.

### Zero-Mode and Complement Split

v1.3G adds a zero-mode/index and complement-projector scaffold for the target
decomposition `H = ker(D_twist) direct_sum H_perp` with
`dim ker(D_twist)=3`. The finite projector identities pass and the finite
sector-coupling block vanishes on the protected coordinate block.

Correct claim: this formalizes the scaffold needed for the `H_T`
no-extra-light-state theorem. It does not prove the full index theorem; the
topological index calculation and mirror-mode exclusion remain open.

### Diagonal Complement and Mirror Modes

v1.3H audits the finite diagonal complement lower bound and opposite-chirality
mirror candidates. The finite coordinate-complement diagonal lower bound is
`1.4641`, clearing `d_required = 0.8038064161349437`, while all three generated
mirror candidates remain `OPEN_MIRROR_RISK`.

Correct claim: the diagonal finite scaffold passes, but the full `H_T` theorem
still requires topological index, mirror-exclusion, and infinite-basis
complement-bound derivations.

### Mirror Exclusion Derivation

v1.3I audits the generated mirror candidates against the weak chiral
projector, Higgs-selected `U(1)` phase, and v1.2 sector boundary functional.
The chiral projector channel excludes `mirror_lepton`, `mirror_up`, and
`mirror_down`; the Higgs-`U(1)` and boundary-functional channels remain open.

Correct claim: mirror candidates are excluded at the chiral-projector scaffold
channel, but the full `H_T` theorem still requires the topological index,
formal/coordinate zero-mode alignment, and infinite-basis complement bound.

### Zero-Mode Alignment

v1.3J audits whether the formal sector-labeled protected zero-mode scaffold is
the same as the finite Level 2 coordinate-protected block. The result is
partial alignment: `zero_mode_lepton` aligns with coordinate `0`, while
`zero_mode_up` and `zero_mode_down` are present at coordinates `18` and `36`
but are not inside the finite coordinate-protected block.

Correct claim: the alignment gap is clarified, not closed. The full `H_T`
theorem still requires a full operator/index/complement proof.

## Limitations and Open Proof Obligations

The release preserves the repository's claim discipline:

- The full twisted Dirac / `H_T` spectrum remains open.
- The `H_T` no-extra-light-state theorem remains proxy/scaffold audited, not
  analytically proven.
- Scalar/topographic decoupling remains scaffold audited, not fully proven from
  the action.
- Boundary operators `Omega_f` are action-linked, not fully action-derived.
- Precision QCD/RG matching remains open.
- `BHSM_DRESSED_V1_CANDIDATE` is a dressed candidate branch, not final
  canonical adoption.

## License

All rights reserved. This repository is not released under an open-source
license at this time. See `LICENSE.md`.

# Berger-Hopf Standard Model Completion Program

This repository formalizes, audits, and numerically tests a conditional
Berger-Hopf topographic framework for reinterpreting Standard Model flavor,
couplings, generations, and the electroweak scale.

The repository is deliberately conservative: it implements the supplied
framework as reproducible screens and ledgers. It does not claim a rigorous
first-principles derivation of the Standard Model from geometry alone.

## First Test Targets

- Hypercharge derivation from admitted chiral pattern, Higgs-selected U(1),
  Yukawa invariance, and anomaly cancellation.
- Standard Model anomaly cancellation for one generation.
- Berger spectrum mass hierarchy screens for the supplied mode ledger.
- Gauge coupling matching screens.
- Electroweak scale calculation.
- Proxy spectral-gap screen for the topographic stability operator.

## Phase 2: Gate 28 Proxy Spectral-Gap Audit

Gate 28 turns the no-extra-light-state condition into an executable proxy
audit. The code uses the supplied Berger scalar spectrum proxy as a temporary
stand-in for `D_hat^dagger D_hat`, applies an explicit heat lift with a fixed
`Lambda^2`, and checks pass/fail against `mu_H = 64 pi^5`.

This is a proxy audit only. The full twisted Dirac `H_T` spectrum remains open,
and the no-extra-light-state theorem is not proven here.

## Phase 3: Gate 28B Natural-Width Robustness Audit

Gate 28B fixes the heat-kernel cutoff to the universal overlap width
`Lambda^2 = S = 1/(4 pi)` by default. The robustness scan reports explicit
pass/fail margins over supplied values of `a`, `n_max`, and additive
curvature/profile lower bounds `v_min`.

At natural width, the first nonzero proxy mode clears the Hopf-gap target for
`a = 1.0`, `n_max = 20`, and `v_min = 0`. Negative `v_min` values are reported
as weakening contributions and may break the proxy gap. This remains a proxy
audit, not a proof of the no-extra-light-state theorem.

## Phase 4: Gate 28C Curvature/Profile Positivity Audit

Gate 28C adds explicit curvature/profile sign models to the proxy audit:
`zero`, `positive_barrier`, `bounded_negative`, and `compensated`. The proxy
Hopf gap is protected when the curvature/profile contribution is nonnegative
on `H_perp`, while negative contributions can break the gap unless compensated
by a positive topographic barrier.

This audit formalizes the needed positivity condition in executable form. It
does not compute the full twisted Dirac `H_T` spectrum and does not prove the
no-extra-light-state theorem.

## Phase 5: Gate 28D Positive-Semidefinite Profile Construction

Gate 28D formalizes the positivity condition as a finite-basis operator audit:
the curvature/profile contribution is represented as `Q^dagger Q` on `H_perp`,
or as `Q^dagger Q - C Pi_0` where `Pi_0` projects onto the protected zero-mode
subspace. The restricted complement operator is tested by its minimum
eigenvalue.

Positive-semidefinite profile terms preserve the proxy Hopf gap. Negative
wells can break it. Compensated barriers restore it when the restricted
profile contribution on `H_perp` is nonnegative. The no-extra-light-state
theorem remains conditional on replacing these proxy finite-basis operators
with the full twisted Dirac `H_T` spectrum.

## Phase 6: Gate 25B Boundary-Operator Mode Selection

Gate 25B turns the supplied operational boundary operators into executable
selection rules. The heavy mode `(0,0)` is included separately, then each
charged sector selects the first two nonzero admissible modes by increasing
Berger action.

The supplied boundary operators recover the charged-sector mode ledger without
using observed mass inputs. Full derivation of `Omega_f` from the twisted
Dirac or bundle action remains open.

## Phase 7: Claims Ledger Automation

Phase 7 adds a machine-readable and manuscript-readable claims ledger generated
from `src/claims.py`. The ledger prevents test results from being upgraded
beyond their implemented status. Forbidden claims remain explicitly forbidden,
proxy audits remain proxy audits, and open tasks remain open.

Current pytest suite: 269 tests.

| Gate | Status |
| --- | --- |
| Hypercharge and anomalies | Verified tests within admitted ledger |
| Coupling and electroweak-scale relations | Strong numerical screens |
| Gate 25B mode selection | Operational boundary audit; full Omega_f derivation open |
| Gate 28/28B/28C/28D spectral gap | Proxy audits; full H_T spectrum open |
| Gate 32B spectral lower bounds | Sufficient lower-bound scaffold; full H_T theorem open |
| Gate 32C basis convergence | Finite-basis convergence audit; full analytic theorem open |
| Gate 32D theorem scaffold | Formal sufficient theorem scaffold; A1-A7 remain proof obligations |
| Phase 18 working model engine | Executable BHSM low-energy reinterpretation object |
| Phase 19 prediction ledger | Table-driven model-output ledger with per-row status and limitations |
| Phase 20 residual audit | Diagnostic residual ranking; no tuning performed |
| Phase 21 flavor implementation audit | CKM/PMNS internal-rule screens connected |
| Phase 22 up-sector root-cause audit | Localized light up-quark and CKM Vub tension diagnosed; no tuning performed |
| Phase 23 canonical geometry audit | Alpha-anchored Berger geometry adopted by theory rule; round geometry remains a control |
| Phase 24 canonical flavor matrix | CKM matrix magnitudes and Hopf-phase CP screen computed under canonical geometry |
| Phase 25 mass scheme audit | Quark mass-ratio comparisons made scheme-aware; QCD running remains open |
| Phase 26 quark running scaffold | Approximate common-scale quark reference pipeline added; precision QCD remains open |
| Phase 27 charm/top tension audit | Threshold-aware running and charm-mode diagnostics added; no correction adopted |
| Phase 28 representation-normalization audit | Up-sector normalization candidates evaluated; no factor adopted |
| Phase 29 virtual-environment dressing | Diagnostic dressing layer formalized; pure-fiber middle-up `1/2` is linked but not canonical |
| Phase 30 virtual-dressed adoption gate | C1-C6 adoption criteria pass; rule is an adoption candidate, not canonical |
| Phase 31 BHSM v1 frozen prediction set | Bare and dressed-candidate no-retuning branches frozen; falsification ledger F1-F9 exported |
| Claims ledger | Automated audit/control layer |

Warning: the no-extra-light-state theorem remains conditional until the full
twisted Dirac `H_T` spectrum is computed.

## Current Proof Gaps

| Gap | Current Status | Next Required Step |
| --- | --- | --- |
| Full twisted Dirac / `H_T` spectrum | `DIRAC_PROXY_LEVEL_2 + SPECTRAL_BOUND_SCAFFOLD + BASIS_CONVERGENCE_AUDIT + THEOREM_SCAFFOLD` | Prove assumptions A1-A7 in the full internal action |
| Boundary operators `Omega_f` | `ACTION_LINKED` | Derive coefficients from the full twisted Dirac/bundle action |
| RG matching | one-loop scaffold | Implement two-/three-loop threshold matching |
| Scalar/topographic decoupling | finite-basis scaffold | Prove decoupling from the full action-level spectrum and couplings |

## Phase 8: Gate 25C Symbolic Boundary-Operator Scaffold

Gate 25C formalizes the representation-to-boundary map for the operational
boundary operators:

- `Omega_lepton = -q + 2j`
- `Omega_up = q - 2j`
- `Omega_down = q + 4j`

The scaffold records the fiber/base coefficients and representation labels,
compares them to the Gate 25B operational functions, and marks all three
boundaries as `OPERATIONAL`, not `ACTION_DERIVED`.

The remaining target is to derive the coefficient pairs `(-1, 2)`, `(1, -2)`,
and `(1, 4)` from chirality, weak component, coframe triplet structure, and
Hopf/base boundary phases in the twisted Dirac/bundle action.

## Phase 9A: Twisted Dirac / H_T Finite-Basis Scaffold

Phase 9A adds `DIRAC_PROXY_LEVEL_1`, a finite-basis twisted Dirac scaffold with
chirality labels, Hopf charges, sector-dependent boundary data, twist shifts,
protected zero modes, complement spectra, and an `H_T` heat-lift construction.

Full `H_T` theorem remains `OPEN`. A first twisted-Dirac finite-basis scaffold
has been implemented, but it is still a proxy and not the final analytic
spectrum.

## Phase 9B: Twisted Dirac / H_T Robustness Audit

Phase 9B stress-tests `DIRAC_PROXY_LEVEL_1` across basis size, Berger
anisotropy, sector selections, chirality inclusion, twist-parameter
perturbations, and PSD profile terms. Negative profile terms remain forbidden
by default and appear only in explicitly labeled failure scans.

The full `H_T` theorem remains `OPEN`; Phase 9B is a robustness audit of the
finite-basis proxy.

## Phase 10: Gate 25D Boundary-Operator Action-Link Audit

Boundary operators are now `ACTION_LINKED`: their coefficients are reproduced
by an explicit symbolic phase-contribution rule tied to Hopf fiber orientation,
base-node phase, chirality, weak component, coframe factor, and family index.

They remain not fully `ACTION_DERIVED` until obtained from variation/spectrum
of the full twisted Dirac/bundle action.

## Phase 11: Gate 29B RG Matching Scaffold

Gate 29B implements a one-loop RG matching scaffold using GUT-normalized
`alpha1`. The supplied geometric couplings behave as electroweak-scale matching
conditions near `MZ`, rather than constants at all scales.

Full two-/three-loop threshold matching remains `OPEN`.

## Phase 12: Gate 30B Scalar/Topographic Decoupling Scaffold

Gate 30B implements a scalar/topographic decoupling scaffold. The
Standard-Model limit requires exactly one light Higgs projection and no
unscreened light direct-coupled scalar.

Filtered and screened light modes are conditional audit cases. Full scalar
decoupling from the action remains `OPEN`.

## Phase 13: Gate 32A Level 2 Twisted Dirac Operator

Gate 32A implements `DIRAC_PROXY_LEVEL_2`, a representation-aware,
matrix-based finite-basis twisted Dirac operator scaffold with Hermitian
diagnostics, protected zero modes, Level 2 `H_T` gap reports, PSD profile
support, and robustness scans.

It is representation-aware and matrix-based, but the full analytic `H_T`
spectrum remains `OPEN`.

## Phase 15: Gate 32B Spectral Lower-Bound Program

Gate 32B implements a spectral lower-bound scaffold for the Level 2 finite
basis. It audits the sufficient condition
`d_lower + mu_H * (1 - exp(-d_lower / Lambda^2)) + V_min >= mu_H` with the
natural cutoff `Lambda^2 = 1/(4 pi)`.

Gate 32B: spectral lower-bound scaffold implemented. The (H_T) theorem remains
open, but the finite-basis proxy is now accompanied by explicit sufficient
lower-bound inequalities and conservative bound checks.

## Phase 16: Gate 32C Basis-Convergence Audit

Gate 32C audits Level 2 `H_T` proxy truncation stability over
`k_max = 4, 6, 8, 10, 12, 16` and `a = 0.573, 1.0,
alpha_inverse/(12*pi**2)` at the natural cutoff. The scan reports basis size,
zero-mode count, direct/min-max/Gershgorin margins, and explicit monotonicity
notes for the first complement eigenvalue.

Gate 32C: basis-convergence audit implemented. The Level 2 (H_T) proxy gap
remains finite-basis/proxy evidence; full analytic spectral theorem remains
OPEN.

## Phase 17: Gate 32D Formal Sufficient Theorem Scaffold

Gate 32D separates the no-extra-light-state argument into explicit assumptions,
conditional implication steps, proxy evidence, and remaining proof obligations.
The scaffold states that if assumptions A1-A7 are proven in the full internal
action, then the no-extra-light-state theorem follows.

Gate 32D: formal sufficient theorem scaffold added. The theorem is not
complete; it lists the exact assumptions A1-A7 that must be proven in the full
internal action.

## Phase 18: Working BHSM Model Engine

Phase 18 adds `BHSMModel`, an executable low-energy Berger-Hopf Standard Model
reinterpretation object. It assembles the gauge group, SM field ledger,
hypercharges, anomaly check, charged-sector generation modes, Yukawa overlap
ratios, symbolic Lagrangian blocks, geometric couplings, Higgs scale screen,
Level 2 `H_T` proxy gap status, and scalar/topographic decoupling status.

This is a working model engine, not a completed proof. The full action-level
derivations and full analytic `H_T` spectrum remain open.

## Phase 19: Prediction Ledger

Phase 19 adds a table-driven prediction/screen ledger generated from
`BHSMModel`. The term prediction here means model-output ledger entry. Rows
cover charged fermion mass ratios, CKM structure, PMNS effective-extension
structure, gauge couplings, Higgs/electroweak outputs, `H_T` proxy gap status,
and scalar decoupling status.

Each row preserves its own status and limitations. Proxy and scaffold entries
remain proxy/scaffold outputs, not final confirmed predictions.

## Phase 20: Prediction Residual Audit

Phase 20 adds a residual audit for the prediction/screen ledger. The audit
ranks ordinary relative errors, adds log-ratio errors for positive mass-ratio
rows, and marks quark mass ratios as scheme-sensitive because no consistent
quark mass-scheme treatment is implemented.

Best finite residuals are exact/status rows with relative error `0.0`. The
largest current ordinary relative error under the canonical geometry is
`mass_ratio.up_quarks.middle` at `0.13003176431657681`; it remains marked
`SCHEME_SENSITIVE`. No parameters are tuned in this phase.

## Phase 21: BHSM Flavor Implementation Audit

Phase 21 repairs the flavor-sector implementation gap by connecting CKM rows
to the supplied BHSM mass-ratio screen rules and PMNS rows to the supplied
effective-extension alpha rules. Quark mass residuals remain scheme-sensitive;
no quark mass parameters are tuned.

## Phase 22: Up-Sector and CKM Vub Root-Cause Audit

The main current flavor tension is the light up-quark overlap and CKM
`V_ub`. The diagnostic reproduces the current up-sector residuals, scans
admissible up modes, compares overlap constants as sensitivity-only cases, and
marks CKM-rule alternatives as exploratory only. The next admissible up mode
overcorrects the light up-quark ratio, so the ledger is not changed.

## Phase 23: BHSM Canonical Geometry

Phase 23 adds `bhsm_config.py` and audits the available Berger anisotropy
configurations:

- `ROUND`: `a=1.0`, retained as a baseline control.
- `LEGACY_LOW_A`: `a=0.573`, retained as legacy sensitivity only.
- `ALPHA_ANCHORED`: `a=alpha^{-1}/(12*pi^2)=1.157054135733433`.

The default `BHSMModel` now uses the alpha-anchored Berger geometry because
the BHSM scale sector contains the theory-side assumption
`epsilon_alpha = alpha^{-1}/(12*pi^2) - 1`. This is not selected by empirical
mass residual minimization. The round geometry remains available for control
comparisons, and the legacy low-a value remains sensitivity-only.

Under the alpha-anchored default, the localized up-sector diagnostic gives
`c/t = 0.008310500554068288`, `u/t = 1.2690463017606151e-05`, and
`sin(theta_13) = 0.0035623676140463315`. Quark mass comparisons remain
scheme-sensitive, and no flavor screen is upgraded to a final prediction.

## Phase 24: Canonical BHSM Flavor Matrix

Phase 24 adds `flavor_matrix.py`, which recomputes the canonical flavor
outputs under the alpha-anchored geometry. CKM angles are computed from the
internal overlap ratios:

- `sin(theta_12) = sqrt(d/s)`
- `sin(theta_23) = 2(s/b)`
- `sin(theta_13) = sqrt(u/t)`

The CKM CP phase is now an implemented Hopf-phase screen,
`delta_CKM = (q_u - q_d) sqrt(S)`, with `q_u=q(10,1)`, `q_d=q(8,2)`, and
`S=1/(4*pi)`. This gives `delta_CKM = 1.1283791670955126` and
`J_CKM = 3.1011702945437805e-05` in the canonical model. These are computed
internal-rule screens, not fitted values and not final action-level flavor
derivations.

## Phase 25: Quark Mass Scheme and Running Audit

Phase 25 adds `mass_scheme.py`, which replaces bare charged-quark comparison
labels with explicit mass-reference scheme metadata. The current repository
inputs are grouped as `MIXED_DEFAULT`; quark cross-generation ratios are marked
`scheme_consistent=False` and `scheme_sensitive=True`. Charged-lepton ratios
remain scheme-stable in this audit.

A second scheme set, `COMMON_SCALE_PLACEHOLDER`, is included only as a scaffold
for future QCD running. It reuses current values and is explicitly incomplete.
No masses are tuned, no external data are fetched, and the canonical
alpha-anchored geometry is unchanged. The remaining `c/t` residual is still
reported, but classified as scheme-sensitive rather than a final failure under
mixed reference inputs.

## Phase 26: Quark Running Scaffold

Phase 26 adds `quark_running.py`, an `APPROXIMATE_RUNNING_SCAFFOLD` for moving
quark mass references toward common comparison scales. It uses a fixed-`nf`
one-loop-inspired formula,
`m(mu_2)=m(mu_1)[alpha_s(mu_2)/alpha_s(mu_1)]^p`, with `p=12/23`.

Target scales currently audited are `M_Z = 91.1876 GeV`, a top-like scale
`172.69 GeV`, and a `10 GeV` control. These tables are kept separate from the
`MIXED_DEFAULT` residual audit. The scaffold changes only the reference
comparison pipeline; canonical BHSM ratios and geometry are unchanged. Full
threshold matching, higher-loop QCD running, and uncertainty propagation
remain open.

## Phase 27: Charm/Top Tension Audit

Phase 27 adds threshold-aware running diagnostics and a localized charm-mode
audit. The new piecewise-`nf` scaffold is labeled
`THRESHOLD_AWARE_APPROXIMATE_RUNNING_SCAFFOLD`; it still does not implement
precision QCD. At `M_Z`, the fixed-`nf` `c/t` reference is
`0.004266868071316746`, while the piecewise-`nf` reference is
`0.004251569034944846`. The `c/t` tension therefore persists.

Top-reference variants are label-only sensitivity cases that reuse the current
repo top value. The next admissible up-sector mode after `(6,0)` is `(10,1)`,
which overcorrects the charm ratio, so the mode ledger is unchanged. A simple
normalization-factor scan finds `1/2` closest under the threshold scaffold, but
no factor is adopted.

## Phase 28: Charm/Top Representation-Normalization Diagnostic

Phase 28 adds `representation_normalization.py`, which audits whether a
`1/2`-like factor could follow from representation geometry rather than from
fitting the `c/t` residual. Candidate rules include `NONE`,
`WEAK_DOUBLE_PROJECTION`, `AMPLITUDE_PROJECTION`, `COFRAME_AVERAGE`,
`COFRAME_AMPLITUDE`, and `ALPHA_SUPPRESSED`.

The `WEAK_DOUBLE_PROJECTION` candidate gives factor `1/2` and brings
`c/t` to `0.004155250277034144` when applied only to the pure-fiber nonzero
`j=0` up mode, but it remains `DIAGNOSTIC_ONLY`. Applying `1/2` to all
up-sector modes also changes `u/t` to `6.3452315088030755e-06` and
`sin(theta_13)` to `0.0025189742969715027`. No factor is action-linked or
canonically adopted in this phase.

## Phase 29: Virtual-Environment Dressing Layer

Phase 29 adds `virtual_environment.py`, which formalizes the diagnostic map
from bare BHSM overlaps to observed/running comparison ratios:

`(m_i/m_3)_observed_mu = Z_virt^{f,i}(mu) (m_i/m_3)_BHSM_bare`.

The pure-fiber middle-up rule `Z_virt^{u,2}=1/2` passes a virtual-environment
linkage test using internal mode data only: `j=0`, `q=6`, and `Omega_u=6` for
mode `(6,0)`. It is marked `VIRTUAL_ENV_LINKED`, not
`ADOPTED_CANONICAL`.

The repository now reports two variants: `BHSM_BARE_CANONICAL`, which remains
the canonical model, and `BHSM_VIRTUAL_DRESSED_DIAGNOSTIC`, which applies the
linked dressing rule diagnostically. Full loop/threshold derivation of the
virtual dressing layer remains open.

## Phase 30: Virtual-Dressed Adoption Criteria Audit

Phase 30 adds a formal adoption gate for the virtual-environment dressing
rule. Criteria C1-C6 check internal representation data, residual independence,
local scope, preservation of successful outputs, field-theory interpretation,
and pre-comparison application order.

The pure-fiber middle-up `1/2` rule passes all six criteria and is marked
`ADOPTION_CANDIDATE`. It is not marked `ADOPTED_CANONICAL_DRESSED`. The bare
canonical prediction ledger remains separate from the dressed candidate ledger.

## Phase 31: BHSM v1.0 Frozen Prediction Set

Phase 31 freezes two no-retuning prediction branches:

- `BHSM_BARE_V1`
- `BHSM_DRESSED_V1_CANDIDATE`

Both branches keep the canonical alpha-anchored geometry
`a = 1.157054135733433`, overlap width `S = 1/(4*pi)`, and supplied mode
ledger fixed. The dressed-candidate branch applies only the existing
pure-fiber middle-up rule `Z_virt^{u,2}=1/2`, changing `c/t` while leaving
`u/t`, `sin(theta_13)`, down-sector ratios, lepton ratios, gauge outputs, and
electroweak outputs unchanged.

Tolerance bands are declared before scoring, and falsification criteria F1-F9
are exported as a machine-readable ledger. Any post-freeze residual-driven
change to `a`, `S`, modes, or `Z_virt` invalidates the v1.0 package. The
dressed branch is a candidate prediction branch, not a completed proof or final
canonical adoption.

## Quick Start

```powershell
cd C:\Users\carbe\OneDrive\Documents\CODEX\berger_hopf_sm_completion
python -m pytest
```

## Claim Discipline

Results are tagged as:

- `derived`: algebraically follows from stated assumptions in the code.
- `conditional`: follows after admitting the specified framework inputs.
- `screened`: numerical agreement or consistency check, not an independent
  prediction.
- `open`: reduced to a computable task or bound, not completed.

See `theory/forbidden_claims.md` and `manuscript/claims_ledger.md`.
