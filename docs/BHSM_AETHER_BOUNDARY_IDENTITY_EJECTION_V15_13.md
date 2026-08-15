# BHSM v15.13 boundary identity, spacetime displacement, and ejection

## Result

The Boundary Identity Preservation Principle has real mathematical content:
it forbids crosswise sewing of the parent and child trace spaces.  It does not,
however, select a unique self-adjoint matter domain.

The reduced two-sector asymptotic trace map must be

\[
\mathcal U_{\rm asym}=\mathcal U_p\oplus\mathcal U_c,
\]

so the exchange matrix is excluded.  On each skin, the existing Green-form
calculation still permits

\[
 \psi_-^{(s)}=U_s\psi_+^{(s)},\qquad
 U_s=\frac{1-i\alpha_s}{1+i\alpha_s},\qquad s\in\{p,c\}.
\]

Every real \(\alpha_s\) gives a maximal-isotropic, flux-conserving domain.
Consequently the new rule reduces the ambiguity to

\[
\boxed{U(1)_p\times U(1)_c}
\]

but does not remove it.  Even if a common overall phase is gauge, the relative
parent/child phase remains continuous.  The pullbacks of the bulk
Levi-Civita, spin, and gauge connections determine tangential parallel
transport once a background and path are known; they do not select the normal
self-adjoint boundary graph.  The retained matter junction action is zero,
while the Hayward term acts only on gravitational joint measure and angle.

Boundary identity also does not reconstruct a transient contact history from
the endpoint.  For example, a Hermitian pulse
\(H(t)=g(t)\sigma_x\) has

\[
 U(A)=\cos A\,I-i\sin A\,\sigma_x,
 \qquad A=\int g(t)\,dt.
\]

At \(A=\pi\) the endpoint is block diagonal even though intermediate states
mix.  Thus the asymptotic identity rule cannot by itself fix a contact
generator.

## Enclosed reconstructed spacetime

No fluid density or new buoyancy coefficient is needed.  Let
\(\Sigma_\tau\) be a relational-clock slice with future unit normal
\(u_{\rm clk}\), and let \(\Omega_c(\tau)\) be the child region in the
reconstructible stratum \(\mathfrak G_A\).  The action-owned enclosed amount is

\[
 \boxed{
 \mathcal V_{\rm ST}(\tau)
 =\int_{\Omega_c(\tau)\cap\mathfrak G_A}
 \iota_{u_{\rm clk}}\epsilon_g
 =\int_{\Omega_c(\tau)}\sqrt{\det h}\,d^7x .}
\]

This is invariant under a joint diffeomorphic pushforward of the metric,
clock slice, and child domain.  It is finite on a compact regular child.  No
spatial measure is assigned to the pregeometric core: at reconstruction-rank
loss the geometric measure is absent or degenerate.  A shape-independent
scale coordinate is the volume radius

\[
 R_V=\left(\frac{\mathcal V_{\rm ST}}{\omega_7}\right)^{1/7},
 \qquad \omega_7=\frac{\pi^{7/2}}{\Gamma(9/2)}.
\]

The physical displacement energy is not a separate volume potential.  It is
the matched relative on-shell Hamiltonian

\[
 E_{\rm disp}
 =H_{\rm phys}^{\rm on\mbox{-}shell}[p+c]
 +H_{\rm corner}
 -H_{\rm phys}^{\rm on\mbox{-}shell}[p],
\]

with the same relational clock, outer data, constraints, gauge quotient, and
reference subtraction.  Its Hadamard variation is

\[
 \frac{\partial E_{\rm eff}}{\partial q}
 =\int_{\Sigma_c}\mathcal T_{\rm rel}
 \left(\frac{\partial X}{\partial q}\!\cdot n_c\right)d\mu_\gamma,
 \qquad
 F_q=-\frac{\partial E_{\rm eff}}{\partial q}.
\]

Here \(\mathcal T_{\rm rel}\) is the complete relative quasilocal traction
from the retained bulk, GHY, Hayward-at-contact, eta, sigma, gauge, and fermion
actions.  It is an output, not a freely chosen pressure.

After eliminating physical response variables \(y\), the restoring curvature
is

\[
 k_q^{\rm eff}=H_{qq}-H_{qy}(H_{yy}^{\rm phys})^{-1}H_{yq}.
\]

At a size stationary point and for \(x=\log(R_c/R_p)\),

\[
 \frac{\partial^2E}{\partial x^2}
 =R_c^2\frac{\partial^2E}{\partial R_c^2}.
\]

The enclosed-spacetime restoring curvature is therefore the same physical
Schur-reduced object previously denoted by the nested-scale curvature, rather
than an additional spring.

## Ejection gate

In a tubular neighborhood before the normal cut locus, define

\[
 d(\tau)=\text{oriented normal geodesic separation of the unique closest
 parent and child skin points}.
\]

The orientation is fixed by the declared child side, so contact is \(d=0\),
successful separation is \(d>0\), and the force is

\[
 \boxed{F_{\rm eject}=-\partial_dE_{\rm eff}.}
\]

The Hayward joint term is active at contact; it is not a post-separation
volume force.  For an identical child/parent phase translated in a homogeneous
background, diffeomorphism/translation invariance makes \(E_{\rm eff}\)
independent of \(d\).  Hence

\[
 F_{\rm eject}=0.
\]

With zero outgoing contact momentum, that control solution remains at
\(d=0\): ejection from rest is not derived.  Successful ejection requires an
action-derived outgoing corner impulse or nonzero post-contact relative
traction.  Neither has been evaluated because no unique matter domain or
physical Hopf child contact solution exists.

## Application to v15.10

Boundary identity and the geometric enclosed measure contain none of
\((\alpha,r,\gamma)\).  At \(\sigma=0\), their direct selector Jacobians
vanish.  The A/B/C witnesses therefore all survive until a backreacted child
solution supplies the physical relative traction and contact momentum.

## Foundational obstruction

This is a constructive obstruction, not a failed solver:

\[
\boxed{
\text{Boundary identity still leaves continuously many inequivalent
self-adjoint state transports.}}
\]

In plain language, saying which skin survives does not say how a matter wave
reflects or passes at that skin.  BHSM needs an action-owned matter boundary
law on each preserved skin (or a proved transparency/regularity theorem) that
fixes the two surviving maximal-isotropic phases without cross-sector
exchange.

The exact next upstream object is:

`ACTION_OWNED_PARENT_AND_CHILD_SKIN_MATTER_BOUNDARY_GENERATOR_FIXING_THE_SURVIVING_U1_TIMES_U1_MAXIMAL_ISOTROPIC_PHASES_WITHOUT_CROSS_SECTOR_EXCHANGE`

`FULL_BHSM_COMPLETE = FALSE`.
