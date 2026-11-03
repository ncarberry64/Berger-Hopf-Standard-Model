# v70: a native weak-source reduction with controlled photon transport jets

3 November 2026. Resumed after capacity interruption; no Python process or
unfinished v70 calculation was found. v69 remains unchanged. The bounded
Python314 invocation succeeded. No extra worker, new resolution, heat/history
campaign, occupation, state, commit or push was used.

**Result.** The native radial derivative-of-test term vanishes on the exact
regular photon-transport core, including its complete mixed response. The
angular and actual domain/edge terms remain. A newly evaluated ordered second
transport term fixes a large mixed-coordinate defect of the earlier first
approximation on the saved initializer. Neither result evaluates the full
physical current, reconnection event or muon magnetic moment.

## 1. Apply the existing photon test to the original weak source

v69 retains the action's weak native source (not an assumed strong density):

    J_N[lambda] = integral [<a,lambda> + <b^rho,D_rho lambda>
                            + sum_i <b^i,D_i lambda>] + J_domain[lambda].

The coefficients are full native/relative kernel contractions. They are not
the finite stationary18 wall load. Product-domain, cutoff, normalization,
event and relative terms remain in the original ledger, with overlap
subtracted once. The independent left source is not replaced by a conjugate
right preparation. No lower-order Dirac, combined-eta or material-time term
is discarded from these coefficients or from the matter equations.

For the v66/v67 radial photon dual on a regular pulled-back chart, put

    lambda_h(rho,Omega) = chi_h(Omega) phi(rho),
    D_rho phi = 0,                 phi(W) = s_H,
    D_rho chi_h = 0.

The eight magnetic sources feed the existing twenty scalar harmonics. This
is their existing radial Gauss dual, not a replacement physical packet.
It follows that

    J_N[lambda_h] = integral [<a,chi_h phi>
                  + sum_i <b^i,(E_i chi_h)phi + chi_h D_i phi>]
                  + J_domain[lambda_h]                         (1)

on the regular transport core. This removes the need to estimate the
**bulk** b^rho contribution for these specific tests. It does not give the
norm of J_N on all electric tests, or eliminate b^rho from the action.
The nonzero angular term proved in v67 persists.

All variations refer to one pulled-back material coordinate system; its
connection/operator derivative includes actual frame/domain motion. Let
E=D_rho lambda. Then E=E_X=E_Y=E_XY=0 for the exact transported family.
The three-factor mixed derivative of b D lambda has all nine placements:

    b_XY D lambda + b_X D_Y lambda + b_X D lambda_Y
    + b_Y D_X lambda + b D_XY lambda + b D_X lambda_Y
    + b_Y D lambda_X + b D_Y lambda_X + b D lambda_XY.

Their sum is b_XY E+b_X E_Y+b_Y E_X+b E_XY=0. The executable free-word
check preserves the order b,A,lambda and independently varied jets. A
fixed-readout derivative would not establish this cancellation. Independent
factor-domain and relative contacts are not part of the cancelled expression.

## 2. Pole and partial-envelope qualifications

An angular test need not be pointwise smooth at the collapsed pole. It must
be justified in the actual weighted energy closure, not silently treated as
a smooth global scalar. On the regular germ k<=k_plus rho^6 and
e<=e_plus rho^4, cut off the test below epsilon and join to it by 2epsilon.
For a linear cutoff with slope 1/epsilon, its additional radial energy is at
most k_plus ||lambda||_Omega^2 (127/7) epsilon^5. The removed angular energy
is at most e_plus ||D_i lambda||_Omega^2 (32/5) epsilon^5. Thus the bounded
transported angular test has a finite-energy limiting representative under
these stated germ hypotheses.

The native cutoff-shell term is separately bounded by

    ||b^rho/sqrt(k)||_shell
       * sqrt(k_plus*127/7) ||lambda||_Omega epsilon^(5/2).

It tends to zero if that native coefficient has the stated weighted L2
regularity. No such full native norm has been evaluated here. Without a
justified continuity/trace result for the complete source, retain this limit
as a pole/domain contact; do not declare full pole cancellation. On actual
retained/released edges retain the common conormal, endpoint and moving-test
terms. A sharp indicator times a weak flux is never used. The exact local
identity (1) does not construct the event-generated trace graph.

## 3. New explicit ordered transport application

Use the saved fractional-polynomial connection exactly as a frozen
representation. Write A(rho)=ad A_rho(rho), x=rho/W and

    A(rho)=sum_m C_m x^(alpha+m),  p_m=alpha+m+1,
    J1(rho)=integral_rho^W A(t) dt,
    J2(rho)=integral_(rho<t<s<W) A(t) A(s) dt ds.

The order is essential. The earlier v67 test is phi1=(I+J1)s_H. Its exact
defect in this representation is D_rho phi1=A J1 s_H. The new term is

    J2 = W^2 sum_(m,n) C_m C_n / p_n
          * [(1-x^p_m)/p_m - (1-x^(p_m+p_n))/(p_m+p_n)],
    phi2=(I+J1+J2)s_H,             D_rho phi2=A J2 s_H.      (2)

No quadrature or evolution step is needed for (2). Its value, sixteen
original radial coefficient derivatives and all 16x16 mixed radial
derivatives are evaluated at the existing 49 nodes. The correction to the
189-coordinate first jet includes the four Higgs readout derivatives.
Sub-roundoff value corrections are stored separately instead of being lost
when added to the O(1) readout. The angular connection correction is also
saved in factored form. This does not supply the unknown physical total Y
direction or its background/endpoint response.

