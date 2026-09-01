# BHSM-AE-3 reciprocal-join localization and enclosure theorem

Status:
`ACTION_OWNED_LOCALIZATION_CARRIER_DERIVED_ON_THE_RETAINED_C2_ACTION_DOMAIN__FULL_FIELD_EVENT_BALANCE_OPEN`.

## 1. Decision

The post-AE2 carrier is not a new wall field. The retained N12 action already
uses the historical reciprocal-join material profile

\[
 \sigma_0(\chi)=-\frac12+\frac{2\chi}{\pi}
 -\frac{\sin 4\chi}{2\pi}
\]

and the localized Hopf weight

\[
 \Lambda(\sigma)=1-4\sigma^2.
\]

BHSM-AE-3.0.0 promotes that fixed profile into the existing eta-to-sigma
response constraint. It adds no propagating field, continuous coefficient,
physical scale, particle label, or Standard Model fit. The only additional
variable is the nonpropagating KKT multiplier that enforces the response.

This is an action-domain promotion. It does not revise the unchanged-AE2 kill
screen: none of the six objects audited *inside unchanged AE2* was a carrier.

## 2. Comparative result

The serious recovered candidates reduce as follows.

| Rank | Candidate | Action result | New continuous data | Decision |
| ---: | --- | --- | ---: | --- |
| 1 | reciprocal eta-to-sigma response plus localized Hopf/FR functional | already frozen in the retained N12 integrand; KKT promotion supplies action ownership | 0 | selected |
| 2 | equal-preimage eta scalar | regular symmetry-fixed level set but no material response by itself | 0 | kinematic cross-check |
| 3 | eta-induced inverse-Euler sigma potential | regular fixed-background critical skin; negative scaling mode and overall normalization open | 1 | weaker |
| 4 | retained quartic sigma wall | inequivalent stable coefficient triples share the same parent | 4 | nonunique |
| 5 | multiplicative support depth `q_D` | zero support is at infinite Haar depth for a positive-capacity regular collar | at least 2 | invalid as a regular finite wall |
| 6 | scalar/topographic level set | threshold and profile are not action-selected | at least 1 | open scaffold |
| 7 | core boundary/collar | embedding, thickness, and response are not selected | at least 1 | conditional only |
| 8 | spacetime edge | no edge theorem follows from the stop or rank loss | 0 | unsupported |

The first candidate wins by provenance as well as parameter economy. The
retained action already evaluates it; AE3 removes its fixed-coordinate status.

## 3. Action

On the oriented cohomogeneity-one orbit space `Q`, let `d ell` be proper
orbit length and let

\[
 W_J[\eta]=\sin^2 f\cos^2 f,
 \qquad
 Z_J[\eta]=\int_Q W_J[\eta],d\ell.
\]

The response constraint is

\[
 \boxed{
 C_\sigma=n_\eta^A\nabla_A\sigma-\frac{W_J[\eta]}{Z_J[\eta]}=0,
 \qquad \sigma|_{Q_-}=-\frac12 .
 }
\]

Its action owner is

\[
 S_{\rm response}
 =\int dt\int_Q d\ell\,\mu_Q\lambda_\sigma C_\sigma .
\]

The multiplier is nonpropagating. Normalization gives
`sigma|Q_+=+1/2` without a coefficient.

The existing Hopf inertia is

\[
 I_H[\Phi]=\int_{\Sigma_t}\sqrt h;
 (\kappa_1+X_\eta^3)\Lambda(\sigma)|K_H|^2,
 \qquad \Lambda(\sigma)=1-4\sigma^2.
\]

Among even polynomials of degree at most two, the three conditions

\[
 \Lambda(0)=1,
 \qquad \Lambda(-1/2)=\Lambda(+1/2)=0
\]

have the unique solution displayed above. This is also the factor already
used by the retained N12 action, so AE3 does not choose from a new operator
basis.

On the odd-FR domain, the zero-current ground ray has

