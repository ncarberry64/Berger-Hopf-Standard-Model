# BHSM continuation: scalar inverse construction and reference-sensitivity certificates

Norman Carberry research continuation — 16 October 2026

**Pinned scientific source:** PR #465, `b6cb15f5ab6f6b44057f13895c5fd498ce928d83`.
The connected repository was read again; its head was unchanged at this revision.

**Result:** a new, explicit scalar-dependent first-order **trial** operator; an
exact local kinetic match; coefficient and curvature/boundary discrepancies of
its heat expansion; sharp finite-CAR sensitivity certificates; a full-density
extension that does not assume a quasifree sea; and an implicit second-variation
remainder formula. These are not a completed native operator or physical muon
contraction. No physical covariance, statistical carrier, coupling, cutoff,
prediction, or repository file was selected or changed.

## 1. Source-defined problem and what is new

The retained scalar target, in the fixed-metric Riemannian comparison chart, is

\[
S_{\rm scalar}=\int d\mu\left[
\frac{Z_\chi}{2}(1+g\sigma^2)|d\chi|^2+
\frac{b}{2}|d\sigma|^2+\frac{A_0}{2}\sigma^2+\frac{G_0}{4}\sigma^4\right],
\qquad b=Z_\sigma.
\]

Its coefficients come from `src/bhsm/interface/master_action/terms.py`, not an
experimental fit. That registry does not supply the full microscopic reduction
maps. The native owner is

\[
\Gamma_{\rm ind}=-\tfrac12\operatorname{STr}E_1(\ell^2P),
\qquad F_p=-\ell^{-p}/p\quad(p>0),
\]

with the existing relative zeta/eta, quotient, domain, and support completion.
The cutoff is the adopted birth-side resistance/inertia functional; it is not an
adjustable parameter for fitting this construction. The current report does not
select the full internal twisting/statistics or inherited covariance.

The preceding package constructed a conditional closed positive domain and
factored the **response Hessian**. Here the new scalar map instead enters an
unsquared first-order operator, so its generating heat coefficients can be
computed and compared with the target. This is an **inverse construction**:
it uses the retained kinetic coefficients to build a mathematical test map.
It does not derive those coefficients, the existence of an appropriate physical
internal carrier, or the full BHSM action from independent microscopic data.

No stationary-ground-state prescription is adopted. The new state analysis
asks what information the complete observable actually consumes, without
choosing the primordial sea or replacing the exact prepared pair density.

## 2. An explicit scalar-dependent first-order trial operator

### 2.1 Scope and carrier

Use a local smooth Riemannian eight-dimensional spin chart. For this construction
only, assume \(Z_\chi>0,b>0,g>0\). This does not establish that every relevant
BHSM branch has these signs. The cases \(g=0\) and \(g<0\) are not limits that may
silently be taken in the formulas containing \(g^{-1/2}\).

Take four Hermitian internal Clifford matrices \(\tau_a\),

\[
\{\tau_a,\tau_b\}=2\delta_{ab}I,
\qquad\langle\tau_a\tau_b\rangle=\delta_{ab},
\]

where angle brackets denote the internal trace divided by its dimension.
A complex four-dimensional representation is explicit in the code. Tensoring
it with Spin16 is **a trial mathematical carrier**, not identification of new
particles, the existing physical gauge representation, or native statistics.
Compatibility with the frozen gauge algebra and its commutant is not established.

Let \(K_\ell>0\) denote the coefficient multiplying the normalized scalar
kinetic trace in this trial sector. With effective negative statistical weight
\(-\nu\) under the owner's supertrace convention,

\[
K_\ell=\frac{\nu}{8(4\pi)^4\ell^4}.
\]

The positive number \(\nu\) records the actual weighted spin/internal
multiplicity of an admitted realization; this calculation does not select it.
In particular, it is not spin chirality and is not adjusted to fit the target.
A scalar sector with a different signed measure must be recomputed accordingly.

Define

\[
t=\frac{b}{2K_\ell},\qquad
\omega^2=\frac{Z_\chi g}{b},\qquad\theta=\omega\chi,
\]

and the Hermitian endomorphism

\[
\boxed{\mathcal M(\chi,\sigma)=\sqrt t\left[
\sigma(\cos\theta\,\tau_1+\sin\theta\,\tau_2)
+g^{-1/2}(\cos\theta\,\tau_3+\sin\theta\,\tau_4)\right].}
\]

Use

