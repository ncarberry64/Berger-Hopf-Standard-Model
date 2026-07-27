# BHSM v6.9.0: junction EFT, sheet screen, and index certification

Primary result:

`BHSM_AVAILABLE_C_BHSM_HAS_ZERO_LIGHT_HEAVY_COUPLING`.

The available v6.7/v6.8 operator has an exact zero light-heavy block. The
single bounded invariant that could change this result is the unresolved
boundary overlap

```text
j_J=<f_0,C_junction f_1>.
```

Family universality makes its minimal block `j_J I_3`. Even if nonzero, its
Schur correction is channel universal and begins at energy order `E^0`, not
`1/p`. No `K_prop` or relative neutral phase is generated.

The lower-sheet kill screen stops at the missing constraint-reduced
junction-bending Hessian invariant. The auxiliary noncompact complete-collar
operator does have a Callias index of one per selected slot, but that result
does not select the physical compact-cap domain.

## Preserved v6.8 theorem

The v6.8 result remains

```text
y_sigma^(4)(beta)=y_sigma^(4)(0)=lambda_geom.
```

`lambda_geom` is one universal dimensionless primitive. `Gamma_star` is the
beta-independent collar Clifford partner, not `Gamma^psi` or
`Gamma^hat3`. Berger volume and normalized-mode density cancel, and
`sqrt(tau_transverse/tau_nested)=exp(-beta)` does not determine the wall
coupling.

## Gate A: smallest junction EFT

Use

```text
H_total=H_L direct sum H_H = C^3 direct sum C^3.
```

In basis order

```text
|P0,f0>, |P1,f0>, |P2,f0>,
|P0,f1>, |P1,f1>, |P2,f1>,
```

`f0` is the v6.7 neutral compact zero mode and `f1` is the first positive
mode on the same declared maximal-isotropic diagnostic domain. The inner
product is `delta_family` times the normalized cap `L2` product. All six
states have `Q_em=Y_BH=0`; triality cycles the three copies in each block.
Conjugation is componentwise with the conjugate domain.

The exact projectors are

```text
P_L=diag(I_3,0_3),  P_H=diag(0_3,I_3).
```

They are idempotent, orthogonal, and complete on the truncation. With first
heavy gap `M_H>0`, the available blocks are

```text
H_LL=p I_3,
H_HH=(p+M_H) I_3,
V_LH=V_HL=0.
```

The exact zeros follow as follows:

- `C_normal+lambda_geom sigma Gamma_star`: `f0` and `f1` are orthogonal
  eigenmodes of this self-adjoint block.
- `C_angular` and `C_Berger`: the smallest truncation uses the same angular
  state, so these act on the common factor and leave `<f0|f1>=0`.
- `C_connection`: the available neutral constant profile is
  family-universal and normal-mode diagonal; charge-proportional terms vanish.
- `C_polarization`: the exported v6.7 normal operator has no polarization
  dependence.
- family/triality projectors commute with both projectors and do not change
  `f0` into `f1`.

A junction-supported insertion is not killed by bulk `L2` orthogonality. The
smallest Hermitian, neutral, triality-singlet extension is therefore

```text
V_LH=V_HL=j_J I_3,
```

with real `j_J`. The current action/domain data do not calculate it.

### Exact Schur reduction

Away from the heavy pole `E=p+M_H`,

```text
C_eff(E,p)
 =[(p-E)-j_J^2/(p+M_H-E)] I_3.
```

For `|E-p|,|j_J| << M_H`,

```text
1/(p+M_H-E)
 =1/M_H+(E-p)/M_H^2+(E-p)^2/M_H^3+... .
```

The exact light root and controlled expansion are

```text
E_light
 =p+[M_H-sqrt(M_H^2+4j_J^2)]/2,

delta E
 =-j_J^2/M_H+j_J^4/M_H^3+... .
```

