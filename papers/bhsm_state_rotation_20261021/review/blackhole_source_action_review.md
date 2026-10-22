# Compact-source action review for the paper's Blackhole Tracker

This is a focused AI-assisted internal derivation/recovery check. It reads the specified local R1 derivation and its associated coefficient/optical code, the directly related common-source and remaining-field derivations, and three previously identified BHSM black-hole source notes. It does not restart the HE0435 campaign or claim a true black-hole solution. No manuscript edits were made.

## Result and legitimate scope

The frozen cubic R1 action supplies a normalized, nonzero scalar/metric exterior response for an ordinary minimally coupled finite matter source, including screening. Its compact-source exterior can support a reproducible weak-metric lens/trajectory tracker at impact radii much larger than the gravitational radius. The scalar coefficient is fixed by the actual rolling background and common metric constraint; it must not be replaced by a fitted scalar coupling.

The recovered result does **not** determine the scalar charge of a physical black hole. Regular-origin matter matching fixed the scalar flux in the published finite-body calculation. A vacuum exterior with a horizon instead requires horizon-regular, cosmologically matched scalar/metric data. The weak-metric exterior equation admits a flux integration constant until that interior/horizon problem is solved. The exact missing object is the horizon-to-overlap scalar/current and metric matching solution in the same rolling R1 theory. Label a tracker using the recovered matter charge as a compact-source or black-hole-candidate far-field proxy, with this charge/matching assumption explicit. It cannot model a shadow, photon ring, near-horizon ray, accretion response, or BHSM de-envelopment.

## Recovered action and normalized source pairing

The source action uses signature `(-+++)`, `c=hbar=1`, `Mpl^-2=8pi G`, and physical cubic coefficient `lambda=Lambda^3`:

\[
S=\int\sqrt{-g}\left[{M_{\rm Pl}^2\over2}R-{1\over2}(\nabla T)^2
+{(\nabla T)^2\Box T\over\lambda}-V(T)\right]+S_m,
\quad V=V_0-\mu^3T.
\]

The scalar Euler equation is

\[
\Box T+{2\over\lambda}\{\Pi_{\mu\nu}\Pi^{\mu\nu}-(\Box T)^2
+R_{\mu\nu}\nabla^\mu T\nabla^\nu T\}-V_T=0,
\quad\Pi_{\mu\nu}=\nabla_\mu\nabla_\nu T.
\]

Its sign agrees with the original background current `J=v+6Hv^2/lambda`, `Jdot+3HJ=mu^3`; no source sign is chosen to obtain attraction.

For a prescribed minimal, nonrelativistic point-matter source, `S_pp=-M int ds`. Varying the covariant metric gives `delta S_pp=(1/2) int sqrt(-g) T_pp^{mu nu} delta g_mu nu`, with `T_pp^{mu nu}=M int u^mu u^nu delta4(x-z(tau))/sqrt(-g) dtau`. In the local static limit `S_pp=-M int(1+Phi)dt+...`, so the normalized excess density is `delta rho=M delta3(r)` and `delta S_pp/delta T=0`. Scalar forcing is generated through the existing Ricci/braiding constraint, not through a new direct `T M` insertion. A minimally coupled fixed-mass worldline is a specified point-matter model; strong self-gravitating black-hole worldline sensitivities or dissipative horizon operators cannot be inferred from it.

Subtract the homogeneous R1 equations before adding the local excess. Freeze `v=Tbar_dot`, `d=Tbar_ddot`, and H during the encounter, use physical local radius r, and define

\[
b={2v^2\over\lambda},\quad A=1+{4(d+2Hv)\over\lambda},\qquad
2M_{\rm Pl}^2\Delta\Phi=\delta\rho-b\Delta\pi_T,\quad \Phi=\Psi,
\]

\[
A\Delta\pi_T-{2\over\lambda}[(\Delta\pi_T)^2-|\operatorname{Hess}\pi_T|^2]
+b\Delta\Phi=0.
\]

