# BHSM v6.0.3 Energy--Geometry Confinement Invariant

## Claim-safe result

Primary result:

`BHSM_ENERGY_GEOMETRY_FINITE_INVARIANT_FAMILY_IDENTIFIED`

Threshold result:

`BHSM_PHYSICALITY_THRESHOLD_ARCHITECTURE_IDENTIFIED`

The v6.0.2 parent-action family permits a finite, branch-organized set of
quadratic sources for a physicality-order-parameter field. It does not select
one source, its coefficient, its sign, a physical signature, or a stable
formed phase. Consequently this sprint does not derive a unique
energy--geometry confinement scalar or physical spacetime formation.

The v6.0.2 results
`BHSM_B8_MINIMAL_ACTION_FAMILY_IDENTIFIED` and
`BHSM_ENERGY_GEOMETRY_PHYSICALITY_SOURCE_NOT_DERIVED` remain in force.

## Domain gate

The strongest admissible audit domain is a real bulk scalar on the parent
eight-manifold. A bulk field can in principle vary between core and surface,
support a finite-energy wall, couple covariantly to parent matter, and produce
a regular level set. A boundary-only scalar presupposes the boundary it would
be asked to generate. A collar field similarly presupposes a collar embedding.
A boundary-localized mode is treated as a spectral subbranch of the bulk
problem, not as an independent field domain. A fiber-dependent field remains
blocked until its associated bundle, connection, norm, and pushforward are
specified.

This is an audit-domain choice, not a BHSM selection of the physical domain.

## Quadratic action and operator

For a parity-even scalar and a Riemannian spectral branch, write the quadratic
action as

\[
 S_\sigma^{(2)}=\frac12\int_{M_8}d\mu_G\,
 \delta\sigma\,H_\sigma^{(0)}\delta\sigma
\]

with

\[
 H_\sigma^{(0)}=
 -\nabla_A(Z_0\nabla^A)+A_0+
 \Xi_{\rm geom}+\Xi_{\rm matter}+\Xi_{\rm boundary}
 +\Xi_{\rm collar}+\Xi_{\rm flux}+\Xi_{\rm other}.
\]

Its principal symbol is (Z_0G^{AB}k_Ak_B). Ellipticity requires a
Riemannian metric and (Z_0>0). In a Lorentzian branch the covariant field
equation is hyperbolic only after a causal domain has been selected; the full
d'Alembertian is not a bounded-below stability operator. Lorentzian stability
therefore requires a separately declared spatial or canonical spectral
problem. This sprint does not average the two signatures or derive one from
the other.

The natural inner product on the Riemannian compact branch is

\[
 \langle f,g\rangle=\int_{M_8}d\mu_G\,\bar f g.
\]

The Green boundary form is

\[
 \int_{\partial M_8}d\mu_h\,Z_0
 [\bar f\,n\!\cdot\!\nabla g-(n\!\cdot\!\nabla\bar f)g].
\]

Real Robin data, or matched Dirichlet/Neumann data, make this form vanish.
Interface transmission data need their own matched junction form. Until the
background, domain, and boundary conditions are selected, the operator is an
architecture rather than a physical spectrum.

## Action-native source families

### Curvature

An explicit term

\[
 \frac12\sigma^2(\xi_1R+\xi_2\mathcal L_2+\xi_3\mathcal L_3)
\]

contributes the displayed curvature combination to the Hessian. P1 can host
the (R) term, while P2 and P3 can host the higher Lovelock terms. These are
conditional geometric-scalarization sources. Curvature alone is not
"enclosed energy."

### Universal metric coupling

If parent matter couples to

\[
 \widetilde G_{AB}=A(\sigma)^2G_{AB},
\]

