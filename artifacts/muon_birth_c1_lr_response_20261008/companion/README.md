# BHSM incoming C1 LR/Higgs reduction — 8 October 2026

## Result

This continuation derives and evaluates new uniform carrier interior and boundary-to-bulk bounds. It also reduces the missing incoming LR/Higgs calculation to same-domain action pairings, a local complex coefficient, and a scalar adjoint contraction.

The numerical incoming Higgs restriction and its response have not been obtained. The complete E1 kernel, complete CAR verdict, physical minimal moment rank, and physical muon magnetic moment remain unevaluated. No physical carrier amplitude, duration, covariance, or reset representative was selected.

The work is based on commit **ad750077f1a3138418a2dc4ee65f7c50236b5608** in Norman Carberry's Berger-Hopf-Standard-Model repository, the reported milestone 3 of [PR #465](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/pull/465). This package is a standalone derivation and verification companion.

## 1. New evaluated carrier bounds

All numbers below retain the lowest product channel, absolute unit-radius eigenvalue \(3/2\), the negative-axis probe \(z=-1\), and the family

\[
0<\lambda\le1.33025636847111862\times10^{-30}.
\]

The probe is the retained mathematical resolvent probe. No identification with physical muon momentum is made.

The source gives \(T(\lambda)=a(\lambda)\lambda^2\) and the carrier

\[
A_0=\partial_\tau+W,\qquad \|W\|_\infty\le S,
\qquad
q_0[u]=\|A_0u\|_{L^2}^2+\kappa_{\rm probe}^2\|u\|_{L^2}^2.
\]

Here \(S=1.5076638829955453\), \(\kappa_{\rm probe}^2=1\), and the retained duration envelope is \(T_*=1.8602143121971425\times10^{-45}\). The coefficient envelope includes the original theorem endpoint and the extra rounded edge-duration value. Using that endpoint as an upper bound does not select it as a physical history.

### Interior inverse

