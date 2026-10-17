# BHSM operator, domain, and inherited-reference construction

Norman Carberry research continuation — 16 October 2026

**Source anchor:** `b6cb15f5ab6f6b44057f13895c5fd498ce928d83`, PR #465.

**Status:** partial mathematical construction and explicit conditional reference
prescription. This is not a completed microscopic BHSM realization, an admitted
physical background, or a numerical magnetic-moment result. No repository files
or frozen predictions were changed. The selected collider preparation is kept.

## 1. What this work actually resolves

This work provides:

* An explicit closed-form construction of the positive operator/domain **once
  the full first-order field expression, Hilbert carrier, and action boundary
  data are supplied**. It does not assume that a Lorentzian retarded inverse is
  the native positive operator.
* Exact scalar quadratic-form factorization and a remainder fixed by the
  existing S8 density. These give a concrete test of the microscopic-to-local
  correspondence rather than an instruction to square an arbitrary Hessian.
* A restriction on possible gradings: spin chirality cannot indiscriminately
  be substituted for physical statistics, because an odd self-adjoint Dirac
  doubling cancels its nonzero heat spectrum under that chirality supertrace.
* A volume-isometric retained/complement construction and an exact resolvent
  reduction, retaining mode coupling without counting the same field twice.
* A mathematical inherited-reference prescription for an asymptotically static,
  gapped incoming Dirac problem, with explicit source derivatives. Applying it
  to BHSM needs its hypotheses proved, or its extra physical premise explicitly
  adopted. It is **not** a derived identification of the primordial sea.
* An adjoint formula for testing whether the observable needs the unresolved
  reference at all, including the induced change of the background.

The remaining full-field twist/endomorphism/statistics map has not been derived.
The actual BHSM incoming reference has not been instantiated. These limitations
are included in the machine-readable results; the algebra controls do not
replace their physical evaluation.

## 2. Preserved source facts and distinctions

The pinned report `theory/muon_ideal_preparation_action_derivation_20261016.md`
distinguishes the local Euler/Jacobi equations from the generating microscopic
operator. The native prescription is

\[
\Gamma_{\rm ind}=-\frac12\operatorname{STr}E_1(\ell^2P_\Phi),
\qquad P_\Phi=D_\Phi^\dagger D_\Phi,
\]

with its existing relative zeta/eta, domain and quotient completion. Its finite
proper-time function must not silently be replaced by an unregulated log-det.
The master action's M8/M5/M4 expressions are not proof of their reduction maps.

The actual two-collar law is interaction-dependent. On the original two traces,

\[
x=\operatorname{Tr}_+\Psi_+,
\quad z=\operatorname{Tr}_-\Psi_-,
\quad z=\mathsf T_\Phi x,
\quad \mathsf T_\Phi=U_{\rm geo}(I+N_\Phi),
\]

where the supplied local construction gives

\[
N_\Phi=J_+^{-1}C(\rho M_Y(H))B,\qquad N_\Phi^2=0
\]

when the stated isotropy identities hold. The free graph is the zero-source
limit; it is not another equation to impose at nonzero surface source.
The interface distribution is represented by this action domain and must not
be added a second time to the same strong operator.

The historical eta-bound normal mode

\[
u_0(s)=\mathcal N J(s)^{-1/2}\sin f_\eta(s),\qquad
\mathcal N^{-2}=\int\sin^2 f_\eta(s)\,ds
\]

has unit normal volume norm on its stated domain. This is a useful **seed
sector**, not proof that the fully interacting muon inclusion stays within that
one mode. In particular, the later interacting graph supersedes the historical
free continuity inference. No historical free-profile claim is promoted beyond
its assumptions here.

The beam preparation fixes external design values. It does not select all sea
correlations, convert a point trace into a volume isometry, or determine a full
microscopic statistical carrier.

## 3. A precise positive-domain construction

### 3.1 Start from the unsquared, action-defined expression

For an already identified field carrier, use the first-order expression in its
retained fermion action. In the eta collar sector this has the schematic form

\[
\mathscr D_\epsilon[\Phi]
=i\gamma^\mu\nabla^{\rm total}_\mu
+i\epsilon\Gamma_\perp
\left(\partial_s+\tfrac12\partial_s\log J
-\partial_s\log\sin f_\eta\right).
\]

