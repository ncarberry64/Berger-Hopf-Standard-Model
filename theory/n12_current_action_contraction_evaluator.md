# Current same-action contraction evaluator

Scope: the existing projected force, coupled KKT and derivative-product
obligations in `docs/GATE7_CURRENT_CALCULATION_SCOPE.md`. No criterion,
endpoint, threshold, environment input or frozen prediction changes.

## Implemented reduction

`src/bhsm/interface/gate7_current_action.py` implements the requested
`evaluate_gate7_current_action(query, requested_products)` interface.
The query supplies one realization of `F(xi,P,n)=0` and the signed action
sectors on that realization. Their partial gradients are summed before
the common solve `F_n^T eta=Gamma_n`. The force is

```
q = Gamma_xi - F_xi^T eta.
```

For either a physical direction u or a launch direction v, solve only

```
dn = -solve(F_n, F_xi*u)       [H product]
dn = -solve(F_n, F_P*v)        [B product].
```

Let d denote that total direction, including dn. Contract the objective
curvature by sector, then subtract `eta^T F_ab` once, giving `L_xi,d` and
`L_n,d` for `L=Gamma-eta^T F`. A single transpose solve gives

```
F_n^T z = L_n,d
product = L_xi,d - F_xi^T z.
```

This is the derivative of the same implicit objective, including the
nonstationary-normal case. It needs neither a stored full normal first jet
nor a normal second-jet tensor. A missing curvature callback is an error,
not an assumed zero. Common state, coefficients, clock, normal system,
contacts, orientation and reset identifiers are checked before assembly.
Normal residual and error evidence remain explicit; pointwise ball radii
are not promoted to uniform root/persistence bounds.

## Heat pencil contraction

`src/bhsm/interface/arb_heat_pencil_contractions.py` evaluates finite positive
quotient pencils with Arb arithmetic. For `A=M^-1 K`,

```
Q = exp(-ell^2 A) A^-1 / 2
A_d = M^-1 (K_d-M_d A)
D Gamma_heat[d] = Tr(Q A_d).
```

The matrix function is similarity invariant; A need not be symmetric in
these coordinates. Positive symmetric K and M are checked through an
interval LDL bound. The Frechet exponential is evaluated as the upper
right block of a block exponential. Differentiating the right inverse
through a transpose solve gives DQ without forming an inverse. The mixed
contraction is

```
A_bp = M^-1 (K_bp-M_bp A-M_b A_p-M_p A_b)
D2 Gamma_heat[b,p] = Tr(DQ[A_p] A_b) + Tr(Q A_bp).
```

Both mass terms are essential. `mixed_direction` binds one p direction and
reuses its cotangent while streaming output rows. No generic mixed
operator tensor is built. This dense kernel is for small/condensed retained
blocks; it is not a request to densify the 1,222-cell operator. Sparse or
transfer realizations may supply the same contractions, retaining the
interior spectral contribution as required by the existing scope.

## Signed vacuum subtraction and classical compression

The actual boundary owner in
`scripts/certify_n12_gate7_accepted_replay_center_outward_74d.py::_boundary`
is `-c*N/R`. The current shared coefficient owner preserves that same
binary64 c=59/30. With `d_tau=N*d_t`, the prescribed subtraction on the
**same realization** gives

```
Gamma_attached_zeta - Gamma_SM_zeta + Gamma_heat
    = Gamma_classical + Gamma_heat.
```

This is common-functional cancellation before differentiation or bounds;
it includes moving clocks, coefficients and implicit response. It does not
set heat, contacts or the classical force to zero. A rational-59/30 packet
and a binary64-59/30 packet must not be silently identified. Frozen split
sector roundoff is reported separately from the unsplit owner.

For the classical finite-N temporal action, integration by parts yields

```
D integral L_cl dt
 = [pi*dq_total + (L_cl-pi*v)*dt]_ends
   + integral [(L_cl,q-D_t pi)*dq_fixed_time + L_cl,m*dm_fixed_time] dt.
```

The current incoming terminal momentum covector and terminal time
coefficient are now evaluated from frozen gradients. The other endpoint,
moving endpoint time and contracted Euler/multiplier residual remain.
The attached-action flow must not be declared stationary for L_classical
after vacuum subtraction. This identity permits an endpoint-plus-adjoint
representation; it does not require storing a full incoming trajectory.

## Current numerical binding

`scripts/evaluate_n12_gate7_current_contractions.py` reads the frozen
local/Q66/shared/C2 packets and runs no scientific action or history producer.
The new adjoint agrees with the existing 124-variable response with
Frobenius discrepancies bounded by:

- selected eigenvalue: `2.3314907404e-69`;
- hard-response border: `9.4982807049e-64`.

The current C2 linear-coefficient element model has zeta value
`-2.8697938043233738e-27` with radius at most `2.314e-35`; its signed
73-direction first contraction has norm at most `2.966e-19`.
This is a finite-prefix coefficient-model contraction, not the complete
joint action or a physical discretization-error certificate.

The authoritative numerical packets are the two directories named in
`artifacts/flagship_integration/current_action_contractions_20260928/validation.json`.
The sufficient-state ledger is included with each packet. Earlier run
directories, if present, are preserved development output, not the current
reproduction target.

## What this does and does not complete

The directional contraction algebra is implemented and tested against
actual reduced scalar actions, noncommuting generalized-pencil actions,
moving masses, a common-scale Ward identity and congruence changes.
An equal boundary Schur response with different interior heat contribution
is explicitly tested. Current frozen normal derivatives replay through
the new evaluator.

The complete current q66 has **not** been evaluated. Its remaining consumed
quantity is the signed classical endpoint/residual contraction plus joint
graded heat contraction after common normal elimination. The other endpoint
and internal/contact realization must come from the existing coupled
equations. Neither a local density, the local 124-variable solve, nor the
finite C2 prefix supplies that quantity alone. The force norm, largest
entries, full H/B products, root and uniform error bounds therefore remain
unreported rather than replaced by subsystem numbers.

No new physical law is requested. The next calculation is to supply those
contractions to the implemented evaluator through the existing coupled
operator/adjoint formulation, keeping only the consumed endpoint, residual,
transfer/interior-trace and error information. Gate7_closed=False and
FULL_BHSM_COMPLETE=False.
