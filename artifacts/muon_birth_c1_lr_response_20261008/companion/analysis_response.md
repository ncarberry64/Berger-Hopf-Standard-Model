# Same-domain incoming LR response reduction: derived identities and new carrier bounds

Reference commit: `ad750077f1a3138418a2dc4ee65f7c50236b5608` in
`ncarberry64/Berger-Hopf-Standard-Model`. This is an intermediate mathematical
note, produced read-only with respect to the repository. The associated exact
arithmetic controls are `response_reduction_verify.py`; exact retained-decimal
bounds are replayed by `response_carrier_bounds.py`.

## Outcome and scope

There is a new numerical result beyond milestone 3: the retained one-channel
carrier supplies a uniform zero-trace interior Green bound and a uniform
boundary-to-bulk Poisson-extension bound. These yield a concrete sufficient
norm criterion and derivative majorant for a bounded perturbation of the SAME
quadratic form and domain. No physical member or covariance is selected.

The physical incoming perturbation is not supplied by this note. In particular,
the norm `v` below is the norm of the verified full-minus-carrier bulk form
operator in the normalized bulk L2 pairing. It is NOT automatically the norm
of the literal LR matrix `M_LR`; neither the common first-order embedding nor
the physical LR/trace-domain response is established by the algebra below.

The other new exact reduction is that the consumed DtN variation needs harmonic
extension/adjoint pairings, rather than all induced harmonic-solution jets.
Stationarity of an implicit scalar background removes its induced derivative
from the total first variation, but in general leaves a mixed-Hessian Schur
term in covariance sensitivity. There is an exact counterexample below.

## 1. Same-domain response identities, including non-Hermitian blocks

After the actual trace, measure and domain graph have been pulled to a common
reference realization, split boundary and zero-trace interior coordinates:

\[
L=\begin{pmatrix}D&C\\B&A\end{pmatrix},\qquad
\Lambda=D-CA^{-1}B.
\]

The hypotheses are that the indicated interior problem is invertible on the
owned domain, with any already-owned constraints included. If an interior KKT
block is required, use that block and its prescribed quotient; do not replace
a missing inverse by an arbitrary pseudoinverse. The identities need no
Hermitian symmetry. For continuum forms, the same products mean the bounded
solution/trace pairings in their appropriate function spaces.

Define the right and left harmonic extensions

\[
E_R=\binom{I}{-A^{-1}B},\qquad
E_L=\binom{I}{-A^{-\dagger}C^\dagger}.
\]

Then `L E_R=(Lambda,0)^T` and `E_L^dagger L=(Lambda,0)`. Direct differentiation
of the Schur complement gives the exact stationary variation

\[
\boxed{\delta\Lambda=E_L^\dagger(\delta L)E_R.}
\]

Indeed, its expansion is

\[
\delta D-(\delta C)A^{-1}B-CA^{-1}\delta B
+CA^{-1}(\delta A)A^{-1}B.
\]

It contains no induced derivative of the interior harmonic solution. For a
complete readout this does not remove external source, readout, normalization
or domain derivatives: they must already be included in `delta L` and in the
separate explicit source/readout terms.

Let `L_1=L_0+V` in this SAME realization. Since the left carrier extension
annihilates every zero-trace carrier variation, there is also the exact identity

\[
\boxed{\Lambda_1-\Lambda_0=E_{0,L}^\dagger V E_{1,R}.}
\]

Proof: `E_0,L^dagger L_1 E_1,R=Lambda_1`, while
`E_0,L^dagger L_0 E_1,R=Lambda_0`. Their difference is the displayed formula.
For self-adjoint forms the left and right extensions coincide. Replacing the
full extension on the right by its carrier value is only the first perturbative
term unless a remainder is also enclosed.

### Exact correction in carrier harmonic coordinates

Let `J` inject zero-trace interior coordinates and put

\[
W=E_{0,L}^\dagger V E_{0,R},\quad
V_{bi}=E_{0,L}^\dagger VJ,\quad
V_{ib}=J^\dagger V E_{0,R},\quad
V_{ii}=J^\dagger VJ.
\]

Changing to the left/right carrier harmonic coordinates diagonalizes the
carrier into `diag(Lambda_0,A_0)`. Hence

