# Port-preserving finite initial-value response of the integrated Maxwell action

Norman P. Carberry / BHSM continuation — 17 October 2026

## Result and strict scope

This continuation **uses the saved M/B/K and W/Wdot arrays** from
`BHSM_integrated_magnetic_source_20261017`. No local Maxwell coefficient,
radial quadrature, or background state was regenerated. The previous package's
50 manifest entries and the uploaded history package's 47 entries were verified.
The extracted inputs retain source revision
`70e82fd4dbe5f53ff27ae17f6aaac7a4727c1fde`; this is an input pin, not a new remote-head check.

Two finite, time-dependent initial-value response maps have now been evaluated,
one for each supplied arm. The maps leave the material-wall traces as arbitrary
inputs, return the interior state and weak boundary response, and include the
source-dependent momentum. They do **not** close the exterior, choose initial
physical fields, identify the before/after interface, or determine a quantum state.

The temporal calculation is four-stage Gauss-Legendre collocation using exactly
the four exported interior nodes per arm. Endpoint coefficient samples are used
to reconstruct the endpoint action data. This is a finite numerical realization,
not a continuum retarded Green certificate. No time interpolation or new samples
are introduced; the physical time error is not enclosed. The stage approximations
are collocation stage values, not a proof of exact causal support inside one step.
No condition is imposed at the final time to close or reflect the history.

The adopted collider choices remain unchanged. The supplied histories are still
provisional and contain the recorded calibrated ancestry. Matter, Higgs, moving
geometry, interface, native quantum, and inherited-state responses have not been
added or assumed zero in the **complete** physical model. This calculation isolates
the already evaluated Maxwell quadratic component with its background held fixed.
The underlying n0 background defects are not corrected by this n1 response.

## 1. Retain wall trace variables instead of eliminating their equations

The previous source package used all 64 temporal At coordinates in a finite
algebraic Gauss demonstration and explicitly warned that actual ports could change
which rows should be eliminated. Here the known radial trace of the four-function
basis is used to keep the material-wall data explicit:

    beta(wall) = (0,0,0,1).

The tangential pullback of a one-form onto the fixed material wall includes At and
A1,A2,A3. Ar is normal to that wall and is **not** assigned a Dirichlet trace by
this construction. The 320 original value coordinates split into:

- 48 interior At coefficients, all with zero wall trace;
- 16 At wall traces and 48 spatial tangential wall traces: 64 input coordinates g;
- 208 remaining spatial/radial coordinates before the relative gauge reduction.

The wall At equations are retained as returned responses. A homogeneous natural
wall relation or a specified wall-potential value is not substituted for the
missing physical matter/exterior relation. A Dirichlet-to-response *map* accepts
these traces as inputs; it is not an adoption of an externally reflecting wall.

Let y denote the 48 interior At variables and r=(x,g) the others. The original
quadratic scalar action has blocks

    L = 1/2 rdot^T M_rr rdot + r^T B_rr rdot + 1/2 r^T K_rr r
        + y^T C r + y^T D rdot + 1/2 y^T A y.

The temporal-coordinate rate columns are absent in this particular Maxwell
quadratic action. Its Gauss equation gives, where this actual finite A is nonsingular,

    y = -A^-1(C r + D rdot).

The reduced M/B/K are obtained by the same quadratic-square elimination as in the
preceding derivation. No positive geometric Gram or pseudoinverse is used. The
omitted wall At rows become derivatives with respect to g rather than equations
that are silently required to vanish.

This is a different **port accounting** of the same stored action matrices. It
is not a correction of a claimed physical boundary law in the earlier package,
which did not claim such a law.

## 2. Only four of the eight exhibited central transformations preserve g

The previous package constructs eight central gauge directions using

    chi_1 = (rho/WALL)^(alpha+1),
    chi_2 = (rho/WALL)^(alpha+2),
    alpha = (sqrt(45)-3)/2,

multiplied by the four n1 harmonics. Both radial functions equal one at the wall.
Consequently the combination chi_1-chi_2 has zero wall trace, while the other
independent combination changes wall data. There are therefore four central
relative-gauge redundancies at fixed g, not eight.

The corresponding original field maps N,Nt obey, to the recorded input arithmetic,

    K N = 0,
    B^T N = 0,
    B N + K Nt = 0,
    M N + B^T Nt = 0.

Here N is the spatial/radial gauge variation and Nt its interior temporal companion
for a time-dependent parameter. The identities imply that, after interior Gauss,
the momentum in a relative-gauge direction vanishes. The transformations with
nonzero wall trace are retained through g and its returned equations.

A representative is chosen by setting four **coordinate** entries of the radial
central field to zero. N is invertible in those four selected entries, so this is
an explicit coordinate slice of the known gauge orbit. It is not a gauge-eigenvalue
threshold, a new physical boundary condition, or deletion of a small physical mode.
An independent slice uses four other radial coefficients, including normal-wall Ar
coefficients, which are not tangential wall data.

The resulting x has 204 coordinates. Its finite kinetic matrix is positive:

