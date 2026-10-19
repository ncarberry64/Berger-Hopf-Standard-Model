# E1 interacting-domain application and the constrained formation problem

Continuation of `9738fc5a`. This checkpoint evaluates an interacting
**fermionic domain operand**, not a formed mechanical mode. The incoming
selector remains conditionally adopted. No new selector is introduced.
The actual retained incoming-hi and child-lo endpoints at E1 are used;
their archive labels remain `PROVISIONAL_NOT_COLLIDER_SOLUTIONS`.

## The existing formation prescription

`covariant_bubble_interface_mechanics.py` already specifies

\[
 H_{\rm form}\psi=\kappa M_\Sigma\psi,\qquad
 H_{\rm form}=H_{\rm bulk,constrained}
                 +\sum_s\gamma_sJ_{\Sigma_s}-H_{\rm event,drive}.
\]

The candidate is the **first regular future simple oriented zero** of
the lowest constrained eigenvalue, positive before and negative after,
which admits a nonlinear constrained branch. The initiating interacting
event fixes populated channels and their amplitude/phase. Cauchy
normalization fixes the scale after identifying the section. A scalar
birth balance, positive quotient or an arbitrary Hessian eigenline does
not implement this prescription.

For the original signed action, let `x` contain differential fields,
`v=dot(x)` and `y` all algebraic fields/multipliers. The required bulk
Jacobi equations are

\[
 L_{xx}\delta x+L_{xv}\delta\dot x+L_{xy}\delta y
 -D_t(L_{vx}\delta x+L_{vv}\delta\dot x+L_{vy}\delta y)=0,
 \quad
 L_{yx}\delta x+L_{yv}\delta\dot x+L_{yy}\delta y=0.
\]

These act on the constrained tangent, with canonical endpoint,
interface, gauge and causal outer-domain rows. Equivalently the formed
normal section and its interior response obey

\[
 K_{\eta\eta}\delta\eta+K_{\eta\Sigma}\psi=0,\qquad
 K_{\Sigma\eta}\delta\eta+
 (K_{\Sigma\Sigma}-H_{\rm event,drive})\psi=\kappa M_\Sigma\psi.
\]

Eliminating eta requires the *complete framed causal boundary inverse*,
if it exists. The classical52 factorization does not provide it. The
remaining task is this value-level coupled Jacobi/domain application and
its nonlinear realization, not adjudication of another selection rule.

The old homogeneous trial at the different large-lambda calibration had
negative local restoring contraction; it excluded that trial only. The
historical all226 nonpass and later stationary subtotals are neither an
evaluated physical formation mode nor a no-go result for this problem.

## A newly evaluated nonzero domain operand

Each history has TWO opposite eta collars. They are not the two
successive time histories, incoming beams, or native temporal conormals.
On one history let x,z be the full384 traces, y=U_eta^-1 z, and use the
action-normalized chiral trace B and source incidence C. The original
weak domain is

\[
 J_+(y-x)=C\,T_H\,Bx,\qquad
 T_H=\rho M_Y(H),\quad \rho=N_{\rm ind}R_4^3.
\]

Isotropy gives `B J_+^-1 C=0`. Thus

\[
 N=J_+^{-1}CT_HB,\quad N^2=0,\quad BN=0,\qquad
 z=U_\eta(I+N)x.
\]

This is an actual algebraic constrained-domain solve, rather than a
choice of polarization. With BE=I, write x=Eg+chi_plus,
y=Eg+chi_minus and B chi_plus/minus=0. Then **exactly**

\[
 \chi_- -\chi_+=NEg,\qquad
 D_5\chi=-D_5(\mathcal E g),
\]

where the second equation requires a specified same-branch INTERIOR
extension mathcal-E of E and the original outer/collar domain. The
point-trace B and algebraic boundary projector I-EB do not themselves
define a bulk projection. A projected bulk equation is available only
after constructing the interior projection and retaining its derivatives.
The first
equation supplies a nonzero boundary forcing for that complement
problem. Discarding the complement changes the interacting domain.

The new evaluator computes the entire18-column coefficient kernel
`Nhat Ehat`, its full384 complement and actual one-sided time jet on
both saved E1 endpoints, and consumes it in the displayed original weak
rows. It checks Green alignment, isotropy, nilpotence, selected-trace
continuity and the residual of the historical hard graph. Both
complement projectors are distinguished: `I-W W^T` for the algebraic
18 trace and `I-[W,Wcharge][W,Wcharge]^dagger` for the retained36 pair.
The latter is not the historical750-dimensional two-sheet complement.

