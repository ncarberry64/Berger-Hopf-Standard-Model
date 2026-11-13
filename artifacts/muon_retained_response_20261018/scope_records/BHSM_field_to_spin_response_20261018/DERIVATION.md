# Open field response connected to finite-time lepton spin response

Norman P. Carberry / BHSM continuation — 18 October 2026

## Result and limits

This calculation joins two previously evaluated objects: the retained Maxwell/Higgs
open-wall response, and the direct finite-time intrinsic lepton calculation. The
new result is a numerical map from 166 explicit classical field/initial-data
variation coefficients to the lepton propagator and spin-readout derivatives on
each of the two exported, provisional histories.

The 166 coefficients are 32 Higgs canonical initial variations plus 134 prescribed
wall-history coefficients. The latter comprise the existing 64 material wall fields
times (1,tau) and six separately retained magnetic-profile columns. They are response
coordinates, not 166 physical particles or a chosen experiment. Their initial
values do not select the quantum density of the lepton component.

The full known classical endpoint/wall equations use 574 inputs: Maxwell initial408,
Higgs initial32, and wall/probe134. The new spin map uses the final166 of that vector.
At *prescribed wall fields and fixed geometry*, the retained intrinsic lepton
Hamiltonian sees the tangential gauge traces and intrinsic Higgs, not independent
zero-wall-trace Maxwell interior coordinates. That conditional zero does NOT remove
the influence of Maxwell initial data once the physical wall-feedback equation is
solved. No normal-field contribution in another domain is assumed absent.

No physical wall law, collider preparation-to-mode application, quantum reference,
formation/decay history, normal geometry response, native memory, Pauli normalization,
or physical a_mu/g_mu is completed here. The two arms remain separate. No physical
2e-10 outgoing-derivative admission or original all226 check is claimed. No Git or
Windows-worktree change is made. The input revision is 70e82fd4dbe5f53ff27ae17f6aaac7a4727c1fde;
this is provenance, not a new remote-head check.

## 1. Reused source data and normalization

The following supplied packages were unpacked without altering their original ZIPs:

- BHSM_finite_time_spin_response_20261017: all32 manifest entries verified.
- BHSM_higgs_wall_coupled_response_20261017: all47 entries verified.
- BHSM_port_preserving_retarded_response_20261017: all30 entries verified.

29 selected input/dependency files are copied unchanged and individually hashed in
inputs/PROVENANCE.json. These checks do not rehash the original, larger Windows
repository archives or certify a physical background. Source-derived representations
remain source-derived reimplementations rather than a full repository execution.

The lepton operator, gauge representation, family-Y coefficients, measured scalar
ancestry, time samples and adopted collider choices are unchanged. The retained
six middle-family entries are indices(2,3,8,9,14,15) of the full18 fiber. They contain
neutral-left and charged-left/right fields. This is not the physical two-spin pole.

Harmonics are normalized conjugate Wigner functions. Four real n1 functions
Y_h=(2x0,2x1,2x2,2x3) are mapped by exact Clebsch-Gordan multiplication to the
existing fourteen harmonics through n=2. The square matrices are Hermitian. A
first insertion acting on initial n<=1 reaches n<=2; n<=2 initial data would also
need n=3. The numerical propagator derivative retains 84 output components from
30 initial components. The spin operator derivative is given on the initial30.

A direct comparison with independently evaluated Haar integrals gives at most
7.78e-16 difference. An enlarged n<=3 multiplication reproduces all n<=1 input
columns exactly and confirms zero n3 output for those inputs. It also confirms
nonzero n3 output for some n2 inputs, preserving the limitation.

## 2. Field-to-Hamiltonian correspondence actually evaluated

For the fixed supplied homogeneous geometry, the original material-clock Hamiltonian is

    h_t = N[-i alpha_i(E_i+Omega_i)/R4 + (3/2)gamma5/R4 + M_Y(H)]
          - i Omega_t.

A tangential gauge/Higgs variation therefore has the local coefficient expression

    delta h_t = -i G_c delta A_t^c
                -i (N/R4) alpha_i G_c delta A_i^c
                + N M_Y(delta H).

Each n1 coefficient multiplies its exact angular multiplication matrix. No second
lapse is attached to At; no extra radial advection, magnetic charge, spin-density
term, new Yukawa, or unit normalization is inserted. The material temporal trace
is already pulled back. The linear M_Y map uses the retained middle-family Yukawa.

The stored wall coordinates have Athat=T At, T=1e-5 in the exported action-time
units. They are converted back by 1/T before the lepton insertion. The scalar
response's fixed conditioning matrix is also undone before applying M_Y. This is
a classical coordinate conversion, not physical spinor/pole normalization.

80 fixed Hermitian angular/fiber matrices represent the64 tangential gauge and16
real Higgs coefficients. Their actual time-dependent coefficients are evaluated
from the saved response and the supplied N,R4. The direct point-Hamiltonian
calculation at independent angular points checks the assembled matrix. In a test
containing a unit-scaled At coordinate, the insertion's entries reach order1e4;
the absolute discrepancy is7.28e-12 and relative discrepancy5.05e-16. This is not
a physical uncertainty or an assertion that arbitrary sources are of that size.

