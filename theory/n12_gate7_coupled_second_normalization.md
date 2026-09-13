# Common-border cancellation through mixed second order

This is a rearrangement of the existing physical field, conditional on the
same selected eigenline and bordered response throughout the input domain.
It supplies no new action, branch selection, physical domain, or prediction.
The caller must already justify p.p=1, p.h=0 and their differentiated
identities through mixed second order. Independent interval coordinates do
not themselves establish those identities.

The original field has numerator G=(s c, w(b p+s h)) and descriptor
numerator delta=cp b+s rem. For a verified nonzero border b, define
t=s/b, a=p+t h, S=h.h+c.c, nu_i=w_i^2-1 and

    Q = 1 + sum_i nu_i a_i^2 + t^2 S,
    U = (t c, w a, cp+t rem).

The identities give |G|=|b| sqrt(Q), so the complete normalized field is
F=sign(b) U/sqrt(Q). All weights must be at least one; the implementation
requires a verified positive Q. It carries full Arb input uncertainty.

For independent direction parameters u,v (subscript x denotes uv),

    t_u = (s_u-t b_u)/b,
    t_v = (s_v-t b_v)/b,
    t_x = (s_x-t b_x-t_u b_v-t_v b_u)/b,
    a_x = p_x+t_x h+t_u h_v+t_v h_u+t h_x,
    S_u = 2(h.h_u+c.c_u),
    S_v = 2(h.h_v+c.c_v),
    S_x = 2(h_u.h_v+h.h_x+c_u.c_v+c.c_x).

Write q_u=Q_u/2, q_v=Q_v/2, q_x=Q_x/2. Then

    q_u = sum nu_i a_i a_ui + t t_u S + t^2 S_u/2,
    q_v = sum nu_i a_i a_vi + t t_v S + t^2 S_v/2,
    q_x = sum nu_i(a_ui a_vi+a_i a_xi)
          +(t_u t_v+t t_x)S+t t_u S_v+t t_v S_u+t^2 S_x/2.

Ordinary product rules give all components of U_u,U_v,U_x, including the
mixed configuration, descriptor, cp, and remainder terms. Finally,

    F_x = sign(b)/sqrt(Q) *
          [U_x-(U_u q_v+U_v q_u+U q_x)/Q+3 U q_u q_v/Q^2].

Tests independently differentiate the original uncanceled field using Arb
Taylor series on a two-parameter family with normalized p and orthogonal h,
nonconstant b,s,cp,rem, nonzero mixed variations, unequal weights, and both
border signs. Polarization extracts the mixed coefficient. A caller that
does not assert the coupled second-order identities is rejected.

The saved-Hessian diagnostic verifies the bound source files and data hash,
loads the same paired physical domain, and uses all seven saved original
bordered solves and all saved original scalar contractions. The original
graph's differentiated normalization and orthogonality equations supply
the required identities for that same exact solution family. The diagnostic
checks overlap with the old uniform enclosure and containment of the
verified point Hessian. These checks do not replace the identity argument.
Only one scaled longitudinal direction and one transverse column are
covered; no full Hessian, independent numerical reproduction, uniform
mean-value bound, global contraction, or Gate 7 closure is claimed.
