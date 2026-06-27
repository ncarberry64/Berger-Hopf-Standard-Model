# BHSM CLI Reference

All commands use `python -m bhsm.interface`. Internet and external HEP tools are
not required for the listed local behavior.

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

Without `--offline-ok`, `pdg-fetch` may try an optional live reference adapter.
The offline fallback is reference-only and is never a derivation input.