The action here has fixed geometry. Delta N, delta R4, a nonuniform spin/coframe,
mode/measurement motion and native terms are additional total-response contributions,
not silently supplied by the homogeneous formula.

## 3. Recover the actual saved scalar response without another solve

Let Z_j be the four stored scalar canonical stages and Z0 the32-by166 initial-data
map. The stage rates are reconstructed from the stored M/B/K and the original G,Gdot
wall maps; no new Higgs Hessian or stage linear system is evaluated. The continuous
numerical polynomial is

    Z(tau)=Z0 + sum_j integral_0^tau l_j(v) dv * F_j,

where l_j are the four-node Lagrange basis and F_j the reconstructed canonical
stage rates. It reproduces every saved stage and endpoint within1.34e-15.

Its first16 rows, after undoing scalar conditioning, give the actual saved delta H
response. Every arbitrary initial scalar coordinate remains an input. The wall
trace is the prescribed G(tau) map; its magnetic part uses a degree-five interpolation
of the six existing W samples. The N and R4 samples use the same declared polynomial
representation. These interpolants are numerical definitions, not solved physical
field histories or a temporal-tail enclosure.

A response with all initial coefficients zero in one source-basis column is not
a choice of a primordial vacuum. No retarded scalar state is selected merely by
returning the fundamental response to arbitrary initial data.

## 4. Actual field-history to spin integration

For each of the166 source coordinates c, the new matrix V_c(t) is evaluated by the
field-to-Hamiltonian map. On the unchanged unperturbed lepton evolution U(t),

    J_c = integral U(t)^dagger V_c(t) U(t) dt,
    delta_c U(tf) = -i U(tf) J_c,
    delta_c O_I(tf) = i [J_c,O_I(tf)].

For storage, J keeps84 rows and30 initial columns. The selected integrated component
spin observables preserve the initial n<=1 subspace under this homogeneous base,
so their30x30 derivatives are reconstructed exactly from that projected J. This
would not be true for an arbitrary angular readout that leaves the retained initial
subspace; such a readout requires its full reached space.

The integration is carried out on the evolving supplied operator, not a stationary
energy eigenstate. It still is a unitary one-particle field component, not the
physical dissipative muon/daughter channel. No lifetime, g(t), two-spin density,
reconnection law or probability of encapsulation is fitted.

The resulting J and spin derivatives separate prescribed gauge-field response and
Higgs response. Generic wall-to-Higgs and arbitrary scalar-initial effects are
nonzero. Freezing the scalar response at its final value changes the integrated
source by9.61e-9 incoming and4.81e-9 outgoing in the recorded coordinate norms. This
is a deliberately changed-history comparison, not an error assigned to old code or
a physical magnetic-moment correction.

## 5. The direct magnetic term is already inside the wall map

The six existing magnetic-profile directions are columns160..165 of the166 input
map. The gauge part of J in these columns reproduces the preceding direct-field J
within8.48e-22; its projected spin response agrees at the same scale.

Thus one must NOT compute

    old direct response + complete new wall-coordinate response

for these same magnetic columns. The first term is already in the second. Correct
accounting is the direct prescribed field ONCE plus those separately established
induced changes not included in its field map.

The explicit duplicate-addition diagnostic has size4.3594e-6 incoming and2.7458e-6
outgoing in J per canonical electric charge, simply the prior direct response
counted twice. These are not values of g or an experimental discrepancy.

## 6. The neutral Higgs coordinate contact is not optional

The generic source map differentiates independent ORIGINAL gauge coordinates. Its
fixed-axis magnetic-profile columns are not automatically the full derivative
of a field-dependent source A -> A+b s(H). In the Higgs action alone,

    S_H,HA[v,a s(H)] + S_H,A[a Ds(H)[v]]=0.

The already evaluated two terms are imported and checked in the SAME time/scalar
conditioning. The scalar source before the contact is4.76e-12 incoming and2.38e-12
outgoing in scaled units; after the contact the discrepancy is at most3.24e-27.
There is no Higgs gauge-rate source on these purely spatial neutral directions.

The tiny fixed-axis Higgs response on those columns therefore must not be promoted
to a physical direct neutral Higgs magnetic contribution. Its complete neutral
source parametrization has the contact above. Conversely, do not delete the generic
Cartesian-wall Higgs response, which is the actual map for those independent inputs.
Maxwell, geometry, matter and native sectors need their own corresponding complete
source pullbacks before any full physical cancellation is inferred. No direct
Higgs trapping force has been introduced.

## 7. The field map passes a gauge-covariance test

Use the source gauge convention

    delta A=D alpha, delta H=-alpha_H H, psi -> exp(-alpha_L) psi.

The lepton Hamiltonian must satisfy

    delta h=[h,alpha_L]-i partial_t alpha_L.

