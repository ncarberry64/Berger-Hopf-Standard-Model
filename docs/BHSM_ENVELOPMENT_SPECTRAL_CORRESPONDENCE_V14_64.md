# BHSM v14.64 — Global Envelopment Spectral Correspondence

## Status

**Primary verdict**

`BHSM_V14_64_GLOBAL_ENVELOPMENT_CAN_CANONICALLY_FIX_THE_STRATUM_INCIDENCE_GRAPH_GEOMETRIC_L2_MEASURES_AND_EDGE_MAGNITUDES_AFTER_DISTANCE_MATCHING_BUT_THE_NAIVE_DIRECT_SUM_L2_SPECTRAL_TRIPLE_IS_NOT_A_VALID_CONTINUUM_REALIZATION_BECAUSE_BULK_TO_BOUNDARY_TRACE_MAPS_ARE_UNBOUNDED_ON_L2_AND_THE_TWO_CAP_DIAMOND_RETAINS_ONE_GAUGE_INVARIANT_LOOP_HOLONOMY_SO_THE_CORRECT_MICROSCOPIC_OBJECT_IS_A_RELATIVE_BOUNDARY_OR_UNBOUNDED_CORRESPONDENCE_OPERATOR_WITH_AN_ACTION_DERIVED_DOMAIN`

**BHSM physical completion:** `FALSE`
**Mark III:** `NOT_REACHED`
**Frozen predictions changed:** `NO`
**Official prediction logic changed:** `NO`
**Physical prediction emitted:** `NO`
**USB touched:** `NO`

---

## 1. Question tested

v14.63 showed that an unspecified cutoff spectral action does not remove the mixed-dimensional coefficient freedom because its heat moments remain functionally independent until a microscopic profile, trace, and finite Dirac structure are defined.

v14.64 asks the strongest geometry-first follow-up:

> Does the already-declared global envelopment geometry itself determine enough of a stratified spectral object to remove those choices without fitting particle data?

The answer is **partly yes**. The geometry fixes considerably more than v14.63 credited, but the correct continuum object is not a naive finite direct-sum spectral triple.

The source architecture retained from the repository is the stratified correspondence

\[
M_8 \longrightarrow M_{5,+},M_{5,-}\longrightarrow M_4,
\]

with the two caps sharing the same equatorial \(M_4\) and with geometric measures already defined on every stratum.

---

## 2. The envelopment incidence graph is fixed

At the level of incidence, the global geometry gives a four-vertex diamond:

\[
M_8\leftrightarrow M_{5,+}\leftrightarrow M_4,
\qquad
M_8\leftrightarrow M_{5,-}\leftrightarrow M_4.
\]

It has

\[
V=4,\qquad E=4,\qquad b_1=E-V+1=1.
\]

Therefore there is exactly one independent cycle in the reduced incidence graph.

For a finite Hermitian incidence witness,

\[
(D_{\rm inc})_{ij}=\frac{e^{i\alpha_{ij}}}{\ell_{ij}},
\]

where \(\ell_{ij}>0\) is the corresponding envelopment/collar length.

If one imposes the **edge-restricted Connes-distance calibration**

\[
d_{ij}=\ell_{ij},
\]

then the magnitude is fixed:

\[
\boxed{|D_{ij}|=\ell_{ij}^{-1}.}
\]

This does not claim that the full continuum Connes metric on the diamond has already been proved equal to the classical stratified distance. It is the exact two-point calibration on each incidence edge.

Thus the edge magnitudes cease to be arbitrary once the global stationary solution supplies the physical nesting/collar lengths.

---

## 3. One phase survives all vertex rephasings

Under vertex phase changes

\[
D\mapsto UDU^\dagger,
\qquad
U=\operatorname{diag}(e^{i\theta_8},e^{i\theta_+},e^{i\theta_-},e^{i\theta_4}),
\]

three independent edge phases can be removed, but one loop phase remains:

\[
\Phi_\diamond
=\alpha_{8+}+\alpha_{+4}-\alpha_{-4}-\alpha_{8-}
\pmod{2\pi}.
\]

The executable witness verifies both spectral invariance and holonomy invariance under a nontrivial vertex gauge transformation.

This is useful for the flavor/CP program, but it is **not** permission to choose \(\Phi_\diamond\) to reproduce a measured CP phase. Its value must come from the action-owned connection, orientation/reflection structure, or the dynamical moving-seam orbit.

