# The Berger–Hopf Standard Model: A Frozen v1.0 Geometric Reinterpretation of Standard Model Flavor, Couplings, and Generations

BHSM = Berger–Hopf Standard Model

Version: frozen v1.0 technical manuscript draft

Frozen baseline:

- Commit: `03039feb14fb4c988edce8453f6ee5b234797eb2`
- Tag: `bhsm-v1.0-freeze`
- Tests at freeze: `269 passed`
- Frozen branches: `BHSM_BARE_V1`, `BHSM_DRESSED_V1_CANDIDATE`

This manuscript is built from the repository audit ledgers and does not modify the frozen model.

# Repository and Reproducibility

This technical note is assembled from the private development repository for the Berger-Hopf Standard Model project. It is a manuscript artifact on the paper branch and does not alter the frozen model. The structure follows a reproducible-research posture: numerical screens, assumptions, limitations, and falsification criteria are kept in versioned files rather than being adjusted inside the manuscript narrative [Reproducible-Research].

| Item | Value |
| --- | --- |
| Repository | `https://github.com/ncarberry64/Berger-Hopf-Standard-Model` |
| Frozen tag | `bhsm-v1.0-freeze` |
| Model freeze commit | `03039feb14fb4c988edce8453f6ee5b234797eb2` |
| Manuscript branch | `bhsm-v1.1-paper` |
| QA test status | `275 passed` |

Reproducibility command:

```powershell
python -m pytest -q
```

# Abstract

The Berger–Hopf Standard Model (BHSM) is a no-retuning, alpha-anchored
geometric reinterpretation framework for Standard Model flavor, couplings,
generations, and electroweak-scale structure. This technical manuscript
summarizes the frozen v1.0 repository state at commit
`03039feb14fb4c988edce8453f6ee5b234797eb2` and tag `bhsm-v1.0-freeze`, where
the test suite passed with `269` tests.

The frozen construction fixes the Berger anisotropy
`a = alpha^{-1}/(12*pi^2)`, the universal overlap width `S = 1/(4*pi)`, and a
charged-sector mode ledger for charged leptons, up quarks, and down quarks.
It reports two declared branches: `BHSM_BARE_V1`, the pure alpha-anchored
Berger-Hopf overlap model, and `BHSM_DRESSED_V1_CANDIDATE`, which applies the
virtual-environment factor `Z_virt^{u,2}=1/2` only to the middle up-sector
ratio `c/t`.

The manuscript presents the frozen prediction tables, CKM and Hopf-phase CP
screens, PMNS effective-extension outputs, gauge/Higgs/electroweak screens,
the finite-basis `H_T` proxy gap audit, scalar/topographic scaffold status,
fixed tolerance bands, and falsification criteria F1-F9. It does not claim a
completed first-principles derivation of the Standard Model, a proof of the
full `H_T` no-extra-light-state theorem, or final canonical adoption of the
dressed branch.

# Introduction

The Berger–Hopf Standard Model (BHSM) is a frozen, no-retuning geometric
reinterpretation framework for Standard Model flavor, couplings, generations,
and electroweak-scale structure. The v1.0 freeze is not a new fit performed
inside this manuscript. It is the documented repository state at commit
`03039feb14fb4c988edce8453f6ee5b234797eb2`, tag `bhsm-v1.0-freeze`.

The purpose of this manuscript is to make the frozen repository outputs
readable as a technical note. The underlying code and ledgers already define
the model outputs, residual audit, virtual-dressing adoption audit, and
falsification ledger. The paper branch reorganizes those materials into a
linear presentation without changing the frozen model.

The Standard Model remains the reference low-energy quantum field theory for
the gauge and matter ledger used here [SM-Review]. BHSM is therefore not
presented as replacing the Standard Model. It is a frozen no-retuning
geometric reinterpretation framework whose outputs are compared against
standard phenomenological ledgers and reference quantities [PDG].

The core claim discipline is:

- BHSM conditionally reproduces the Standard Model gauge and matter ledger
  inside the admitted framework.
