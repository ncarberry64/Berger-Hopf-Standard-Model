# BHSM muon: action-weight and horizontal-transport continuation

**Author/project:** Norman P. Carberry — Berger–Hopf Standard Model  
**Date:** 2 October 2026  
**Scientific reference:** `524ed90689bd5923c249bba2e699abf627e703cd`  
**Inspected publication head:** `0b02a8ddce780b97b03899410a857d9370d962d7`, PR #465  
**New checkpoint:** `BHSM_PRECURSOR_HORIZONTAL_PAIRING_AND_EQUIVARIANCE_20261002`

## Executive result

This continues the preceding normalized Hopf-frame calculation rather than repeating it. That calculation established the geometric identity

\[
Z_g=(Au,Bv)^T/\sqrt{A^2+B^2},\qquad Z_g^\dagger dZ_g=\omega_{\rm mech}.
\]

It did not identify the frame with a physical precursor/muon state. The present work obtains three further results:

1. Differentiating the retained local eta density shows that its common factor `Lambda*(1+X_eta^3)` does not supply the unequal two-orbit weighting needed by that geometric frame. The precise required weight ratio in the minimal two-block ansatz is derived and evaluated at the published cut. This is not a new coefficient to add to the theory.
2. The historical charged-middle vertical Dirac seed has representation `(3,5/2)`. Neither separate left nor right fiber action contains a weak doublet. However, their **different diagonal Spin(4) subgroup does contain an exact two-dimensional channel**. Its 42-by-2 Clebsch–Gordan isometry and projected generators are computed exactly. This subgroup must not be confused with the original free principal Sp(1) action. A physical weak identification is not established.
3. The needed connection can be recovered from the horizontal kinetic-overlap matrix and its metric, without constructing a complete physical wavefunction. Canonical normalization fixes the metric part but does not determine the anti-Hermitian horizontal transport.

Six targeted exact checks passed. Two final executions produced six byte-identical output files. No native heat, exterior solution, physical muon state or Pauli coefficient was evaluated. All frozen local contributions are unchanged.

## 1. Inputs and evidence boundary

The previous packet's consumed report, checkpoint, receipt and scalar/representation snapshot were checked against its SHA-256 manifest without rerunning its 27 checks. The new calculation reads a selected-equation snapshot of five pinned GitHub source files:

- `aether_sobolev_galerkin_pencil_lift_v15_81.py::generalized_lagrangian`;
- `aether_diagonal_fiber_dirac_lift_v15_55.py`;
- `particle_chirality_anomaly_normalization.py::MODE_LEDGERS`;
- `aether_hybrid_standard_model_bundle_v15_53.py`;
- `completion/foundational_dirac_spin_glue_v14_45.py`.

Paths, connector-reported Git blob identities and the exact consumed expressions are in `inputs/retained_equations.json`. These are **equation transcriptions**, not raw repository snapshots. The repository itself and full NPZ arrays were not mounted or replayed. A direct binary retrieval attempt was unsuccessful; no binary-array verification is claimed.

The only numerical geometry input is the published binary64 scalar `lambda=0.5066207222913062`, carried unchanged from the preceding packet. The older unmatched angular matrices accompanying that scalar are not used. The historical radial eta-knot/collar profile is not transplanted into the current `f=chi` join.

## 2. Differentiated local eta action

The retained local density includes

\[
\mathcal L_\eta=-N\mathcal V\Lambda F(X),\qquad
F(X)=X/2+X^4/8,
\]

with the round target norm, `f=chi`, and a background normal velocity in the f direction. Write `c=cos f`, `s=sin f`. At one fixed point, take the independent target-orientation velocity increments `xi_u,xi_v` in the two imaginary-quaternion directions. They obey

\[
\|\delta v_\eta\|^2=c^2|\xi_u|^2+s^2|\xi_v|^2,
\qquad
\langle v_{\eta,0},\delta v_\eta\rangle=0.
\]

The second equality follows because the background f derivative has real radial components in each quaternion, whereas orientation generators are imaginary. Thus