\[
 \Psi_0(\theta)=\pi^{-1/2}\cos(\theta/2),
 \qquad \langle J\rangle=0,
 \qquad \langle J^2\rangle=\frac14,
\]

and hence

\[
 H_{\rm FR}[\Phi]=\frac{1}{8I_H[\Phi]}.
\]

Let `S_BHSM,AE2^ret` denote the current stratified retained action, including
the N12 geometry/eta functional, its existing FR contribution, and the AE2
reset-glued fermion domain. AE3 replaces the frozen coefficient profile by
the response variable everywhere it occurs and adds the constraint once:

\[
 \boxed{
 S_{\rm AE3}[\Phi,\sigma,\lambda_\sigma]
 =S_{\rm BHSM,AE2}^{\rm ret}
 [\Lambda(\sigma_0)\mapsto\Lambda(\sigma)]
 +S_{\rm response}.
 }
\]

The displayed `H_FR` is already part of the retained functional and is
promoted by this substitution; it is not added a second time.

on the already-existing degree-one odd-FR component. On the trivial/even
component the response/odd-FR sector is absent and `J^2=0`; the action is
exactly AE2. This is the inactive limit. It is discrete and topological, not
a fitted activation function.

## 4. Euler equations

Variation in `lambda_sigma` gives `C_sigma=0`. For any variation on the orbit
space,

\[
 \delta C_\sigma
 =D_\ell\delta\sigma
 -\frac{\delta W_J}{Z_J}
 +\frac{W_J\delta Z_J}{Z_J^2}
 +\delta_g(D_\ell\sigma),
\]

\[
 \delta Z_J=\int_Q
 \left(\delta W_J+W_J\,\delta\log d\ell\right)d\ell,
 \qquad
 \delta W_J=\frac12\sin(4f)\delta f.
\]

The sigma adjoint equation is

\[
 -\mu_Q^{-1}D_\ell(\mu_Q\lambda_\sigma)
 +\frac{1}{\mu_Q}\frac{\delta H_{\rm regular}}{\delta\sigma}
 +\frac{1}{\mu_Q}\frac{\delta H_{\rm FR}}{\delta\sigma}=0.
\]

Writing the inertia density without `Lambda` as `K_H`, the FR term is

\[
 \frac{\delta H_{\rm FR}}{\delta\sigma}
 =\frac{4\langle J^2\rangle}{I_H^2}
 \mu_Q K_H\sigma
 =\frac{\mu_Q K_H\sigma}{I_H^2}
\]

in the ground domain. The eta and metric equations receive the exact
Fréchet response from `delta W_J`, `delta Z_J`, the orbit normal/measure, and
`delta I_H`. No pressure, wall tension, or contact coefficient is inserted.

## 5. Carrier theorem

On the retained identity eta branch,

\[
 W_J=\sin^2\chi\cos^2\chi,
 \qquad Z_J=\frac\pi{16},
\]

so

\[
 \sigma_0'(\chi)=\frac{W_J}{Z_J}
 =\frac4\pi\sin^2(2\chi)>0
 \quad (0<\chi<\pi/2).
\]

Consequently `sigma_0` maps the orbit interval monotonically from `-1/2` to
`+1/2`, has exactly one zero at `chi=pi/4`, and

\[
 \sigma_0'(\pi/4)=\frac4\pi\ne0.
\]

Therefore

\[
 D_{\rm enc}=\{x:\sigma(x)<0\},
 \qquad
 \Sigma_{\rm enc}=\{x:\sigma(x)=0\}
\]

is a well-defined oriented local domain with

\[
 n_A=\frac{\nabla_A\sigma}{\sqrt{|\nabla\sigma\cdot\nabla\sigma|}},
 \quad h_{AB}=g_{AB}-\epsilon n_An_B,
 \quad K_{ab}=h_a{}^Ah_b{}^B\nabla_An_B.
\]