\[
\boxed{
R_\Sigma:=\Lambda_1-\Lambda_0
=W-V_{bi}(A_0+V_{ii})^{-1}V_{ib}.
}
\]

This expression needs only consumed form pairings and interior solves against
their sources. It does not require the inverse as a fully assembled matrix.
Finite internal species dimension alone does not make multiplication by a
spacetime-dependent Higgs field a finite-rank bulk operator.

## 2. Moving-domain derivatives and forced contacts

For actual left/right pullbacks `T_L(alpha),T_R(alpha)`, write

\[
\widetilde L=T_L^\dagger L_{\rm native}T_R.
\]

The derivative to use in the stationary identity is

\[
\delta\widetilde L=(\delta T_L)^\dagger L_{\rm native}T_R
+T_L^\dagger(\delta L_{\rm native})T_R
+T_L^\dagger L_{\rm native}\delta T_R.
\]

This is the finite-coordinate version of retaining moving trace, normalization,
pairing and domain terms. Pure interior coordinate changes can cancel in the
Schur response; moving boundary trace normalizations need not. The exact
control deliberately includes both, so it cannot pass by relying only on a
coordinate invariance that makes every transport term vanish.

For a supplied forced system `Lu=f`, the interior equation gives

\[
i=A^{-1}(f_i-Bb),\qquad
\Lambda b=f_{\rm eff},\qquad f_{\rm eff}=f_b-CA^{-1}f_i.
\]

With `r_i=A^{-1}f_i`, its complete derivative is

\[
\delta f_{\rm eff}=\delta f_b-(\delta C)r_i
-CA^{-1}(\delta f_i-(\delta A)r_i).
\]

Thus the same reduction explicitly retains returned/source contacts. Existing
response constraints and their multipliers can be included in the original
augmented system or booked separately exactly once. These formulas do not
license dropping `DJ`, multiplier derivatives or the separately consumed
integrated Hamiltonian row in the repository's complete E1 readout.

### Lifted action cotangent

For `F=Re Tr(G^dagger Lambda)`, using the real Hilbert-Schmidt pairing,

\[
\delta F=\operatorname{ReTr}\{(E_LGE_R^\dagger)^\dagger\delta L\}.
\]

For `F=Re Tr(G^dagger S^{-1})`, first form

\[
W_S=-S^{-\dagger}GS^{-\dagger},
\]

then lift `W_S` in place of `G`. An independently varying returned load adds its
own `Re Tr(W_S^dagger delta M_return)` contact. This makes the consumed scalar
readout computable from a finite list of action pairings and adjoint solves,
without all field-response jets.

## 3. New uniform interior and extension bounds from the retained carrier

The retained channel has, in the normalized proper-time bulk pairing,

\[
q_0[u]=\int_0^T\left(|(\partial_\tau+W)u|^2
+\kappa^2|u|^2\right)d\tau,\qquad |W|\le S.
\]

Here `T=a(lambda)lambda^2` is bounded by the existing duration theorem;
`z=-kappa^2` is its spectral probe. This section is confined to the existing
carrier and does not assert an additional LR operator embedding.

### Zero-trace interior inverse

For `u in H_0^1(0,T)`, Poincare and the reverse triangle inequality imply

\[
\|(\partial_\tau+W)u\|\ge(\pi/T-S)\|u\|.
\]

Using `pi>3` and `ST<3` gives

\[
\|G_{0,D}\|\le
\frac{T^2}{(3-ST)^2+\kappa^2T^2}.
\]

The right side increases with T while `ST<3`, so a uniform duration envelope
`T<=T_*` yields

\[
\boxed{d_*:=\frac{T_*^2}{(3-ST_*)^2+\kappa^2T_*^2}.}
\]

This is an interior zero-trace Green inverse, not the seam inverse from
milestone 3. No derivative of W is used.

### Boundary-to-bulk Poisson lift

Let `E_0 b=u_b` be the harmonic carrier solution with `u_b(0)=0,u_b(T)=b`.
It minimizes the positive form at those traces. The linear trial function
`u(tau)=(tau/T)b` therefore gives

\[
q_0[u_b]\le
\left[\frac1T+S+\frac{(S^2+\kappa^2)T}{3}\right]|b|^2.
\]

