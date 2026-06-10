# Berger-Hopf Standard Model

BHSM = Berger-Hopf Standard Model.

This repository is the public research release for the completed BHSM internal
theorem package and the frozen no-retuning executable prediction set. BHSM is a
Berger-Hopf geometric reinterpretation framework for Standard Model flavor,
couplings, generations, and electroweak-scale structure.

BHSM is not presented here as an experimentally confirmed replacement of the
Standard Model. Empirical validation, precision QCD/RG comparison, and future
phenomenology remain separate from the internal theorem completion recorded in
this repository.

## Final Status

| Item | Status |
| --- | --- |
| Complete operator identification | `PROVEN` |
| Action uniqueness | `PROVEN` |
| Projector commutator control | `PROVEN` |
| Projector graph-domain stability | `PROVEN` |
| H_T lower-bound transfer | `PROVEN` |
| Index theorem | `PROVEN` |
| Mirror exclusion | `PROVEN` |
| Full H_T theorem | `FULL_HT_THEOREM_PROVEN` |
| Full BHSM theorem package | `FULL_BHSM_THEOREM_PACKAGE_COMPLETE` |
| Frozen outputs | `unchanged` |

## Frozen Model

The frozen model is immutable for this release.

| Quantity | Frozen value |
| --- | --- |
| Bare branch | `BHSM_BARE_V1` |
| Dressed candidate branch | `BHSM_DRESSED_V1_CANDIDATE` |
| Canonical geometry | `a = 1.157054135733433` |
| Universal overlap width | `S = 0.07957747154594767` |
| Virtual dressing rule | `Z_virt^{u,2}=1/2` for `c/t` only |

The dressed candidate changes only `c/t`; it leaves `u/t`, CKM
`sin_theta_13`, down-sector ratios, lepton ratios, gauge outputs,
Higgs/electroweak outputs, H_T status, and scalar outputs unchanged.

## Frozen Prediction Table

| Quantity | `BHSM_BARE_V1` | `BHSM_DRESSED_V1_CANDIDATE` | Changed |
| --- | --- | --- | --- |
| `c/t` | `0.008310500554068288` | `0.004155250277034144` | `True` |
| `u/t` | `1.2690463017606151e-05` | `1.2690463017606151e-05` | `False` |
| `s/b` | `0.021933971495439474` | `0.021933971495439474` | `False` |
| `d/b` | `0.0011165200546001757` | `0.0011165200546001757` | `False` |
| `sin_theta_13` | `0.0035623676140463315` | `0.0035623676140463315` | `False` |

## Reproduce

```powershell
python -m pytest -q
```

The final release validation on this branch passed the full pytest suite and
the frozen sanity check.

## Final Paper

The final paper package is in:

- `manuscript/BHSM_final_paper.md`
- `manuscript/BHSM_final_paper.tex`
- `manuscript/BHSM_final_paper.pdf`

## Cite

Use `CITATION.cff` for repository citation metadata. The release tag is:

```text
bhsm-final-theorem-v1.0
```

No Zenodo DOI is written into the repository unless Zenodo mints one after the
GitHub release.

## Branches and Tags

| Ref | Meaning |
| --- | --- |
| `main` | frozen v1.0 baseline history |
| `bhsm-final-paper-release` | final theorem paper and release package |
| `bhsm-v1.0-freeze` | frozen model tag |
| `bhsm-v1.1-preprint` | v1.1 preprint package tag |
| `bhsm-final-theorem-v1.0` | final theorem package tag |

## No-Retuning Rule

The frozen package is invalidated if `a`, `S`, the mode ledger, tolerance
bands, frozen outputs, or `Z_virt` are changed based on residuals.

## Limitations and Future Work

- Experimental confirmation is not claimed by repository theorem completion.
- Precision QCD/RG threshold matching remains future empirical/precision work.
- PMNS/neutrino rows remain effective-extension screens unless separately
  promoted by explicit model content.
- The release does not claim QCD confinement, empirical discovery, new particle
  discovery, or guaranteed publication acceptance.
- Zenodo DOI status is pending unless and until Zenodo mints one.

## License

All rights reserved. This repository is not released under an open-source
license. See `LICENSE.md`.
