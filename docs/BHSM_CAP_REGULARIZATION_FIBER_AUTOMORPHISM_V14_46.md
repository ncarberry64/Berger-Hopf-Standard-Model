# BHSM v14.46 — Compact-cap regularity, Hopf-fiber automorphism, and neutron-star bridge

## Primary verdict

`BHSM_SMOOTH_CAP_REGULARITY_AND_TRUE_HOPF_BUNDLE_AUTOMORPHISMS_DO_NOT_FIX_C2REN_C4REN_BECAUSE_THE_CURVATURE_INVARIANTS_ARE_SEPARATELY_REGULAR_AND_FIBER_STRETCHING_IS_A_MODULUS_DEFORMATION_NOT_A_BUNDLE_AUTOMORPHISM`

## Secondary verdict

`PROMOTING_THE_BERGER_ANISOTROPY_TO_A_DYNAMICAL_MODULUS_SUPPLIES_AT_MOST_ONE_STATIONARITY_RELATION_AND_DOES_NOT_REMOVE_THE_TWO_COUNTERTERM_RENORMALIZATION_FREEDOM`

## Bridge verdict

`THE_COVARIANT_4D_TO_CAP_PROJECTION_AND_NEUTRON_STAR_EQUATION_CONTRACT_ARE_FORMULATED_BUT_NO_ASTROPHYSICAL_MATCHING_IS_EXECUTED_WITHOUT_THE_CAP_PROJECTION_NORMALIZATION_EOS_MARGINALIZATION_AND_PREREGISTERED_DATA_SPLIT`

---

## 1. Question

The v14.45 determinant gate has two local renormalized coefficients,

\[
\Lambda_L^{\rm ren}
=
c_2^{\rm ren}q_L
+c_4^{\rm ren}q_L^2
+\Pi_L^{\rm nonlocal},
\qquad
q_L=(L-1)(L+3),
\]

with

\[
q_2=5,
\qquad
q_3=12.
\]

The two critical channels are independent because

\[
\det
\begin{pmatrix}
5&25\\
12&144
\end{pmatrix}
=420.
\]

This sprint tests two proposed internal mechanisms before allowing external neutron-star matching:

1. smooth compact-cap regularity;
2. Hopf-bundle automorphism or fiber-stretch invariance.

It then formulates the covariant four-dimensional and stellar equations required for a later no-fit astrophysical bridge.

---

## 2. Covariant local operator basis

Use the four-dimensional effective action

\[
\Gamma_{4D}
=
\int d^4x\sqrt{-g}
\left[
\frac{M^2}{2}R-\Lambda
+\alpha R^2
+\beta R_{\mu\nu}R^{\mu\nu}
\right]
+\Gamma_{\rm nonlocal}
+S_{\rm matter}.
\]

In four dimensions a Riemann-squared term may be traded for this basis plus the Euler density and its boundary transgression.  The Euler coefficient is topological on a smooth closed manifold and does not supply an additional local field equation.

The bulk field equation is

\[
M^2G_{\mu\nu}
+2\alpha H^{(1)}_{\mu\nu}
+\beta H^{(2)}_{\mu\nu}
+H^{\rm nonlocal}_{\mu\nu}
=T_{\mu\nu},
\]

where

\[
H^{(1)}_{\mu\nu}
=
RR_{\mu\nu}
-\frac14g_{\mu\nu}R^2
+g_{\mu\nu}\Box R
-\nabla_\mu\nabla_\nu R,
\]

and

\[
H^{(2)}_{\mu\nu}
=
2R_{\mu\alpha\nu\beta}R^{\alpha\beta}
-\frac12g_{\mu\nu}R_{\alpha\beta}R^{\alpha\beta}
+\Box R_{\mu\nu}
+\frac12g_{\mu\nu}\Box R
-\nabla_\mu\nabla_\nu R.
\]

The compact-cap projection of each local invariant is defined by

\[
\mathcal H_L[I_i]
=
\frac{1}{\|\beta_L\|^2}
\delta^2
\int\sqrt g\,I_i
\bigg|_{\beta_L}.
\]

Given the total local channel projections \(\mathcal H_2,\mathcal H_3\), the BHSM coefficients are

\[
\boxed{
c_2^{\rm ren}
=
\frac{144\mathcal H_2-25\mathcal H_3}{420},
}
\]

\[
\boxed{
c_4^{\rm ren}
=
\frac{-12\mathcal H_2+5\mathcal H_3}{420}.
}
\]

This is the exact covariant-to-cap projection contract.  The numerical columns \(\mathcal H_L[R^2]\) and \(\mathcal H_L[R_{\mu\nu}^2]\) remain open because the complete compact-cap background and normalized coexact modes have not yet been supplied.