For functions vanishing only at the first endpoint, the one-end Poincare
inequality is `||u'|| >= pi/(2T)||u||`. Thus, for `ST<3/2`,

\[
\|E_0\|_{\text{boundary}\to L^2}^2\le
\frac{T[1+ST+(S^2+\kappa^2)T^2/3]}
{(3/2-ST)^2+\kappa^2T^2}.
\]

Dropping the positive final denominator term gives the monotone, rational
whole-family envelope

\[
\boxed{e_*^2:=
\frac{T_*[1+ST_*+(S^2+\kappa^2)T_*^2/3]}
{(3/2-ST_*)^2}.}
\]

The norm here is from the canonically normalized boundary data to the bulk
L2 function. It is not the Euclidean norm of a vector that counts boundary
coordinates as additional interior components; that norm would be at least 1.

### Exact retained inputs and outward results

The retained decimal inputs are read as exact rational numbers:

- `lambda_*=1.33025636847111862e-30`;
- original `a_upper=1051216787836407.6`;
- stored edge-duration upper `1.8602143121971425e-45`;
- lowest-channel `S=1.5076638829955453`;
- `kappa^2=1`.

Following milestone 3, use
`a_upper_eff=max(original_a_upper,T_edge_upper/lambda_*^2)` to retain the
additional original producer rounding, and `T_*=a_upper_eff lambda_*^2`.
This widens a uniform duration theorem; it does not select the edge as a
physical history. Here the resulting `T_*` equals the recorded edge upper.

Conservative short upper bounds are

\[
\begin{aligned}
d_*&\le3.844885874782\times10^{-91},\\
e_*^2&\le8.267619165321\times10^{-46},\\
b_*e_*^2&\le1.537954349913\times10^{-90},\\
d_*+b_*e_*^2&\le1.922442937391\times10^{-90},\\
b_*^2e_*^2&\le2.860924693214\times10^{-135}.
\end{aligned}
\]

`response_carrier_bounds.py` retains exact fractions and 80-significant-digit
outward decimal brackets. Its printed precision is exact arithmetic on the
inherited decimal bounds, not extra accuracy for their underlying source data.

## 4. A concrete conditional LR response and cotangent criterion

Suppose V has been VERIFIED as a bounded operator on the normalized proper-time
bulk L2 space, perturbing the SAME quadratic form and domain, with `||V||<=v`.
An arbitrary H1-relative form does not meet this assumption: first-order cross
terms such as `D^dagger E+E^dagger D` cannot be assigned the L2 multiplication
norm of E or of a mass matrix. The perturbation must act in the retained
channel, or in a verified closed sector covered by the same carrier bounds.
If it mixes additional spatial channels, those coupled channels need their
own joint baseline control before the one-channel numbers can be used.
Set `theta=d_* v`. If `theta<1`,
the full zero-trace inverse obeys

\[
\|G_1\|\le\frac{d_*}{1-d_*v}.
\]

The full harmonic extension is `E_1=E_0-G_1 V E_0`. In the self-adjoint carrier
pairing the exact boundary correction is

\[
R_\Sigma=E_0^\dagger V E_0-E_0^\dagger V G_1 V E_0.
\]

Consequently

\[
\boxed{\|R_\Sigma\|\le\frac{e_*^2v}{1-d_*v}},\qquad
\boxed{\|R_\Sigma-E_0^\dagger V E_0\|
\le\frac{e_*^2d_*v^2}{1-d_*v}}.
\]

For the retained positive seam with inverse bound b_*,

\[
\rho_{\rm rel}\le\frac{b_*e_*^2v}{1-d_*v}.
\]

A single sufficient condition ensuring the interior and seam inverses is

\[
\boxed{(d_*+b_*e_*^2)v<1.}
\]

The exact threshold evaluates to an interval beginning

\[
\frac1{d_*+b_*e_*^2}
=5.2017148626389565588543229219707876\ldots\times10^{89}.
\]

Thus the stricter short condition `v<5.201714862638e89` is sufficient on this
normalized scope IF v is an owned bound on the actual full-minus-carrier
perturbation. There is no physical value of v in this note. The very large
threshold is a consequence of the very short retained proper-time interval
and carries the units/norm of that form; it is not a particle mass threshold.

### Consumed LR directional insertion

