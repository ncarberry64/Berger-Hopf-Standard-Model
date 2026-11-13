# Normal-graph Higgs and membrane response on the retained histories

Norman P. Carberry / BHSM continuation — 17 October 2026

## Result and scope

This calculation adds an explicit **regular boundary-deformation input and its
returned scalar/interface action response** to the previous dynamic Higgs
calculation. Four spatially nonuniform n=1 graph coordinates are retained as
inputs, with their coordinate-time rates. They are not fixed to a guessed
formation mode, and their own complete equations are not claimed solved.

Executed on all twelve exported incoming/outgoing samples:

* Exact induced-metric pullback of the existing intrinsic Higgs action for a
  fiber-invariant normal graph, including its time/space mixed components.
* The selected M8 interface-volume action on that graph, per its existing symbolic
  coefficient gamma. The fiber volume is retained; no numerical gamma is selected.
* The Higgs, gauge-trace and normal-graph quadratic action matrices and their
  mixed terms. The previous 80-variable Higgs/gauge blocks are recovered, then
  reused unchanged in the time evolution.
* Eight additional graph-drive response columns on each arm, their Higgs final
  states, gauge-wall response, normal response and temporal conormals. Every
  previously saved Higgs response column is retained byte for byte.
* Independent original scalar equations, complex-doublet action and high-precision
  local derivative checks, angular quadrature checks and normal/gauge identities.

This is not a completed Maxwell-shape/Einstein/eta/GHY/Hayward response, physical
wall closure, topology-changing rupture, collider preparation, daughter quantum
propagator or magnetic moment. In particular it does NOT replace the missing
Maxwell normal-graph response with zero in a claimed complete system. The membrane
coefficient remains symbolic, and even its possible scale-dependent variation
would need the existing scale equation before a total derivative could be claimed.

Repository source read anchor: PR #465 at
`70e82fd4dbe5f53ff27ae17f6aaac7a4727c1fde`. The branch head was verified during this
turn. The action formulas below are a source-derived reimplementation and a stated
geometric extension of its normal-graph expression, not execution of a complete
repository checkout. No GitHub/Windows file was modified.

## 1. Same normal coordinate; nonuniform regular graph

The source uses the material wall coordinate

    chi_w(t) = pi/4 + s0(t)/C_star(t),
    chi_w_dot = (s0_dot - log(C_star)_dot s0)/C_star.

Extend this existing graph coordinate over the quotient S3 by four normalized
n=1 harmonics Y_a=(2x0,2x1,2x2,2x3):

    xi(t,Omega) = sum_a xi_a(t) Y_a(Omega),
    chi = pi/4 + (s0+xi)/C_star,
    chi_dot = [s0_dot+xi_dot-log(C_star)_dot(s0+xi)]/C_star,
    d_S3 chi = d_S3 xi/C_star.                              (1)

C_star and its logarithmic rate are the actual source formulas evaluated from
q and qdot. The ambient q/qdot/m geometry is held at the supplied time-dependent
background. Equation (1) is a regular graph-coordinate probe, not an identification
of a physical eigenmode or a new independent normal force. The graph does not
pass through a pinch-off or change topology in this calculation.

The source-defined radial profiles determine N,C,A,B,beta at the displaced chi,
not at a frozen wall. Put

    L_F=sqrt(A^2+B^2),  R4=A B/L_F,  lambda=A^2/(A^2+B^2).

On the fiber-invariant quotient the induced metric is

    h = diag(N^2,-R4^2,-R4^2,-R4^2) - C^2 v v^T,
    v = (chi_dot+beta, d_S3 chi).                           (2)

This is the metric expression already stated in the original normal-graph
backend. The new calculation evaluates it on the exported nonzero normal
coordinate, with its angular variation, instead of restricting its coefficient
formula to the older parity center. In its regular timelike domain,

    Q = 1-C^2 [(chi_dot+beta)^2/N^2-|d_S3 chi|^2/R4^2],
    sqrt(-det h) = N R4^3 sqrt(Q),
    h^-1 = h0^-1 + (C^2/Q)(h0^-1 v)(h0^-1 v)^T.             (3)

