# Interval-13 null: two-sided reset and attachment owner test

Base: `ed61d89c3a7946f5cd4f5af9e321771dabe2edc1`, branch
`theory/gate7-66d-reduced-adjoint-integration`.

**TWO_SIDED_SCALAR_OWNER_NOT_YET_DERIVED.** The fourth two-sided reset
configuration condition is present and explicit, but it annihilates the current
left-descriptor null with the opposite state fixed. The fuller seam equations
have no supplied pullback to that independent descriptor. This bounded trace
does not prove that the physical interface cannot select it; it identifies the
missing derivative binding. No scalar condition is invented or appended.

## Exact reset row owner

`src/bhsm/interface/aether_full_reset_action_jacobian.py:248-410` assembles the
paired residual; lines 565-635 assemble its analytic derivative. For event and
child states `Y_e,Y_c` (each 98 components), the zero-based row ledger is:

| Rows | Owner |
| --- | --- |
| 0:25 | Event multiplier constraints and canonical energy |
| 25 | Selected ordered event eigenvalue |
| 26:30 | Four boundary configuration differences |
| 30:55 | Child multiplier constraints and canonical energy |
| 55:57 | Two canonical momentum differences |

Fixing the event leaves `25+4+2=31` child equations. The four raw configuration
rows are exactly

```
B_conf = (T(q_child-q_event), x_D(q_child)-x_D(q_event))
u_b = sum_{k=1}^12 (-1)^k q_u,k
v_b = sum_{j=0}^11 (-1)^j q_v,j
q_w = q0 + u_b - log(cosh(2 v_b))/2
x_D = q0-q_w = -u_b + log(cosh(2 v_b))/2.
```

The chart and its derivative are owned by
`aether_cross_resolution_reconnaissance_v21_35.py:2751-2795`. The code sometimes
calls x_D the second attachment coordinate q_c; the N3 incidence owner calls
the global scale q_C and the depth x_D. These names do not identify x_D with s.
The reciprocal matcher `-q_C+q_W+x_D=0` is an identity of the state map, not an
additional equation on an independent coordinate
(`aether_n3_event_attachment_state_incidence_v17_89.py:38-65`).

In action coordinates the two configuration blocks have signs

```
D B_conf = [-C_event W_q^-1, +C_child W_q^-1]
C_side = [T; D x_D(q_side)].
```

The retained inverse-square-root row normalization multiplies all four rows;
therefore stored normalized row 29 alone is not the raw fourth condition. The
new diagnostic reconstructs all four normalized rows from the pure chart and
checks them against the frozen full-reset analytic Jacobian. It does not rerun
the reset action or its derivative producer. The maximum entrywise center replay
difference is `1.666e-15`; it is not a new outward reset certificate.

The canonical rows are `H_m^(1/2)(p_child-p_event)`, with fixed historical
normalization. Persistence's seven Stage-B rows are instead three traces, two
canonical momentum rows and two dynamic flux rows. Their flux sign is
`child_flux+momentum_rate-force+event_flux`. The retained fourth configuration
condition is not among those seven rows. This difference in row ledgers is
real, but it does not establish a descriptor-dependent persistence descendant.

## What the carried descriptor is

The exact fixed-s field selects the simple eigenline of the **raw** reduced
Hessian `D(Y)=L_zz(Y)`, `z=(velocity,multipliers)` (61 coordinates). Its physical
fiber is `D(Y) psi=lambda(Y) psi`, `lambda(Y)=s`. The augmented shooting model
carries s independently and transports it by `ds/darc=Delta/||G||`, where
`Delta=Dlambda[G]`. It does not recalculate s from a noisy eigenvalue at every
step. See `aether_forward_c2_exact_fixed_s_field.py:28-48,77-87,135-145,197-217`
and the collocation `_field` at lines 67-77.

Thus the carried descriptor is a derived child spectral scalar represented as
an independent proof variable. It is not a lapse, an environment datum, a seam
depth, the operator spectral parameter z, or proper time.

The source-level maps to the other quantities are:

```
physical ds = 1e-7 * d(proof descriptor)
N_boundary(Y) = exp(sum_{k=1}^12 (-1)^k m_k)
x_D(Y) = x_D(q)
d tau/darc = N_boundary(Y) * s / ||G(Y,s)||.
```