For a verified pulled-back bounded LR insertion `delta_alpha V`, stationarity
and the extension bound give

\[
\|D\Lambda_1[\delta_\alpha V]\|
\le\frac{e_*^2\|\delta_\alpha V\|}{(1-d_*v)^2}.
\]

Combining with the seam inverse and simplifying the two denominators yields

\[
\boxed{
\|D S_{\rm total}^{-1}[\delta_\alpha V]\|
\le
\frac{b_*^2e_*^2\|\delta_\alpha V\|}
{[1-(d_*+b_*e_*^2)v]^2}.
}
\]

For the actual scalar solve readout this is multiplied by its actual source
and readout norms. The LR insertion is only one term in the full directional
action: other carrier, source, multiplier, returned-load and domain contacts
must still be included before assembling E1 and applying the frozen CAR map.

### Scaled family version

An unweighted uniform bound on V is stronger than necessary near lambda=0.
With `a=a_upper_eff`, `t_*=a lambda_*^2`, define

\[
D_c=\frac{a^2}{(3-St_*)^2},\quad
B_c=\frac{a}{1-4St_*},\quad
E_c=\frac{a[1+St_*+(S^2+\kappa^2)t_*^2/3]}{(3/2-St_*)^2}.
\]

Then `d(lambda)<=D_c lambda^4`, `b(lambda)<=B_c lambda^2`, and
`e(lambda)^2<=E_c lambda^2`. For
`v_hat=sup_lambda lambda^4||V(lambda)||`, the sufficient condition is

\[
(D_c+B_cE_c)\widehat v<1.
\]

Its conservative threshold begins

\[
\widehat v<1.6288756428353042415408384117500570\ldots\times10^{-30}.
\]

For a consumed derivative, the response prefactor scales as lambda^6. A
bound on `sup lambda^6||delta_alpha V||`, together with the scaled inverse
gap and actual source/readout factors, can therefore suffice even if the
unweighted derivative is not uniformly bounded. This is a viable whole-family
target; it does not force member selection.

### Companion criterion for a relatively bounded Hermitian form

There is a separate route when the perturbation is known as a Hermitian form,
and no bounded bulk-L2 operator representation has been established. Suppose
the actual common-domain forms satisfy

\[
q_1=q_0+r,\qquad |r[u]|\le\eta q_0[u],\qquad 0\le\eta<1,
\]

for ALL form-domain functions with u(0)=0, including functions with nonzero
terminal trace. The hypothesis only on zero-trace interior functions would
not suffice to control the boundary response. The variational characterizations
at fixed terminal trace then imply

\[
(1-\eta)M_0\preceq M_1\preceq(1+\eta)M_0.
\]

If the same nonnegative returned-child load is added to both, their seams obey

\[
S_1\succeq(1-\eta)S_0,\qquad
\boxed{\|S_1^{-1}\|\le b_*/(1-\eta).}
\]

This is a valid form-level alternative for derivative cross terms once their
same-domain action embedding and relative bound are actually verified. It
has no numerical eta in the currently supplied incoming data and does not
identify the unknown complete retarded AE4 block with this positive seam.

## 5. Scalar stationarity: precisely what cancels and what survives

Let `A(x,C,h)` be the TOTAL action after all actual pullbacks, with x a consumed
geometry/interface direction, C affine CAR coordinates and h scalar/background
variables. Suppose an already-owned stationary branch satisfies `A_h=0` and
the constrained scalar Hessian `H=A_hh` is invertible in the specified tangent
space. Define `F(x,C)=A(x,C,h_*(x,C))`.

The first-variation envelope identity is

\[
F_x=A_x.
\]

The cancellation is `A_h h_x=0` in the TOTAL action. The LR piece alone is
not stationary with respect to h, so dropping its scalar variation without
including the scalar action would be incorrect.

Differentiating with respect to C gives

\[
H h_C[X]+A_{hC}[X]=0,
\]

and hence

\[
\boxed{D_C F_x[X]=A_{xC}[X]-A_{xh}H^{-1}A_{hC}[X].}
\]

For a finite set of consumed x rows, solve only the adjoint equations

\[
H^\dagger z_x=A_{xh}^\dagger.
\]

