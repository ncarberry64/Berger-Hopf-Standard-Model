# BHSM v15.10 Aether-cycle sigma-coefficient reconstruction

## Result

The v15.9 degree-one radial eta branch remains intact as a derived full-Euler
solution. This sprint does not repeat or weaken it.

The retained eta-sigma action admits an exact inverse from a minimal,
canonically normalized sigma response jet to the three coefficient invariants

\[
\alpha=\frac{A_0}{g\kappa_1X_0},\qquad
r=\frac{g\kappa_1}{Z_\sigma},\qquad
\gamma=\frac{G_0}{g^2X_0^4}.
\]

The current Aether/cycle state does not yet produce that response jet. The
repository contains no physical sigma tangent propagator, no derivative of
that propagator with respect to eta support, and no constrained nonlinear
sigma response from which the bare quartic can be recovered. Consequently the
retained theory still admits inequivalent stable coefficient triples on the
same sigma-zero eta/metric parent.

The coefficient-selection result is therefore

`OUTCOME_D_TRUE_RETAINED_ACTION_NONUNIQUENESS`.

This is a constructive nonuniqueness result, not a choice of convenient
coefficients. No physical sigma onset, Hopf child, nested scale, mass, or
formation endpoint is promoted.

`FULL_BHSM_COMPLETE = FALSE`.

## Retained local response

At fixed geometric and eta fields, write

\[
F(X)=\frac{\kappa_1}{2}X+\frac18X^4,
\]

\[
\mathcal E(X,\sigma)
=F(X)(1+g\sigma^2)
+\frac{A_0}{2}\sigma^2
+\frac{G_0}{4}\sigma^4.
\]

At \(\sigma=0\),

\[
\mathcal E_X=\frac12(\kappa_1+X^3),\qquad
\mathcal E_{XXXX}=3,
\]

\[
\mathcal E_{\sigma\sigma}
=A_0+g\left(\kappa_1X+\frac14X^4\right),
\]

\[
\mathcal E_{\sigma\sigma X}=g(\kappa_1+X^3),\qquad
\mathcal E_{\sigma\sigma XXXX}=6g,
\]

\[
\mathcal E_{\sigma\sigma\sigma\sigma}=6G_0.
\]

Therefore the same-\(g\) integrability identities are exact:

\[
\frac{\mathcal E_{\sigma\sigma X}}{2\mathcal E_X}
=\frac{\mathcal E_{\sigma\sigma XXXX}}{2\mathcal E_{XXXX}}
=g.
\]

They test the retained action structure. They do not select a numerical value
of \(g\).

## Exact response-jet inverse

Define the canonically normalized fixed-background response data

\[
S_\sigma=\frac{\mathcal E_{\sigma\sigma}}{Z_\sigma},\qquad
S_{\sigma,X}=\frac{\mathcal E_{\sigma\sigma X}}{Z_\sigma},\qquad
\lambda_{\sigma,\mathrm{bare}}
=\frac{\mathcal E_{\sigma\sigma\sigma\sigma}}{6Z_\sigma^2}
=\frac{G_0}{Z_\sigma^2}.
\]

Then the invariant triple is recovered without knowing the absolute
normalization of \(Z_\sigma\):

\[
\boxed{
r=\frac{S_{\sigma,X}}{1+X_0^3/\kappa_1}
}
\]

\[
\boxed{
\alpha=\frac{S_\sigma}{rX_0}-1-\frac{X_0^3}{4\kappa_1}
}
\]

\[
\boxed{
\gamma=
\lambda_{\sigma,\mathrm{bare}}
\frac{\kappa_1^2}{r^2X_0^4}
}.
\]

At the v15.9 crossing \(X_c^3=5\kappa_1\), these simplify to

\[
\boxed{r=\frac16S_{\sigma,X}},\qquad
\boxed{\alpha=\frac{S_\sigma}{rX_c}-\frac94}.
\]

Thus coefficient selection has been reduced to three concrete response
observables. The inverse is algebraic and injective wherever the mixed
response is nonzero.

## Physical tangent and nonlinear response

For a physical sigma fundamental matrix,

\[
A_\sigma=\dot M_\sigma M_\sigma^{-1}
=\begin{pmatrix}0&1\\-S_\sigma&-\Gamma_\sigma\end{pmatrix},
\]

so

\[
S_\sigma=-(A_\sigma)_{21},\qquad
\partial_t\log Z_\sigma=-(A_\sigma)_{22}-7H.
\]

The Wronskian fixes relative transport of \(Z_\sigma\), not its absolute
normalization. That is sufficient for the invariant inverse only after the
physical sigma propagator and its \(X\)-derivative exist.

The canonical quartic must be the fixed-background or backreaction-unreduced
coefficient. If environmental variables \(I\) have already been eliminated,

\[
\lambda_{\mathrm{phys}}
=\lambda_{\mathrm{bare}}
-\frac12B^T(H_{II}^{\mathrm{phys}})^{-1}B,
\]

and therefore

\[
\boxed{
\lambda_{\mathrm{bare}}
=\lambda_{\mathrm{phys}}
+\frac12B^T(H_{II}^{\mathrm{phys}})^{-1}B
}.
\]

This prevents a reduced nonlinear response from being misidentified with the
retained coefficient \(G_0/Z_\sigma^2\).

## Homogeneous-cycle inverse

The frozen homogeneous degree-one inverse is