The Higgs surface coupling belongs to the interacting two-trace condition above.
A bulk mass and a surface mass representing the same term must not both be
inserted. Fields and coefficients here retain their actual source dependence.
An established continuation to the native positive/Hilbert problem is still
needed; changing the sign of a Lorentzian matrix does not perform it.

### 3.2 A graph, not a fictitious closing cap

On the admitted positive/Hilbert realization, let \(\mathcal D_0\) be a dense
core of piecewise regular sections satisfying all actual action constraints and
trace relations, including \(\operatorname{Tr}_-\Psi_-=\mathsf T_\Phi
\operatorname{Tr}_+\Psi_+\). Endpoint and exterior requirements are part of this
core; this argument does not choose them by convenience.

For a closable \(\mathscr D_\Phi\), set

\[
D_\Phi=\overline{\mathscr D_\Phi|_{\mathcal D_0}},\qquad
q_\Phi[u,v]=\langle D_\Phi u,D_\Phi v\rangle,
\quad \mathcal D(q_\Phi)=\mathcal D(D_\Phi).
\]

This is a closed, densely defined, nonnegative form. Its associated operator is

\[
\boxed{P_\Phi=D_\Phi^\dagger D_\Phi},\qquad
\boxed{\mathcal D(P_\Phi)=\{u\in\mathcal D(D_\Phi):D_\Phi u\in
\mathcal D(D_\Phi^\dagger)\}}.
\]

**Proof of the constructive point.** Give \(\mathcal D(D_\Phi)\) the graph norm
\(\|u\|^2+\|D_\Phi u\|^2\). Closedness makes it complete. For every \(f\), the
coercive weak equation

\[
\langle v,u\rangle+\langle D_\Phi v,D_\Phi u\rangle=\langle v,f\rangle
\quad (v\in\mathcal D(D_\Phi))
\]

has a unique solution. By the definition of the adjoint, that solution satisfies
\(D_\Phi u\in\mathcal D(D_\Phi^\dagger)\) and \((I+P_\Phi)u=f\).
Thus the form specifies the positive operator rather than merely writing a
formal differential square. No fourth-order square of a scalar Hessian is used.

For a first-order differential expression with smooth coefficients on each open
collar, compactly supported tests away from the interface give a dense formal
adjoint domain and therefore closability of the regular restriction. Equality
of its closure with a stated piecewise \(H^1\) graph requires a compatible
elliptic/trace estimate. Essential self-adjointness of a Lorentzian Cauchy
generator, global heat trace-class properties and quotient compatibility are
additional properties, not consequences of this closability argument.

A physical outgoing/retarded response is obtained from the appropriate causal
problem on the coupled system, or its legitimate reduction. **This positive-form
construction does not identify that retarded inverse with the quantum heat
operator.**

### 3.3 Moving domain and moving measure

At the local interface,

\[
D_h\mathsf T=(D_hU_{\rm geo})(I+N)+U_{\rm geo}D_hN,
\]

and the mixed derivative is

\[
D_{hk}\mathsf T=U_{hk}(I+N)+U_hN_k+U_kN_h+UN_{hk}.
\]

Differentiating the original trace equation additionally differentiates the
trace maps themselves. For example,

\[
\operatorname{Tr}_-D_h\Psi_-+(D_h\operatorname{Tr}_-)\Psi_-
=\mathsf T\operatorname{Tr}_+D_h\Psi_+
+\mathsf T(D_h\operatorname{Tr}_+)\Psi_+
+(D_h\mathsf T)\operatorname{Tr}_+\Psi_+.
\]

This is the source for the moving-domain variation. It is not zero merely
because the operator's bulk coefficient jet was evaluated.

For finite Cauchy/volume Gram \(G>0\), let \(S=G^{1/2}\) be its positive root.
The exact derivative solves

\[
S\,D_hS+(D_hS)S=D_hG.
\]

The elementwise scalar rule \(D_hS=(2\sqrt G)^{-1}D_hG\) is generally wrong
when \(G\) and its derivative do not commute. With isometries to fixed input and
output pairings, \(\widehat D=S_{\rm out}D S_{\rm in}^{-1}\). Real-parameter
variations then give

\[
D_h\widehat P=(D_h\widehat D)^\dagger\widehat D+
\widehat D^\dagger D_h\widehat D.
\]

Analytically continued source jets require independently continued left leaves,
not complex-conjugation of an analytic source parameter. None of this adds a
moving-adjoint contribution to the separately defined fixed-adjoint source
contraction.

## 4. Full normal inclusion and the complement

