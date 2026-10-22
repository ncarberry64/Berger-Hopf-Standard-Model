# Final internal numerical and physical-chain review

Reviewed `manuscript/main.tex`, `manuscript/action_provider_appendix.tex`, `code/rotation_response.py`, its exact inherited effective-action/optical provider, `results/rotation_response.json`, the inherited SIS numerical record, and the independent Hopf/rigidity receipts. This is an AI-assisted internal check, not external peer review. Existing manuscript and scientific code were not edited by this reviewer. The direct synthetic matrix-ODE/sign check from the earlier review was retained rather than rerunning the entire physical pipeline unnecessarily.

## Verdict

No serious numerical or mathematical flaw was found in the central Hopf bound, the explicitly auxiliary rigidity theorem, or the conditional ordered R1 transfer bilinear. The manuscript now distinguishes those three domains correctly. The principal physical limitation remains real and explicitly disclosed: the microscopic BHSM-to-R1 normalized action/metric correspondence and state selection have not been derived. The new paper must remain conditional at that arrow. The known lensing commutator and affine equivalent-lens freedom are properly acknowledged.

One notation error was reported and corrected during review: the optical nodal tensors now read `(Z/sqrt(2)) direct_sum 0` and `(X/sqrt(2)) direct_sum 0` on `W direct_sum P`, consistent with `A|P=0`. The initial reversed direct-sum notation would have contradicted the node.

A minor scope clarification remains recommended at Eq. `lensrotation`: the displayed full matrix derivative assumes the local reduced Hessian L is prescribed and held fixed, as in the code's illustration. For a general fixed physical potential sampled at a perturbed impact/image, a further `-delta L` appears. This extra term is symmetric on the unperturbed isotropic distances, so it does not change the reported antisymmetric coefficient. State explicitly “for a prescribed fixed local Hessian L”, or write the equation for the antisymmetric part. This is a statement-scope repair, not a change to the numerical result.

## Numerical values checked against saved results

| Claim | Saved value | Assessment |
|---|---:|---|
| Closed-background K | `0.018` | Matches action manifest and harmonic normalization |
| Volume harmonic normalization N | `0.038315997065440505` | Equals `sqrt(6/(pi^2 R^3))`, `R=K^-1/2` |
| Density-pair rotation at source z=1 | `-9.982537934702104e-19` | Printed `-9.98254e-19` correct |
| Matter/reference-momentum rotation | `6.70643934873883e-14` | Printed `6.70644e-14` correct |
| Density-pair ordered quadrature difference | `5.147200024064406e-29` | Printed upper rounding `5.2e-29` correct |
| Temporal-provider refinement difference | `1.2096102819845874e-28` | Printed upper rounding `1.3e-28` conservative |
| Maximum direct finite-ODE coefficient difference | `4.225187849947129e-26` | Printed `4.3e-26` conservative |
| Common-profile finite-map skew | `3.3881317890172014e-21` | Printed `3.4e-21` correct; numerical null control |
| Reduced kinetic sampled minimum | `0.002484990502673359` | Printed `2.485e-3` correct |
| Auxiliary sampled maximum condition number | `102918.71085998723` | Printed `1.03e5` correct |
| Original scaled constraint residual | `2.9103830456733704e-11` | Printed “at most 2.92e-11” conservative |
| Physical-anchor reconstruction error | `2.220446049250313e-16` | Printed `2.23e-16` conservative |
| Density-pair sampled angular Phi/Psi bounds | `0.00043429115182226993`, `0.0004342911518221205` | Both below printed `4.35e-4` |
| Momentum-example sampled angular Phi/Psi bounds | `0.0018995143904275307`, `0.001899514390417177` | Both below printed `1.90e-3` |
| Sampled Volterra nu | `6.5583880886910185e-6` | Printed `6.56e-6` correct |
| Sampled higher-even-order estimate | `5.107166638670571e-27` | Printed `5.11e-27` correct; not a continuum/interval certificate |
| Fixed-L angular-source first-order skew | `6.821905801947945e-8` | Printed `6.82191e-8` correct |
| Centered finite-difference discrepancy | `1.92092872724008e-15` | Printed `1.93e-15` conservative |
| Fermat-weighted skew derivative | `0.0` | Consistent with exact symmetry identity |
| Inherited SIS baseline | `7.753621449299` days | Printed `7.753621449` correct |
| Inherited SIS linear delay coefficient | `-0.3532160902388808` seconds | Printed `-0.353216090` correct |

The new fractional-delay output times the saved baseline gives `-0.35321609024334805` seconds, agreeing with the inherited result to `4.47e-12` seconds. The selected state pairs are explicitly different preparations; the larger momentum response is not a precision improvement to the tiny density-pair response.

