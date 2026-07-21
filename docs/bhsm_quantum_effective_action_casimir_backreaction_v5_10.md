# BHSM v5.10 Quantum Effective Action and Casimir Backreaction

Primary result: `BHSM_QUANTUM_EFFECTIVE_ACTION_PARTIAL`.

This sprint asks whether the actual BHSM fluctuation spectrum produces a finite Casimir or trace-anomaly backreaction that fixes the v5.8 global size modulus. The answer cannot currently be computed for the full theory. The repository does not contain a completed gauge-fixing functional and ghost domain, completed fermion action/domain and eta invariant, gauge-fixed geometric Hessian, charged-current quadratic operator, normalized neutral determinant, complete Berger-Hopf spectra, or field-theoretic heat-kernel and counterterm closure.

Claiming a complete one-loop action from those inputs would violate the existing v4.6 and v5.4 gates. v5.10 instead computes the strongest exact determinant supported by a closed domain and keeps every excluded sector explicit.

## Background and mode ownership

The retained collective variables are

```text
q_background=(L,a_Berger,sigma_scale,rho_star).
```

The v5.7 homogeneous scalar/topographic basis splits as

```text
delta_parallel=(delta T+delta Phi)/sqrt(2),
delta_perp=(delta T-delta Phi)/sqrt(2).
```

`delta_parallel` is the retained `sigma_scale` coordinate and is not integrated out. Only `delta_perp` is integrated into the reduced one-loop diagnostic. Geometry, gauge, ghost, fermion, charged, neutral, and nonhomogeneous scalar/topographic modes are excluded rather than assigned invented determinants.

This ownership rule prevents the same scalar zero-point mode from appearing in both `Gamma_1loop` and the v5.9 Bohmian quantum potential.

## Euclidean operator gate

The full v5.4 symbolic action is not a closed Lorentzian action with all signs, reality conditions, and boundary domains, so no full Euclidean continuation is claimed. On the v5.7 real homogeneous Robin domain, the included orthogonal Hessian is the positive one-dimensional block

```text
H_perp(L,sigma_scale)=L^-2(4+8 sigma_scale^2).
```

At `sigma_scale=1/2`, its eigenvalue is `6/L^2`. Positivity is exact for `L>0`, but a finite matrix is not used to claim differential ellipticity for the missing field operators.

The gauge candidate `(1/lambda_i)L_i(rho)` remains excluded because the actual BHSM gauge-fixing functional, Faddeev-Popov operator, ghost boundary condition, residual-gauge quotient, and zero-mode projection are not derived. The same discipline excludes the fermion, geometry, charged, and neutral determinants.

## Exact reduced determinant

For the one included mode,

```text
zeta_perp(s)=[L^-2(4+8 sigma_scale^2)]^-s,
zeta_hat(0)=1,
zeta_hat'(0)=-log(4+8 sigma_scale^2).
```

With the renormalization scale kept explicit,

```text
log det(H_perp/mu^2)
  =log(4+8 sigma_scale^2)-2 log(mu L),

Gamma_1loop,perp
  =1/2 log det(H_perp/mu^2).
```

The direct finite determinant and zeta formula agree exactly. No cutoff, box, flat-space momentum integral, assumed Casimir coefficient, or fitted input is used.

This finite homogeneous determinant is not a Casimir energy. It has no infinite spectral remainder from which local ultraviolet pieces have been subtracted. Its heat trace is the finite expression `exp(-t H_perp)`; those Taylor coefficients are not Seeley-DeWitt coefficients of the missing full differential system.

## Renormalization and anomaly boundary

The reduced determinant has

```text
mu dGamma_1loop,perp/dmu=-1,
delta_omega Gamma_1loop,perp=-1
```

under `L->exp(omega)L` with fixed `mu`. These are one-mode scale responses. The repository does not supply the running renormalized coefficients needed to cancel `mu` dependence, a total sector sum, boundary anomaly terms, or an RG-invariant `Lambda_BH`. Therefore `log(mu L)` is not promoted to dimensional transmutation, a physical trace anomaly, or an absolute scale.

