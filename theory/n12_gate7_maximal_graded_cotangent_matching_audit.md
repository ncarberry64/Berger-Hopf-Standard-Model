# Gate-7 maximal graded cotangent matching audit

Status: `MAXIMAL_GRADED_COTANGENT_TYPE_CLOSED_BIRTH_LOADED_OPERATOR_FAMILY_OPEN`.

The retained BRST/statistics ledger already fixes every coefficient in the
physical heat direct sum.  After the longitudinal gauge/complex-ghost pair is
cancelled mode by mode, the nonzero weights are

`w_gauge(m)=+24*(m^2-1), m>=2`,

`w_Weyl(n)=-48*(n+1)*(n+2), n>=0`,

`w_HS(m)=+4*m^2, m>=1`.

These weights survive the retirement of the periodic proper-cycle domain.
They are representation/statistics data, not temporal boundary conditions.
The current temporal domain is the forward AE2 event--child graph on the
action-realized history.  The initial birth trace remains a degree of freedom
in the closed operator when `J_ext=0`; it is not replaced by a Dirichlet
condition.

For every level `k` and every member `xi` of the certified local history
family, let `P_C,k^joint(xi)` be the complete positive self-adjoint joint
operator after incoming formation, transported child response, `U_R`,
`W_phys`, and retained contact/incidence blocks have been assembled once.
The exact operator cotangent is

`Q_C,k(xi)=(w_C,k/2)*exp(-ell^2*P_C,k^joint)*P_C,k^joint^(-1)`

`=(w_C,k/2)*integral_(ell^2)^infinity exp(-s*P_C,k^joint) ds`.

For any primitive action coefficient `a`,

`q_a^heat(xi)=sum_(C,k) ReTr[Q_C,k(xi)^dagger D_a P_C,k^joint(xi)]`.

The replacement covector is

`q_a^rep=q_a^heat-(59/30) D_a integral d_tau/R4`.

The common-scale component retains its already-certified moving-duration
Ward cancellation.  No other component is removed.  In particular,
`J_ext=0` removes only the external linear birth/Cauchy coupling; it neither
changes these weights nor deletes a trace, seam, child response, or contact
block.

The repository matching result is sharp:

- the grading, multiplicities, heat Fréchet seed, zeta subtraction, block
  reverse order, reset pullback, and projected-Cauchy criterion are valid
  existing matches;
- the old incoming whole-axis enclosure rigorously controls the Dirichlet
  reference block `M11`, but its identification with the physical zero-source
  `M_f` is superseded; the latter requires the action-owned birth-graph Schur
  reduction or an unreduced joint operator retaining the birth trace;
- the outgoing `M_C2` whole-axis object has a rigorous finite-core
  representation, but the broad enclosure does not fix the nonlinear heat
  functional;
- the 1,222-segment reverse actions are certified, but the finite proof edge
  is not a physical endpoint;
- no scalar at a proof center represents the physical family;
- the actually missing datum begins with the retained birth graph `B_birth`
  and its first jet, or an unreduced operator that keeps the birth trace, and
  then the sharp per-level joint operator family `P_C,k^joint(xi)` and its
  first action jet, or an equivalent decisive trace-functional enclosure, on
  the action-realized maximal history or an actual finite event/canonical
  stop.

Thus neither a new grading, a new external source, more isolated negative-axis
probes, nor a new response theory is required.  Once the birth-loaded actual
joint family is supplied, the already-derived seed is evaluated, the single
signed reverse sweep is run, and the existing physical quotient tests the
Cauchy tail before the same-action KKT root.

Gate 7 remains open, Gate 8 remains locked, chord 3 remains unauthorized, and
`FULL_BHSM_COMPLETE=false`.
