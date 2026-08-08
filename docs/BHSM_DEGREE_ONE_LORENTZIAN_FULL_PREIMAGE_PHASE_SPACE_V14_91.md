# BHSM v14.91 degree-one Lorentzian full-preimage phase-space gate

## Primary verdict

`BHSM_V14_91_THE_RETAINED_M8_P1_ETA_BLOCK_HAS_AN_EXACT_COMPACT_ROUND_DEGREE_ONE_IDENTITY_MAP_BRANCH_ON_THE_EXISTING_COEFFICIENT_LOCUS_KAPPA0_EQUALS_15_OVER_4_KAPPA1_TIMES_5KAPPA1_TO_THE_ONE_THIRD_AND_THE_HOPF_HEMISPHERE_SPLIT_HAS_A_SMOOTH_ZERO_FLUX_TRANSMISSION_DOMAIN;_BUT_THIS_LOCUS_IS_NOT_ACTION_SELECTED_AND_THE_INDEPENDENT_M4_GAUGE_DIRAC_SECTOR_HAS_NO_ACTION_OWNED_COMMON_DOMAIN_CRITICAL_VALUE_OR_VARIATIONAL_BUNDLE_INTERTWINER_WITH_M8,_SO_THE_REQUESTED_FULL_COUPLED_BVP_PHYSICAL_PROJECTOR_RELATIVE_TENSOR_SPECTRUM_DELTA_PI_CAP_INERTIAS_AND_B_DYN_L2_REMAIN_UNDEFINED`

This is a positive result for the compact parent Einstein--eta block and a
negative result for the requested full stratified boundary-value problem. The
two conclusions must not be merged.

The one next irreducible object is
`ACTION_OWNED_LORENTZIAN_M8_TO_M4_METRIC_ETA_GAUGE_DIRAC_COMMON_DOMAIN_CRITICAL_VALUE_FUNCTOR_WITH_VARIATIONAL_BUNDLE_INTERTWINER`.

## Canonical field and momentum ledger

The retained M8 phase space contains the spatial metric and its ADM momentum,
the scalar fields, and the constrained eta map. Lapse, shift, and the eta
multiplier are constrained variables. The physical gauge connection and the
adopted Dirac field are intrinsic or stratified M4 data; the repository has
not derived them as fields on the M8 full preimage.

| Field | Retained domain | Momentum/constraint | Full-preimage status |
| --- | --- | --- | --- |
| h_ij | spatial S7 in M8 | pi^ij=(kappa1/2)sqrt(h)(K^ij-Kh^ij) | owned |
| lapse N | M8 | p_N=0, Hamiltonian constraint | multiplier |
| shift beta_i | M8 | p_beta=0, momentum constraint | multiplier |
| chi | M8 | p_chi=sqrt(h) Zchi (1+g sigma^2) D_perp chi | owned |
| sigma | M8 | p_sigma=sqrt(h) Zsigma D_perp sigma | owned |
| eta | M8 | p_eta=sqrt(h)(1+g sigma^2)(kappa1+X^3)D_perp eta | owned, constrained |
| Lambda_eta | M8 | p_Lambda=0, eta.eta=1 | multiplier |
| A_physical | intrinsic M4 | electric flux and Gauss law after B1/candidate adoption | not an M8 field |
| Psi | intrinsic/stratified M4 | first-order Dirac constraints | no selected common domain |
| X_seam | candidate seam | none | not a retained canonical field |
| driver/environment | none | none | absent by v14.89 |

Thus the actual retained M8 canonical space is schematically the cotangent
space of

\[
\operatorname{Met}_+(S^7)\times\chi\times\sigma\times
\operatorname{Map}^{1}(S^7,S^7),
\]

subject to ADM, unit-norm, tangent-momentum, and diffeomorphism constraints.
There is no already-derived full stratified canonical product containing the
M4 gauge and Dirac sectors with their junction data.

## Degree and topology provenance

On every M8 spatial slice, the parent eta field has

\[
\eta_t:S^7_{\rm domain}\longrightarrow S^7_{\rm target},
\qquad [\eta_t]\in\pi_7(S^7)=\mathbb Z.
\]

The identity map is a degree-one representative. This is the parent M8/UV
degree. It is not a physical M4 Finkelstein--Rubinstein charge: the physical
M4 spatial eta candidate maps S3 to S6, and pi3(S6)=pi4(S6)=0.

For the quaternionic Hopf map p_H:S7 to S4, split the base into its two closed
hemispheres, S4=B4_plus union over S3 B4_minus. Then

\[
\widetilde C_\pm=p_H^{-1}(B^4_\pm),
\qquad
\widetilde\Sigma=p_H^{-1}(S^3),
\qquad
S^7=\widetilde C_+\cup_{\widetilde\Sigma}\widetilde C_-.
\]

Because each hemisphere is contractible, each cap is B4 x S3. The restricted
bundle over the equatorial S3 is trivial, so the lifted seam is S3 x S3.
Individual caps have boundary and do not carry independent absolute integer
degrees; the integer belongs to the glued closed map.

## Exact compact M8 Einstein--eta branch

Set chi=sigma=0, with U(0)=U'(0)=0, use unit lapse and zero shift, and take

\[
ds_8^2=-dt^2+a^2g_{S^7},
\qquad
\eta=\operatorname{id}_{S^7}.
\]

The domain and target round connections agree under constant rescaling, so
the identity is harmonic. Its energy scalar and density are