\[
\kappa_1=\frac{343}{a^6(5-6a^2\dot H)},
\]

\[
\kappa_0=
\frac{7203(8a^2H^2+2a^2\dot H+5)}
{4a^8(5-6a^2\dot H)}.
\]

Combining the first equation with the v15.9 crossing
\(a_c^6=343/(5\kappa_1)\) while requiring the same \(\kappa_1\) gives
\(\dot H=0\). On the stationary turning slice \(H=\dot H=0\), the second
equation becomes

\[
\kappa_0=\frac{7203}{4a_c^8}
=\frac{15}{4}\kappa_1X_c,
\]

which exactly reproduces the v14.91 round identity-map locus. This closes an
eta/gravity compatibility check. It does not expose sigma coefficients,
because the sigma-zero background removes them from both the background
action and its first variation.

## Constructive retained-action nonuniqueness

The deterministic artifact constructs three positive-\(Z_\sigma\),
positive-quartic, stable examples on the same \(\sigma=0\) eta/metric parent.
In the \(\kappa_1=Z_\sigma=1\) normalization:

| Witness | \(\alpha\) | \(r\) | \(\gamma\) | Purpose |
| --- | ---: | ---: | ---: | --- |
| A | \(-1\) | \(1\) | \(1\) | reference |
| B | \(-13/8\) | \(2\) | \(1\) | same \(S_\sigma(X_c)\) as A, different \(S_{\sigma,X}\) |
| C | \(-1\) | \(1\) | \(3\) | same complete quadratic jet as A, different quartic |

All three make zero contribution to the sigma-zero background and first
variation. A and B even have the same normalized quadratic curvature at the
cycle slice, proving that a single sigma mass value does not determine
\(\alpha\) and \(r\). A and C have the same quadratic response and differ only
in nonlinear response, proving that \(\gamma\) requires independent
fourth-order information.

## Exhausted action-owned routes

The backward search found:

- Homogeneous cycle inversion selects \(\kappa_1,\kappa_0\) conditionally but
  is blind to \(Z_\sigma,g,A_0,G_0\) at \(\sigma=0\).
- Global scale stationarity and the Hamiltonian constraint vary fields and
  moduli, not independent Wilson coefficients.
- The v11.2 support/Haar character system explicitly treats existing
  coefficients as inert; it cannot act as a spurion selector.
- The v14.62 provenance quotient keeps the M8 parent Wilson family
  independent.
- The v14.64--v14.69 Calderón/Wentzell machinery supplies theorem classes,
  but its physical operator blocks and renormalized values are absent.
- The v14.94 propagator is a metric-shape propagator. Its exact branch has
  \(\sigma=0\) and records no nonlinear response.
- The v15.2--v15.6 Aether chain explicitly lacks a core pairing, physical
  attachment, and foundation-to-regular action-sector reconstruction functor.
- The spectral/zeta branch remains an unadopted candidate with a local
  counterterm prescription still open.

No Ward, response, reconstruction, anomaly, support, or stationarity identity
currently supplies the missing numerical jet.

## Consequences for the requested chain

- Coefficient reconstruction: exact inverse derived; values not selected;
  Outcome D proved constructively.
- Eta to sigma: v15.9 conditional thresholds remain valid, but no physical
  \(\alpha\) or \(a_\sigma\) is selected.
- Coupled eta-sigma continuation: ineligible without the selected response
  jet.
- Full \(S^3\times S^3\) Hopf child: not reached.
- Nested scale: not reached.
- Stationary Hessian or Floquet persistence: not reached.
- Formation and de-envelopment: the radial eta precursor remains; no physical
  enclosure endpoint exists.
- Gauge, flavor, neutrino, mass, and scale gates: unchanged and open.

Advancing farther by picking one witness would violate action ownership.

## Hindsight 20/20

### VALIDATED

- Homogeneous cycle inverse compatibility with the v15.9 stationary slice.
- Exact retained-action response integrability identities.
- Exact injective inverse from three canonical response observables to
  \((\alpha,r,\gamma)\).
- Constructive stable nonuniqueness after background and partial response data.

### INVALIDATED

- Background equations alone select sigma coefficients.
- One sigma mass value selects \(\alpha,r\).
- Quadratic sigma tangent data select \(\gamma\).
- The v14.94 metric-shape propagator may be relabelled as sigma response.
- Wronskian transport fixes absolute \(Z_\sigma\).

### RECLASSIFIED

- The coefficient blocker is now a precise three-observable reconstruction
  problem rather than an undifferentiated list of independent inputs.
- The v15.9 conditional sigma threshold is downstream of this response map.

### OPEN

`ACTION_OWNED_AETHER_CYCLE_TO_REGULAR_SIGMA_RESPONSE_JET_MAP_PRODUCING_THE_PHYSICAL_SIGMA_TANGENT_PROPAGATOR_X_DERIVATIVE_AND_BACKREACTION_UNREDUCED_CANONICAL_QUARTIC_ON_THE_V15_9_BRANCH`

## Reproduction

```powershell
python scripts/materialize_cycle_sigma_coefficients_v15_10.py
python -m pytest -q tests/test_bhsm_aether_cycle_sigma_coefficient_reconstruction_v15_10.py
```

The materializer must reproduce
`artifacts/BHSM_aether_cycle_sigma_coefficient_reconstruction_v15_10.json`
byte for byte.
