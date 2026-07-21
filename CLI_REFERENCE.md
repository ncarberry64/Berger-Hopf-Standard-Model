# BHSM CLI Reference

All commands use `python -m bhsm.interface`. Internet and external HEP tools are
not required for the listed local behavior.

Neutral spectral-stiffness commands:

```bash
python -m bhsm.interface neutrino-mass-gap-action --format json
python -m bhsm.interface legacy-dimensional-gate --format json
python -m bhsm.interface neutral-stiffness-ratio --format json
python -m bhsm.interface neutral-spectral-gap --format json
python -m bhsm.interface neutral-kernel-positivity --format json
python -m bhsm.interface neutral-spectral-report --format markdown
python -m bhsm.interface neutral-kernel-exact-audit --format json
python -m bhsm.interface neutral-admissible-domain --format json
python -m bhsm.interface neutral-positivity-proof --format json
python -m bhsm.interface neutral-positivity-counterexample --format json
python -m bhsm.interface neutral-positivity-report --format markdown
python -m bhsm.interface neutral-action-source-search --format json
python -m bhsm.interface neutral-action-stiffness --format json
python -m bhsm.interface neutral-physical-curvature-map --format json
python -m bhsm.interface neutral-action-response-cone --format json
python -m bhsm.interface neutral-action-spectral-closure --format json
python -m bhsm.interface neutral-action-closure-report --format markdown
python -m bhsm.interface neutrino-closure-status --format json
python -m bhsm.interface neutrino-closure-status --format markdown
python -m bhsm.interface full-completion-ledger --format json
python -m bhsm.interface full-completion-priority-map --format json
python -m bhsm.interface full-completion-selected-target --format json
python -m bhsm.interface full-completion-status --format markdown
python -m bhsm.interface charged-source-search --format json
python -m bhsm.interface charged-action-stiffness --format json
python -m bhsm.interface eta-l-source-audit --format json
python -m bhsm.interface ckm-exponent-source-audit --format json
python -m bhsm.interface charged-mixing-law-audit --format json
python -m bhsm.interface charged-dimensional-audit --format json
python -m bhsm.interface charged-closure-report --format markdown
python -m bhsm.interface common-16-source-search --format json
python -m bhsm.interface common-16-incidence-audit --format json
python -m bhsm.interface common-16-bridge-beta-audit --format json
python -m bhsm.interface common-16-ckm-transport-audit --format json
python -m bhsm.interface common-16-provenance-audit --format json
python -m bhsm.interface common-16-closure-report --format markdown
python -m bhsm.interface final-completion-status --format markdown
python -m bhsm.interface final-completion-ledger --format json
python -m bhsm.interface normalized-action-adjoint-pair-search --format json
python -m bhsm.interface normalized-action-adjoint-pair-selection --format json
python -m bhsm.interface hermitian-charged-current-rule --format json
python -m bhsm.interface ckm-transport-space-gate --format json
python -m bhsm.interface ckm-alternative-channel-blockers --format json
python -m bhsm.interface normalized-action-adjoint-pair-report --format markdown
```

These commands are offline and claim-safe. They do not use reference data as
theorem inputs and do not emit a default physical neutrino mass.

