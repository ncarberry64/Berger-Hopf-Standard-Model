# Source, joint variation and the current M5/M4 attachment

Continuation from `d8e5c2e15fba8f591a14a7de9e36b3ff0f98b567` on
`codex/muon-parent-maxwell-density-review`. The scientific reference remains
`524ed90689bd5923c249bba2e699abf627e703cd`. The checkout began clean;
the live primary checkout and all historical results were preserved.

The new result corrects the role of the earlier target Theta_p. The actual
photon source produces an insertion image; it does not prescribe an
independent microscopic wall field for that image. The known bulk and wall
Euler variations and normal Green density are derived below, with actual
node3 contractions saved. The intrinsic wall response stays a coupled
unknown. A complete native joint variation cannot yet be assembled from
the displayed current action equations. This is not a numerical solution
or a new physical boundary condition to choose.

## 1. Identify the source before selecting a domain lift

The defining physical source is the connection coordinate **b_A**, with
beta=T_b b and A_Q=sqrt(2) beta. In the adopted common section

\[
\delta_{b_A}\Omega=T_bY_A(-iQ),\qquad Q=T_3+Y,\qquad
\Xi_A=\delta_{b_A}D.
\]

The current source-frame, carrier, charge-conjugation and Clifford signs
are unchanged. No action-index2/3 or n2 contact fraction enters the vertex.
The known tangential insertion and its n1/n3 connected outputs are reused.
The source is independent of a Hopf-shape variation.

The original `physical_source_vertex_contract` in v15.99 differentiates
P_cycle with respect to connection, Higgs and geometry coordinates. It
does not prescribe a fermion forcing equal to the saved compact p. In a
fixed local form domain the source derivative is

\[
q_A(v,u)=\langle\Xi_Av,Du\rangle+\langle Dv,\Xi_Au\rangle,
\]

before adding pairing/domain pullback terms where required. The affine
local contact is Xi_Z^dagger Xi_A+Xi_A^dagger Xi_Z. The full stratified
source jet, including interface and completion terms, remains unevaluated.

The actual compact field is

\[
\phi_k=\widehat\chi(\rho)e_k,\qquad
p_{Ak}=\Xi_A^{(5)}\phi_k
 ={T_b\widehat\chi\over r}\Xi_A^{\rm unit}e_k.
\]

`muon_parent_source_contact.computational_profiles` explicitly makes the
hat a computational spinor test and L a computational trace lifting. The
parent source/contact report makes the same distinction. Later,
`muon_wall_source_pairing.source_reached_pairing` constructs p on those
probes. It is an insertion image, not a physical LSZ state, a new fermion
species, or an unknown field named iota_p.

The accepted parent-bulk tail subsequently uses this image as a
**diagnostic Riesz load**, f=M p, with a supplied source-reached node2
trace. `endpoint_element` and `terminal_core_element` implement exactly
this load. This model response and its stationary return remain valid at
their stated numerical-component scope; they do not change the source
image into an action-prescribed physical fermion forcing.

The notation iota_p therefore has three distinct possible meanings:

| Use | What is required |
|---|---|
| RHS/probe image p | A vector in H, or a continuous functional in V'; it need not lie in Dom(D) |
| Galerkin trial column | A computational conforming lift in the owned form domain, or a justified nonconforming formulation |
| Full insertion image | Pi4 Xi_strat[a] phi, derived from the same source-dependent joint operator, not an independently selected Theta_p |

For a diagnostic parent load,
`ell_p(v5)=<v5,p5>_5` satisfies `|ell_p(v5)|<=||v5||_5 ||p5||_5`.
Neither Dp nor a prescribed independent-H4 component is needed to define
that functional. The saved native heat-contact route likewise does not
require every source image to be a D-domain vector: it requires the
appropriate full form jet and full heat action on the reached image.

Thus the earlier checkpoint's request for Theta_p as a separate physical
datum was too strong. Its nonfactorization and bounded-graph results are
preserved: they rule out particular substitutions, not a forcing vector.

