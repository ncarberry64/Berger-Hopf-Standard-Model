# AE4 current-C2 stratified event-flux assembly

## Result

The missing full-field bridge is now one explicit algebraic object rather
than a list of separately normalized sector problems.  On the reset-glued
maximal-history trace space use the ordered graded sum

```text
geometry/eta/sigma + gauge transverse + gauge constraint + BRST ghost
                   + fermion/family + HS scalar.
```

Every block is a derivative of the same AE4 Dirac-zeta owner.  The statistics
and ghost signs therefore enter through the common supertrace; this assembly
does not permit sector-by-sector normalizations.

For parent trace `q`, future-child coordinate `c`, response multiplier
`lambda`, explicit current/source `J`, and response row `Cq=d`, the stationary
event equations are

```text
H_pp q + H_pc c + C^dagger lambda + J = 0,
H_cp q + H_cc^R c = 0,
C q = d.
```

The child is eliminated only with the already-selected retarded resolvent:

```text
c = -(H_cc^R)^(-1) H_cp q,
H_eff^R = H_pp - H_pc (H_cc^R)^(-1) H_cp.
```

The nonzero event canonical traction identity is consequently

```text
Pi_parent + Pi_returned-child + J + C^dagger lambda = 0.
```

This extends the historical zero-background homogeneous match without
reconstructing the N12 continuum child.  Contracting the identity with any
action symmetry tangent `delta q=Tq`, `T^dagger=-T`, gives the corresponding
event Noether-flux balance

```text
sum_i 2 Re <Tq,Pi_i> = 0.
```

The retarded passivity identity remains exact in the same assembly.  Thus a
closed parent-plus-child action and a dissipative reduced parent response are
compatible rather than contradictory.

## Claim boundary

The direct-sum, source/response KKT reduction, event canonical balance and
Noether contraction are derived.  The numerical witness tests the theorem
with all six sectors and nonzero source and response data; it is not physical
BHSM data.

The canonical-stop **center** coexact gauge block and its exact BRST quotient
are now evaluated and attached to this assembly.  The composed 72-direction
affine-carrier proper-time first jet is also attached as a fail-closed
candidate; its existing nonlinear transfer rejection is preserved.  Neither
is inserted into the theorem witness as though the other physical sector
blocks or nonlinear authority were known.
The direct mixed Green/transverse graph is now reconciled outward with the
independent polarization route and materialized on every post-reset endpoint
with a defined Green axis.  This closes the endpoint representation operand,
but its correlated midpoint and causal transport remain open; it therefore
does not yet enter this flux assembly as a complete certified nonlinear block.
The correlation-preserving outward nonlinear stop family and the remaining
action-derived nonzero current-C2 Calderon blocks have not yet been
evaluated.  In particular, this result does not supply a physical Maxwell
residue, broken HS saddle, action-selected fermion/Hadamard state, physical
event flux, or completed encapsulation.  Those values must be inserted only
after they are obtained as variations of the common AE4 operator, with no
fitted normalization.

The next calculation is therefore narrower: close the same-center interval
contraction and repeat the existing proper-time gauge/BRST cotangent
contraction on the nonlinear stop family, evaluate the HS/fermion mixed
nonzero blocks on that same domain, insert them in this assembly, and test
the resulting physical event and Noether-Hamiltonian balance.