---

## 3. Exact boundary variation at a smooth cap

For any local Lagrangian depending algebraically on the Riemann tensor, define

\[
P^{\mu\nu\alpha\beta}
=
\frac{\partial\mathcal L}{\partial R_{\mu\nu\alpha\beta}}.
\]

The metric symplectic potential can be written as

\[
\Theta^\mu
=
2P^{\mu\alpha\beta\nu}\nabla_\nu\delta g_{\alpha\beta}
-2\nabla_\nu P^{\mu\alpha\beta\nu}\delta g_{\alpha\beta}.
\]

The apparent cap contribution is

\[
\delta\Gamma\big|_{\rm cap}
=
\lim_{\rho\to0}
\int_{\Sigma_\rho}d\Sigma_\mu\,\Theta^\mu.
\]

A smooth cap is not a physical boundary.  It is a regular origin written in collapsing-fiber coordinates.  In an orthonormal smooth frame:

- curvature and its admissible variations are finite;
- the collapsing \(S^3\) measure scales as \(\rho^3\);
- a regular coexact level-\(L\) field behaves no worse than \(u_L\sim\rho^{L-1}\).

The worst fourth-order Green concomitant contains one undifferentiated mode and three derivatives of the second mode.  Its radial power is

\[
\rho^3\,u_L\,\delta u_L^{(3)}
\sim
\rho^{2L-2}.
\]

Thus

\[
L=2:\quad \rho^2\to0,
\]

\[
L=3:\quad \rho^4\to0.
\]

The \(R^2\) and \(R_{\mu\nu}R^{\mu\nu}\) boundary fluxes therefore vanish **separately** for the two critical channels.  No cancellation between their coefficients is required.

### Consequence

\[
\boxed{
\text{Smooth cap regularity does not impose }
A c_2^{\rm ren}+B c_4^{\rm ren}=0.
}
\]

If the cap is artificially cut and treated as a physical boundary, a well-posed fourth-order variational problem requires appropriate boundary data or generalized boundary functionals for each invariant.  Cancelling unrelated boundary terms against one another would depend on a restricted variation and would not constitute a robust coefficient theorem.

A genuine cap anomaly could change this conclusion, but no such anomaly functional has been derived in the present BHSM action.

---

## 4. True Hopf-bundle automorphisms

For a Berger metric written schematically as

\[
h_a
=
R^2\left(\sigma_1^2+\sigma_2^2+a^2\sigma_3^2\right),
\]

true principal-bundle automorphisms include:

- fiber \(U(1)\) translations and gauge transformations;
- compatible base diffeomorphisms;
- the generic Berger isometry group \(SU(2)_L\times U(1)_R\).

Every covariant scalar invariant is separately invariant under these transformations.  Their Ward identities enforce covariance and transversality; they do not relate \(\alpha\) and \(\beta\), or equivalently \(c_2^{\rm ren}\) and \(c_4^{\rm ren}\).

### Fiber stretching is not an automorphism

The transformation

\[
a\longrightarrow e^\tau a
\]

changes the metric modulus.  It is not a gauge transformation or an isometry of a fixed generic Berger geometry.

For a channel with Hopf weight \(p\), use the standard deformation

\[
q_{L,p}(a)
=
q_L+(a^2-1)p^2.
\]

Then

\[
\frac{d}{d\log a}
\left[
c_2q_{L,p}+c_4q_{L,p}^2
\right]
=
2a^2p^2
\left[c_2+2c_4q_{L,p}\right].
\]

Demanding this vanish mode by mode for two distinct channel costs forces the trivial local solution

\[
c_2=c_4=0.
\]

That would remove the local renormalized Hessian rather than derive its physical ratio.  It demonstrates that modewise fiber-stretch invariance is too strong and is not a symmetry of the fixed Berger model.

---

## 5. Dynamical anisotropy modulus

A legitimate internal route remains possible if \(a\) is promoted to a field or collective modulus and varied in the complete effective action.

The stationarity condition has the form

\[
0
=
\frac{d\Gamma}{d\log a}
=
c_2^{\rm ren}\mathcal A_2'(a)
+c_4^{\rm ren}\mathcal A_4'(a)
+\Pi_{\rm nonlocal}'(a).
\]

This is one scalar equation.  Generically it reduces the two-dimensional coefficient plane to one line:

\[
\boxed{
\dim\{c_2,c_4\}:2\longrightarrow1.
}
\]

It does not fix both coefficients.  A second independent condition would still be required, such as:

- a second dynamical modulus;
- a microscopic normalization or anomaly condition;
- one declared physical renormalization condition.

