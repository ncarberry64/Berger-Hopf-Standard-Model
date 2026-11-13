# Inherited connection index and pointwise parent Maxwell weight

1 October 2026. Scientific source revision:
`524ed90689bd5923c249bba2e699abf627e703cd`.
Checkpoint: `BHSM_MUON_PREDECESSOR_INDEX8_POINTWISE_WEIGHT_524ED906_20261001`.
This continues the published current-parent local-velocity checkpoint without
overwriting its two replays, three checks, source hashes or earlier evidence.

## New result

The predecessor embedding is now explicit:

\[
 \jmath(e_a)=\bigoplus_{1}^{4}(-i\sigma_a)\oplus0_8=-2iT_a,
 \qquad I_\jmath=8,\quad
 K_{\mathrm{trace}}=K_{\mathrm{comp}}/8,\quad
 K_Q=\tfrac23 K_{\mathrm{comp}}.
\]

The current cap fields also supply the pointwise event weight required by
the v15.73 parent action, W=Lambda(1+X_eta cubed). In the inherited b frame,
the executable **weighted local Maxwell velocity coefficient** is therefore

\[
 E^{\mathrm{local,event}}_{b,AB}
 =\kappa_1\frac23\pi^2L_F^5\Lambda(1+X_\eta^3)
       \frac{C_\rho r}{\nu R_4}\,G^{\mathrm{Haar}}_{AB}.
\]

For the first and last saved boundary nodes, E/kappa1 has fixed-input Arb
enclosures

```text
[1321.07999798523190786340369777438731820966886 +/- 2.66e-42]
[1321.43279217342823741810562448391617094445836 +/- 5.95e-44]
```

These are parent electric action-density coefficients in the retained action
coordinates. They are not anomalous moments. The full AE4 induced matching
response, native shifted resolvent and physical muon Pauli coefficient remain
unevaluated. No numerical value of kappa1 or new Wilson coefficient is chosen.

## Why the index is derived

Three concrete retained equations supply the previously unrecovered route:

1. `aether_diagonal_sp1_m4_attachment_v15_50.py` uses
   theta=u inverse du, the unit round S3 volume 2 pi squared and the geometric
   component action -K_comp F^a F^a/4, K_comp=kappa1 pi squared L_F^5.
2. `aether_hybrid_standard_model_bundle_v15_53.py::chiral_bundle_contract`
   fixes the Sp(1) doublet/singlet carrier. Its `hybrid_bundle_gluing` states
   that the post-event Sp(1) kinetic norm is inherited from this parent
   diagonal quotient.
3. `aether_unified_m5_m4_pushforward_v15_69.py::unified_parent_boundary_functional`
   extends that same diagonal Sp(1) operator through one rank-16 trace to
   the retained (SU3 times Sp1 times U1Y)/Z6 bundle.

These are normalization and representation equations, not merely a
certification flag. The earlier checkpoint's unresolved predecessor index
is superseded by this recovery. It was not an absence theorem.

For unit imaginary quaternions [e_a,e_b]=2 epsilon_abc e_c. The fundamental
map is e_a maps to -i sigma_a, with T_a=sigma_a/2. The retained one-family
carrier contains three colored Q_L doublets and one L_L doublet, plus eight
weak singlets. Each doublet contributes
Tr[(-i sigma_a) dagger(-i sigma_b)]=2 delta_ab. Consequently I_jmath=8.
The index is unchanged by unitary changes of doublet/family frame. A
numerical choice of a Pauli normalization is unnecessary.

The actual covariant-derivative coordinates obey

\[
 d+\jmath(\omega)=d-iT_a\widehat W^a,\qquad
 \widehat W^a=2\omega^a.
\]

The same factor holds for nonlinear curvature, not only a linearized
generator. In the canonical connection coordinates the Q source is
(W3_hat,B_hat)=beta(1,1), so its generator is Q=T3+Y. The exact inherited
traces are Tr T3 squared=2, Tr Y squared=10/3, Tr T3Y=0 and Tr Q squared=16/3.
Thus K_Q/K_comp=(16/3)/8=2/3. No second factor four belongs in this conversion,
and no additional mode, color or family count multiplies it. Color
multiplicity is already included in the supplied representation rows.

The orthogonal connection coordinate remains A_Q=sqrt(2) beta. The saved
muon source/sign conventions are not renormalized in this calculation.
The rank-16 table writes all fields as left-Weyl fields, so e_c has charge
+1; its conjugate supplies the charge -1 right-handed charged-lepton sector.
The muon and its conjugate-charge source sectors must remain distinct.
The neutral singlet is a representation slot, not an inserted massive
neutrino pole or a selected neutrino mass.

## Pointwise additional weight from the same parent fields

`aether_event_shell_joint_operator_v15_73.py::weighted_parent_operator`
specifies

