# PO-BH-48 - Neutral Topographic Suppression Action Theorem

## Mission

This sprint localizes the open numerical-closure object
`S_nu_topo` in the neutral-sector relation

```text
epsilon_nu_topo = exp(-S_nu_topo)
M_nu = epsilon_nu_topo M_nu^(0)
```

The goal is not to fit the neutrino mass scale. The goal is to determine
whether the existing BHSM scalar/topographic and boundary-Hessian scaffolds
already force a pre-comparison expression for `S_nu_topo`.

## Verdict

`S_nu_topo` remains `OPEN_LOCALIZABLE`.

The neutral topographic suppression action has been localized as the next
numerical-closure object. A candidate Hessian/barrier formula is identified,
but numerical neutrino closure remains open unless explicitly derived and
locked before comparison.

## Locked Neutral Relations

```text
epsilon_nu_topo = exp(-S_nu_topo)
M_nu = epsilon_nu_topo M_nu^(0)
H_nu = epsilon_nu_topo^2 H_nu^(0)
```

The current neutral ledger is

```text
(0,0), (3,0), (1,1)
```

and the neutral operator is

```text
Omega_nu = -q - 2j = -k.
```

The relation `k=q+2j` gives neutral `k` values `[0,3,3]`.

## Candidate Route A - Gaussian Hessian Displacement Suppression

Candidate formula:

```text
S_nu_topo = 1/2 Delta y_nu^T G_nu_topo Delta y_nu + S_barrier
G_nu_topo = 1/2 E_nu^T H_topo^(nu) E_nu
```

Status: `OPEN_LOCALIZABLE`.

Reason: the repository contains candidate boundary-Hessian and topographic
action scaffolds, but it does not yet derive:

- the neutral displacement `Delta y_nu`;
- the neutral Hessian `H_topo^(nu)`;
- the neutral embedding tensor `E_nu`;
- the barrier term `S_barrier`;
- the finite-width neutral saddle/path.

This is the best localized candidate route because it identifies a concrete
object to derive from the scalar/topographic boundary action.

## Candidate Route B - Neutral Boundary Stiffness Mismatch

Candidate formula:

```text
S_nu_topo = S_eff^(nu) - S_eff^(charged_ref)
```

Status: `STRUCTURALLY_MOTIVATED_NOT_DERIVED`.

Reason: a neutral-versus-charged stiffness mismatch is compatible with the
BHSM topographic picture, but the repo does not yet compute a neutral
finite-width saddle/path, a charged reference saddle/path, or an explicit
`S_eff` functional evaluated on both.

## Candidate Route C - Neutral Operator Barrier From Omega_nu

Candidate formula:

```text
Omega_nu = -q - 2j = -k
```

Status: `STRUCTURALLY_MOTIVATED_NOT_DERIVED`.

Reason: `Omega_nu` localizes the neutral sector and suggests a `k`-barrier
interpretation, but the repo does not yet derive a positive action map from
`Omega_nu` to `S_nu_topo`.

## Verdict Table

| candidate route | formula | dependencies | status | reason | allowed next step | forbidden shortcut |
| --- | --- | --- | --- | --- | --- | --- |
| Gaussian Hessian displacement | `S_nu_topo = 1/2 Delta y_nu^T G_nu_topo Delta y_nu + S_barrier` | `Delta y_nu`, `G_nu_topo`, `H_topo^(nu)`, `E_nu`, `S_barrier` | `OPEN_LOCALIZABLE` | Hessian scaffold exists, but neutral displacement/Hessian/barrier are not derived. | Derive the neutral displacement, Hessian, embedding, and barrier from the boundary/topographic action. | Fit `S_nu_topo` or `epsilon_nu_topo` to observed neutrino masses. |
| Neutral stiffness mismatch | `S_nu_topo = S_eff^(nu) - S_eff^(charged_ref)` | neutral saddle/path, charged reference saddle/path, `S_eff` | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | Effective stiffness comparison is plausible, but neither saddle/path is computed. | Construct and evaluate `S_eff` internally before comparison. | Fit or choose the mismatch from neutrino scale residuals. |
| Omega barrier | `Omega_nu = -q - 2j = -k` | neutral ledger, `Omega_nu`, positive barrier/action functional | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | The operator localizes a structural hint, not a numerical action. | Derive a positive neutral barrier functional from `Omega_nu`. | Convert `k` values into a fitted suppression exponent. |

## Claim Boundary

This sprint does not claim numerical neutrino prediction, neutrino mass
ordering, PMNS numerical closure, or full Standard Model replacement.

Observed neutrino masses, observed mass splittings, PMNS angles, and PMNS CP
data are forbidden inputs for choosing `S_nu_topo`.

The topographic suppression remains common-leading-order. No mode-dependent
neutral correction theorem is introduced here.

## Missing Dependencies

- derive `Delta y_nu` from internal BHSM scalar/topographic data;
- derive `H_topo^(nu)` from the full boundary Hessian;
- derive `E_nu` from the neutral sector boundary tensors;
- derive or prove unnecessary `S_barrier`;
- evaluate the neutral finite-width saddle/path;
- prove positivity of the resulting suppression action;
- lock the formula before any comparison to observed neutrino data.

## Current Public Status

`structural architecture integrated conditional; numerical closure open`
