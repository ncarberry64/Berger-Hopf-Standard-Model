# BHSM v16.78 scale and child-channel ownership audit

The measured `log_scale` obstruction is not an extra freely chosen particle
scale.  The canonical reconstruction fixes `q_log_scale(0)=0`, hence
`R(0)=R_star=(343/5)^(1/6)` in the action's units, and the anchored KKT omits
that reset coordinate.  Its 23 remaining scale coordinates are the breathing
history on the open reset-to-event orbit and have exactly 23 stationarity
rows.  Removing one of those rows would delete a physical variation.

The audit therefore does not modify the current 376 by 376 event KKT.  The
post-v15.84 chain still lacks a valid event/environment-conditioned broken
return solution map.  Once the same action derives

`R_rec = R_rec[I_event,I_environment]`,

the return condition is

`C_rec = q_log_scale(return) - log(R_rec/R_star) = 0`.

It may then be imposed by substitution (375 unknowns and 375 equations for
the corresponding return formulation) or by retaining the endpoint scale
and adding `C_rec` with one conjugate multiplier (377 and 377).  It must not
be inserted before `R_rec` exists.

Reconstruction is a channel map

`(I_event,I_environment,B_SM) -> (admissible child sector,R_rec,z_return)`.

Already-derived degree, orientation, FR parity, response endpoint order,
incidence, boundary identities, SM representation labels, C3 family
projectors, hypercharge operator, and bundle isomorphism class restrict its
output block.  They forbid arbitrary cross-sector branch selection without
adding an empirical particle-selection rule.  Continuous environment data
sufficient to fix an event-specific scale remain a downstream broken-return
dependency: gauge-covariant, constraint-compatible boundary Cauchy and
Noether-flux data must be extracted from the physical event layer and supplied
to the reconstruction BVP. This is not a metric transported through the
firewall.

## Post-audit numerical falsification of over-independence

The unchanged 376 by 376 KKT continuation reduced the complete
scale-stationarity norm

`14.016355587104 -> 0.465980389110 -> 0.213798884712 -> 0.191940795808`

while retaining all 23 open-orbit `log_scale` unknowns and all 23 conjugate
stationarity rows. The v16.98 state has complete residual
`1.498176849072`, event magnitude `0.130037517716`, and positive
`eta_min=0.780698017687`. This directly identifies the former 14.016
obstruction as a solvable stationarity defect, not a redundant row caused by
assigning the child an independent size.

With `q_0` fixed by the reset, the anchored action has the form

`Gamma[q,m,T] = T sum_i omega_i L(q_i,(Dq)_i/T,m_i)
                + Gamma_common_heat[R[q],tau[m,T]]`.

Each free scale history value `q_i^scale`, `i=1,...,23`, therefore owns the
Euler equation `partial Gamma/partial q_i^scale + rho partial E/partial
q_i^scale=0`. The fixed datum `q_0^scale=0` owns neither an unknown nor a
variation. The present count is

`230 q + 144 multipliers + 1 period + 1 event multiplier = 376`

against

`230 q-stationarity + 144 multiplier-stationarity + 1 period-stationarity
 + 1 event equation = 376`.

Only after the broken reconstruction BVP derives `R_rec[I_event,I_env]` may
the return-endpoint scale be eliminated. In the corresponding endpoint
sector, substitution removes one unknown and its free-endpoint stationarity
equation (`376-1=375` on both sides); the equivalent KKT form retains the
unknown and adds one constraint plus its multiplier (`376+1=377` on both
sides). These are endpoint-sector recounts, not claims about the eventual
dimension of the full broken-return system.

At v17.04 the scale block temporarily re-entered the active owner set at
`0.440239029257`. v17.05 therefore added that existing block to the measured
simultaneous descent cone, without adding or deleting any physical equation.
The accepted six-owner step reduced scale to `0.432309885844` while also
reducing complete residual, period, `w_0`, `v_0`, and the identical event.
This is the direct KKT test requested by the ownership clarification: the
scale equation remains necessary and jointly solvable.
