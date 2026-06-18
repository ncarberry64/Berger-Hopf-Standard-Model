# PO-BH-54 - Normal-Coupling / Collar Convention Theorem

Status: `OPEN_LOCALIZABLE`

Current public status: structural architecture integrated conditional; numerical closure open.

## Problem

PO-BH-53 conditionally derived the symbolic neutral boundary condition:

```text
n_mu partial^mu Phi
- D_A(chi_nu^{AB}D_B Phi)
+ R_nu[lambda_nu, Phi, n.grad Phi]
= 0 on partialB.
```

The remaining ambiguity is the normal-coupling/collar contribution produced by:

```text
S_lambda^(nu) =
int_partialB lambda_nu Phi n.grad Phi dA.
```

The purpose of PO-BH-54 is to localize the possible conventions for:

```text
R_nu[lambda_nu, Phi, n.grad Phi].
```

This sprint does not derive the numerical value or functional form of `lambda_nu`.

## Route A - Fixed Normal Derivative Convention

If `n.grad Phi` is treated as a prescribed boundary datum during variation, then:

```text
delta(lambda_nu Phi n.grad Phi)
= lambda_nu (n.grad Phi) delta Phi.
```

Under this restricted convention:

```text
R_nu = lambda_nu n.grad Phi.
```

Status: `DERIVED_CONDITIONAL`.

Reason: this follows if the normal derivative is fixed as boundary data. The repo does not yet prove this is the BHSM scalar/topographic boundary convention, so the result is restricted rather than generally derived.

## Route B - Symmetrized Normal Bilinear Convention

The normal bilinear has the algebraic identity:

```text
Phi n.grad Phi = 1/2 n.grad(Phi^2).
```

This can be read as a normal total derivative inside a collar, but the physical consequence depends on the collar and edge convention. It may become:

- a collar total derivative;
- a Robin-type boundary contribution;
- a boundary-of-boundary or inner-edge term;
- or an ambiguity that remains in `R_nu`.

Status: `STRUCTURALLY_MOTIVATED_NOT_DERIVED`.

Reason: the identity is exact, but its boundary-action meaning is not fixed without collar geometry and edge data.

## Route C - Collar Extension Route

Introduce a collar coordinate `rho` normal to the boundary:

```text
n.grad Phi = partial_rho Phi.
```

The localized thin-collar candidate is:

```text
S_collar =
int_{partialB x [0,epsilon]}
lambda_nu(rho,Y) Phi partial_rho Phi d rho dA.
```

Varying the collar action requires choices for:

- collar measure;
- normal orientation;
- behavior at the inner collar edge;
- whether `delta Phi` or `delta partial_rho Phi` is fixed;
- whether the `epsilon -> 0` limit is taken before or after variation.

Status: `OPEN_LOCALIZABLE`.

Reason: the collar construction localizes the missing convention, but the repo does not yet derive the collar measure, inner-edge behavior, or limiting boundary term.

## Route D - Robin Boundary Condition Route

A derived collar convention may reduce the normal-coupling term to an effective Robin form:

```text
A_nu Phi + B_nu n.grad Phi - D_A(chi_nu^{AB}D_B Phi) = 0.
```

Here `A_nu and B_nu` would have to follow from `lambda_nu` and the collar convention.

Status: `OPEN_LOCALIZABLE`.

Reason: Robin form is structurally compatible with the normal-coupling term, but `A_nu`, `B_nu`, and the relation to `lambda_nu` are not derived.

## Route E - Conservative Remainder Route

Until the normal/collar convention is derived, PO-BH-54 keeps:

```text
R_nu[lambda_nu, Phi, n.grad Phi]
```

as a symbolic remainder with allowed candidate forms:

```text
R_nu = lambda_nu n.grad Phi
```

under fixed-normal data, or

```text
R_nu -> A_nu Phi + B_nu n.grad Phi
```

under a derived Robin/collar convention.

Status: `OPEN_LOCALIZABLE`.

Reason: this is the honest repository status. The local term is identified, but the full BHSM convention is not fixed.

## Assumptions