Eliminating that same metric constraint gives

\[
C\Delta\pi_T-{2\over\lambda}[(\Delta\pi_T)^2-|\operatorname{Hess}\pi_T|^2]
=-{b\over2M_{\rm Pl}^2}\delta\rho,\qquad
C=A-{b^2\over2M_{\rm Pl}^2}.
\]

One static reduced functional reproducing this retained scalar equation is

\[
S_{\rm QS}=\int dt\,d^3r\left[-{C\over2}|\nabla\pi_T|^2
+{|\nabla\pi_T|^2\Delta\pi_T\over\lambda}
+{b\,\delta\rho\,\pi_T\over2M_{\rm Pl}^2}\right].
\]

This displays the consumed scalar source pairing after the common metric constraint is eliminated; it is not an additional covariant matter interaction. For an additional physical cap/surface, the recovered exact source slot is `J_eff=J_T-b(rho+rho_Sigma)/(2Mpl^2)`. Its scalar variation J_T and metric density rho_Sigma require the actual surface action. A traceless source stress also requires a slip equation. The open BHSM surface-to-R1 map is not supplied by renaming one of those slots a black-hole luminosity.

## Tracker equations in physical/code units

Let `L_H=c/H0`, `x=r/L_H`, `mhat=(GM/c^2)/L_H`, `That=T/Mpl`, `vhat=v/(Mpl H0)`, `dhat=d/(Mpl H0^2)`, `lambdahat=lambda/(Mpl H0^2)`. Define the tracker symbol

\[
\boxed{\widehat\beta\equiv {b\over M_{\rm Pl}}={2\widehat v^2\over\widehat\lambda}},
\quad
C=1+{4(\widehat d+2\widehat H\widehat v)\over\widehat\lambda}
-{\widehat\beta^2\over2},\qquad p(x)={d(\pi_T/M_{\rm Pl})\over dx}.
\]

The historical source code calls this `b`, not `beta_hat`. It is distinct from the existing lens class's angular search-scale `self.b`. No factor of two should be hidden in the rename. For a regular finite source with enclosed mass fraction f(x), spherical integration gives

\[
\boxed{C x^2p-{4\over\widehat\lambda}xp^2=-\widehat\beta\,\widehat m f(x)},
\]

\[
\boxed{p(x)={-2\widehat\beta\,\widehat m f(x)\over
x^2[C+\sqrt{C^2+16\widehat\beta\,\widehat m f(x)/(\widehat\lambda x^3)}]}},
\qquad
\boxed{\Phi_x=\Psi_x={\widehat m f(x)\over x^2}-{\widehat\beta\over2}p(x)}.
\]

The selected root is continuous with the decaying linear source response and numerically stable against cancellation. For `C,lambdahat>0`, nonnegative f, it has `p<=0` and positive extra attractive force. For a point exterior set f=1 **only outside the unresolved source/interior**. The formal limit p~x^-1/2 at x→0 is not a regular center or a horizon boundary condition.

For the regular-source exterior,

\[
x_V^3={16\widehat\beta\widehat m\over\widehat\lambda C^2},\qquad
\epsilon_\infty={\widehat\beta^2\over2C},\qquad
\epsilon_F(r)={2\epsilon_\infty\over1+\sqrt{1+(r_V/r)^3}}.
\]

At `r>>rV`, `pi_T=pi_0+b GM/(Cr)` and `Phi=Phi_0-(1+epsilon_infty)GM/r` to the retained order. Additive scalar values and clock/potential normalization belong to the outer state, rather than independent time-delay fitting constants. Deep in screening, `p≈-sqrt(beta_hat lambdahat mhat/x)/2`, so `p^2/vhat^2≈mhat/(2x)`. The omitted spatial-gradient corrections are therefore controlled by weak compactness in this screened regime; they are not controlled at a horizon.

## Actual frozen coefficients

