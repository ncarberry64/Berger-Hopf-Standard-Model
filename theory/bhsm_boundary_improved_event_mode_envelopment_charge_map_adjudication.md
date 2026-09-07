# BHSM boundary-improved event-mode/envelopment charge-map adjudication

## Result

The current BHSM action does **not** yet define either

\[
H_{\xi,\mathrm{mode}}^{\mathrm{avail}}
\quad\text{or}\quad
\Delta H_{\xi,\mathrm{child+seam}}
\]

on a common domain.  The obstruction occurs before a counterterm or reference
can be chosen: no common action-owned generator is tangent to the active
full-field event--child reset domain.  The classifications are

```text
XI5, CHG4, REF5, MODEE5, ENVH5, DOMH4, AE4R5.
```

This is a rigorous composition of existing BHSM negative theorems, not a
failure to import a generic GR formula.

## Registered action and boundary variation

The registered object is the stratified action complex

```text
S8 -> S5|4(caps+GHY+B1+matcher) -> S4eff.
```

It contains thirteen registered terms, but the two reduction maps are not
owned and the complex is not a single closed parent action on one moving
event--child domain.  Consequently its levelwise boundary variations can be
inventoried while their sum cannot be promoted to one full-field covariant
presymplectic potential.

The maximal formal expression is

\[
\Theta_{\rm formal}=
\Theta_{\rm EH+GHY}
+\Theta_{\chi,\sigma,q_D,H}
+\Theta_{\rm YM}
+\Theta_{\rm Dirac}
+\Theta_{\rm FP}
+\Theta_{\rm N12}
+\Theta_{\rm HS}.
\]

This expression is a ledger, not a differential form on a common phase
space.  The complete event, child, and relative potentials remain `None`.

| Sector | Theta contribution | Boundary term | Corner term | Ownership |
| --- | --- | --- | --- | --- |
| Geometry | EH potential plus Brown--York/GHY canonical metric pair | coefficient-locked GHY cancels normal derivatives of `delta g` | Hayward area/relative-angle pair on its separately declared moving geometric interface | levelwise regular caps only |
| Carrier/scalars | normal Legendre potentials for `chi`, `sigma`, Higgs, and regular `q_D` | Dirichlet or Neumann scalar term after an ensemble | no full-reset corner term | sectorwise; complete support action/ensemble open |
| Maxwell | weighted `1/g_i^2` Maxwell Green form | outward weighted Maxwell conormal | none | EFT Green form; boundary domain remains input |
| Fermion | first-order Dirac Green form | AE2 independent seam action is exactly zero | none | AE2 spin/gauge transmission graph only |
| Ghost/BRST | FP Green form and adjoint antighost relation | ghost/antighost conormals | none | sectorwise gauge-fixed Hessian, not a complete parent term |
| Higher-spin/HS | zero bare normal Green form | normal momentum is zero | none | rank-zero bare Legendre map; incidence open |
| N12 canonical | `p_I delta q^I` | finite-chart endpoint pair | none | reduced chart only, not a covariant full-field charge |
| AE3 `sigma=0` | opposite-normal same-action potentials cancel | internal GHY/Brown--York cancellation | none | local material carrier, not terminal reset boundary |
| AE4 retarded domain | no new covariant potential | no new boundary counterterm | none | causal domain class only; current child blocks remain unevaluated |

For the scalar portion, examples of actually owned levelwise terms are

\[
\Theta_\chi^A=-\sqrt{-G}\,Z_\chi(1+g\sigma^2)
\nabla^A\chi\,\delta\chi,
\]

\[
\Theta_\sigma^A=-\sqrt{-G}\,Z_\sigma
\nabla^A\sigma\,\delta\sigma,
\qquad
\Theta_D^A=-\sqrt{-G}\,\partial^Aq_D\,\delta q_D.
\]

These formulas retain BHSM coefficients and conventions, but they do not
repair the absent common domain.

## Generator adjudication: XI5

The desired relative transformation would act on a spatial attachment by

\[
\delta_\xi F=\xi_c\circ F-F_*\xi_e.
\]

The existing relative-generator audit proves the following failure order:

1. `F_B` is not a varied configuration argument.
2. The full-field reset graph has no `F_B` dependence or first variation.
3. Therefore `delta_xi F` is not tangent-defined on the active domain.
4. Therefore `Omega(delta X,delta_xi X)` cannot be evaluated.
5. Only afterward could complete `Theta`, `Q_xi`, `B_xi`, ensemble, and
   reference data be tested.

None of the apparent substitutes is a common generator.  The N12 forward
flow is within-side; the AE4 retarded prescription is a causal boundary value,
not a symmetry; the ordered event eigenline is not a spacetime vector field;
and the Hopf Killing rotor is a bulk spatial collective mode not identified
with event--child attachment time evolution.  No Killing field or coordinate
time translation is assumed.  Thus the classification is `XI5`.

## Differentiability and integrability: CHG4

Formally, a completed construction would require

\[
\delta H_\xi
=\sum_{s=e,c}\left(
C_s[\xi_s]+\int_{\partial\Sigma_s}
(\delta Q_{\xi_s}-\iota_{\xi_s}\Theta_s)
\right)-\delta B_\xi.
\]

At present this is not a functional differential on the active domain.
Accordingly `CHG4` applies.  The integrability test has not been reached;
`B_xi` is undefined, not zero.  A later completed domain may expose a `CHG3`
ensemble ambiguity, but that later classification cannot replace the current
obstruction.

## Reference structure: REF5