\[
\boxed{D_{\rm trial}=i\gamma^A\nabla_A+\gamma_*\mathcal M.}
\]

This is first order in the section acted upon; it is not a square of the
second-order scalar Jacobi operator. A legitimate global continuation, closure,
and action domain are still needed. The previous closed-form construction
applies only after those data are supplied. The trial has no claimed
interacting two-collar or M8-to-M5/M4 realization.

### 2.2 Exact local kinetic correspondence

The Clifford relations give

\[
\mathcal M^2=q_s I,\qquad q_s=t(\sigma^2+g^{-1}),
\]

and

\[
\langle(d\mathcal M)^2\rangle
=t\,|d\sigma|^2+t\omega^2(\sigma^2+g^{-1})|d\chi|^2.
\]

There is no mixed \(d\sigma\cdot d\chi\) term. Consequently

\[
\boxed{
K_\ell\langle(d\mathcal M)^2\rangle
=\frac b2|d\sigma|^2+
\frac{Z_\chi}{2}(1+g\sigma^2)|d\chi|^2.}
\]

This is an exact identity on the stated local field chart at fixed \(\ell\).
It reproduces the curved scalar kinetic metric, not just its value at one
background. Its fixed-metric/fixed-cutoff variations consequently agree with
the target kinetic variations. The scalar potential and the rest of the action
still require separate matching.

A constant shift of \(\chi\) rotates both Clifford planes by a constant unitary
conjugation, preserving \(q_s\) and its traced powers. This realizes a local
shift-invariant potential without inserting a \(\chi\)-dependent scalar mass.
The map is periodic in \(\chi\); its global use would require the correct
field topology/identifications. No compactification of Norman's field is inferred.
A local frame rotation also changes the connection and must not be used to
remove \(\chi\) while deleting that induced connection.

## 3. Test the generating heat expansion instead of assuming correspondence

### 3.1 Standard heat coefficients, specialized here

For the bulk Laplace convention \(P=-(\nabla^2+E)\), the standard integrated
coefficients contain

\[
a_2=(4\pi)^{-4}\int d\mu\,\operatorname{tr}(E+R/6),
\]

\[
a_4=(4\pi)^{-4}\int d\mu\,\operatorname{tr}
\left[\tfrac12E^2+\tfrac16RE+\tfrac16\Box E
+\tfrac1{12}\Omega_{AB}\Omega^{AB}+\text{pure metric terms}\right].
\]

These are the smooth bulk formulas in Vassilevich, equations (4.27)–(4.28).
His Dirac convention has \(E=-R/4\) in the untwisted geometric sector.
For the trial operator, the scalar additions produce

\[
\Delta a_2\propto-\langle\mathcal M^2\rangle,
\]

\[
\Delta a_4\propto
\tfrac12\langle(d\mathcal M)^2\rangle+
\tfrac12\langle\mathcal M^4\rangle+
\tfrac1{12}R\langle\mathcal M^2\rangle-
\tfrac16\Box\langle\mathcal M^2\rangle.
\]

The \(R\mathcal M^2\) coefficient follows directly from
\(\tfrac12(-R/4-\mathcal M^2)^2+R(-R/4-\mathcal M^2)/6\): its cross
coefficient is \(1/4-1/6=1/12\). No curvature term is supplied by fitting.

Multiplying by the actual native moments \(F_6,F_4\) gives the trial scalar
part of the **a2+a4 heat-order truncation**:

\[
\boxed{\mathcal L_{\rm trial,2+4}=
K_\ell\left[\langle(d\mathcal M)^2\rangle+q_s^2
-\frac{4}{3\ell^2}q_s+\frac R6q_s-\frac13\Box q_s\right].}
\]

Pure metric terms and the a0 constant are not displayed, not set to zero.
The \(\Box q_s\) term is a bulk divergence at fixed cutoff; its boundary
flux must be combined with the actual domain/interface heat terms. It cannot
be dropped in the stratified problem just because it drops out of a compactly
supported interior comparison.

The expressions are not a convergent evaluation of \(E_1\). Higher heat
coefficients, relative completion, and the physical cutoff can contribute at
fixed physical scales. In particular, heat order and number of spacetime
derivatives are different gradings: a6 can also contain potentials and
field-dependent two-derivative terms. No higher-order remainder bound is claimed.

### 3.2 Coefficient equations

The flat interior potential of this truncation is

\[
V_{\rm trial}=K_\ell\left[t^2(\sigma^2+g^{-1})^2
-\frac{4t}{3\ell^2}(\sigma^2+g^{-1})\right].
\]