`scripts/r1_screened_review/r1_qs_coefficients.py:evaluate` and `code/strong_lensing_r1_screened.py:R1Coefficients.frozen` load the original background with no local parameter fit. At lens redshift 0.3 their saved receipt gives:

| Quantity | Saved value |
|---|---:|
| `That` | `0.09074930116446112` |
| `vhat` | `0.23776442637096692` |
| `H/H0` | `1.1836105771859786` |
| `dhat` | `0.24847158912363834` |
| `lambdahat` | `1` |
| `beta_hat = historical b` | `0.11306384489502991` |
| A | `4.24525027594442` |
| C | `4.238858559433196` |
| leading homogeneous time coefficient D | `4.396221028708471` |
| C/D | `0.9642050596983963` |
| epsilon_infty | `0.001507886243809552` |
| `c/H0`, H0=67.4 km/s/Mpc | `4447.959317507418 Mpc` |

The local scalar perturbation is `pi_T=delta T`, not the existing provider's time-displacement observable. The latter is `pi_time=-chi_ADM`; conversion from uniform-T gauge is `pi_T=-v pi_time`. Use the local scalar in these source equations and the reconstructed metric in photon equations. Substituting the scalar field directly as a metric or time-displacement column changes its normalization and physical units.

The source local principal calculation has positive leading `Kr`, `Kangular`, `Ktime` for nonnegative enclosed density on this branch. It also exhibits scalar radial characteristic speed squared up to about `1.47` in a screened exterior. Photons still follow the metric null cone. These are leading scalar characteristics, not full-system stability, near-horizon hyperbolicity or an ultraviolet causality certificate.

## Compact-source numerical scales and optical consequence

Scaling the saved 10^11 solar-mass receipt by `rV proportional M^(1/3)`, at z_l=0.3:

| M / solar mass | Schwarzschild reference radius 2GM/c^2 [pc] | rV [kpc] | H_l rV/c |
|---:|---:|---:|---:|
| 10^6 | `9.570831683e-8` | `4.568031176` | `1.215561931e-6` |
| 10^9 | `9.570831683e-5` | `45.680311759` | `1.215561931e-5` |
| 10^11 | `0.009570831683` | `212.029224977` | `5.642138685e-5` |

The Schwarzschild length is a reference compactness scale, not a derived horizon radius in R1. Strong multiple imaging can occur at impact parameters far outside that scale; a near-horizon solution is not required for every strong-lensing application.

For physical impact s, the same-action weak-local deflection is

\[
\widehat\alpha(s)={4GM\over c^2s}+\delta\widehat\alpha(s),\qquad
\delta\widehat\alpha(s)=4s\int_0^\infty{\delta\Phi'(\sqrt{s^2+z^2})\over\sqrt{s^2+z^2}}\,dz.
\]

Equivalently, for a point exterior,

\[
{\delta\widehat\alpha\over4GM/(c^2s)}
=\int_0^{\pi/2}\epsilon_F(s\sec\theta)\cos\theta\,d\theta.
\]

No new lensing coupling appears because `Phi=Psi` at the retained order. Integrating this deflection over impact gives the physical projected lens potential for relative delays; do not use epsilon_F(s) directly as a photon deflection or delay ratio. An independent scalar quadrature using the full screening transition gives the following **matter-charge-matched point-source illustration**, M=10^9 solar mass:

| s [pc] | GM/(c^2s) | force correction epsilon_F | projected deflection correction fraction |
|---:|---:|---:|---:|
| 1 | `4.785415842e-5` | `3.088907773e-10` | `8.061904807e-10` |
| 10 | `4.785415842e-6` | `9.767953408e-9` | `2.523831915e-8` |
| 100 | `4.785415842e-7` | `3.088591724e-7` | `7.725395524e-7` |
| 1000 | `4.785415842e-8` | `9.736398110e-6` | `2.187376643e-5` |

These are conditional scales, not detection claims. In the deep-screened asymptotic limit the projection/force ratio tends to `sqrt(pi) Gamma(1/4)/(2 Gamma(3/4))≈2.62206`; the tabulated values use the full transition. The infinity extension is a standard thin-lens matched-tail convenience, not a static solution out to infinity. At matching distance L>>max(s,rV), the omitted scalar deflection tail relative to `4GM/(c^2s)` is at most approximately `epsilon_infty s^2/(2L^2)` at leading order.

## Boundary conditions: regular source versus true black hole

The equation integrated in a vacuum exterior determines

\[
C r^2\pi_T'-{4\over\lambda}r(\pi_T')^2=Q_T,
\qquad
r^2\Phi'=m_{\rm metric}-{b\over2M_{\rm Pl}^2}r^2\pi_T'.
\]

