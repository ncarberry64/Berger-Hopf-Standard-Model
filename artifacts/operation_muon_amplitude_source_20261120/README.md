# Higgs-amplitude source selection on the incoming-hi trial

This checkpoint resolves a specific possible shortcut: the Higgs-null photon has zero **direct classical amplitude forcing**, but that zero does not survive elimination of the other coupled trial fields. It does not evaluate a physical exterior response or a magnetic moment. The already recorded axial mixed coefficient is recovered, with its indirect source identified. The calibrated Higgs potential, temporal-only admitted baseline, and physical guard `2e-10` are unchanged.

Parent checkpoint: `53e1812a0ad46148af2682c4f570c692c1815c07`. Original evidence is in `../operation_muon_incominghi_20261120/evidence`; its complete manifest is checked before execution. No formation history, old heat campaign, or artificial exterior was run.

## The source derived from the owned action

Write the real Higgs doublet as `H=h n`, `n.T n=1`, and its real antisymmetric gauge generators as `T_a`. For the original intrinsic signed kinetic action `C sum_mu w_mu |D_mu H|^2`, the mixed weak row, with amplitude test `v n` and gauge variation `a`, is

```text
q_hA[v,a] = 2 C sum_mu w_mu [
    D_mu(v n).T T(a_mu) H + (D_mu H).T T(a_mu)(v n)
].
```

Both placements are necessary. If `T(a_mu)H=0` pointwise wherever `h != 0`, both terms vanish for the amplitude test. This is an exact local classical selection rule, including a nonzero background `DH`; it is not an assumption that the background is vacuum. The potential has no direct gauge variation. The corresponding direct kinetic momentum vanishes under the same pointwise condition. Shape, moving-frame, cutoff, native/relative, and other source terms are outside that statement.

For general Higgs tests the source is nonzero. On the saved homogeneous candidate the spatial photon columns give transverse Higgs rows `+0.025396601522590545` and `-0.02539660152175427`. Direct evaluation of both weak placements agrees with the saved Higgs Hessian block within `4.91e-18`. The amplitude projection is below `1.83e-32`.

The original quadratic convention is

```text
L2 = (1/2) qdot.T M qdot + q.T B qdot + (1/2) q.T K q,
momentum = M qdot + B.T q,   E = d_t(momentum) - K q - B qdot.
```

Consequently an imposed gauge column `a(t)` drives the scalar equation through

```text
s_H[a] = K_HA a + B_HA adot
         - d_t(M_HA adot + B_AH.T a),
```

plus the other owned bulk, native/relative and moving-domain sources. This is the source used by the existing coupled Higgs response producer, not a new independent scalar equation. Projection onto a varying `n` retains `n.T d_t p = d_t(n.T p) - ndot.T p`. A held physical incident field still requires its actual trace, time/space derivatives and action conormal; the formula does not supply them.

The saved connection has `||[Omega_1,T(q_H)]||=0.43953964881` and `||[Omega_2,T(q_H)]||=0.43953964880`. These are evaluated commutators in the saved homogeneous frame. They must not be promoted to a complete exterior `D_mu Q_H` without its derivative term. They do show why a vacuum or commuting-background decoupling argument is inapplicable to this finite candidate. Similarly, the neutral amplitude vertex commutes with the retained charge matrix, but the saved six-dimensional body does not (`0.71519358436`); this is not a complete native propagator test or a violation of covariant charge conservation.

## The coupled application and independent dual

Use the original joint `K84 -> D20` constraint reduction, then hold its four temporal boundary values. Let `A=D20[4:,4:]`, `P` contain the three Higgs-null photon spatial columns, and `s=(0,n)`. Complete `[P,s]` orthonormally by twelve columns `X`. No physical source or boundary condition is selected by this basis decomposition.

```text
Y = -(X.T A X)^(-1) X.T A [P,s],
A_eff = [P,s].T A ([P,s] + X Y).
```

All fields are in the common trial system before this elimination. Its one intrinsic Higgs sheet is counted once. The direct axial amplitude-photon entry is zero, but the indirect entry is

```text
-s.T A X (X.T A X)^(-1) X.T A P_3 = 0.1253556148577143.
```

This number was already present in the saved two-component composition matrix; the new result is its action/source decomposition and the failed inference from direct zero to total zero. It is a coordinate-unit trial coefficient, not the requested exterior amplitude reaction. The twelve-column block has singular values from `0.00947888101` to `3.01416978372`; its inverse here has no continuum or outgoing-boundary interpretation.

The independent left equation `(X.T A X).T d = X.T A.T s` gives the same contraction `-d.T X.T A P_3`, differing from the right solve by `2.21e-16` across all three photon columns. The complement residual is `2.79e-14`; lifting to the original interior/Gauss rows gives `4.42e-12`. The held temporal reaction has norm `9.9234165910` and is explicitly retained, not silently forced to zero. Passive common frame rotation changes the returned coefficient by less than `1e-12`. Rebuilding only the original action at radial quadrature 96 versus saved 384 changes it by `8.73e-14`. These checks test this finite calculation; they are not physical uncertainty or outer-domain convergence.

## Signed exterior projection still required

