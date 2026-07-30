# BHSM v8.0 mass--curvature response

## Doctrine and scope

BHSM v8.0 introduces or completes the mass-curvature response coupling
between the hyperspherical core/cap system and localized M4 matter.

This is an explicit extension of the stratified action, not a reinterpretation
of the v7.3 absence theorem. The construction uses the existing
Einstein--GHY canonical momentum, cap matcher, localized Standard Model
Yukawa operators, and v7.1 collar geometry. It introduces no new dynamical
field, mediator, fitted mode choice, boundary parameter, or scale
calibration.

The construction has a rigorous negative physical outcome. The unique local
curvature insertion is family-universal, and the current constrained action
does not split into two independent positive core and surface energies.
Consequently it cannot generate either an action-selected localization
family or nondegenerate charged-family masses.

## Canonical carrier

Varying the scalar kinetic term gives the outward scalar momentum

\[
 \pi_{\sigma,\epsilon}
 =-\sqrt{|h|}\,Z_5 n_\epsilon^A D_A\sigma .
\]

The retained scalar is odd under the cap reflection and has Dirichlet seam
trace \(\sigma|_{M_4}=0\). A linear \(\pi_\sigma\) insertion is parity odd,
while the first even combination \(\sigma\pi_\sigma\) vanishes on the
selected domain. The scalar momentum is therefore not the mass carrier.

The coefficient-locked Einstein--Hilbert plus GHY variation instead gives,
in the repository's density-free structural convention,

\[
 \pi_\epsilon^{ab}
 =\epsilon\kappa_1
 \left(K_\epsilon^{ab}-K_\epsilon h^{ab}\right).
\]

The metric matcher equation is
\(\Lambda_\epsilon^{ab}=\pi_\epsilon^{ab}\). It identifies the reaction
with the same canonical momentum; counting both would double count one
boundary response. After solving the cap Einstein--scalar, radial ADM,
matcher, gauge, and closed-range-complement equations, the covariant
Dirichlet-to-Neumann object is

\[
 \Lambda_{\rm env}:\delta h|_{M_4}
 \longmapsto\delta\pi_{\rm env}|_{M_4},\qquad
 \pi_{\rm env}^{ab}=\frac{\pi_+^{ab}+\pi_-^{ab}}2 .
\]

The cap-even, Lorentz-scalar, dimension-one contraction is uniquely

\[
 \kappa_{\rm env}
 =-\frac{1}{3\kappa_1}h_{ab}\pi_{\rm env}^{ab}
 =\frac{\epsilon_+K_++\epsilon_-K_-}{2}.
\]

It vanishes on the exact round equatorial background, where \(K_{ab}=0\).

## Minimal action extension

The unique local response insertion of operator dimension at most five is

\[
 S_{\rm mass-response}^{(5)}
 =-\sum_{f=u,d,e}c_f\int_{M_4}\sqrt{|h|}\,
 \kappa_{\rm env}{\cal O}_{Y,f}+\mathrm{h.c.},
\]

with

\[
 {\cal O}_{Y,u}=\overline Q_L\widetilde H u_R,\quad
 {\cal O}_{Y,d}=\overline Q_L H d_R,\quad
 {\cal O}_{Y,e}=\overline L_L H e_R .
\]

Equivalently, on a selected nonzero response channel, action-canonical
normalization defines

\[
 \widehat\Lambda_{\rm env}
 =\kappa_{\rm env}/|\kappa_{\rm env}|_{\rm action}
\]

and the three ordinary sector strengths \(y_u,y_d,y_e\) multiply the
normalized insertion. This is the explicit v8.0 action coupling. It is not
an admissible flavor mechanism: on a fixed background its family-scalar
factor is equivalent to a common local rescaling of the corresponding
sector Yukawa strength. The zero-response round equator cannot be
normalized and yields no curvature-induced mass incidence.

The other dimension-five-or-lower candidates fail:

- \(\pi_\sigma{\cal O}_Y\) violates scalar parity;
- the matcher trace duplicates \(\pi_{\rm env}\);
- an observer contraction \(u_a u_b\pi_{\rm env}^{ab}\) requires an
  underived timelike observer;
- \(R[h]{\cal O}_Y\), \(K^2{\cal O}_Y\), and
  \(K_{ab}K^{ab}{\cal O}_Y\) are dimension six;
- the quadratic extrinsic-curvature terms also require new independent
  coefficients.

Thus the local extension candidate is unique, while the nonredundant
family-resolving admissible set is empty.

## Collar geometry and radial operator

The collar coordinate is fixed by \(\rho=0\) at the common \(M_4\) seam,
with increasing \(\rho\) directed into either cap toward its core. In the
v7.1 embedding,

\[
 c_\epsilon(t,x,\rho)
 =(t,\pi/2-\epsilon\rho,x).
\]

The normal-first tubular convention gives

\[
 J(Y,\rho)=\det(I+\rho S(Y)),
\qquad
 \langle u,v\rangle_{\rm collar}
 =\int_{M_4}\int_{\cal C}u^\dagger v\,
 J(Y,\rho)\,d\rho\,d\mu_h .
\]