| Command | Purpose | Output | Requires internet? | Requires external HEP tools? |
| --- | --- | --- | --- | --- |
| `registry` | List prediction-registry entries | text or JSON | no | no |
| `status KEY` | Show one registry entry | text or JSON | no | no |
| `predict --particle KEY` | Run a deterministic interface demonstration | JSON or text | no | no |
| `report` | Build a combined reviewer report | text or JSON | no | no |
| `gallery` | Build the claim-aware prediction gallery | Markdown or JSON | no | no |
| `plot-gallery --dry-run` | Inspect deterministic plot outputs | JSON | no | no |
| `notebook-pack --check` | Validate parse-only reviewer notebooks | JSON | no | no |
| `pdg-status` | Report optional live-adapter and fallback availability | JSON | no | no |
| `pdg-fetch --particle KEY --offline-ok` | Load a comparison reference with local fallback | JSON | no | no |
| `speculative list` | List disabled speculative templates | JSON | no | no |
| `speculative report` | Report candidate-template status | text or JSON | no | no |
| `theorem-blockers` | List current theorem dispositions and remaining numerical gaps | JSON | no | no |
| `theorem-attempt --blocker KEY` | Run a fail-closed closure attempt | text or JSON | no | no |
| `artifact-sources` | Discover local BHSM evidence | text or JSON | no | no |
| `formula-registry` | List formula callables and theorem gates | text or JSON | no | no |
| `compute-artifact KEY` | Load one registered local artifact | text or JSON | no | no |
| `artifact-predictions` | List adapter-backed values | JSON | no | no |
| `artifact-report` | Build the provenance-aware adapter report | Markdown or JSON | no | no |
| `theorem-closure-report` | Run strict proof-gate attempts | Markdown or JSON | no | no |
| `close-theorem KEY` | Evaluate one theorem against available evidence | text or JSON | no | no |
| `theorem-proof-gates KEY` | Show one theorem's gate results | text or JSON | no | no |
| `cp-o-int-report` | Run the focused CP attachment audit | Markdown or JSON | no | no |
| `cp-o-int-stages` | Show CP attachment stages | JSON | no | no |
| `cp-o-int-proof-gates` | Show focused CP proof gates | JSON | no | no |
| `cp-o-int-candidate` | Inspect the disabled author template | JSON | no | no |
| `cp-o-int-field-action` | Build the symbolic field/action candidate report | Markdown or JSON | no | no |
| `cp-o-int-field-action-stages` | Show Sprint C construction stages | JSON | no | no |
| `cp-o-int-production-eligibility` | Show production and runtime eligibility | JSON | no | no |
| `cp-o-int-action-candidate` | Show the symbolic action-density candidate | JSON | no | no |
| `minimal-action` | Build the complete minimal-action decision record | JSON | no | no |
| `minimal-action-report` | Render the ontology-aware decision table | Markdown or JSON | no | no |
| `close-minimal-action KEY` | Evaluate one minimal-action theorem | JSON | no | no |
| `minimal-action-status` | Show concise theorem statuses | JSON | no | no |
| `neutrino-propagation` | Build the conditional neutrino propagation-mass package | JSON | no | no |
| `neutrino-propagation-report` | Render the dimensionless closure report | Markdown or JSON | no | no |
| `neutrino-effective-mass` | Show canonical channel response rows | JSON | no | no |
| `neutrino-observable-map` | Show propagation/static/comparison distinctions | JSON | no | no |
| `neutrino-scale-law` | Show the audited neutral scale law and missing unit objects | JSON | no | no |
| `neutrino-threshold-response` | Show `K_nu`, `g_nu`, and `kappa_nu` response rows | JSON | no | no |
| `neutral-scale-candidates` | Classify local neutral scale candidates | JSON | no | no |
| `neutral-threshold-energy-map` | Audit the threshold-to-energy map | JSON | no | no |
| `neutral-boundary-measure` | Audit the neutral boundary measure normalization | JSON | no | no |
| `neutrino-dimensionful-mass` | Attempt unit-safe eV/GeV output and fail closed without a unit source | JSON | no | no |
| `neutrino-scale-report` | Render the neutral scale closure audit | Markdown or JSON | no | no |
| `legacy-curvature-artifacts` | Index bundled author-supplied curvature papers | JSON | no | no |
| `curvature-mass-functional` | Show the legacy curvature mass functional and ansatz boundary | JSON | no | no |
| `neutrino-propagation-radius` | Search for a physical neutral localization radius | JSON | no | no |
| `neutral-curvature-mapping` | Audit dimensionless response versus physical curvature units | JSON | no | no |
| `legacy-neutral-scale` | Build the gated legacy neutral-scale candidate | JSON | no | no |
| `legacy-neutral-scale-report` | Render the legacy curvature scale audit | Markdown or JSON | no | no |
| `neutral-propagation-radius` | Separate symbolic, dimensionless, reference, and forbidden radius candidates | JSON | no | no |
| `neutral-physical-curvature` | Separate dimensionless response from symbolic and physical curvature maps | JSON | no | no |
| `neutral-radius-curvature-closure` | Apply coupled radius, curvature, transport, stiffness, and dimension gates | JSON | no | no |
| `dimensionful-neutrino-mass-candidate` | Attempt mass output only after all physical-unit and dimensional gates pass | JSON | no | no |
| `neutral-radius-curvature-report` | Render the v1.2 neutral closure report | Markdown or JSON | no | no |
| `neutrino-closure-status` | Render the canonical five-part neutral closure status without a mass value | Markdown or JSON | no | no |
| `neutrino-bedrock-status` | Report allowed bedrock claims, deferred dynamic claims, forbidden claims, and remaining blockers | Markdown or JSON | no | no |
| `full-completion-ledger` | Render the sixteen-category completion blocker ledger | JSON | no | no |
| `full-completion-priority-map` | Render predeclared closure-target scores | JSON | no | no |
| `full-completion-selected-target` | Render the selected target and fail-closed result | JSON | no | no |
| `full-completion-status` | Render the conservative integrated completion status | Markdown or JSON | no | no |
| `charged-source-search` | Inventory local charged source artifacts | JSON | no | no |
| `charged-action-stiffness` | Audit charged action and stiffness provenance | JSON | no | no |
| `eta-l-source-audit` | Audit eta_l projection, stochastic, action, and transport sources | JSON | no | no |
| `ckm-exponent-source-audit` | Audit the CKM 1/16 exponent source | JSON | no | no |
| `charged-mixing-law-audit` | Audit theta12/theta23/theta13 and CP-source provenance | JSON | no | no |
| `charged-dimensional-audit` | Check dimensional consistency without adding physical units | JSON | no | no |
| `charged-closure-report` | Render the complete charged closure audit | Markdown or JSON | no | no |
| `common-16-source-search` | Locate common-16 source artifacts | JSON | no | no |
| `common-16-incidence-audit` | Verify exact conditional incidence identities | JSON | no | no |
| `common-16-bridge-beta-audit` | Compare bridge/beta common-16 factorizations | JSON | no | no |
| `common-16-ckm-transport-audit` | Apply the CKM reciprocal transport gate | JSON | no | no |
| `common-16-provenance-audit` | Report action and transport provenance blockers | JSON | no | no |
| `common-16-closure-report` | Render the v1.8 focused closure report | Markdown or JSON | no | no |
| `final-completion-status` | Render the conservative v1.8 completion status | Markdown or JSON | no | no |
| `final-completion-ledger` | Render the v1.8 blocker ledger | JSON | no | no |
| `engine-status` | Show validated and excluded BHSM Engine capabilities | Markdown or JSON | no | no |
| `physics-status` | Show conditional BHSM Physics status and blockers | Markdown or JSON | no | no |
| `reviewer-reproduction` | Show deterministic reviewer commands and prerequisites | Markdown or JSON | no | no |
| `engine-invariants` | Run Lorentz, round-trip, near-null, and backward-error checks | Markdown or JSON | no | no |
| `minimal-theorem-core` | Render the evidence-gated theorem core | Markdown or JSON | no | no |
| `omega-f-action-audit` | Audit charged boundary-operator action provenance | Markdown or JSON | no | no |
| `rho-ch-action-audit` | Audit charged Hessian anisotropy provenance | Markdown or JSON | no | no |
| `falsification-table` | Render explicit engine and physics falsifiers | Markdown or JSON | no | no |
| `external-reproduction-packet` | Render the unsent narrow reproduction packet | Markdown or JSON | no | no |
| `primitive-charged-incidence` | Compute the exact conditional charged-incidence spine | Markdown or JSON | no | no |
| `rho-ch-gcd-selection` | Audit gcd normalization and its missing action rule | Markdown or JSON | no | no |
| `overlap-4-over-3-source` | Audit the maximal primitive overlap candidate | Markdown or JSON | no | no |
| `bridge-beta-identity` | Verify exact bridge and beta fractions | Markdown or JSON | no | no |
| `ckm-log-transport-gate` | Gate the reciprocal `1/16` transport candidate | Markdown or JSON | no | no |
| `physical-normalization-gate` | Report missing physical unit-map objects | Markdown or JSON | no | no |
| `external-reproduction-status` | Report prepared versus completed reproduction | Markdown or JSON | no | no |
| `primitive-charged-incidence-report` | Render the combined v2.0 report | Markdown or JSON | no | no |
| `action-lemma-source-search` | Locate evidence and missing action-rule sources | Markdown or JSON | no | no |
| `primitive-lattice-rule` | Gate common-rescaling quotient provenance | Markdown or JSON | no | no |
| `maximal-overlap-bridge-rule` | Gate maximal primitive overlap action selection | Markdown or JSON | no | no |
| `log-transport-averaging` | Prove the abstract quadratic log-energy lemma | Markdown or JSON | no | no |
| `ckm-log-transport-application` | Gate the abstract lemma's CKM application | Markdown or JSON | no | no |
| `action-lemma-closure-report` | Render combined v2.1 action-lemma status | Markdown or JSON | no | no |
| `ckm-channel-source-search` | Locate CKM channel evidence without treating occurrences as proof | Markdown or JSON | no | no |
| `ckm-channel-count-audit` | Compute all four predeclared channel dimensions | Markdown or JSON | no | no |
| `ckm-maximal-sector-selection` | Gate maximal primitive self-response selection | Markdown or JSON | no | no |
| `ckm-channel-equivalence-report` | Render combined v2.2 CKM channel-equivalence status | Markdown or JSON | no | no |
| `ckm-bidirectional-source-search` | Locate charged-current and Hermitian-conjugate evidence | Markdown or JSON | no | no |
| `ckm-bidirectional-channel-count` | Compute exact one-way and bidirectional channel dimensions | Markdown or JSON | no | no |
| `ckm-adjoint-pair-selection` | Gate action-level adjoint-pair selection | Markdown or JSON | no | no |
| `ckm-channel-alternative-resolution` | Compare one-way, bidirectional, self, and total spaces | Markdown or JSON | no | no |
| `ckm-bidirectional-log-transport-application` | Gate the abstract lemma's bidirectional CKM application | Markdown or JSON | no | no |
| `ckm-bidirectional-channel-report` | Render combined v2.3 bidirectional-channel status | Markdown or JSON | no | no |
| `normalized-action-adjoint-pair-search` | Search action and charged-current sources for normalized adjoint-pair provenance | Markdown or JSON | no | no |
| `normalized-action-adjoint-pair-selection` | Gate normalized-action selection of the Hermitian charged-current adjoint-pair space | Markdown or JSON | no | no |
| `hermitian-charged-current-rule` | Separate the general Hermitian action rule from CKM exponent derivation | Markdown or JSON | no | no |
| `ckm-transport-space-gate` | Fail closed unless the normalized action selects the CKM adjoint-pair transport space | Markdown or JSON | no | no |
| `ckm-alternative-channel-blockers` | Record one-way, adjoint-pair, maximal-self, sector-self, and total-endomorphism blockers | Markdown or JSON | no | no |
| `normalized-action-adjoint-pair-report` | Render combined v2.5 normalized-action adjoint-pair status | Markdown or JSON | no | no |
| `charged-current-action-search` | Search local sources for normalized charged-current action evidence | Markdown or JSON | no | no |
| `normalized-charged-current-action-term` | Audit the candidate normalized charged-current action term | Markdown or JSON | no | no |
| `charged-current-transport-space` | Compare action evidence for charged-current transport spaces | Markdown or JSON | no | no |
| `hermitian-adjoint-pair-transport-gate` | Gate adjoint-pair transport selection on normalized action evidence | Markdown or JSON | no | no |
| `ckm-transport-space-application-gate` | Fail closed unless CKM acts on an action-selected space | Markdown or JSON | no | no |
| `charged-current-action-report` | Render combined v2.6 charged-current action transport-space status | Markdown or JSON | no | no |
| `ckm-bounded-interface-search` | Search bounded-term promotion evidence | Markdown or JSON | no | no |
| `ckm-bounded-interface-term` | Audit the located bounded CKM interface term | Markdown or JSON | no | no |
| `normalized-projector-sandwich` | Gate normalized projector-sandwiched action provenance | Markdown or JSON | no | no |
| `projector-domain-codomain` | Gate projector-selected operator directions | Markdown or JSON | no | no |
| `paired-term-normalization` | Audit shared forward/adjoint normalization | Markdown or JSON | no | no |
| `ckm-identification-gate` | Gate identification with CKM transport | Markdown or JSON | no | no |
| `ckm-transport-space-selection` | Combine all CKM transport-selection gates | Markdown or JSON | no | no |
| `ckm-bounded-interface-report` | Render combined v2.7 status | Markdown or JSON | no | no |
| `ckm-boundary-measure-search` | Search measure and normalization sources | Markdown or JSON | no | no |
| `ckm-boundary-measure-source` | Audit symbolic boundary-measure provenance | Markdown or JSON | no | no |
| `ckm-coefficient-normalization` | Audit the CKM coefficient source | Markdown or JSON | no | no |
| `ckm-action-measure-coefficient-pair` | Gate same-term measure/coefficient support | Markdown or JSON | no | no |
| `normalized-ckm-action-candidate` | Combine normalization promotion gates | Markdown or JSON | no | no |
| `ckm-projector-sandwich-requirement` | Audit projector attachment | Markdown or JSON | no | no |
| `ckm-paired-normalization-rule` | Audit shared forward/adjoint normalization | Markdown or JSON | no | no |
| `ckm-transport-space-blocker` | Preserve downstream CKM blockers | Markdown or JSON | no | no |
| `ckm-boundary-measure-normalization-report` | Render combined v2.8 status | Markdown or JSON | no | no |
| `ckm-coefficient-form-source-search` | Search coefficient form/value sources | Markdown or JSON | no | no |
| `weak-charged-current-coefficient-form` | Audit the weak coefficient form | Markdown or JSON | no | no |
| `g2-bh-source` | Audit runtime versus action provenance | Markdown or JSON | no | no |
| `alpha2-bh-source` | Audit registered alpha2 provenance | Markdown or JSON | no | no |
| `weak-coupling-convention` | Audit the g2/alpha2 convention | Markdown or JSON | no | no |
| `ckm-coefficient-form` | Audit the CKM coefficient form | Markdown or JSON | no | no |
| `ckm-coefficient-value-source` | Audit the coefficient value source | Markdown or JSON | no | no |
| `ckm-measure-coefficient-attachment-v2-9` | Audit same-term attachment | Markdown or JSON | no | no |
| `ckm-coefficient-form-report` | Render combined v2.9 status | Markdown or JSON | no | no |
| `weak-gauge-action-source-search` | Inventory weak algebra, action, trace, runtime, and registry sources | Markdown or JSON | no | no |
| `weak-gauge-algebra-source` | Audit the conditional weak algebra source | Markdown or JSON | no | no |
| `normalized-weak-gauge-action-skeleton` | Audit the normalized weak gauge action skeleton | Markdown or JSON | no | no |
| `weak-gauge-trace-normalization` | Separate relative trace normalization from coupling derivation | Markdown or JSON | no | no |
| `g2-bh-action-source` | Separate artifact-backed runtime provenance from action derivation | Markdown or JSON | no | no |
| `alpha2-bh-action-source` | Separate registered coupling provenance from action derivation | Markdown or JSON | no | no |
| `normalized-weak-gauge-action-coefficient` | Gate the unfixed overall weak kinetic coefficient | Markdown or JSON | no | no |
| `ckm-value-source-blocker` | Propagate the weak-action blocker to the CKM value | Markdown or JSON | no | no |
| `weak-gauge-action-source-report` | Render combined v3.0 status | Markdown or JSON | no | no |
| `gauge-coupling-quantum-search` | Search registry, volume, weight, action, and downstream value sources | Markdown or JSON | no | no |
| `gauge-coupling-registry-pattern` | Audit the registered `1:2:7` pattern | Markdown or JSON | no | no |
| `gauge-coupling-volume-denominator` | Audit the proposed `3 Vol(S^3)` denominator | Markdown or JSON | no | no |
| `gauge-sector-weight-source` | Audit candidate sector-weight provenance | Markdown or JSON | no | no |
| `universal-gauge-coupling-quantum` | Gate the proposed universal quantum | Markdown or JSON | no | no |
| `gauge-coupling-action-attachment` | Gate normalized-action attachment | Markdown or JSON | no | no |
| `alpha-i-action-derivation` | Audit all three coupling action sources | Markdown or JSON | no | no |
| `g2-action-source-update` | Propagate the alpha2 result to `g2_BH` | Markdown or JSON | no | no |
| `ckm-value-source-update` | Propagate the `g2_BH` blocker to CKM | Markdown or JSON | no | no |
| `gauge-coupling-quantum-report` | Render combined v3.1 status | Markdown or JSON | no | no |