\[
X=|D\eta|^2=\frac7{a^2},
\qquad
F(X)=\frac{\kappa _1}{2}X+\frac18X^4.
\]

The eta multiplier supplies the normal component,
Lambda_eta=(kappa1+X^3)X. The stored stress formula gives

\[
\rho=F(X),
\qquad
p=\frac{X}{7}(\kappa _1+X^3)-F(X).
\]

For the static round product, G_tt=3X and
G_ij=-(15/7)X h_ij. The Hamiltonian and spatial Einstein equations reduce to

\[
3\kappa _1X-\frac{\kappa _0}{2}=\rho,
\qquad
-\frac{15}{7}\kappa _1X+\frac{\kappa _0}{2}=p.
\]

Adding them yields X^3=5 kappa1. Back-substitution gives

\[
\boxed{
X=(5\kappa _1)^{1/3},
\qquad
a^2=\frac7{(5\kappa _1)^{1/3}},
\qquad
\kappa _0=\frac{15}{4}\kappa _1(5\kappa _1)^{1/3}.
}
\]

The executable evaluator returns zero eta compatibility, Hamiltonian, spatial
Einstein, and momentum residuals to floating precision. This proves existence
on a codimension-one locus of existing coefficients. It does not prove that
retained BHSM axioms select that locus: kappa0 and kappa1 remain independent
primitives.

## Cap/seam variational and symplectic domain

Cutting the smooth S7 solution into Hopf hemispherical preimages does not add a
new seam field. The physical domain inherited from global smooth fields has
continuous metric, eta, chi, and sigma traces with opposite-outward-normal
canonical and conormal flux matching. The two internal GHY terms cancel
because the outward normals are opposite. The matter Green forms and the
gravitational canonical flux cancel pairwise. Therefore the sum of cap
symplectic fluxes is zero for restrictions of global smooth perturbations.

This derives a common transmission domain for the M8 block. It does not derive
a moving seam phase space, an independent seam oscillator, or the intrinsic
M4 junction domain.

## Why the requested coupled BVP is not owned

The exact M8 branch is not a full stationary solution of the stratified BHSM
action. Three previously established facts remain operative:

1. The physical M4 Yang--Mills connection is intrinsic and has no action-owned
   eta bundle/reduction intertwiner from M8.
2. The adopted Dirac sector has no selected common M8/M4 self-adjoint domain or
   state source.
3. The intrinsic M4 Einstein term changes the equatorial junction equation;
   the old smooth K_mu_nu=0 equator has a nonzero intrinsic Einstein reaction,
   and its shifted coupled background has not been solved.

Consequently no single retained Hessian or symplectic form exists for
(G,eta,A,Psi) on the requested common domain. Treating the sectors as a formal
block-diagonal sum makes the missing mixed variations zero by construction;
that is not the requested coupled theory and cannot be used as a physical
no-go for tensor modes.

## Downstream statuses

- Full stationary solution: not derived. The M8 Einstein--eta sub-block has
  the exact conditional branch above.
- Hamiltonian and momentum constraints: zero on the M8 branch.
- M4 Gauss and Dirac constraints: undefined on a common domain.
- Common Green form and symplectic flux: derived only for smooth M8
  transmission data.
- Gauge-reduced physical projector: undefined.
- Linearized coupled spectrum: undefined.
- Reflection-odd cap-relative tensor spectrum: kinematically allowed, not
  physically reduced.
- DeltaPi: undefined, not zero.
- M_plus and M_minus: undefined.
- Equal inertia and nu=1/4: v14.84 conditional theorem only.
- J_dyn and B_dyn,L2: undefined.
- Dynamic Schur response: ineligible for insertion.
- Complete L2 eigenvalues and first-instability ordering: not reached.
- Landau r,u,v, Goldstone locking, Floquet, and alpha-critical gates: not
  reached.
- CKM provenance remains
  `PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_OF_THE_SPECTRAL_CHARGED_CURRENT_KERNEL`.
- The family-noncentral left-handed current and PMNS/neutrino provenance remain
  open unchanged.

## Hindsight 20/20

Validated:

- the degree-one object is the global M8 map in pi7(S7);
- an exact compact round degree-one Einstein--eta stationary branch exists on
  an explicit locus of existing coefficients;
- the two full-preimage caps and lifted seam are actual Hopf domains, not new
  fluids;
- global smoothness supplies the zero-flux M8 transmission domain.

Invalidated:

- the stronger statement that the archive contains no compact analytic
  degree-one M8 candidate;
- assigning an independent integer degree to either cap;
- treating the currently retained cross-level action as the requested coupled
  metric--eta--gauge--Dirac BVP.

Reclassified:

- the primary obstruction is now full stratified action ownership and the M4
  junction, not absence of an M8 stationary point;
- M8 seam self-adjointness is a smooth-transmission theorem, while M4 common
  domain ownership remains absent.

Open, exactly:

`ACTION_OWNED_LORENTZIAN_M8_TO_M4_METRIC_ETA_GAUGE_DIRAC_COMMON_DOMAIN_CRITICAL_VALUE_FUNCTOR_WITH_VARIATIONAL_BUNDLE_INTERTWINER`

## Completion flags

```text
FULL_BHSM_COMPLETE = FALSE
MARK_III = NOT_REACHED
PHYSICAL_EXECUTION_BLOCKED = TRUE
USB_SYNCHRONIZATION_ELIGIBLE = FALSE
```

Frozen predictions and official prediction logic are unchanged. No CKM kernel,
measured input, fitted susceptibility, external driver, or new continuous
coefficient has been introduced.
