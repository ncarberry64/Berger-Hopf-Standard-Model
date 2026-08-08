# BHSM v14.0 — Eta-knot action completion audit

## Result

The recovered v13.1–v13.5 chain contains four reproducible advances:

- the retained (p=2+p=8) eta action has a degree-one, radially stable static
  solution in the equivariant sector;
- its odd topological sector admits the discrete FR fermionic quantization
  rule (2j=N\pmod 2);
- the oriented eta wall selects conjugate rank-three (G_2/SU(3))
  polarizations;
- a varying wall selector induces the canonical Grassmann connection
  (\nabla^P=P,d), with (F^P=P[dP,dP]P\in\mathfrak{su}(3)), and meson and
  baryon invariant tensors close exactly under this transport.

These results do not yet authorize the gauge-dressed meson or baryon boundary
value problem. The eta action is owned on (S_8). The independent
(SU(3)\times SU(2)\times U(1)) gauge connection and Yang–Mills density are
owned by the retained (S_{4,\mathrm{eff}}) action. The master-action ledger
explicitly records the gauge bundle/measure pushforward as missing. No current
action density jointly contains eta and the independent (SU(3)) connection.

Therefore

\[
\frac{\delta^2 S}{\delta\eta\,\delta A_{SU(3)}}=0
\]

for the retained block-separated action, and there is no eta-sourced
independent (SU(3)) Gauss equation to solve.

The exact next action object is:

`ACTION_OWNED_ETA_WALL_TO_M4_SU3_BUNDLE_PULLBACK_AND_CONNECTION_IDENTIFICATION_WITH_VARIATIONAL_GAUSS_LAW`

## Orientation, chirality, and flavor

For the degree-(+1) wall, (u_\eta) is selected by the oriented normal and
nonzero profile derivative. Reversing the physical degree branch gives

\[
\Pi_{10}(-u)=\Pi_{01}(u)=\Pi_{10}(u)^*,
\qquad
F^P(-u,-du)=F^P(u,du)^*.
\]

The two branches are distinct topological components, not rotations relative
to an external frame. This establishes a conjugate color-polarization branch.
It does not establish a boundary Dirac index: the action still lacks the
oriented boundary Dirac operator and its self-adjoint domain, so

\[
\operatorname{Index}D_{\rm rel}
\quad\text{and}\quad
\eta(D_{\partial,\Omega})
\]

remain unevaluated.

The projector connection acts on the color factor as

\[
A^P_{\rm color}\otimes I_{C_3}.
\]

It consequently commutes with the exact (C_3) family cycle and cannot source
a family-noncentral up/down charged current. When the relative orientation is
removed, (du_\eta=0), (F^P=0), and the family weak current remains (I_3),
preserving the v11.6 unoriented no-go result.

No (K_{ud}) is inserted and no CKM invariant is emitted. The independent
flavor provenance object remains:

`PARENT_ACTION_DERIVATION_OR_UNIQUENESS_SELECTION_OF_THE_SPECTRAL_CHARGED_CURRENT_KERNEL`

## Candidate action completion

After declaring a covariant eta-wall-to-(M_4) bundle map, the smallest
no-new-field, no-new-continuous-coefficient composite replacement candidate is

\[
S_{P,\mathrm{candidate}}
=-
\frac{1}{4g_3^2}
\int_{M_4}\sqrt{-h}\,
\operatorname{tr}(F^P_{\mu\nu}F_P^{\mu\nu}).
\]

It uses the retained (g_3), metric, eta selector, and projector connection.
It vanishes for constant relative orientation. It is classified only as a
candidate action completion: the current action neither declares the required
bundle map nor proves that this replacement is unique. Retaining an
independent (A_{SU(3)}) instead requires an additional covariant compatibility
relation between (A_{SU(3)}) and (A^P).

## Numerical boundary

The static eta profile was independently re-run from three materially
different initial slopes. They converge to the same branch, with

\[
E_8/E_2\simeq 5,
\]

and the finite-interval radial Jacobi spectrum remains positive. This is not a
gauge-dressed singlet solution. The coupled BVP, Gauss residual, constrained
nonradial Hessian, Berry connection, and family response Hessians must wait for
the common-domain action object above.

## Completion status

- Static eta-knot subgate: reached conditionally.
- FR fermionic quantization subgate: reached conditionally.
- Eta-wall color projector geometry: reached conditionally.
- Meson/baryon covariant singlet closure: reached.
- Action-derived chiral index: not reached.
- Gauge-dressed singlet BVP: blocked before numerical solution.
- Nontrivial CKM/flavor action: not closed.
- BHSM physical completion: not reached.