An independent evaluator forms h, its determinant and its inverse directly; it
does not call the rank-one formulas used by the differentiated implementation.
Neither beta nor the inherited wall speed is set to zero. Dropping the off-diagonal
entries of h changes the evaluated scalar graph Hessian (section 7).

## 2. Original Higgs action on that graph

Use the same cap-normalized intrinsic action and calibration as the previous
package:

    S_H = c int dt dHaar [sqrt(-h) h^(mu nu) (D_mu H)^T D_nu H
                         -sqrt(-h) lambda_H (H^T H-nu2)^2],
    c=1/(2 pi^2), lambda_H=0.1290946235307726, nu2=4.         (4)

The retained lambda_H is calibrated from G_F and Higgs mass. This is not a new
fit or an uncalibrated first-principles input. All four real Higgs components,
the actual Hdot and the gauge traces are used.

The independent gauge variables are **material intrinsic trace coordinates**.
Their temporal component remains A_t,ref, without adding Eulerian radial
advection a second time. The mechanical spatial connection lambda(chi)-1 moves
once. No ambient normal extension of the intrinsic Higgs field is invented.
A different representation holding Eulerian bulk fields fixed would require its
own trace pullback; the present fixed-material-trace partial must not be substituted
for that total physical derivative.

The physical real field is (Re H1,Re H2,Im H1,Im H2). Coordinates are

    values: (Higgs16, gauge wall64, normal graph4) = 84,
    rates:  Higgs16 and graph4.

The original action has no direct gauge-rate dependence in this intrinsic sector.
The graph DOES have a rate, and its scalar-sector canonical momentum is retained.
The full 104-variable local Hessian yields

    L2 = 1/2 qdot^T M qdot + q^T B qdot + 1/2 q^T K q.

At xi=0 the upper 80x80 blocks reproduce the previously evaluated action within
4.45e-16 in the conditioned coordinates. For propagation those lower blocks are
replaced by the unchanged saved arrays, not recalculated at greater precision.

Only the n1 finite tangent/response sector is constructed. A localized physical
packet and a finite-amplitude nonlinear graph require larger spaces and their
own convergence. Zero n1 first covectors on a homogeneous background follow from
angular mean zero, not from stationarity of the full n0 background.

## 3. Area is M8 volume, not an unweighted M4 membrane

The existing selected interface term is

    S_Sigma/gamma = -int N A^3 B^3 sqrt(1-U^2) dt

on a homogeneous wall. For the fiber-invariant graph its geometrical lift is

    S_Sigma/gamma = -int dt dHaar L_F^3 sqrt(-det h).         (5)

Since R4^3 L_F^3=A^3 B^3, (5) recovers that source expression exactly when the
angular gradient vanishes. It is the same area action, not another action added
at a lower stratum. Its contribution is kept separate per gamma. No alpha_FSC,
length, physical tension or value of gamma is fitted or chosen. This is also not
the gravitational GHY/Hayward completion; that distinct action is not evaluated
on the new nonuniform graphs here.

Let f(s,r) be the homogeneous area density, with r the added normal-coordinate
rate. For one normalized n1 harmonic, the normal quadratic coefficients satisfy

    M_area=f_rr,
    B_area=f_sr,
    K_area=f_ss+3 G_area,
    G_area=-N A^3 B^3 C^2/(R4^2 sqrt(Q) C_star^2).            (6)

The factor 3 is the gradient eigenvalue of the normalized n1 functions used in
this stated round-quotient representation. Independent high-precision derivatives
of the original homogeneous law plus (6) agree with the graph Hessian within
8.53e-14. At the first exported sample of each arm:

| Per-gamma normal coefficient | Incoming | Outgoing |
|---|---:|---:|
| M_area | 5.796691435861827 | 9.292288449969814 |
| B_area | -29.952225237145743 | -32.11370687839938 |
| K_area | 198.51278619531612 | 139.5482012718847 |
| G_area | -7.673656758503802 | -4.879933797618941 |

