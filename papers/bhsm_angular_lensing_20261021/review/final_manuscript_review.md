# Final scientific review of the standalone angular-lensing manuscript

## Decision and scope

**The central calculations and the stated conditional interpretation pass this review. Three small wording corrections are recommended before freezing the draft; none changes a calculated response or requires a new numerical experiment.** They are listed first below. No algebraic or receipt-level discrepancy was found in the nodal timing law, effective-potential correspondence, or restricted source-redshift contrast.

Reviewed sources: `manuscript/main.tex`, its angular-transfer, representation, and action-provider inputs, both generated tables, the bibliography, the saved angular/temporal/lensing receipts, and the independent SIS/geometry audit receipts. Primary literature was checked directly, including the arbitrary-background Fermat and equivalent-lens construction, generalized multi-plane mass-sheet freedom, full-sky spin-two optics, and the three-sphere harmonic reference. This is a scientific scope and consistency review of the supplied calculations. It is not independent empirical validation, a new derivation of the complete microscopic BHSM theory, a general stability analysis, or a journal decision. PDF visual inspection belongs to the separate build review.

## Three corrections to apply

### 1. Label the quoted image positions and delay as the unperturbed baseline

In “A finite illustrative preparation,” the manuscript says:

> The two continued images on the chosen axis lie at ... Their relative delay is ...

The quoted positions `+0.8331365` and `−0.6377768` arcsec are the `baseline_images` entries in `artifacts/lensing/nodal_sis_prediction.json`. The quoted `7.75362145` days is `baseline_delay_days`. The continued finite-map image positions for the illustrative state are instead approximately `+0.8331362774` and `−0.6377765966` arcsec. Both calculations are consistent, but their roles should be explicit.

Suggested replacement:

> The two unperturbed images on the chosen axis lie at ... Their baseline relative delay is ...

Keep the existing baseline numbers. The next displayed `−0.35321609 cos(2φ)` seconds then clearly supplies the first-order change from that baseline.

### 2. Distinguish the generally computed tracefree maps from the complete nodal maps in the Conclusions

The first conclusion paragraph says that the normalized Hessian and temporal responses give “the three propagation maps required for a local lens encounter.” On a generic sightline they give only their tracefree first-order parts. The nodal result then makes those parts sufficient for the complete retained first-order maps. The main technical sections already make this distinction correctly.

Suggested replacement:

> Combining that Hessian with the six physical temporal responses gives the tracefree parts of the three propagation maps required for a local lens encounter. On the specified nodal ray the scalar trace and endpoint responses vanish, making these the complete first-order map perturbations within the paraxial approximation.

For consistency, the abstract could likewise say “tracefree response matrices” before introducing the special nodal configuration. This is a useful precision improvement, not a change of result.

### 3. Avoid suggesting that the local body was solved from the propagated state

The opening paragraph currently motivates specifying “the same state throughout the incoming propagation, local lens encounter and outgoing propagation.” That can imply a globally matched state/body solution which this paper intentionally does not compute. The later scope statements correctly explain that the SIS is an independently prescribed local encounter, fixed while the smooth state changes.

Suggested opening replacement:

> This calculation carries one specified smooth environmental state through the incoming and outgoing propagation and combines it with an explicitly prescribed local lens encounter. It asks which linked optical quantities that preparation fixes.

This keeps the BHSM priority while accurately stating the achieved physical closure. No new microscopic source construction should be implied by the local SIS prescription.

## Claim-by-claim assessment