Use outward **action** conormals in the same gauge/constraint reduction. In this paragraph `L_G` denotes the operator obtained by integration by parts from the action weak form: on the temporal quadratic block it is `L_G=-E`, so its source is `s_G=-s_E`. This sign must be converted when using the preceding evolution-source formula. The independently derived Green identity is

```text
q[z,u] = <z,L_G u> + sum_faces <gamma z,p_u>
       = <L_G^sharp z,u> + sum_faces <p_z,gamma u>,
<z,L_G u>-<L_G^sharp z,u>
       = sum_faces (<p_z,gamma u>-<gamma z,p_u>).
```

When a same-domain independent adjoint with `L_G^sharp z=0` and wall trace `gamma z=n` exists, the amplitude conormal is therefore

```text
n.T p_u,wall = -<z,s_G> + sum_faces <p_z,gamma u>
                         - sum_other_faces <gamma z,p_u>.
```

Entering, released, edge and endpoint terms remain in these sums. The finite transpose solve above verifies only its local algebraic counterpart. No full physical Green identity was numerically applied.

For the prior checkpoint's convention, `p_ext=Lambda_R(w-w_inc)-t_inc` and `K_int w+p_ext+j_other=0`, so its net source is `f=-p_ext-j_other`. Hence `chi_H=n.T f_H` has the opposite exterior-conormal sign. A moving projection adds `delta(n.T f_H)=n.T delta f_H+(delta n).T f_H`; frame, clock, measure and cut derivatives also remain. A computational cut is not an extra Higgs sheet. No receiving-cut regression was possible because no verified native exterior collar was recovered.

For the complete system, the scalar and complementary equations must remain coupled:

```text
L_hh h_B + L_hz z_B = s_h,
L_zh h_B + L_zz^R z_B = s_z.
```

Eliminating the second row changes both the operator and source: `s_h,eff=s_h-L_hz (L_zz^R)^(-1)s_z`. The direct classical zero controls only one part of `s_h`; it does not set this complete source to zero. The present finite calculation exhibits its indirect mechanism without claiming a native exterior realization.

The common parent boundary functional owns both gauge and composite Higgs derivatives. Its native mixed term is the same-functional derivative `delta_h delta_a Gamma_boundary`, with the relative subtraction, regulator and moving-domain contacts varied once. The Higgs inverse kernel is `(2 C_f G_DtN)^(-1)-Chi_LR,f`. An independent bulk radial Higgs action or an extra scalar Pauli term would change that ownership. Neither is introduced here.

## Focused recovery and the first missing input

The source ledger records exact hashes of the inspected action records, including newer local research bytes whose Git HEAD is not evidence of their contents. Existing coupled Higgs and mean-heat adjoints retain the missing joint derivatives rather than set them to zero. The local overlap construction uses a different 336-dimensional harmonic problem and explicitly stops short of a global physical exterior/LSZ match. The older corrected retarded Maxwell producer uses an October 10 corrected iterate and prescribed source columns, not this incoming-hi background. Its exact named result directories were not materialized at the two checked repository locations. This is a scoped finding, not a claim that no offline copy exists; no further broad Downloads scan was performed.

The **first unavailable source coefficient** is the same-formed-background external connection and kinetic profile defining `L_zz^R[X0,out]`, in particular

```text
C_mu(x) = D_mu Q_H(x) = partial_mu Q_H(x) + [Omega_mu(x),Q_H(x)],
```

on the exterior overlap, together with the composite same-state derivative above. The saved 268-component wall germ and the interior `0 <= rho <= pi/2` action builder do not provide this exterior profile. Their nonzero local commutators prevent replacing it by a commuting vacuum without an additional, unsupported assumption. The subsequent source operand is the independently normalized held incident solution `a_inc^Q(x)` and its conormal, entering `s_z=-L_zA a_inc^Q + ...`. Existing outgoing selection specifies the retarded branch (`omega+i0`), not these coefficient values or incident data.

A testable next construction is one source-selected mixed application on an action-admitted continuation of that **same formed background**, with its common relative domain and independent Green dual. It must match the known wall jets, satisfy the owned background Euler/Gauss equations, and carry the observer-calibrated incident trace/conormal. Assemble shared interior/exterior variables before reduction, retain contacts, then test the signed Green residual and the projected response under actual domain/discretization refinement using the unchanged guard and specified norms. No full inverse is required. An arbitrary impedance, extension, zero source, or the old different-background overlap does not pass this admission test.

The previous finite sensitivity remains `delta gap = -7.21199006824777e-7 delta chi_H` when its five consumed readouts are fixed, up to the recorded finite adjoint remainder. The physical `chi_H`, photon/spin normalization, native subtraction and total uncertainty are still unevaluated. Consequently neither `a_mu` nor `g_mu` is reported.

## Reproduction

From the repository root, in an inspected environment with NumPy/SciPy:

```text
python -I -S artifacts/operation_muon_amplitude_source_20261120/verify_source.py --site-packages INSPECTED_GLOBAL_SITE --output RESULT_PATH
```

The verifier rejects unexpected import origins, disables bytecode writes, blocks network/subprocess calls, uses one numerical thread, and verifies the original evidence hashes. Two independent executions produced byte-identical `RESULT.json`; hashes and the scoped payload review are in `REPLAY_RECEIPT.json` and `INVENTORY.json`.
