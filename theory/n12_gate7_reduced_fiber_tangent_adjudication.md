# Owner-induced reactions and reduced physical history tangents

Base: `8e52ee75bec0e14cce32f8250dce833fb709291c`, branch
`theory/gate7-66d-reduced-adjoint-integration`.

**STOP_INTRINSIC_HISTORY_TANGENT_COMPONENT_REMAINS.** Preserve
`EULER_DIRAC_DESCRIPTOR_FIBER_OWNER_RECOVERED` as ownership and stored-center
invertibility. Do not promote the center certificate. The original descriptor
allowance remains exactly the frozen rational value, approximately
`8.915423761304125e-7`.

The prior 8-by-66 reaction discrepancy is vertical in the declared split, but
this fact alone is tautological: that calculation held p fixed and changed only
q. Testing all shooting derivative rows reveals a nonzero intrinsic Schur
forcing. The reduced right-endpoint tangent spans agree; the reduced paired
history tangents do not. Layer C is not rebound.

## Declared split and metric

Use the frozen node-14 trial matrix
`P=[Pp,Pq]=diag(X[Z,L],1)` with 66 intrinsic coordinates and eight reactions
(seven boundary/interface directions and the descriptor). Z is the final
Stage-B child kernel; L is its action-Hessian complement. Compute the exact
inverse Pi of the stored P for algebra, retaining the same subspaces, then
`R_p=Pp Pi_p`. This is an **oblique** reduction. Replacing it with Euclidean
orthogonal removal of the boundary subspace would change the declared split.

The angle metric is the stored positive action norm
`||W_state dy_raw||_2`. The physical tangent frames B already map to these
weighted coordinates; weights must not be applied twice. The Hessian defining
L need not be positive and is not used as a principal-angle metric. For paired
endpoint history columns we use the direct sum of the two positive action
norms as a diagnostic, not as a new physical radius/budget norm.

At node 13 use the corresponding frozen Z13/X13 and the saved final-R23
boundary lift from the descriptor-owner packet. No action, Stage-B, local
proof, or 8-by-8 extraction is rerun.

## Signed owner-induced contribution

Reuse the previous packet's left-descriptor derivative adjustment
`delta_s=b_fiber V13`, of norm about `9.503752405e-7`. Let

```
n = N13 e_s
f = Pi n delta_s = (f_p,f_q)
Msplit = Pi M13 P = [[Mpp,Mpq],[Mqp,Mqq]].
```

If right p is held fixed, the q-only response is
`dq_fixed=-Mqq^-1 f_q`. Its component norms are:

| Contribution | Frobenius norm |
| --- | ---: |
| Seven boundary coordinates | 2.672072164e-9 |
| Descriptor coordinate | 9.5887339998e-7 |
| Complete q increment | 9.5887712307e-7 |

The raw previous reaction error against truth has lift
`Pq(Dnew-Dtruth)`. Its intrinsic coordinate projection has Arb upper bound
`1.555e-148`, and its vertical reconstruction defect is below `7.544e-145`.
Thus that particular error is indeed in the reaction space. The excess
`6.5143548358e-8` is a difference of norms, not a signed tangent vector that
can itself be projected. The complete signed error matrix is what is reduced.

However, the same q-only correction leaves the intrinsic equation residual

```
f_reduced = f_p - Mpq Mqq^-1 f_q.
```

Its Frobenius norm is approximately **9.3342196164e-6** with a strictly positive
Arb lower bound. Ignoring this residual would omit the p rows of the shooting
derivative. The complete response instead obeys

```
S  = Mpp - Mpq Mqq^-1 Mqp
dp = -S^-1 f_reduced
dq = -Mqq^-1(f_q + Mqp dp)
dV14 = Pp dp + Pq dq = -M13^-1 n delta_s.
```

| Complete response | Frobenius norm |
| --- | ---: |
| Intrinsic p coordinates | 9.3174896129e-6 |
| Boundary q coordinates | 2.6722583003e-9 |
| Descriptor q coordinate | 9.5885574411e-7 |
| Intrinsic weighted state component | 9.3174896129e-6 |
| Boundary weighted state component | 9.1631345584e-6 |
| Full 74-coordinate change | 1.2986484547e-6 |

