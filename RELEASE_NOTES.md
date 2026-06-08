# BHSM v1.1 Preprint Package Release Notes

Branch: `bhsm-v1.1-paper`

## Unreleased / Development: v1.2 Action-Origin Development

Branch: `bhsm-v1.2-action-origin`

The v1.2 development branch packages the action-origin audit for the
charged-sector boundary operators. The charged-sector operators are derived
from an explicit symbolic sector boundary functional, and that functional is
reduced from a symbolic parent internal-action scaffold. Minimality and
tested-variant uniqueness audits find the scaffold
`UNIQUE_UNDER_BHSM_AXIOMS`.

This is a development addendum only. It does not alter `BHSM_BARE_V1`,
`BHSM_DRESSED_V1_CANDIDATE`, canonical constants, frozen predictions,
tolerances, or v1.1 public release outputs. It does not claim global uniqueness
of the complete Berger-Hopf internal action.

## Unreleased / Development: v1.3 H_T Spectrum

Branch: `bhsm-v1.3-ht-spectrum`

The v1.3 development branch is opened to attack the full twisted Dirac /
`H_T` spectrum gap. Current finite-basis Level 2, spectral lower-bound, and
basis-convergence scaffolds are preserved. The near-term target is an analytic
or semi-analytic lower-bound program for:

```text
H_T|_{H_perp} >= (4 pi^2 v)^2
```

This planning branch does not retune predictions and does not claim completion
of the `H_T` theorem.

v1.3F adds a state ontology and particle/mode classification ledger. It
clarifies that internal Berger-Hopf modes, virtual excitations, and
virtual-environment dressing contributions are not automatically new
observable particles. Any extra observable light state remains forbidden
unless experimentally identified or lifted/screened by the `H_T` and
scalar-sector mechanisms.

v1.3G adds a zero-mode/index and complement-projector scaffold for
`H = ker(D_twist) direct_sum H_perp` with target `dim ker(D_twist)=3`. The
finite Level 2 projector identities pass, but the full topological index
calculation and mirror-mode exclusion remain open.

v1.3H audits the diagonal complement lower bound and generated mirror-mode
candidates. The finite diagonal complement lower bound clears the required
Dirac threshold, but all three opposite-chirality mirror candidates remain
`OPEN_MIRROR_RISK`.

v1.3I audits those mirror candidates through chiral, Higgs-`U(1)`, and
boundary-functional channels. The weak chiral projector excludes all three
generated mirror candidates at the scaffold-channel level; theorem completion
remains false because the topological index and infinite-basis complement
bound remain open.

v1.3J audits the alignment between the formal protected zero-mode labels and
the finite Level 2 coordinate-protected block. The result is partial alignment:
the lepton label aligns, while the up/down labels remain
`OPEN_ALIGNMENT_GAP`.

v1.3K builds the formal sector-labeled protected projector directly from
coordinates `(0,18,36)` and recomputes the gap. The current Level 2 scaffold is
classified `FORMAL_KERNEL_NOT_PROTECTED`; the old coordinate-first gap does not
survive the formal-projector audit.

v1.3L-O correct and package the formal-kernel `H_T` scaffold. The corrected
reference is `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL`, with coordinate-free
`K_formal = span{|ell,0,0,q=0,chi=-1>, |u,0,0,q=0,chi=-1>, |d,0,0,q=0,chi=-1>}`
and finite `k_max=4` realization `(0,18,36)`. Coordinate-first conclusions
depending on `(0,1,2)` are superseded. The full `H_T` theorem remains open.

## Unreleased / Development: BHSM Completion Campaign

Branch: `bhsm-completion-campaign`

The completion campaign packages v1.3 formal-kernel `H_T` results, adds
scheme-aware QCD/RG comparison scaffolds, strengthens scalar/topographic
decoupling scaffolds, and builds a unified dependency/theorem ledger. It does
not retune predictions and does not claim completed first-principles proof
unless every theorem dependency is explicitly closed.

Gate 2 adds the v1.4 QCD/RG matching scaffold. It records
`MIXED_DEFAULT`, `COMMON_SCALE_APPROX`, `THRESHOLD_AWARE_APPROX`, and
`PRECISION_QCD_PLACEHOLDER` reference sets, recomputes quark-ratio comparison
tables including dressed `c/t`, and keeps precision QCD as an explicit future
placeholder. Frozen BHSM ratios are compared but not changed.

