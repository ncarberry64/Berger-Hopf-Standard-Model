# Berger-Hopf Standard Model: A No-Retuning Geometric Reinterpretation Framework for Standard Model Flavor, Couplings, and Generations

Norman P. Carberry  
Independent Researcher  
Oconomowoc, Wisconsin, USA  
ORCID: <https://orcid.org/0009-0000-6650-3485>

## Abstract

The Berger-Hopf Standard Model (BHSM) is a no-retuning geometric
reinterpretation framework for Standard Model flavor, couplings, generations,
and electroweak-scale structure. This paper packages the frozen BHSM prediction
set, claim ledger, falsification ledger, and reproducibility instructions for
public GitHub and Zenodo archival. Claims are deliberately separated into
derived-conditional, verified-test, strong-screen, proxy-audit, open, and
forbidden categories. The release does not claim experimental confirmation,
community acceptance, QCD confinement, quantum gravity, or a final replacement
of the Standard Model.

## Plain-Language Summary

BHSM treats some Standard Model patterns as if they are allowed notes of an
internal geometric instrument. The instrument is a Berger-Hopf internal
geometry. The notes are protected or screened internal modes. The project asks
whether a fixed, no-retuning geometry can organize flavor hierarchies, coupling
screens, generation structure, and no-extra-light-state constraints.

## Introduction

The Standard Model is empirically successful but contains many free flavor and
Yukawa parameters. BHSM is a conservative research framework that audits
whether a Berger-Hopf internal geometry can reinterpret some of those
structures. The repository is built as an executable audit: constants, modes,
and tolerances are frozen before comparison, and the claims ledger prevents
proxy or screen results from being upgraded into stronger statements.

## Motivation and Scope

The scope is limited to the repository evidence. BHSM supplies:

- a frozen charged-sector mode ledger;
- overlap-based mass-ratio screens;
- CKM and PMNS/effective-extension screens;
- gauge and electroweak-scale matching screens;
- H_T and scalar/topographic proxy or scaffold audits;
- falsification criteria.

The scope does not include experimental validation, QCD confinement, quantum
gravity, or a community-accepted replacement of the Standard Model.

## Mathematical and Geometric Setup

The canonical geometry and overlap width are frozen:

```text
a = alpha^{-1}/(12*pi^2) = 1.157054135733433
S = 1/(4*pi) = 0.07957747154594767
```

The Berger scalar spectrum proxy used in the audit is:

```text
lambda_{k,j}(a) = a^2 (k - 2j)^2 + 2((2j + 1)k - 2j^2)
```

The Hopf charge is:

```text
q = k - 2j
```

## Berger-Sphere / Hopf-Fibration Interpretation

The Hopf fibration supplies a fiber/base split. The integer pair `(k,j)` labels
the supplied internal modes, while `q` tracks Hopf charge. In this release, the
geometry is used as a frozen reinterpretation framework and screen generator,
not as a claimed first-principles derivation of the entire Standard Model.

## Charged-Sector Mode Ledger

| Sector | Heavy | Middle | Light |
| --- | --- | --- | --- |
| Charged leptons | `(0,0)` | `(5,2)` | `(9,3)` |
| Up quarks | `(0,0)` | `(6,0)` | `(10,1)` |
| Down quarks | `(0,0)` | `(6,3)` | `(8,2)` |

## Boundary Operators

The operational/action-linked boundary operators are:

```text
Omega_l = -q + 2j = 3
Omega_u =  q - 2j = 6
Omega_d =  q + 4j = 12
```

They are labeled `ACTION_LINKED` / derived-conditional in this release unless
the inspected repository branch proves a stronger status. They recover the
charged-sector mode ledger without using observed mass data, but the release
does not claim a full first-principles derivation of the Standard Model.

## Frozen Prediction Set

| Quantity | `BHSM_BARE_V1` | `BHSM_DRESSED_V1_CANDIDATE` | Changed |
| --- | --- | --- | --- |
| `c/t` | `0.008310500554068288` | `0.004155250277034144` | `True` |
| `u/t` | `1.2690463017606151e-05` | `1.2690463017606151e-05` | `False` |
| `s/b` | `0.021933971495439474` | `0.021933971495439474` | `False` |
| `d/b` | `0.0011165200546001757` | `0.0011165200546001757` | `False` |
| `sin_theta_13` | `0.0035623676140463315` | `0.0035623676140463315` | `False` |

## Bare and Dressed Prediction Branches

`BHSM_BARE_V1` is the alpha-anchored Berger-Hopf overlap model.

