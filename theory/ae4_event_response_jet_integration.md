# AE4 response integration during Gate 7 certification

The existing variable audit identified an implementation handoff between the
finite-core HS response and the already assembled event equations. The new
`ae4_event_response_jet_integration` module implements that handoff's algebra.
It introduces no action term, fitted coefficient, family assignment, domain,
background or terminal load. The running Gate 7 action, center and proof
contract remain authoritative for promotion of the carrier jets.

## Reuse the finite-core transport

The saved 1222-segment current-C2 calculation supplies the coefficients of

```
M' = a + s u
M'' = b + 2 c u + q u^2 + s v
u = D_H L_terminal; v = D_H^2 L_terminal.
```

`substitute_terminal_hs_jets` consumes the decimal coefficients and requires
both terminal derivatives explicitly. It performs no new segment propagation.
The core, source profile, spectral parameter and terminal value must remain
those used to generate the coefficients. Changing them requires a new
coefficient evaluation. Reference zero or nonzero derivatives in the artifact
are software witnesses, not selected physical boundary conditions. Decimal
arithmetic alone supplies no outward remainder certificate.

## Transport derivatives through the event equations

For one real source on a common fixed domain, write the supplied derivatives
of parent, coupling and retarded child blocks as `(P, B, L)`. The existing
stationarity equations are

```
P q + B c + C^dagger lambda + J = 0
B^dagger q + L c = 0
C q = d.
```

The implementation differentiates `L X = B^dagger` without commuting matrices:

```
L X'  = B'^dagger - L' X
L X'' = B''^dagger - L'' X - 2 L' X'
E = P - B X
E'  = P' - B' X - B X'
E'' = P'' - B'' X - 2 B' X' - B X''.
```

With `K = [[E,C^dagger],[C,0]]`, `y=(q,lambda)` and `f=(-J,d)`,

```
K y'  = f' - K' y
K y'' = f'' - K'' y - 2 K' y'.
```

The child state and all four event tractions are differentiated as well.
The function reports the residual at each order for the parent equation,
child equation and response constraint. Every input jet contains the value,
first derivative and second derivative, not factorial-scaled coefficients.
Unknown derivatives cannot be omitted. Singular child or reduced systems fail
instead of acquiring a regularizer. Dense finite matrices are a conditional
implementation; continuum operators still require their retarded domain and
outward control.

`canonical_noether_flux_balance_jet` then differentiates the existing
`2 Re <T q, traction>` contraction with a fixed anti-Hermitian generator. It
retains derivatives of both factors. This does not evaluate the complete
composite-minus-matched-parent Hamiltonian.

## Completion handoff

The existing asset entry point now consumes the later enclosure/state and
six-sector assembly results. It preserves the unresolved values instead of
reopening the already supplied carrier, family modes or mass mechanism. Its
functional description uses the selected owner's zeta/eta prescription;
that prescription is not another independent determinant.

| Existing object | Remaining physical input or evaluation |
| --- | --- |
| Frozen Gate 7 center and causal proof | Signed tensor composition, outward remainder and two-radius certification on the active track |
| Full finite-core HS response law | Physical terminal load and its two HS derivatives; source/domain projection and full spectral integration |
| Six-sector Schur/KKT and event identities | Physical sector matrices and their compatible source/constraint derivatives |
| AE3.1 charged-lepton Yukawa and conditional mass operator | First-order LR operator on the retained domain, global poles/residues and matched-parent readout |
| Neutral three-slot response | Lorentzian returned operator and weak-flavor intertwiner |
| Up/down ratio operators | Action third variations and projections fixing their two missing normalizations |
| Common scale contract | Explicit universal calibration for the finite-input route, or evaluated impedance crossing for the zero-input extension |

The materializer reuses all saved terminal-HS reference rows and exercises the
existing six-sector direct sum with explicitly synthetic finite matrices.
It does not assert a physical projection between those reference rows and the
synthetic sector matrix. That projection remains an owned physical input.
All physical-promotion and full-completion flags remain false.

Verification compares the response jets against 55-digit derivatives of the
independent, unreduced parent-child KKT system with complex noncommuting blocks
and moving constraints. Terminal substitution is compared against full segment
jet propagation for both chiralities. Tests cover missing, nonfinite,
incompatible and singular inputs, the existing zero-order solve, and Noether
balance. Artifact generation is deterministic and performs no shard or
finite-core campaign.

The integration pass passed 58 selected tests across the response, existing
asset, completion map, event assembly, lepton, neutral, quark, internal
transport and enclosure modules. Six unrelated materializer tests were
excluded. The response artifact, existing asset artifact and canonical system
map were each generated twice with byte-identical output. Frozen prediction
integrity and forbidden-claim audits passed. The pre-change Gate 7 action
tuple, irreducible objects, next dependency and claim boundary compare equal.
