# BHSM v6.0.1 B8/S7 Physical Domain and Action-Source Closure

## Primary result

`BHSM_B8_S7_PARENT_ACTION_SOURCE_MISSING`

The exact v6.0 nested topology is unchanged:

```text
S3 -> S7 -> S4
S1 -> S7 -> CP3
S2 -> CP3 -> S4
U(1) subset Sp(1),  p_H = tau o p_C.
```

No stored BHSM source is a foundational `B8` action or an action-selected
`S7` boundary action. The repository therefore cannot yet select physical
time, signature, metric, squashing, orientation, collar scale, fiber measure,
or a map to an observed `3+1` domain.

## Physical-domain candidates

The candidates remain separate:

- A compact Riemannian `B8` with Euclidean boundary `S7` is mathematically
  coherent but has no time or causal interpretation.
- A Lorentzian eight-dimensional bulk can have a spacelike boundary with
  timelike normal or a timelike boundary with spacelike normal. These have
  different induced signatures and variational data.
- Euclidean preparation followed by Lorentzian continuation is unavailable
  until the continued action, fields, contours, and boundary conditions are
  specified.
- A canonical `R_t x B8` construction has nine total dimensions and boundary
  worldvolume `R_t x S7`; v5.9 supplies only a reduced collective Hamiltonian,
  not this canonical field theory.
- An independent Lorentzian `M3,1` times compact internal `K` branch most
  naturally preserves ordinary causality and the v5 distinction between
  spacetime and internal Berger geometry. It still lacks a Kaluza–Klein parent
  action and does not make `S7=partial B8`.

No branch is selected.

## Energy–geometry relational physicality candidate

A candidate interpretation is retained: a spacetime region becomes physically
distinguished when an action-derived energy distribution encloses or
constrains it and creates a geometric or normal-stress differential at an
interface. This becomes testable only through all of the following:

1. a bulk metric equation coupled to a conserved stress tensor;
2. a boundary or junction equation coupling normal stress to extrinsic
   geometry;
3. a constraint selecting admissible bounded initial or boundary data; and
4. a conserved energy-transfer law across the interface.

Topology, a coordinate boundary, or a nonzero normalized vacuum functional is
not enough. The current repository supplies no `B8` geometry–stress action and
cannot evaluate this criterion. It is a conditional physicality principle, not
a derived BHSM equation.

## Time and signature

With signatures recorded as `(timelike, spacelike)`:

- Riemannian `B8`: `(0,8)`, spacelike normal `epsilon_n=+1`, boundary `(0,7)`.
- Lorentzian bulk with spacelike boundary: `(1,7)`, timelike normal
  `epsilon_n=-1`, boundary `(0,7)`.
- Lorentzian bulk with timelike boundary: `(1,7)`, spacelike normal
  `epsilon_n=+1`, boundary `(1,6)`.
- Canonical `R_t x B8`: `(1,8)`, boundary worldvolume `(1,7)` while each `S7`
  slice is Riemannian.
- Product `M3,1 x K`: time remains on the independent Lorentzian factor.

The standard Hopf maps are Riemannian submersions. They do not turn `S4` into
observed Lorentzian spacetime or establish causal propagation.

## Parent-action source trace

- v5.4 integrates a symbolic candidate over a relative Berger boundary with
  `sqrt(det h_rho)d3x`.
- v5.6 separates an unspecified spacetime `B`, internal Berger space, symbolic
  boundary, and collar.
- v5.7 evaluates a normalized one-mode cell.
- v5.9 supplies reduced collective dynamics.
- v5.10 supplies one finite homogeneous determinant diagnostic and explicitly
  lacks a full Lorentzian-to-Euclidean continuation.
- v5.11 is a partial second-variation ledger, not a parent action.
- v5.12 supplies symbolic boundary/collar terms and a candidate general-`d_B`
  top form whose normalization and source are absent.
- v6.0 supplies topology and a conditional pushforward theorem, not an action.

Setting `d_B=8`, moving `Sigma` terms onto `S7`, or treating the lower Berger
boundary as `S7` would be new assumptions rather than derivations.

## B8/S7 boundary and collar geometry

If a later branch selects `partial B8=S7`, the dimension-correct definitions
are

