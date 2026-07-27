# BHSM v6.8.0: Berger-Clifford reduction of the wall coupling

Primary result:

`BHSM_Y_SIGMA_EXP_MINUS_BETA_REJECTED_BY_CANONICAL_NORMALIZATION`.

The exact Berger geometry contains inverse-vielbein factors proportional to
`exp(-beta)`, but the `Gamma_star` adopted in v6.3--v6.7 is not an internal
coordinate-index Hopf matrix. It is the collar-normal Clifford partner used
in `K=i Gamma_n Gamma_star`. Consequently the internal interaction operator
is `Gamma_star tensor identity_S3`. Its overlap equals the fermion kinetic
norm, so canonical normalization cancels the full Berger volume dependence:

```text
y_sigma^(4)(beta)=lambda_geom=y_sigma^(4)(0).
```

The reduction fixes the relative law to one. It does not fix the absolute
dimensionless coefficient `lambda_geom`; that one primitive remains.

## Exact Berger geometry

Use

```text
theta in [0,pi], phi in [0,2pi], psi in [0,4pi]
```

and put `a=R/2`, `c=a exp(beta)`. In coordinate order
`(theta,phi,psi)`,

```text
g_B =
  (R^2/4) [
    [1, 0, 0],
    [0, sin^2(theta)+exp(2 beta)cos^2(theta),
        exp(2 beta)cos(theta)],
    [0, exp(2 beta)cos(theta), exp(2 beta)]
  ].
```

Thus

```text
det(g_B)=(R^6/64) exp(2 beta) sin^2(theta),

g_B^(-1)=(4/R^2) [
  [1, 0, 0],
  [0, csc^2(theta), -cos(theta)csc^2(theta)],
  [0, -cos(theta)csc^2(theta),
      exp(-2 beta)+cot^2(theta)]
].
```

For the left-invariant forms

```text
eta_1= cos(psi)dtheta+sin(psi)sin(theta)dphi,
eta_2=-sin(psi)dtheta+cos(psi)sin(theta)dphi,
eta_3= dpsi+cos(theta)dphi,
```

an orthonormal coframe and its derived dual are

```text
e^1=a eta_1,  e^2=a eta_2,  e^3=c eta_3,

X_1=(2/R)[ cos(psi)partial_theta
           +sin(psi)csc(theta)partial_phi
           -sin(psi)cot(theta)partial_psi ],

X_2=(2/R)[-sin(psi)partial_theta
           +cos(psi)csc(theta)partial_phi
           -cos(psi)cot(theta)partial_psi ],

X_3=(2/R)exp(-beta)partial_psi.
```

The volume form and total volume are

```text
dvol_B=(R^3/8)exp(beta)sin(theta)
       dtheta wedge dphi wedge dpsi,

Vol(S3_B)=2 pi^2 R^3 exp(beta).
```

At `beta=0` this is the round three-sphere of radius `R`, not a collapse.

## Connection and an exact internal mode

With `d eta_1=-eta_2 wedge eta_3` cyclically, Cartan's first equation gives

```text
omega_12=[exp(beta)-2exp(-beta)]e^3/R,
omega_13= exp(beta)e^2/R,
omega_23=-exp(beta)e^1/R.
```

For Hermitian Pauli matrices and
`D_B=i Gamma^hat_a nabla_(X_a)`, the internal operator may be written

```text
D_B = i sum_a Gamma^hat_a X_a
      +[exp(beta)+2exp(-beta)]/(2R).
```

A constant spinor in the global left-invariant spin frame is therefore an
exact eigenspinor. Its unit-normalized density and eigenvalue are

```text
f_beta^dagger f_beta
  =1/[2 pi^2 R^3 exp(beta)],

lambda_inv(beta)
  =[exp(beta)+2exp(-beta)]/(2R).
```

The round value is `3/(2R)`. This establishes an exact homogeneous-sector
mode, not a global ordering theorem for the entire Berger spectrum. No such
ordering is needed: the wall overlap below is identical for every normalized
admissible internal mode.