`BHSM_DRESSED_V1_CANDIDATE` applies the virtual-environment factor
`Z_virt^{u,2}=1/2` only to `c/t`. It leaves `u/t`, CKM `sin_theta_13`,
down-sector ratios, lepton ratios, gauge outputs, Higgs/electroweak outputs,
H_T rows, and scalar rows unchanged.

## No-Retuning Rule

Any post-freeze adjustment of `a`, `S`, modes, tolerance bands, outputs, or
`Z_virt` based on residuals invalidates the frozen prediction set.

## Coupling Outputs and Matching-Scale Caveats

| Quantity | BHSM output | Status |
| --- | --- | --- |
| `alpha_1` | `0.01688686394038963` | electroweak-scale matching screen |
| `alpha_2` | `0.03377372788077926` | electroweak-scale matching screen |
| `alpha_3` | `0.1182080475827274` | electroweak-scale matching screen |
| `sin2_theta_w` | `0.23076923076923078` | electroweak-scale matching screen |
| `alpha_em_inv_mew` | `128.30485721416164` | electroweak-scale matching screen |

Full higher-loop and threshold RG matching remains open/future work.

## Mass-Ratio Prediction Tables

| Quantity | BHSM output | Caveat |
| --- | --- | --- |
| charged leptons middle/heavy | `0.06007447093260976` | screen |
| charged leptons light/heavy | `0.00029729106456492414` | screen |
| up middle/heavy, bare | `0.008310500554068288` | quark scheme-sensitive |
| up middle/heavy, dressed | `0.004155250277034144` | candidate dressing only |
| up light/heavy | `1.2690463017606151e-05` | quark scheme-sensitive |
| down middle/heavy | `0.021933971495439474` | quark scheme-sensitive |
| down light/heavy | `0.0011165200546001757` | quark scheme-sensitive |

## CKM Status Table

| Quantity | BHSM output | Status |
| --- | --- | --- |
| `sin_theta_12` | `0.2256184580048353` | internal-rule screen |
| `sin_theta_23` | `0.04386794299087895` | internal-rule screen |
| `sin_theta_13` | `0.0035623676140463315` | internal-rule screen |
| `delta_cp` | `1.1283791670955126` | Hopf-phase CP screen |
| `J_CKM` | `3.1011702945437805e-05` | Hopf-phase CP screen |

## Higgs, H_T Gap, and Scalar-Decoupling Audit Summary

| Sector | Status |
| --- | --- |
| Higgs/electroweak scale | strong numerical screen |
| H_T no-extra-light-state gap | `PROXY_AUDIT` / open full spectrum |
| Scalar/topographic decoupling | finite-basis scaffold / open full action proof |

The H_T and scalar rows are not presented as completed analytic proofs in this
release unless a future branch supplies and documents stronger evidence.

## Test and Reproducibility Section

Run:

```powershell
python -m pip install -e .
python -m pytest
```

The release includes a dedicated integrity test:

```powershell
python -m pytest tests/test_final_paper_release_package.py
```

## Claim-Status Ledger

Claims are categorized as:

- `DERIVED_CONDITIONAL`
- `VERIFIED_TEST`
- `STRONG_SCREEN`
- `PROXY_AUDIT`
- `OPEN`
- `FORBIDDEN`

See `docs/claim_status_table.md` and `theory/claims_ledger.json`.

## Forbidden Claims

This release does not claim:

- a full derivation of the Standard Model from first principles;
- a proof of confinement;
- a proof of quantum gravity;
- a final replacement of the Standard Model;
- experimental confirmation by the particle-physics community;
- any post-data retuning.

## Limitations and Open Problems

Open or future work includes:

- full twisted Dirac/H_T spectrum beyond proxy/scaffold audits;
- scalar/topographic decoupling beyond current scaffold status;
- precision QCD/RG threshold matching;
- independent community review;
- external empirical validation.

## Falsification Criteria

The falsification ledger F1-F9 is summarized in
`docs/falsification_criteria.md`. In particular, F9 states that post-freeze
changes to `a`, `S`, modes, or `Z_virt` based on residuals invalidate the
frozen prediction set.

## How to Reproduce

See `docs/reproducibility.md`.

## Citation and Archival Information

Use `CITATION.cff`. Zenodo archival should be triggered through GitHub-Zenodo
integration after the GitHub release, if enabled. Do not manually invent a DOI.

## AI-Assisted Drafting Acknowledgment

AI-assisted drafting/coding support was used to organize repository artifacts,
tests, manuscript text, and release metadata. Scientific responsibility,
claim discipline, and release approval remain with the author.
