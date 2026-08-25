# N=12 exact weight-seven center family

Status: `EXACT_LEADING_WEIGHT_CENTER_FAMILY_DERIVED_NORMAL_ATTRACTION_NOT_YET_PROMOTED`.

Let the retained logarithmic spatial variables be fixed functions of the
Galerkin coordinate and let only the common logarithmic scale evolve,

`q0(tau)=q0_bar+H0 tau`, `qdot=H0 e0`, `log N=0`, `beta=0`,

where `H0^2=kappa0/42`.  This is an exact family of solutions of the complete
weight-seven action, not just a statement about its quadratic jet.

At every spatial point the three logarithmic expansion rates are
`Hc=Ha=Hb=H0`.  Consequently the ADM scalar in the retained integrand is

`K7=Hc^2+3 Ha^2+3 Hb^2-(Hc+3 Ha+3 Hb)^2=-42 H0^2=-kappa0`.

Writing `V=C A^3 B^3`, lapse variation of

`V[-kappa0 N/2+K7(unnormalized)/(2N)]`

at `N=1` is `V[-kappa0/2-K7/2]=0`.  The response term is quadratic in
`beta/N`, so its first variation also vanishes there.

For any retained coordinate variation, let
`s=delta log C+3 delta log A+3 delta log B`.  On the family,

`partial L7/partial q=-kappa0 V s`,

`partial L7/partial qdot=-6 H0 V s`.

Since `Vdot=7 H0 V`,

`D_tau(partial L7/partial qdot)=-42 H0^2 V s=-kappa0 V s`,

and every coordinate Euler--Lagrange residual vanishes exactly.

Finally, a shift variation gives

`delta_beta L7=6 H0 [V beta' + V' beta]=6 H0 (V beta)'`.

The retained shift basis has the required pole behavior, so the integrated
boundary term vanishes.  Thus all lapse and shift constraints hold.

After quotienting the twelve local time/lapse chains, this family has the 24
fixed `w_j,b_j` shape parameters and the common-scale/orbit-phase parameter.
Its 25-dimensional tangent at the round member therefore exhausts the 25
physical zero roots of the certified descriptor.  In particular the missing
leading-weight identity `N7(a,0)=0` is now action-derived.

This theorem does not yet promote an open capture basin.  That promotion
still requires the analytic constraint reduction to be uniform on a
neighborhood of this family and a normal-attraction/trapping estimate for the
complete nonlinear leading-weight dynamics, followed by absorption of the
positive powers of `epsilon=R4^-2`.  No eigenvalue, selector, action term,
scale, fit, endpoint, recurrence assumption, or chord is added.