The test scale `1e6` does not enter any physical equality. The lapse is owned by
the action's multiplier field (`aether_n3_exact_full_local_action_jet_v17_60.py:
217-225`) and the persistence clock (`certify_n12_candidate_positive_duration_
persistence.py:81-84`). The proper-time density is recorded explicitly by the
frozen endpoint producer at lines 184-195.

For the two-sided state product the available map is
`(Y_e,Y_c,s_c) -> (x_D(Y_e),x_D(Y_c),N(Y_e),N(Y_c),s_c)`.
No inverse or equality identifying s_c with a relative attachment or opposite
lapse is supplied. At fixed state, `partial_s x_D=partial_s N=0`.

## Evaluations on the frozen null

Use the positively oriented unit null from the previous checkpoint, without
re-solving the shooting system. Its left state is exactly zero, and its left
physical descriptor component is `5.9056854121223064e-8`. With the opposite
state held fixed, the following zeros are structural and do not depend on a
finite-difference tolerance or transferring a reset Jacobian to node 13.

| Candidate | D B[u] | Authority |
| --- | ---: | --- |
| Fourth reset attachment configuration | 0 | State-only two-sided difference |
| Three trace differences | (0,0,0) | State-only two-sided difference |
| Reciprocal depth matcher | 0 | Identically zero pullback |
| Two canonical momentum differences | (0,0) | State-only reset rows |
| Two persistence dynamic flux rows | (0,0) | State-only, event flux fixed |
| Difference of boundary lapses | 0 | State-only; no separate lapse-equality row in the reset owner |
| Proper-time density at node 13 | 1.1838581180436112e-4 | Derived output, **not a two-sided matching equation** |
| Full seam/attachment graph response | unavailable | Missing opposite-side/trace/attachment derivative with respect to s13 |

For the density `rho=N s/g`, the reported center derivative retains all terms:
`D rho=(s/g)DN+(N/g)Ds-(Ns/g^2)Dg`. Here `DN=0` on the left and the frozen
descriptor norm derivative supplies `Dg`. A nonzero density response cannot be
promoted to a matching condition by setting it to zero. Unit directions are
not assertions of admissible finite steps inside the physical tube.

As a guard against relocating the equation, the raw fourth row evaluated at
the right endpoint gives `D x_D(Y14)[u_right] = -4.83880314e-5`. Its restriction
to the frozen 66D child state basis has norm `0.06665406035`. These are center
diagnostics, not new equations: holding that right attachment value fixed
would act on the existing child tangent. **Nodes 13 and 14 are consecutive
history points, not event/child copies of one physical seam.** No source
authorizes substituting them for the two sides or reclassifying this response
as the missing reaction scalar.

If the opposite state or attachment varies with s13, its derivative must be
supplied explicitly. The structural-zero results do not set such an unknown
derivative to zero or establish zero total response for an unspecified graph.

## Boundary graph comparison and stop

The owned outward conormals have opposite signs. In common coordinates a
supplied trace transport gives `q_e=C(F_B)q_c` and the canonical relation
`p_c+C(F_B)^*p_e=J_enc`. The physical compatibility is intersection of the child
graph with the pulled-back opposite graph. The full attachment variation also
contains `sum_s <Pi_e,s,D_F C_s[eta]q_c,s>` and the surface/constraint terms;
dropping those would change the variational problem.

These signs and conditional equations are explicit in
`bhsm_owner_authorized_encapsulation_interface_action.md:65-99,263-328` and
`bhsm_covariant_interface_seam_selection_audit.md:73-108`. The latter's selected
area action and local Maxwell rank witnesses do not produce the physical
reduced stationary N12 graph or its s13 derivative (lines 207-221).

The two-sided operator owner likewise gives
`S=M_event+U_R^dagger M_child U_R+W_phys`. A vanishing local fermion W does not
erase the opposite response. The one-seam direct descriptor already retains
both arms at the common E1/C2 trace; its word “descriptor” denotes the joint
operator realization, not the scalar shooting s. None of these operator
identities supplies a scalar row on the present 75-dimensional local space.
The historical two-seam and later one-seam conventions are recorded as distinct
owner formulations; neither is silently substituted into the local residual.

For any actual local row b, rank can rise from 74 to 75 only if b[u] is nonzero.
All recovered fixed-opposite-side left-state rows annihilate u. No usable
nonzero scalar owner was recovered, so no 75-by-75 system, inverse, condition
number or reaction replay is claimed. The 66D child and seven boundary
directions remain unchanged.

The exact missing object is a source-bound lift from `(s13,p,q)` to the two
traces, relative attachment and opposite-arm response **at the same physical
interface**, together with its derivative and the selected scalar component of
the existing seam equations. Stop here; do not search for a generic scalar or
perform nonlinear work.

Reproducer: `scripts/audit_n12_gate7_two_sided_null_owner.py`. Packet:
`artifacts/flagship_integration/gate7_two_sided_null_owner_20260926/`.
It freezes source hashes, literal source lines, the row replay and evaluations.
Two fresh processes reproduce the report and arrays byte-identically. Validation:
`python -m pytest --noconftest tests/test_gate7_two_sided_null_owner.py tests/test_gate7_local_null_classification.py -q`
passed **8 tests**. They cover the exact chart/depth identity, attachment
derivative, reset signs and row replay, fixed-side null response, source hashes,
and preservation of the unresolved classification.
`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.