```text
h = i^*g_B8
g(n,n) = epsilon_n
K_AB = (1/2) L_n h_AB
S^A_B = h^AC K_CB
K = Tr_h S
X(Y,u) = exp_Y(u n)
J = sqrt(|det h_u|/|det h_0|).
```

Here `S` is a `7 x 7` shape operator. The abstract v5 collar determinant
identity is dimension-independent, but its evaluated three-dimensional Berger
metric, shape coefficients, and action cannot be reused as `S7` data.

For normalized `rho`, a physical normal coordinate would be
`u=ell_c rho`. The physical scale `ell_c` is absent. In a flat principal-frame
normal flow, `h_ii(u)=(1+u k_i)^2h_ii(0)` and
`J=product_i(1+u k_i)`. General ambient curvature requires the full normal
evolution equations.

## S7 metric candidates

The round family has

```text
g = L^2 g_round,unit
Vol(S7) = pi^4 L^7/3
R = 42/L^2
Ric = 6g/L^2
Isom = SO(8).
```

The quaternionic canonical variation uses four horizontal and three vertical
directions,
`g=L_H^2 g_H+L_Q^2 sum eta_i^2`, with volume
`pi^4 L_H^4 L_Q^3/3` in the standard 3-Sasakian convention. The round ratio is
Einstein; the conventional Jensen squashed ratio
`L_Q^2/L_H^2=1/5` is also an Einstein metric as mathematics, not as an
action-selected BHSM solution.

The complex Hopf variation
`g=L_C^2 p_C^*g_FS+L_1^2 eta^2` has volume
`pi^4 L_C^6 L_1/3`. A fully nested family needs independent `S4`, twistor
`S2`, and `S1` scales, with volume
`pi^4 L_4^4 L_2^2 L_1/3`. One Berger parameter cannot control all these scales
without an additional theorem.

There is no reduced parent action to vary, so first variations, a Hessian,
negative modes, and dynamical flat directions are not defined. The metric
parameters are conventional topological-family moduli, not stationary
solutions. Uniform rescaling changes volume by `lambda^7` and curvature by
`lambda^-2`; that covariance does not generate a scale.

## Measures and pushforwards

In the standard round-Hopf convention:

```text
Vol(S7)             = pi^4 L^7/3
Vol(S4, radius L/2) = pi^2 L^4/6
Vol(S3)             = 2 pi^2 L^3
Vol(CP3)            = pi^3 L^6/6
Area(S2, radius L/2)= pi L^2
Length(S1)          = 2 pi L.
```

These satisfy both Hopf and twistor factorizations. They are convention checks,
not physical measures. A selected action could require raw Riemannian measure,
scaled Haar measure, an action-weighted density, an invariant trace, or collar
warp/Jacobian factors. Normalized Haar probability is a different operation
and is not selected.

Scalar functions, differential forms, invariant gauge polynomials, and action
top forms can be fiber-integrated under the v6.0 hypotheses. Gauge connections
cannot be directly averaged as affine objects. Spinors, associated sections,
raw adjoint-valued curvatures, and stress tensors require a connection,
horizontal lift, holonomy or invariant-mode projection, representation pairing,
and frame/parallel transport.

## Physical boundary and Berger S3

`S7->S4` produces a Riemannian base in the stored geometry. A further
`CP3->3+1` map is absent. `M3,1 x S7 -> M3,1` is a coherent conditional
internal-space architecture but assumes rather than derives the Lorentzian
factor. No physical boundary map is closed.

The existing Berger `S3` can be a quaternionic Hopf fiber only after a vertical
metric and explicit embedding are selected. It can instead remain an
independent internal factor or a homogeneous truncation. No stored theorem
chooses among these roles. Correct `S3` coordinates, Hodge identities, measure
relations, and reduced-mode calculations are retained on their stated domains;
the interpretation of that `S3` as an `S7` boundary is invalidated.

## Scalar-localization readiness and next gate

Full v6.1 localization must not begin. The parent domain, signature, time,
physical measure, `S7` metric, collar embedding, bundle connection, locations
of `T` and `Phi`, and physical coefficient dimensions remain absent.

The narrow next branch is
`bhsm-b8-geometric-action-construction-v6-0-2`. Its first task is to construct
or source a dimensionally complete geometry–stress action, including its
variational boundary completion, so the energy-enclosure physicality criterion
and competing domain branches can be tested rather than chosen aesthetically.