The old normal mode gives a volume map, not a point evaluation:

\[
(\iota\psi)(s,x)=u_0(s,x)\,\mathcal U(s,x)\psi(x),\qquad
\int ds\,J\,\mathcal U^\dagger|u_0|^2\mathcal U=I.
\]

For an interacting, nonseparable background replace this special expression
by its actually solved matrix-valued normal mode frame. The condition that must
survive is \(\iota^\dagger\iota=I\). The source dependence of this map and of its
normalization must be retained. An identity valid in the free eta sector does
not compute that interacting frame.

Let \(Q=I-\iota\iota^\dagger\). In a unitary identification of the whole carrier
with the retained image plus its complement, write

\[
P=\begin{pmatrix}A&B\\ B^\dagger&C\end{pmatrix}.
\]

Where the indicated resolvents exist,

\[
\boxed{\iota^\dagger(P-z)^{-1}\iota
=\big[A-z-B(C-z)^{-1}B^\dagger\big]^{-1}.}
\]

Thus the retained quantum response is calculable without treating every
complement mode as an independent daughter enclosure, but the complement is
not removed from the physics. In particular,

\[
\iota^\dagger f(P)\iota\ne f(\iota^\dagger P\iota)
\]

in general. Use a justified functional calculus of the complete resolvent.
Do not assign the heat of a small compressed matrix to the full trace.
Nor add the full D5 trace and the same localized M4 fermions as two independent
species. Finite determinant identities extend to regularized determinants only
after the common relative and boundary prescription is established.

This fixes the **form of a faithful correspondence**. It does not construct
missing M8 twists or the currently unsolved physical normal frame.

## 5. Exact scalar correspondence target

Use the real Riemannian fixed-metric counterpart of the scalar density as a
local algebraic matching test:

\[
S_E=\int d\mu\left[\tfrac12a(\sigma)|d\chi|^2+
\tfrac12b|d\sigma|^2+V(\sigma)\right],
\]

\[
a=Z_\chi(1+g\sigma^2),\quad b=Z_\sigma,\quad
V=\tfrac12A_0\sigma^2+\tfrac14G_0\sigma^4.
\]

This is not a proof of a global Wick continuation. Its quadratic variation for
\((u,v)=(\delta\chi,\delta\sigma)\) is exactly

\[
\delta^2S_E=\int d\mu\,[a|du|^2+2a'v\langle d\chi,du\rangle+b|dv|^2
+(\tfrac12a''|d\chi|^2+V'')v^2].
\]

Completing the square gives an explicit first-order differential map

