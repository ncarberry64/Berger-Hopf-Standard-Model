# Selected-area seam variation and a nonzero Maxwell selection audit

This is a bounded derivation for the already selected regular-stratum action
`BHSM-AE-3.2.16-COVARIANT-BUBBLE-INTERFACE-MECHANICS`. It changes no action
coefficient, frozen result, physical primitive, or Gate-7 setting. It makes the
attachment-selection question executable before a coupled interface solve.

## 1. Variables and the precise partial-variation statement

Retain the two embeddings, attachment `F_B`, and nonfermion relation `L_s` of
`bhsm_owner_authorized_encapsulation_interface_action.md`. Work on one regular
timelike worldvolume `W` with spacelike unit normal and fixed corner data (or
compactly supported variations). On the selected constant environment stratum,

\[
S_\Sigma=-\int_W\gamma\,d\mu_h,\qquad
\gamma=\alpha_{\rm FSC}\ell^{-3}.
\]

The metric and embedding first variations are

\[
\delta S_\Sigma=-\frac12\int_W\gamma h^{ab}\delta h_{ab}\,d\mu_h,
\qquad
\delta_X S_\Sigma=\int_W\gamma H_\mu V^\mu\,d\mu_h
-\int_{\partial W}\gamma\nu_a e^a_\mu V^\mu\,d\mu_{\partial h}.
\]

Here `H` is the mean-curvature vector, and the ambient metric is fixed in the
second formula. It follows by substituting
`delta h_ab=2 e_(a . nabla_(b) V` and integrating by parts. If the scale or
ambient metric varies, their explicit variations must be retained too; this
audit does not set them to zero in the coupled problem. For `K=-n.H` and
`V=v n`, the surface normal coefficient is `-gamma K v`.

The area density contains no independent attachment, boundary-relation, or
gauge-trace variable. Thus its **direct partial derivatives**, holding the
induced geometry and scale fixed, satisfy

\[
(D_{F_B}S_\Sigma)_{h,\ell}=0,\qquad
(D_{L_s}S_\Sigma)_{h,\ell}=0,\qquad
(D_aS_\Sigma)_{h,\ell}=0.
\]

`L_s` is a domain relation in a Lagrangian Grassmannian; this is not a claim
that differentiating the full bulk action with a moving domain gives zero.
Likewise, when metric/trace compatibility ties `F_B` to the two embeddings,
their allowed variations are coupled. The chain rule and constraint forces
remain. The two embeddings have not been identified or independently solved.

Let `B_mu` denote the coefficient of the admitted shape variation from both
bulk actions and the already-owned boundary/corner terms. The projected shape
equation is `Pr_allowed(B+gamma H)=0`. Its normal component has the selected
surface contribution `B_n=gamma K`; no additional surface gauge source or
curvature-square coefficient is introduced.

## 2. Maxwell seam variation and the conditional relation

Take the already-owned local Maxwell sector, with its positive action
normalization left symbolic:

\[
S_M=-\frac{1}{4g^2}\int_M F_{\mu\nu}F^{\mu\nu}\,d\mu_g,
\qquad
\delta S_M=\frac1{g^2}\int_M\nabla_\mu F^{\mu\nu}\delta A_\nu\,d\mu_g
+\int_W p^a\delta a_a\,d\mu_h,
\quad p^a=-g^{-2}n_\mu F^{\mu a}.
\]

These signs use each region's outward normal; event and child normals are
opposite. Factoring out `g^(-2)` in the diagnostic is not a numerical coupling
selection. Normalization belongs in the physical canonical flux.

If the admissible trace space has already supplied
`a_e=C(F_B)a_c` modulo admitted gauge, then

\[
\delta a_e=C\,\delta a_c+D_FC[\eta]a_c,
\]

and the gauge part of the seam first variation becomes

\[
\langle p_c+C^*p_e,\delta a_c\rangle
+\langle p_e,D_FC[\eta]a_c\rangle.
\]

Consequently the gauge component of the selected source law is
`p_c+C^*p_e=0`, conditional on that trace domain. The area derivative is zero
in this component; its active normal geometric derivative remains nonzero.
For completely independent event/child gauge variations the natural
conditions instead are `p_e=p_c=0`. These are two different variational
domains. Their distinction shows what must be supplied by the existing
admissibility/compatibility construction; it does not prescribe a new choice.

For a supplied linear transport `C` on a finite, **already reduced** canonical
trace space, `q_e=C q_c`, `p_c=-C^T p_e` has free variables `(q_c,p_e)`.
The parameterization is injective, has half the product dimension, and the
sum of the two outward-normal Green forms pulls back to zero. This proves
the conditional Lagrangian graph lemma. It does not construct the physical
Gauss/BRST reduction or choose the physical `L_s`.

## 3. Attachment work cannot be omitted

For connection transport, the attachment variation contains the Cartan term

\[
\mathcal L_\eta a=\iota_\eta f+d(\iota_\eta a),\qquad f=da.
\]

After pullback to common coordinates, tangential integration by parts gives

\[
\int_Wp^a\mathcal L_\eta a_a
=\int_Wp^af_{ba}\eta^b
-\int_W(D_ap^a)(\iota_\eta a)
+\text{corner}.
\]