Matching its quadratic and quartic pieces requires

\[
\boxed{G_0=\frac{b^2}{K_\ell}},\qquad
\boxed{A_0=\frac{G_0}{g}-\frac{4b}{3\ell^2}}.
\]

These are **constraints on this candidate at this truncation**, not predictions
of BHSM already established by the source. They cannot determine a freely
chosen \(\ell\), because the cutoff owner has already been specified.
The vacuum constant also needs matching to the actual volume term; it is not
silently subtracted to make the equations succeed.

### 3.3 An explicit curvature and boundary discrepancy

The same calculation produces

\[
\boxed{\Delta\mathcal L_R=\frac b{12}\sigma^2R+\frac b{12g}R,}
\qquad
\boxed{\Delta\mathcal L_{\rm div}=-\frac b6\Box\sigma^2.}
\]

The constant curvature contribution can be compared with the total Einstein
coefficient. The field-dependent \(\sigma^2R\) term is not present in the
retained minimal S8 density. Thus the simple trial sector is not a full match,
even when its potential coefficient relations happen to hold.

This discrepancy changes actual equations. For example,

\[
\frac{\delta\Delta S_R}{\delta\sigma}
=\sqrt G\,\frac b6 R\sigma,
\]

while variation of the \(\sigma^2R\) part with respect to the inverse metric
contains

\[
\frac b{12}\sqrt G\left[
\sigma^2(R_{AB}-\tfrac12G_{AB}R)
+(G_{AB}\Box-\nabla_A\nabla_B)\sigma^2\right].
\]

Therefore setting \(R=0\) at one background does **not** generally remove the
metric/source discrepancy for a nonconstant scalar. The flux of the displayed
divergence is \(-b\,n\cdot d(\sigma^2)/6\); this is not by itself the complete
interface heat coefficient or a replacement for the existing two-trace law.

A full realization could change this comparison through its actual coupled
carrier, endomorphism/connection, geometric field map, statistics, cutoff, or
relative completion. None of those cancellations has been demonstrated here.
Adding an arbitrary compensating \(-b\sigma^2R/12\) term would change the action
and is not performed. The discrepancy restricts this trial construction, not
all possible BHSM constructions.

### 3.4 Source and cutoff motion remain explicit

At fixed retained coefficients and multiplicity, this inverse map scales as
\(\mathcal M=\ell^2\mathcal A(\chi,\sigma)\). Consequently

\[
\delta\mathcal M=(\delta\mathcal M)_{\ell\,\mathrm{fixed}}
+2\frac{\delta\ell}{\ell}\mathcal M.
\]

Writing fixed-cutoff local jets as \(L_h,L_k,L_{hk}\), the mixed jet is

\[
\delta_{hk}\mathcal M=L_{hk}
+2\frac{\ell_h}{\ell}L_k+2\frac{\ell_k}{\ell}L_h
+\left(2\frac{\ell_{hk}}{\ell}
+2\frac{\ell_h\ell_k}{\ell^2}\right)\mathcal M.
\]

These are conditional trial-map derivatives, not evaluated action-owned birth
jets. If the actual retained coefficients also vary, their jets must be added.
Matching at one frozen \(\ell\) is not matching the complete branch derivative.
No change is made to the original fixed-adjoint analytic source convention.

## 4. Turn inherited-reference dependence into a precise operator certificate

### 4.1 Complete solved-variable derivative

Let \(y\) contain all solved physical variables on the constrained quotient:
background, interface/history variables, unit calibration, physical modes,
pole/residue normalizations, and any quantities that move at fixed physical
preparation. Include the scale equation
\(G_F e^{2e}-c_F[y,C]=0\) and the moving chart-packet conditions where required.
Do not freeze \(e\) or a chart packet that represents a fixed physical beam.

Write the complete equations and readout as

\[
\mathcal R(y,C)=0,\qquad a=a(y,C),\qquad J=\mathcal R_y.
\]

Assume an admitted differentiable branch and an invertible constrained \(J\).
For an admissible covariance direction \(X\),

\[
y'[X]=-J^{-1}\mathcal R_C[X],\qquad J^*\lambda=a_y^*.
\]

The prior adjoint identity becomes an effective Hermitian kernel when its
trace representation exists:

\[
\boxed{D_Ca_{\rm solved}[X]=\operatorname{Re}\operatorname{Tr}(M_{\rm eff}X),}
\qquad M_{\rm eff}=a_C^*-\mathcal R_C^*\lambda.
\]

