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