These signs are the original ACTION convention, not all positive mechanical
stiffnesses. Stability needs the Euler operator, including time derivatives,
all other action sectors and constraints. These values are not frequencies,
particle masses, measured surface tensions, or magnetic shifts.

## 4. Propagated graph source and returned normal action

Retain the previous time scaling tau=(t-tlo)/T, T=1e-5, S_hat=T S, and the fixed
initial scalar kinetic conditioning. No physical time or energy scale is inferred.
The original 134 gauge/magnetic wall-drive functions are unchanged. The graph
adds four value profiles times (1,tau): eight extra input coefficients. Their
physical coordinate derivatives are retained, including (1).

With h the conditioned scalar16 and e=(gauge wall64,graph4), the canonical system
uses all mixed blocks:

    f=K_he e+B_he e',
    k=B_eh^T e+M_he e',
    p_H=M_hh h'+B_hh^T h+k,
    h'=M_hh^-1(p_H-B_hh^T h-k),
    p_H'=B_hh h'+K_hh h+f.                                  (7)

The new rate-dependent momentum k is not omitted. The existing homogeneous scalar
stage matrix is reused, and only eight new right-hand sides are solved. The
previous 166 initial/gauge/magnetic columns, including every saved stage and
endpoint, are copied unchanged. No Maxwell matrix or Maxwell evolution is rerun.

The evaluated maps have sizes

    Higgs final: 32 x 174,
    Higgs gauge/normal weak wall response: 142 x 174,
    area weak response per gamma: 142 x 174.

Input order is Higgs initial32, old drive134, new graph drive8. Output weak-test
order is old wall tests134, new normal graph tests8. Initial data remain arbitrary
inputs. A zero column entry is a response-basis convention, not a physical vacuum.
No final endpoint equation is imposed. Incoming and outgoing arms remain separate.

