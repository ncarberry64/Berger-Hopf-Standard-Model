# Incoming C1 LR/Higgs cotangent: exact local charged-CAR reduction

## Result and scope

The retained electromagnetic and CAR representations do **not** remove the LR/Higgs contribution merely because it is off diagonal in chirality. The charged left and right muon components have the same electromagnetic charge. Their off-diagonal chiral bilinear lies inside the particle charge sector; it is not an off-charge Nambu block.

A new exact local reduction is available. At a fixed point in an orthonormal spin frame, after the retained charged-muon family restriction, the measure-plus-coefficient variation of the intrinsic LR bilinear depends on one complex combination

\[
t_\alpha=b_\alpha m_\mu+\delta_\alpha m_\mu,
\qquad m_\mu=y_\mu h,
\]

where `h` is the component of the existing Higgs field in the charged-lepton gauge contraction. No value or incoming profile for `h` is chosen. In that fixed frame its Hermitian particle coefficient is

\[
B(t_\alpha)=\Re(t_\alpha)\beta+
 \Im(t_\alpha)i\beta\gamma_5.
\]

This gives the exact pointwise identities

\[
B(t)^2=|t|^2 I_4,
\qquad \|B(t)\|=|t|,
\qquad B(t)=0\iff t=0.
\]

In canonical self-dual coordinates the ordinary ordered covariance-derivative functional has the CAR-odd representative

\[
S(t)=\tfrac12\operatorname{diag}(B(t),-\overline{B(t)}).
\]

It is nonzero whenever `t` is nonzero, in the entire local affine charged-CAR tangent allowed by the retained source. This is an exact statement about the local action subspace, not a nonzero verdict on the incomplete physical E1 operator.

The local real span at a fixed point/frame is the rank of the coefficient rows `(Re t_alpha, Im t_alpha)` and is at most two. **That bound does not apply to the complete E1 moment rank**, to variable multiplication kernels over the collar, or to their domain/solution-response pullbacks. Those quantities remain unevaluated.

## Pinned source provenance

All repository reads use commit `ad750077f1a3138418a2dc4ee65f7c50236b5608` of `ncarberry64/Berger-Hopf-Standard-Model`. Relevant files are cached under `source_snapshot/` adjacent to this note.

1. `AGENTS.md`: retain supplied action architecture, distinguish conditional algebra from a physical prediction, preserve frozen screens, and do not introduce empirical mass inputs.
2. `src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py`, `dirac_gamma_matrices`, `foundational_action_payload`, and `zero_mode_pullback_payload`: the actual gamma convention is Dirac representation with signature `(+---)`; opposite collar orientations supply the retained left/right zero modes; the global additive bridge is `-integral[bar(Psi_+) Y_f H Psi_-+h.c.]`; normal kinetic and two-sheet Higgs overlap are both one.
3. `src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py`, `action_composition_contract`, `charged_lepton_yukawa_operator`, and `first_variation_and_pole_gate`: the term is `-bar(L_L)Y_l H e_R+h.c.`, `Y_l=(16 sqrt(2 pi)/3969)T_l`, `T_l` is the fixed internal family operator, `Y_l` is Hermitian positive, commutes with family projectors, and the Higgs remains an intrinsic active field. Only this action and tensor structure are used; the C2 Higgs saddle and numerical masses are not imported.
4. `artifacts/muon_birth_fermion_state_representation_20261008/run_1/fermion_state_representation.json`: the electromagnetic generator is `Q_l=-I4_spinor tensor I3_family`; the conjugate-charge partner is separate; the existing muon is the charged-lepton slot1 `(5,2)`; nonisometric localization requires its induced CAR pairing rather than ambient identity.
5. `src/bhsm/interface/muon_birth_covariance_sensitivity.py` and `theory/muon_birth_covariance_sensitivity_20261008.md`: normalized charged-CAR tangent, real Hilbert-Schmidt projection, ordinary ordering `N=I-C_plus`, exact moment-span definition, complete E1 assembly requirement, and moving-domain product rules. The source deliberately does not impose a fixed occupation or require the incoming tangent to commute with reset.
6. `artifacts/muon_birth_parametric_fermion_seam_20261008/lower_order_owner_receipt.json`: current incoming additive cotangent, beta/action-embedding guard, no C2 numerical transplant, unbound `H_C1` and consumed variation, and explicit need for same-domain response.

GitHub `fetch_file` returns normalized text. The cached CAR module has the receipt's raw SHA-256 `3abdd542942ee1bed36966e566e440e8f6466759e769612d99d1341abfe77890`. The foundational source is CRLF in the repository: the fetched LF text hash is `480058b9cd78bcc31306531c04485a4a8e2c789d201feed757dbc55c44dfdcc3`; restoring CRLF gives the receipt's raw hash `ad05ede643af517ded29823b6f5d3076ae64bc2e985ebf500ba48564ad8c8015`. No cache hash is silently substituted for a raw-source hash.