For the exact round cap,

\[
 J_{\rm round}(\rho)=\cos^3\rho,\qquad
 d\mu_5=Na^4\cos^3\rho\,dt\,d\rho\,d\mu_{S^3}.
\]

The scalar normal operator produced by the reduced second variation has the
structural form

\[
 {\cal L}_\sigma
 =-J^{-1}D_\rho(JZ_5D_\rho)
 +U_5''(\sigma_{\rm bg})+V_{\rm metric,constraint}.
\]

Its selected domain is the regular weighted \(H^2\) scalar domain with
zero seam trace, regularity at the cap pole, the metric gauge quotient,
matcher reaction, and explicit Lyapunov--Schmidt kernel coordinate. The
strict fixed-\(h\) representative has kernel \(\operatorname{span}\{u_1\}\)
and normalized complement gap \(64.0147366689857\). The gap is not used as
a mass floor, and the zero-trace scalar channel is not inserted into the
mass operator.

## Energy envelopment and localization

The desired ratio

\[
 \varepsilon
 =\frac{{\cal E}_{\rm core}}
 {{\cal E}_{\rm core}+{\cal E}_{\rm surface}}
\]

is not defined by the current action. The complete cap/ADM/matcher
quadratic form is an indefinite KKT saddle. Brown--York surface energy
requires an observer and a reference subtraction. A Lorentzian scalar
gradient is not positive without an observer. The positive fixed-\(h\)
scalar-complement form has zero Dirichlet trace, and its DtN expression is
the same bulk quadratic energy rather than an independent surface energy.
The compatibility multiplier is a constraint, not a positive energy.

Taking absolute values, adding a subtraction, or splitting one quadratic
form into nominal “core” and “surface” copies would introduce arbitrary
structure. Therefore no \(\varepsilon\), nonlinear self-consistency map,
stationary profile family, monotonic
\(d\langle\rho\rangle_\varepsilon/d\varepsilon\), or endpoint localization
limits are asserted.

The exact intermediate obstruction is

`BHSM_MASS_RESPONSE_BLOCKED_BY_NO_POSITIVE_ENERGY_ENVELOPMENT_FUNCTIONAL`.

## Family response and physical transport

The selected response space is one real, cap-even, gauge-singlet scalar
channel. It carries neither chirality nor a family representation. It does
not derive three generations. Conditional on the already supplied
\(\mathbb C^3\) localized family spaces, Schur's lemma forces

\[
 \widehat\Lambda_u
 =\widehat\Lambda_d
 =\widehat\Lambda_e=I_3.
\]

Each response has rank three and singular values \((1,1,1)\). At the v7.2
reference scale,

\[
 m_{f,i}^{\overline{\rm MS}}(\mu_\star)
 =\frac{y_fv(\mu_\star)}{\sqrt2}s_{f,i},
\qquad
 \frac{m_{f,i}}{m_{f,j}}=1.
\]

The overall \(y_f\) cancels, so the conditional prediction is exactly
\(1:1:1\) in every supplied charged sector. Exact degeneracy leaves the
left singular bases arbitrary. Hence
\(V_{\rm CKM}=U_u^\dagger U_d\), its angles, phase, and Jarlskog invariant
are not response invariants and are not predicted.

## Freeze and falsification

Before any comparison, the extended action, carrier, absent envelopment
ratio, collar orientation, Jacobian, operator, domain, mode count,
normalization, matrices, exact degeneracies, uncertainty, and falsification
threshold were serialized and hashed. The frozen SHA-256 is

`BDE7FA8DC967120E09823BBC496F2FE564912A7CD363857571C4B6B9F3AD767C`.

Only afterward were the repository-held historical bare screen, dressed
candidate, and common-scale reference ratios opened. All are nondegenerate
and therefore incompatible with the frozen universal response. No operator
or normalization was retuned. The historical records remain provenance and
are not promoted into the v8.0 action-derived predictive path.

The falsification threshold is exact: any nondegenerate charged-sector
singular-value ratio invalidates the universal response as a flavor
mechanism. The repository-held comparison already meets that threshold.
The family-resolution obstruction is the strongest final result because it
is independent of, and would survive the later supply of, a positive
core/surface energy functional.

RB-15 remains `BLOCKED_EXACT_OBJECT_PROVED`; RB-16 remains
`DOWNSTREAM_BLOCKED`. The remaining object is

`FAMILY_RESOLVING_ACTION_INCIDENCE_BEYOND_THE_UNIVERSAL_CURVATURE_SCALAR`.

The strongest v8.0 verdict is

`BHSM_MASS_RESPONSE_BLOCKED_BY_UNIVERSAL_RESPONSE_WITH_NO_FAMILY_RESOLUTION`.

## Reproduction

```bash
python -m compileall src/bhsm/interface/master_action/mass_curvature_response.py
python -m bhsm.interface.master_action.mass_curvature_response --materialize
python -m bhsm.interface mass-curvature-response-status --format json
python -m bhsm.interface mass-curvature-response-status --format markdown
```

The materializer writes deterministic UTF-8/LF JSON for the v8.0 response
artifact and the canonical completion gate.
