# Internal physical-scope and normalization consistency review

Reviewed the tracker main manuscript, exterior derivation, projection theorem, current lens-response implementation and saved numerical record. This is an independent AI-assisted internal check, not external peer review. No main-manuscript edits were made. The root author is updating the nuisance family after this review, so its final numerical counts/spectra must be regenerated rather than copied from the earlier 28-nuisance output.

## Scientific assessment

The central physical chain is now explicit and defensible in its declared domain: supplied cubic R1 action and rolling homogeneous background; fixed weak-metric quasi-static scalar/metric constraint; supplied exterior scalar flux and normalized worldtube state; uniquely decaying linear multipole; fixed metric coupling; full-line phase and common lens potential; primary-image/flux/Fermat response; stated finite-family nuisance projection. The same mass is counted once. The new paper does not claim that this is a derived physical black-hole solution or that an observed response identifies a horizon.

The screened radial powers and hypergeometric response are established cubic-Galileon ingredients. The useful paper-specific work is the normalized composition, the estimator/shear null and actual information lost or retained under the declared data and nuisance family. The main text acknowledges that restriction and does not call an ordinary moving point-mass template a new lensing principle.

The physical-state amplitude is supplied and very faint. The reported picosecond-scale delay is a formal value of a truncated static model with a leading timing cancellation. It is explicitly not certified at that physical accuracy. Uncomputed time variation, unknown matching and ordinary lens/source propagation effects could matter more. The broad multi-million-year equivalent spatial scan is appropriately labeled an information experiment, not an observing proposal.

## Concrete consistency items reported to the root

1. The main manuscript originally inserted section headings before input files that already begin with section headings, producing empty duplicate sections. The root is correcting the wrappers/headings.
2. The normalized-STF projection theorem originally reused `N2=sqrt(15/(8pi))`, while the exterior provider uses the normalized explicit transverse mode `N2=sqrt(15/(16pi))`. Both are mathematically correct: `C_plus=diag(1,-1,0)/sqrt(2)` converts between them. The root is renaming the former `N_STF` and retaining the explicit transverse/axial basis normalization, so boundary amplitudes are not silently rescaled. In an orthonormal visible basis, `a_plus=sqrt(2)*a*s1`, `a_cross=sqrt(2)*a*s2`, and `a_axial=sqrt(3/2)*a*c`.
3. The initial information experiment varied but did not profile the central open scalar flux. The root is adding its monopole tangent. At a zero-quadrupole reference, this is the correct first-order flux nuisance; changing flux and quadrupole amplitude together is a higher mixed variation. Finite order-one changes of the flux still require the released family controls, and the `flux=0` rank collapse remains a real conditional limitation.
4. The transverse experiment is a stated two-coordinate boundary family. General STF projection retains a third visible, axial component; fixing it to zero is a physical assumption, not a line-of-sight null. The provider now supplies that component for a separate axial nuisance control. Starting with 28 listed columns, adding central scalar flux gives 29, and adding one axial boundary coordinate gives 30. Numerical rank may be lower than column count. Preserve both outcomes and the actual SVD spectra rather than describing the enlarged family using the old count.

## Axial projection supplied and checked

The added method `projected_axial(b_pc)` uses the independently normalized `Y20=sqrt(5/(16pi))*(3*n_z^2-1)`, returning the scalar-driven metric phase and its first two radial derivatives in pc, dimensionless units and pc^-1, per unit scalar boundary amplitude. It adds no arbitrary metric mode. For the reference exterior at 1000 pc it returns

```text
q0  = -4.030938800058792 pc
q0' =  0.0014208439989684405
q0''= -1.4313392748598807e-6 /pc.
```

Independent original-z quadrature agrees to `5.33e-15 pc`; centered derivative checks agree to `1.50e-12` and `5.63e-12` relative. The leading deep axial phase is logarithmic and mass-like. Its harmonic far-field leading term cancels under full symmetric projection. This is precisely why its nuisance status must be distinguished from both transverse spin-two response and central scalar flux.

The exact zero-flux identities now bypass interpolation: the transverse phase is `-4 beta N2 r0^3/(3b^2)` and the axial phase and derivatives vanish identically. Thus a residual from quintic interpolation does not masquerade as information in that degeneracy control. The provider's independent source-action, radial ODE, translation, phase/deflection and Hessian tests remain passing; the full receipt is `review/radial_response_provider_check.json`.

## Remaining limits to preserve in final claims

The finite nuisance family does not cover arbitrary extended quadrupolar density, unrestricted radial lens profiles, arbitrary source-frame transformations, changing distances, time-dependent lens multipoles or non-geometric flux propagation. The projection theorem already constructs an ordinary distributed quadrupolar envelope that can reproduce the screened angular phase, so the finite-family rank result cannot identify a gravity theory. A nonzero transfer and a fully identified exterior would still not identify a black-hole interior.

The exact projection nulls use a symmetric frozen full line. Finite endpoints, unequal weights, source motion and the cosmological completion can modify the projection; they must be calculated rather than claimed to recover hidden coordinates automatically. A positive leading scalar principal symbol establishes only the stated local leading conditions, not the full coupled nonlinear/horizon or ultraviolet problem. The whole weak-field worldtube remains outside an unresolved compact source.

The radial response for the selected homogeneous background is physically more constrained than an arbitrary phenomenological shear: its scalar-to-metric coefficient, transition scale once flux is supplied, boundary conormal normalization and one common potential are all fixed. That is the strongest defensible interpretation. The horizon flux, boundary amplitude, interior multipoles and microscopic BHSM common-action identification remain inputs or uncompleted maps.

Subject to updating counts and numerical results after the agreed flux/axial controls, no remaining serious normalization or physical-chain flaw was found in the reviewed conditional construction.