\[
 W(\tau,\rho)=\Lambda(\sigma)(1+X_\eta^3),\qquad
 Q[A]=\tfrac12K_{\mathrm{trace}}
   \int W\operatorname{Tr}_{16}(d_{A_0}A,d_{A_0}A).
\]

It explicitly rejects replacing this field by a uniform Legendre minimum.
`aether_sobolev_galerkin_pencil_lift_v15_81.py::generalized_lagrangian`
supplies the scalar F(X)=X/2+X^4/8 and its principal-fibre factor
2F'(X)=1+X cubed, as well as the current f=chi target map. It fixes

\[
 X_\eta=\frac1{4C_\rho^2}
       +\frac{3\cos^2\chi}{A^2}
       +\frac{3\sin^2\chi}{B^2}
       -\left(\frac{\zeta_\rho}{2\nu}\right)^2,
 \qquad\rho=2\chi.
\]

Here nu=N/N_b and zeta_rho=2 beta_chi/N_b are the already-recovered
boundary-proper-time fields; C_chi=2 C_rho. The angular terms use the full
two-orbit parent target map, not the quotient radius alone. At the regular
pole sin squared chi/B squared is evaluated by its analytic cancellation,
using v(0)=0 in the retained ansatz. No cutoff wall or 0/0 replacement is used.

The 48-by-65 cached samples have L_eta in
[0.8365015283474324,6.708224570486777]. These sampled extrema are **not** a
continuous-domain certificate, and their minimum is not used as a uniform
weight. For example, at node 0 and rho=pi/4 the fixed-input ball is
L_eta=[0.999646709449726205046178714665181272408913063 +/- 4.29e-46], while
at its boundary it is
L_eta=[6.70822457048678432739842047491660576418907885 +/- 3.73e-45].

The earlier Lambda-only geometric density and raw artifact remain untouched.
After attaching the newly derived index, its boundary values per kappa1 are
approximately 196.934372739607 and 197.168745250135. The event-weighted
coefficient is a separate additional evaluation of the retained predecessor
action, not a refit of the old geometry or local anomalous-moment values.

The AE3 Lorentz frequency report writes the full W in its action equation,
while its inspected radial implementation calls the Lambda-only weight.
Those frozen numbers are not altered or promoted to the present pointwise
coefficient. This mismatch supplies an additional concrete reason to retain
the parent form before radial elimination rather than reuse a low-frequency
surrogate as the full current operator.

## Projection, derivative terms and native scope

Both W and the quotient metric depend on tau,rho only. The actual round
angular quotient and saved Haar-normalized mode lifts give G_Haar=I8 for
this local electric term. Curl squared=9 I8 remains the saved angular
restriction, and is not used to infer electric scalarity or replace a full
covariant magnetic operator. The historical curl squared=4 is unused.

The beta coefficient is still 2 pi squared K_Q W C_rho r/nu. Pulling it
back with beta=b/sqrt(2 pi squared R4) once gives the coefficient above.
The same local bilinear retains

\[
 D b=b_\tau-\zeta_\rho b_\rho-H_b b/2,\quad
 \pi_\tau=E_b D b,\quad
 \pi_\rho=-\zeta_\rho\pi_\tau+epsilon r_b^{\mathrm{local}}b_\rho,
 \quad r_b^{\mathrm{local}}=K_QW\nu r/(C_\rho R_4).
\]

The divergence contains coefficient derivatives, including those of L_eta,
and the -H_b pi_tau/2 frame term. Temporal and radial/interface pairings
are distinct. Lorentz Maxwell has epsilon=-1; a positive spatial form
requires its already-owned positive realization. No positive metric, Wick
rotation, terminal wall or new endpoint parameter is chosen here.

The canonical-stop gauge/BRST cache was followed through its concrete
materializer and producer, and **inspected only**. It evaluates a scalar
unit-shape history operator with three curl-plus-2 modes and potential four.
It does not contain this eight-mode pointwise weighted parent coefficient,
its radial lift, or the complete induced matching response. Its finite
Calderon value cannot be substituted, rescaled by a trace count, or counted
as the required native resolvent. Its canonical-stop domain contract is
preserved; no unrelated Gate-7 closure is required by this report.

The selected AE4 functional remains
Gamma=-1/2 STr E1(ell_star squared P_strat), with its relative-zeta/eta
completion. The complete electric response is the primitive local term
plus the same-owner induced remainder, which is unevaluated, not zero.
It may be a nonlocal kernel. No independent Wilson coefficient or second
determinant is added to supply it.

For source directions A,B this response needs the actual source jet