Without `--offline-ok`, `pdg-fetch` may try an optional live reference adapter.
The offline fallback is reference-only and is never a derivation input.

<!-- BHSM_FULL_ACTION_CLOSURE_V4_0 -->
### v4.0 full-action closure commands

```bash
python -m bhsm.interface full-action-status-snapshot --format json
python -m bhsm.interface full-theorem-blocker-dag --format json
python -m bhsm.interface unified-action-skeleton --format json
python -m bhsm.interface boundary-frame-averaging --format json
python -m bhsm.interface gauge-denominator-source --format json
python -m bhsm.interface sector-weight-action-attachment --format json
python -m bhsm.interface gauge-action-coefficient-k --format json
python -m bhsm.interface alpha-i-action-gate --format json
python -m bhsm.interface g2-action-gate --format json
python -m bhsm.interface ckm-completion-gate --format json
python -m bhsm.interface neutral-scale-gate --format json
python -m bhsm.interface scalar-topographic-gate --format json
python -m bhsm.interface dimensionful-scale-bridge --format json
python -m bhsm.interface full-bhsm-completion-gate --format json
python -m bhsm.interface full-action-closure-report --format markdown
```

## Full action closure v4.0

Status: `FULL_BHSM_NOT_COMPLETE`.

The deterministic blocker DAG is in [docs/full_theorem_blocker_dag.md](docs/full_theorem_blocker_dag.md) and
`artifacts/BHSM_full_theorem_blocker_dag_v4_0.json`.