| Claim | Assessment and evidence |
|---|---|
| The full scalar `n=2` space has nine real modes, decomposing into sky dimensions `1+3+5`. | Correct. The ambient tracefree symmetric four-matrix construction gives dimension nine, Laplace eigenvalue `−8K`, and the stated angular decomposition. The reported volume Gram defect `3.4861e−14` agrees with `artifacts/angular_geometry_checks.json`. The general harmonic framework is established prior art. |
| Only the five quadrupoles contribute to the retained first-order smooth shear. | Correct for observer-centered radial background rays in this retained scalar sector. The tracefree screen Hessian kills the monopole/dipoles. The manuscript correctly preserves their possible trace/redshift/timing effects and the local lens's shear. This is an application of spin-two angular geometry, not a newly discovered BHSM-only selection rule. |
| Six temporal initial coordinates are retained per harmonic. | Correct as the specified gauge-fixed initial coordinates of the supplied finite action. The appendix provides the auxiliary elimination, canonical six-state evolution, and the full anchor conversion. It correctly distinguishes the reference momentum from the coupled canonical momentum. No universal two-state, rank-one, or state-selection claim remains. |
| The response coefficients are action-derived. | Supported within the declared R1 effective realization and the supplied finite quadratic action. The term must retain that qualification: neither a unique microscopic derivation of this effective action nor selection of its initial data has been established. The manuscript consistently says this. |
| The nodal ray gives a complete retained first-order timing comparison. | Correct within the stated weak smooth perturbation, fixed-body, nonconjugate, common-screen, paraxial experiment. The vanishing scalar quantities apply to the fiducial ray. The added finite-angle qualification prevents the claim being extended to exact image trajectories or nonlinear matching. |
| The SIS delay changes as `sqrt(2)[(g_os−g_ol)·y] cos(2φ)`. | Correct at fixed physical source displacement and physical SIS strength. The full stationary-image variation contains the time-matrix, source-angle, and physical-impact terms. The lens-to-source term cancels for this specified comparison. Independent SI and map-variation receipts agree. |
| The illustrative timing amplitude is `−0.35321609 s` at `(0.3,1)`. | Correct for the declared density coefficient `10^−3`, normalization, background, SIS, and physical source displacement. The manuscript explicitly states that this coefficient is not a uniform `0.1%` density perturbation and is neither observed nor dynamically selected. |
| A common spatial tensor makes the three smooth shears collinear. | Correct under that profile restriction. The general six-by-five preparation need not satisfy it. The numerical determinant below `1.01e−28` checks the algebraic factorization, not stochastic covariance, observable image-shape independence, or empirical evidence. |
| An effective ordinary lens potential preserves the one-source images and relative delays. | Correct with symmetric `T`, the transformed source `β_eff=Mβ`, and the stated common constant-map approximation. The transpose in the physical-potential gradient is retained. This is a constructive optical representation, not proof of full action equivalence or globally admissible density. |
| The two-redshift contrast can be nonzero. | Correct for the supplied shared state. It rules out absorption by one fixed physical main-plane quadratic contribution, with the other local potential, common `D_ol`, distance convention, and source transformation held as specified. It does not exclude distributed ordinary gravity or establish unique state recovery. |
| Multiple source redshifts and/or delay ratios identify BHSM. | Not claimed; correctly rejected. The nuisance-projected response design is local and conditional on a specified observational covariance/nuisance family. No such fitted inference is performed here. |

## Quantitative correspondence with the receipts

All quoted verification rows were checked against their corresponding saved fields:

- Harmonic normalization: `3.4861002973229915e−14`.
- Physical-anchor reconstruction: `2.220446049250313e−16`.
- Scaled original finite-action constraints: `1.4551915228366852e−11`.
- Green kernel versus forced Jacobi equation: `1.4513563961759957e−14`.
- Main versus refined temporal kernels: `1.466158195285311e−13`.
- Original angular equation, complex-step derivative: `2.080367128565186e−15`.
- Original angular equation, real half-step comparison: `5.700214605885989e−13`.
- Full image-solve delay derivative: `7.117306743964491e−12`.
- Independent SI baseline delay: `6.243489403967209e−16` relative discrepancy.
- Effective-potential identity in the main lens receipt: `2.0053203183808578e−16` after its stated scaling.

The independent geometry audit has its own slightly different control parameters and maxima. Its `2.53e−16` value residual must not be substituted for the main receipt's `2.01e−16` without changing the cited check. The manuscript currently uses the correct main-receipt number.

The four first-order principal-axis timing shifts and the table's signs agree with the saved lens records. The reported sampled metric amplitudes and matter speeds agree with the angular-geodesic audit and are appropriately described as sampled weak-field diagnostics, not rigorous global or nonlinear error bounds. The 33-point redshift scan and the specific two-redshift number are synthetic outputs, with no target data entering them.

For the redshift contrast, the recorded reduced density-coordinate coefficients are

\[
-3.7252233192178603\times10^{-4}
\quad\text{and}\quad
-3.074261762808943\times10^{-4}
\]

for source redshifts `1.0` and `0.6`, respectively. Their difference, multiplied by `sqrt(2)×10^−3`, is

\[
R_{11}=-9.205986616569894\times10^{-8},
\]

matching the displayed result and its declared order `s=1`, `t=0.6`.

## Independent assessment of the source-redshift argument

With `M_s=T_s/T0,s`, the exact effective potential is