| Actual kinetic matrix on the first relative-gauge slice | Incoming lo | Outgoing lo |
|---|---:|---:|
| Minimum eigenvalue | 1.88018450e-5 | 2.68785780e-5 |
| Maximum eigenvalue | 10.92086198 | 12.56369117 |

This establishes only the stated finite Maxwell slice. It is not the complete
nonabelian/matter/geometry gauge quotient. The two slice reconstructions and all
original-equation checks are retained.

## 3. Explicit time and canonical normalization

Let T=thi-tlo=1e-5 in the exported coordinate-time units, tau=(t-tlo)/T.
No physical unit conversion or muon timescale is inferred from T.
Use Ahat_t=T At, the other gauge values unchanged, and multiply the action by T:

    S_hat = T S_original.

If J0 maps these coefficients back to the original fields,

    M_hat = J0^T M J0,
    B_hat = T J0^T B J0,
    K_hat = T^2 J0^T K J0.

This is an exact nonsingular change of coordinates and overall action scale. It
makes the temporal potential and time interval explicit rather than mixing
coordinate-time and proper-time units.

A fixed Cholesky factor R of the actual x kinetic matrix at the initial endpoint
is used for conditioning only:

    X=R x,
    Pi=R^-T T p_original.

The transformation is canonical at the scaled-action level. It is not a mass
normalization of physical particle modes. It is held fixed within each arm,
so no moving-whitening term is deleted. All reconstructions and output units are
recorded. The fields still carry the original five-component/internal/harmonic order.

## 4. Source-dependent force and momentum are consumed

After interior Gauss and the gauge coordinate choice, the action is written in
(x,g) with known matrices Mbar,Bbar,Kbar. Prescribed traces g(tau) give

    f = Kbar_xg g + Bbar_xg g',
    h = Bbar_gx^T g + Mbar_xg g',
    pi = Mbar_xx x' + Bbar_xx^T x + h,

    x' = Mbar_xx^-1(pi - Bbar_xx^T x - h),
    pi' = Bbar_xx x' + Kbar_xx x + f.

These are evaluated at each actual exported node. The known magnetic columns are
included by g=Wg b and g'=Wg' b+Wg b'. Wg' uses the saved Wdot and exact time scale.
The same source is not added again as a separate Gauss load or old F/H column.

The source basis comprises:

- each of the 64 wall traces times 1 and tau: 128 coefficients;
- each of the three existing magnetic wall traces Wg(t) times 1 and tau: 6 coefficients.

The extra six are separately supplied magnetic profile directions, not six extra
physical particles. They need not be independent of all possible unrestricted
wall functions. They retain the inherited Wdot/R4/H-axis data that a generic
fixed affine trace does not encode.

All 408 initial canonical coordinates remain explicit. There are thus 542 input
columns. The evaluated endpoint map has shape 408x542. The input zero in a column
means a unit response basis with other inputs held zero, not a chosen primordial
vacuum or a physical assertion of zero initial environment. No numerical magnetic
field amplitude or switching protocol is selected.

## 5. Four-stage initial-value solve, without a final cap

For v=(x,pi), the scaled equation is

    v' = F(tau) v + f_drive(tau) theta.

Using the four Gauss coefficients a_ij,b_i at the **exported** nodes,

    V_i - sum_j a_ij F_j V_j = v0 + sum_j a_ij f_drive,j theta,
    vf = v0 + sum_i b_i (F_i V_i + f_drive,i theta).

The 1632-by-1632 stage system is solved once with all 542 input columns. There is
no future endpoint equation. Each chronological arm is evaluated separately; no
identity event/reset map glues incoming and outgoing fields.

The finite homogeneous transfer preserves the canonical symplectic form. This is
a numerical/action consistency check, not an assertion that the physically open
muon system has no decay, no radiation, or no environmental dissipation.

## 6. Independently solve the original differential/algebraic equations

A second implementation does not use the Gauss-Schur matrices or a kinetic
inverse. Its stage unknowns are the 204 field coordinates x, their 204 rates v,
and 48 interior At values y. At each of four stages it enforces:

1. the Gauss-Legendre position equation;
2. the original canonical momentum equation with its integrated original Euler force;
3. the 48 original Gauss equations.

This gives an 1824-by-1824 system, solved for all 542 inputs independently. Its
reconstructed stage states and terminal canonical state agree with the reduced
initial-value solution:

| Check | Incoming | Outgoing |
|---|---:|---:|
| Canonical stage system residual | 1.34e-15 | 1.34e-15 |
| Direct original DAE matrix residual | 4.26e-12 | 5.94e-12 |
| Reduced/direct stage difference | 1.18e-11 | 9.12e-12 |
| Reduced/direct final-state difference | 5.55e-12 | 7.56e-12 |
| Reconstructed interior Gauss | 6.83e-13 | 1.14e-12 |
| Reconstructed interior momentum | 1.08e-11 | 9.12e-12 |
| Reconstructed interior Euler | 1.01e-16 | 1.03e-16 |