\[
\mathcal A(u,v)=
\left(\sqrt a\,du+\frac{a'}{\sqrt a}v\,d\chi,\ \sqrt b\,dv\right)
\]

and

\[
\boxed{\delta^2S_E=\|\mathcal A(u,v)\|^2+\int d\mu\,W_\Phi v^2},
\]

\[
\boxed{W_\Phi=A_0+3G_0\sigma^2+
Z_\chi g\frac{1-3g\sigma^2}{1+g\sigma^2}|d\chi|^2.}
\]

These identities hold for the stated density off shell at fixed metric, before
additional moving-boundary/metric terms. They were verified symbolically.
If \(a,b>0\) and \(W_\Phi\ge0\), appending \(\sqrt{W_\Phi}v\) produces a local
rectangular first-order factor of this scalar Hessian, with its actual form
domain. If \(W_\Phi\) has negative parts, deleting them changes the action;
pointwise negativity by itself does not prove that the integrated Hessian is
unstable. Even a successful factor is a factor of the **response Hessian**, not
proof of identity with the microscopic generating \(D_{\rm strat}\).

The scalar field-space metric is

\[
ds_{\rm fields}^2=a(\sigma)d\chi^2+b\,d\sigma^2,
\quad
\boxed{\mathcal K_{\rm fields}=-\frac{g}{Z_\sigma(1+g\sigma^2)^2}.}
\]

Consequently one cannot generally replace these fields by two independently
normalized flat field coordinates. The field-space connection and all source
contacts associated with it are determined, rather than freely selectable.
Ordinary and field-space-covariant Hessians differ off shell by the connection
contracted with the Euler residual. Do not use an on-shell cancellation on an
unmatched base.

The actual missing microscopic test is

\[
\mathcal E_{\rm retained}\Gamma_{\rm ind}[P_\Phi,\ell_\Phi]
=S_{\rm retained}[\Phi]
\]

at the stated continuation/expansion orders, together with its field, mixed and
boundary variations. Here \(\mathcal E_{\rm retained}\) means the already claimed
local expansion, not a newly fitted subtraction. The scalar density above is
one explicit target.

A purely geometric untwisted \(P_8(G)\), held independent of \(\chi,\sigma\)
while cutoff, support and relative completion are also held fixed, has zero
scalar variation. It cannot reproduce the nonzero target above. A scalar
embedding into geometry, internal connection, endomorphism, support or cutoff
must therefore actually be derived. This excludes that restricted candidate;
it neither excludes all BHSM completions nor establishes a unique new twist.

## 6. Statistics is not spin chirality

Suppose a proposed full self-adjoint operator is odd under a grading \(\gamma\),
with invariant domain: \(\gamma D=-D\gamma\). A common automatic construction is

\[
\mathbb D=\begin{pmatrix}0&T^\dagger\\T&0\end{pmatrix},\qquad
\gamma=\operatorname{diag}(I,-I).
\]

Its square has blocks \(T^\dagger T\) and \(TT^\dagger\). Every nonzero eigenvalue
is paired: applying \(T/\sqrt\lambda\) identifies the two eigenspaces.
Therefore, wherever traces are defined, the nonzero contribution to

\[
\operatorname{Tr}\big(\gamma e^{-s\mathbb D^2}\big)
\]

cancels. With zero modes removed in both sectors, it is zero. With zero modes
kept, the index contribution remains. This is not a generic source of the
required scalar, gauge and gravitational bulk coefficients.

Thus assigning opposite statistical signs to two chiralities merely because
there are two spinor sectors can destroy the action being constructed. Both
chiralities of an ordinary fermion carry fermionic statistics. The physical
statistics/ghost measure must be identified independently of a formal Dirac
doubling. The conclusion has the stated self-adjoint/odd/domain assumptions;
it is not asserted for every non-self-adjoint matrix with a label 'grading'.

A Gaussian fluctuation calculation can determine familiar determinant weights
from its already specified bosonic, Grassmann and ghost integrations. That
calculation is **not automatically the microscopic AE4 action**, which is
supposed to generate the retained local actions. Quantizing a local action and
then calling its Hessian the operator that originally induced the same action
is an extra self-consistency postulate, not an identity established here.

## 7. Explicit conditional selection of an inherited reference

### 7.1 Additional premise, clearly identified

A possible benchmark closure is:

> On an actual regular incoming reference history, the physical Cauchy
> Hamiltonian tends to a stationary, gapped Hamiltonian in the remote past,
> and the reference is its no-particle ground state transported causally.

This is a precise physical boundary prescription. It is **not implied** by the
words 'no extra radiation relative to the inherited sea'. It is not derived
from the white-hole/core ontology, and it does not establish that present
cosmological relic populations vanish. Applying it would narrow the reference
for this benchmark. Existing sources do not establish that BHSM meets these
asymptotic conditions.

### 7.2 The construction

Use the Lorentzian first-order **physical** Cauchy Hamiltonian \(h(t)\), not the
positive factor \(P^{1/2}\). Suppose, after identification of the Cauchy Hilbert
spaces and their domains, \(h(t)\to h_-\). Write

\[
\Pi_+^-={\bf1}_{(0,\infty)}(h_-),\qquad
C_{\rm in}^+(t)=\lim_{s\to-\infty}U(t,s)\Pi_+^-U(s,t).
\]

The \(+\) covariance here is the positive-frequency two-point convention;
the occupied negative-energy projector is its complement. Specifying this
convention avoids calling the two complementary objects the same covariance.
For a self-dual CAR chart with antiunitary \(\mathcal J\) and
\(\mathcal J h_-\mathcal J=-h_-\), no zero modes, and charge-compatible evolution,

\[
0\le C^+\le I,\quad (C^+)^2=C^+,\quad
C^++\mathcal J C^+\mathcal J=I.
\]

Under suitable asymptotically static bounded-geometry assumptions, published
Dirac-field results give existence and the Hadamard property of these in/out
states. They do not prove those assumptions for BHSM, or for a singular
stratified interface without its own analysis.

A simple sufficient finite/bounded-perturbation condition is
\(\int_{-\infty}^{t_0}\|h(t)-h_-\|dt<\infty\). In the interaction picture,
Duhamel's formula makes the incoming Moller limit Cauchy. It yields the
projector-limit error estimate

\[
\|C_{\rm in}^+(t_0)-U(t_0,s)\Pi_+^-U(s,t_0)\|
\le 2\int_{-\infty}^{s}\|h(t)-h_-\|dt.
\]

The factor 2 follows by writing the difference of unitary conjugations of a
projector. This bound is for the stated bounded model; extension to unbounded
operators needs compatible graph estimates. A proper-time heat kernel does
not itself specify this Lorentzian polarization: \(h\) and \(-h\) have the same
square and opposite frequency projectors.

### 7.3 Derivatives that a physical implementation would consume

For a fixed gap, the spectral-projector derivative has divided differences

\[
(D_h\Pi_+)_{ij}
=\frac{\mathbf1_{\lambda_i>0}-\mathbf1_{\lambda_j>0}}
{\lambda_i-\lambda_j}(D_hh_-)_{ij},
\]

with zero coefficient within a common sign cluster. This is independent of
basis choices inside each spectral cluster. A gap closing needs separate
treatment; arbitrarily assigning the zero mode to one side is not a derivative.

Transport satisfies

\[
i\partial_tC=[h,C],\qquad
i\partial_t(D_hC)=[h,D_hC]+[D_hh,C].
\]

At an inherited unitary reset \(V\),

\[
C_{\rm child}=VC_{\rm parent}V^\dagger,
\]

and differentiation includes \(V_h\), \(C_h\), and the appropriate dual map.
These formulas carry the inherited state; they do not generate its seed.
Full unitary transport preserves differences between two reference covariances.
Dissipation in a reduced sector can change that conclusion, but then its noise
and environment state must be specified consistently; retarded damping alone
does not determine them.

For a bosonic quadratic physical sector with positive incoming frequency
operator \(\Omega_-\), the corresponding ground-state equal-time covariances
would be \(\langle QQ\rangle=\tfrac12\Omega_-^{-1}\),
\(\langle PP\rangle=\tfrac12\Omega_-\), and zero symmetrized QP covariance
in natural units. This also requires its physical quotient and zero-mode
conditions. Ghosts are not independent positive-occupation particles. An
interacting inherited state may need higher connected correlations; a quadratic
reference does not prove a nonperturbative Gaussian state. The exact prepared
pair mixture remains separate throughout.

## 8. Alternative: derive only the reference dependence actually consumed

There is an exact reduction for this question. Work on a fixed realified
physical quotient and include all required constraints in

\[
\mathcal R(\Phi,C)=0.
\]

Let \(a(\Phi,C)\) denote the **complete** matched magnetic readout, including
its state/domain/normalization dependence. If the constrained
\(J=\mathcal R_\Phi\) is invertible, an admissible covariance variation \(X\)
gives

\[
D\Phi[X]=-J^{-1}\mathcal R_C[X].
\]

Solve one adjoint equation \(J^*\lambda=a_\Phi^*\). Then

\[
\boxed{D_Ca_{\rm solved}[X]=a_C[X]-\langle\lambda,\mathcal R_C[X]\rangle.}
\]

This is the observable's direct state sensitivity minus its background-mediated
state sensitivity. The adjoint here belongs to this newly defined complete
real sensitivity; it does not alter the fixed-adjoint convention of the
previous chronological source derivative.

A fixed-background cancellation checks only the first term. To remove the
reference dependency, the whole expression must vanish on every admissible
state direction relevant to the approximation, or be bounded at the target
accuracy. A zero derivative at one point is not proof of independence over a
family. Pure-state tangents, mixed CAR covariances, allowed ultraviolet
regularity and any higher correlations impose different admissible variation
spaces; they must not be conflated.

If this derivative is represented as \(\operatorname{Tr}(M_{\rm eff}X)\), then
\(|D_Ca[X]|\le\|M_{\rm eff}\|\,\|X\|_1\) when the operator/trace norms exist.
No bound on actual BHSM state variations is claimed here. This is a possible
way to avoid reconstructing an entire cosmic sea when only a small functional
of it survives in the muon observable.

## 9. Executed verification and its scope

`verify_constructions.py` was run twice with byte-identical JSON outputs. It
uses the scalar action coefficients symbolically and deliberately constructed
finite matrices for the other algorithmic checks. It does not load physical
BHSM fields or claim a native contraction.

Selected recorded results:

* Exact scalar quadratic-form completion, field-space curvature, historical
  eta normal identity, and nilpotent interface/Green identities: symbolic zero.
* Finite compressed-resolvent identity: Frobenius error about 7.01e-17.
* Incorrect heat-of-compression replacement in the same control: difference
  about 1.464e-3. This demonstrates the noncommuting-complement issue, not its
  numerical size in BHSM.
* Chirality-graded heat control: cancellation about 2.22e-16 while the ordinary
  doubled trace is about 2.321. These are not physical statistical weights.
* Moving Gram square-root Sylvester residual: about 8.91e-17; independent
  finite-difference derivative error about 5.15e-11.
* Conditional in-reference control: self-dual CAR residual about 5.36e-13.
  Independent source-derivative errors decrease from 4.12e-7 to 1.03e-7 to
  2.57e-8 under halving, as expected for the central-difference check.
* The explicitly integrable model has reference tail bound 0.7 exp(s); at
  s=-12 the bound is about 4.30e-6 before numerical evolution error. This is
  intentionally not claimed as the physical 2e-10 gate or as a complete
  derivative-tail enclosure.
* A distinct admissible covariance separated by operator norm 0.1 remains
  separated by 0.1 after the same unitary evolution; its retarded evolution
  operator is unchanged.
* Full/background-mediated sensitivity and the adjoint formula agree to
  about 5.55e-17 in their finite control.

The initial symbolic test harness compared an unsimplified matrix expression
with the identity structurally. It was corrected to simplify their difference
before testing equality. No physical equation or tolerance was changed by that
harness correction.

## 10. What is still required to claim resolution

The full microscopic construction needs an actual map
\(\Phi\mapsto(\mathcal H_{\rm phys},D_\Phi,\mathcal D(D_\Phi),\mathrm{statistics},
\mathrm{quotient})\) whose expansion and variations reproduce all consumed
retained action sectors. The positive-domain theorem specifies the completion
of a **given** D; it does not invent the missing twisting/endomorphisms or
statistics of the M8 carrier. The scalar and grading results above make that
remaining problem sharper and exclude particular unjustified constructions.

The reference can be selected by the proposed in-ground-state rule only if its
physical premise is adopted and the actual incoming Hamiltonian/history meets
its mathematical assumptions. Otherwise the primordial covariance or its
consumed observable projection still requires an action-derived selection.
No presently absent cosmological population was set to zero by this work.

These are substantive outstanding conditions, not new numerical input files
that Norman must locate and not proof that BHSM has no completion. The next
scientific application is the actual field-to-native matching on the current
coupled carrier, and the inherited-state construction or complete sensitivity
calculation on that same solution. No packet/terminal/all226/Pauli admission is
reported from the symbolic or finite controls in this package.

## Sources and provenance

Pinned repository:

1. `theory/muon_ideal_preparation_action_derivation_20261016.md`
   https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/b6cb15f5ab6f6b44057f13895c5fd498ce928d83/theory/muon_ideal_preparation_action_derivation_20261016.md
2. `src/bhsm/interface/master_action/terms.py`
   https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/b6cb15f5ab6f6b44057f13895c5fd498ce928d83/src/bhsm/interface/master_action/terms.py
3. `src/bhsm/interface/muon_two_collar_weak_domain.py`
   https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/b6cb15f5ab6f6b44057f13895c5fd498ce928d83/src/bhsm/interface/muon_two_collar_weak_domain.py
4. Library: `BHSM_FOUNDATIONAL_DIRAC_SPIN_GLUE_V14_45.md`, normal-action and
   normalized-mode sections. Its free seam continuity inference is not used
   in place of the newer interacting graph.

Mathematical context (not BHSM physical-input substitutions):

5. D. V. Vassilevich, Heat kernel expansion: user's manual.
   https://arxiv.org/abs/hep-th/0306138
6. C. Gerard and T. Stoskopf, Hadamard states for quantized Dirac fields on
   Lorentzian manifolds of bounded geometry.
   https://arxiv.org/abs/2108.11630
7. C. Gerard and T. Stoskopf, Hadamard property of the in and out states for
   Dirac fields on asymptotically static spacetimes.
   https://arxiv.org/abs/2108.11955
8. J.-M. Bismut, Hypoelliptic Laplacian and Orbital Integrals, chapter 7
   (McKean-Singer heat-supertrace/index context).
   https://doi.org/10.23943/princeton/9780691151298.003.0008

The proofs and conditional specializations in sections 3–8 are the present
analysis. They must not be attributed wholesale to these sources.