- BHSM is not complete until the full action-normalization and scale gates close.
- The 1:2:7 gauge-coupling registry pattern is artifact-backed but not action-derived.
- The candidate denominator 6π² = 3 Vol(S³) is not a coupling derivation unless attached to the normalized gauge action.
- Sector weights do not derive gauge couplings without action attachment.
- The overall gauge-action coefficient k remains open unless fixed by the action.
- The CKM coefficient form is artifact-backed, but the CKM coefficient value remains open unless g2_BH is action-derived.
- The CKM exponent remains not derived unless all CKM action, transport, identification, and log-averaging gates close.
- Dimensionless neutral/PMNS structure does not imply physical neutrino masses.
- Physical Delta m², matter effects, radiative corrections, stiffness length, curvature, and unit normalization remain open unless separately derived.
- Full BHSM completion is not claimed by this repository unless every completion gate passes.

<!-- BHSM_BOUNDARY_COLLAR_MEASURE_V4_1 -->
### v4.1 boundary/collar measure commands

```bash
python -m bhsm.interface boundary-collar-measure-search --format json
python -m bhsm.interface boundary-collar-measure-source --format json
python -m bhsm.interface unit-s3-volume-normalization --format json
python -m bhsm.interface three-boundary-frame-directions --format json
python -m bhsm.interface boundary-frame-averaging-v4-1 --format json
python -m bhsm.interface gauge-trace-frame-average-attachment --format json
python -m bhsm.interface gauge-denominator-source-v4-1 --format json
python -m bhsm.interface universal-gauge-quantum-update --format json
python -m bhsm.interface gauge-action-attachment-update --format json
python -m bhsm.interface alpha-i-update-v4-1 --format json
python -m bhsm.interface g2-update-v4-1 --format json
python -m bhsm.interface ckm-value-update-v4-1 --format json
python -m bhsm.interface full-completion-update-v4-1 --format json
python -m bhsm.interface boundary-collar-measure-report --format markdown
```

