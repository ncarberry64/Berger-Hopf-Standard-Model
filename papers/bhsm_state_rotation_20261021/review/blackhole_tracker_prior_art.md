# Blackhole Tracker: targeted primary-literature and novelty audit

2026-10-21. Internal AI-assisted research review, not external peer review. Directed search, not an exhaustive priority search. No microscopic BHSM-to-R1 map, black-hole horizon, observational detection or novel general microlensing identity is assumed.

## Closest existing results

- **An isolated dark lens is already tracked by astrometric microlensing.** Sahu et al., *An Isolated Stellar-Mass Black Hole Detected Through Astrometric Microlensing*, ApJ **933**, 83 (2022), DOI [10.3847/1538-4357/ac739e](https://doi.org/10.3847/1538-4357/ac739e), [primary preprint](https://arxiv.org/abs/2201.13296). Combining source astrometry with a photometric parallax signal yielded a lens mass, distance and absolute proper motion. The paper's original reported mass should not be relabeled a new tracker prediction. Astrometric systematics and blending require real treatment; see also [Mróz, Udalski and Gould (2022)](https://arxiv.org/abs/2207.10729).
- **Mass/distance/proper-motion separation is established.** Gould and Yee, *Microlens Masses From Astrometry and Parallax in Space-Based Surveys: From Planets to Black Holes*, ApJ **784**, 64 (2014), DOI [10.1088/0004-637X/784/1/64](https://doi.org/10.1088/0004-637X/784/1/64), [full text](https://arxiv.org/html/1401.2463v1). Their equations (1)–(2) make the mass–distance–relative-velocity degeneracy explicit. A trajectory fit or long event duration alone does not determine a lens mass.
- **Correlated moving dark structures are already inferred from many source tracks.** Van Tilburg, Taki and Weiner, *Halometry from Astrometry*, JCAP **07** (2018) 041, DOI [10.1088/1475-7516/2018/07/041](https://doi.org/10.1088/1475-7516/2018/07/041), [primary preprint](https://arxiv.org/abs/1804.01991). It develops multi-source astrometric templates and correlations for positions, masses and kinematics of nonluminous pointlike and extended structures. A moving-center dark-lens map by itself is not a novel research contribution.
- **Strong-lens compact central masses are already reconstructed.** Nightingale et al., *Abell 1201: Detection of an Ultramassive Black Hole in a Strong Gravitational Lens*, DOI [10.1093/mnras/stad587](https://doi.org/10.1093/mnras/stad587), [primary preprint](https://arxiv.org/abs/2303.15514). Its central point-mass inference uses host/cluster mass models and source reconstruction. This is relevant to nuisance control and compact-mass recovery, not a precedent for tracking an isolated moving object or proving a horizon from arbitrary lens data.
- **Motion-dependent delay drift is established.** Dai and Lu, *Probing motion of fast radio burst sources by timing strongly lensed repeaters* (2017), DOI [10.3847/1538-4357/aa8873](https://doi.org/10.3847/1538-4357/aa8873), [full text](https://arxiv.org/html/1706.06103v2). Their source/lens/Earth motion decomposition and repeated-burst timing show that uniform relative motions produce delay drift; observer motion and nonuniform emission-point motion matter. A delay wobble cannot automatically be assigned to a changing lens envelope.
- **Time-dependent black-hole lensing is already modeled.** Pantig, *Time-dependent black hole lensing from ringdown quasinormal mode*, JCAP **07** (2026) 013, DOI [10.1088/1475-7516/2026/07/013](https://doi.org/10.1088/1475-7516/2026/07/013), [v3 full text](https://arxiv.org/html/2510.19849v3). This is a specified perturbed-Schwarzschild ringdown calculation, including time-dependent deflection/imaging and delays. A distinct R1 tracker must derive its own response; ringdown results cannot be imported as a generic envelope or horizon model.
- **Horizon-scale Kerr structure is a different regime.** Gralla and Lupsasca, *Lensing by Kerr Black Holes*, PRD **101**, 044031 (2020), DOI [10.1103/PhysRevD.101.044031](https://doi.org/10.1103/PhysRevD.101.044031), [primary preprint](https://arxiv.org/abs/1910.12873). Its critical parameters control highly bent image demagnification, rotation and timing. Weak-field moving-mass fits are not a substitute for this near-critical geodesic physics.
- **The relevant screened radial reduction is established, but must be specialized.** Kimura, Kobayashi and Yamamoto, *Vainshtein screening in a cosmological background in the most general second-order scalar-tensor theory*, PRD **85**, 024023 (2012), DOI [10.1103/PhysRevD.85.024023](https://doi.org/10.1103/PhysRevD.85.024023), [full text](https://arxiv.org/html/1111.6749v2). Section IV.1 treats the `G4X=0, G5=0, G3X!=0` class, including constant G4. Equations (39)–(45) give a screened scalar-gradient root and its metric response. The frozen R1 functions/background must determine those coefficients and the admitted root. The scalar gradient alone is not the light-deflecting Weyl potential.

## Known identities that a tracker must recover

For an isolated GR point lens, with calibrated angular units and no blended light,

\[
\theta_E^2=\kappa M\pi_{\rm rel},\quad
t_E=\theta_E/\mu_{\rm rel},\quad
\pi_E=\pi_{\rm rel}/\theta_E,\quad
M=\theta_E/(\kappa\pi_E),\qquad
\kappa=4G/(c^2\,\mathrm{AU}).
\]

The unresolved image centroid displacement relative to the unlensed source is \(\delta\theta_c=\theta_E\boldsymbol u/(u^2+2)\). Unknown source proper motion, parallax, acceleration, companions and astrometric-frame drift can absorb a slow signal. A known source distance and source/observer reference frame must be stated rather than silently supplied by a synthetic generator. Annual parallax or multiple observer baselines can help; incomplete or degenerate parallax fits do not automatically determine distance.

**Delays can also measure mass without parallax under specific assumptions.** Muñoz, Kovetz, Dai and Kamionkowski, *Lensing of Fast Radio Bursts as a Probe of Compact Dark Matter*, PRL **117**, 091301 (2016), DOI [10.1103/PhysRevLett.117.091301](https://doi.org/10.1103/PhysRevLett.117.091301), [primary preprint](https://arxiv.org/abs/1605.00008), treats the point-lens double-image delay. With u≥0,

\[
\Delta t=\frac{4GM(1+z_l)}{c^3}h(u),\qquad
h(u)=\frac{u\sqrt{u^2+4}}2+
\log\frac{\sqrt{u^2+4}+u}{\sqrt{u^2+4}-u}.
\]

The image flux ratio R>1 gives \(u=2\sinh[(\log R)/4]\). Thus delay plus flux ratio measures redshifted mass in this restricted model. If θE, source distance and lens redshift are also known, distance can be recovered without an annual-parallax measurement. Do not claim that such a mass estimator or the removal of this degeneracy is new.

For general strong lenses, source reconstruction, macro-profile, distance/time-delay-distance and line-of-sight freedoms remain. A mass-sheet transformation preserves image configurations and flux ratios but rescales delays. Independently known time-delay distance and absolute delays can constrain its scale; otherwise the usual mass/time-distance ambiguity survives. More source redshifts do not automatically remove every allowed transformation. Arbitrary time-dependent source trajectories or envelope templates can manufacture apparent tracking uniqueness.

## Most useful precise target

The most promising minimal paper is an **action-derived correction and identifiability analysis for a compact-lens tracker**, not another point-mass animation. First derive the screened radial Weyl potential from the specified R1 action and matched cosmological background. Then use the same potential for astrometry, image magnifications and Fermat delays, with a moving center and explicitly bounded angular multipoles. Give a concrete synthetic test with source motion/parallax, frame drift, ordinary external shear/convergence and realistic covariance admitted as nuisances. Show which mass, relative trajectory or envelope combination survives profiling over them.

An exact baseline diagnostic is

\[
\mathcal M_{\rm pm}(t)=\frac{c^3\Delta t(t)}{4G(1+z_l)h[u(R(t))]}.
\]

For a constant point mass in the slow-motion, frozen-lens limit this is constant for **arbitrary source/parallax trajectory and center translation**: those motions change u and cancel between the two observables. This is a consequence of the known point-lens equations, not a new general invariant. The useful new calculation would be its R1 screened/multipole response, error bound and surviving nuisance directions. Independently differentiating those equations gives

\[
\delta\log\mathcal M_{\rm pm}
=\frac{\delta\Delta t}{\Delta t}
-\frac{u^2+4}{4h(u)}\,\delta\log R,
\]

because h′(u)=√(u²+4) and d(log R)/du=4/√(u²+4). This removes baseline kinematic changes, but variable true mass, evolving macrostructure, microlensing, finite sources, absorption, blending and timing propagation can imitate its residual. It is an envelope diagnostic only inside a declared nuisance family, not a BHSM identification or horizon test.

Two additional exact conditional targets may help:

1. **Radial center constraint.** For independently known unlensed source positions βi(t) and any common axisymmetric radial law, αi=θi−βi is parallel to θi−c. Two nonparallel deflection directions determine c by line intersection regardless of the radial mass/envelope profile. Error grows as their angle becomes small. Unknown source tracks, external shear and multipoles invalidate this simple cancellation. This is standard radial geometry; the addition would be its demonstrated robustness/error bound for the actual R1 response.
2. **Screening-scale distance branches.** If the action fixes rV³=C M with known positive C, and data genuinely identify both θV=rV/Dl and a point-mass normalization θE², then, for Euclidean distances and known Ds,

\[
\theta_E^2=\frac{4G\theta_V^3}{c^2C}D_l^2(1-D_l/D_s).
\]

The right side is maximal at Dl=2Ds/3. Hence

\[
\theta_E^2/\theta_V^3\le16G D_s^2/(27c^2C),
\]

with two distance/mass branches below the maximum. This standard-ruler/mass-radius logic is an independently derived conditional branch theorem, not a claim that R1 data already measure a screening scale. A simulation confined deep inside the screened point-mass regime cannot identify θV merely because it was included in the fit. Cosmological distances require their own branch analysis. Actual R1 coefficient evaluation and noise/nuisance tests are the potentially substantive addition.

## Required physical and inference limits

- An instantaneous translated static profile is only a quasistatic approximation. Bound v/c, envelope change over the light-crossing and scalar sound-crossing times, image-delay sampling of different lens epochs, and the difference between observer epoch and lens crossing time. An arbitrary c(t) does not solve the full moving KGB equations.
- Choose a regular source/interior prescription, physical screened branch, asymptotic matching and metric normalization. Establish the radial domain of weak metric fields and of the effective theory. Keep the ordinary and envelope descriptions of the same stress/metric contribution from being added twice.
- The familiar estimate rV∝(GM/H²)^(1/3) can make stellar microlensing radii deeply screened. Compute the actual frozen R1 coefficients; do not tune a free screening radius to produce an effect. A conventional-gravity limit is scientifically valid even if it prevents measurable envelope tracking.
- Local identifiability requires the center/mass/envelope derivative columns, after projection off admitted source/frame/parallax/shear nuisances, to have the claimed rank. Profile likelihoods or singular directions should expose failures; strong priors and regularization do not turn a null direction into data information. The projection/rank identity is standard linear algebra; only its calculated application to the physical response can be new here.
- Identical metric/phase transfer on all probed ray domains yields identical lens data. In particular, unresolved spherical compact distributions with the same exterior response need not be distinguishable from a point mass. A dark compact lens can be a black-hole candidate, but this tracker alone does not establish a horizon, spin or an interior structure.

## Novelty verdict

Existing literature already supplies dark-lens mass/proper-motion recovery, multi-source dark-structure tracking, motion-induced delay drift, time-dependent black-hole lensing and screened cubic scalar–tensor radial solutions. A general “Blackhole Tracker” label does not establish originality. The defensible advance would be a **specialized, normalized action-to-Weyl-to-joint-data tracker**, with an exact motion-canceling correction or a nontrivial identifiability/branch theorem and an executed nuisance-controlled example. Keep any microscopic BHSM connection conditional unless it is actually derived. The older nodal-charge theorem may support envelope angular structure, but does not itself generate a compact radial lens or select its moving state.

## Targeted addendum: same-action screened quadrupole transfer

The subsequently proposed radial-deformation route has a plausible substantive optical application, but its scalar exponents have direct prior art:

- Brito, Terrana, Johnson and Cardoso, *The nonlinear dynamical stability of infrared modifications of gravity*, PRD **90**, 124035 (2014), [full text](https://arxiv.org/html/1409.0886v2), Section VII, equation (60), constructs nonspherical perturbations about a cubic screened spherical source. The text immediately after (60) and equation (61) explicitly gives outer `r^(-l-1)` and screened-exterior `r^(-l/2)` behavior. For l=2 these are r⁻³ and r⁻¹. It also explains that globally regular spherical sources do not sustain static nonspherical hair without a nonspherical source or boundary input.
- Chu and Trodden, *Retarded Green's Function of a Vainshtein System and Galileon Waves*, PRD **87**, 024011 (2013), DOI [10.1103/PhysRevD.87.024011](https://doi.org/10.1103/PhysRevD.87.024011), [full text](https://arxiv.org/html/1210.6651v2), Section III.2.1, equations (118)–(124), gives the static multipole radial equation and exact hypergeometric solutions. This is a strong independent analytical benchmark for the specialized radial solver after conventions are matched.
- Kobayashi and Takadera, *Unscreened multipole moments of the fifth force in the EFT of dark energy*, [arXiv:2607.09098](https://arxiv.org/html/2607.09098v1) (July 2026 preprint), extends nonspherical screening to broader theories. Appendix B, equations (109)–(113), includes the cubic Galileon multipole equation, outer boundary behavior and the two screened homogeneous powers `r^((l+1)/2)` and `r^(-l/2)`. Its beyond-Horndeski unscreening results must not be transferred to cubic R1 by name association.

Therefore claim neither a first multipole linearization nor a new screened r⁻¹ quadrupole exponent. The possible advance is deriving and evaluating **the fixed R1 metric response, normalized at a declared worldtube, projected into joint astrometry/magnification/delays and an estimator that cancels baseline translation**.

For a radial operator

\[
(r^2K_r f_l')'-l(l+1)K_\Omega f_l=0,
\qquad f_l(r_0)=1,\quad f_l(\infty)=0,
\]

positivity of the action-derived Kr,KΩ supplies a useful controlled-response check. A difference with zero boundary data obeys the integrated energy identity, so the decaying solution is unique when it exists. For l≥1 its positive normalized solution is monotonic decreasing, with

\[
-r_0^2K_r(r_0)f_l'(r_0)
=\int_{r_0}^{\infty}[r^2K_r(f_l')^2+l(l+1)K_\Omega f_l^2]dr>0.
\]

This standard Sturm–Liouville identity is a physical normalization/solver check, not a new mathematical discovery. Match the outer boundary within the domain of the quasistatic reduction or control the formal infinite-radius tail.

An exterior metric equation of the form `laplacian(delta Phi + b delta pi/(2 Mpl²))=0` admits a homogeneous harmonic metric multipole as well. Setting it to zero needs a matching/no-independent-material-quadrupole assumption. A stronger inference test retains the ordinary decaying mass quadrupole as a nuisance. A scalar Dirichlet amplitude alone must not silently fix every metric boundary constant.

There is a useful lens-projection distinction to calculate. For a transverse STF quadrupole `delta W=C(x²-y²)/r³`, corresponding to a screened r⁻¹ radial amplitude,

\[
\int_{-\infty}^{\infty}\delta W\,dz=2C\cos2\varphi.
\]

The leading projected phase is radially constant spin two, with zero radial deflection and tangential deflection proportional to `sin(2 phi)/b`. An unscreened r⁻³ radial amplitude instead projects as `4 C cos(2 phi)/(3 b²)` and deflects as b⁻³. These integrals are direct algebra, not a claimed new general lens law. The actual normalized transition solution, finite worldtube, line-of-sight tails, angular orientation and action-fixed metric coefficient must be integrated, and its template tested against ordinary mass quadrupole (`b^-2` projected phase), external shear (`b²`) and source reconstruction. Demonstrating a surviving measurable response across multiple impacts would be more consequential than quoting the known scalar exponent.

The prescribed boundary deformation is a conditional exterior state at r0≫rh. It establishes no relation to black-hole horizon shape, spin or hair. Keep that distinction explicit while using the compact dark object as the tracking target.

### Exact single-line-of-sight quadrupole null space

For the same quasistatic infinite thin-lens projection, a full three-dimensional STF boundary tensor C has additional restrictions. With line of sight z and sky impact b, write

\[
\delta W=f(r)C_{ij}x_ix_j/r^2,\qquad r^2=b^2+z^2.
\]

The Cxz and Cyz terms are odd in z and integrate to zero for **any** radial f. One line of sight therefore cannot determine all five three-dimensional quadrupole coordinates, even with arbitrarily accurate image positions, fluxes and static delays in this model. The observable projected family has at most the two transverse STF components and the axisymmetric Czz component.

For f=C*/r in the deep screened region, the Czz contribution cut at |z|≤Z is

\[
C_*C_{zz}\,[2\operatorname{asinh}(Z/b)-3Z/\sqrt{Z^2+b^2}]
\simeq C_*C_{zz}[2\log(2Z/b)-3].
\]

Its leading b-dependent phase is logarithmic, just as the compact point-mass phase. Thus deep-screen data may also trade Czz against the compact mass normalization. The actual transition and line-of-sight tails can distinguish that radial channel; they do not remove the exact odd-z null directions under the same symmetric projection. Finite endpoints, time variation during crossing, observer parallax or independent orientation information require their own calculation before claiming recovery of the full boundary tensor. These are useful precise limits for the tracker, rather than reasons to abandon recovery of its identifiable transverse deformation components.