## Derivation from the owned action, with beta kept in its actual basis

The first step is the ordered bilinear in the action, not identification of unrelated `2 x 2` block labels. Suppress the fixed muon family projector and write the charged Weyl fields as two two-component spinors `chi_L,chi_R`. The retained local Yukawa quadratic is

\[
\mathcal L_H=-\chi_L^\dagger m_\mu\chi_R
              -\chi_R^\dagger\overline{m_\mu}\chi_L.
\]

This is the same local Lorentz scalar as the inherited `bar(L_L)Y_l H e_R+h.c.` term. In chiral coordinates, with `chi=(chi_L,chi_R)`, its Hermitian particle bilinear is

\[
B(m)=
\begin{pmatrix}
0&m I_2\\
\bar m I_2&0
\end{pmatrix}.
\]

For the actual Dirac gamma convention of the source,

\[
\beta_D=\gamma_D^0=
\begin{pmatrix}I_2&0\\0&-I_2\end{pmatrix},
\qquad
\gamma_{5,D}=i\gamma_D^0\gamma_D^1\gamma_D^2\gamma_D^3=
\begin{pmatrix}0&I_2\\I_2&0\end{pmatrix}.
\]

Chirality is the eigenspace decomposition of `gamma5`, not the two diagonal blocks of this Dirac-basis `gamma0`. The covariant mass coefficient is

\[
\mathcal M(m)=m P_R+\bar m P_L
            =\Re(m)I+i\Im(m)\gamma_5,
\]

and the Hermitian coefficient in the ordinary `chi^dagger (...) chi` action is

\[
\beta\mathcal M(m)=\Re(m)\beta+i\Im(m)\beta\gamma_5=B(m).
\]

An exact change of basis reproduces the chiral block written above. A common error would be to multiply the displayed Dirac-basis `gamma0` by a schematic off-diagonal LR mass without transforming or binding both to the same space. For a real coefficient this produces `beta_D gamma5_D`, which is anti-Hermitian and would disappear under Hermitianization. That is a basis/tensor-factor mistake, not an action-derived zero. The verifier explicitly guards against it. This note does not redefine the source's generic `beta M_LR` notation; it supplies a safe calculation directly from the retained physical bilinear and its actual spin basis.

Define `B_R=beta` and `B_I=i beta gamma5`. The Clifford relations imply

\[
B_R^\dagger=B_R,\quad B_I^\dagger=B_I,\quad
B_R^2=B_I^2=I_4,\quad \{B_R,B_I\}=0.
\]

Therefore `B(t)^2=|t|^2 I4`. Their real Hilbert-Schmidt Gram matrix is `4 I2`, so they are independent. These relations prove both the norm identity and the two-quadrature coefficient-rank formula without selecting a value of `m`.

## Incoming coefficient and variation that are actually consumed

For measure variation `b_alpha=delta_alpha log(mu)` and fixed orthonormal test-spinor frame,

\[
\delta_\alpha\big[-\mu\chi^\dagger B(m)\chi\big]
=-\mu\chi^\dagger B(b_\alpha m+\delta_\alpha m)\chi.
\]

Thus the useful incoming operand is the **combined** coefficient `t_alpha`, rather than separate loose upper bounds on `b`, `m`, and `delta m`. Keeping this combination allows genuine cancellation required by an owned variation to survive. When `Y_l` is expressed in the inherited fixed family basis,

\[
t_\alpha=y_\mu(b_\alpha h+\delta_\alpha h).
\]

If the consumed pullback moves the family representation or the Yukawa coefficient, use instead

\[
t_\alpha=b_\alpha y_\mu h+(\delta_\alpha y_\mu)h+y_\mu\delta_\alpha h,
\]

or its correctly projected matrix version. No `delta Y=0` is inserted merely because a numerical C2 `Y` was previously stored. Off-family or charged-Higgs terms can also enter through induced response even if a direct local compression removes them.

For a moving spin trivialization the additional local matrix terms are retained:

\[
\delta B(m)=B(\delta m)
+\Re(m)\delta\beta
+i\Im(m)\big[(\delta\beta)\gamma_5+\beta\delta\gamma_5\big].
\]

One can choose a fixed local orthonormal trivialization to compute the coefficient identity. That does not set the actual E1 frame, trace, density normalization or source response to zero. Their transformations must be booked in the full pullback.

## Charged-CAR projection and exact local non-annihilation criterion

The inherited charge operator on this particle module is `-I4`. Hence it commutes with both local quadratures. In self-dual space, charge is the separate particle/conjugate grading `diag(I4,-I4)`. The allowed family-supported affine tangent in canonical Gamma-swap coordinates is

\[
X=\operatorname{diag}(A,-\bar A),\qquad A=A^\dagger.
\]

The ordinary ordered convention is `N=I-C_plus`. For an action row with particle coefficient `A_H=-B(t)`, its covariance derivative is therefore