## Boundary/collar measure v4.1

Measure status: `CONDITIONAL_BOUNDARY_COLLAR_MEASURE_SOURCE`. Three coframe directions:
`ARTIFACT_BACKED_THREE_BOUNDARY_FRAME_DIRECTIONS`. Unit-S3 normalization, frame averaging,
gauge trace attachment, and the gauge denominator remain open.

- The mathematical identity Vol(S³_unit)=2π² is not by itself a gauge-coupling derivation.
- The candidate denominator 6π² = 3 Vol(S³_unit) is not action-derived unless BHSM supplies an action-selected three-frame boundary average.
- A three-frame decomposition does not by itself imply a frame average.
- A frame average does not derive gauge couplings unless attached to gauge trace densities in the normalized action.
- The gauge coupling quantum λ_gauge = 1/(6π²) remains open unless the denominator is action-attached.
- The α_i values remain open unless the gauge quantum, sector weights, and action coefficient are attached by the normalized action.
- g2_BH remains open unless α2_BH is action-derived and the weak convention applies.
- The CKM coefficient value remains open unless g2_BH is action-derived.
- The CKM exponent remains not derived.
- Full BHSM remains not complete unless all action-normalization and scale gates close.

<!-- BHSM_BERGER_FRAME_WEIGHTING_V4_2 -->
### v4.2 Berger frame-weighting commands