For the recovered regular-body, minimally coupled solution, `Q_T=-b GM` and `m_metric=GM` follow from center regularity and the normalized volume source. For a horizon exterior, those equalities are not established by the exterior differential equations. The ADM/outer mass, scalar current/charge, rolling asymptotic state, accretion and horizon regularity must be related by an actual field solution. This does not prove that a black-hole charge differs, vanishes or is an arbitrary physical parameter; it identifies the unexecuted matching condition. Do not fit Q_T to recover a desired tracker signal or silently impose the star relation as a black-hole theorem.

The exact recovered current is `J^mu=U^mu+(2/lambda)(Pi^{mu nu}U_nu-Box(T)U^mu)`, `nabla_mu J^mu=-mu^3`. A constant-time static ansatz `T=vt+pi(r)` on an exactly static asymptotically flat metric does not inherit the rolling cosmological solution: its radial current grows as `-mu^3 r/3` after imposing center regularity, and the linear potential makes stress time dependent when `mu^3 v!=0`. The correct genuine horizon problem must retain time dependence or a controlled consistent local subtraction and horizon-penetrating regularity. Schwarzschild coordinates, regular-origin flux integration and an isolated static scalar ansatz do not supply that solution.

The supplied remaining-field note gives explicit polar-areal Einstein/scalar applications for `m(t,r),nu(t,r),T(t,r)`, including energy/momentum constraints and the exact current. Those are usable defining equations, but their horizon-regular common-state solution is not evaluated. The polar-areal patch itself assumes areal radius spacelike and therefore needs appropriate continuation at a horizon.

## Combining the tracker with angular states or source motion

The cleanest executed compact-source model uses the homogeneous frozen R1 background plus the sourced local response, with zero additional global harmonic state. Adding a nonzero cosmological harmonic is a separate controlled expansion, not exact nonlinear superposition. The recovered source-action equation for `pi=piL+piE` contains

\[
C\Delta\pi_L-{2\over\lambda}[(\Delta\pi_L)^2-|\Pi_L|^2]
-{4\over\lambda}[(\operatorname{tr}\Pi_E)\Delta\pi_L-\Pi_E:\Pi_L]
=-{b\rho_L\over2M_{\rm Pl}^2}.
\]

Even a metric-nodal ray can have nonzero environmental scalar Hessian. Its effective spatial tensor is `ZE^ij=C deltaij-(4/lambda)[(tr PiE)deltaij-PiEij]`. The independent check using the current round provider at z_l=.3, converting `piT=-v*pi_time` and its exact nodal Hessian, gives `||ZE-CI||/C≈7.8127e-7` for the existing matter/radiation pair and `6.0813e-5` for the matter/reference-momentum pair. These are local coefficient-expansion parameters, not certified errors of the full screened lens or global matching. A physical combined calculation must solve or bound the consumed contraction. A metric source-plane shear alone does not determine PiE.