The finite Casimir remainder, total anomaly, renormalized vacuum energy, and quantum stress tensor remain null in the artifacts rather than being set to zero.

## Reduced backreaction diagnostic

Combining the v5.7 classical normalized scale potential with the one included mode gives

```text
Gamma_eff,reduced(L,sigma)
  =-sigma^2+2 sigma^4
   +1/2 log[(4+8 sigma^2)/(mu^2 L^2)].
```

Its reduced equations are

```text
partial_L Gamma=-1/L,
partial_a Gamma=0,
partial_sigma Gamma=-2 sigma+8 sigma^3+8 sigma/(4+8 sigma^2),
partial_rho_star Gamma=0.
```

`-1/L=0` has no finite positive solution. The only real sigma stationary point of this partial diagnostic is `sigma=0`, where its sigma Hessian vanishes. There is no positive coupled Hessian, and `a_Berger` and `rho_star` remain flat because their supported determinant dependence is missing.

The partial diagnostic therefore does not correct the official v5.7 input `sigma_scale=1/2`. A one-mode, `mu`-dependent truncation cannot replace the full coupled stationarity calculation.

## Pilot-wave update

The intended hierarchy is retained:

```text
noncollective modes -> renormalized Gamma_eff
retained collective variables -> effective Hamiltonian
retained wavefunction -> Bohmian quantum potential and guidance.
```

The v5.9 Hamiltonian and guidance law are not changed because the full `Gamma_eff` is not closed. Its expanding branch remains the prior conditional scale-covariant result; survival under complete backreaction remains open. Redshifted relics remain physical on-shell relics, while effective or virtual language remains restricted to response memory.

## Uploaded-source audit

Only the pasted sprint instruction was present in the attachment directory; no manuscript files were available for textual verification. The candidate-source descriptions were nevertheless bounded as required:

- Casimir language is motivation only; no coefficient is imported.
- fine-structure/group-volume factors are not used in the determinant and no coupling is promoted.
- `K[rho]=-Delta log rho` remains a legacy candidate absent from the included Hessian; the mass ansatz is not used.
- the old curvature-threshold mass-gap claim remains invalidated.
- cosmology distinctions are retained without importing `R_H`, `B`, `Q_1`, `Q_2`, `H_0`, or redshift scales.

## Result

Derived:

- disjoint retained/integrated mode ownership
- exact positive finite determinant for `delta_perp`
- direct/zeta agreement without a cutoff
- explicit unresolved `mu` and `L` dependence
- reduced backreaction equations and no-finite-`L` result for the partial system

Conditional:

- the determinant relies on the v5.7 homogeneous Robin Hessian and symbolic `L^-2` scale family
- the one-mode scale response is diagnostic, not a physical anomaly
- a future closed `Gamma_eff` can feed the v5.9 collective Hamiltonian without double counting

Invalidated or ruled out:

- a complete BHSM one-loop action from the current operator ledger
- a gauge determinant without ghosts and a derived gauge domain
- `log(mu L)` as an absolute unit
- the finite homogeneous determinant as a Casimir spectral remainder
- the legacy curvature-threshold mass ansatz or mass-gap shortcut as an action result

The primary open gates are the full geometric/gauge-fixed Hessian and domains, ghosts, fermion action and phase, complete spectra, heat-kernel/counterterm closure, coefficient running, finite Casimir remainder, total anomaly, nonlinear coupled backreaction, and absolute unit anchor. All gauge, CKM, neutral-scale, mass-operator, rare-B, and full-BHSM gates remain open.

No physical validation, particle mass, gauge coupling, CKM completion, rare-B prediction, white-hole observation, Yang-Mills mass gap, or full BHSM completion is claimed.

Command:

```bash
python -m bhsm.interface quantum-effective-action-status --format markdown
```

Recommended next sprint: `bhsm-full-geometric-gauge-fixed-hessian-v5-11`.
