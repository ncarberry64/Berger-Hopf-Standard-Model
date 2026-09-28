# BHSM Foundational Closure: Absolute Scale Bridge and Dimensional Consistency

**Status:** Candidate canonical closure note for repository integration
**Scope:** Objections 1–2: propagation/localization radius and dimensional action coupling
**Date:** 2026-09-28

## Executive result

The scale objection must be split into three mathematically distinct questions.

1. **Relative-scale closure:** Can the BHSM action fix dimensionless ratios such as
   \[
   r_{\rm prop}/\ell_\star,\qquad M_{\rm BH}/M_\star,
   \]
   and therefore predict mass ratios or a complete spectrum in units of one common scale?

2. **Calibration closure:** Can one measured dimensionful observable fix the single common scale
   \(\ell_\star\) (equivalently \(M_\star=\ell_\star^{-1}\) in natural units), after which all
   action-derived dimensionless ratios become physical predictions?

3. **Absolute-unit generation:** Can a classical action containing only dimensionless geometric
   data generate a unique nonzero value of \(\ell_\star\) in metres or \(M_\star\) in GeV with
   no dimensionful input, anomaly scale, boundary scale, or calibration?

The current BHSM record supports the following claim boundary:

- relative dimensionless scale relations may be derived conditionally;
- one common physical scale may be calibrated, provided it is explicitly identified as a calibration;
- the current classical action does **not** generate an absolute unit from dimensionless data alone.

This is not merely a missing numerical calculation. Under the assumptions below it is a
scale-covariance obstruction.

---

## 1. Physical mass map

Let the dimensionless Berger-space eigenproblem be

\[
-\widehat{\Delta}\,Y_n=\lambda_nY_n ,
\]

where \(\lambda_n\) is dimensionless. If the physical propagation/localization radius is

\[
r_{\rm prop}=c_{\rm prop}\,\ell_\star ,
\]

with \(c_{\rm prop}\) dimensionless, then

\[
-\Delta_{\rm phys}Y_n
=
\frac{\lambda_n}{r_{\rm prop}^{2}}Y_n .
\]

For a Klein--Gordon-type quadratic fluctuation,

\[
m_n^2
=
\frac{\lambda_n}{r_{\rm prop}^{2}}
\quad(\hbar=c=1),
\]

so

\[
\boxed{
m_n
=
\frac{\sqrt{\lambda_n}}{c_{\rm prop}}\,M_\star ,
\qquad M_\star=\ell_\star^{-1}.
}
\]

Restoring units,

\[
\boxed{
m_n c^2
=
\frac{\hbar c}{r_{\rm prop}}\sqrt{\lambda_n}.
}
\]

Therefore:

- the Berger spectrum can determine dimensionless mass ratios;
- an action-derived \(c_{\rm prop}\) can determine the localization radius **relative** to
  \(\ell_\star\);
- an absolute GeV value requires one physical scale \(M_\star\).

A separate fitted \(r_{\rm prop}\) for each particle or sector would destroy predictive power.
A single universal \(M_\star\), fixed once and then propagated through action-derived ratios,
is a different and much weaker assumption.

---

## 2. Classical scale-generation no-go statement

### Proposition

Suppose a classical reduced BHSM action contains:

1. only dimensionless couplings and topological integers;
2. no dimensionful boundary tension, gravitational normalization, condensate, external length,
   renormalization scale, or other dimensional datum;
3. a global scale modulus \(L>0\) introduced only by
   \(g_{\mu\nu}=L^2\widehat g_{\mu\nu}\) (or the corresponding spatial scaling);
4. no quantum anomaly that introduces a transmutation scale.

Then variation of that classical action cannot select a unique finite nonzero absolute value of
\(L\) in physical units.

### Proof sketch

Under \(L\mapsto aL\), a curvature invariant containing \(2n\) derivatives scales as

\[
\mathcal I_n \mapsto a^{-2n}\mathcal I_n ,
\]

while a \(D\)-dimensional volume element scales as

\[
dV \mapsto a^D dV .
\]

Hence a term with a dimensionless coefficient scales as

\[
S_n(L)=C_nL^{D-2n}.
\]

If the action has only one homogeneous scaling power,

\[
S(L)=CL^q,
\]

then

\[
\frac{dS}{dL}=qCL^{q-1}.
\]

For \(q\neq0\), there is no isolated finite nonzero stationary point unless \(C=0\).
For \(q=0\), \(L\) is a flat modulus and is not selected.

If different powers of \(L\) are added to stabilize \(L\), dimensional consistency requires
their coefficients to carry compensating dimensions unless an additional physical mechanism
supplies a scale. Dimensionless topology can quantize ratios or flux numbers but cannot turn
a pure number into metres or GeV.

Thus a unique absolute scale requires at least one of:

- a dimensionful action coefficient or boundary tension;
- a gravitational normalization such as a Planck scale;
- a physical boundary/initial-condition scale;
- a condensate whose normalization is itself physically fixed;
- quantum dimensional transmutation together with a physical renormalization condition;
- one empirical dimensionful calibration.

QED within the stated assumptions.

---

## 3. What this means for \(r_{\rm prop}\)

The correct dynamical target is not

> "derive a number of femtometres from dimensionless eigenvalues alone."

It is

\[
\boxed{
\text{derive }c_{\rm prop}=r_{\rm prop}/\ell_\star
\text{ from the action and prove it is a stable stationary value.}
}
\]

