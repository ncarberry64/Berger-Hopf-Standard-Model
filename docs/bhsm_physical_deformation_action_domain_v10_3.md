# BHSM v10.3 Physical Deformation Action-Domain Theorem

## Verdict

`BHSM_COMMON_ENVELOPMENT_MODE_EQUIVALENCE_BLOCKED_BY_UNDERIVED_CROSS_DOMAIN_HESSIAN`

This result preserves the v10.2 Topological-Buoyancy no-go. It does not say
that the full metric lacks scalar deformation degrees. It says that the
present stratified action has not yet decided whether the seam--fold component
and the Hopf breathing component form one physical mode. Physical
inequivalence is not claimed.

## Prior work recovered under earlier names

The campaign imports six earlier chains instead of repeating them:

1. v6.13--v6.27 called normal displacement a moving endpoint, support shift,
   threading trace, and normal-support residual. Full shift variation proved
   fixed-B1 compatibility through local two-derivative order and removed the
   apparent need for a dynamical B1 embedding.
2. v6.27 also derived the exact endpoint relation
   `S_Sigma=-(tau*pi*chi_1/16)q_fold`; the seam trace is therefore a
   constrained boundary projection of the fold amplitude on that domain.
   v6.28--v6.30.5 constructed the scalar-wall fold amplitude `q`, its
   operator/domain, Fredholm projection, positive conditional kinetic norm,
   and reduced interaction. It is not seam depth or Hopf radius.
3. v7.1 identified `a_F` as the vertical metric determinant and stated that
   varying it produces scalar--tensor gravity rather than the stored S5
   action.
4. v7.1 supplied covariant pushforward, trace, and KKT adjoint maps, but kept
   the M8, M5, and M4 actions distinct off shell.
5. v6.29 supplied a lifted metric-modulus Schur response for the fold sector.
   It fixes a normalized response coefficient, not a dimensional cosmic
   modulus.
6. v7.3 and v10.2 established the absent cross-stratum matter/radion source
   and incomplete common-domain stress ownership.

## Configuration-space result

The largest current pre-gauge space contains independently owned M8 fields,
two M5 cap systems, intrinsic M4 fields, and compatibility multipliers. The
embeddings are fixed data. Consequently a varied `X:M4->M8` is an action-domain
extension, not a previously hidden current variable.

There is also a codimension distinction that cannot be suppressed:

- direct `M4 -> M8` has four normal directions;
- lifted `Sigma7 -> M8` has one normal direction but no action owner;
- `B1=M4 -> M5` has one normal and the v6.27 fixed-support theorem.

Thus the symbol `psi` does not yet identify a unique field.

## Existing local radion

For the round vertical metric

\[
G_{ab}^{\rm fiber}=a_F^2\gamma_{ab},\qquad
\beta=\ln(a_F/a_{F0}),
\]

the pure Einstein reduction from eight to five dimensions gives

\[
S_{\rm EH}^{(5)}=
\frac{\kappa_5}{2}\int\sqrt{|g_E|}
\left[R_E-6(\nabla\beta)^2
+R_Fa_{F0}^{-2}e^{-4\beta}+\cdots\right].
\]

Hence the breathing mode is an existing metric degree and has healthy kinetic
sign when `kappa5>0`. No scalar was appended. However its intrinsic M4 source
is absent, the stored S5 action is not its full pushforward, and its
homogeneous limit reproduces the v10.2 no-static-equilibrium result.

## Degree count

After the known seam--fold constraint, the formal reduced basis contains two
conditional components whose equivalence is unresolved:

- local M8 breathing mode `beta`;
- M5 scalar-wall fold amplitude `q`.

The B1 threading trace is constraint-fixed and a coordinate `rho` shift is
gauge. Neither surviving scalar satisfies the complete buoyancy criteria.
The missing fold--Hopf kinetic/Hessian blocks allow physical kinetic rank one
or two. Therefore the selected buoyancy scalar count is zero, but neither
non-uniqueness nor physical inequivalence follows.

## Seam--Fold--Hopf Unification Audit

Historical objects:

- seam/support shift: invariant endpoint trace `S_Sigma` from v6.27;
- scalar-wall fold: normalized Jacobi amplitude `q_fold` from v6.28--v6.30;
- Hopf breathing: `varphi_F=delta ln(a_F/a_F0)` from the M8 metric.

Common perturbation vector: `q_env=(psi,zeta,varphi_F)^T` with
`psi=S_Sigma` and `zeta=q_fold`.

Common kinetic matrix and Hessian: the fold and Hopf diagonal blocks are
derived conditionally; the seam row is removed by the exact constraint
`psi+(tau*pi*chi_1/16)zeta=0`; every fold--Hopf mixed block is
`UNDEFINED_CROSS_DOMAIN`, not zero.

- Gauge rank: `0` for the imported invariant/reduced representatives.
- Constraint rank: `1`.
- Physical kinetic rank: unresolved, with allowed rank `{1,2}`.
- Gauge equivalence: not proved; seam--fold is a constraint projection.
- Intertwiner: `U_zeta_to_psi` derived; Hopf intertwiners absent.
- Schur-complement equivalence: unresolved across M5/M8.
- Boundary-condition equivalence: seam--fold derived locally; Hopf unresolved.
- Source, spectral, and conserved-charge equivalence: unresolved for Hopf.
- Nonlinear continuation: blocked by the missing common linear operator and
  stationary common background.

Unified physical variable: unavailable. Its boundary and interface components
are related exactly, but its interior coefficient and normalization cannot be
derived before the common cross-domain variation.

## Exact next object

`COMMON_PHYSICAL_ENVELOPMENT_MODE_INTERTWINER_BETWEEN_SEAM_SHIFT_FOLD_AND_HOPF_BREATHING`
