# Current covariant connection attachment: retained equations and new Higgs row

Checkpoint `BHSM_MUON_ACTION_CONNECTION_ATTACHMENT_20261002` continues PR465
at `bc27b082542ccb3c4c64fadc7b894430d71292a6`, scientific reference
`524ed90689bd5923c249bba2e699abf627e703cd`. The publication branch is
`codex/muon-parent-maxwell-density-review`. Its starting tree was clean.
All earlier mechanical transport, mixed weak rows, contacts and frozen
local contributions are preserved. No earlier scientific producer or
five-test mechanical calculation was rerun.

The intended meaning of the zero mechanical-sector amplitude can now be
traced to a concrete retained source: v17.97 declares **zero fluctuation
around the mechanical connection**. Its executable calculation supplies
zero traces and fluxes, however, rather than an expansion of the fermion
covariant derivative about that connection. The actual background
substitution into `S_Dirac[e,omega_spin,A_SM,Psi]` remains unspecified in
the inspected action/attachment chain. This finding does not certify any
alternative background as a solution of the full equations.

The new mathematical results are an exact Higgs compatibility obligation
and an evaluated Higgs/gauge mixed source action on the actual eight saved
lifts. These sharpen the required attachment and the terms it must carry;
they are conditional mechanical-reference results, not a physical anomaly
or an exterior forcing return.

## Action-to-operator trace

`retained_equations.json` records verbatim function bodies, defining
equations, original line numbers and source hashes. Functions were read
by AST, not executed. The following chain is the evidence, independent
of old completion/status flags.

| Producer | Actual retained expression | What it fixes |
|---|---|---|
| v15.50 `diagonal_quotient_contract`, `action_ownership_ledger` | `omega=lambda theta_u+(1-lambda)theta_v`; classical background mechanical; its curvature energy is already in R8; physical weak identification requires representation attachment | Geometric principal connection and its gauge-energy ownership |
| v15.53 `chiral_bundle_contract`, `hybrid_bundle_gluing` | rank16 SM representation, three family projectors, Higgs doublet; post-event zero sector, inherited norm; discrete labels transported, continuous connection one-forms not pregeometric primitives | Associated representation and reset carrier, not a covariant-derivative offset |
| v15.57 `full_reconstruction_operator` | `z_star_SM=... A_SM=0,H_SM=0,Psi=0` | Which named reset field amplitudes vanish; this is not the later nonzero local Higgs branch |
| v17.97 `zero_background_calderon_closure` | explicit zero-fluctuation-around-mechanical declaration; actual arrays `trace=event_flux=child_flux=zeros(4)` | Intended reference meaning; the calculation establishes a homogeneous zero-input graph only |
| foundational v14.45 `foundational_action_payload` | `barPsi [i gamma^mu nabla_mu^total+i eps Gamma_perp(partial_s+...+m_eta)] Psi` | Canonical adopted fermion action; `nabla_total` is not expanded into a physical background here |
| foundational v14.45 `zero_mode_pullback_payload` | normalized `u0=N J^(-1/2)sin(f_eta)`, integral `J abs(u0)^2=1`; tangential kinetic pullback retains `barpsi i gamma^mu nabla_mu psi` | No new residue multiplier; the unchanged symbol does not compute a connection projection |
| v15.75 `first_order_parent_action`, `contorsion_schur_complement` | separate coframe, spin connection and rank16 gauge connection; `S_Dirac[e,omega,A,Psi]`; `omega_spin=omega_LC+C`, `C_star=-M_C^-1 J_S` | Spin/internal factors are distinct; no substitution of the mechanical connection into `A` is expanded |
| v15.55 `diagonal_fiber_dirac_contract`, `spinor_lift_incidence` | round vertical Dirac blocks scaled by `L_F^-1`, representation incidence and wall chirality | Vertical eigenvalues; no horizontal connection-preserving spinor projection |
| current AE3.1 `action_composition_contract`, `first_variation_and_pole_gate` | `abs(DH)^2-V+i barL slash(D)L+i bare_R slash(D)e_R-Yukawa`; full Higgs equation includes `-D^2 H` | Minimal covariant interactions and Higgs equation; the connection in `D` remains implicit |
| `chiral_operator_assembly` | `[[D_L,M_l],[M_l^dagger,D_R]]` on the AE2 reset-glued domain; actual mass block assembled | Massive first-order structure is assembled; this packet does not reopen it |
| v15.69 `unified_parent_boundary_functional`; AE4 `microscopic_owner_contract` | fixed-trace parent functional; same-owner `D_strat`, `P=D^dagger D` and finite E1 | Ownership and domains; neither supplies the omitted background substitution |