At all stages compute the original gradient L_q and momentum L_qdot. Return the
normal momentum as well as the force and the explicit endpoint contribution:

    W[eta] = sum_i b_i [eta_i^T L_e,i+eta_i'^T p_e,i],
    W_Euler = W-[eta^T p_e]_lo^hi.                          (8)

The Higgs weak map obeys its discrete action/endpoint identity

    W-W^T+H_f^T P_f-P_f^T H_f=0

on zero-initial source columns. The standalone area weak map is symmetric; its
normal endpoint momentum is nevertheless nonzero and is returned separately.
The two action pieces can enter W_H+gamma W_area once gamma and any variations
required by its original scale law are provided; gamma=0 is not implicitly chosen.

## 5. What couples, and what cancels

The first-sample scalar/normal value Hessian maxima are 0.19075156492299003
incoming and 0.12209929930550391 outgoing. The propagated normal-to-gauge-wall
response maxima in the stated short-time coordinates are 1.3138067062e-8 and
2.3707825053e-8. They are nonzero finite source maps, not a magnetic anomaly or
an error bound. Different coordinate/drive normalization would change these
maxima, and no physical graph amplitude is selected.

The Higgs-selected neutral line still annihilates H pointwise. Accordingly the
**direct** shape/neutral-gauge mixed contribution K_shape,gauge W_mag vanishes
within 1.74e-18 across the samples. The arbitrary gauge response must not be
interpreted as a new neutral Higgs trapping force. The field-dependent magnetic
inclusion and its full second-map contacts are still required in a total physical
magnetic derivative.

A mixed gauge/shape identity was also evaluated on all twelve samples, with
16 gauge parameters and four graph tests. The gauge direction's mechanical
connection changes when lambda(chi) moves. Its original action-residual contact
is retained; the complete identity is within 9.01e-18. At these aligned retained
states that extra contact is itself tiny. This is not a demonstrated large error
in earlier code and not a complete physical BRST/native gauge certificate.

## 6. Independent original-equation and high-precision checks

A separately assembled scalar position/momentum/Euler collocation system does
not use the reduced first-order evolution. It agrees with the eight new source
columns within 5.30e-23 in the recorded scaled coordinates. The maps themselves
are small; this is a numerical consistency check, not such a small physical
uncertainty. Original scalar momentum checks are at most2.23e-16.

For the local action, an independent 65-decimal mpmath implementation uses complex
doublets and explicit metric determinant/inverse operations. Its derivatives are
compared to the automatic-differentiation Hessians. Across the tested value,
rate and mixed field/graph directions at the first sample of each arm, discrepancies
are at most9.05e-14. These are numerical high-precision checks, not interval
arithmetic enclosures of the continuum or of physical input error.

Finite-step five-point second differences are retained at steps .002,.001,.0005.
They show fourth-order truncation reduction. The last pure-normal-value area
comparison is still about9.34e-8 incoming (8.18e-8 outgoing), ABOVE2e-10. It is not
called a passing physical derivative. Agreement with the independent high-
precision derivative identifies the scoped truncation; no further coefficient
precision refinement or altered physical equation was used to conceal it.

Two specifically incomplete comparison formulas show why the geometric pullback
matters:

| Deliberate omission, max local Hessian change | Incoming | Outgoing |
|---|---:|---:|
| Keep only diagonal induced metric density | 0.0034795682 | 0.0062785482 |
| Freeze fiber volume L_F^3 in the area derivative | 3.9843183063 | 3.6193968699 |

Those variants are omission controls on the same actual backgrounds, not claimed
implementations of the physical theory and not errors assigned to historical code.

## 7. Remaining physical application

This adds the intrinsic-field and selected area contribution to the **normal
port**. It does not determine that port's physical history. Its complete equation
also needs the Maxwell shape response, gravitational/eta and appropriate moving
GHY/Hayward terms, the actual matter/current and native/reference contributions,
and the compatible before/after transition and exterior relation. Old homogeneous
geometry coefficients cannot be copied into the n1 graph merely because both use
a normal-coordinate label. Those extra sectors are absent from this partial map,
not set to zero in a purported complete solution.

The previously combined Maxwell-Higgs response is preserved. This package must be
integrated as an additional source/normal port block; its lower Higgs block must
not be added again. Geometry q/qdot/m response and physical scalar/mode/source
normalization still move in a total physical derivative. A regular linear graph
is not a rupture or topology-changing daughter-envelope simulation.

The prior Maxwell field-gauge reconstruction discrepancy remains unresolved.
All new calculations share the same finite angular space and the exported four-
stage time rule. There is no fresh radial/time/domain convergence enclosure,
physical wall law, inherited-state selection, collider Maxwell/all226 pass,
coupled background correction, quantum pole/residue, a_mu, g_mu or total uncertainty.
The physical2e-10 guard is unchanged. No GitHub or Windows write was made.

## Source readings and provenance

Read through the connected GitHub tool at the pinned revision:

1. `src/bhsm/interface/muon_intrinsic_m4_normal_pullback.py`, blob
   `4a2f91693b6b14d63e9fc85a88ba2a919d616f67`: explicit induced-graph metric and
   the q-dependent normal coordinate/time derivative.
2. `src/bhsm/interface/muon_moving_geometric_action.py`, blob
   `00e1123d4ca03b6eec701056fdb466c8474ba1c6`: existing area action per gamma and
   distinct moving gravitational completion.
3. `theory/muon_moving_interface_action_20261009.md`: prior evaluated homogeneous
   geometric/interface sectors, distinct fiber measure and fixed-domain scope.

Numerical and reusable code inputs are extracted from the attached dynamic-Higgs
package and verified against its manifest. Its calibrated inputs, original real
representation and scalar conditioning are unchanged. The full original history
manifest is also verified. The package is self-contained for the new calculations;
production integration still needs comparison with current repository owner
functions. No network is needed to rerun it.