- Hypercharge and anomaly checks remain ledger-level and test-backed.
- Flavor outputs are internal-rule screens tied to the supplied mode ledger
  and overlap rule.
- Gauge and electroweak outputs are matching screens.
- `H_T` and scalar/topographic sectors remain proxy or scaffold audits.
- The dressed branch is an adoption candidate, not a final canonical model.

No post-freeze adjustment of `a`, `S`, the mode ledger, tolerance bands, or
`Z_virt` is part of this manuscript.

# Framework

BHSM = Berger–Hopf Standard Model.

The Berger–Hopf Standard Model is a no-retuning, alpha-anchored geometric
reinterpretation framework for Standard Model flavor, couplings, generations,
and electroweak-scale structure.

## Frozen Constants

The v1.0 freeze fixes:

| Quantity | Frozen Value | Status |
| --- | --- | --- |
| Berger anisotropy | `a = alpha^{-1}/(12*pi^2) = 1.157054135733433` | alpha-anchored canonical geometry |
| Universal overlap width | `S = 1/(4*pi) = 0.07957747154594767` | frozen overlap width |

The alpha-anchored geometry is selected by the theory-side rule recorded in
the model card: the BHSM scale sector contains
`epsilon_alpha = alpha^{-1}/(12*pi^2) - 1`. It is not selected by residual
minimization.

## Fixed Mode Ledger

| Sector | Heavy | Middle | Light |
| --- | --- | --- | --- |
| charged leptons | `(0,0)` | `(5,2)` | `(9,3)` |
| up quarks | `(0,0)` | `(6,0)` | `(10,1)` |
| down quarks | `(0,0)` | `(6,3)` | `(8,2)` |

The Hopf charge is `q = k - 2j`. The mode ledger is frozen and is not modified
in this manuscript.

## Overlap Rule

Charged-sector ratios are generated from the internal overlap form already
implemented in the repository:

```text
m_i/m_3 = exp[-S lambda_{k,j}]
```

where the Berger scalar spectrum proxy used for the overlap ledger is:

```text
lambda_{k,j}(a) = a^2 (k - 2j)^2 + 2((2j + 1)k - 2j^2)
```

The resulting numbers are screens from the frozen internal ledger, not fitted
mass parameters.

The use of an internal Berger-Hopf mode ledger places BHSM near a broad family
of spectral, higher-dimensional, and internal-geometric approaches to particle
physics [Spectral-Geometry], [Internal-Geometry]. The v1.0 repository does not
claim that those analogies prove the model; they provide context for why a
geometric mode ledger can be audited as a structured alternative to free
Yukawa inputs.

# Gauge and Field Ledger

The working model card records the Standard Model gauge group:

```text
SU(3)_c x SU(2)_L x U(1)_Y
```

The field ledger is:

| Field | Chirality | SU(3) | SU(2) | Y | Generations |
| --- | --- | --- | --- | --- | --- |
| `Q_L` | left | `3` | `2` | `1/6` | 3 |
| `u_R` | right | `3` | `1` | `2/3` | 3 |
| `d_R` | right | `3` | `1` | `-1/3` | 3 |
| `L_L` | left | `1` | `2` | `-1/2` | 3 |
| `e_R` | right | `1` | `1` | `-1` | 3 |
| `H` | scalar | `1` | `2` | `1/2` | profile `Phi(y)` |

The repository test suite verifies anomaly cancellation within this admitted
ledger. The ledger is a conditional BHSM input/output consistency layer; it is
not presented here as a rigorous derivation of the Standard Model from pure
geometry alone.

The symbolic low-energy Lagrangian blocks retained in the model card are the
usual gauge, fermion kinetic, Higgs, Yukawa, effective neutrino, and
topographic/internal sectors. The neutrino sector is treated as an effective
extension rather than as part of the minimal Standard Model.

The gauge and field ledger follows the usual Standard Model representation
bookkeeping [SM-Review]. Hypercharge and anomaly checks in the repository are
therefore ledger-consistency tests inside the admitted BHSM setup, not a claim
that the Standard Model gauge structure has been obtained without assumptions.