**Verdict:** the envelopment graph has one genuine holonomy degree of freedom, not four arbitrary edge phases.

---

## 4. Cross-stratum trace normalization is less arbitrary than v14.63 assumed

Once the microscopic Hilbert object is declared to be the geometric direct sum

\[
\mathcal H
=\mathcal H_8\oplus\mathcal H_{5,+}\oplus\mathcal H_{5,-}\oplus\mathcal H_4,
\]

with each \(\mathcal H_s\) built from the already-defined geometric \(L^2\) measure, the standard Hilbert trace is simply

\[
\operatorname{Tr}_{\mathcal H}
=\operatorname{Tr}_8+
\operatorname{Tr}_{5,+}+
\operatorname{Tr}_{5,-}+
\operatorname{Tr}_4.
\]

There is no need to introduce fitted positive weights \(w_s\operatorname{Tr}_s\). The two M5 contributions occur because the geometry contains two caps, not because a coefficient was tuned.

This closes a portion of the v14.63 “cross-stratum trace normalization” ambiguity **conditional on accepting the geometric direct-sum correspondence**.

It does **not** solve the operator-domain problem described next.

---

## 5. The naive continuum direct-sum spectral triple fails

The finite incidence matrix is only a theorem witness. The actual correspondence between a bulk field and its seam value uses a trace/restriction map.

A trace from bulk \(L^2\) to boundary \(L^2\) is not bounded.

The package uses the exact normalized boundary-layer family on \([0,1]\),

\[
u_n(x)
=\sqrt{\frac{2n}{1-e^{-2n}}}\,e^{-nx}.
\]

It satisfies

\[
\|u_n\|_{L^2([0,1])}=1,
\]

while

\[
|u_n(0)|
=\sqrt{\frac{2n}{1-e^{-2n}}}
\sim\sqrt{2n}\to\infty.
\]

Therefore no constant \(C\) can satisfy

\[
\|\operatorname{Tr}_{\partial}u\|_{L^2(\partial M)}
\le C\|u\|_{L^2(M)}
\]

for all bulk \(L^2\) fields.

So the compatibility block cannot simply be inserted as a bounded finite-Dirac edge between continuum \(L^2\) spaces.

The correct object must carry explicit Sobolev/domain information, for example through a boundary triple, Calderon projector, Wentzell/dynamic boundary realization, relative spectral triple, or unbounded Kasparov correspondence.

This is a **mathematical reclassification**, not a failure of global envelopment.

---

## 6. Heat-semigroup branch collapses the cutoff-profile ambiguity

There is one especially economical microscopic branch.

For a positive self-adjoint operator \(P\), its canonical diffusion semigroup is

\[
K_t=e^{-tP}.
\]

At the scalar spectral level, suppose \(f_t(u)\) satisfies

\[
f_0(u)=1,
\qquad
f_{t+s}(u)=f_t(u)f_s(u),
\]

is continuous in \(t\), and has generator normalization

\[
\left.\frac{\partial f_t(u)}{\partial t}\right|_{t=0}=-u.
\]

Then

\[
\boxed{f_t(u)=e^{-tu}.}
\]

Thus if BHSM **predeclares** the microscopic functional to be

\[
\Gamma_{\rm heat}(t)=\operatorname{STr}e^{-tP},
\]

the generic v14.63 cutoff-profile freedom disappears. In the normalized exponential convention, the heat moments are fixed by

\[
F_p=a^{-p/2},
\]

and at unit dimensionless rate all retained normalized moments are one.

This is substantial compression.

But it is essential not to overstate it:

\[
\boxed{\text{canonical heat semigroup of }P}
\]

is mathematically canonical **after \(P\) is known**, whereas

\[
\boxed{\text{the microscopic action is }\operatorname{STr}e^{-tP}}
\]

is an additional physical action principle. The current BHSM archive does not derive that latter statement.

Therefore v14.64 records this as an available foundational branch, not as an automatically adopted completion rule.

---

## 7. Finite Dirac/Yukawa data are reclassified as stationary-background derivatives

The zero-input branch should not insert a measured Yukawa matrix into the microscopic operator.

Instead, after the complete global stationary configuration \(\Phi_\star\) has been solved, define

\[
D_{\rm eff}
=
\left.
\frac{\delta^2\Gamma}
{\delta\bar\Psi\,\delta\Psi}
\right|_{\Phi_\star}.
\]