This is the **complete** kernel, including the background's response. It is not
the fixed-background kernel and not the retarded propagator. The following
new projection makes its relevant component precise.

### 4.2 Exact self-dual CAR projection

On a finite normalized Cauchy chart let \(\mathcal J\) be the CAR antiunitary,
\(\mathcal J^2=I\). Admissible covariances satisfy

\[
C=C^\dagger,\quad0\le C\le I,\quad C+\mathcal JC\mathcal J=I.
\]

Their real linear difference space consists of Hermitian \(X\) with
\(\mathcal JX\mathcal J=-X\). Replace \(M_{\rm eff}\) by its Hermitian part and
set

\[
\boxed{M_-=\tfrac12(M_{\rm eff}-\mathcal JM_{\rm eff}\mathcal J).}
\]

Then

\[
\boxed{\operatorname{Re}\operatorname{Tr}(M_{\rm eff}X)
=\operatorname{Tr}(M_-X).}
\]

**Proof:** conjugation by \(\mathcal J\) is an involutive orthogonal map on the
real space of Hermitian matrices under \(\operatorname{Re}\operatorname{Tr}(AB)\).
Its even and odd eigenspaces are orthogonal. The covariance direction is odd.
Thus the even part of the kernel cannot affect that direction.

At an interior mixed covariance, \(M_-=0\) is necessary and sufficient for
vanishing on all unconstrained self-dual first-order directions. If exact
charges or other linear expectations are fixed, project further onto their
allowed difference space. Equivalently, a kernel in the span of those fixed
constraint normals is insensitive to their allowed variations. No such
additional charges or population restrictions are invented here.

### 4.3 A sharp finite affine interval without selecting a state

For a genuinely affine readout \(F(C)=\operatorname{Tr}(M C)\), on the full
finite CAR covariance set,

\[
\boxed{F(C)\in\left[\tfrac12\operatorname{Tr}M-\tfrac12\|M_-\|_1,
\ \tfrac12\operatorname{Tr}M+\tfrac12\|M_-\|_1\right].}
\]

This interval is sharp. The finite optimization witnesses are

\[
C_\pm=\tfrac12(I\pm\operatorname{sign}M_-),
\]

with occupation \(1/2\) on the zero eigenspace. They satisfy CAR because
\(\mathcal JM_-\mathcal J=-M_-\), and hence the sign is also odd. The largest
and smallest trace pairings are \(\pm\|M_-\|_1/2\) about the center.
These covariances are mathematical extremizers, **not** proposed primordial
references. Zero-mode handling in this finite covariance optimization is not
a choice of the physical Dirac frequency polarization.

Around a specified \(C_0\), the affine approximation to the complete readout has
center

\[
a_0+\operatorname{Tr}\big[M_-(I/2-C_0)\big]
\]

and radius \(\|M_-\|_1/2\). For a nonlinear solved readout this is a tangent
interval, not an error bar until the following remainder is controlled.

### 4.4 Pure-state tangents do not test all inherited occupation changes

At a pure projector \(C\), pure-orbit tangents additionally obey
\(CX+XC=X\), so only

\[
M_{\rm pure}=CM_-(I-C)+(I-C)M_-C
\]

is tested. The diagonal/occupation part can be nonzero even when this vanishes.
The code gives an exact diagonal example with zero pure-tangent response but
nonzero affine range over mixed covariances. Thus a pure-state rotation check
cannot be used to establish independence from an unspecified inherited mixture.

## 5. Remove the hidden quasifree assumption when higher products matter

The current source requires exact higher current products and explicitly does
not turn the prepared pair mixture into a quasifree sea. Accordingly the CAR
certificate above has a stated scope: it controls the dependence represented
by \(C\), not arbitrary higher connected correlations.

There is a direct extension. Use the actual regulated many-body density
\(\rho\) on the physical sector instead of only its covariance:

\[
\mathcal R(y,\rho)=0,\qquad
\boxed{K_{\rm eff}=a_\rho^*-\mathcal R_\rho^*\lambda},\qquad
D_\rho a_{\rm solved}[\delta\rho]
=\operatorname{Tr}(K_{\rm eff}\delta\rho).
\]

After projection to the allowed superselection blocks, the full finite-density
affine range is the spectral interval

\[
\boxed{[\lambda_{\min}(K_{\rm phys}),\lambda_{\max}(K_{\rm phys})].}
\]