# Flavor Predictions

The frozen flavor outputs are generated from the fixed mode ledger and overlap
rule. The term prediction here means frozen model-output ledger entry, not a
claim of a completed first-principles derivation.

In the Standard Model, Yukawa matrices encode flavor masses and mixings as
inputs rather than as values fixed by the gauge symmetry alone. BHSM addresses
this familiar flavor-parameter problem by freezing an internal overlap ledger
and then auditing the residuals [Flavor-Problem]. The quark rows remain
scheme-sensitive because light, charm, bottom, and top mass references require
careful common-scale and scheme treatment [Quark-Masses], [PDG].

## Charged Fermion Ratios

| Sector | Heavy | Middle | Light |
| --- | --- | --- | --- |
| charged leptons | `1.0` | `0.06007447093260976` | `0.00029729106456492414` |
| up quarks, bare | `1.0` | `0.008310500554068288` | `1.2690463017606151e-05` |
| down quarks | `1.0` | `0.021933971495439474` | `0.0011165200546001757` |

In the mixed-default residual audit, charged lepton rows are scheme-stable,
while quark rows are marked scheme-sensitive. The worst mixed-default charged
fermion residual is `mass_ratio.up_quarks.middle`, with relative error
`0.13003176431657681`, and is classified as `SCHEME_SENSITIVE`.

## PMNS Effective Extension

The PMNS rows are effective-extension screens:

| Quantity | BHSM Output |
| --- | --- |
| `sin2_theta_13` | `0.021892057707851405` |
| `sin2_theta_12` | `0.3114412756254819` |
| `sin2_theta_23` | `0.5437841154157028` |
| `delta_m2_21_over_delta_m2_31` | `0.029189410277135206` |

These entries are not minimal-Standard-Model predictions. They are included as
effective neutrino-sector screens with explicit limitations.

The PMNS rows are framed as effective-extension outputs because neutrino
masses and mixings are outside the minimal Standard Model matter ledger used
for the charged-sector freeze [PMNS-Review]. They should be read as
extension-level screens, not as minimal-model predictions.

# CKM and CP Structure

The CKM angles are computed from the canonical BHSM mass-ratio screens:

```text
sin(theta_12) ~= sqrt(d/s)
sin(theta_23) ~= 2(s/b)
sin(theta_13) ~= sqrt(u/t)
```

The frozen outputs are:

| Quantity | BHSM Output | Residual Severity |
| --- | --- | --- |
| `sin_theta_12` | `0.2256184580048353` | `EXCELLENT` |
| `sin_theta_23` | `0.04386794299087895` | `MODERATE` |
| `sin_theta_13` | `0.0035623676140463315` | `MODERATE` |
| `delta_cp` | `1.1283791670955126` | `MODERATE` |
| `J_CKM` | `3.1011702945437805e-05` | `GOOD` |

The Hopf-phase CP screen is:

```text
delta_CKM = (q_u - q_d) sqrt(S)
```

with `q_u = q(10,1)`, `q_d = q(8,2)`, and `S = 1/(4*pi)`.

The frozen CKM matrix magnitude screen is:

```text
[[0.9742095600721029, 0.22561702639894465, 0.0035623676140463315],
 [0.2254664853946855, 0.9732628072432431, 0.04386766463774175],
 [0.008977584746899065, 0.04308671994825354, 0.9990309992869156]]
```

The CKM sector remains an internal-rule flavor screen. Full action derivation
of the boundary operators `Omega_f` remains open.

CKM mixing and CP violation are standard phenomenological targets for flavor
models [CKM-CP]. BHSM v1.0 freezes the angle rules and the Hopf-phase CP screen
before residual comparison. The CKM entries are therefore no-retuning screens,
not fitted post hoc matrix elements.

# Gauge, Higgs, and Electroweak Screens

## Gauge Couplings

The frozen geometric coupling screens are:

| Quantity | BHSM Output | Status |
| --- | --- | --- |
| `alpha_1` | `0.01688686394038963` | electroweak-scale matching screen |
| `alpha_2` | `0.03377372788077926` | electroweak-scale matching screen |
| `alpha_3` | `0.1182080475827274` | electroweak-scale matching screen |
| `sin2_theta_w` | `0.23076923076923078` | electroweak-scale matching screen |
| `alpha_em_inv_mew` | `128.30485721416164` | electroweak-scale matching screen |

The residual audit classifies `alpha_3`, `sin2_theta_w`, and
`alpha_em_inv_mew` as `EXCELLENT` against the available reference rows. Full
two-/three-loop threshold RG matching remains open.

## Higgs and Electroweak Scale

The frozen electroweak outputs are:

| Quantity | BHSM Output | Status |
| --- | --- | --- |
| `v_gev` | `246.16986520825228` | numerical screen |
| `m_H_approx_v_over_2` | `123.08493260412614` | zeroth-order screen |
| `M_lift` | `9718.396740299762` | Hopf lift scale |

These are electroweak-scale screens. They are not presented as an independent
proof of the Higgs sector.

The gauge-coupling rows are interpreted as electroweak-scale matching screens,
not constants at every scale. Higher-order threshold matching is left open in
the repository, and the quark-mass comparison pipeline separately records the
scheme dependence of running masses [EFT-Review], [Quark-Masses], [PDG].

# H_T Gap and Scalar Sector

## H_T Gap

The frozen repository records the `H_T` sector as a finite-basis proxy audit:

| Quantity | Frozen Output |
| --- | --- |
| Status | `PROXY_AUDIT` |
| Model level | `DIRAC_PROXY_LEVEL_2` |
| First complement eigenvalue | `1.4630400252994733` |
| First `H_T` complement gap | `19586.72266333732` |
| Target | `19585.25982625801` |
| Margin | `1.4628370793107024` |
| Passes proxy target | `True` |

The no-extra-light-state theorem remains open until the full analytic twisted
Dirac `H_T` spectrum replaces the finite-basis proxy scaffold.

The `H_T` audit is written in the language of finite-basis spectral bounds and
internal operators, which is naturally adjacent to spectral/internal geometry
programs [Spectral-Geometry]. The present result remains a proxy audit because
the full twisted Dirac spectrum has not been computed.

## Scalar and Topographic Sector

The scalar/topographic audit is recorded as a finite-basis scaffold:

| Quantity | Frozen Output |
| --- | --- |
| Status | `FINITE_BASIS_SCAFFOLD` |
| Passes scaffold | `True` |
| Light Higgs projection count | `1` |
| Mode count | `6` |

The Standard-Model-equivalent low-energy limit requires exactly one light
Higgs projection and no unscreened light direct-coupled scalar. The repository
currently audits that condition in a scaffold, not as a full action-level
proof.

# Bare vs Dressed Branches

The frozen v1.0 package declares two branches.

## BHSM_BARE_V1

`BHSM_BARE_V1` is the pure alpha-anchored Berger-Hopf overlap model. It uses:

- `a = alpha^{-1}/(12*pi^2)`
- `S = 1/(4*pi)`
- the fixed charged-sector mode ledger
- no virtual-environment dressing factors

## BHSM_DRESSED_V1_CANDIDATE

`BHSM_DRESSED_V1_CANDIDATE` uses the same frozen model, but applies:

```text
Z_virt^{u,2} = 1/2
```

only to the middle up-sector ratio `c/t` for pure-fiber middle up mode `(6,0)`.
It leaves `u/t`, CKM `sin(theta_13)`, down-sector ratios, charged lepton
ratios, gauge outputs, Higgs/electroweak outputs, `H_T`, and scalar outputs
unchanged.