The induced contribution is then `-<z_x,A_hC[X]>`. Equivalently, with
`B:X->A_hC[X]`, the CAR-dual correction is `-B^dagger z_x` before the complete
E1 kernel is projected. Only this inverse-Hessian contraction is needed; the
full collection of scalar response fields for every CAR variation need not
be reconstructed.

However, A_xC, A_xh, H and A_hC are still evaluated on the actual stationary
incoming background. The identity does not manufacture their numerical values
or an incoming Higgs profile. The supplied source audit does not establish
the necessary incoming scalar stationarity/Hessian. At a fixed supplied
uneliminated scalar background, the fixed-background derivative is A_xC;
that is a different calculation from the total on-shell covariance derivative.

### Exact counterexample to dropping the mixed scalar response

Take the control-only scalar action

\[
A(x,c,h)=\tfrac12(4+x)h^2-(1+2x+3c+5xc)h+7xc.
\]

The stationary scalar is `h_*=(1+2x+3c+5xc)/(4+x)` and

\[
F(x,c)=7xc-\frac{(1+2x+3c+5xc)^2}{2(4+x)}.
\]

At x=c=0, `h_*=1/4` and

\[
F_x=A_x=-15/32,\qquad
A_{xc}=23/4,\quad A_{xh}=-7/4,\quad A_{hc}=-3,\quad H=4.
\]

Therefore

\[
F_{xc}=23/4-21/16=71/16.
\]

The first-variation scalar cancellation holds exactly, while treating the
mixed response as the fixed-h value misses `21/16`. Thus stationarity alone
does not make the CAR sensitivity zero.

## 6. Verification and the next actual operand

`response_reduction_verify.py` uses only Python's standard library and exact
Fraction arithmetic. Independent forward-mode nilpotent jets differentiate
Gaussian elimination directly. All six controls pass:

1. Direct full-minus-carrier Schur response equals the extension pairing.
2. Direct response equals the carrier-coordinate Schur correction.
3. Direct differentiated elimination equals the complete pulled-back pairing;
   freezing the moving pullback instead gives a nonzero exact error.
4. Full forced-system boundary solution and its derivative equal their reduced
   forcing construction.
5. The scalar first envelope and mixed Schur derivative both agree exactly;
   the false mixed cancellation is rejected.
6. The directly differentiated inverse-seam readout equals the lifted adjoint
   plus the returned-load contact.

All intended residuals are exactly zero. The control matrices are real,
nonsymmetric and noncommuting. They verify the algebra rather than instantiate
any physical BHSM operator.

The useful next physical operand is now smaller and more explicit: bind the
incoming additive bridge to the common quadratic form/domain and obtain its
consumed form pairings or norm v plus directional insertion bounds. If the
background is implicit, supply the constrained mixed-Hessian contractions
needed by those same rows. The new carrier bounds already supply the interior
and lift factors for this calculation. No old carrier producer, continuum-tail
campaign or selected covariance is required by this reduction itself.

## Inspected primary sources

- `theory/muon_birth_parametric_fermion_seam_20261008.md`: retained carrier,
  response difference, cotangent and first incoming LR blocker.
- `artifacts/muon_birth_parametric_fermion_seam_20261008/lower_order_owner_receipt.json`:
  same-domain ownership, exact additive bridge, no C2 numeric transplant,
  conditional first-order embedding and minimal consumed projection.
- `theory/muon_birth_covariance_sensitivity_20261008.md`: complete E1 rows,
  moving domain graph, forced canonical derivative, CAR dual pairing, and
  requirement to include induced background derivatives when applicable.
- `src/bhsm/interface/ae31_c2_intrinsic_m4_lepton_action.py`: retained nonlinear
  Higgs action and sourced Euler equation; its evaluated saddle is current-C2
  and cannot be silently used as the incoming C1 background.
- `src/bhsm/interface/ae31_c2_full_scalar_derivative_pole.py`: universal scalar
  principal-pole information does not supply a finite incoming scalar Hessian.
- `src/bhsm/interface/muon_birth_parametric_carrier_bounds.py` and the two
  source JSONs named by `response_carrier_bounds.py`: exact retained-decimal
  envelope and scope reused for the new carrier estimates.

All paths above were read at the reference commit. An immutable source URL is
`https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/ad750077f1a3138418a2dc4ee65f7c50236b5608/`
followed by the corresponding path.