\[
X=X_0-c^2|\xi_u|^2-s^2|\xi_v|^2
\]

for this local velocity differentiation. Direct symbolic differentiation gives

\[
\boxed{
\partial^2_{\xi}\mathcal L_\eta\big|_0
=N\mathcal V\Lambda(1+X_0^3)
\operatorname{diag}(c^2I_3,s^2I_3).
}
\]

The normal-velocity convention is used; conversion to coordinate velocities supplies the common lapse factors and does not change the relative orbit weights. The potential `F''` rank-one correction is absent on these directions because of the displayed orthogonality.

**Scope:** this is the local scalar term at fixed geometry and localization, extended to the stated target tangent directions. It is not an evaluation of the full constrained collective kinetic metric, the nonlocal Hopf-inertia term, a constraint-eliminated action, or the physical fermion Hilbert pairing. Those additions can matter. The calculation only rules out claiming that this *common scalar factor by itself* supplies the geometric dressing.

## 3. The precise minimal-frame weight condition

For positive block weights `g_u,g_v`, consider the minimal normalized frame

\[
Z_G={1\over\sqrt{g_u\cos^2f+g_v\sin^2f}}
\binom{\sqrt{g_u}\cos f\,u}{\sqrt{g_v}\sin f\,v}.
\]

With the ordinary flat ambient derivative after this normalization, its connection is

\[
Z_G^\dagger dZ_G=\lambda_G\theta_u+(1-\lambda_G)\theta_v,
\qquad
\lambda_G={g_u\cos^2f\over g_u\cos^2f+g_v\sin^2f}.
\]

Matching `lambda_G=A²/(A²+B²)` requires

\[
\boxed{g_u/g_v=(A^2/B^2)\tan^2f.}
\]

The actual retained ansatz is

\[
A=R e^{u+v}\cos\chi,\quad B=R e^{u-v}\sin\chi,\quad f=\chi,
\]

so the condition simplifies exactly to

\[
\boxed{g_u/g_v=e^{4v}.}
\]

At the material cut `f=pi/4`, the required ratio is exactly

\[
{\lambda\over1-\lambda}
={1140808448064649\over1110991365620599}
\in[1.026838266584902033505612694756,
1.026838266584902033505612694757].
\]

This is a rigorous arithmetic enclosure at the published scalar, not an uncertainty interval for the true physical state. The ratio is **not** a fitted coupling, a proposed addition to the action, or a muon correction. It describes what the minimal two-block construction would need.

Important limitation: a general metric-compatible ambient connection may have a nonzero skew part. Such a part can also contribute to `Z†nabla Z`. Therefore the ratio above is not a universal requirement on every physical realization of the mechanical background. In particular it must not become a new completion gate. The physical transport, not just an auxiliary metric, must be derived from the retained matter action.

## 4. Bare vertical modes and the weak representation

The retained v15.55 seed assigns

\[
V_k^+\simeq V_{(k+1)/2}\otimes V_{k/2},\qquad
V_k^-\simeq V_{k/2}\otimes V_{(k+1)/2}
\]

under the left/right isometry factors of one internal round S3. The charged-middle ledger is `(k,q)=(5,2)`, for both `L_L.lower` and `e_c.singlet`. Hence its positive seed is `(3,5/2)`, of dimension 42.

These are historical internal spectral seeds, not established current physical muon states. The physical representation ledger separately calls for a weak doublet for `L_L` and a weak singlet for `e_c`.

### 4.1 What the separate left/right actions cannot do

Use anti-Hermitian generators `G_a=-2i J_a`, so

\[
[G_a,G_b]=2\epsilon_{abc}G_c,\qquad -\sum_aG_a^2=4j(j+1)I.
\]

An equivariant injection `T` of a fundamental doublet would require `G_a T=T t_a` with `t_a=-i sigma_a`, whose Casimir is 3. The k5 separate factors have Casimirs 48 and 35, so no nonzero such injection exists. They likewise contain no invariant singlet.

The replay computes the exact positive normal operator on Hom matrices, defined by