```bash
python -m bhsm.interface berger-frame-weighting-search --format json
python -m bhsm.interface equal-frame-weighting --format json
python -m bhsm.interface frame-average-normalization --format json
python -m bhsm.interface berger-anisotropy-compatibility --format json
python -m bhsm.interface gauge-trace-frame-average-attachment-v4-2 --format json
python -m bhsm.interface gauge-denominator-update-v4-2 --format json
python -m bhsm.interface universal-quantum-update-v4-2 --format json
python -m bhsm.interface gauge-action-attachment-update-v4-2 --format json
python -m bhsm.interface alpha-i-update-v4-2 --format json
python -m bhsm.interface g2-update-v4-2 --format json
python -m bhsm.interface ckm-value-update-v4-2 --format json
python -m bhsm.interface full-completion-update-v4-2 --format json
python -m bhsm.interface berger-frame-weighting-report --format markdown
```

## Berger frame weighting v4.2

Equal weighting and frame-average normalization remain open. Berger anisotropy compatibility is
conditional on an action-selected orthonormal gauge coframe. Gauge attachment and all downstream
coupling gates remain open.

- Three artifact-backed Berger frame directions do not by themselves imply equal weighting.
- Equal weighting does not by itself imply average normalization by 1/3.
- Average normalization does not by itself attach to gauge trace densities.
- Berger anisotropy must be checked before equal frame averaging can be promoted.
- The denominator 1/[3 Vol(S³)] remains open unless equal frame averaging, unit-volume normalization, and gauge-trace attachment are supported.
- The gauge coupling quantum remains open unless the denominator is action-attached.
- α_i, g2_BH, CKM coefficient value, and CKM exponent remain open unless downstream action gates close.
- Full BHSM remains not complete.

