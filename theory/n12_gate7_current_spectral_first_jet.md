# Current N12 spectral coefficients and first launch jet

Base: `978cbe73`, branch `theory/gate7-66d-reduced-adjoint-integration`.

The current node-13 spectral coefficient first jets are now enclosed in
Arb512 on the stored recentered 73D chart. This calculation uses the frozen
state and chart, not a new local action derivative. The complete joint
history operator is **not** yet instantiated. This is decision **B**:
the finite-N law exists, but its current-base history realization remains
incomplete. No absent continuum physical owner is claimed.

## New current-center numerical result

In the existing attachment coordinates,

```
x = log(RADIUS0/2) + q0 + u_L - log(cosh(2v_L))/2,
l = log N = sum_j (-1)^(j+1) m_j,
D x = Dq0 + Du_L - tanh(2v_L) Dv_L,
D l = sum_j (-1)^(j+1) Dm_j.
```

The 98-state action weights are undone before evaluating these expressions;
the parameter columns remain the frozen 72 reset-family labels plus flow.
The separate proof descriptor scale is not inserted into the physical
radius or lapse. All eight first jets are saved as 1x73 interval rows.

| Coefficient at current node 13 | Midpoint (full intervals saved) |
|---|---:|
| log R4 | -0.005096113331339609 |
| N | 0.7003740050513328 |
| R4^-1 | 1.005109120603006 |
| R4^-2 | 1.0102443443193483 |
| D_tau log R4 | 0.08877623404661852 |
| Zeta density per proper time, -(59/30)/R4 | -1.9767146038525787 |
| Zeta density per coordinate time, -(59/30)N/R4 | -1.3844395239436895 |

The proper-time radius rate is the existing `(D_q x . qdot)/N`. Its first
variation uses the derivative of tanh in this coefficient formula; no
second **operator** jet is computed. Zeta density derivatives retain the
lapse term, so moving measure is not silently frozen.

An independent binding uses rows A and B of the frozen native trace jet:
`Dx=((1-tanh(2v))/2) Dtrace_A + ((1+tanh(2v))/2) Dtrace_B`.
The two interval results overlap zero in their difference; its Frobenius
upper bound is **8.612828e-15**. The unchanged tolerance remains
`8.915423761304125e-7`.
Enclosures concern this stored center and its chart derivatives, not an
entire history tube or a bound for the missing full response.

## Finite-N law and dependency table

`aether_ae2_one_seam_descriptor::_element` and
`aether_forward_c2_finite_core_descriptor::assemble_finite_core_descriptor`
already provide the physical scalar/product-Dirac action elements:

```
S=[[1,-1],[-1,1]], A=[[2,1],[1,2]], C=diag(-1,1),
M_e=h_e A/6,
K_e=S/h_e + mu^2 exp(-2 x_mid) M_e
    + epsilon mu exp(-x_mid) C          (last term: product Dirac only),
dK_e=K_xmid (dx_left+dx_right)/2 + K_h dh_e,
dM_e=A dh_e/6.
```

These are a generalized form pencil `K-lambda M`; K alone is not the
heat operator. The direct domain eliminates E0 and the far Friedrichs
proof-core node and retains E1/C2 once. It adds the owned contact once at
that seam. The equivalent Schur assembly is
`M_f+U_R^dagger M_C2 U_R+W_phys`; summing both representations double counts.
Positive durations give positive mass, and the retained forms have the
stated real self-adjoint transmission realization. This is a symbolic
domain statement until the current paths and contacts are assembled.

| Ingredient | Status | Scope |
|---|---|---|
| Current center, action weights, recentered chart | OWNED_NUMERICALLY | Reused frozen |
| Eight current spectral/measure coefficient first jets | OWNED_NUMERICALLY | New packet |
| Joint finite-element form, first coefficient jets | OWNED_SYMBOLICALLY | Executable existing law |
| Grading, regulator and gauge quotient | OWNED_SYMBOLICALLY | Explicit retained ledger below |
| 1,222 historical coefficient intervals and duration actions | BOUND_AVAILABLE | Historical base only |
| Incoming and C2 coefficient histories at current base | OWNED_SYMBOLICALLY | Current-base transport/propagation needed |
| Reset transport and gauge/scalar/contact laws | OWNED_SYMBOLICALLY | Not numerically instantiated along current joint history here |
| Historical zeta covector and full graded heat bound | BOUND_AVAILABLE | Not transplanted across the base mismatch |