| Quantity | `BHSM_BARE_V1` | `BHSM_DRESSED_V1_CANDIDATE` | Changed |
| --- | --- | --- | --- |
| `c/t` | `0.008310500554068288` | `0.004155250277034144` | `True` |
| `u/t` | `1.2690463017606151e-05` | `1.2690463017606151e-05` | `False` |
| `s/b` | `0.021933971495439474` | `0.021933971495439474` | `False` |
| `d/b` | `0.0011165200546001757` | `0.0011165200546001757` | `False` |
| `sin_theta_13` | `0.0035623676140463315` | `0.0035623676140463315` | `False` |

The virtual dressing adoption audit marks the rule as `ADOPTION_CANDIDATE`.
It is not `ADOPTED_CANONICAL_DRESSED`.

The dressed branch can be read as a controlled effective comparison layer:
the virtual-environment factor is applied before residual scoring, and its
scope is local to `c/t` [EFT-Review]. This is why the manuscript keeps
`BHSM_BARE_V1` and `BHSM_DRESSED_V1_CANDIDATE` separate.

# Falsification Ledger

The v1.0 package includes explicit falsification and weakening criteria. These
criteria protect the no-retuning status of the frozen branches.

| ID | Criterion | Status |
| --- | --- | --- |
| `F1` | If alpha-anchored `a` cannot be derived from the internal action, BHSM geometry weakens. | `OPEN_PROOF_OBLIGATION` |
| `F2` | If `Omega_f` cannot be derived from the twisted Dirac/bundle action, mass hierarchy predictions remain unsupported. | `OPEN_PROOF_OBLIGATION` |
| `F3` | If scheme-consistent quark ratios disagree beyond fixed tolerance bands, BHSM flavor mapping fails or must be revised. | `FALSIFIABLE_NUMERICAL_BRANCH` |
| `F4` | If canonical BHSM `V_us`, `V_cb`, `V_ub`, `delta`, and `J` fail outside fixed tolerances, BHSM flavor mapping is falsified or constrained. | `FALSIFIABLE_NUMERICAL_BRANCH` |
| `F5` | If neutrino ordering, octant, or phase decisively contradict BHSM effective-extension outputs, the neutrino branch fails. | `EFFECTIVE_EXTENSION_BRANCH` |
| `F6` | If the full twisted Dirac/`H_T` spectrum produces extra light states below `4*pi^2*v`, the SM-equivalent BHSM mapping fails. | `OPEN_SPECTRAL_THEOREM` |
| `F7` | If unscreened light scalar/topographic modes remain, BHSM fails as a Standard-Model-equivalent low-energy theory. | `OPEN_ACTION_LEVEL_PROOF` |
| `F8` | If higher-loop/threshold RG matching moves coupling agreement away from the electroweak scale beyond tolerance, the coupling branch weakens. | `OPEN_RG_MATCHING` |
| `F9` | Any post-freeze adjustment of `a`, `S`, modes, or `Z_virt` based on residuals invalidates the v1.0 prediction set. | `FREEZE_CONSTRAINT` |

## Fixed Tolerance Bands

| Class | Tolerance |
| --- | --- |
| `exact_status` | `pass_fail` |
| `gauge_couplings` | `0.01` |
| `higgs_electroweak_v` | `0.01` |
| `higgs_mass_zeroth_order` | `0.02` |
| `charged_lepton_ratios` | `0.25` |
| `quark_ratios_scheme_aware` | `0.25` |
| `quark_ratios_otherwise` | `SCHEME_SENSITIVE` |
| `ckm_angles` | `0.1` |
| `ckm_cp_jarlskog` | `0.1` |
| `pmns_effective` | `0.05` |
| `ht_gap` | `binary_pass_fail` |
| `scalar_decoupling` | `binary_scaffold_pass_fail` |

The frozen score summaries are:

- Bare: `{'PASS': 22}`
- Dressed candidate: `{'PASS': 21, 'SCHEME_SENSITIVE': 1}`

# Limitations

This manuscript preserves the repository claim discipline.

- The `H_T` spectrum remains proxy/scaffold audited, not analytically proven.
- Scalar/topographic decoupling remains scaffold audited, not established from
  the action.
- Boundary operators `Omega_f` are action-linked, not fully action-derived.
- Precision QCD common-scale running and higher-loop/threshold RG matching
  remain open.
