# BHSM N=3 measured six-owner continuation v17.05

Let `x in R^376` denote the scaled anchored KKT variable and let
`F(x) in R^376` be the unchanged fresh-SBP physical residual. The six owner
norms used at v17.05 are

`n = (||F||, |F_T|, ||F_w0||, ||F_v0||, ||F_scale||, |F_event|)`.

No component of `F` is replaced or renormalized. In particular,
`F_scale` contains all 23 open-orbit scale-stationarity rows.

For the fresh residual Jacobian `J` and damped physical normal operator

`H_mu = J^T J + mu^2 I`,

form the six-dimensional trial subspace

`d_b = H_mu^(-1) grad(log n_b)`.

Because the analytic Jacobian model gave the wrong `v_0` response sign at
v17.01, the response matrix is measured from the actual residual:

`M_ab = D(log n_a)[d_b]`

by centered evaluations of `F(x +/- epsilon d_b)`. Coefficients are chosen by
the physical-normal maximin problem

`maximize t`

subject to

`M c <= -t 1`,

`c^T (G H_mu^(-1) G^T) c <= 1`,

where the rows of `G` are the six fractional owner gradients. The resulting
direction is `d=sum_b c_b d_b`. A state is promoted only when exact nonlinear
evaluation decreases all six original owner norms and preserves the positive
Legendre domain.

The accepted v17.05 state is

| owner | before | after |
|---|---:|---:|
| complete | 1.446086490970 | 1.428689906334 |
| period | 0.722701415446 | 0.703793411493 |
| `w_0` | 0.980460966550 | 0.973745697552 |
| `v_0` | 0.622140476897 | 0.620368346240 |
| `log_scale` | 0.440239029257 | 0.432309885844 |
| event | 0.124504504205 | 0.122933895890 |

The minimum fractional progress is `0.002848441345` and
`eta_min=0.778050948322`. This materially advances simultaneous N=3 event
saddle closure. It does not establish closure, the common M5 -> M4
pushforward, the broken branch, a returned mass operator, or full BHSM.

The scale result has a specific ownership meaning: the scale block is an
ordinary equation block of the open physical orbit and can be jointly
decreased without removing it. The event/environment-dependent return scale
remains a later output of the broken reconstruction BVP.

## v17.06-v17.14 continuation

The single six-owner damping subspace lost simultaneous descent at v17.06,
but the unchanged residual retained common descent in the span of all 18
owner/filter normal directions. v17.07 orthonormalized that span, measured its
actual response, and certified maximin descent with the convex owner-simplex
dual. Exact nonlinear comparison of ranks 6, 9, 12, 15, 18 and all three
single-filter subspaces selected the `1e-6` family at v17.08, v17.10, v17.11,
and v17.13.

Dense exact-radius refinement selected factor `0.064` at v17.12. The fresh
v17.13 rebuild then accepted factor `0.1`, reaching:

| owner | v17.05 | v17.13 |
|---|---:|---:|
| complete | 1.428689906334 | 1.383417886043 |
| period | 0.703793411493 | 0.677117633290 |
| `w_0` | 0.973745697552 | 0.940057261626 |
| `v_0` | 0.620368346240 | 0.610774014072 |
| `log_scale` | 0.432309885844 | 0.417559825333 |
| event | 0.122933895890 | 0.118278228365 |

The v17.14 soft eigenpair residual is `1.7e-14`, its lower/upper gaps are
`0.455630407903/0.002098081487`, and `eta_min=0.777122429571`. N=3 closure
and the common event pushforward remain open.

Fresh post-dense rebuilds v17.15-v17.16 accelerate the same certified family:

`1.383417886043 -> 1.358000324006 -> 1.329816603643`

for the complete residual, and

`0.118278228365 -> 0.115746656221 -> 0.113054939136`

for the identical event magnitude. The latest period, `w_0`, `v_0`, and scale
norms are `0.644977936704`, `0.899842579758`, `0.599765834697`, and
`0.400779135003`; `eta_min=0.775832703564`. The minimum six-owner fractional
progress increased to `0.010824146325`.

Two further fresh passes reach v17.18:

`1.329816603643 -> 1.300395602281 -> 1.272877993568`

for the complete residual and

`0.113054939136 -> 0.110285053452 -> 0.107558924761`

for the event. The latest period, `w_0`, `v_0`, scale and eta minimum are
`0.611901245067`, `0.857718051797`, `0.585620731388`, `0.382990119281`, and
`0.773679579542`. All six owner norms decrease in the promoted step.

v17.20 reaches complete residual `1.247036920944`; dense radius refinement at
v17.21 selects factor `0.075` and improves it to `1.252645654335` relative to
the v17.18 base while maximizing the six-owner bottleneck on that fixed
direction. Because `v_0` remains the recurring nonlinear limiter, v17.22
tests bounded `v_0` priority factors only inside the same measured tangent
families. Priority `3` in the `1e-6` family wins under the original unweighted
six-owner acceptance:

| owner | v17.21 | v17.22 |
|---|---:|---:|
| complete | 1.252645654335 | 1.192046120259 |
| period | 0.600835741708 | 0.571634002410 |
| `w_0` | 0.842509946308 | 0.805293753488 |
| `v_0` | 0.580401743588 | 0.546193432306 |
| `log_scale` | 0.376290798969 | 0.359549472209 |
| event | 0.105533276232 | 0.099693053009 |

The minimum actual fractional reduction is `0.044173001142` and
`eta_min=0.772159229346`. Priority is a numerical direction preconditioner;
the physical residual and promotion criteria are unchanged.