then its first scalar variation is proportional to
((d\ln A/d\sigma)T). Parity gives (A'(0)=0), and the quadratic source is

\[
 \Xi_{\rm matter}=\alpha_2T,
 \qquad
 \alpha_2=\left.\frac{d^2\ln A}{d\sigma^2}\right|_0.
\]

This source vanishes for trace-free matter. It cannot represent a universal
response to radiation without another action-native coupling. Stress
conservation also belongs to the full coupled-frame equations; it cannot be
checked from a symbolic trace alone.

### Matter Lagrangian

A term (f(\sigma)\mathcal L_m) gives (f''(0)\mathcal L_m), but its
threshold can change under an additive or representation change of
(\mathcal L_m). It is rejected as a physicality source until a theorem makes
that representation physical and closes the accompanying volume term.

### Stress composites and currents

(T_{AB}T^{AB}), its trace-free part, determinant/eigenvalue invariants,
(J_AJ^A), and (T_{AB}u^Au^B) require explicit composite-operator or current
actions. They generally introduce new dimensional normalizations. Stress
squares are not automatically positive in Lorentzian signature. An energy
density cannot be introduced by silently choosing a timelike (u^A).

### Interface and collar

A pressure jump is meaningful only after an interface, normal, two sides, and
junction variation exist. (K), (K^2),
\(\operatorname{Tr}(S^2)\), collar strain, and Jacobian terms become physical
Hessian sources only through independent interface/collar action terms.
Coefficient-locked GHY or Lovelock boundary completions are not adjustable
surface tension. A Gaussian-normal rewrite is not a second action.

### Top form

For a Euclidean convention (Z_F(\sigma)F_d^2/(2d!)), fixed local flux gives

\[
 \Xi_F=Z_F''(0)F_d^2/(2d!).
\]

Eliminating the form at fixed integrated charge produces the opposite
quadratic response when (Z_F'(0)=0). Fixed-(f) and fixed-(Q) ensembles
must therefore remain distinct. BHSM supplies neither a selected form action
nor a core source in this sprint.

## No unique scalar (C_{EG})

The surviving conditional source is a vector whose entries live on different
domains:

- local: curvature, stress trace, declared stress composites, local form norm;
- interface: pressure jump, extrinsic curvature and junction stress;
- quasilocal: enclosed energy, boundary Hamiltonian and integrated surface flux;
- global: total top-form flux or connected-core charge.

No symmetry or parent-action theorem combines these into one scalar. Enclosed
energy is not local until a surface, normal, time flow, and quasilocal energy
definition are supplied.

## Harmonic constructive-interference selection hypothesis

The proposed harmonic/octave selection rule can be stated without guessing a
new local invariant. Project the action-derived Hessian onto its normalized
modes:

\[
 H_{mn}=(Z_0k_n^2+A_0)\delta_{mn}+C_{mn},\qquad
 C_{mn}=\langle f_m,\Xi_{\rm total}f_n\rangle.
\]

Constructive interference can select a physical channel only if the parent
action produces nonzero off-diagonal overlaps, their relative phases or signs,
and a control variable that drives an eigenvalue through zero. A relation such
as \(\omega_m/\omega_n=2^p\) is admissible when it is derived from the spectrum
and is dimensionless. Grouping values by decimal orders of magnitude is not by
itself a covariant action law; it becomes physical only if a logarithmic
spectral or renormalization structure derives the grouping. The present
repository does not yet contain the complete spectrum or coherence matrix, so
this remains a candidate selection theorem for v6.0.4.

## Spectral threshold and finite size

The physical eigenvalue is the lowest non-gauge, normalizable eigenvalue of a
declared self-adjoint problem:

\[
 H_\sigma^{(0)}f_n=\lambda_nf_n.
\]

The undifferentiated branch is locally stable for
(lambda_{\rm phys}>0), marginal at zero, and unstable below zero. For a
simple normalized eigenmode and action-derived control (c), the crossing
direction is

\[
 \frac{d\lambda_{\rm phys}}{dc}
 =\langle f_0,(\partial_cH)f_0\rangle.
\]

No such control variable is selected here.

For a finite region,

\[
 \lambda_0(L)=\frac{Z_0q_0^2}{L^2}+A_{\rm eff}(L)
 +\lambda_{\rm boundary}(L)+\lambda_{\rm collar}(L).
\]

Only in the restricted case of constant negative (A_{\rm eff}) and no
extra surface shifts does

\[
 L_c=q_0\sqrt{Z_0/(-A_{\rm eff})}
\]

follow. The dimensionless (q_0) depends on geometry and boundary data; a
homogeneous Neumann mode has (q_0=0). This expression does not generate an
absolute unit because its coefficients are unsourced.

## Nonlinear branch and wall

Projecting onto one normalized unstable mode gives

\[
 S(q)=\frac12\lambda_{\rm phys}q^2+\frac14g_{\rm eff}q^4+\cdots.
\]

For (lambda_{\rm phys}<0) and (g_{\rm eff}>0),

\[
 q_\pm=\pm\sqrt{-\lambda_{\rm phys}/g_{\rm eff}},\qquad
 \Delta S=-\lambda_{\rm phys}^2/(4g_{\rm eff}),
\]

and the formed-mode curvature is (-2\lambda_{\rm phys}>0). This proves
stability only in that one projected direction, not in the coupled theory.

For the planar idealization
(U=G(\sigma^2-v^2)^2/4), (A<0), (G>0), and (Z>0),

\[
 \sigma(\rho)=v\tanh[(\rho-\rho_0)/\delta],\quad
 v=\sqrt{-A/G},\quad
 \delta=\sqrt{2Z/(-A)},
\]

\[
 \tau=\frac{2\sqrt2}{3}\frac{\sqrt Z(-A)^{3/2}}G.
\]

This is a conditional Z2 wall formula. A (0\to\sigma_{\rm surface})
envelope requires a different phase-coexistence potential or source and has
not been constructed. No collar endpoint or thickness is assumed.

## Emergent interface and coupled phase

A candidate level set

\[
 \Sigma_{\rm phys}=\{x\mid\sigma(x)=\sigma_*\}
\]

is a physical interface only if (sigma_*) is action-derived, the level is
regular, its induced metric is nondegenerate, and its normal, extrinsic
curvature, localized stress, and junction equations all follow from one
action. These gates remain open. The imposed (S^7) boundary is not relabeled
as emergent.

The coupled Hessian must include scalar modes, overall scale, nested squashing,
interface displacement, and relevant matter or flux collective modes. No
stationary background or absence-of-negative-modes theorem exists yet.

## Parent matter and v5 reduction

A symbolic conserved stress tensor is sufficient to display a trace-source
screen, but not to vary the coupled nonlinear phase. Selecting an energy
trigger requires a covariant parent matter action with declared signature and
an independently justified scalar coupling. Composite stress, current,
pressure-jump, and flux candidates need their own additional source data.

Recovery of

\[
 V_{\rm red}=-\sigma^2+2\sigma^4,
 \quad A_{ST}=-2,\quad G_{ST}=8,\quad |\sigma|=1/2
\]

requires normalized mode projection, fiber/collar pushforward, a quadratic
matrix element, a quartic overlap, and an amplitude map. The structure is
compatible but blocked. None of these v5 numbers is used as a parent input.

## Separate thresholds

Physicality formation uses (H_\sigma^{(0)}) about (sigma=0). Primordial
release uses a surface operator about an already formed compact enclosure.
Black-hole de-enveloping uses a coupled topology/envelope Hessian near a
throat or core interface. They have different backgrounds and cannot share an
eigenvalue by assertion. Shared-core language remains structural compatibility
only.

## Stop condition

`V6_0_3_STOP_FINITE_INVARIANT_FAMILY_THRESHOLD_ARCHITECTURE_ONLY`

Recommended next branch:

`bhsm-physicality-coupling-selection-theorem-v6-0-4`

No physical spacetime formation, primordial release, black-hole recycling,
signature emergence, absolute scale, particle property, gauge coupling, or
full BHSM completion is claimed.