The route is `LOCAL_SAME_SPACETIME_ENCLOSURE`. The action contains one smooth
spacetime and a resolved scalar profile; it contains neither a terminal
boundary nor a spacetime-edge transition.

## 6. Same-action interface variation

`Sigma_enc` is an internal resolved level set, not the AE2 reset locus.
Splitting the one smooth action into `sigma<0` and `sigma>0` pieces creates
opposite-normal boundary terms which cancel. Equivalently, independent
one-sided notation gives

\[
 [h_{ab}]=[N]=[\beta_\parallel]=0,
 \qquad [\Pi_g^n]=0,
\]

\[
 [\eta]=[\Pi_\eta^n]=0,
 \qquad [\sigma]=[\mu_Q\lambda_\sigma]=0,
\]

\[
 [\iota_X^*A]=[\Pi_A^n]=0,
 \qquad [n_AJ^A_{\rm Noether}]=0.
\]

The fermion is a smooth section across the enclosure level set, and its
opposite-normal Green forms cancel. The separate event-child trace law stays

\[
 \Gamma_{0,c}\Psi=U_R\Gamma_{0,e}\Psi,
 \qquad
 \Gamma_{1,c}\Psi=-U_R\Gamma_{1,e}\Psi.
\]

Gauge ghosts and antighosts use the continuous pullback domain, so BRST
compatibility is preserved. With all profile stress included,

\[
 [T_{nn}]_{\rm resolved}=0.
\]

There is no delta-supported surface tension. Opposite-normal internal GHY or
Brown--York terms cancel and may not be relabelled as material tension.

## 7. Nonlinear localized witness

The analytic `sigma_0` profile is nonconstant, finite, and transverse. The
retained N12 action evaluates exactly `Lambda(sigma_0)` at every quadrature
point. The current continuum certificate supplies an actual positive-duration
C2 child for that same retained cohomogeneity-one action domain. Thus the
carrier is no longer a Hessian zero or proof-box boundary: it is a regular
field level set on a nonlinear child history.

This conclusion is independently supported, but not upgraded, by the earlier
response-constrained nonlinear chain. That chain wrote one explicit reduced
Einstein--eta--response functional, solved its finite Galerkin spatial Euler
projection, solved both response-constrained ADM initial-data constraints,
and integrated a Lorentzian trajectory reaching surface separation. Those
are reusable nonlinear existence witnesses. They did not establish a
persistent full-field particle and are not substituted for the actual C2
history.

This statement does not promote the unrestricted nonround
Einstein--eta--sigma--gauge--fermion--HS boundary-value problem as solved.

## 8. Family/mode instantiation

The C2 geometry is a base history, not a particle-species selector. Requiring
it to choose one electron-, quark-, or generation-like label would add a
false selection problem. The correct object is the frozen state fiber

\[
 \mathcal H_{C2}^{\rm particle}
 =\bigsqcup_{r\in\{\ell,u,d\}}
 \bigsqcup_{n=0}^2
 \left(C2\times\Pi_{r,n}\mathcal F_r\right).
\]

An upstream BHSM-native state supplies `(r,n)` as initial data. On

\[
 L^2(Q)\otimes(\mathrm{Spin}\times G_{\rm SM})\otimes\mathcal F_r,
\]

the reset, family projector, enclosure restriction, and smooth carrier act on
separate tensor factors:

\[
 U=I_Q\otimes U_R\otimes I_F,\quad
 \widehat\Pi_{r,n}=I_Q\otimes I_{\rm Spin\times G}\otimes\Pi_{r,n},
\]

\[
 P_D=\mathbf 1_{\{\sigma<0\}}\otimes I\otimes I,\qquad
 L_\sigma=\Lambda(\sigma)\otimes I\otimes I.
\]

Here `P_D` is a restriction projector; `L_sigma` is a smooth multiplication
operator, not a projector. Therefore

\[
 [U,\widehat\Pi_{r,n}]=[U,P_D]=[U,L_\sigma]
 =[P_D,\widehat\Pi_{r,n}]=[L_\sigma,\widehat\Pi_{r,n}]=0
\]