All sixteen n1 internal gauge directions are checked at three time samples per
arm, using the ORIGINAL local gauge/Higgs variations rather than constructing the
right side by definition. The maximum absolute discrepancy is1.12e-16. Omitting
the Higgs gauge variation gives8.11e-5 incoming or5.11e-5 outgoing in these tests.

This checks representation consistency and the temporal/source sign. It does not
say an arbitrary gauge variation of an off-shell background solves its uncompleted
physical linearized field equations. It does not repair the stricter Maxwell
field/gauge reconstruction failure in the earlier package.

## 8. Combine with the actual open classical boundary equations

Let eta=(u_M408,u_H32,theta134). Reusing the saved maps gives

    classical final = F_classical eta,
    known wall weak variation = W_classical eta,
    spin operator first = sum_(c=0..165) eta_(408+c) K_c.

F_classical is440x574; W_classical is134x574. The separate temporal wall term is
also retained. Their saved Green balance is3.35e-15 incoming,6.03e-15 outgoing;
an independent sum of the sector applications differs by at most2.78e-17.

This is an evaluated JOINT OPEN input/readout relation. It does not impose
W_classical eta=0 or select the unknown wall fields. The physical equation still
has the geometry/interface, true current, exterior/native/reference, preparation
and transition terms. In a compatible linearization they must be added once, with
original residuals and endpoint conventions. The quantum feedback of the lepton
state on those fields is also not obtained simply by driving its Hamiltonian with
this one-way map.

If an actually defined remaining wall relation makes a reduced matrix A_w
invertible, theta is obtained from its true right side via A_w theta=b_w. For a
specified physical scalar readout c^T theta, one adjoint A_w^T lambda=c supplies
lambda^T b_w. This algebra can avoid a whole explicit inverse, but neither A_w nor
b_w is selected in this package. A physical boundary condition or quantum reference
cannot be manufactured by replacing them with identity or zero.

## 9. Numerical verification and what the numbers mean

Thirteen scoped categories pass on each arm. Two independent processes execute the
new calculations and produce eleven byte-identical data/result files. Redundant
J_total, propagator-first and separate-spin arrays are omitted from the compact
NPZ export; they are recovered exactly from J_gauge+J_Higgs, U and the saved spin
operators. Both runs were subjected to the same deterministic compact export.

The independent finite-field reruns integrate H0+epsilon*V along the calculated
LINEARIZED field response; they do NOT resolve the nonlinear coupled background
at finite epsilon. The mixed wall/scalar input comparison gives propagator errors
2.61e-12,1.63e-13,1.03e-14 at steps.02,.01,.005 (fourth-order difference). The
spin comparison at the last step differs by3.71e-15. On the smaller magnetic
profile direction, finer steps increase roundoff; all errors/steps are retained.

The new insertion integral's12-vs16-node comparison differs by at most1.12e-16.
This controls integration of the chosen finite polynomial path, not the physical
classical collocation error, radial truncation, wavepacket tails, or native quantum
uncertainty. No original source coefficient was precision-refined.

Optional eigenvalue ranges are supplied for the magnetic-profile spin derivative
operators in the initial30 space. They bound that finite Hermitian expectation
for a positive unit-trace density IN THAT SPACE. They are not uncertainty intervals
on physical g, a_mu, a Fock sea, or the completed observable. No density is selected.

The1e-5 coordinate interval is unchanged and is not identified with seconds or
muon decay age. Both arms are separate; no before/after identity reset is imposed.

## 10. Remaining physical calculation

The new evaluated connection fills the one-way, fixed-geometry wall/Higgs-to-lepton
spin application on the given finite histories. It leaves the physical wall/source
closure, actual collider/formation mode construction, source-dependent geometry,
inherited quantum state and full quantum daughter memory unresolved. All relevant
energy, charge, Cauchy, spin and detector normalization must still be established.

A genuinely evolving magnetic moment would require this complete response and its
physical state/measurement projection. A nonzero finite input map, a time-varying
background, or tiny local agreement does not establish such variation.

No physical2e-10 outgoing admission, coupled background correction, fresh collider
Maxwell/all226 pass, pole/residue, final a_mu/g_mu or total uncertainty is claimed.
No repository update was attempted. The next useful operation is the compatible
physical wall/source/reference closure, not another static spectrum or another
precision sweep of these already evaluated coefficient maps.

## Reproduction

With the recorded Python/numpy/scipy/sympy versions, run

    python run_connection.py --output replay_new

The package is self-contained. It requests no new user export, Internet download,
or Windows repository mutation. See field_spin_connection.apply_open_result for
applying the evaluated joint maps to explicit574-coordinate variations. Its optional
finite initial density does not amount to physical muon-state admission.

## Source basis

All scientific source inputs are the three supplied packages listed in section1,
including their derivations, coefficient arrays, response maps and preserved
source-derived functions. The Hamiltonian and field formulas retain their pinned
BHSM provenance. This continuation uses no new outside physical parameters and
claims no newly derived universal field theory from the combination.