The foundational action is explicitly adopted as effective fermion input,
not a newly derived bosonic-to-fermionic action in this continuation.
The v15.75 historical gravitational weight is not substituted for the
current coefficients. Its separate spin/internal variables and contorsion
identity alone are used; the frozen gauge weight
`Lambda(1+X_eta^3)` stays unchanged.

The intended decomposition, with the original field names distinguished,
is

\[
\Omega_{\rm SM,total}=\Omega_{\rm SM,ref}+a_{\rm SM},\qquad
\Omega_{\rm SM,ref}\ \text{intended as}\ \rho_{16*}(\omega_{\rm mech}),
\qquad a_{\rm SM}^{(0)}=0.
\]

This is the v17.97 declaration, not an implemented current-D substitution.
The retained parent action instead writes `F_A` and `S_Dirac[...,A,...]`
without expanding whether its named `A` is the total connection or that
fluctuation and without giving the connection-compatible attachment.
The equation `N_linear 0=0` holds for any homogeneous linear graph; it
cannot distinguish background coefficients or produce the nonzero SAME-
source return `j_ext`. This is an algebraic limitation of that calculation,
not an assertion that two possible backgrounds solve the field equations.

The supplied `rank16_connection_attachment` does fix `rho`, with
`jmath_a=-2iT_a` and `W_hat=2omega`. It resolves the representation and
index8 normalization already computed. A representation homomorphism
alone does not identify the principal connection in the current matter
action with the metric mechanical connection. No trace factor supplies
that missing equality.

## Spin, current local carrier and source

In a current associated-bundle trivialization the required product
connection has the form

\[
\nabla_{\rm total}=
\nabla_{\rm spin}(e,\omega_{\rm LC}+C)\otimes I_{16}\otimes I_3
+I_{\rm spin}\otimes\nabla_{\rm SM,total}\otimes I_3.
\]

The two terms act on different factors. The geometric angular Dirac block
already contains its ordinary spin connection. It is not a second weak
connection. Conversely, including the mechanical curvature in R8 does
not remove a coupling that an actual matter attachment would require.
At zero classical Psi, the algebraic spin current gives `C_star=0`;
this does not set quantum current contacts or the internal background to
zero.

The recovered original local file `fermion_body.py` implements

\[
H_{\rm free}=R^{-1}\operatorname{diag}(-D_3,+D_3)
+m\sigma_{1,LR}\otimes I,
\]

and a separate affine electromagnetic Clifford insertion. It is explicitly
a parameterized free chiral propagation block. It has no explicit rank16
mechanical background insertion. This omission is implementation evidence,
not a physical proof that `Omega_SM^(0)=0`. Its source hash is
`6aaab74462fa802fe294f74113a78675a056b70321884f636c4ab147491c337e`;
a byte-identical provenance snapshot is included, without running it.
Similarly v15.96's periodic free squared-spectrum seed is not an expanded
interacting current Dirac operator and was not executed.

Differentiation remains in **b**, with the retained source

\[
\delta_{b_A}\Omega_0=T_bY_{A,c}\theta_R^c(-iQ),\qquad
\delta_{b_A}\Omega_1=U\delta_{b_A}\Omega_0U^{-1}.
\]

The saved source-independent `U=rho(w)` and right coframe are reused.
No source, temporal or radial derivative of U is newly assumed; those
were established in the prior transport. There is no additional `2/3`
vertex factor. H and Q must be transported together by the same attachment:
`H1=U_H H0`, `Q1=U_H Q0 U_H^-1`. Their electromagnetic relation remains
`Q1 H1=0`. It says nothing by itself about `D_Omega H`.

If the mechanical weak connection is attached, it is noncentral on the
left weak doublet, while the right charged-lepton singlet has no weak
generator. It can mix the two left components; an isolated scalar charged
line cannot replace that operator. No phenomenological neutrino mass or
new family coefficient is supplied in this packet.

## New exact compatibility condition and actual source action

Use only the retained local Higgs branch `H0=nu(0,1)` and weak doublet
`e_a=-i sigma_a`. This is a **conditional** check of coupling that branch
to the mechanical reference, not a selected global Higgs solution. In
the saved section

\[
\Omega_1=(\lambda-1)e_a\theta_R^a,\quad
dH_1=e_a\theta_R^aH_1,\quad
D_{\Omega_1}H_1=\lambda e_a\theta_R^aH_1.
\]

The unit angular-coframe identities are