\[
\langle\operatorname{vec}T,\mathscr L\operatorname{vec}T\rangle
=\sum_a\|G_a T-Tt_a\|_F^2.
\]

Its spectra are:

| Parent factor | Exact Hom-Laplacian eigenvalues | Nullity |
|---|---|---:|
| j=5/2 to doublet | 24 (multiplicity 5), 48 (multiplicity 7) | 0 |
| j=3 to doublet | 35 (multiplicity 6), 63 (multiplicity 8) | 0 |

These are representation obstructions, not physical instability or missing-particle conclusions. A separately attached internal weak factor is not excluded. Replacing the weak generators by a convenient corner of a larger angular momentum matrix is not an equivariant substitute.

### 4.2 A different subgroup does have an exact doublet

The diagonal subgroup of the *fiber's* left/right Spin(4) factors has

\[
V_3\otimes V_{5/2}=V_{1/2}\oplus V_{3/2}\oplus\cdots\oplus V_{11/2}.
\]

An exact isometry is

\[
T_{(m_L,m_R),m}=\langle3m_L,\tfrac52m_R\mid\tfrac12m\rangle.
\]

All 84 entries of this 42-by-2 matrix are saved as exact algebraic strings. The replay directly verifies

\[
T^\dagger T=I_2,\qquad
(G_{L,a}+G_{R,a})T=Tt_a.
\]

It also evaluates

\[
\boxed{T^\dagger G_{L,a}T={8\over3}t_a,\qquad
T^\dagger G_{R,a}T=-{5\over3}t_a.}
\]

For general k in this minimal diagonal channel, the coefficients are `(k+3)/3` and `-k/3`; their sum is one. Thus a fixed Clebsch frame projects a two-factor connection to

\[
B_{\rm proj}=[\tfrac{k+3}{3}\omega_L-\tfrac{k}{3}\omega_R]^a t_a.
\]

These coefficients are **not** asserted to be BHSM weak couplings. They are exact projections in the historical internal representation. Equal left and right connection coefficients yield the fundamental diagonal connection, but the actual action has not been shown to supply that equality.

The complement is explicit. Put `R_L=(I-TT†)G_LT`, and similarly for R. Then

\[
R_L+R_R=0,\qquad \sum_aR_{L,a}^\dagger R_{L,a}={80\over3}I_2.
\]

Only the total diagonal generator preserves this subspace. A connection acting on one factor alone couples it to the complement. The full diagonal decomposition also has no singlet, so it is not a complete derivation of both chiral weak assignments for a muon.

### 4.3 Do not confuse two uses of “diagonal”

The retained mechanical principal action on `S3_u x S3_v` is simultaneous **right** multiplication `(u,v)->(u q,v q)` and is free. The diagonal subgroup of the left/right isometries of a **single** S3 fiber acts by conjugation `q->h q h^-1`, has fixed points, and is not free. They are not identified merely by both being called Sp(1) or diagonal.

Consequently, the newly constructed doublet is a useful candidate representation channel, not the missing physical bundle identification. It may instead be related to internal spin/frame transport. Assigning it weak charge requires the actual action-preserving attachment, with spin, internal gauge and family factors distinguished.

## 5. The smaller horizontal-overlap calculation

A complete microscopic precursor wavefunction is not mandatory. Let E be an available, not necessarily orthonormal, frame of the **physically identified** precursor/parent states, with owned fiber/wall metric M. Define

\[
G=E^\dagger ME,\qquad
K_\alpha=E^\dagger M\nabla_{{\rm parent},\alpha}E.
\]

After pulling to a common domain with compatible metric transport,

\[
K_\alpha+K_\alpha^\dagger=\partial_\alpha G.
\]

Choose a normalizer S with `S†GS=I`. The induced connection is

\[
\boxed{B_\alpha=S^\dagger K_\alpha S+
S^\dagger G\partial_\alpha S.}
\]

Subtract the base-spin connection once on the correct factor. This formula is verified with a nonorthogonal, varying frame and a noncommuting connection. The test is algebraic, not a constructed physical state.