\[
 \Xi_A=\delta_{\beta_A}D_{\mathrm{strat}},\quad
 P_A=D_0^\dagger\Xi_A+\Xi_A^\dagger D_0+\text{owned adjoint/domain terms},
\]
\[
 P_{AB}=\Xi_A^\dagger\Xi_B+\Xi_B^\dagger\Xi_A
       +\text{owned second-source/adjoint/domain terms}.
\]

The local internal factor Q is now supplied. On M4 its minimal source is
c_src(a_A)Q, where c_src includes the phase/sign in the retained Dirac-source
convention. Here a_A=T_b Y_A times the supplied profile, with Y_A a unit-S3
coordinate one-form. Thus beta=T_b b, T_b=(2 pi squared R4)^(-1/2), and the
orthonormal-frame coefficient is T_b/R4=f_R4. E_b is the b-frame velocity
coefficient, not the beta-frame coefficient. The current native
positive-parent and cross-stratum/domain lift of that insertion has not
been materialized by the inspected owner or event-flux assembler; they
define or accept those operands. A geometry Hessian or scalar template is
not that source jet. This is an implementation/realization gap in the
selected operator route, rather than another adjustable predecessor
normalization or a request to select a new physical state.

The generalized heat evaluation must retain both K and M, their genuine
mixed jets, grading, source-dependent length and domain terms when present:

\[
 A_{AB}=M^{-1}(K_{AB}-M_{AB}A-M_AA_B-M_BA_A),\quad
 Q(A)=\tfrac12A^{-1}e^{-\ell^2A},\quad
 \Gamma_{AB}=\operatorname{STr}(DQ[A_B]A_A+QA_{AB})
\]

for fixed length, plus the owned length/completion terms otherwise. Both
moving-mass terms are required. The native length is not sent to zero and
the proper-history resolvent variable is not physical momentum squared.
No divergent or finite matching cancellation is claimed in this sprint.

## Evidence and one next operand

The new three targeted checks validate the quaternion/nonabelian curvature
normalization and component action pairing, and independently reconstruct
X_eta by contracting the full Lorentzian parent inverse metric with the
target-map Gram. They passed in 0.09 seconds in the standalone layout and
in 2.51 seconds in the publication repository layout.
Two inexpensive deterministic replays produced the new matrix
representation and weighted density, with four fixed-input Arb192
evaluations. No history solve, spectral solve, native heat or physical
soft-transfer direction was executed. Raw earlier replays were not repeated.

Arb balls enclose arithmetic at exact cached binary64 inputs, including
display rounding. They do not enclose history/interpolation, quadrature,
source/domain lift, complement, full induced matching or theoretical error.
The current Galerkin bulk uses its own discrete localization quadrature;
matching that discretization to the exact predecessor Lambda profile is
also part of the remaining implementation error, not silently certified.

Input hashes, actual source/publication revisions, relevant source diff and
replay evidence are stored with the packet. Reproduction:

```text
python replay.py --output <new-directory>
python -m pytest test_muon_connection_weight.py -q
```

Repository reproduction reuses the previous immutable geometry artifact:

```text
python scripts/replay_muon_connection_weight.py --output <new-directory>
python -m pytest tests/test_muon_connection_weight.py -q
```

The inherited conditional local numbers remain frozen:
a_mu_QED_local=0.00116550200495813, calibration-only standard uncertainty
1.79e-13; 0<delta_a_mu_h_local_1<3.500331e-9;
0.0011655039493<a_mu_selected_local<0.0011655109506. The calibration convention
is alpha inverse=137.035999084, standard uncertainty=2.1e-8, with other
original conditional inputs fixed. The selected-local interval is already
combined. No component is added again or compared with experiment.

All six native ledger entries remain null/unevaluated:
native_bulk_heat, state_variation, contact, domain_boundary,
completion_counterterm and strong_within_native. Strong terms remain a
nested native subset, not a separate phenomenological addition.
Physical a_mu, g_mu=2(1+a_mu), and total uncertainty remain unevaluated.
No dimensionful magnetic moment is reported. This code is a muon realization
of the existing machinery, with no universal-framework refactor.

**One next operand:** materialize the current-domain photon source jet of
P_strat above, restricted to the eight supplied lifts and required generated
profiles with connected-complement control. Use it to evaluate the same-owner
induced matching response, then apply the completed K+sM to the existing
source with geometric duality. The index8 and pointwise local weight no
longer block that step. Do not replace the remaining source/domain jet by
a finite benchmark, an assumed zero remainder, or a newly selected boundary.

The three focused checks also passed in the publication repository. All
five required read-only publication audits passed; their command, staged
diff hash, parent revision and log SHA-256 are recorded in
`publication_validation.json`. These audits do not certify the native
operator or a physical anomaly. The full suite was not run. Git-staged
blobs of all four scientific files were independently checked against
the two-replay manifest; no scientific calculation was repeated.