\[
\sum_a\|D_aH_1\|^2=3\lambda^2\nu^2,\qquad
(F_{\Omega_1})_{*a}=2\lambda(\lambda-1)e_a,
\]
\[
\sum_a\|(F_{\Omega_1})_{*a}H_1\|^2
=12\lambda^2(\lambda-1)^2\nu^2.
\]

One curvature component has determinant
`4lambda^2(lambda-1)^2`; hence no nonzero parallel doublet exists at
`0<lambda<1`, independent of its chosen direction. Angular derivatives
and curvature carry their usual `R_angular^-1` and `R_angular^-2` factors.
In the fixed sigma0 constant-H chart the angular Laplacian gives
`Delta_Omega H0=-3lambda^2 H0/R_angular^2`. Thus the potential saddle
`(H^dagger H-nu^2)H=0` alone does not solve the full covariant Higgs
equation. Temporal/radial contributions, a nonconstant H and the inherited
interfaces have not been solved or excluded.

There is a sharper source consequence. For the angular pairing
`q_H(v,H)=<Dv,DH>` and photon `aH=0`, differentiation gives

\[
\delta_a q_H(v,H)=\langle v,a^\dagger D H\rangle.
\]

The direct fixed-H photon quadratic column vanishes, but this Higgs/gauge
mixed row need not vanish. Transform it into sigma0 without rotating the
spatial coframe. With the **saved** adjoint coefficients `R=Ad_w`, its
new explicit action is

\[
U_H^{-1}a_{1,A}^\dagger D_{\Omega_1}H_1
=\frac{T_b\lambda\nu}{R_{\rm angular}^2}
\sum_cY_{A,c}\begin{pmatrix}R_{c1}-iR_{c2}\\0\end{pmatrix}.
\]

This map was evaluated for all eight supplied `real_mode_coefficients`,
using the saved rotation coefficients and the existing Gaunt product
helper. It did not rerun the mechanical transport or weak-row producer.
Both connected output levels n1 and n3 are retained. All eight normalized
Haar column norms squared evaluate to `0.6666666666666663`; these are
binary64 coefficients of this conditional Higgs source map. They are
neither a vertex normalization nor the older n2 contact fraction nor
Pauli coefficients. The supplied cut lambda and T_b are applied once;
nu and `R_angular^-2` remain explicit, without fitting a VEV or radius.

`conditional_higgs_source_actions.npz` saves the unit coefficients and
65-node cut coefficients per `nu R_angular^-2`. The pairing above is
positive angular notation. Its Lorentz action sign and density must be
taken from the actual inherited bilinear, rather than choosing a new
positive parent metric. The corresponding coupled-Higgs elimination
would involve its actual source cross blocks and owned causal inverse;
the zero direct column does not justify omitting that response. No such
inverse, background selection or exterior response is claimed here.

## First unresolved equation, sufficient contraction and row use

The first missing coefficient is `A_hor^(0)`, the internal horizontal
one-form in the current action, with its M5/M4 attachment. A precise
connection-preserving version of the equation is

\[
I_{\rm spin}\otimes\mathcal A_{\rm hor}^{(0)}\otimes I_3
=J_5^{-1}\nabla_{5,\rm total}[A_{\rm SM}=0]J_5
-\nabla_{5,\rm spin}\otimes I_{16}\otimes I_3,
\qquad \mathcal T_{54}J_5=J_4\mathcal T_{54}^{\rm canonical}.
\]

Here `J5:S(g5) tensor E_SM,16 tensor C3 -> E5_physical` and the analogous
J4 are the action's isometric Clifford attachments on the existing trace
domain, not new boundary choices. `A_hor^(0)` is an anti-Hermitian
one-form valued in `rho16_*(ad P_SM)`. A direct supplied coefficient or
its contracted Clifford actions on the existing source/test space suffice;
this packet does **not** require building full J matrices or a complete
Dirac kernel. For the intended associated mechanical route the equality
would give `A_hor^(0)=rho16_*(omega_mech)` through an actual compatible
principal attachment. If a parent spinor pushdown instead generates the
coefficient, its owned normalized projection must be supplied:

\[
(\mathcal A_{\rm ind,\mu})_{rs}
=\langle\eta_r,\nabla_{{\rm parent},X_\mu^H}\eta_s\rangle_{\rm fibre/wall}
-(\text{base spin connection})_{rs},\quad
X_\mu^H=\partial_\mu-\omega_\mu^aV_a.
\]

The retained vertical eigenvalues do not supply that horizontal projection.
This formula describes an alternative *producer route*, not another
phenomenological background choice. Additional Clifford-degree-zero
potentials must be identified separately if that reduction requires them.
The source tangent is fixed above; it fixes a derivative, not this value
at zero source. Source derivatives of an actual varying attachment must
be retained if the defining action makes it vary.