\[
\delta_C\operatorname{Tr}(A_HN)=\operatorname{Tr}(\delta C_+ B(t)).
\]

One valid representative on the doubled tangent is `Delta=diag(B(t),0)`. Applying the retained orthogonal projection gives

\[
S=\frac12\operatorname{diag}(B(t),-\bar B(t)),
\qquad \Re\operatorname{Tr}(X\Delta)=\operatorname{Tr}(A B(t)).
\]

The factor `1/2` is derived here from the projection of a specified ordinary ordered functional. It is not an extra quantum normalization factor attached to the original kinetic action. In a noncanonical compatible charge-conjugation basis the kernel and CAR structure transform together; the non-annihilation conclusion is unchanged.

If `t!=0`, take the allowed local affine direction `A=B(t)`. The pairing is `Tr(B(t)^2)=4|t|^2>0`. This is the exact local duality test. It does not select a physical covariance, prove a continuum Hadamard tangent, or assert that the complete E1 mismatch contains a nonzero residue after other terms are assembled. A same-sign artificial doubling `diag(B,+bar B)` would be Gamma-even and vanish, but it would represent a different functional on the retained tangent.

If supplied local rows have `t_alpha=a_alpha+i c_alpha`, then

\[
\dim_\mathbb R\operatorname{span}\{B(t_\alpha)\}
=\operatorname{rank}_\mathbb R\begin{pmatrix}a_1&c_1\\\vdots&\vdots\\a_N&c_N\end{pmatrix}.
\]

It is zero only if every `t_alpha=0`, one if all nonzero coefficients share a real line in the complex plane, and two otherwise. Choosing a gauge in which a base Higgs coefficient is real does not prove all its consumed derivatives are real or remove the compensating gauge/source derivatives.

## Boundary pullback, rank limitations and seam cancellation

If `T` is the owned map from common boundary data to the local field entering the quadratic, the direct contribution is `T^dagger B(m)T`. Its variation includes

\[
(\delta T)^\dagger B(m)T
+T^\dagger\delta B(m)T
+T^\dagger B(m)\delta T.
\]

The measure contribution combines with `delta B` to form the local `B(t)` term above. Fixed-map local integration would obey the sufficient bound

\[
\left\|\int T^\dagger B(t_\alpha)T\,d\mu\right\|
\le\int\|T\|^2|t_\alpha|\,d\mu,
\]

provided the actual measure, normalization and function spaces justify the integral. The moving-map terms have their own bounds. This can be a smaller target than constructing every entry of the full unprojected Higgs operator. No value for these maps, weighted integrals or domain norms is supplied by the present local algebra.

Even before response, different functions `t_alpha(rho)` multiplying the same two spin matrices can be linearly independent as operators. After solution, trace and domain maps act, additional matrix structures can also appear. Thus the local two-quadrature statement is not a uniform two-moment claim for the E1 problem.

An exact seam cancellation requires an action-matched identity for the corresponding pulled-back form. With `W_e+U_R^dagger W_c U_R=0` throughout the relevant variation family, differentiation gives cancellation only after including

\[
\delta W_e+(\delta U_R)^\dagger W_c U_R
+U_R^\dagger\delta W_c U_R
+U_R^\dagger W_c\delta U_R=0.
\]

A zero base mismatch alone does not imply this derivative identity. Family-central reset intertwining fixes the action of `Y` on the family factor, not the incoming Higgs coefficient, its geometry/source jet, or the moving domain pairing. The global Spin trace graph and existing zero Green/EM forms do not prove this separate LR identity. No new seam action is requested or inserted.

## Verification and deliverables

`car_reduction_verify.py` uses only exact Gaussian rational arithmetic from the Python standard library. It implements the pinned gamma convention, exact Dirac-to-chiral sandwiches without floating-point square roots, the full 16-element Hermitian local particle tangent basis, the correct ordered particle-to-CAR lift, charge compatibility, and the scalar quadrature Clifford identities. Testing the complete coefficient bases proves the stated linear/quadratic identities; these are not random floating-point witnesses.

The script reports **32 exact checks passed**. Its output was materialized twice with byte-identical results:

- First result: `car_reduction_verification.json`.
- Repeat: `car_reduction_verification_repeat.json`.
- Result SHA-256: `282990a7e112856bc5cec70613fbcac5f5890307589652f59091d8d13d798326`.
- Script SHA-256 at verification: `f19a2c807b406da09057f06710d734a1a336eaa7a621745e76252a8e2ffeb9c8`.

Replay: `python car_reduction_verify.py car_reduction_verification.json`.

The physical incoming `H_C1`, its consumed `t_alpha` and frame/source/domain response remain unbound. The complete E1 kernel, CAR verdict, minimal physical moment rank, `a_mu`, and `g_mu` remain unevaluated. The result is a concrete reduction of the incoming coefficient producer and a proof that chirality alone cannot be used as the missing annihilator.
