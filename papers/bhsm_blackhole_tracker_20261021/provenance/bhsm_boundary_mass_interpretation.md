# BHSM interpretation of the ordinary compact-lens fit

This focused follow-up implements the user's clarification: ordinary lens fitting is useful when it has an explicit BHSM physical interpretation. A distinctive non-GR signal is not required for that interpretation. The recovered BHSM record actually adopts the Einstein/GHY gravitational sector, derives its spherical seam curvature, and evaluates a boundary charge. The mass fitted by the ordinary Weyl monopole can therefore be reported as the mass represented by those BHSM boundary quantities. This is a source-grounded dictionary, not a claim that a microscopic BHSM state or horizon flux has been derived.

No new inventory was undertaken. The direct sources below and the already-listed v14.25 ZIP member were reread; originals and checkouts were not modified. Full hashes, headings/line numbers and an independent identity check are in `bhsm_boundary_mass_interpretation_sources.json`.

## The strongest actual source chain

1. **`C:/Users/carbe/Downloads/BHSM_Galaxy_Gravity_Loaded_Schur_Hessian_v0_5.md`, §§1–2.** The owned input list begins with Einstein gravity and a GHY-completed boundary variation. Section 2 is titled “The gravitational load is a boundary curvature, not a new driver.” For a static spherical Schwarzschild spatial slice it derives
   `delta k_g(r) = [1 - sqrt(1 - 2m/r)] / r`, `m=GM/c²`,
   with `delta k_g = g_b/c² + O(m²/r³)`. This is an evaluated geometric map. Its later parent-threshold and coupled topographic Schur claims have additional conditions and are not needed to interpret the compact monopole.
2. **`C:/Users/carbe/Downloads/BHSM_Topographic_Galaxy_Encapsulation_Solution_v0_3.md`, §3.** The source derives the mixed surface invariant, with its Einstein normalization,
   `V_Sigma² = (c²/8pi) integral_Sigma H_Sigma Delta K_uu dA`,
   and obtains `V_Sigma²=GM_b/r_star` in the static spherical weak-field limit. It explicitly separates this boundary identity from the additional hypothesis that the invariant is exported as a scalar-topographic source. That distinction permits the ordinary boundary-mass interpretation without importing the unclosed extra export law or the galaxy's logarithmic total potential.
3. **`C:/Users/carbe/Downloads/BHSM_v14_25_seam_threshold_Brown_York_package.zip`, member `docs/BHSM_ETA_SEAM_THRESHOLD_BY_v14_25.md`, §§3–5.** The member was listed during the earlier bounded recovery and reread directly. Conditional on a time-symmetric spherical Einstein constraint, it evaluates the parent-relative charge
   `Delta Ehat_BY = (lambda/gamma_G)(sqrt(F0)-sqrt(F)) = 2 Ehat_matter/[sqrt(F0)+sqrt(F)]`,
   `F0=1-lambda²`, `F=F0-2gamma_G Ehat_matter/lambda`.
   Section 5 states the essential rule: after solving the Einstein constraint, this is the total matter-plus-gravity interface energy; a separate gravitational correction is not added on top. The source's small numerical witness is not a physical compact-object mass prediction.
4. **`C:/Users/carbe/Downloads/BHSM_optical_constitutive_reduction.tex`, “Static seam export.”** It carries the same surface amplitude into the optical source ledger and states its weak-field limit `Q_Sigma=V_Sigma²=GM/r_star`. Its proposed additional export and mixed metric response remain conditional. This source reinforces the normalization/dictionary but is not required to turn an already adopted ordinary monopole into an extra R1 force.

The source derivation is thus genuinely in the BHSM research record. Its conventional Einstein/GHY content remains conventional gravity; agreement with GR is exactly what this retained sector predicts. The dictionary should not be presented as a new derivation of Einstein gravity from the microscopic M8 fields.

## Exact local dictionary for the product

Adopt a nonrotating, isolated spherical vacuum exterior and a static timelike worldtube at a declared areal radius `r0>2m`:

`ds²=-f c²dt²+f^(-1)dr²+r²dOmega²`, `f=1-2m/r`, `m=GM/c²`.

For its outward normal and static observers,

`H(r0)=2 sqrt(f0)/r0`,
`kappa_acc(r0)=m/[r0² sqrt(f0)]`,