for all nine frozen charged-sector slots. Each actual lifted C2 history keeps
its projector from parent to stop, event-child, enclosure, and child. The
existing Standard Model manifestation map is downstream and unchanged.

This closes family/mode *transport*. It does not claim that the geometry
chooses which particle species was supplied upstream, nor does it derive a
mass hierarchy or mixing matrix. It also does not claim commutation with a
not-yet-constructed interacting full-field C2 Hamiltonian.

## 9. Dependency closure

For each charged sector the machine-readable artifact transports exactly the
transitive closure of:

- C2 geometry, eta, sigma, the response multiplier, and enclosure geometry;
- degree, orientation, FR data, and the reset-glued `Spin x G_SM` bundle;
- the selected sector and rank-one family projectors;
- the sector fermion, its Green trace domain, and its owned current;
- gauge/BRST traces;
- the Higgs/HS trace only when the existing manifestation operator requires
  it.

Unrelated sectors are not required in one local particle state.

## 10. Claim boundary

### Systems-integration rule

The downstream program is not serialized into a ladder of gates. Localization,
particle identity, the common field action, muon `F2(0)`, collisions, spectral
forecasts, and gravity/cosmology are independently advanceable sections. A
valid corpus result may be fitted into any section immediately. Promotion of a
composed result requires only the interfaces it actually uses to share the
same action version, background, variational domain, state factorization,
scale/renormalization, and provenance. Full BHSM completion is the compatible
assembly of these sections with commuting interface maps.

Derived:

- an owner-authorized `BHSM-AE-3.0.0` localization action domain;
- a regular action-owned scalar carrier and local enclosure route;
- the resolved same-action interface laws;
- a nontrivial localized C2 witness on the retained action domain;
- dependency ledgers and all-slot family-fiber transport;
- preservation of the AE2 reset and all frozen particle assets.

Open:

- one C2 action oracle containing geometry, gauge/ghost, fermion, HS, and
  response-multiplier coordinates together;
- the complete event canonical flux/contact evaluation in that oracle;
- the full parent/event/child Noether--Hamiltonian balance;
- unrestricted nonround full-field continuation and its physical Hessian;
- the downstream Gate-7 force/KKT, pair-plus-contact, Ward/BRST trace, and
  scalar-readout rows.

The historical common gauge--ghost--Weyl--HS superdeterminant does not close
the first item. It is a zero-source functional on a historical closed proper
cycle. The actual C2 object is a positive-duration maximal history carrying
nonzero upstream family-state initial data. Action version, background,
domain, explicit field coordinates, and source dependence must all agree
before a block can be attached; no choice of a continuous coefficient repairs
this domain/source mismatch. Reusable BRST, representation, reset-domain, and
HS-response structures remain upstream assets.

Accordingly:

```text
ACTION_OWNED_LOCALIZATION_CARRIER_DERIVED = TRUE
BHSM_NATIVE_FAMILY_MODE_STATE_TRANSPORTED_THROUGH_LOCALIZATION = TRUE
EXISTING_SM_MANIFESTATION_READOUT_PRESERVED = TRUE
PHYSICAL_ENCAPSULATION_IDENTIFIED = FALSE
FULL_BHSM_COMPLETE = FALSE
```

The exact next mathematical object is:

```text
ONE_AE3_FULL_FIELD_C2_ACTION_ORACLE_WITH_GEOMETRY_GAUGE_GHOST_FERMION_HS_AND_RESPONSE_MULTIPLIER_BLOCKS;
THEN_EVALUATE_THE_EVENT_CANONICAL_FLUX_AND_COMPLETE_NOETHER_HAMILTONIAN_BALANCE_WITHOUT_ADDING_A_CONTACT_COEFFICIENT
```

The machine-readable authority is
`artifacts/action_extension/BHSM_ACTION_AE3_RECIPROCAL_JOIN_LOCALIZATION.json`.
