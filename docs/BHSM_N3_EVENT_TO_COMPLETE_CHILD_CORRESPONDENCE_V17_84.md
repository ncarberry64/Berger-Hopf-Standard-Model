# BHSM v17.84 event-to-complete-child correspondence

The whole child is not an extra source coordinate in the 376-variable
reset-to-event KKT system. It is the outgoing, constraint-solved object whose
existence must be tested by a boundary canonical relation.

Let `Gamma0` denote the gauge-quotiented boundary trace and `Gamma1` the
GHY-completed canonical boundary momentum, including the compatible eta,
gauge, and Noether-flux data. The event-to-child variational system is

```text
E_child(Phi) = 0,
Gamma0_event(z) - Gamma0_child(Phi) = 0,
Gamma1_event(z) + Gamma1_child(Phi)
    + W_phys Gamma0_event(z) = 0.
```

After solving the child interior equations, the required event condition is

```text
Phi_z = Solve_child_BVP[Gamma0_event(z), I_event, I_env, B_SM],
F_child(z) = P_coker(D_Phi(E_child,B_child))
             [Gamma1_event(z) + Gamma1_child(Phi_z)
              + W_phys Gamma0_event(z)] = 0.
```

This is the precise form of “the whole system counts”: an event is complete
only if its boundary data lie in the Calderon range of a regular complete
child.

The current v15.45 firewall transports only degree, orientation, incidence,
response order, FR parity, and bundle class. It explicitly does not transport
metric or canonical momentum. The v15.46 reconstruction therefore depends
only on the discrete event component and action scale. On every connected
event component its present `F_child` is constant, with differential rank
zero in the 375 continuous N=3 base variables. It cannot select a point on
the near-flat event surface.

The formal self-adjoint boundary-triple class is derived, but the physical
metric/eta/gauge/spinor/ghost Calderon blocks and the action-derived event
attachment Wentzell block `W_phys` are not. Setting `W_phys=0` would be an
extra physical assumption and is not adopted.

Therefore the direct v17.83 Newton calculation is deferred before execution.
The next finite-dimensional scientific target is the terminal N=3 trace and
GHY canonical-flux extractor together with the constraint-reduced complete-
child Galerkin Dirichlet-to-Neumann Schur complement. Once those blocks are
derived, `F_child=0` can be evaluated on candidate event states and either
used as an external acceptance condition or included variationally with a
rank-balanced matching multiplier.

`FULL_BHSM_COMPLETE = FALSE`. GitHub and USB synchronization remain
ineligible.