Let the reduced effective action contain moduli \(q^A=(c_{\rm prop},s,\ldots)\):

\[
S_{\rm red}
=
\int d^4x\sqrt{-g_4}
\left[
\frac12G_{AB}(q)\partial_\mu q^A\partial^\mu q^B
-
M_\star^4\,U(q)
\right].
\]

A localization radius is dynamically closed when

\[
\partial_A U(q_\star)=0
\]

and the gauge/constraint-reduced Hessian satisfies

\[
v^A\left(\nabla_A\nabla_BU\right)_{\star}v^B>0
\]

for every non-gauge physical perturbation \(v\neq0\).

Then

\[
r_{\rm prop}=c_{\rm prop,\star}\ell_\star
\]

is derived relative to the common scale.

If no such stationary \(c_{\rm prop,\star}\) exists, the mass formula remains kinematic.

---

## 4. Dimensional consistency of curvature-to-energy terms

The statement that BHSM must "derive \(\hbar\) and \(c\)" from the metric is not the correct
field-theory requirement. \(\hbar\) and \(c\) may be restored as unit-conversion constants.
The substantive question is whether the action contains the required dimensionful
normalization.

In four-dimensional natural units,

\[
[x]=-1,\qquad [\partial]=1,\qquad [R]=2,\qquad [\mathcal L]=4.
\]

Therefore:

| Structure | Mass dimension | Required coefficient |
|---|---:|---:|
| \(R\) | 2 | \(M^2\) |
| \(R^2\) | 4 | dimensionless |
| \((\partial\phi)^2\) with \([\phi]=1\) | 4 | dimensionless |
| \(\phi^2R\) | 4 | dimensionless |
| constant vacuum energy | 0 before coefficient | \(M^4\) |
| 3D boundary tension term | 3 | \(M^3\) |
| \(F_{\mu\nu}F^{\mu\nu}\) | 4 | dimensionless \(1/g^2\) |

Consequently, a linear curvature term interpreted as an energy-density contribution requires
a scale such as

\[
M_\star^2R.
\]

Newton's constant \(G\) is required only if that coefficient is specifically identified with
Einstein gravity,

\[
M_{\rm Pl}^2\sim G^{-1}.
\]

Internal Berger curvature does not automatically require \(G\); it requires whatever
dimensionful normalization the BHSM action assigns to that operator.

Thus the precise obstruction is:

\[
\boxed{
\text{dimensionless internal curvature cannot by itself equal a physical energy density.}
}
\]

The missing object is a dimensionally correct action normalization, not a derivation of unit
conversion constants.

---

## 5. Repository claim boundary

The canonical BHSM status should distinguish:

### DERIVED / conditionally derivable

- dimensionless Berger eigenvalues and mode ratios;
- dimensionless radius or mass ratios when obtained from a stationary reduced action;
- a universal mapping
  \[
  m_n/M_\star=\sqrt{\lambda_n}/c_{\rm prop}
  \]
  once both \(\lambda_n\) and \(c_{\rm prop}\) are action-derived.

### CALIBRATED, not generated

- one universal physical scale \(M_\star\) or \(\ell_\star\), if fixed from one explicitly
  declared measured dimensionful observable;
- all subsequent predictions must use that same calibration without sector-by-sector retuning.

### NOT DERIVED by the present classical scale-free action

- a metre/GeV absolute unit from dimensionless topology alone;
- a unique physical \(r_{\rm prop}\) if \(c_{\rm prop}\) is not a stable stationary solution;
- a physical energy density obtained by equating curvature directly to mass density without
  the required action normalization.

---

## 6. Closure tests

Objection 1 is **structurally addressed** when the repository demonstrates:

1. \(r_{\rm prop}=c_{\rm prop}\ell_\star\);
2. \(c_{\rm prop}\) is obtained from the Euler--Lagrange equations;
3. the physical Hessian at \(c_{\rm prop}\) is positive;
4. the same \(\ell_\star\) is used in every sector;
5. no measured particle mass is used to retune \(c_{\rm prop}\).

It is **absolute-unit closed** only if BHSM additionally provides an allowed scale-generating
mechanism for \(\ell_\star\), or explicitly downgrades the stronger claim and retains one
physical calibration.

Objection 2 is **dimensionally closed** when every term in the physical action has the correct
mass dimension and every dimensionful coefficient has explicit provenance.

---

## 7. Immediate implications for future audits

Future assessments should **not** state:

> "BHSM fails because a dimensionless Berger eigenvalue cannot produce GeV unless \(\hbar,c,G\)
> are dynamically derived."

That conflates unit restoration with dynamical normalization.

The accurate statement is:

> "BHSM can derive dimensionless spectral structure and, if the localization modulus is
> action-fixed, masses in units of one universal scale. Its current classical scale-free
> geometry does not generate an absolute unit from dimensionless data alone; any physical
> GeV prediction must therefore identify one universal scale source or one explicit
> dimensionful calibration."

This is the claim that should be kept synchronized with `CLAIMS.md`,
`docs/current_bhsm_status.md`, and any scale/neutral-radius audit.

---

## 8. Next mathematical object

The next calculation is the **action-derived dimensionless localization stationary point**:

\[
\boxed{
\partial_{c_{\rm prop}}U
=
\partial_sU
=
\cdots
=0,
\qquad
H_{\rm phys}>0.
}
\]

That calculation determines whether the old \(r_{\rm prop}\) objection reduces to one common
absolute-scale calibration or whether an additional localization mechanism is still missing.