A scalar multiple of the identity on the allowed sector is invisible to
trace-zero density variations. If sector weights are fixed, a separate scalar
on each block is invisible; if weights can vary, unequal block scalars are
observable. Additional fixed linear expectations require the corresponding
constrained optimization, not this unrestricted spectral interval.

### Exact counterexample with the same particle number

On four complex fermion modes define

\[
\rho_A=\tfrac12|1100\rangle\langle1100|
+\tfrac12|0011\rangle\langle0011|,
\]

\[
\rho_B=\tfrac12|1010\rangle\langle1010|
+\tfrac12|0101\rangle\langle0101|.
\]

Both densities are positive, normalized, even, and supported entirely in the
**same exact two-particle sector**. Every normal and anomalous quadratic
covariance agrees. Nevertheless,

\[
\boxed{\langle n_1n_2\rangle_A=\tfrac12,
\qquad\langle n_1n_2\rangle_B=0.}
\]

The code verifies all the quadratic identities and this quartic difference
with exact rational arithmetic. These are not proposed BHSM states; they
prove that equality or cancellation at the covariance level alone cannot
establish independence of a higher-current readout. A derivation that higher
cumulants are absent at the requested order, or the full-density certificate,
is needed wherever this dependence survives.

## 6. A finite-family remainder formula, not just a derivative at one point

