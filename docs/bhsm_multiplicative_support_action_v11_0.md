# BHSM v11.0 Multiplicative Support Action

## Exact result

On the regular support group `(0,1]`, continuity and

`q_D(uv)=q_D(u)+q_D(v)`, `q_D(1)=0`

give

`q_D=-lambda_D log(upsilon)`, `lambda_D>0`.

The invariant field-space metric and canonical kinetic term are

`ds_D^2=lambda_D^2 dupsilon^2/upsilon^2`,

`S_D,kin=-1/2 int sqrt(-G) |nabla q_D|^2`.

This invalidates the constant-kinetic realization retained as a v10.4
counterexample. The author axiom `U_D,bare=0` is imposed without adding a
mass, double well, or restoring force.

## What composition does not fix

Multiplicative couplings are continuous characters,

`F_a(upsilon)=upsilon^w_a=exp[-(w_a/lambda_D)q_D]`.

The current parent action declares `upsilon` to be an independent
dimensionless scalar. It does not define how support dilation acts on the
metric, measure, bundles, cap embeddings, or intrinsic M4 fields. Tensor rank,
density weight, dimensionality, and covariance therefore do not determine
`w_a`.

Two integer assignments already satisfy covariance, positivity on the regular
domain, `F_a(1)=1`, dimensional consistency, and nontrivial `q_C` and `q_W`
sources:

| assignment | `w_C` | `w_W` | all other weights |
| --- | ---: | ---: | ---: |
| A | 1 | 1 | 0 |
| B | 1 | 2 | 0 |

They are inequivalent because their canonical slopes `(w_C/lambda_D,
w_W/lambda_D)` differ. Choosing A because it has the smallest positive
integers would be a sparsity convention, not a theorem of the action.

The Haar metric is unique only up to `lambda_D`. In the free scalar sector
that factor can be absorbed into the canonical coordinate. Once any nonzero
character is present, the action depends on `w_a/lambda_D`; the scale is then
a relative interaction strength and cannot be set to one as a harmless unit
choice.

## Verdict

Kinematic result:
`BHSM_MULTIPLICATIVE_SUPPORT_HAAR_KINEMATICS_DERIVED`.

Action result:
`BHSM_MULTIPLICATIVE_SUPPORT_HAAR_KINEMATICS_DERIVED_BUT_NORMALIZATION_AND_SUPPORT_WEIGHTS_NOT_ACTION_FIXED`.

Exact next object:
`ACTION_DERIVED_SUPPORT_REPRESENTATION_FUNCTOR_ON_STRATIFIED_SECTORS_WITH_FIXED_HAAR_SCALE`.