Gate 3 adds the v1.5 scalar/topographic decoupling scaffold. The current
action-level scaffold distinguishes the SM Higgs projection from heavy,
screened, virtual, and forbidden scalar/topographic modes. It reports exactly
one light Higgs projection and zero current `OPEN_SCALAR_RISK` rows. Filtered
and screened topographic modes remain conditional scaffolds, not full
action-level scalar decoupling proof.

Gate 4 adds the v2.0 dependency graph and theorem ledger. The graph separates
frozen predictions, boundary-functional derivations, parent-action reductions,
basis realizations, semi-analytic scaffolds, finite-basis scaffolds, adoption
candidates, open items, and forbidden states. It reports no hidden circularity
or dependency on empirical residual machinery.

## Unreleased / Development: v1.4 Precision QCD/RG Matching

Branch: `bhsm-v1.4-precision-qcd-rg`

The v1.4 focused branch upgrades the quark-mass comparison architecture with
precision-oriented metadata, threshold-aware running scaffolds, uncertainty
propagation scaffolds, and placeholder shells for future PDG-style and
precision-QCD reference inputs. It does not change frozen BHSM predictions,
does not tune `a`, `S`, modes, tolerances, or `Z_virt`, and does not claim
precision quark matching is solved.

## Unreleased / Development: v1.5 Scalar/Topographic Action-Decoupling

Branch: `bhsm-v1.5-scalar-action-proof`

The v1.5 focused branch extends scalar/topographic decoupling toward an
action-level scaffold. It separates:

- `HIGGS_PROJECTED_LIGHT_MODE`;
- `HOPF_GAP_LIFTED`;
- `HT_COMPLEMENT_LIFTED`;
- `DERIVATIVE_SCREENED`;
- `CURVATURE_SCREENED`;
- `VIRTUAL_ONLY`;
- `FORBIDDEN_UNSCREENED_LIGHT_SCALAR`;
- `OPEN_SCALAR_RISK`.

The scaffold uses the corrected `DIRAC_PROXY_LEVEL_2_FORMAL_KERNEL`
dependency for H_T-linked scalar complement lifting and keeps the forbidden
unscreened light scalar channel as an explicit falsifier. It does not change
frozen BHSM predictions and does not claim full scalar decoupling from the
complete action.

Frozen baseline:

- Tag: `bhsm-v1.0-freeze`
- Commit: `03039feb14fb4c988edce8453f6ee5b234797eb2`
- Model branches:
  - `BHSM_BARE_V1`
  - `BHSM_DRESSED_V1_CANDIDATE`

## Included

- BHSM v1.0 frozen executable model framework.
- BHSM v1.1 technical note in Markdown, LaTeX, and PDF form.
- No-retuning prediction and falsification ledgers.
- Bare canonical branch and dressed-candidate branch.
- Manuscript appendices for constants, mode ledger, frozen outputs,
  falsification criteria, `H_T`/scalar scaffold status, and reproducibility.
- Release checklist, citation metadata, and all-rights-reserved license notice.

## Bare and Dressed Candidate Branches

`BHSM_BARE_V1` is the frozen alpha-anchored Berger-Hopf overlap model.

`BHSM_DRESSED_V1_CANDIDATE` applies `Z_virt^{u,2}=1/2` only to the middle
up-sector ratio `c/t`. It leaves `u/t`, CKM `sin_theta_13`, down-sector ratios,
lepton ratios, gauge outputs, Higgs/electroweak outputs, `H_T`, and scalar
outputs unchanged.

The dressed branch remains a candidate, not final canonical adoption.

## No-Retuning Rule

The v1.0 freeze is invalidated if `a`, `S`, the supplied mode ledger,
tolerance bands, or `Z_virt` are changed based on residuals.

## Current Limitations

- Full analytic twisted Dirac / `H_T` spectrum remains open.
- `H_T` no-extra-light-state theorem remains proxy/scaffold audited.
- Scalar/topographic decoupling remains scaffold audited, not fully proven from
  the action.
- Boundary operators `Omega_f` remain action-linked, not fully action-derived.
- Precision QCD/RG matching remains open.
- Dressed branch remains a candidate branch.

## Reproducibility

Run:

```powershell
python -m pytest -q
```

The v1.1 paper branch test status at release preparation is `281 passed`.