The leading coefficient has mass dimension
`[j_J]^2/[M_H]`; it was not assumed to be `1/M_H`. The result is local and
Hermitian away from the pole. It is proportional to `I_3`, independent of
path or environment, and has leading scaling `E^0`. It therefore does not
define

```text
K_prop/(2p).
```

For the actually available operator `j_J=0`, so `delta E=0`. For the minimal
nonzero universal extension all three channels acquire the same constant
shift. In both cases

```text
Delta phi_ij=0.
```

No operational mass-squared matrix is produced because there is no
`kappa/(2p)` term.

## Gate B: lower-sheet kill screen

The smallest declared physical coordinates are

```text
q=(delta sigma,delta beta,delta b),
```

where `delta b` is the existing junction-position/embedding bending
perturbation. The known scalar-Berger kinetic block is
`diag(1,6/7)`. Retain the unresolved physical bending normalization as
`k_b`; admissibility requires `k_b>0`.

Lapse/length and moving-endpoint/domain variations are constrained. Their
gauge kernel must be removed before forming

```text
H_phys=H_PP-H_PC H_CC^(-1)H_CP.
```

No sign is inferred from `det(H_CC)`. Existing v6.1.7 and v6.5 ledgers state
that the action curvature, junction-bending operator, and cap Green operator
are absent.

For the exact pure-bending witness

```text
v=(0,0,1),
```

define the one missing invariant family

```text
B_sheet
 =e_b^dagger
  [H_PP-H_PC H_CC^(-1)H_CP]
  e_b.
```

Then

```text
R_lower=B_minus/k_b,
R_upper=B_plus/k_b.
```

The derived branch orientation `nu1_lower<0<nu1_upper` does not determine
action curvature. A lower-sheet tachyon would require
`k_b>0` and `B_minus<0`; a ghost would instead require `k_b<0`; a gauge
direction would be removed as a constraint artifact. Neither `B_minus` nor
`B_plus` is supplied. Thus the result is

`BHSM_LOWER_SHEET_KILL_SCREEN_REQUIRES_ONE_MISSING_HESSIAN_INVARIANT`.

The lower sheet is not rejected. No conclusion about full upper-sheet
stability follows from this three-dimensional trial space.

## Gate C: auxiliary Callias index

Use the auxiliary graded complete-collar operator

```text
D_aux=[[0,A^dagger],[A,0]],
A=partial_rho+lambda_geom sigma(rho).
```

This is a BHSM elliptic certification operator, not a physical bulk Dirac
parent law. It acts on the noncompact normal collar `R`, with grading
`K=i Gamma_n Gamma_star`, `L2` inner product, and asymptotic decay.

Its principal symbol is

```text
[[0,-i xi],[i xi,0]],
```

with determinant `-xi^2`, hence it is elliptic for `xi!=0`. For the selected
wall orientation,

```text
m_minus<0<m_plus,
m=lambda_geom sigma,
```

and both limits are nonzero. The asymptotic potential is coercive and
localized changes are compact perturbations, so the operator is Fredholm and
Callias applies:

```text
ind(A)
 =[sgn(m_plus)-sgn(m_minus)]/2
 =1
```

per selected internal slot. Triality gives total net index three.

The scalar rank-one equation independently gives one normalizable

```text
f proportional exp[-integral m d rho]
```

while the adjoint exponential is nonnormalizable. Thus paired zero modes are
excluded for this auxiliary complete-collar problem, not merely inferred
from index one.

APS is not applied. The physical compact cap lacks an action-selected
tangential boundary operator, APS projector, eta invariant, and boundary
kernel. The Callias result agrees with the selected-domain numerical index
one, positive gap, and absent opposite-chirality zero mode, but it does not
select or certify the physical compact-cap domain.

## Claim boundary

No measured input, fitted matrix, sector-dependent coupling, manufactured
`K_prop`, physical bulk Dirac law, global spectrum, full PDE, hidden
`lambda_geom=1`, or lower-sheet selection is introduced. Frozen predictions
and official prediction logic are unchanged.