- Quark mass comparisons remain scheme-sensitive unless a complete
  scheme-consistent running treatment is supplied.
- The PMNS sector is an effective-extension screen and is not part of the
  minimal Standard Model ledger.
- The dressed branch is an adoption candidate, not final canonical adoption.
- The manuscript does not claim a rigorous derivation of the Standard Model
  from pure geometry alone.
- The manuscript does not address Yang-Mills confinement.
- No numerical match is upgraded to a final prediction beyond its ledger status.

The v1.0 no-retuning rule is strict: changing `a`, `S`, the supplied mode
ledger, tolerance bands, or `Z_virt` based on residuals invalidates the frozen
package.

# Conclusion

The frozen BHSM v1.0 repository defines a reproducible no-retuning prediction
and falsification package for a Berger–Hopf reinterpretation of Standard Model
flavor, couplings, generations, and electroweak-scale structure.

The paper branch reorganizes that package into a technical manuscript. It
records the alpha-anchored geometry, universal overlap width, fixed charged
sector mode ledger, bare and dressed-candidate branches, CKM and CP screens,
PMNS effective-extension rows, gauge/Higgs/electroweak screens, `H_T` proxy
gap status, scalar scaffold status, fixed tolerance bands, and falsification
criteria F1-F9.

The main outcome is not a completed proof. It is a protected baseline: a
frozen model-output ledger and explicit failure ledger that can be audited
without retuning. The next technical work remains action-level derivation of
`Omega_f`, full analytic `H_T` spectral computation, scalar/topographic
decoupling from the full action, and precision QCD/RG matching.

# References

Verified bibliography entries for the BHSM v1.1 technical manuscript. Entries
below use stable, standard references where available. Bibliographic metadata
should still be checked against the target journal style before submission.

## [SM-Review]

- S. Navas et al. (Particle Data Group), "Review of Particle Physics,"
  *Physical Review D* **110**, 030001 (2024).
  DOI: `10.1103/PhysRevD.110.030001`.
  URL: `https://pdg.lbl.gov/2024/`.
- S. L. Glashow, "Partial-symmetries of weak interactions,"
  *Nuclear Physics* **22**, 579-588 (1961).
  DOI: `10.1016/0029-5582(61)90469-2`.
- S. Weinberg, "A Model of Leptons,"
  *Physical Review Letters* **19**, 1264-1266 (1967).
  DOI: `10.1103/PhysRevLett.19.1264`.

## [PDG]

- S. Navas et al. (Particle Data Group), "Review of Particle Physics,"
  *Physical Review D* **110**, 030001 (2024).
  DOI: `10.1103/PhysRevD.110.030001`.
  URL: `https://pdg.lbl.gov/2024/`.

## [Flavor-Problem]

- C. D. Froggatt and H. B. Nielsen, "Hierarchy of quark masses, Cabibbo
  angles and CP violation," *Nuclear Physics B* **147**, 277-298 (1979).
  DOI: `10.1016/0550-3213(79)90316-X`.
- G. Altarelli and F. Feruglio, "Discrete flavor symmetries and models of
  neutrino mixing," *Reviews of Modern Physics* **82**, 2701-2729 (2010).
  DOI: `10.1103/RevModPhys.82.2701`.
  arXiv: `1002.0211 [hep-ph]`.

## [CKM-CP]

- N. Cabibbo, "Unitary Symmetry and Leptonic Decays,"
  *Physical Review Letters* **10**, 531-533 (1963).
  DOI: `10.1103/PhysRevLett.10.531`.
- M. Kobayashi and T. Maskawa, "CP-Violation in the Renormalizable Theory
  of Weak Interaction," *Progress of Theoretical Physics* **49**, 652-657
  (1973). DOI: `10.1143/PTP.49.652`.
- C. Jarlskog, "Commutator of the quark mass matrices in the standard
  electroweak model and a measure of maximal CP nonconservation,"
  *Physical Review Letters* **55**, 1039-1042 (1985).
  DOI: `10.1103/PhysRevLett.55.1039`.

