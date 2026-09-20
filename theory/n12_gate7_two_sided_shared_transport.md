# Two-sided shared-input HS transport

Use the original fixed trial frames, physical domain and two-radius norm.
Write `P = frozen_right^{-1} test`, let `Q` be the retained output projection
at node 14, and put `L=(2h/3)QP`. The left and right input frames are distinct.
No physical input projection is identified with `Q` by this notation.

For either endpoint, let `E` be its trial frame, `A=DF_endpoint E`, `M` the
midpoint derivative on the same actual family, and `U` an exact proposed
midpoint input map. Set `B=L DF_mid U`. The exact HS chain rules are

```
left:  Dmid = E/2 + h A/8
right: Dmid = E/2 - h A/8.
```

Thus the complete projected local defects are

```
left:  QP(frozen_left+I)E + (h/6)QP A + B + L M(E/2+h A/8-U)
right: Q-QP E            + (h/6)QP A + B + L M(E/2-h A/8-U).
```

For an arbitrary exact anchor `A0`, these are `C+B+D(A-A0)`, where

```
D_left  = (h/6)QP + (h/8)L M
D_right = (h/6)QP - (h/8)L M
C_left  = QP(frozen_left+I)E + (h/6)QP A0 + L M(E/2+h A0/8-U)
C_right = Q-QP E            + (h/6)QP A0 + L M(E/2-h A0/8-U).
```

These identities hold before interval evaluation. In particular, the left
constant is not the right constant, and the input-map mismatch cannot be
discarded. All endpoint residual cancellation and its weighted remainder
must occur before applying the interval `M`, as in the certified right block.
The implementation is `two_sided_input_transport.py`; tests compare it with
the independently implemented original one-column chain for both sides.

The original midpoint state coordinates are, in order, left scalar, right
scalar, 74 left coordinates, 74 right coordinates, and 99 inherited box
coordinates. Consequently, a left endpoint model uses midpoint coordinates
`[0]+[2,...,75]`; the right endpoint uses `[1]+[76,...,149]`. Endpoint base
solve errors remain separate from midpoint errors. Input longitudinal axes
are at node 13 on the left and node 14 on the right; the output axis remains
at node 14. Changing these identifications would change the physical map.

## Reusing verified midpoint data

The pinned left and right midpoint records have identical exact arrays for
the state domain, weighted tube directions, base response, and base predictor
derivatives. `n12_gate7_left_saved_family.py` checks both midpoint and radius
arrays before permitting this statement. Directional response arrays and
input maps are not covered by that equality.

The 124 midpoint base equations contain no physical input leg. Their retained
coefficients can therefore be reused after verifying equality of all effective
base radii and state predictors. The preparatory eigenvalue-radius slot is
excluded from that radius comparison only because both producers replace it
with the radius of their Rayleigh predictor. The reuse producer separately
requires exact equality of the entire source-bound Rayleigh coefficient and
remainder arrays; it does not infer equality from a small numerical difference.
Every saved base-equation support is replayed, and both the old and new source
fingerprints are retained. This permits reuse of those equations, not reuse of
the right directional residuals or its transport bound.

An adjoint covector is a freely chosen exact cancellation coefficient in
`Y-beta G`, because `G=0` on the original implicit graph. It may be proposed
using an earlier anchor. That transfers neither the earlier error bound nor
its input map: the new source-bound left action residual and all its tails
must be evaluated explicitly. The left anchor producer recomputes its base
adjoint against the left input map, with the positive chain-rule sign.

## Deferred base cancellation and the directional output adjoint

It is also exact to retain `W=Y-v2 G2-v3 G3` and defer all 124 base
equations to the shared pretransport cancellation. Their remainders are
then multiplied by the actual common-input coefficients before bounding.
Changing this free cancellation choice does not change the input map,
base predictors, correction radii, or separately certified velocity models.
The reuse checks require exact equality of the state-only Rayleigh jet and
replay all 124 base-equation supports against their original parent.

For the actual endpoint, the last two point adjoint blocks can be computed
without differentiating the action in every physical direction. Write
`a_i=rw_i/weights[37+i]`, `p=psi`, and
`d=(configuration/weights, a*h)`. The three free-vector third contractions

```
g_i = D3[e_i,p,p]
q_i = D3[e_i,p,a*p]
t_i = D3[e_i,p,d]
```

give `c=p.q` and `r=p.t`. For the normalized scalar
`y=z.(N,delta)/||N||` and its directional derivative `Y`, put
`alpha=(z.(N,delta))/||N||^3`, `v=z_N/||N||-alpha*N`, and
`gamma=z_delta/||N||`. The two directional-variable gradients are

```
Y_psi_u[i] = rw_i*b*v_vel[i] + gamma*(b*(2*q_i+a_i*g_i)+2*s*t_i)
Y_h_u[i]   = rw_i*s*v_vel[i] + gamma*s*a_i*g_i
Y_psi_u[61] = 0
Y_h_u[61]   = sum_i(v_vel[i]*rw_i*psi_i) + gamma*c.
```

Solve the response adjoint first, then the line adjoint after subtracting
the triangular coupling. These solves only propose exact point covectors;
the uniform residuals remain part of the proof. At the retained right
endpoint, the independent full 248-variable adjoint and this formula agree
within `4.20e-140` in the line block and `3.21e-145` in the response block.
The separately computed actual left-endpoint proposal reproduces byte for
byte. This verifies the proposal, not a global contraction inequality.

## Retained-axis remainder evaluation

The first column of the original two-radius majorant fixes the physical
input to `u=a*t`, where `a` is the stored node-13 axis and `|t|<=1`.
The state domain remains the original domain. If the source-bound common
error map is `eta=E(theta)u`, then
`|eta_i|<=sup_theta |(E(theta)a)_i| |t|`. An outward power-of-two upper
bound `s_i` permits the exact substitution `eta_i=s_i*xi_i`, `|xi_i|<=1`.
Multiplying the original dyadic correction radius by `s_i` is exact. This
changes the auxiliary parametrization, not the retained physical radius.

The scalar action can be evaluated with this substitution before any
nonlinear remainder norm is taken. Existing complete velocity models can
be restricted by the same linear substitution. Their prior remainder is
multiplied by `max(||a||_2,max_i s_i)`; the possible rounding excess in the
stored axis norm is retained. Subsequent implicit-equation refinements are
intersected with this original inclusion, then expressed in the `xi`
coordinates. Endpoint base cancellation still precedes interval midpoint
transport, and all weighted residual tails are retained until substitution.

The resulting bound covers only longitudinal physical input. It may improve
the first column of a separately certified complete-input majorant; it cannot
supply the transverse column or establish a full-input contraction by itself.

## Scope

This algebra and the original implicit inclusions prepare a left-block
certificate. They do not themselves establish a uniform left operator bound,
all-history coverage, the nonlinear 72-direction physical first jet,
Gate-7 closure, or BHSM completion.