In the source-free Maxwell subproblem, Gauss reduction and fixed corners
remove the last two terms. The first remains. With all geometry and other
terms held fixed and **arbitrary independent admissible** relative-map
variations, its stationarity equation would be `f_ba p^a=0`. The actual BHSM
equation must also include its other-sector, shape, environment, and
admissibility-constraint contributions, and use only the allowed variations.
It cannot be replaced with this isolated condition without proving that
those terms vanish and that the variations really are independent.

This is why the zero direct area derivative is not a general obstruction to
attachment selection. It also explains why a rank calculation alone is not
enough: the traces must first lie on the full stationary constraint surface.

## 4. Exact local Lorentz selection witness, with a stationarity check

Freeze a common orthonormal seam metric `h=diag(-1,1,1)`. Suppose metric
compatibility has restricted a candidate relative attachment differential to
`SO^+(1,2)`. This is a pointwise differential subproblem around a known
matching, not an assumption that the physical map is the identity. Write

\[
B=\begin{pmatrix}0&a&b\\a&0&c\\b&-c&0\end{pmatrix},\qquad
f=\begin{pmatrix}0&1&0\\-1&0&0\\0&0&0\end{pmatrix}.
\]

The same-orientation lowered canonical flux `e=h p` transforms as a covector.
More explicitly, for `Q=D F_B`, child momentum density transported to event
coordinates is `|det Q| Q^(-1)p_c`. Outward flux balance gives
`e_e+Q^T e_c=0` for proper Lorentz `Q`. At a known matched reference
`e_c=-e_e`, preserving the matching is therefore `Q^T e=e`.

The linearized equations are

\[
\delta f=B^Tf+fB=
\begin{pmatrix}0&0&c\\0&0&-b\\-c&b&0\end{pmatrix},
\qquad \delta e=B^Te.
\]

| Exact trace input | Rank in `(a,b,c)` | Kernel dimension | Isolated Maxwell free-map work |
| --- | ---: | ---: | --- |
| `f=0`, `e=0` | 0 | 3 | zero |
| displayed `f`, `e=0` | 2 | 1 | zero |
| displayed `f`, `e=(0,0,1)` | 2 | 1 | zero |
| displayed `f`, `e=(0,2,0)` | 3 | 0 | `(2,0,0)` |

For the last row, residual ordering `(df01,df02,df12,de0,de1,de2)` gives

\[
J=\begin{pmatrix}
0&0&0\\0&0&1\\0&-1&0\\2&0&0\\0&0&0\\0&0&2
\end{pmatrix}.
\]

Its minor using `df02,df12,de0` has determinant `2`. All ranks and kernels
are computed over exact rationals, with no numerical tolerance.

The full-rank traces are realized by the nonzero source-free field
`A=(t-2z)dx`, `F=dt wedge dx-2 dz wedge dx` in Minkowski space at `z=0`,
with event normal `+dz`. The factored lowered event canonical flux is
`(0,2,0)` and `F_munu F^(munu)/2=3`. **This field is not claimed to solve
the coupled membrane problem:** its isolated map-work coefficient is
`(2,0,0)`, so the full stationary problem needs additional coupled terms or
restrictions. The artifact retains this failed isolated stationarity test.

For this fixed nonzero `f`, isolated free-map stationarity forces
`e_0=e_1=0`, precisely the alignment that leaves the boost `a` unresolved.
This is a restricted diagnostic, not a general nonexistence theorem. The
actual allowed map directions, other fields, embedding coupling, and
boundary constraints are still unevaluated.

A finite countercheck uses the nonidentity reference differential

\[
Q_0=\begin{pmatrix}5/3&4/3&0\\4/3&5/3&0\\0&0&1\end{pmatrix}.
\]

It preserves the metric and `f`, but sends `(0,2,0)` to `(8/3,10/3,0)`.
Assigning identity when the known reference is `Q_0` passes the curvature
check and fails the flux check. A zero-field or curvature-only identity test
therefore cannot establish complete Maxwell transport.

## 5. What this contributes and what comes next

Validated: the selected surface first variation; conditional Maxwell seam
and cotangent-graph relations; the surviving attachment-work term; and exact
algebraic rank witnesses with their isolated stationarity residuals.

Invalidated: promoting a zero direct area derivative to a zero total
attachment equation; selecting a trace domain from area density alone;
using curvature-only matching or pointwise rank as physical attachment proof.

Open: the action-owned admissible seam/embedding domain; the complete
reduced stationarity Jacobian evaluated on physical nonzero traces; and the
coupled interface IVP, unique simple first crossing, induced global map,
spin/bundle transport, and full reset domains. Constant illustrative fields
do not select translations, map integrability, or global topology. No
physical `F_B`, `L_s`, carrier, or new N12 rank is earned here.

The next concrete object is
`ACTION_OWNED_ADMISSIBLE_SEAM_DOMAIN_AND_COMPLETE_REDUCED_STATIONARITY_JACOBIAN_ON_NONZERO_PHYSICAL_TRACES`.
This is a necessary local input to the previously named coupled IVP, not a
new constitutive function or a replacement for that theorem.

## Reproduction

Run `python scripts/materialize_covariant_interface_seam_selection.py` twice
and compare the generated bytes. Run
`python -m pytest tests/test_covariant_interface_seam_selection.py`.
The artifact records the selected source, derivation, implementation,
materializer, and test hashes. Empirical comparisons are absent: these are
exact mathematical diagnostics, not fitted physical predictions.