These checks are in the explicitly scaled/normalized finite coordinates. They
are not the original physical all-226 guard. All comparisons use the same finite
time rule; agreement does not constitute a temporal convergence study.

No action depends on the rate of At in this representation. Its unused rate slot
is omitted/zero in action-map arrays, which does NOT claim d_t At physically vanishes.

## 7. Returned wall force, momentum, and Green relation

At the solved stages, the original action gives the separate wall covectors

    ell_g = L_g,
    p_g = L_(g').

Their contraction against wall test eta is

    W_wall[eta] = sum_i b_i (eta_i^T ell_g,i + eta'_i^T p_g,i).

The reported Euler weak coefficient also subtracts its explicit temporal endpoint:

    W_Euler[eta] = W_wall[eta] - [eta^T p_g]_lo^hi.

Neither expression is relabeled as an already established physical spatial
traction or an instantaneous birth-saddle operator. Together with the terminal
interior canonical data they provide the finite response to be joined through the
actual interface and exterior equations.

On zero-interior-initial-data input columns, symmetry of the original action yields

    W_wall - W_wall^T + Xf^T Pif - Pif^T Xf = 0.

The implemented maps satisfy this identity. Omitting the temporal canonical term
leaves a much larger antisymmetric boundary response:

| Boundary/action check | Incoming | Outgoing |
|---|---:|---:|
| Full discrete boundary/temporal Green identity | 3.35e-15 | 6.04e-15 |
| Without terminal symplectic contribution | 1.88442e-5 | 1.89702e-5 |
| Homogeneous symplectic-transfer defect | 3.34e-16 | 6.67e-16 |

The returned At wall covectors are nonzero on the known magnetic trace columns.
Their zero cannot be imposed in addition to fixed trace data without changing
the boundary problem. This is the concrete reason to preserve these 16 equations
for coupling to the unresolved matter/exterior response.

## 8. Independent gauge-coordinate comparison and a preserved limitation

The initial-value and wall maps were computed again in the alternative explicit
relative-gauge slice, on the same original matrices, time nodes, and input traces.
For zero interior initial state, their returned wall response agrees to:

    incoming: <=4.22e-13,
    outgoing: <=7.31e-13,

including the Euler and temporal-endpoint split. The comparison does not choose a
different physical state. The exact continuum/finite-action gauge identities
predict equality; the stored matrices satisfy those identities only up to their
previously recorded arithmetic precision.

A stricter check of reconstructed fields modulo the explicit gauge transform is
less accurate: the worst combined field/rate diagnostic is about 7.30e-10 incoming
and 6.33e-10 outgoing in the listed original/time-rescaled coordinates. These exceed
2e-10 and are preserved as **not passing** that additional reconstruction test.
No projection of the stored action matrices onto exact gauge identities was used
to force agreement, and no cause is claimed certified for the residual discrepancy.
The wall-functional agreement must not be promoted into an all-field error bound.

## 9. What the solved maps do and do not supply

This calculation supplies an actual finite causal/initial-value map from retained
interior initial data and arbitrary wall traces to propagated fields, canonical
endpoint data and weak wall response. In this fixed linear problem the response
map is also its derivative with respect to those input coefficients.

It does NOT supply the complete parameter derivative obtained by moving the
physical background, modes, Gauss domain, interface, source projection and state.
It does not supply a quantum daughter propagator or magnetic Pauli contraction.
The original odd n1 Maxwell response is only one homogeneous-reference sector.
The integrated magnetic third variation between n0 and n1 is preserved in the
preceding package and was not replaced or re-refined here.

To turn this into the physical outgoing return, the actual equations for g must
now be imposed jointly with the returned wall/temporal data, including the matter,
source, interface, native, and inherited-reference pieces. They remain explicit
unknown inputs, not an instruction to set all g or all reactions to zero. After
that connection, the full physical preparation, nonlocal response and derivative
need their own convergence and original-equation tests.

The two arms are not joined here. No coupled physical background correction,
fresh collider Maxwell/all226 admission, normalized muon spin/pole, a_mu, g_mu,
physical uncertainty, Git commit, or Windows-worktree change was produced.

## Reproduction and source provenance

Inputs are exact array extracts of M,B,K,W,Wdot from the preceding integrated
package, plus the analytically constructed central-gauge maps checked against the
same exported radial basis. `inputs/metadata.json` identifies each complete
parent coefficient/sample file hash. `prepare_inputs.py` verifies both prior
manifests before extracting; `run_response.py` works on the self-contained extracts.
The previous Maxwell producer is not called during response evaluation.

Two independent processes run `run_response.py` and their saved results are
compared byte-for-byte. Eight primary finite-equation check categories are tested
on each arm, with the stricter field-gauge reconstruction recorded separately as
not passing its stated 2e-10 threshold. See VERIFICATION.json for exact values.

Scientific source basis: the uploaded history ZIP, the attached integrated-source
DERIVATION/VERIFICATION, and their included original action snapshots. The port
split, causal solve and checks above are new calculations on those matrices; no
outside theory, fitted parameter, or new electromagnetic interaction was inserted.
