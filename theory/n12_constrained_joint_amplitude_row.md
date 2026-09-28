# Formation amplitude in the existing joint KKT functional

The user decision of 28 September 2026 fixes the interpretation: the
existing formation amplitude is a variational coordinate of the complete
constrained joint action. Zero external birth source does not fix it.
No amplitude law, multiplier, endpoint, or completion condition is added.

## Existing owners and signs

The amplitude in `n12_desingularized_finite_history_operator_parameter.md`
is the incoming selected signed descriptor at the moving birth endpoint,
with terminal event held fixed in that particular family. The duration is
derived from the same flow, not independently assigned. The current proper
clock includes lapse: `d tau_minus/ds=-N*s/Delta`; its event germ has
`T(A)=-N_E*A^2/(2*c_E*b_E)+o(A^2)`.

`formation_stationarity_kkt.assemble_stationarity` uses
`L=Gamma+mu^T R`. This is the user's minus-multiplier convention with
`mu=-lambda`. `derive_n12_gate7_formation_stationarity_inputs.py` supplies
the current 32 terminal equations as functions of the two endpoint states.
They do not contain the birth amplitude explicitly. At fixed terminal
coordinates, `R_A=0`; along a coupled solution, `D_A R=R_y*y_A` must still
be carried. None of these terminal equations algebraically selects A.
The birth condition `Gamma0_birth U=0` in
`n12_compact_history_endpoint_role_provenance.md` is the zero-source field
reference, not an equation fixing the geometric amplitude.

These observations do not set the existing 24 local action multiplier
coordinates, the terminal KKT multipliers, the event multipliers, or the
history adjoints to zero. Local multiplier dependence already present in
the action is not added again as a second action sector.

## One adjoint for the physical and amplitude rows

Write the retained internally solved equations as `F(xi,A,P,n)=0` and
the uneliminated existing constraint/event rows as `R(xi,A,P,n)=0`.
Do not register a row in both systems. With

```
L = Gamma + mu^T R - eta^T F,
F_n^T eta = Gamma_n + R_n^T mu,
```

the two force outputs of the same realization are

```
q_xi = Gamma_xi + R_xi^T mu - F_xi^T eta,
f_A  = Gamma_A  + mu^T R_A  - eta^T F_A.
```

Here `F_A` is the internal-equation forcing, distinct from the final
amplitude stationarity row `f_A`. Its contribution cannot be omitted
because the terminal constraints have zero explicit amplitude derivative.
All signed objective sectors are combined before this common adjoint.
Constraint curvature is included in H/B products before subtracting the
single `eta^T F_ab` contraction. Multipliers are fixed coordinates only
when taking partial derivatives of this full Lagrangian; their equations
and responses remain in the coupled saddle solve.

The evaluator now returns raw `Gamma_A`, explicit multiplier terms,
internal-adjoint terms, endpoint/event and contact/heat subtotals, and
the final constrained row. Endpoint and contact subtotals belong to the
raw partial and are not added twice. It refuses an amplitude request with
any absent amplitude partial or internal forcing. The new tests compare
against an explicitly reduced nonlinear constrained action, and verify
invariance under `Gamma -> Gamma+kR`, `mu -> mu-k`.

If a future source-bound existing equation slaves A, its derivative is
composed into the reduced action instead; no independent `f_A=0` is then
added. If A is retained among the internally solved saddle variables,
`f_A=0` is one of their existing stationarity equations. This does not
declare a new 67-dimensional physical tangent or alter frozen Q66.

## Smaller temporal contraction on the fixed-terminal orbit-cut family

The existing amplitude family restricts the same incoming curve to a
moving birth point; it does not change the terminal event or child. At
the birth endpoint, let `Y_A=Y_s`, `t_A=s/Delta`. The exact temporal
first-variation formula from `n12_current_temporal_force_source.md` gives

```
birth term = -pi*q_A -(L-pi*v)*t_A = -L*t_A,
q_A = v*t_A.
```

For the induced tangential reparametrization in the interior,

```
S_Y*Y' + S_t*t' =
 -E_q*(nu*v) + nu*L_m*m' + (E_q*v-L_m*m')*nu = 0.
```

This identity retains nonzero Euler and multiplier residuals; it does
not assume the stored field is exactly Euler--Lagrange stationary.
It eliminates this particular tangential temporal integral. It does not
eliminate the general 66 physical-direction integral, nor the constraint
forcing of a non-tangential correction made by the joint KKT solve.

For the exact fixed-terminal cut, explicit event, child, reset-transport
and terminal-contact derivatives vanish. Their values and internal
couplings still enter the joint spectral operator and its response.
When the coupled variation moves the terminal point, their nonzero
derivatives belong to the full evaluator, not to this restricted shortcut.

The attached/zeta cancellation is also composed with the moving clock:

```
D_A Gamma_attached - D_A Gamma_zeta
    = -(L_attached-L_zeta)*t_A.
```

The script `contract_n12_constrained_amplitude.py` contracts these
identities using only frozen current operands, including their first 66
variations. The current signed descriptor is negative and excludes zero.
Those numerical contractions are a local algebra replay, not a
positive-amplitude birth member or a full force evaluation. It is not
legitimate to assign that point as the missing birth endpoint.

## Smaller full-domain heat contraction for this amplitude direction

On an existing positive self-adjoint coupled realization, keep the
proper-time coefficients fixed at fixed physical time and extend the
birth endpoint by `dT>0`. The birth source reference is Dirichlet. The
Hadamard identity for a normalized mode of the **complete coupled
operator** is `D_T lambda_k=-|u'_k(birth)|^2`. For product-Dirac channels
the conormal is `(D_tau+W)u`; on the zero birth trace it equals `u'`.
Transmission/contact terms at the fixed terminal seam do not move, but
they determine the normalized global modes. Thus

```
D_T Gamma_heat = -1/2 sum_k w_k exp(-ell^2 lambda_k)
                              |u'_k(birth)|^2/lambda_k.
```

This is one graded boundary spectral contraction, including the incoming
interior spectrum. A boundary Schur response alone is insufficient.
For a maximal domain the equivalent relative spectral-measure contraction
must exist with its owned projected tail; this finite-mode formula does
not select a far cutoff. Retained signs, multiplicities and the positive
quotient are unchanged. No sign of the graded sum is assumed.

On a normalized-coordinate discretization the same derivative uses
`P_A=M^-1(K_A-M_A*P)`. The existing `HeatPencil` implementation retains
this moving-mass contribution. Dropping it would not evaluate the same
shape derivative. The new continuum interval regression checks the
boundary contraction against the differentiated heat action, while the
existing pencil regression checks the moving-mass form.

## Current completion state

The amplitude ownership ambiguity is resolved. Numerical full-amplitude
stationarity is not yet evaluated: the frozen packets do not contain a
positive-amplitude joint realization, its complete heat/contact cotangent,
or the solved joint KKT multipliers. These are computational inputs to the
existing force/root obligation, not missing physical laws or new gates.
The smallest next evaluation is the signed joint amplitude/physical
force at a coupled trial state, retaining A as an unknown. Complete
history storage is unnecessary. No further amplitude interpretation is
requested from the user.

`Gate7_closed=False`. `FULL_BHSM_COMPLETE=False`.