Along an admitted straight reference path \(C(s)=C_0+sX\), let
\(v(s)=y'(s)=-J(s)^{-1}\mathcal R_C(s)[X]\). Then

\[
y''=-J^{-1}\left(\mathcal R_{yy}[v,v]
+2\mathcal R_{yC}[v,X]+\mathcal R_{CC}[X,X]\right).
\]

Substituting the same complete adjoint gives

\[
\boxed{\begin{aligned}
\frac{d^2a_{\rm solved}}{ds^2}={}&a_{yy}[v,v]+2a_{yC}[v,X]+a_{CC}[X,X]\\
&-\langle\lambda,\mathcal R_{yy}[v,v]
+2\mathcal R_{yC}[v,X]+\mathcal R_{CC}[X,X]\rangle.
\end{aligned}}
\]

Equivalently it is the Hessian of \(a-\langle\lambda,\mathcal R\rangle\) on the
direction \((v,X)\), holding the adjoint fixed at each evaluation point.
The same formula holds with \(\rho\) in place of \(C\).

An actual bound \(H_X\ge\sup_{0\le s\le1}|a''(s)|\) yields

\[
\boxed{|a(C_0+X)-a(C_0)-\operatorname{Tr}(M_{-,0}X)|\le H_X/2.}
\]

Invertibility, branch existence, domain regularity, and fixed-preparation
conditions must hold along the path. Neither an isolated inverse nor a small
kernel at its starting point supplies this uniform bound.

### Exact nonlinear control

Take the constructed scalar implicit problem

\[
\mathcal R(y,C)=y+y^3-\operatorname{Tr}(BC)=0,
\quad B=\operatorname{diag}(1,-1),\quad a=y^2.
\]

At \(C_0=I/2,y_0=0\), the **complete** first-order state kernel is zero. At
\(C_1=\operatorname{diag}(13/16,3/16)\), the exact solution is \(y_1=1/2\),
so \(a_1-a_0=1/4\). The branch is regular since \(J=1+3y^2>0\).
For \(\beta=\operatorname{Tr}(BX)\),

\[
a''=\frac{2(1-3y^2)\beta^2}{(1+3y^2)^3},\qquad |a''|\le2\beta^2.
\]

The resulting remainder bound is \(\beta^2=25/64\), which covers the exact
change \(1/4\). This control proves why even complete first-order cancellation
at one base is not a finite-family independence certificate.

## 7. Transport only the kernel consumed by the observable

For a fixed admitted history, an inherited perturbation is
\(X(t)=U(t,t_0)X_0U(t,t_0)^\dagger\). A sensitivity with endpoint, history,
and reset terms can be pulled back to the initial reference:

\[
M_{\rm seed}=U(T,t_0)^\dagger M_TU(T,t_0)
+\int_{t_0}^T U(t,t_0)^\dagger M_tU(t,t_0)\,dt
+\sum_rU_r^\dagger M_rU_r.
\]

Here the kernels must already include the complete direct-minus-adjoint
background contribution; the \(U_r\) include the actual unitary resets.
Motion of the history/reset maps is represented in the solved-variable
linearization, not omitted or counted twice. The full-density version uses
the actual many-body evolution and does not presume a one-particle closure.

This can reduce the state information that has to be reconstructed to the
operator actually tested by the muon observable. It is an exact duality formula
under its stated assumptions, not a numerical evaluation of the BHSM kernel.
There is no replacement of forward physical time by proper-time heat evolution.

## 8. Continuum, ultraviolet, and physical admission

The finite trace norms and optimization witnesses in this package do not prove
an ultraviolet or infinite-history enclosure. A continuum application needs
compatible domains, trace-class relative kernels (or a specified weaker paired
space), allowed smooth/Hadamard perturbations, the physical quotient, and
controlled tails. The full finite CAR set is generally larger than the
physically admissible inherited-state family. That makes its interval useful
as a finite conservative bound when a proper inclusion is proved, but not a
license to use arbitrary finite covariances as continuum physical states.

The inherited-state receipt remains uninstantiated. The physical operator,
complete reference-sensitivity kernel, and uniform nonlinear/tail remainders
have not been evaluated by the new script. It does not produce physical
incoming modes, pole normalizations, terminal return, Maxwell/all226 admission,
or a Pauli-weighted native contraction. There is no physical 2e-10 admission
and no total uncertainty for \(a_\mu\) or \(g_\mu\).

## 9. Executed checks and results

`continue_operator_reference.py` was run twice. The JSON outputs are
byte-identical. No previous benchmark was rerun as a substitute for a new
physical calculation.

| New check | Recorded result | Scope |
|---|---|---|
| Four internal Clifford relations | Exact symbolic zero | Trial algebra |
| Hermitian scalar map, squared mass, full kinetic metric | Exact symbolic identities | Local fixed-cutoff inverse construction |
| Quartic/quadratic heat matching equations | Exact symbolic identities | a2+a4 trial truncation |
| Extra scalar-curvature coefficient | Exactly b/12 | Nonzero trial discrepancy |
| CAR projection trace-pairing agreement | Error 2.225e-16 | Constructed finite matrices |
| Sharp CAR extremal bounds | Worst endpoint error 3.553e-15 | Constructed finite matrices |
| Covariance equality with unequal quartic expectation | Exact, 1/2 versus 0 | Same-number finite Fock control |
| Nonlinear complete derivative and remainder | Exact, change 1/4 bounded by 25/64 | Constructed implicit control |

These control errors describe arithmetic/algorithm checks only. They are not
uncertainties in physical BHSM observables.

## 10. Exact continuation boundary

The scalar test now supplies a concrete field map and a coefficient-by-coefficient
comparison, including its nonzero curvature and boundary obligations. It does
not authorize promoting the trial Clifford representation into the native
carrier. The next field-to-native calculation must establish the actual
representation and its complete matching, rather than setting the discrepancy
to zero or choosing the cutoff from it.

For the inherited reference, the new target is the complete kernel projected
onto the **actual** allowed state directions, together with its nonlinear and
continuum remainders. Where higher connected products survive, that target is
the full-density kernel, not a covariance-only cancellation. This keeps the
inherited sea unspecified without pretending that causal transport selects it.

`native_operator_reproduces_full_action=False`

`inherited_reference_selected=False`

`physical_reference_sensitivity_evaluated=False`

`Gate7_closed=False`

`FULL_BHSM_COMPLETE=False`

## Provenance and external mathematical context

**Source-derived BHSM content**

- Pinned term registry: https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/b6cb15f5ab6f6b44057f13895c5fd498ce928d83/src/bhsm/interface/master_action/terms.py
- Native functional, moment, cutoff and carrier contract: https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/b6cb15f5ab6f6b44057f13895c5fd498ce928d83/src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py
- Current operator/reference limitations and physical preparation: https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/b6cb15f5ab6f6b44057f13895c5fd498ce928d83/theory/muon_ideal_preparation_action_derivation_20261016.md
- Prior generated package: `BHSM_operator_reference_construction_20261016.zip` and its `DERIVATION.md`; hashes recorded in `provenance.json`.

**External primary mathematical source**

D. V. Vassilevich, *Heat kernel expansion: user's manual*, arXiv:hep-th/0306138,
sections 3.3 and 4.1, especially equations (3.27), (4.27), and (4.28):
https://arxiv.org/html/hep-th/0306138

The scalar embedding, its specialized matching/discrepancy equations, the
CAR/Fock certificates, and the worked exact controls are the present derivations.
They are not claimed to be BHSM physical conclusions from this external paper.