## 2. First variation before localized-mode restriction

The adopted v14.45 collar action, before Psi5=W_eta psi4, is

\[
S_5^F=\sum_{\epsilon=\pm}\int d\mu_4 ds\,J\,
\bar\Psi_\epsilon\big[i\gamma^\mu\nabla_\mu^{total}
 +i\epsilon\Gamma_\perp(\partial_s+\tfrac12\partial_s\log J+m_\eta)\big]
 \Psi_\epsilon+S_H.
\]

Varying bar-Psi gives D5 Psi in the bulk. Integrating the variation of
Psi by parts gives the formal left Euler operator and the outward
normal principal boundary term `J bar(Psi) i epsilon Gamma_perp deltaPsi`.
The eta coefficient, spin/common-A lower-order terms and Yukawa terms
contribute to the Euler operator; they do not change this principal
Green symbol. No normal action is inferred from a scalar cancellation.

Write g_+ and g_- for the arguments used in the retained seam bridge

\[
S_H=-\int d\mu_4[\bar g_+YH g_-+\bar g_-H^\dagger Y^\dagger g_+].
\]

Its left variations are `-YH g_-` and `-H^dagger Y^dagger g_+`, and its
right variations and Higgs variation are retained with the same signs.
The formula supplies those bilinears on its arguments. It does not
specify their off-mode pullback from every independent canonical
H5/H4 field. Unit normal overlap fixes the localized-mode coefficient,
not an all-complement trace/variation equation. The already assembled
chiral family mass block is preserved in its inherited block convention
and units; it is copied as evidence, never refitted or converted here.

For the intrinsic active fields of AE31,

\[
E_L=i\slash D L_L-Y_lH e_R,\quad
E_R=i\slash D e_R-Y_l^\dagger H^\dagger L_L,
\]

\[
E_H=-D^2H-2\lambda_H(H^\dagger H-\nu_{BH}^2)H
 -\bar e_RY_l^\dagger L_L.
\]

These are the retained Euler signs; the assembled LR carrier representation
is unchanged. If the intrinsic wall variables are dynamical, their
variations must be retained as unknowns. At fixed fields, the direct
photon variation gives `bar(Psi) Xi5 Psi` in S5, the corresponding
left/right Xi4 bilinears in S4, and the covariant Higgs kinetic source
variation. Induced Higgs, trace, pairing and domain responses belong to
the same coupled variation, not independently chosen states at each source.

This is an inventory of the **known first variations**, not permission to
sum S5 and S4 as independent determinant owners. AE4 explicitly makes the
local actions expansions of one microscopic functional. The missing
matching term must be recovered from that same realization.

## 3. Actual normal and temporal Green terms at node3

The retained common coframe is theta0=nu d_tau and
theta4=C(d_rho+zeta d_tau), with angular radius r and signature +----.
The inverse principal coefficients are

\[
a^\tau=i\Gamma^0/\nu,\qquad
a^\rho=i\Gamma^4/C-i\zeta\Gamma^0/\nu.
\]

For geometric positive-L2 pairing with coordinate-time volume density
mu5=2pi² nu C r³, the first-order Green densities are

\[
J_{\rho,L2}=i2\pi^2r^3(\nu\Gamma^4-C\zeta\Gamma^0),\qquad
J_{\tau,L2}=i2\pi^2Cr^3\Gamma^0.
\]

For the **Dirac-bar action pairing**, bar(Psi)=Psi^dagger Gamma0, they are

\[
J_{\rho,F}=i2\pi^2r^3(\nu\Gamma^0\Gamma^4-C\zeta I),\qquad
J_{\tau,F}=i2\pi^2Cr^3 I.
\]

The two pairings are not interchanged. The temporal density uses the
Cauchy measure; it is not the radial/material traction. For AE2's retained
symmetrized action the boundary variation has the factor
`(Psi^dagger J_F deltaPsi-deltaPsi^dagger J_F Psi)/2`.
The Green density matrix itself gets no additional half. Opposite outward
orientations are carried once by the existing two-sided spin/reset map.
This is not a new symmetry assumption for the retarded response.