For a tracker center z_c(t), translating the leading spherical QS solution to `r=|x-z_c(t)|` is a leading slow-motion approximation. A prescribed/synthetic path is an input. Minimal S_pp determines a geodesic in a supplied external metric once initial data are specified; it does not independently derive a binary orbit, self-force or accretion history. Require small source speed/c, weak metric along the light path, encounter duration short compared with background/coefficient variation, and finite outer matching. State velocity/retardation corrections omitted. Do not report an animated center prescription as action-selected black-hole dynamics.

A localized positive excess on a compact S3 cannot be exported by simply extending the flat static Poisson equation globally: its integral would require zero total excess. The actual outer curvature/time-dependent constraints, homogeneous response or specified compensation must be solved. This is not a prohibition on a local positive mass. The paper can use a controlled overlap worldtube and its existing smooth cosmological transfer while counting the local matter/metric contribution only once.

## Targeted BHSM black-hole leads

`BHSM_DRIVEN_HYPERSPHERE_BLACK_HOLE_FLUX_GATE_V14_81.md` explicitly rejects “black-hole activity implies local expansion/de-envelopment” without a derived source. `BHSM_MASTER_ACTION_BH_SUSCEPTIBILITY_V14_82.md` gives exact conditional response identities, e.g. `chi=C-DR[K^-1 b]`, while recording the physical BH/accretion/horizon source functional and susceptibility as undefined. `BHSM_VOLUME_WORK_CORE_SOFTENING_GATE_V14_83.md` gives a sign threshold under an outward dilation-work source but labels `B0(R)=R^7` a bridge-and-prove normal form. None supplies the missing R1 horizon charge or an observed black-hole source normalization. Positive energy/luminosity cannot be substituted for a derived outward spatial-work projection.

## Provenance

Historical source worktree: `C:/Users/carbe/Manuscript-Generation/.worktrees/strong-lensing-first-comparison-20261020`, current HEAD `4f044a6af5757f6f1c4e99e6547b43d6c45e353c`. The inspected five files have no local changes. Their content cites original action revision `49a1dabbe148f8ba9da4ac079a8d93fe97c5de76`; the four background-provider input hashes are preserved in the original coefficient receipt.

| Relative source | SHA256 |
|---|---|
| `docs/strong_lensing_r1_screened_20261020/R1_LOCAL_COUPLING_DERIVATION_20261020.md` | `C5AC9A69AC0F0AAF9443D8411A82367198353BC366815EC753C058E5C0E991D4` |
| `docs/strong_lensing_r1_screened_20261020/R1_REMAINING_FIELD_DERIVATION_20261020.md` | `6A8820FBE57D98F017273E1A81D83D26A71264A9C342E9AC5D999C0C83934A36` |
| `docs/strong_lensing_r1_screened_20261020/BHSM_COMMON_SOURCE_DERIVATION_20261020.md` | `2E86B4514B473153FB68B91C88492EE0367E52D3E963A0AEC7D8BD3855E16266` |
| `code/strong_lensing_r1_screened.py` | `3B60951D7D10C44B9F250991CE07A1264B6E0A9C1559EF63DFF350950706094C` |
| `scripts/r1_screened_review/r1_qs_coefficients.py` | `AAB0DA7634A1B60D590A2401575750CA33D5AE0144280B2533FDB0631AD58971` |

Scientific deliverable supported by this recovery: a transparent compact-source far-field tracking/lensing application of the existing R1 source response, with fixed source pairing and screening scales, plus an explicit horizon-boundary requirement before calling it a derived true-black-hole response. The later source records materially advance beyond a purely supplied shear coefficient; they do not close the microscopic BHSM source map or the black-hole horizon problem.

## Follow-up: exact screened exterior multipole transfer from the same action

This supplies a stronger finite closure than a standard moving point mass. It is a response theorem on the stated exterior worldtube domain, not a horizon solution.

Let pi0(r) be the above screened spherical exterior and p=pi0'. Perturb it by `delta pi=f_l(r)Y_lm(Omega)`, with `int |Y_lm|^2 dOmega=1`. The exact linearization of the retained quasi-static scalar equation is