<!-- BHSM_GAUGE_COFRAME_HODGE_V4_3 -->
### v4.3 gauge coframe/Hodge commands

```bash
python -m bhsm.interface gauge-coframe-hodge-search --format json
python -m bhsm.interface gauge-coframe-basis --format json
python -m bhsm.interface hodge-star-metric-factors --format json
python -m bhsm.interface anisotropy-compatibility-update-v4-3 --format json
python -m bhsm.interface equal-orthonormal-gauge-frame-coefficients --format json
python -m bhsm.interface frame-average-update-v4-3 --format json
python -m bhsm.interface gauge-trace-attachment-update-v4-3 --format json
python -m bhsm.interface denominator-update-v4-3 --format json
python -m bhsm.interface downstream-coupling-update-v4-3 --format json
python -m bhsm.interface full-completion-update-v4-3 --format json
python -m bhsm.interface gauge-coframe-hodge-report --format markdown
```

## Gauge coframe/Hodge v4.3

Gauge coframe basis remains open; Hodge-star metric dependence is conditional. Equal coefficients, frame averaging, gauge attachment, denominator, and downstream couplings remain open.

- Equal frame coefficients in an orthonormal coframe are distinct from equal coefficients in the raw Berger coframe.
- Hodge-star metric factors may absorb Berger anisotropy, but this does not by itself imply frame averaging by 1/3.
- Equal orthonormal coefficients do not imply average normalization.
- Average normalization does not imply gauge trace attachment.
- Gauge couplings, CKM coefficient value, and full BHSM completion remain open unless downstream gates close.

<!-- BHSM_BERGER_HODGE_COMPONENT_V4_4 -->
## Berger Hodge component map v4.4

The explicit component map is conditionally derived from the Berger metric and chosen orientation. Gauge-action coframe selection, equal action coefficients, frame averaging, attachment, denominator, and downstream couplings remain open.

- An explicit Berger Hodge-star component map is distinct from selecting the gauge-action coframe basis.
- The orthonormal coframe e^a absorbs Berger metric scale factors, while raw sigma_a components retain anisotropic Hodge factors.
- A component Hodge map does not by itself imply equal gauge-frame coefficients.
- Equal coefficients do not by themselves imply average normalization by 1/3.
- Gauge trace Hodge expansion does not by itself derive gauge couplings.
- The denominator 1/[3 Vol(S^3)] remains open unless frame averaging, unit volume normalization, and gauge-action attachment are all supported.
- alpha_i, g2_BH, CKM coefficient value, CKM exponent, and full BHSM completion remain open unless downstream gates close.

<!-- BHSM_FULL_GEOMETRIC_GAUGE_FIXED_HESSIAN_V5_11 -->
## Full geometric and gauge-fixed Hessian v5.11

```bash
python -m bhsm.interface full-geometric-gauge-fixed-hessian-status --format json
python -m bhsm.interface full-geometric-gauge-fixed-hessian-status --format markdown
python scripts/materialize_full_geometric_gauge_fixed_hessian_v5_11.py
```

The command reports `BHSM_QUADRATIC_OPERATOR_COMPLEX_PARTIAL`, including field and 36-block ledgers, gauge/ghost candidates, fermion/domain/eta status, scalar recovery, mode audits, and the finite consistency model. It does not emit a one-loop action or physical Casimir energy.

<!-- BHSM_PRIMORDIAL_BOUNDARY_TENSION_ACTION_SOURCE_CLOSURE_V5_12 -->
## Primordial boundary-tension action source closure v5.12