Likewise the charged-current and moving-seam vertices are

\[
\Gamma_+
=
\left.
\frac{\delta^3\Gamma}
{\delta W^+\,\delta\bar\Psi_u\,\delta\Psi_d}
\right|_{\Phi_\star},
\]

\[
\Gamma_{+,X}^{Lr}
=
\left.
\frac{\delta^4\Gamma}
{\delta q_{Lr}\,\delta W^+\,\delta\bar\Psi_u\,\delta\Psi_d}
\right|_{\Phi_\star}.
\]

This is exactly compatible with the moving-seam/noncentral flavor program developed in v14.54-v14.57: flavor data become derivatives of the globally selected orbit rather than arbitrary static matrices.

The reclassification does not yet numerically close flavor because the continuum microscopic \(\Gamma\) and its self-adjoint domain are still missing.

---

## 8. Validated / invalidated / reclassified / open

### Validated

- The envelopment architecture fixes a two-cap diamond incidence graph.
- Its cycle rank is exactly one.
- Edge-restricted distance matching fixes incidence magnitudes once geometric edge lengths are selected by the global solution.
- One gauge-invariant loop holonomy survives vertex rephasing.
- The geometric direct-sum Hilbert trace removes the need for arbitrary fitted stratum trace weights.
- The naive bulk-L2 to boundary-L2 trace map is unbounded.
- Strongly continuous normalized diffusion semigroup composition fixes the scalar profile to \(e^{-tu}\).
- A heat-trace microscopic branch would remove the generic cutoff-profile freedom from v14.63.

### Invalidated

- “The finite diamond incidence matrix is already the exact continuum stratified spectral triple.”
- “All edge phases can be gauged away.”
- “The current BHSM action already proves that the microscopic action must be the heat trace.”

### Reclassified

- The missing “global spectral triple” is more accurately a **relative/boundary spectral correspondence with a self-adjoint domain**.
- Cross-stratum trace normalization is largely geometric once the direct-sum correspondence is accepted.
- Cutoff-profile freedom can be compressed to an explicit foundational branch choice.
- Finite flavor/Yukawa entries should be stationary-background derivative outputs on the zero-input branch.

### Open

- construct the continuum boundary correspondence operator;
- derive its Calderon/boundary-triple domain from the global action;
- derive the single diamond holonomy from connection/orientation data;
- decide the microscopic functional before physical comparison;
- include the complete ghost and zero-mode quotient;
- evaluate mixed-dimensional heat coefficients with boundaries;
- solve the actual global stationary parent-child background;
- derive the effective fermion/current operators;
- run branch exhaustion, Hessian, DtN, relative heat kernel, neutrino kill screen, and only then downstream physical predictions.

---

## 9. Completion status

The v14.59 inverse-cap deadlock remains bypassed. v14.60-v14.62 global-envelopment and coefficient-provenance progress is retained. v14.63's generic cutoff-moment independence result remains valid but is now narrowed: a canonical heat-semigroup branch can eliminate that functional freedom if adopted before comparison.

However the continuum cross-stratum operator/domain is not yet constructed and the heat-trace action has not been derived from the current BHSM axioms.

Therefore:

`FULL_BHSM_COMPLETE = FALSE`

`MARK_III = NOT_REACHED`

`USB_TOUCHED = FALSE`

No physical masses, couplings, CKM/PMNS entries, CP phases, neutrino splittings, or cross sections are emitted.

---

## 10. Exact next object

`ACTION_DERIVED_RELATIVE_BOUNDARY_SPECTRAL_CORRESPONDENCE_OR_UNBOUNDED_KK_CYCLE_FOR_M8_TO_M5_PLUS_MINUS_TO_M4_WITH_CALDERON_OR_BOUNDARY_TRIPLE_DOMAIN_GEOMETRIC_EDGE_LENGTHS_GAUGE_GHOST_COMPLETION_AND_PREDECLARED_HEAT_SEMIGROUP_OR_OTHER_MICROSCOPIC_FUNCTIONAL_THEN_DERIVE_THE_FULL_HEAT_COEFFICIENTS_FINITE_FERMION_OPERATOR_GLOBAL_ENVELOPMENT_STATIONARY_BRANCH_DTN_RELATIVE_HEAT_KERNEL_AND_ZERO_RETUNING_NEUTRINO_KILL_SCREEN`