The large intrinsic and boundary state components cancel substantially under
the oblique split. Their norms cannot be added or interpreted as orthogonal
energy budgets. The signed full-response decomposition has residual below
`4.077e-144`; the complete shooting derivative change
`M13 dV14+n delta_s` is below `2.714e-158` in Arb arithmetic.

These lower/upper bounds concern the frozen coefficients. The descriptor
gradient used to obtain delta_s is still diagnostic; they do not supply a new
physical derivative enclosure or prove physical instability.

## Reduced tangent comparison

The original family is the frozen full-owner pair `(V13,V14)`, using the same
66 node-14 child parameters at both endpoints. The owner-consistent linear
response is `(V13+e_s delta_s,V14+dV14)`. It enforces the fiber derivative and
preserves the **existing** shooting derivative residual; that existing defect
is not set to zero or promoted to an exact variational solution.

Remove reactions through each declared p/q split and lift the retained state
components into the action metric:

```
T_old = [ B13 (R_p13 V13)_state ; B14 (R_p14 V14)_state ]
T_new = [ B13 (R_p13 V13new)_state ; B14 (R_p14 V14new)_state ].
```

| Action-metric comparison | Largest principal angle | Projector operator residual | Projector Frobenius residual |
| --- | ---: | ---: | ---: |
| Reduced right endpoint alone | 1.292e-13 degrees (roundoff) | 1.545e-15 | 5.729e-15 |
| Reduced paired left/right history | **0.000120749441 degrees** | **2.107475315e-6** | **2.980420173e-6** |

Both reduced families have rank 66. The paired comparison has one resolved
nonzero angle; the next angle is about `2.03e-13` degrees. All 66 angles are
saved. An independent Arb Gram-projector evaluation encloses the paired
Frobenius difference and gives a strictly positive lower bound, removing the
possibility that the displayed paired discrepancy is merely QR roundoff.

Right-endpoint agreement is expected: after p/q projection both full-rank
matrices span the same fixed Pp subspace. It can hide a change in the history
map. The paired comparison cannot hide that change: its left projection stays
fixed, while its right projection acquires dp. A change of the common 66 input
basis does not remove the paired projector difference. This is the relevant
distinction for causal Layer-C history aggregation.

## Action-owned authority and stop

The retained authority is the Stage-B state subspace Z, final normalized R23
interface, H_T-defined boundary complement L, and the Case-B X/B frame bridge.
The former descriptor graph comes from the stored causal reset-plus-flow
family. The new graph uses the physical fiber covector but only its stored
diagnostic Dlambda. These are not yet an identical certified physical history
jet. The exact nonzero fiber **value** defect at node 13 also remains unchanged.

It is therefore not justified to reclassify the entire failure as a harmless
reaction representation mismatch or to start Layer C by simply deleting q.
Slaved reactions are not gauge directions; their induced output derivatives
must be retained when reconstructing rates. A right-endpoint projector test
alone would pass without testing those history derivatives.

Before rebinding, establish an owner-bound fiber-consistent center and a common
action-certified first-order history tangent, with explicit uncertainty on
Dlambda and its left-to-right Schur transport. Decide that tangent authority
before changing any reduced response/output binding. No such recentering or
new derivative producer is attempted here.

Reproducer: `scripts/compare_n12_gate7_reduced_fiber_tangents.py`.
Packet: `artifacts/flagship_integration/gate7_reduced_fiber_tangents_20260926/`.
Ownership and center invertibility remain frozen; no tolerance relaxation,
center-certificate promotion, nonlinear work or Layer-C rebinding occurs.
`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.

Validation: two independent fresh-process runs produced byte-identical
`report.json` and `arrays.npz`, recorded in the packet's `reproduction.json`.
The focused reduced-tangent and appended-center tests passed: **8 passed**,
using `python -m pytest --noconftest tests/test_gate7_reduced_fiber_tangents.py
tests/test_gate7_appended_fiber_center.py -q`. No scientific producer was run.