where kappa_acc is proper normal acceleration divided by c². Direct substitution gives the exact extension of the recovered weak-field surface identity:

`Q_Sigma(r0) := (c²/8pi) integral H kappa_acc dA = GM/r0`.

Therefore

`M = r0 Q_Sigma/G`.

Here Q_Sigma has velocity-squared units. With the common convention `K_ab=h_a^mu h_b^nu nabla_mu n_nu`, outward `K_uu=-kappa_acc`; the source's positive acceleration-like Delta K_uu must be matched to an explicit normal/reference convention. Using kappa_acc avoids silently changing its sign.

The source's exact curvature deficit gives another equivalent mass dictionary:

`delta k_g=(1-sqrt(f0))/r0`,
`M=(c²/G)[r0² delta k_g - (r0³/2) delta k_g²]`.

With a flat subtraction, Brown–York energy is

`E_BY=(c^4 r0/G)(1-sqrt(f0))`,
`M=E_BY/c² - G E_BY²/(2c^6 r0)`.

Its particularly stable mass-equivalent form is `E_BY/c² = 2M/[1+sqrt(f0)]`. Thus quasilocal energy changes when the enclosing radius/reference changes even if the conserved mass M does not. That is not a physical mass drift.

The exact Schwarzschild extension and inverse identities are independent calculations in this recovery; the historical source directly supplies the curvature deficit and weak-field mixed-invariant result. A dimensionless check over `r/m = 2.000001, 3, 10, 1000, 10^7` verifies all three identities at floating-point roundoff, with values retained in the JSON.

## The same Weyl response is counted once

In the usual weak local metric with dimensionful potentials, `Phi=Psi=-GM/R`, so `Phi+Psi=-2GM/R`. Its deflection is `alpha_hat(b)=4GM/(c²b)`. Replacing M by its boundary representation gives

`Phi+Psi = -2 r0 Q_Sigma/R`,
`alpha_hat(b) = 4 r0 Q_Sigma/(c²b)`.

These are the same field and the same lens potential. The product's mass, center and proper motion can be labeled as the mass and center/motion of the corresponding boundary/envelope representation in the retained BHSM gravitational sector. No independent “BHSM mass” or added force accompanies the already fitted Schwarzschild mass. A separately derived non-spherical or scalar contribution would enter the same total Weyl potential once and retain its own state/domain conditions.

For software, useful derived interpretation fields are the declared r0, compactness `2GM/(c²r0)`, spherical mean curvature, static acceleration-like curvature, `Q_Sigma=GM/r0`, and the reference-labeled Brown–York mass equivalent. They are conditional postprocessing of the fitted mass, not additional independently measured parameters. Their uncertainties must propagate the fitted mass and any declared uncertainty in the chosen physical r0; current distance/frame/worldtube calibration is supplied, not inferred. The computational default r0 must not be relabeled an observed physical surface.

## Assumptions and claim boundary

- The exact formulas concern static spherical vacuum worldtubes outside `2m`, with the stated observer and subtraction. They do not apply at or inside a null horizon. In the horizon limit H tends to zero while static proper acceleration diverges; the finite product does not create a dynamical horizon construction.
- A slowly moving fitted center can label a sequence of local rest-frame representations within the product's quasistatic approximation. It is not an exact causal moving-surface solution, nor permission to replace M by an arbitrary M(t).
- The asymptotically flat subtraction is a local model choice. A globally closed cosmological embedding has its own parent-relative reference and matching. The v14.25 expression supplies such a conditional charge formula but does not solve that astrophysical embedding.
- A fitted ordinary compact mass does not select its interior, prove a horizon, determine microscopic BHSM fields, or fix the R1 scalar flux or a surface-deformation amplitude. Those stronger questions remain separate from making the ordinary fit meaningful within the BHSM boundary interpretation.

**Recommended paper wording:** “In the retained Einstein/GHY sector of the BHSM boundary description, the inferred compact monopole is equivalently represented by the spherical boundary curvature/charge. For a declared static exterior worldtube, Q_Sigma=GM/r0 and the same M supplies the Weyl potential used by the lens fit. We count this contribution once. This establishes a BHSM boundary interpretation of the ordinary track; it does not select a microscopic state, horizon flux or additional deformation.”
