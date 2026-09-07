# AE4 future-collapse relative-boundary domain

The future-only collapse decision removes the finite route ambiguity left by
the AE3.1 outer-Calderón no-go. The new domain is not a reciprocal reflected
cap and the reset graph is not silently promoted into an outer state selector.

The complete parent and child remain one closed variational system. On the
first future impedance surface, write the quadratic boundary block as

```text
H = [[H_pp,H_pc],
     [H_cp,H_cc]].
```

Future support selects the retarded child boundary value
`H_cc^R(omega+i0)`. Eliminating the child gives the parent response

```text
H_eff^R = H_pp-H_pc (H_cc^R)^(-1) H_cp.
```

This elimination is an exact same-action Schur complement, not a fitted
boundary term. If `Im H_cc^R` is positive semidefinite, then

```text
Im H_eff^R
 = H_pc (H_cc^R)^(-dagger)
   Im(H_cc^R)
   (H_cc^R)^(-1) H_cp
 >= 0.
```

The implementation verifies this causal/passive identity directly. The full
parent–child system remains closed; only the reduced parent response may be
dissipative when future child channels are open.

This does not contradict the AE3.1 reflection theorem. That theorem assumed a
mirrored regular cap with
`N_child=U_reset N_parent U_reset^dagger`, which doubles both residues. AE4
instead requires the returned child impedance from the single stratified
Dirac–zeta action. Noncommon gauge response is now allowed, but its value is
not known until the current-C2 child block and coupling are evaluated.

The same retarded prescription applies to coexact gauge, constraint,
Faddeev–Popov ghost, spinor/family, HS/scalar and metric blocks. This preserves
the BRST pairing instead of selecting gauge and ghost domains separately.

This construction reuses the older child chain at its exact strength:

- v17.84 already derived the event-to-complete-child first variation and
  `F_child` boundary canonical relation;
- v17.86 evaluated a finite-chart metric/lapse Dirichlet slice, matched its
  trace, and obtained a finite DtN mismatch norm `127.161505414014`; the
  static spatial child BVP did not close and was correctly reclassified as
  insufficient for a Lorentzian nonequilibrium child;
- v17.87 already defines a particle as a complete reconstructed encapsulated
  persistent nonequilibrium child and decay as its first exit from `B_child`;
- v17.88--v17.98 close the retained Lorentzian dynamic Wentzell/Cauchy,
  attachment momentum/force/flux, gravity--eta scalar, zero-background
  gauge--spinor--ghost--HS, and discrete-firewall boundary blocks;
- v17.99 evolves that complete child for a positive constraint-consistent,
  eta-hyperregular proper-time interval;
- v21.35 validates exact-attachment weak-conormal complete persistent children
  at N3 through N6, fixed-background linear Calderon graph convergence, weak
  bulk-tail decay, an exact N-minus-two product shell bound, and an asymptotic
  high-shell inverse;
- the later direct N12 child and continuum majorant certificate close the
  resolution-independent event-child construction and supersede the finite
  N6-to-M0 bridge as a current blocker;
- the N12 time-domain audit proves that the physical clock orientation is one
  and forward, while the local singular hitting/reset theorem leaves global
  forward terminal-chart reachability open;
- the AE2 nonfermion theorem supplies the positive child-core zero-energy
  impedance lower `6.37052204298831e-8`.

The old five-block checklist and finite Schur-bridge blocker are both retired.
The retained continuum child calculation is certified and must not be
restarted. The primary domain join is now the nonzero AE4 stratified
gauge--ghost--fermion--HS source/response block on the reset-glued maximal
history, followed by the event canonical flux and complete
Noether--Hamiltonian balance. Global forward reachability remains a parallel
dependency for `Q_xi` and parent-relative energy; it does not reopen the local
same-spacetime enclosure. V17.97 closed only the selected zero-background
gauge--spinor--ghost--HS match.

Scientific milestones:

```text
AE4_FUTURE_COLLAPSE_RELATIVE_BOUNDARY_DOMAIN_CLASS_SELECTED = TRUE
AE4_RETARDED_CHILD_SCHUR_COMPLEMENT_DERIVED = TRUE
AE4_V21_35_N3_TO_N6_COMPLETE_PERSISTENT_CHILDREN_REUSED = TRUE
AE4_FINITE_N6_TO_M0_NORMAL_SCHUR_BRIDGE_CERTIFIED = TRUE
AE4_N12_CONTINUUM_EVENT_CHILD_CERTIFICATE_REUSED = TRUE
AE4_GLOBAL_FORWARD_TERMINAL_CHART_REACHABILITY_DERIVED = FALSE
AE4_CURRENT_C2_FUTURE_CHILD_BLOCK_EVALUATED = FALSE
```

`FULL_BHSM_COMPLETE = FALSE`.