At the actual proper wall nu_b=1, zeta_b=0, r_b=R. Thus
`J_rho,F=i mu4 Gamma0 Gamma4`, mu4=2pi²R³.
The normalized radial mode's known pointwise multiplier is
`kappa=1/sqrt(2I)`. On the12 saved source-image test directions, in their
existing common frame,

\[
G_W^{(3)}=J_{\rho,F}\kappa\Xi,\qquad
\partial_\tau G_W^{(3)}=
\left(3H-{I_\tau\over2I}\right)G_W^{(3)}.
\]

The geometric compact-p boundary term is zero by its known geometric
trace. That fact does not set Pi4 Xi_strat phi, an independent wall
response, or the conormal of P to zero. The derivatives above are the
known common-frame coordinate coefficients; a different native attachment
can have further transport/trace derivatives which remain required.

New execution reads cached node3/action_arc6, branch24, its98-coordinate
state and action-generated Y_tau. No state/clock or point action is rebuilt.
The known boundary coefficient rate is **-2.1042688271082444**. The stored
1280-by12 Dirac Green columns have Frobenius norm90.57814099901451; their
time jet has norm190.60075852164147. These are boundary-column diagnostics,
not native R4, stationary conormals, magnetic moments or uncertainties.

Using the already saved D5 p_original, the script also contracts the known
bulk Dirac Euler action against all12 W and12 p test directions. It uses
Gamma0 in the action dual and the full volume measure once. Its amplitude
vector norm is3.061205102195361 and its time-coefficient norm is
0.4566440396744268. The positive-L2 diagnostic load has norm
0.40151816974808946 and is stored separately as a24-by12 dual matrix.
All n1/n3 and64-carrier outputs survive these contractions. The omitted
native interface/Higgs/constraint/completion terms are null, not zero.

## 4. Coupled variation without an arbitrary fixed wall lifting

A normalized isometry permits the **parent-only coordinate decomposition**
`u5=W w_mode+chi`, `B chi=0`. Here w_mode=B u5 and chi are unknown
coordinates of the parent field. The known parent variation can be written

\[
a_5(Wv+\eta,Ww_{mode}+\chi)=\ell_5(Wv+\eta),\qquad B\eta=0.
\]

This is a change of coordinates inside H5, with the inherited pairings and
moving projections. It is the role of the cancellation-preserving W/p and
W/chi coordinates in the accepted numerical component. It does not make
w_mode the independent microscopic AE4 H4 field, impose a bounded graph
in H5⊕H4, or identify a reduced heat operator with the full stratified one.

For the actual native problem keep U=(u5+,u5-,psi4,...) in the owned
joint form domain V_F(a). With formal spectral shift s, the coupled
weak equation and its photon derivative are

\[
a_s(V,U)=q_a(V,U)+s m_a(V,U)=\ell_a(V),
\]

\[
a_{s,0}(V,U_A)=\ell_A(V)-a_{s,A}(V,U_0).
\]

In a fixed common chart, q_A contains the two Xi/D pair terms stated in
section1; all actual pairing, trace, length and domain pullbacks must be
added. The full source image is determined by Xi_strat on its input,
not by setting psi4=B_rad p. A bulk-only diagnostic load can have zero
wall functional **by its definition** while the solved wall response is
nonzero through coupling. This does not select the native photon's wall
source component, whose same-action insertion remains required.

The first unsupplied *variational* entry is explicit. In a compatible
trace chart write

\[
c_{45}(v_4,g_5)
 :=D_{\bar\psi_4}D_{g_5}S^F_{joint}[v_4,g_5],
 \qquad g_5=\gamma_5u_5.
\]