\[
\delta E=Z^{ij}\partial_i\partial_j\delta\pi
=\partial_i(Z^{ij}\partial_j\delta\pi),\quad
Z^{ij}=C\delta^{ij}-{4\over\lambda}[(\Delta\pi_0)\delta^{ij}-\Pi_0^{ij}].
\]

The divergence form is an identity: `partial_i Z^ij=-(4/lambda)[partial_j Delta(pi0)-partial_i partial_i partial_j pi0]=0`. Therefore it is not legitimate to retain only a scalar replacement of C while discarding the anisotropic Hessian term. The spherical eigenvalues are

\[
K_r=C-{8p\over\lambda r},\qquad
K_\Omega=C-{4\over\lambda}(p'+p/r),\qquad
K_r'={2\over r}(K_\Omega-K_r).
\]

For an actual matter multipole `delta rho=rho_l(r)Y_lm`, the normalized forced radial equation is

\[
\boxed{{1\over r^2}(r^2K_r f_l')'-{l(l+1)K_\Omega\over r^2}f_l
=-{b\over2M_{\rm Pl}^2}\rho_l(r).}
\]

Outside the source the right side vanishes. The equivalent nondivergence equation is `Kr f''+2 KOmega f'/r-l(l+1)KOmega f/r^2=0`, with the derivative identity above supplying the equivalence. Both coefficients are positive on the chosen exterior branch.

### Exterior scaling, exact special function, and translation identity

For `rho=r/rV`, define `u=rho^-3`. In the exterior,

\[
K_r=C\sqrt{1+u},\quad K_\Omega=C{1+u/4\over\sqrt{1+u}},\quad
{K_\Omega\over K_r}={1+u/4\over1+u}.
\]

The deep-screening power equation is `s(s-1/2)-l(l+1)/4=0`, giving

\[
f_l\propto r^{(l+1)/2}\quad\hbox{or}\quad r^{-l/2}.
\]

At large radius the two branches are r^l and r^(-l-1). Thus a decaying l=2 perturbation behaves as r^-1 deep in the screened exterior and as r^-3 in the unscreened far zone. Those are radial transfer exponents; their amplitude comparison must use a common specified source/boundary pairing.

There is an exact decaying solution throughout the retained spherical exterior:

\[
\boxed{\mathcal R_l(\rho)=\rho^{-l-1}
\,{}_2F_1\!\left({l+1\over2},{l+2\over6};{2l+4\over3};-\rho^{-3}\right).}
\]

To verify it, use t=-rho^-3 and Euler derivative D=rho partial_rho. The ODE becomes `(1-t)D^2 f+(1+t/2)D f-l(l+1)(1-t/4)f=0`. Substituting `f=rho^(-l-1)H(t)` gives the hypergeometric equation with the displayed parameters. For l=2 they are `(3/2,2/3;8/3)`. Its dominant small-rho coefficient is

\[
\mathcal R_l\sim
{\Gamma((2l+4)/3)\Gamma((2l+1)/6)\over
 \Gamma((l+1)/2)\Gamma((l+2)/2)}\rho^{-l/2};
\qquad \mathcal R_2\sim1.9163774512813263\,\rho^{-1}.
\]

Translation is an exact independent check. A shifted center gives `delta pi=-delta z dot grad pi0`, so its l=1 shape must be `f1=-p`. This follows by differentiating the source-free background scalar equation, and explicitly from

\[
{}_2F_1(1,1/2;2;-u)={2\over1+\sqrt{1+u}},\qquad
\mathcal R_1(\rho)={2\rho^{-2}\over1+\sqrt{1+\rho^{-3}}}\propto-p.
\]

`review/check_compact_multipole_specialfunction.py` independently checks the l=1,2,3 special functions against the original radial differential equation on 151 points, `rho=1e-3...1e3`, using analytic hypergeometric derivatives. Maximum scaled residual is `2.09e-14`; translation agreement is `7.08e-16`. The measured l=2 endpoint logarithmic slopes are `-1.0000003180` and `-2.999999998875`. Its JSON receipt selects neither a horizon nor an amplitude.

### Worldtube normalization and source pairing

Choose a declared matching worldtube `r0` outside the material/horizon region and satisfying weak compactness, not a surface relabeled as a black-hole horizon. With Dirichlet datum `f_l(r0)=f0`, the isolated decaying exterior response is

\[
f_l(r)=f_0\,{\mathcal R_l(r/r_V)\over\mathcal R_l(r_0/r_V)}.
\]

The exterior quadratic scalar energy inherited from the same variation is

\[
E_l^{(2)}={1\over2}\int_{r_0}^\infty
[r^2K_r(f_l')^2+l(l+1)K_\Omega f_l^2]dr.
\]

Its outward conormal at the inner boundary of the **exterior domain** is negative radial, so its canonical source pairing is

\[
q_l=-r_0^2K_r(r_0)f_l'(r_0)=\Lambda_l f_0,
\qquad
\Lambda_l=-r_0^2K_r(r_0){\mathcal R_l'(r_0)\over\mathcal R_l(r_0)}>0,
\quad E_l^{(2)}={1\over2}\Lambda_l f_0^2.
\]

The prime in this expression denotes physical-r differentiation of the composed function `mathcal R_l(r/rV)`. With a fixed conjugate source q_l rather than fixed boundary field,

\[
f_l(r)={q_l\,\mathcal R_l(r/r_V)\over
 -r_0^2K_r(r_0)\,d\mathcal R_l(r/r_V)/dr|_{r_0}}.
\]

The positive energy proves uniqueness of the zero-data decaying exterior solution on this elliptic domain; it does not select f0 or q_l. Comparing screened and unscreened transfer at fixed f0 and comparing it at fixed q_l are different physical protocols. A true matter quadrupole requires the forced interior equation and its canonical flux matching; an unknown BH horizon requires its own action-owned boundary relation. Do not silently use a prescribed f0 as an action-derived black-hole quadrupole or import a Kerr mass quadrupole as a scalar charge.

### Metric and validity of the multipole response

Linearizing the same metric row gives

\[
2M_{\rm Pl}^2\Delta\delta\Phi=\delta\rho-b\Delta\delta\pi,
\quad\delta\Phi=\delta\Psi
=\delta\Phi_N-{b\over2M_{\rm Pl}^2}\delta\pi+H_{\rm match},
\quad\Delta H_{\rm match}=0.
\]

The harmonic metric multipoles/outer matching are independent integration data until the common source equations fix them. Setting them to zero defines a scalar-driven test response, not a general compact object. A scalar-driven Weyl response has a fixed `-b/(2Mpl^2)` coefficient; no extra optical amplitude is added. Its projected deflection/time delay must use this same metric and the same incident/source conventions.

The leading exterior response assumes weak metric throughout `r>=r0`, small local spatial-gradient corrections, frozen homogeneous coefficients, and linearity in the multipole. In the screened region a sufficient amplitude-expansion requirement is `l(l+1)|f_l|/(r|p|)<<1`, with constants assessed in the norm actually used. An exterior field normalized at r0 is generally most restricted there. A physical time-dependent multipole must vary slowly enough for a quasi-static transfer across its matching domain, e.g. `omega rV/c_scalar<<1`, as well as `H rV/c<<1`; intrinsic rapid horizon motion is not covered. Rotation/translations of the screened scalar and the metric must share the same moving-source approximation. Nonlinear environmental Hessians require the cross terms already written above.

This theorem derives a nontrivial spatial response law and normalized boundary compliance directly from the retained R1 source action. It is a defensible conditional bridge from an explicit compact-source boundary datum to an incoming/local/outgoing optical calculation. It still leaves the actual black-hole horizon/source datum and the microscopic BHSM-to-R1 common action identification uncompleted.