The current BHSM anisotropy is frozen as structural input rather than derived from a modulus Euler equation.  Therefore even this one-line reduction is conditional and cannot yet be promoted.

---

## 6. Internal-route verdict

### Validated

- The cap variation can be written with the exact curvature-action symplectic potential.
- Smooth-cap fluxes vanish separately in the \(L=2\) and \(L=3\) channels.
- True Hopf-bundle automorphisms leave each covariant invariant separately invariant.
- Fiber stretching is a physical Berger-modulus deformation, not a bundle automorphism.
- One dynamical anisotropy modulus gives at most one coefficient relation.

### Invalidated

- Fixing the counterterm ratio by cross-cancelling separately regular cap fluxes.
- Treating arbitrary fiber-length scaling as gauge symmetry.
- Claiming the internal geometry already fixes both coefficients.

### Reclassified

The strongest BHSM-native continuation is now:

\[
\boxed{
\text{derive a dynamical Berger modulus and one additional independent
microscopic renormalization condition.}
}
\]

---

## 7. Neutron-star equation contract

The external bridge uses the same covariant action only after the cap projection is established.

For a static spherical star,

\[
ds^2
=
-e^{2\Phi(r)}dt^2
+\left(1-\frac{2m(r)}{r}\right)^{-1}dr^2
+r^2d\Omega^2,
\]

with

\[
T^\mu{}_{\nu}
=
\operatorname{diag}(-\rho,p,p,p),
\qquad
p=p(\rho).
\]

The higher-derivative stellar problem is the boundary-value system

\[
E^t{}_t[g;\alpha,\beta,\Gamma_{\rm nonlocal}]
=-\rho,
\]

\[
E^r{}_r[g;\alpha,\beta,\Gamma_{\rm nonlocal}]
=p,
\]

\[
p'=-(\rho+p)\Phi',
\]

with the angular equation as an independent higher-derivative equation or consistency condition.

Regular center data require

\[
m(r)=O(r^3),
\qquad
\Phi(0)<\infty,
\qquad
\rho(0)<\infty,
\]

plus regularity of every auxiliary curvature variable introduced to reduce the fourth-order system.

At the stellar surface,

\[
p(R_\star)=0,
\]

and the metric plus all required higher-derivative matching data must connect to the declared vacuum exterior.

### Radial stability

Use a Lagrangian displacement \(\xi(r)e^{i\omega t}\) together with the curvature-sector perturbations.  The linearized problem is

\[
\mathcal L_{\rm rad}Y
=
\omega^2\mathcal W_{\rm rad}Y,
\]

with regular-center conditions and vanishing Lagrangian pressure perturbation at the surface.  Stability requires

\[
\boxed{\omega_0^2>0.}
\]

### Tidal response

Solve the static even-parity \(\ell=2\) perturbation system through the stellar surface and exterior.  The ratio of the decaying response coefficient to the applied tidal-source coefficient defines the Love number and dimensionless tidal deformability.

---

## 8. No-fit matching architecture

The neutron-star layer is explicitly separated from the internal theorem.

### Calibration layer

- predeclare which observables are used as renormalization conditions;
- use an explicit equation-of-state family and marginalize over it;
- infer an allowed coefficient region rather than choose values by eye;
- freeze \(\alpha,\beta\), the scale, and subtraction convention after calibration.

### Held-out layer

Predict observables not used in calibration, such as another star's radius, a tidal deformability, a moment of inertia, or a radial-stability threshold.

### Kill conditions

The bridge fails if:

- coefficients must be retuned for each star or EOS;
- the calibrated theory lacks regular stable stars;
- held-out observables fail;
- the inferred coefficient region is incompatible with the cap projection;
- the model requires identifying cap coefficients with 4D operators without calculating the projection.

No neutron-star data are consumed in v14.46.  No coefficient is fitted or emitted.

---

## 9. Completion status

BHSM remains incomplete.  Frozen predictions are unchanged.  No physical values of \(c_2^{\rm ren}\), \(c_4^{\rm ren}\), \(\alpha\), \(\beta\), \(\Pi_2\), \(\Pi_3\), neutron-star mass, radius, tidal deformability, CKM, CP phase, or absolute scale are emitted.  The USB remains untouched.

## Exact next object

`FULL_COMPACT_CAP_COVARIANT_HESSIAN_PROJECTION_FOR_R2_AND_RICCI2_TOGETHER_WITH_A_DYNAMICAL_BERGER_MODULUS_OR_MICROSCOPIC_RENORMALIZATION_CONDITION_AND_A_PREREGISTERED_EOS_MARGINALIZED_NEUTRON_STAR_MATCHING_PIPELINE`