## [PMNS-Review]

- Z. Maki, M. Nakagawa, and S. Sakata, "Remarks on the Unified Model of
  Elementary Particles," *Progress of Theoretical Physics* **28**, 870-880
  (1962). DOI: `10.1143/PTP.28.870`.
- S. M. Bilenky and S. T. Petcov, "Massive neutrinos and neutrino
  oscillations," *Reviews of Modern Physics* **59**, 671-754 (1987).
  DOI: `10.1103/RevModPhys.59.671`.
- S. F. King and C. Luhn, "Neutrino mass and mixing with discrete symmetry,"
  *Reports on Progress in Physics* **76**, 056201 (2013).
  arXiv: `1301.1340 [hep-ph]`.

## [Spectral-Geometry]

- A. Connes, *Noncommutative Geometry*, Academic Press (1994).
  ISBN: `0-12-185860-X`.
- W. D. van Suijlekom, *Noncommutative Geometry and the Standard Model of
  Elementary Particle Physics*, Springer (2015).
  DOI: `10.1007/978-94-017-9162-5`.
- A. H. Chamseddine, A. Connes, and M. Marcolli, "Gravity and the standard
  model with neutrino mixing," *Advances in Theoretical and Mathematical
  Physics* **11**, 991-1089 (2007). arXiv: `hep-th/0610241`.

## [Internal-Geometry]

- T. Appelquist, A. Chodos, and P. G. O. Freund, eds.,
  *Modern Kaluza-Klein Theories*, Addison-Wesley (1987).
  ISBN: `0-201-09829-6`.
- J. M. Overduin and P. S. Wesson, "Kaluza-Klein gravity,"
  *Physics Reports* **283**, 303-378 (1997).
  DOI: `10.1016/S0370-1573(96)00046-4`.
  arXiv: `gr-qc/9805018`.

## [EFT-Review]

- C. P. Burgess, "An Introduction to Effective Field Theory,"
  *Annual Review of Nuclear and Particle Science* **57**, 329-362 (2007).
  DOI: `10.1146/annurev.nucl.56.080805.140508`.
  arXiv: `hep-th/0701053`.
- A. V. Manohar, "Introduction to Effective Field Theories,"
  *Les Houches Lecture Notes* **108** (2020).
  DOI: `10.1093/oso/9780198855743.003.0002`.
  arXiv: `1804.05863 [hep-ph]`.

## [Quark-Masses]

- K. G. Chetyrkin, J. H. Kuhn, and M. Steinhauser, "RunDec: A Mathematica
  package for running and decoupling of the strong coupling and quark
  masses," *Computer Physics Communications* **133**, 43-65 (2000).
  DOI: `10.1016/S0010-4655(00)00155-7`.
  arXiv: `hep-ph/0004189`.
- Z.-z. Xing, H. Zhang, and S. Zhou, "Updated Values of Running Quark and
  Lepton Masses," *Physical Review D* **77**, 113016 (2008).
  DOI: `10.1103/PhysRevD.77.113016`.
  arXiv: `0712.1419 [hep-ph]`.
- Particle Data Group, "Quark Masses" review in S. Navas et al.,
  *Physical Review D* **110**, 030001 (2024).
  DOI: `10.1103/PhysRevD.110.030001`.
  URL: `https://pdg.lbl.gov/2024/reviews/rpp2024-rev-quark-masses.pdf`.

## [Reproducible-Research]

- G. K. Sandve, A. Nekrutenko, J. Taylor, and E. Hovig, "Ten Simple Rules
  for Reproducible Computational Research," *PLOS Computational Biology*
  **9**(10), e1003285 (2013). DOI: `10.1371/journal.pcbi.1003285`.
- G. Wilson, J. Bryan, K. Cranston, J. Kitzes, L. Nederbragt, and
  T. K. Teal, "Good enough practices in scientific computing,"
  *PLOS Computational Biology* **13**(6), e1005510 (2017).
  DOI: `10.1371/journal.pcbi.1005510`.