\[
\psi_{\rm eff,s}(\theta)=a_s\hat\psi(D_{ol}\theta)
+\tfrac12\theta^TB_s\theta,
\qquad a_s=p_s/d_{ol},\quad B_s=I-M_s.
\]

A shared physical quadratic lens `δψ̂(x)=xᵀA_lens x/2` supplies the quadratic matrix `a_s D_olᵀA_lens D_ol`. Thus `B_s/p_s` must be source-independent for exact absorption by that particular common physical term. This algebra is sound. Its tracefree difference is a necessary obstruction when nonzero; a vanishing tracefree difference alone would not prove full absorption, since the trace must also be addressed.

The manuscript does not incorrectly turn this representation-level obstruction into a directly measured statistic. It retains source transformations, additional planes, nonquadratic lens freedom, and uncertain distance factors as relevant. This is the right claim boundary. The background source-redshift scaling is familiar lens theory; the calculated shared-state value and redshift curve are the model-specific outputs.

## Novelty and attribution

The defensible contribution is the **explicit composition of the specified R1 six-state propagator with the normalized full `n=2` angular sector, followed by linked three-map and fixed-source timing predictions**. The chosen nodal preparation makes a complete first-order conditional calculation possible with particularly transparent signs and null directions. Its coefficient table, redshift dependence, linked response, and reproducible independent formulations are substantive outputs even though the initial amplitude is conditional.

The spin-two selection rule, distance-matrix Fermat function, equivalent-lens/source transformation, and reduced physical-lens scaling are established mathematical ingredients. The Introduction correctly separates them from the new composition. The exact correspondence should continue to be described as an application of prior lens theory. Nothing in this review supports the claim that the conditional values are exclusive to BHSM, preferred by observations, or a verification of all BHSM dynamics.

An optional title refinement could emphasize the model-specific contribution more directly: **“Shared-State Angular Light Transfer and Strong-Lensing Time Delays in a Closed Berger–Hopf Effective Cosmology.”** The current title is acceptable because the abstract and Introduction explicitly state the conditional realization and attribute the angular geometry; changing the title is editorial rather than necessary.

## Primary sources checked

1. Fleury, Larena and Uzan, *Gravitational lenses in arbitrary space-times*, CQG **38**, 085002 (2021), [DOI](https://doi.org/10.1088/1361-6382/abea2d), [full text](https://arxiv.org/html/2011.04440v4). Sections 3.4–3.5 and Appendix B support the matrix arrival function, symmetry, source-only freedom, and equivalent-lens/source transformation. The source transformation is essential to obtaining a potential in the general case.
2. Schneider, *Generalized multi-plane gravitational lensing: time delays, recursive lens equation, and the mass-sheet transformation*, A&A **624**, A54 (2019), [DOI](https://doi.org/10.1051/0004-6361/201424881), [full text](https://arxiv.org/html/1409.0015v1). Section 4 supports the generalized transformation and common scaling of the delays. It does not support generic degeneracy breaking by ratios or several source planes.
3. Schneider and Sluse, *Source-position transformation: an approximate invariance in strong gravitational lensing*, A&A **564**, A103 (2014), [DOI](https://doi.org/10.1051/0004-6361/201322106), [author preprint](https://arxiv.org/abs/1306.4675). This supports retaining source-position freedom and avoiding unique-inference claims.
4. Bernardeau, Bonvin and Vernizzi, *Full-sky lensing shear at second order*, PRD **81**, 083002 (2010), [DOI](https://doi.org/10.1103/PhysRevD.81.083002), [full text](https://arxiv.org/html/0911.2244v2). Its first-order and spin-operator treatment supports the angular selection context; the manuscript is not claiming to reproduce its second-order physics.
5. Lindblom, Taylor and Zhang, *Scalar, vector and tensor harmonics on the three-sphere*, GRG **49**, 139 (2017), [publisher record](https://link.springer.com/article/10.1007/s10714-017-2303-y). The manuscript uses the correct official article number and DOI.

The two frozen Carberry repository sources are correctly marked as unpublished derivations/source code. They are provenance for the chosen effective realization, not independent observational corroboration. The intentional author-confirmation placeholder for funding and competing interests was left outside the scientific corrections.

## Final disposition

After the three local clarifications above, the manuscript supports a clear theoretical result: one explicitly prepared effective BHSM state gives linked angular and timing responses with reproducible numerical coefficients. The remaining microscopic selection, full nonlinear/body matching, general stability, and observational identification questions are stated as separate tasks. No new target-data application or expansion of the paper is needed to make the present conditional claims accurate.