Hats are **normalization numerators**. The physical LR and RL
coefficients remain, separately,

\[
 a_{LR}=\frac1{u_{L,+}u_{R,-}},\qquad
 a_{RL}=\frac1{u_{L,-}u_{R,+}}.
\]

Their derivatives include
`Da=-a(Du_L/u_L+Du_R/u_R)`. No value of u is set to one. Independent
analytic left sources are not obtained by conjugating continued right
ones. The charged middle-family coefficient subspace can be tested as
a whole; no particular spinor is selected as a physical section.

More precisely let `D_R=u_R,+ P_L+u_R,- P_R`. Then
`B_phys=D_R^-1 Bhat`, `E_phys=Ehat D_R`; hence their boundary projector
`I-E_phys B_phys=I-Ehat Bhat` is independent of these right amplitudes.
Chiral support gives the actual forcing

\[
 N_{\rm phys}E_{\rm phys}
 =\widehat N_{LR}\widehat E/u_{L,+}
  +\widehat N_{RL}\widehat E/u_{L,-}.
\]

The saved coefficients are therefore operands in the physical boundary
equation, not an assertion of unit normal values. Their adapted combined
norm is0.02162442470946075 and numerical rank12. On the entire charged
middle-family subspace (indices8,9,14,15 in the action's heavy/middle/light
family order), all four singular values are approximately
0.0006483689988282714. Independent finite nonzero left normalization
factors rescale disjoint chiral input columns and preserve rank4. Thus
a nonzero charged middle-family section with **both complements zero**
cannot solve this boundary relation. This is a specific domain
obstruction to that retained-only ansatz, not a no-go for a full mode.

Across both endpoints the largest original weak value/time residual
is1.735e-18, the largest separate-channel nilpotence value/time residual
is4.574e-20, and Green alignment is within5.552e-16. These are arithmetic
checks on the displayed finite coefficient problem, not continuum or
physical admission estimates.

The original Jacobi boundary row is also explicit. For
`J(y-x)-C T_H Bx=0`,

\[
 J(\delta y-\delta x)+(\delta J)(y-x)
 -(\delta C)T_HBx-C(\delta T_H)Bx
 -CT_H(\delta B)x-CT_HB\delta x=0.
\]

It retains state, field, pairing, moving-frame, density, normal-mode and
domain contacts. The saved coordinate-time derivative is one actual
tangent of this equation, not its complete physical derivative.

## E1 frames, density and the native factor contact

With opposite eta orientation eps, each actual endpoint has
`S_eps=exp[-atanh(-eps U) Gamma0 Gamma_perp/2]`. The two distinct local
time-frame incidences are

\[
 T_+=S_{+,c}S_{+,p}^{-1},\qquad
 T_-=S_{-,c}S_{-,p}^{-1}.
\]

The evaluator checks `U_eta,c T_plus=T_minus U_eta,p`, selected numerator
incidence and interacting numerator covariance. These are local
coefficient/frame diagrams; they do not establish the physical
transmission of sections. In particular the normalized right trace
contains the uncomputed `u_R,p/u_R,c` ratio, and the left ratio is
independent. Equal spatial connection/Higgs data constrain local gauge
stabilizers but do not prove global bundle/phase or temporal incidence.
The outgoing inherited wall image is kept explicit.

The canonical Cauchy variable is chi=R4^(3/2) psi. The new native-domain
contact application uses each actual induced lapse and
`kappa_s=(3/2)D_tau_s log R_s`; `D_tau=N_ind^-1 D_t`.
Here is the exact missing incidence relation in a form that exposes its
known and unknown terms. **If** the physical event establishes a common
coordinate-time trace `q_c=T(t)q_p`, and
`v_s=(N_s^-1 partial_t+C_s)q_s`, then

\[
 v_c=rTv_p+
 [N_c^{-1}\dot T+C_cT-rTC_p]q_p,\qquad r=N_p/N_c.
\]

For its known density factor d=(R_c/R_p)^(3/2), the newly evaluated
coefficient is

\[
 K_{\rm density}=d[(\kappa_c-r\kappa_p)I+C_c-rC_p],
 \qquad C_s=W_s-i\Omega_s.
\]

For the unassigned remaining incidence V in T=dV, the COMPLETE contact is

\[
 K(T)=K_{\rm density}V+
 d[N_c^{-1}\dot V+r(C_pV-VC_p)].
\]