The corrected code indexes only the first two Newtonian rows for the Phi/Psi bounds. The separate all-row diagnostic includes matter/velocity rows and is not mislabeled as a potential. Angular bounds use an exact triangle inequality for the two normalized tensors and sampled temporal coefficients. They are not uniform time enclosures. The manuscript preserves that distinction and does not infer a universal ghost/gradient-stability theorem from the sampled kinetic block.

## Action, normalization and units

The appendix finite polynomial agrees term by term with the supplied `unreduced_lagrangian` and action blocks: auxiliary factors of two, `b2=8K/a^2`, `s2=5K/a^2`, fluid enthalpies, radiation w=1/3, and dust w=0 are consistent. The Schur blocks `M=M0-B^T A^-1 B`, `L=-B^T A^-1 D`, `V2=E-D^T A^-1 D` and canonical equations use the correct transpose/sign convention. Pi_reference is correctly distinguished from the coupled canonical p_zeta. Newtonian reconstruction includes the derivative of the shift row and propagated state, rather than treating that row as constant.

The cubic action `-2X Box(T)/lambda` and physical scaling `lambda=Lambda^3/(Mpl H0^2)` agree after `T_phys=Mpl T` and time rescaling. Background quantities and optical lengths are consistently dimensionless in H0=c=Mpl=1 units, with physical lengths restored by c/H0. The harmonic coefficients retain inherited volume-normalized units; equal coordinate magnitudes are not equal physical energies.

The round harmonic norm is correct: normalized-measure fourth moment gives `int F_A F_B dmu=tr(AB)/12`, and physical volume `2pi^2 R^3` with `N^2=6/(pi^2 R^3)` gives `int Q_A Q_B dV=tr(AB)`. The Berger volume changes by the constant a^-1, leaving normalized fractions unchanged. The paper correctly labels the mixed-sector spectral quantity as a Rayleigh quotient, fixes horizontal R for its derivative, and separately computes the fixed-volume derivative. It does not mistake the sign of the fixed-R derivative for a full-envelope-energy result.

The nodal transverse Hessians are `sqrt(2) N K Z` and `sqrt(2) N K X`, matching the inherited STF3 normalization. The shear integral and matrix ODE use the same `c_star=sqrt(2) N K`; no extra factor of two or vertex scale factor was found. `d_ab=a_b S_K(chi_b-chi_a)` and the three distinct vertex problems are consistent. The SIS baseline and fixed-physical-source derivative use the same lens body and source comparison.

## Central geometry and independent physical-chain assessment

The Hopf involution/projector proof is valid on real STF4. For a stationary node, `A=C direct_sum 0`, with nonzero real STF2 C. Compressing the complex structure to the transverse plane gives `tr(A J^T A J)=-kappa^2 tr(A^2)`, hence exactly `f2=(1+kappa^2)/2`. This is independent of transverse tensor orientation and amplitude, includes both orientation classes of J, and excludes any nonzero purely neutral nodal state. The theorem does not select a preferred Hopf structure at the round point.

The auxiliary free-scalar persistence proof is valid because its precise degree-two subspace is invariant under the Berger Laplacian. If the node persists, both A and its charged projection must lie in the nodal subspace; their difference is neutral and nodal and therefore zero. This forces kappa=1 for nonzero solutions when a!=1. The round exception, zero solution and isolated nodal times are correctly retained. None of this proves persistence under the different coupled R1 action or a full BHSM envelope action; the manuscript says so explicitly.

The ordered R1 Jacobi derivation has the correct sign and state normalization. Its antisymmetric second-order coefficient is independent of unknown symmetric second-order tides on an isotropic smooth reference segment. The restriction to that baseline is necessary and is stated. Optical twist remains zero; Jacobi-map antisymmetry does not violate the Wronskian. The common-profile null condition is sufficient, while independent inputs need not produce nonzero integrated rotation. Singular values in arbitrary anchor coordinates are correctly not treated as physical energy bounds.

The strong-lens mapping admits the stated common affine symmetrizer when transfers are common across images. Thus raw skew is not promoted to a source-independent observable, and the paper's mass-sheet/source-position qualifications are appropriate. The fixed-L example is a representation/consistency check. Absolute astronomical rotation, full nonlinear magnification/time delay, a squashed-spacetime optical prediction, and state amplitude selection remain outside the established result.

## Minor numerical-formality note

The displayed Volterra series is an infinite positive-tail bound. Code numerically sums even terms through order 18; at the reported nu the omitted next term is below `1e-153`, vastly smaller than the printed precision and floating-point uncertainty. For a formally rigorous arithmetic upper bound, add a geometric bound on the tiny remaining tail and outward rounding, using a uniform tidal supremum rather than the sampled maximum. The present manuscript already labels the numerical estimate sampled/noncertified, so this does not change its scientific conclusion or quoted numbers.

Overall: retain the explicit conditional claims and apply the fixed-L wording clarification. No numerical reparameterization, retuning, expanded uncertainty or new state selection is needed.