- The boundary embedding is fixed unless a collar geometry is explicitly introduced.
- The normal vector is fixed, or the collar geometry supplies the normal.
- `delta(n.grad Phi)` is fixed only in the restricted fixed-normal route.
- `delta Phi is free on the boundary` unless explicitly constrained.
- The boundary has no boundary, or edge terms are explicitly tracked.
- `lambda_nu` is treated as a background coefficient.
- No fitting to neutrino masses, neutrino mass splittings, PMNS values, or anomaly/FTL data is allowed.
- No claim of local causality violation is made.
- No claim of experimental FTL is made.

## Verdict Table

| candidate route | formula | assumptions | dependencies | status | reason | allowed next action | forbidden shortcut |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Fixed normal derivative convention | `R_nu=lambda_nu n.grad Phi` | `n.grad Phi` fixed; fixed normal vector; `lambda_nu` background | `lambda_nu`, fixed-normal boundary datum | `DERIVED_CONDITIONAL` | Follows under a restricted convention only. | Derive whether fixed-normal data is the BHSM convention. | Choose this route from neutrino residuals. |
| Symmetrized normal bilinear | `Phi n.grad Phi = 1/2 n.grad(Phi^2)` | normal total derivative has a collar interpretation | collar geometry, edge behavior | `STRUCTURALLY_MOTIVATED_NOT_DERIVED` | Algebraic identity is exact, but boundary meaning is not fixed. | Derive edge/collar behavior from the action. | Drop or keep total derivative after comparison. |
| Collar extension | `S_collar=int_{partialB x [0,epsilon]} lambda_nu(rho,Y) Phi partial_rho Phi d rho dA` | collar coordinate, measure, orientation, edge condition | collar measure, normal orientation, inner edge, variation data | `OPEN_LOCALIZABLE` | Localizes the missing convention but does not derive its limit. | Derive the thin-collar limit and edge conditions. | Fit collar profile to neutrino or anomaly data. |
| Robin boundary condition | `A_nu Phi + B_nu n.grad Phi - D_A(chi_nu^{AB}D_B Phi)=0` | `A_nu`, `B_nu` derived from `lambda_nu` and collar convention | `lambda_nu`, collar convention, Robin coefficients | `OPEN_LOCALIZABLE` | Plausible reduction but coefficients are not derived. | Derive `A_nu`, `B_nu` from collar action. | Fit Robin coefficients to PMNS or mass residuals. |
| Conservative remainder | `R_nu[lambda_nu, Phi, n.grad Phi]` | no convention chosen by fit | all above routes | `OPEN_LOCALIZABLE` | Stores the unresolved normal contribution honestly. | Derive or reject the normal/collar convention before comparison. | Treat `R_nu` as a fitted damping or mass-scale parameter. |

## Closure-Map Status

Preferred status:

```text
R_nu_normal_coupling: OPEN_LOCALIZABLE
normal_collar_convention: OPEN_LOCALIZABLE
lambda_nu: OPEN_LOCALIZABLE
neutral_boundary_condition: DERIVED_CONDITIONAL as a symbolic form with R_nu still open
```

The fixed-normal route is conditionally derived only as a restricted convention. The general normal-coupling/collar convention remains localized but open.

## Claim Boundary

The normal-coupling/collar convention for the neutral boundary term has been localized. A fixed-normal restricted route gives `R_nu=lambda_nu n.grad Phi`, while collar and Robin routes remain open-localizable. The numerical value or function of `lambda_nu` remains open. No numerical neutrino prediction is claimed. No claim of local causality violation is made. No claim of experimental FTL is made.

Observed neutrino masses, observed neutrino mass splittings, PMNS angles, PMNS CP phase, fitted FTL/anomaly data, and post-comparison choices of `lambda_nu`, `R_nu`, collar convention, Robin coefficients, `S_eff_nu`, `Delta_y_nu`, `S_nu_topo`, or `epsilon_nu_topo` are forbidden inputs.

## Next Action

Derive or reject the BHSM collar convention, normal orientation, inner-edge condition, admissible variation data, and any Robin coefficients from the complete scalar/topographic boundary action before comparison.