It is the cross term which supplies E45(g5) in the independent-wall
first-order Euler equation `E4(psi4)+E45(g5)=eta4` and the matching assignment of
the bulk Green functional to allowed joint variations. Equivalently an
owned joint variation graph and wall-output rule can determine that same
entry without adding a surface density. Its input is the actual H5
Sobolev trace/normal-data space; its output is the intrinsic chiral/family
H4 dual with its geometric measure. Only its source-reached restriction
is required, together with the derivative of that **same** prescription
under b_A. This is not the bounded overlap B_rad, a temporal projection,
or a conormal chosen from a generic boundary family.

Here eta4 denotes a linear Grassmann source **if** one is present in that
first-order problem; none is selected here. It is distinct from the
diagnostic positive-P weak-load functional ell4 above. The compact p is
not silently inserted into the first-order Euler action. The saved
contract's abstract wall RHS label `ell4` must be read with this distinction.

The displayed pre-restriction v14.45 action contains Psi_± and its seam
arguments. AE31's displayed local active-wall action contains L_L,e_R,H.
Neither displays a mixed independent-wall/off-mode-bulk variational term
or the joint allowed-variation equation connecting those variables.
v15.69 specifies a fixed-trace functional but does not expand that trace
and its source-dependent derivative on off-mode independent-H4 fields.
AE4 specifies the canonical direct sum and a functional of D_strat; that
formula does not in turn define D_strat's missing incidence action/domain.
The older v14.67 term is a theorem-class attachment on geometric KKT
directions, and v14.69's realized incidence is a symmetric-metric-tensor
map. They are not this fermion entry and were not copied into it.

Consequently the **examined displayed equations are insufficient** for
this entry: omitting it leaves an uncoupled local-wall variation, while
identifying the wall field by B or a trace requires an extra relation
not contained in those formulas. This is a precise scope statement,
not a proof of absence from every local handoff or a claim that arbitrary
alternative attachments solve the BHSM action. A recovered further
equation could supply it. The current code does not choose one.

Native assembly stops at c45/the equivalent joint variation prescription,
before assigning a full wall output or forming its interference Gram.
Unknown blocks remain null and the accepted parent solution is unchanged.
No reference wall number is appended to its old stationary return.

## 5. Execution, checks and resumption

`run_2/node3_joint_known_variations.npz` contains the evaluated Green
columns, time jet, bulk Euler vectors, diagnostic load and actual state
identities. `run_1` preserves the failed first new attempt: a64-spin matrix
was initially applied to a flattened1280-row angular direct sum. Separate
n1/n3 actions corrected the layout before any result was produced. No old
production calculation was repeated. The successful cache-only run took
0.93 seconds; three new targeted checks passed in0.48 seconds. They check
the actual coframe/action-dual Green row, its owned time coefficient,
and independently contracted Euler/load pairings. The old seven checks
and old reference wall rows were not rerun.

Reproduction from the publication checkout, into a fresh directory:

```powershell
C:\Python314\python.exe scripts/replay_muon_joint_variational_attachment.py --output <fresh-directory>
C:\Python314\python.exe -m pytest --noconftest -q tests/test_muon_joint_variational_attachment.py
```

The packet retains exact revision, branch, source/input hashes, equations,
raw failed/successful artifacts, executed-code snapshots, ledgers and
error scope. Numerical norms above are nominal binary64/nodal contractions;
they do not certify history, domain/interface, continuum or Pauli accuracy.
The inherited endpoint/tube/interpolation errors remain distinct. Native
shift and spectral length are not assigned a value. Frozen QED/Higgs/weak
contributions and calibration convention are copied unchanged. No physical
a_mu, g_mu, strong correction or native uncertainty is claimed.

Resume with one operand: the **current action-owned joint first-order
interface variation c45, or its equivalent domain/output prescription,
on the source-reached directions**. Derive its source jet from the same
equation, then assemble and solve for the wall field jointly. Do not ask
for a separate physical Theta_p, project the full heat action onto an
isolated block, or restart mass/profile/common-A/calibration derivations.