Thus neither V=I nor its derivative or commutator is implicitly selected.

Its complete ordinary two-jet is saved in the explicitly separate46
chart `[theta_parent22,theta_child22,kappa_parent,kappa_child]`. The
original factor chain rule is independently checked using the saved
raw history derivatives. This is a nonzero contact in the native-domain
equation, **not** an additional heat, current, restoring force or event
source. Normal-profile ratios, their derivatives, spin/gauge holonomy,
the physical event flow and any inherited interface generating term
remain unassigned. They cannot be dropped from T or its contact.
The retained child Cauchy-density and connection two-jets are reused
byte-for-byte from the completed9738fc5a application. The new contact
has Frobenius norm4.1686234465242125, maximum1.0911742020077244 and
independent factor-chain residual1.7763568394002505e-15. Its child coefficients use
the retained own+independent connection; the unverified inherited image
and its derivatives remain explicit corrections, not zero fields.

The saved native past map satisfies a temporal product-factor problem
at its own stationary comparison background and lambda=-1. Its future
comparison is not a physical child. Before consuming that map as an
event return, the analytic/causal contour and full corner trace incidence
must be derived for the moving background. Blind real-time Riccati
propagation would add an auxiliary contour assumption. No such
propagation or same-boost conormal gluing is performed here. The native
resolvent lambda, cutoff c, physical unit coordinate and the above46
contact chart remain distinct.

## Exact obstruction to a full mode and cutoff application

The fermionic localization section obeys the existing collar equation

\[
 (\partial_s+\tfrac12\partial_s\log J
       -\partial_s\log\sin f_{\rm child}(X))u_\eta=0,
 \quad u_\eta=\mathcal N J^{-1/2}\sin f_{\rm child}(X).
\]

Its normalization requires the actual same-branch profile and domain,
`integral J |u_eta|^2 ds=1`, the interacting complement equation above,
and the inherited event/outer conditions. A pointwise wall metric or
Higgs value does not determine this integral or the two-history normal
ratios. This is distinct from the mechanical normal-deformation mode
psi in H_form. Both must be solved on the coupled constrained branch.

Specifically unexecuted are: the complete same-background bulk/state
Jacobi and impedance operator, the incident interacting event projector
and reference correlations it consumes, the D5 normal/complement
boundary problem, and their causal/native corner incidence. Existing
action equations define these problems; their absent value-level
application is not evidence of physical nonuniqueness. The nonzero
boundary forcing computed here is an explicit term those solves must
consume, rather than another free mode supplied to a wrapper.

Only after that solve are same-mode bulk I/R and kinetic-separated
surface restoring pairings available. The cutoff equation remains

\[
 F(c)=cR_{\rm bulk}-I_{\rm bulk}
 +\sum_s\alpha_{\rm FSC}c^{-d_s/2}(cJ_{s,rest}-I_s)=0.
\]

No root, positivity of its full pairings, simple branch, implicit Dc or
D2c is admitted. In particular c is not minimized against a residual or
magnetic datum. Full mode/pairing/domain derivatives belong in F_c and
F_y before any implicit formula. Physical-unit incidence remains a
separate equation.

## Accounting and error scope

No local Maxwell/Higgs functional is subtracted again, and none of its
response is re-added. The Higgs seam is the already-owned domain
interaction, not a second bulk mass or current. Fixed-Y coefficients
and the independent calibration are unchanged. Numerical numerator
coefficients do not set the surface alpha_FSC, normal-mode Gram, native
complement multiplicity or inherited-state contractions.

The latest known subtotal after whole local removal still has maximum
265.7146799759407 and area-orthogonal obstruction16.580384939674158;
its structural zero52 is not physical closure. The earlier worsened
wall/Higgs residuals remain historical evidence. This checkpoint does
not replace them with seam arithmetic residuals. Complementary native,
phase, boundary, matched-state and calibration matching remain explicit.
Gauge reconstruction, membrane finite-step, continuum/time and
conditional-state errors are not bounded by the new algebraic checks.
The unchanged physical2e-10 guard has not passed; no coupled correction,
fresh Maxwell/all226 claim, magnetic moment or uncertainty follows.

`NEXT_OPERAND`: solve the displayed same-branch D5 complement/normal
boundary problem with the saved LR/RL forcing, together with the
constrained formation KKT/event problem and the derived physical corner
incidence. Preserve the evaluated kernels and their time/contact jets.