For zero trace at both ends, the Poincare inequality gives
\(\|u'\|_2\ge\pi\|u\|_2/T\). Hence, when \(ST<3\),

\[
\|A_0u\|_2\ge(3/T-S)\|u\|_2,
\]

where replacing \(\pi\) by 3 is conservative. Therefore the zero-trace interior inverse has the uniform bound

\[
\boxed{
\|G_{0,D}\|\le d_*=
\frac{T_*^2}{(3-ST_*)^2+\kappa_{\rm probe}^2T_*^2}.
}
\]

This is a new interior Green-operator bound. It is a different operator from the seam inverse and from the active-Higgs response.

### Boundary-to-bulk lift

Let \(E_0\xi\) be the carrier harmonic extension with \(u(0)=0\) and \(u(T)=\xi\), in the inherited normalized endpoint pairing. The one-end Poincare inequality gives \(\|u'\|_2\ge\pi\|u\|_2/(2T)\). Combining it with the retained linear-trial energy estimate gives

\[
\boxed{
\|E_0\|_{\partial\to L^2}^2\le e_*^2=
\frac{T_*[1+ST_*+(S^2+\kappa_{\rm probe}^2)T_*^2/3]}
{(3/2-ST_*)^2}.
}
\]

The positive probe term was dropped from this denominator to obtain a conservative monotone envelope. The condition \(ST_*<3/2\) is satisfied. This norm counts the bulk proper-time \(L^2\) field; it does not count the endpoint value as another Euclidean coordinate.

With the inherited seam inverse bound \(b_*=T_*/(1-4ST_*)\), exact rational evaluation gives the following outward upper bounds:

| Quantity | Conservative upper bound |
|---|---:|
| Interior inverse \(d_*\) | \(3.844885874782\times10^{-91}\) |
| Lift norm squared \(e_*^2\) | \(8.267619165321\times10^{-46}\) |
| \(b_*e_*^2\) | \(1.537954349913\times10^{-90}\) |
| \(c_*=d_*+b_*e_*^2\) | \(1.922442937391\times10^{-90}\) |
| Inverse-seam insertion prefactor \(b_*^2e_*^2\) | \(2.860924693214\times10^{-135}\) |

The exact fractions and outward decimal brackets are in the replay output. Extra arithmetic digits are not a stronger physical uncertainty claim than the inherited source bounds.

## 2. What these bounds permit for an actual LR contribution

Suppose the actual difference \(V=L_1-L_0\) has been verified to be a bounded operator on the normalized bulk \(L^2\) space, on the same quadratic-form and trace domain, and in the retained channel or a separately controlled closed coupled sector. Write \(\|V\|\le v\).

This assumption is substantive. A raw first-order mass coefficient is not automatically \(V\), which here has the units of the quadratic carrier operator. Squaring a first-order perturbation generally produces derivative cross terms that are not bounded on \(L^2\). Arbitrary relatively bounded \(H^1\) forms require the separate form criterion below.

If \(d_*v<1\), the exact same-domain extension and response identities give

\[
E_1=(I+G_{0,D}V)^{-1}E_0,
\]

\[
R_\Sigma=\Lambda_1-\Lambda_0=E_0^\dagger VE_1,
\]

and thus

\[
\|R_\Sigma\|\le\frac{e_*^2v}{1-d_*v}.
\]

The error after keeping only the carrier-extension pairing is bounded by

\[
\left\|R_\Sigma-E_0^\dagger VE_0\right\|
\le
\frac{e_*^2d_*v^2}{1-d_*v}.
\]

For the seam, one sufficient condition combines the interior and boundary requirements:

\[
\boxed{c_*v=(d_*+b_*e_*^2)v<1.}
\]

It yields

\[
\boxed{
\|S_{\rm full}^{-1}\|
\le
\frac{b_*(1-d_*v)}{1-c_*v}.
}
\]

The exact threshold \(1/c_*\) begins

\[
5.2017148626389565588543229219707876\ldots\times10^{89}.
\]

This is a threshold in the retained quadratic-operator units, not a particle mass in GeV. There is no physical value of \(v\) in this package. For a non-Hermitian perturbation the result proves invertibility; it does not assert positivity of the full operator.

For a bounded LR directional insertion, with the remaining base and domain contributions accounted for separately in the full directional derivative,

\[
\boxed{
\|D S_{\rm full}^{-1}[\delta_\alpha V]\|
\le
\frac{b_*^2e_*^2\|\delta_\alpha V\|}
{(1-c_*v)^2}.
}
\]

The actual readout and source norms must also be included in an observable contraction. The \(10^{-135}\) prefactor alone is not the size of a physical correction.

### Keep the amplitude weights

The construction gives \(d(\lambda)\le c_D\lambda^4\),
\(b(\lambda)\le c_b\lambda^2\), and
\(e(\lambda)^2\le c_E\lambda^2\).
Therefore a sufficient condition can be imposed directly on

\[
\widehat v=\sup_\lambda \lambda^4\|V(\lambda)\|.
\]

Its exact sufficient threshold is

\[
\boxed{
\widehat v<
1.6288756428353042415408384117500570\ldots\times10^{-30}.
}
\]

For an insertion, the corresponding response prefactor scales as \(\lambda^6\). This preserves shared amplitude dependence and can avoid demanding a finite unweighted bound on an intermediate that grows toward the excluded \(\lambda=0\) endpoint. No actual Higgs scaling law is inferred.

### When the perturbation is only form-relative

For a Hermitian perturbation \(r\), a different sufficient hypothesis is

\[
|r[u]|\le\eta q_0[u],\qquad \eta<1,
\]

for every form-domain vector with \(u(0)=0\), including vectors with nonzero terminal trace. Variational comparison then gives

\[
(1-\eta)M_0\preceq M_1\preceq(1+\eta)M_0,
\qquad
\|S_1^{-1}\|\le \frac{b_*}{1-\eta}
\]

with the same positive child load. A bound only on zero-trace interior vectors is insufficient for this particular boundary comparison. No numerical physical \(\eta\) is supplied.

## 3. Exact response reduction

The missing response can be computed through consumed pairings, without first constructing every entry of a full lower-order boundary matrix.

For a verified common quadratic realization, split boundary and interior coordinates:

\[
L=\begin{pmatrix}D&C\\B&A\end{pmatrix},
\qquad
\Lambda=D-CA^{-1}B.
\]

Use the right and left harmonic extensions

\[
E_R=\binom{I}{-A^{-1}B},
\qquad
E_L=\binom{I}{-A^{-\dagger}C^\dagger}.
\]

Then

\[
\boxed{\delta\Lambda=E_L^\dagger(\delta L)E_R}
\]

and

\[
\boxed{\Lambda_1-\Lambda_0=E_{0,L}^\dagger(L_1-L_0)E_{1,R}.}
\]

These identities also hold for nonsymmetric operators. Their proof uses the zero interior residual of the extensions. Induced harmonic-solution derivatives cancel, while explicit action, source, trace and domain derivatives remain.

In carrier harmonic coordinates the correction is exactly

\[
R_\Sigma=W_c-V_{bi}(A_0+V_{ii})^{-1}V_{ib},
\]

where \(W_c=E_{0,L}^\dagger V E_{0,R}\), and the other \(V\) blocks are the corresponding carrier/interior pairings. The second term is a real interior-response correction; it cannot be discarded merely because the first term is easy to evaluate.

A moving pullback has

\[
\widetilde L=T_L^\dagger L T_R,
\]

\[
\delta\widetilde L
=
(\delta T_L)^\dagger L T_R
+
T_L^\dagger(\delta L)T_R
+
T_L^\dagger L\,\delta T_R.
\]

All three terms belong in the response identity. The appendix also gives the reduced forced-source term and its derivative, including the terms used by the E1 source and multiplier rows.

This algebra does not establish the missing physical incoming embedding. It specifies a smaller exact calculation once that embedding is supplied.

## 4. The local LR coefficient that actually matters

Starting directly from the retained charged-lepton bilinear avoids confusion between chirality and particle/conjugate-charge doubling.

At one point in a fixed orthonormal spin frame, after the fixed muon family restriction, let \(m_\mu=y_\mu h\), where \(h\) is the Higgs component in the charged-lepton gauge contraction. Its value remains symbolic. The measure-plus-coefficient variation consumes

\[
\boxed{
t_\alpha=b_\alpha m_\mu+\delta_\alpha m_\mu,
\qquad b_\alpha=\delta_\alpha\log\mu.
}
\]

The combination should be retained before taking absolute values. It can contain cancellations that separate bounds on \(b_\alpha\), \(m_\mu\), and \(\delta m_\mu\) would lose.

In the actual Dirac gamma convention, the Hermitian particle bilinear is

\[
B(t)=\operatorname{Re}(t)\beta+
\operatorname{Im}(t)i\beta\gamma_5,
\]

with

\[
\boxed{B(t)^2=|t|^2I_4,\qquad \|B(t)\|=|t|.}
\]

The real and imaginary matrices anticommute and each squares to the identity. Frame, family-representation, source, trace and domain variations remain outside this fixed-frame local simplification and must be included in the complete pullback.

The existing charge operator has the same electric charge on both charged chiral components. Thus the LR term is within a particle charge block. With the inherited ordering \(N=I-C_+\), its local covariance derivative has representative

\[
S(t)=\frac12\operatorname{diag}(B(t),-\overline{B(t)}).
\]

On the retained local affine tangent, \(S(t)=0\) if and only if \(t=0\). For example, the allowed local direction \(A=B(t)\) pairs to \(4|t|^2\). No covariance is selected.

This is a local non-annihilation criterion, not a nonzero verdict for the complete E1 mismatch. Other assembled terms can cancel it. At a fixed point/frame the local coefficient span is at most two real dimensions; different coefficient functions over the collar and their response maps can generate a larger operator span. The physical E1 moment rank remains unevaluated.

## 5. Active-Higgs response and the minimal scalar input

The retained active-Higgs Euler equation is

\[
F_H=-D^2H-2\kappa_H(H^\dagger H-\nu^2)H-J=0,
\qquad J=\bar e_RY_\ell^\dagger L_L.
\]

The quartic coefficient \(\kappa_H\) is distinct from the carrier amplitude \(\lambda\) and from the resolvent probe \(\kappa_{\rm probe}\).

Set \(s=H^\dagger H\) and \(h_\alpha=\delta_\alpha H\). The scalar Jacobi operator is real-linear:

\[
\mathcal L_H h
=
-D^2h
-
2\kappa_H\left[(s-\nu^2)h+
(H^\dagger h+h^\dagger H)H\right].
\]

Differentiating the retained equation gives

\[
\boxed{
\mathcal L_Hh_\alpha
=
(\delta_\alpha D^2)H+\delta_\alpha J
+
2(\delta_\alpha\kappa_H)(s-\nu^2)H
-
2\kappa_H\delta_\alpha(\nu^2)H.
}
\]

The conjugate variation is essential. Coefficient variations can be set to zero only where the direction owner fixes them. If the source has already been evaluated self-consistently, move \(D_HJ[h_\alpha]\) into the operator and retain the fixed-\(H\) source variation on the right. Other induced fields and constraints belong in the compatible coupled response.

The actual scalar boundary or Cauchy graph is also needed. For a supplied action-owned trace map \(T_H\),

\[
\Gamma_cH_c=T_H\Gamma_eH_e
\]

implies

\[
\Gamma_ch_c-T_H\Gamma_eh_e
=
(\delta T_H)\Gamma_eH_e+
T_H(\delta\Gamma_e)H_e-
(\delta\Gamma_c)H_c.
\]

This inhomogeneous boundary forcing cannot be replaced by a fixed-field homogeneous graph. The carrier reference \(u(E0)=0\) is not an active-Higgs boundary condition.

Bundle the actual scalar, boundary and constraint equations as
\(\mathcal A_Hh_\alpha=f_\alpha\). For the consumed real-linear functional
\(\ell_\alpha(h)\), one compatible adjoint solve gives

\[
\mathcal A_H^*p_\alpha=\ell_\alpha,
\qquad
\boxed{\ell_\alpha(h_\alpha)=\langle p_\alpha,f_\alpha\rangle.}
\]

This avoids reconstructing every scalar variation. Its scalar boundary multipliers remain in the contraction. The small carrier inverse is not a bound for \(\mathcal A_H^{-1}\).

### Why the stored geometric scalar bound does not fill this input

The inspected incoming compact scalar potential is
\(-D_\tau^2+c e^{-2x}\). The geometric action producer propagates geometric harmonic coordinates and includes a free conformal Casimir term. Those calculations do not supply the active \(H^\dagger H\) background, the Higgs quartic energy, or the incoming scalar source and Cauchy data. The source audit in the scalar appendix records the exact functions and paths. This is a bounded conclusion about the inspected producers, not an exhaustive absence claim.

The normal overlap is already identically one and its normalized variation is zero. It introduces no new Yukawa normalization. The intrinsic Higgs and moving-domain derivatives remain.

### Stationarity does not erase the mixed E1 response

For a fully supplied stationary scalar branch, the total action obeys the first-derivative envelope identity \(F_x=A_x\). Its covariance/geometry mixed derivative can nevertheless contain

\[
F_{xC}
=
A_{xC}-A_{xh}A_{hh}^{-1}A_{hC},
\]

or the appropriate constrained version. The supplied exact control demonstrates a nonzero omitted response even when the first envelope identity holds. Thus scalar stationarity alone cannot establish a zero complete CAR kernel.

## 6. What remains unevaluated

The next physical calculation is the actual same-C1 active-Higgs source/domain restriction and its contraction into the retained LR response:

1. The incoming \(H\) source functional and its consumed variation, including induced coupled-field terms when applicable.
2. The incoming scalar trace/Cauchy/reset relation and its moving-domain variation.
3. The action-correct embedding of the additive LR contribution into the boundary-response realization; an \(L^2\) or relative-form enclosure on its actual controlled sector.
4. The resulting consumed LR action/adjoint pairings and the other required E1 contacts.

A direct enclosure of the final consumed contraction can replace a reconstruction of the full scalar field and all matrix entries. Physical-member selection has not been proved necessary. Once the complete E1 kernel is available, the existing CAR projection and real moment-span calculation can be used. No missing physical entry has been assigned zero in this continuation.

## 7. Verification and reproduction

The package requires only Python's standard library. All finite controls use exact rational or Gaussian-rational arithmetic. It includes:

- Six independent block-elimination, moving-domain, source and mixed-response controls.
- Thirty-two local gamma/LR/CAR coefficient checks, including the complete 16-element local Hermitian particle tangent basis.
- Five scalar Jacobi and boundary-adjoint controls.
- Exact rational evaluation of the new carrier bounds, with directed decimal rounding and a check against the pinned source inputs.
- A manifest of forty-three source files checked at the pinned commit by Git blob SHA-1 and local SHA-256. Repository source files remain available at their immutable GitHub links.

Run from the extracted folder:

    python verify_all.py --out replay

On Norman's recorded Windows Python installation, the equivalent invocation is:

    & C:\Python314\python.exe .\verify_all.py --out replay

To also repeat the pinned repository-source check, add --source-root followed by the path to the repository at the cited commit. For the previously reported Windows worktree:

    & C:\Python314\python.exe .\verify_all.py --source-root "C:\Users\carbe\Downloads\BHSM_muon_parent_maxwell_worktree_20261001" --out replay

The included run_1 and run_2 directories contain the two deterministic materializations made with the source check enabled. The verification receipt records their comparison and hashes. These controls verify the stated mathematical identities and arithmetic, not a physical Higgs solution, a continuum tail, a completed CAR verdict or an experimental prediction.

The previous repository-wide milestone tests and five publication audits were not rerun for this standalone package. This continuation does not claim a new repository publication or alter the inherited physical completion flags.

## Files and provenance

- analysis_response.md: full response identities, numerical bounds, scaled criterion and form-relative alternative.
- analysis_car.md: physical-bilinear local reduction, charge/CAR proof, and basis-convention guard.
- analysis_scalar.md: incoming active-Higgs equation, source/domain audit and scalar adjoint.
- carrier_bounds_independent_audit.md: independent proof and scope review of the new bounds.
- response_carrier_bounds.py: exact new numerical bounds.
- response_reduction_verify.py, car_reduction_verify.py, scalar_reduction_verify.py: exact controls.
- pinned_source_manifest.json: immutable source identities and content hashes. The source_snapshot paths in the derivation notes refer to the inspected source cache; the corresponding files can be read at the pinned GitHub commit.
- run_1/results.json and run_2/results.json: full deterministic results.
- verification.json: replay comparison and scope.

Primary source entry points are the pinned [milestone-3 report](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/ad750077f1a3138418a2dc4ee65f7c50236b5608/theory/muon_birth_parametric_fermion_seam_20261008.md), [carrier-bound code](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/ad750077f1a3138418a2dc4ee65f7c50236b5608/src/bhsm/interface/muon_birth_parametric_carrier_bounds.py), [active-Higgs action](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/ad750077f1a3138418a2dc4ee65f7c50236b5608/src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py), and [complete CAR criterion](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/ad750077f1a3138418a2dc4ee65f7c50236b5608/theory/muon_birth_covariance_sensitivity_20261008.md).