| Saved/new term | Present justified use |
|---|---|
| Completed mechanical angular mixed rows, curvature contacts, temporal/radial connection jets | Evaluated primitive **geometric reference** operator. They enter the physical gauge primitive if the retained intended connection attachment is established; no manual sign/lambda repair |
| Index8, `K_Q=(2/3)K_component`, full pointwise weight and Lorentz principal coefficients | Preserved normalization/metric operands; do not redetermine the background connection |
| New fixed-branch Higgs/gauge mixed row | Conditional additional action term required for that mechanical associated-Higgs realization; no physical H or induced response is selected |
| Current interacting Dirac and full AE4 mixed response | Null/unevaluated until the actual action-to-carrier coefficient is supplied; primitive and induced local expansion must remain a single owner |
| SAME-source exterior `j_ext`, shifted resolvent | Null/unevaluated; zero graph and continued local source are not these response applications |

The inspected expressions do not specify the required equality. This is
more than an omitted term in a known local matrix: the mapping of the
parent gauge field and `nabla_total` into the current matter connection is
not expanded by these producers. It is not a proof of non-identifiability
in every BHSM record. If an owned attachment coefficient is recovered,
its implementation and response become computations using the preserved
rows. No interpolation coefficient, new physical state or history solve
has been introduced.

The past face stays the artificial C2 step1222 cut, with its inherited
prefix orientation; the future uses its canonical stop. There is no
pre-E0 arm, artificial future tail, independent endpoint condition or
positive-sign replacement of the Lorentz weak problem. Parent-H and
affine-logR reconstruction errors remain distinct and inherited.

## Evidence, checks, error scope and frozen ledger

Twenty-three input hashes, extracted equations and the original local
carrier snapshot are in `artifacts/muon_connection_attachment_20261002`.
The relevant retained producer texts agree with the primary scientific
checkout after line-ending normalization; no relevant primary source
changes were found. The newer PR-only realization modules and unrelated
primary work are untouched. Source context records both actual branches
and HEADs. The old mechanical array SHA-256 remains
`146435df28178967c321c0aa7e89a1511395d196f96b8715532aa98e3e312c2b`.

Executed: one scoped source/exact-algebra pass, followed by one expanded
pass to evaluate the newly derived Higgs mixed action. A final short replay
corrected the result's global error-scope description to include those
binary64 conditional contractions. All outputs remain in Downloads.
Three new targeted tests pass: right-Maurer curvature and
invertibility; differentiation of the unreduced Higgs bilinear; and
pointwise reconstruction of the new n1+n3 action on all eight actual
source lifts at three group points. These are action/algebra/array checks,
not physical transfer directions. A test-only parsing issue (`lambda`
as a Python keyword) was corrected; no scientific data were changed.
The earlier five tests are preserved and were not rerun.

Exact: curvature/integrability identities and finite representation support.
Conditional numerical: the new finite Gaunt coefficients at supplied
reference inputs. No new certified quadrature/tail/domain, physical
background or native soft-limit bound is asserted. State, renormalization,
strong/native subsets and post-division extraction remain later requirements.
All six signed native ledger entries stay null, never zero.

The frozen conditional local ledger remains

```
a_mu_QED_local = 0.00116550200495813
calibration-only standard uncertainty = 1.79e-13
0 < delta_a_mu_h_local_1 < 3.500331e-9
0.0011655039493 < a_mu_selected_local < 0.0011655109506
```

The selected-local interval already combines its local terms. The
calibration uncertainty retains its original convention (alpha inverse
137.035999084 with standard uncertainty 2.1e-8, other original inputs
fixed). No terms were refitted or added, and it is not a total uncertainty.
No physical `a_mu=F2(0)` or `g_mu=2(1+a_mu)` has been calculated here.
No experimental anomaly or discrepancy was used.

Reproduce into a fresh output directory:

```powershell
python scripts/replay_muon_connection_attachment.py --output C:\Users\carbe\Downloads\BHSM_muon_connection_attachment_replay_new
python -m pytest --noconftest -q tests/test_muon_connection_attachment.py
```

The standalone `replay.py`, compact checkpoint, hashes, exact working-tree
diff and publication receipt are saved in
`C:\Users\carbe\Downloads\BHSM_muon_connection_attachment_524ed906_20261002`.
The single next operand is the action-owned value/substitution equation
for `A_hor^(0)` above, on the current attached source/test space. Its
consumer is the physical mixed parent/Dirac operator and then the
inherited SAME-source exterior response.