```bash
python -m bhsm.interface primordial-boundary-tension-status --format json
python -m bhsm.interface primordial-boundary-tension-status --format markdown
python scripts/materialize_primordial_boundary_tension_action_source_closure_v5_12.py
```

The command reports source, localization, dimension, stress, pressure, surface-Hessian, crossing, one-scale, and energy-conversion status without emitting a physical `L_c`.

It also reports `BHSM_SPACETIME_RECYCLING_CONSTRAINT_ARCHITECTURE_IDENTIFIED`: the general candidate top-form action, core-source and causal audits, ensemble-dependent recycling pressure, rank-one surface-mode response, and open absolute-scale gates. It does not assert black-hole-driven expansion.

<!-- BHSM_S7_FIBER_INTEGRATION_PHYSICAL_LOCALIZATION_V6_0 -->
## S7 fiber integration and physical localization v6.0

```bash
python -m bhsm.interface s7-fiber-integration-status --format json
python -m bhsm.interface s7-fiber-integration-status --format markdown
python scripts/materialize_s7_fiber_integration_physical_localization_v6_0.py
```

The command reports `BHSM_S7_ARCHITECTURE_AMBIGUOUS`. It derives the exact
nested Hopf–twistor diagram and conditional fiber-pushforward theorem but does
not select an S7 physical action domain, absolute scale, mass, or coupling.

<!-- BHSM_B8_S7_PHYSICAL_DOMAIN_ACTION_SOURCE_CLOSURE_V6_0_1 -->
## B8/S7 physical domain and action-source closure v6.0.1

```bash
python -m bhsm.interface b8-s7-physical-domain-status --format json
python -m bhsm.interface b8-s7-physical-domain-status --format markdown
python scripts/materialize_b8_s7_physical_domain_action_source_closure_v6_0_1.py
```

The command reports `BHSM_B8_S7_PARENT_ACTION_SOURCE_MISSING`. It preserves
the v6.0 nested topology, separates all viable physical-domain branches, and
audits the energy–geometry enclosure criterion without promoting it to a
derived action or physical normalization.

<!-- BHSM_B8_GEOMETRY_ENERGY_PARENT_ACTION_V6_0_2 -->
## B8 geometry–energy parent action v6.0.2

```bash
python -m bhsm.interface b8-parent-action-status --format json
python -m bhsm.interface b8-parent-action-status --format markdown
python scripts/materialize_b8_geometry_energy_parent_action_v6_0_2.py
```

The command reports `BHSM_B8_MINIMAL_ACTION_FAMILY_IDENTIFIED` and
`BHSM_ENERGY_GEOMETRY_PHYSICALITY_SOURCE_NOT_DERIVED`. It does not select a
signature, physical action coefficient, confinement invariant, stable phase,
surface tension, or absolute scale.

<!-- BHSM_ENERGY_GEOMETRY_CONFINEMENT_INVARIANT_V6_0_3 -->
## Energy--geometry confinement invariant v6.0.3

```bash
python -m bhsm.interface energy-geometry-confinement-status --format json
python -m bhsm.interface energy-geometry-confinement-status --format markdown
python scripts/materialize_energy_geometry_confinement_invariant_v6_0_3.py
```

The command reports `BHSM_ENERGY_GEOMETRY_FINITE_INVARIANT_FAMILY_IDENTIFIED`
and `BHSM_PHYSICALITY_THRESHOLD_ARCHITECTURE_IDENTIFIED`. It exposes the
complete conditional sigma Hessian, spectral threshold, finite-size and
nonlinear formulas, and the harmonic-coherence selection hypothesis without
selecting a physical coupling or claiming a formed physical phase.

<!-- BHSM_HARMONIC_PHYSICALITY_COUPLING_SELECTION_V6_0_4 -->
## Harmonic physicality coupling selection v6.0.4

```bash
python -m bhsm.interface harmonic-physicality-selection-status --format json
python -m bhsm.interface harmonic-physicality-selection-status --format markdown
python scripts/materialize_harmonic_physicality_coupling_selection_v6_0_4.py
```

The command reports `BHSM_HARMONIC_SELECTION_SOURCE_NOT_DERIVED` and
`BHSM_PHYSICALITY_COUPLING_SELECTION_BLOCKED`. It includes the linear
no-selection theorem, exact round-S7 `l=4,10` octave ratio, nonlinear
interaction gates, coherence projector, sigma-shift audit, and scale firewall
without promoting commensurability to a physical coupling.