The metric G fixes only the Hermitian part of K. Its anti-Hermitian part is the remaining horizontal transport information. Neither Gram normalization, the unit collar overlap, the precursor's pointwise value, nor the vertical eigenvalues determine it.

The existing independent16 child-test Gram is not automatically this physical precursor Gram. Use it only after the action identifies the injection or after an equivalent contracted coefficient is established.

### Same-source first variation

For the retained photon variation, differentiate the complete expression:

\[
\begin{split}
\delta B={}&\delta S^\dagger KS+S^\dagger\delta K S+S^\dagger K\delta S\\
&+\delta S^\dagger G\partial S+S^\dagger\delta G\partial S
+S^\dagger G\partial\delta S.
\end{split}
\]

Additional moving-domain terms belong in the compatible pullback. When a Hermitian `S=G^{-1/2}` is used, its derivative can be obtained through a Sylvester solve for `H=G^{1/2}`: `H deltaH+deltaH H=deltaG`, `deltaS=-S deltaH S`. No full second-jet tensor is demanded if directional contractions suffice.

Keep the independent electromagnetic fluctuation `Q=T3+Y`. Its hypercharge action on weak singlets is not generated by varying a two-component Hopf shape. A Berry/background representation must not silently change the already-frozen source.

## 6. One next physical operand and stopping point

**`ACTION_OWNED_CURRENT_LEPTON_HORIZONTAL_KINETIC_OVERLAP_FIRST_JET`**:

The matrix `K_alpha,rs=<E_r,nabla_parent,alpha E_s>_owned`, with its normalization/metric and required photon-source first variation, or the equivalent already-normalized internal Clifford contraction on the existing source space. Its producer is the retained effective fermion action and physical associated-bundle/collective-mode attachment; its consumer is `A_hor^(0)` and the source jet of the current M5/M4 Dirac operator.

This is the same unresolved connection-preserving attachment, now constrained by explicit action and representation calculations. It is not a demand to replace the v14.45 adopted effective fermion action with an ab initio bosonic-to-Grassmann theory. A direct valid principal-bundle connection identity can supply the answer without constructing E, S, or the full Clebsch channel.

The inspected sources do not provide the actual horizontal matrix element or an equation selecting the diagonal channel as the physical weak factor. Therefore the new matrices cannot be inserted into the physical native operator. Further physical progress needs that retained attachment, not a chosen block weight or generator that merely reproduces the expected representation.

All native ledger entries remain null; `strong_within_native` is a subset, not a new addend. No physical `a_mu`, `g_mu`, exterior return, finite-E1 response, or shifted resolvent was obtained. The existing local QED/Higgs/weak interval is preserved verbatim in the checkpoint.

## 7. Reproduction and verification

Run with Python 3.10+ and SymPy:

```text
python replay_transport.py --output fresh_replay
```

Six exact targeted checks cover the local eta Hessian, minimal dressing condition, nonorthogonal normalization/overlap identity, k5 separate-factor obstruction, complement identities, and the exact diagonal doublet.

The first development execution left a true exponential identity unsimplified under `trigsimp`; replacing it with general `simplify` resolved the software assertion without changing the equation. That development note and an intermediate five-check result are retained. Two final six-check executions agree byte-for-byte. The `run_1` and `run_2` result, matrix, input, check and missing-operand files are final; the `development_run_5checks` directory is historical.

Only exact algebra and arithmetic on the previously published cut scalar were executed. Zero prior BHSM production runs, zero full NPZ input arrays, zero physical source-response solves, and zero physical soft-transfer directions were used.

## References for conventions and retained sources

The exact repository paths, revisions and reported source identities are in `inputs/retained_equations.json`. The previous report and checkpoint are included under `prior_evidence`; historical source notes are copied under `sources`. NIST DLMF §§34.1–34.2 document the Clebsch–Gordan/3j phase and triangle conventions used by the matrix construction. The projected coefficients, no-intertwiner tests, and action-local identities are calculated explicitly in the replay rather than accepted from a literature formula.