No repository source or internal-operator derivation supports
`rho(theta) proportional to cos^2(theta/2)` as an eigenspinor density. It is
not used.

## `Gamma_star` classification

The v6.3 source defines two Hermitian matrices in the rank-two collar factor,
`Gamma_n` and `Gamma_star`, and then

```text
K=i Gamma_n Gamma_star,

C_BHSM=-i Gamma_n nabla_n
       +Gamma_star m_B(x)+C_tangential.
```

The same definition is retained by the adopted v6.6/v6.7 wall invariant.
Therefore `Gamma_star` is candidate A: the collar-normal Clifford
partner/chirality operator. It has no Berger scale.

The other candidates are distinct:

- `Gamma^hat3` is an orthonormal internal Hopf-direction matrix and has no
  explicit scale.
- The internal volume element
  `i Gamma^hat1 Gamma^hat2 Gamma^hat3` is frame normalized and has no
  explicit scale.
- A projected composite was never defined by the adopted action.
- The coordinate-index internal matrix is

```text
Gamma^psi
 =-(2/R)cot(theta)
   [sin(psi)Gamma^hat1+cos(psi)Gamma^hat2]
  +(2/R)exp(-beta)Gamma^hat3.
```

Only its vertical component carries `exp(-beta)`. The transverse mixing is
required by the full inverse vielbein. `Gamma^psi` is coordinate-indexed,
changes its component form with the Euler convention, and is not the
declared `Gamma_star`.

This proves
`BHSM_WALL_GAMMA_OPERATOR_HAS_NO_BERGER_SCALING` and rejects the proposed
input `gamma_star_projection=exp(-beta)`.

## Canonical four-dimensional reduction

Use the diagnostic factorization

```text
Psi(x,y)=psi(x)f_beta(y).
```

The adopted action already contains the M4 wall field `sigma`. Its available
internal parent candidate is the scalar fiber singlet; the v6.6/v6.7 action
does not contain an unnormalized S3 scalar carrier. Introducing a new
`Z_sigma` here would therefore change the ontology rather than normalize the
adopted invariant.

For an arbitrary admissible mode,

```text
Z_psi(beta)
 =integral_S3 dvol_B f_beta^dagger f_beta,

I_sigma(beta)
 =integral_S3 dvol_B f_beta^dagger
  (Gamma_star tensor identity_S3)f_beta
 =Z_psi(beta) Gamma_star.
```

After `psi_canonical=sqrt(Z_psi) psi`,

```text
y_sigma^(4)(beta)
 =lambda_geom I_sigma/Z_psi
 =lambda_geom.
```

For the unit mode, `Z_psi=1` directly. Here `R` has length dimension,
`f_beta` has dimension `length^(-3/2)`, the internal measure has dimension
`length^3`, and `lambda_geom` is dimensionless. The four-dimensional fields
have their usual canonical dimensions: `dim(psi)=3/2` and `dim(sigma)=1`.

The absolute result is not locked because the adopted boundary action has no
higher-dimensional parent coefficient theorem. The strongest exact result is

```text
y_sigma(beta)/y_sigma(0)=1,
y_sigma(0)=lambda_geom remains one primitive.
```

## Hopf stiffness and kill tests

The prior exact identity

```text
tau_nested/tau_transverse=exp(2 beta)
```

does imply

```text
sqrt(tau_transverse/tau_nested)=exp(-beta).
```

It does not connect that square root to the collar operator or its canonically
normalized overlap. Using the identity as the coupling law would be a hidden
operator-identification assumption.

Coordinate and orthonormal-frame invariance, Euler-convention independence,
the `4pi` fiber period, the round limit, dimensions, kinetic normalization,
charges and `Y_BH`, family universality, conjugation, wall parity, and scalar
sign all pass. No measured input, sector-dependent coupling, physical bulk
Dirac parent law, scalar normalization, or assumption `lambda_geom=1` is
introduced. Frozen predictions and official prediction logic are unchanged.