BHSM owns EH/GHY coefficients and orientations.  Those data do not select a
charge zero point.  No common Brown--York reference, cap geometry, vacuum
subtraction, seam reference, environment reference, or full reset ensemble is
owned.  Since no differentiable common charge exists, reference dependence
cannot even be evaluated as a charge ambiguity.  The present classification
is `REF5`.

## Event and mode charges

The total event charge `H_xi,event` is undefined.  Finiteness, integrability,
gauge reduction, constraint compatibility, orientation, and reference
consistency therefore cannot be certified.

There is no physical charge projector `P_mode`.  Frozen family projectors and
the N12 ordered-event eigenline do not provide a projector of a nonlinear
Hamiltonian charge.  Cross-mode interaction terms have no action-owned
allocation.  The classification is `MODEE5`, and both `H_xi,mode` and
`H_xi,mode^avail` remain undefined.

The required accounting slots remain distinct:

| Slot | Current status |
| --- | --- |
| retained parent/environment | no common charge |
| persistent modes | physical mode projector absent |
| outgoing flux | sectorwise flux forms only |
| constraints | sectorwise Hamiltonian, momentum, and Gauss constraints; not energy subtractions |
| independent children | no charge or action-owned branching incidence |

No subtraction formula is adopted merely because these slots must eventually
be accounted for.

## Child, seam, and envelopment increment

`H_xi,child+seam` is undefined.  Geometry, GHY/corner, matter, gauge, scalar,
seam/environment, constraint, and reference contributions cannot be assembled
on a common charge domain.  Hence

\[
\Delta H_{\xi,\mathrm{child+seam}}
\]

is also undefined and classified `ENVH5`.  Path, carrier, ensemble, reference,
and topology dependence are unevaluable rather than absent.

## Common domain: DOMH4

BHSM owns several sectorwise regular domains, one-forward causal orientation,
and the AE4 retarded domain class.  It does not own a domain carrying both
requested comparable full charges with common carrier, generator, ensemble,
reference, orientation/corner data, gauge reduction, and regularity.  Thus
`DOMH4`, rather than `DOMH2`, applies.

## AE4 impedance and crossing

The historical `E_mode` cannot be identified with the undefined
`H_xi,mode^avail`, and `E_impedance` cannot be identified with the undefined
`Delta H_xi,child+seam`.  The classification is `AE4R5` and

```text
rho_hold = UNEVALUABLE_NOT_A_RATIO_OF_CURRENT_CHARGES.
```

No crossing function or domain exists, so no existence, uniqueness, rank
change, bifurcation, support-loss, or saturation conclusion can be drawn.  No
root search is performed.

## Conservation and branching

The no-ex-nihilo rule remains validated as a firewall.  It cannot yet be
applied to any proposed child because the charge ledger is unavailable.  No
configuration is declared energetically allowed or forbidden, and numerical
nonconvergence is not relabelled physical inadmissibility.

No multi-child output is forced.  The generic `1->n` machinery is not used to
invent amplitudes, masses, channels, or incidence maps.

## N12 firewall

No charge equation was derived on the N12 variables.  The new independent
rank is zero; `98-31=67` remains, with `66` after the existing time quotient.

## Decision boundary

### VALIDATED

- thirteen registered action terms and the complete sectorwise variation
  inventory;
- levelwise EH/GHY, scalar, Maxwell, Dirac, ghost, HS, and finite canonical
  boundary data;
- absence of complete event, child, and relative potentials;
- absence of a tangent common generator;
- `XI5`, `CHG4`, `REF5`, `MODEE5`, `ENVH5`, `DOMH4`, and `AE4R5`;
- the no-ex-nihilo firewall and zero N12 rank addition.

### INVALIDATED

- assembling disconnected levelwise forms into a complete potential;
- using coordinate time, retarded boundary value, event eigenline, or Hopf
  rotor as the common generator;
- setting `B_xi=0` because no improvement has been derived;
- treating action normalization as a reference subtraction;
- relabelling frozen projectors as an energy projector;
- forcing the AE4 impedance ratio or crossing.

### REDUNDANT

- recomputing the formal two-sided diffeomorphism formula;
- rederiving the AE2 fermion cancellation or AE3 internal-interface
  cancellation;
- testing reference choices before a differentiable generator exists;
- numerical root searches for an undefined crossing function.

### OPEN

- the action-owned full-field moving trace graph and its first variation;
- complete event and child potentials and Noether-charge assemblers;
- common boundary generator, ensemble, counterterm, and reference;
- event, mode, available, child/seam, and increment charges.

## Decision power and exact next object

The decisive result is that charge construction stops at domain tangency, not
at an unknown numerical normalization.  Therefore neither charge, their ratio,
nor a carrier crossing can be evaluated.

The exact next object remains

```text
ACTION_OWNED_F_B_DEPENDENT_FULL_FIELD_RESET_TRACE_GRAPH_WITH_FIRST_MOVING_DOMAIN_VARIATION_ABSENT
```

Its charge-theoretic role is to place `F_B` in the action domain, provide the
spatial pullback for every participating trace sector, and define
`D_F Graph(R_F)[delta F]`.  Only then can a common tangent generator be tested
and the complete `Theta`, `Q_xi`, `B_xi`, ensemble, and reference analysis
begin.  This does not authorize choosing an arbitrary reset graph.

No owner question is warranted because the obstruction is mathematical rather
than a small physical choice.  No response law is constructed, no frozen
prediction is changed, and Gate 7 is not promoted.