| Coefficient-level quantity | First transport approximation | Including J2 |
| --- | ---: | ---: |
| Maximum sampled radial defect | 8.2473963e-28 | 1.4149868e-41 |
| Maximum first radial-coordinate defect | 2.8404422e-13 | 4.5273709e-27 |
| Maximum mixed radial-coordinate defect | 67.9619245142 | 1.4950076e-12 |

The value correction is only 4.0094586e-28, but its largest mixed coefficient
is 26.3306181171. This is why small value error alone cannot justify dropping
ordered terms from a response calculation. These coordinates are derivative
axes of the original representation; they are not new physical perturbation
amplitudes or a claim of instability. The v67 first-jet result remains valid
within its documented first-order scope; no old artifact is overwritten.

## 4. Explicit omitted-order bounds and their limits

Let a>=integral ||A|| and B_j>=integral ||A_j|| on the fixed interval.
For a<1 and s fixed under these affine radial-coordinate variations, the
remaining Dyson series has the conservative bounds

    ||phi-phi2|| <= ||s|| a^3/[6(1-a)],
    ||partial_j(phi-phi2)|| <= ||s|| a^2 B_j/[2(1-a)],
    ||partial_j partial_k(phi-phi2)|| <= ||s|| a B_j B_k/(1-a).

These follow by differentiating the absolutely convergent ordered series;
the factorials count all placements, not commuting matrix powers. The code
uses ||s||_1 as an upper bound and directed Decimal arithmetic for the
finite coefficient expressions. The analytic scalar moment

    integral_0^1 x^(2alpha) (sum_m c_m x^m)^2 dx
       = sum_(m,n) c_m c_n/(2alpha+m+n+1)

retains cancellations in the actual polynomial basis. Cauchy-Schwarz bounds
each color's integral norm; summing colors conservatively bounds the owned
ad norm. No added nodes or regulator change is involved.

The resulting bounds for the frozen representation are:

* integral connection norm <=1.3404872058e-13;
* omitted value <=1.3006959980e-39;
* largest omitted first radial derivative <=2.8920250799e-25;
* largest omitted mixed radial derivative <=4.2868377523e-11.

The last is a conservative continuum-in-rho transport bound, not the sampled
defect in the table. None includes floating evaluation/input error, the
unknown physical source norm, native kernel, geometry/domain errors or
physical uncertainty. In particular it is not a certificate that a complete
physical residual passes 2e-10. For a native contraction the appropriate
dual norm must still multiply the test error. Actual total/mixed Y also
requires its owned coefficient directions and domain motion.

## 5. Reconciled physical dependency and exact next obligation

The original Pauli readout already permits a source-projected soft derivative
and does not universally require a complete production-history calculation
(`theory/muon_minimum_pauli_readout_20260930.md`). Repeating that reduction or
assuming LSZ removes internal native/domain dependence would not advance it.
The regular interface law is the later AE3.2.16 covariant membrane action,
not the superseded AE3.2.15 unselected density class. No new author choice,
attachment law or inherited occupation is requested.

For (1), the precise unresolved application is the complete same-domain
native/relative kernel against the zero-derivative source and the **angular**
derivative source, plus the prescribed entering and pole/event/retained/
released functional. The owned fixed-domain representative is
K_c=(1/2)P^(-1)exp(-cP), P=LR, with both B_R psi=0 and B_L R psi=0 and
their varied forcing. Its causal first-order counterpart and relative
continuation must refer to the same physical domain. The cutoff is its
owned i/r, not one. Neither an 18D inverse nor a heat of compressed blocks
evaluates this object.

The accessible owner still explicitly leaves the global stratified operator
and domain unrealized. The local two-collar code takes the physical plus/
minus traces, geometric transport and independent left/affine source jets
as inputs; it does not generate them. v62's coupled tuple therefore remains
the earliest unconstructed physical object: constrained fields/momenta and
action-selected event trace graph, with stationary-past dressing and complete
native/relative source applied on it. Existing local rank inverses do not
make its complete residual evaluable. This is unfinished coupled mathematics,
not proof of inconsistency or absent user intent.

The smallest next constructive task is to realize that source-projected
native boundary problem for the reduced tests (1), with its actual B_R and
B_L R rows and entering data, and verify the pole/edge continuity needed by
section 2. Physical pair currents additionally need the prescribed right
and independent left weighted entering/material-time jets; v69's product
bound still applies conditionally and supplies none of those values. No
numerical background/history launch is justified by this checkpoint alone.

## 6. Verification and unchanged admission status

Six focused tests pass. Nine numerical coefficient checks have maximum defect
5.231466405214886e-12, below the unchanged 2e-11 method tolerance. Five exact
algebra/cutoff checks cover ordering, all nine mixed placements and the
regular-pole scaling. Final deterministic outputs are run_3 and run_4;
run_1/run_2 and the initial code/test snapshot are preserved. Eleven source
records and the bounded invocation receipts identify the inputs and runtime.

The physical guard remains 2e-10. The last admitted temporal20 point remains
t=2^-9, residual 2.962944017741165e-13; the later conditional wall-coordinate
diagnostic remains separate. Neither is a full physical Cauchy state.
Reconnection, complete residual, native a_mu/g_mu and total physical
uncertainty remain uncomputed. The old calibrated additive subtotal is not
completed or supplemented by this operator calculation.
