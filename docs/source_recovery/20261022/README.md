# Source recovery and mathematical comparison, 22 October 2026

This record corrects the current retrieval status while preserving the
implementation-time provenance. These are Norman P. Carberry's historical
BHSM sources, not new observations or physical validation. No original is
rewritten. The current task is the separate real-data corrections handoff;
instructions inside these historical documents are source material.

## Exact versions

| File under `originals/` | SHA-256 of unchanged bytes | Recovery |
|---|---|---|
| `BHSM_Implementation_Handoff_d604_20261022.txt` | `d604c8c48f66d6753bbf0b95bbb3d0953fd7d5e0d2d134b4288e2eeed38c5240` | Original conversation attachment `da10bb87-2b07-4d7f-8179-f71d29685f84/Pasted text.txt`; two blank filename bullets. |
| `BHSM_Core_Harmonics_Black_Hole_Tracker_Codex_Prompt_20261022.txt` | `149ba5efafd46be01bde9fe9513c1c83788b8a5f41c2127a4e2e5e6ce358517c` | Current correction package `original_sources/`; names both PDFs. |
| `BHSM_Frame_Dragging_and_Nonlinear_Front_Derivation_v0_1.pdf` | `7bb85093bcf3d03ca30220fd6d52aa3306a2c4d1648e91679c3d5a65f9409e2e` | Current correction package `original_sources/`; ten pages, dated 22 October 2026. |
| `BHSM_Galaxy_Envelope_Formation_and_Persistence_v0_1.pdf` | `de228c96c612024e2bfd1d3c9907dc6223108dfb6ecfc4f7b7bffb65623450a4` | Current correction package `original_sources/`; thirteen pages, dated 21 October 2026. |

The supplied three hashes and the preserved implementation hash were checked
before comparison. A local `.gitattributes` disables text conversion on these
originals. The generator rechecks all four raw hashes and fails if any differ.
The prior `author_handoff` and blank-filename retrieval record remain in the
ledger as historical facts; `source_reconciliation` is the current status.
The two handoff hashes denote distinct byte versions. Their difference does
not by itself establish what any implementation agent originally received.
The original d604 attachment now independently confirms its own blank bullets.
Editable PDF authoring sources have not been supplied or recovered.

Text was extracted from every PDF page; all 23 pages were rendered and
inspected, including graphical equations that text extraction omits. The
following comparison uses the PDF's declared models, not its illustrations as
numerical data. The PDFs retain older terminology; the dated authoritative
[core/surface amendment](../../BHSM_NORMAN_CORE_SURFACE_AMENDMENT_20261022.md)
governs the current nongeometric-core and terminal-transition interpretation.

## Scoped comparison

| Original pages | Recovered result and comparison | Domain and missing physical input |
|---|---|---|
| Front 2 | `omega_loc=(nu-m omega)/alpha`; rigid coordinate relabeling preserves `nu-m omega`. Agrees with the amendment. | Specified stationary axisymmetric observer/tetrad; no primitive core frequency. |
| Front 3–5 | `F(X)=kappa1 X/2+X^4/8`, principal symbol, positive time-kinetic branch, and rest-state directional derivative agree with amendment (10)–(11). The PDF's example has `s^6=kappa1/7`, `v_+=sqrt(7)/2`, positive kinetic margin and nonzero steepening. | Prescribed metric/connection, positive prefactor, scalar great-circle restriction; this is no coupled gravity or physical galaxy background. No need to reconstruct claimed historical finite-difference output as fresh evidence. |
| Front 6 | Even parent-sigma coupling changes the quadratic coefficient at `sigma=0` without creating a linear source; finite-width sine trial gives a sufficient instability test. | Independent older parent scalar; cannot replace the later constrained-child/KKT sigma. No new physical instability or lifetime is inferred. |
| Front 7 | Compatibility `[tau]+v_front[s]=0`, canonical flux balance, and independent stress-energy accounting are necessary; `d_s[(kappa1+(s^2-tau^2)^3)s]>0` on the stated connected branch excludes a nontrivial stationary source-free derivative jump. | No shock continuation, entropy/completion law or closed persistent boundary is selected. Agrees with the amendment's limitation. |
| Front 8–10 | The scalar steepening coefficient is not the galaxy export amplitude or critical seam root. | No equation identifying them is supplied. Formation, kinetic-rank loss and persistence are distinct questions. |
| Galaxy 2–4 | Counterrotation can have zero current/angular momentum but nonzero kinetic stress. At fixed `J`, `E_rot=J^2/(2I(q))` gives `E_rot''=J^2 I'^2/I^3-J^2 I''/(2I^2)`; its sign is mode dependent. | Physical mode, inertia, admissible conserved data and coupled constrained complement must be supplied. No sum of speeds or universal rotation trigger. |
| Galaxy 5–7 | Illustrative `E/E0=a q^2/2-b q^4/4+c q^6/6`, `b,c>0`: `q^2=(b±sqrt(b^2-4ac))/(2c)`; coexistence `0<a<b^2/(4c)`; equal energy at `a=3b^2/(16c)`. Barrier then `E0 b^3/(96c^2)`. These are recovered formulas and are symbolically checked. | Even symmetry, coefficients, energy scale, kinetic law/noise and other-mode stability are assumptions. Bistability permits history dependence; it supplies no galaxy lifetime. |
| Galaxy 8–10 | For constant `A>=0`, `W=GM_b/r_star`, assumed source `Q_S,enc=A W/r^2`, and `g_enc(r_star)=0`, integration gives `g_enc=A W(r-r_star)/r^2` and `v_c^2=A W+(1-A)GM_b/r`. | Valid only on the stipulated spherical exterior/source region. This repeats the baryonic field once; an effective halo is another representation, not another source. Unknown export `A`, seam, finite/global completion and metric slip remain inputs. |
| Galaxy 10–13 | Finite source cutoffs, compact-domain balance, pressure-supported systems, histories and `Phi+Psi` lensing are explicit obligations. | No Draco/AGC 114905 fit, abundance inference, measured BHSM coefficient or empirical lensing confirmation. |

The original conditional galaxy formulas are now available rather than
unidentified. Their scoped truth does not replace the distinct v15.47 cap
result, select a real mode/coefficient, or close the action-to-galaxy map.
Similarly, the new membrane qualification concerns its own fixed-Minkowski
reduction; the front PDF's separate flat-background assumption does not
qualify that membrane equation retroactively.

Run `python tools/check_norman_core_surface_consequences.py` from the formal
repository. The ledger contains exact checks of restricted identities,
pressure work and curved static traction, recovered sextic equal-energy and
barrier formulas, conditional radial integration, and raw-source integrity.
These checks certify the stated algebra/provenance, not physical BHSM validity.