No entry is labeled ABSENT_PHYSICAL_OWNER: the issue is an uncomputed
current realization, not missing physics. The finite-core law does not
require solving the entire continuum hierarchy to assemble a finite form.

The exact graded ledger is inherited from
`BHSM_aether_common_quantum_superdeterminant_v15_96.json`:

| Sector | Levels | Signed multiplicity | Current local coefficient |
|---|---|---|---|
| HS | m>=1 | +4m^2 | m^2 R4^-2 |
| Transverse gauge | m>=2 | +24(m^2-1) | m^2 R4^-2 |
| Weyl | n>=0 | -48(n+1)(n+2) | W=epsilon(n+3/2)R4^-1, factorized form |
| Longitudinal + complex ghost | matched modes | 0 | BRST cancellation; global gauge zero modes quotiented |

These formulas cover all retained angular levels without introducing a
cutoff or doubling the Weyl multiplicity for the two factorization signs.
The common regulator is ell_kappa=1 in retained units. The current
finite-endpoint functional is `-STr E1(ell_kappa^2 P)/2`; the fixed-reference
derivative follows its owned first-variation contract. No new absolute
reference normalization is selected. The local Casimir/zeta term is
`-(59/30) integral d_tau/R4` and is subtracted once in the replacement.
The old periodic lattice is not imported as a current finite-history domain.

## Why the stored 1,222 arrays cannot be used unchanged at node 13

The full stored coefficient enclosure is

```
old log R4 in [-0.005096247479711742, -0.005096247266689165].
current log R4 = -0.005096113331339609 (outward interval saved).
current x - old global upper > 1.33935349e-7.
```

This is a rigorous disjointness check using the stored interval endpoints
and the current Arb center. It concerns the **certified stored coefficient
cover**, not a claim that no larger exact family exists or that the two
points are different physical children. No chart transport connecting the
old operator enclosure to this new coefficient base has been supplied by
relabeling the local 73D chart.

The older incoming amplitude box is similarly based at the old seam radius.
The current corrected point cannot be spliced onto either arm while retaining
its old durations and claiming the same history. The 1,222 interval-action
certificates are preserved at their original base; none of their expensive
local rows is recomputed. A current-base history construction must propagate
the coefficient paths and their pullbacks, retaining endpoint/midpoint
incidence and the shared descriptor/normalization equations.

The nearest pending numerical object is therefore the **current-base
incoming/C2 coefficient history and its launch pullback**, to insert into
the existing one-seam pencil. Merely writing another matrix assembler would
not repair the disjoint base; the assembler already exists. No phenomenological
contact, new environment law, or history selection was substituted here.

## First force versus derivative of a reaction

The user's first-jet scope is preserved: `D Gamma=Tr(Q dP)` requires only
the first operator jet. There is no second operator jet in this packet.
The existing superdeterminant derivative contract also distinguishes
`D_b D_a Gamma=Tr(DQ[P_b]P_a+Q P_ab)`. If a native reaction is a first
variation, its derivative cannot generally be obtained by reusing a scalar
first-force covector seven times. An owner identity may remove particular
mixed terms, but that must be demonstrated. This distinction does not
prevent the current first-coefficient calculation above.

## Unfinished result

The full `P_joint(xi0)`, its history first jet, and `R_heat/zeta_7x73` remain
uncomputed. Seven adjoint residuals, completed rank, rowwise correction
norms and the largest correction therefore remain null. The local response
is not promoted. Historical heat suppression is not rounded to zero or
transferred to the current history without binding. `Gate7_closed=False`;
`FULL_BHSM_COMPLETE=False`.

Producer: `scripts/derive_n12_gate7_current_spectral_coefficients.py`.
Packet: `artifacts/flagship_integration/gate7_current_spectral_20260927/`.

Validation: **66 focused tests pass** (six new current-spectral tests plus
the 60 checkpoint tests, `pytest --noconftest`). Two independent runs produce
byte-identical `arrays.npz` and `report.json`; their hashes are recorded in
`reproduction.json`. No frozen scientific packet was modified.
