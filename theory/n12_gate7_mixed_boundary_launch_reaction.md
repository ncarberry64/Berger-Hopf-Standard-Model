# Gate-7 mixed boundary/launch reaction derivative

Base: `d0586b6067e89f8a347cc8998832dc636b6ee80b`.

The target is the derivative of seven physical boundary reactions, not seven
copies of the scalar action gradient. The exact remaining object is

`CURRENT_CENTER_HEAT_ZETA_MIXED_BOUNDARY_LAUNCH_JET_7x73`.

Its directional contraction formulas and an outward implementation are now
derived. Its **current physical numerical matrix remains unmaterialized**.
The current 1,222-cell prefix and its stored arrays are consumed unchanged.
No generic second operator tensor, history integration, historical action
producer, or full continuum heat calculation is performed.

## What the internal solve does and does not eliminate

Let `n=Phi(b,p)` solve `F(b,p,n)=0`, and let `K=F_n`. If the objective
`Gamma` itself is stationary in `n`, with `F=Gamma_n` or an established
bordered equivalent, the envelope theorem gives

```
Lambda_b = Gamma_b,
Phi_p = -K^-1 F_p,
H_red,bp = Gamma_bp - Gamma_bn K^-1 F_p.
K^T lambda = Gamma_bn^T,
H_red,bp = Gamma_bp - lambda^T F_p.
```

This removes explicit mixed derivatives of `Phi`. It does **not** remove
the mixed derivative already present in `Gamma_bp`.

The requested history-only sector need not be stationary separately from
the local action. For that case the stationary shortcut is unjustified.
Use the scalar objective adjoint and Lagrange function at the common base:

```
K^T eta = Gamma_history,n^T,
L = Gamma_history - eta^T F,       (eta fixed in L_uv),
Phi_b = -K^-1 F_b,
H_red,bp = L_bp + L_bn Phi_p + Phi_b^T L_np
                        + Phi_b^T L_nn Phi_p.
```

An equivalent implementation requires seven boundary solves and seven
adjoint solves, rather than 73 forward normal histories:

```
K^T lambda = (L_bn + Phi_b^T L_nn)^T,
H_red,bp = L_bp + Phi_b^T L_np - lambda^T F_p.
```

Here `L_uv=Gamma_history,uv-eta^T F_uv`: contracted mixed residual terms
are still required. The full joint internal block must be supplied; the
frozen local 125-dimensional shooting border is not substituted for it.
No inverse matrix is explicitly formed.

## The heat law retains a genuine mixed operator contraction

For the retained fixed heat length,

```
Gamma_heat(P) = -Tr E1(ell^2 P)/2,
Q(P) = exp(-ell^2 P)/(2P),
Gamma_heat,bp = Re Tr(DQ(P)[P_p] P_b)
             + Re Tr(Q(P) P_bp).
```

The first term is computable from the operator value and the two sets of
first jets. In an owned orthonormal spectral frame it is

`sum_kl q[lambda_k,lambda_l] (P_p)_kl (P_b)_lk`.

The adapter handles coincident eigenvalues without dividing by a spectral
gap. It accumulates the seven-by-73 contractions directly. Its real-frame
inputs are conditional on a certified common frame supplied by the caller;
it does not certify a floating eigensolve or fabricate current operator data.
For general complex Hermitian blocks the displayed real-trace formula is
the owner; a matching complex or realified frame is still required.

The second term is not determined by those first jets. This is true even
with an exactly solved stationary internal variable. The algebraic example

```
P_c(b,p)=2+b+p+c*b*p,
Gamma_c=f(P_c)+n^2/2, F=Gamma_c,n=n
```

has identical base operator, boundary/launch first jets, internal inverse,
and constant seeds for `c=0,1`, but its mixed reaction differs by
`q(2)=exp(-2)/4 > 0`. Both operators are positive on `|b|,|p|<=1/4`.
This is an input-sufficiency test, **not BHSM numerical data**.

The current action law supplies no general identity discarding this term.
Its existing `aether_forward_common_source_incidence` routines explicitly
retain nonzero mixed log-radius vertices. Those routines hold the supplied
temporal graph and source profile fixed; they do not supply the additional
moving-duration, material-seed, or implicit-history incidence automatically.
An action-specific cancellation after complete signed composition remains
possible, but is not assumed from first jets or stationarity alone.

## Derive only the needed form contractions

For the existing AE2 element, write midpoint log radius as `x`, duration as
`h`, `S=[[1,-1],[-1,1]]`, `A=[[2,1],[1,2]]`, `C=diag(-1,1)`. The law is

```
K = S/h + h V A/6 + W C,   M = h A/6,
V=c exp(-2x)                         (scalar),
W=chi*mu exp(-x), V=W^2              (product Dirac).
```

For one physical boundary direction `b` and one launch direction `p`,

```
V_bp = V (4 x_b x_p - 2 x_bp),
W_bp = W (x_b x_p - x_bp),
K_bp = S (2 h_b h_p/h^3 - h_bp/h^2)
     + A/6 (h V_bp + h_b V_p + h_p V_b + V h_bp)
     + C W_bp,
M_bp = A h_bp/6.
```

The implementation computes one such 2x2 pair at a time. It does not
allocate a full second operator jet. Crucially, `x_bp` and `h_bp` are
required arguments, not default zeros. Form jets must subsequently enter
the generalized pencil and moving measure correctly; `K` alone is not the
heat operator. Contacts and reset-frame derivatives enter once in that
same assembly. The missing heat input can be stored as only the streamed
scalars `Re Tr(Q P_ba,pj)`, not a tensor of full mixed matrices.

The corresponding exact linear-element zeta mixed term is

```
Gamma_zeta,bp = -(59/30) integral_0^1 exp(-x(u)) *
 [ h (x_b(u)x_p(u)-x_bp(u)) - h_b x_p(u) - h_p x_b(u) + h_bp ] du.
```

Its polynomial/exponential moments are evaluated outwardly, including the
coincident-radius limit. These formulas retain signed radius/duration cross
terms. A raw duration norm cannot replace any of them.

The packet also saves the current unit-mode coefficient-coordinate
partials `V_xx=4V` and `W_xx=W` and their partial launch rows. They are
nonzero current coefficients; they are **not** substitutions for the seven
physical boundary seeds.

## Moving seeds and the sign convention

For `Lambda_a=DGamma_red[B_a]`, ordinary differentiation is

`D_P Lambda_a = H_red[P,B_a] + DGamma_red[D_P B_a]`.

Subtracting the seed-motion term from this **iterated derivative** produces
the connection-corrected fixed-seed Hessian. If `D2 Gamma[P,B]` instead
denotes the bilinear Hessian already, subtracting that term defines a
different quantity. Both signs are explicit in the adapter; the full
physical material-connection convention must be bound before promotion.
The existing `moving_port_jet` also uses the ordinary plus product rule.

The AE2 bundle theorem `nabla U_R=0` removes an **independent frame source**.
It retains the physical transported child variation. It does not prove that
all seven material seed vectors have zero geometric derivative. Accordingly,
only the independent frame contribution is saved as exactly zero; the
complete reset contribution remains null/uncomputed.

## Retained contact accounting

| Owner | Classification | Accounting |
|---|---|---|
| Independent reset-frame source | ZERO | Transport included in covariant child jets |
| Independent fermion delta-supported `W_phys` | ZERO | AE2 owns `S_Sigma_F=0` |
| Transverse gauge Wentzell | ACTIVE | `K_F c_group sqrt(Delta1)`; keep radius/form derivatives |
| Scalar/topographic local response | ACTIVE | Retain nonaffine scalar potential and source incidence |
| Pair and mixed/contact terms | ALREADY_INCLUDED | The two heat derivative terms above, once |
| Constraint/descriptor/history response | INTERNAL_REACTION | Full common objective adjoint; no sector zeroed |

No separate scalar delta action is inferred merely from the name
`scalar/topographic contact`. No positive contact is declared a transition.

## Numerical materialization still required

The stored 73 launch first jets do not contain seven material boundary seeds
and their derivatives, the current formation/reset pullback, or the mixed
`x_bj,h_bj` incidences. The complete joint operator and full internal
objective-adjoint blocks also remain uninstantiated. These are inputs to
the derived object, not new environment laws. The 72 seed-image dimensions
do not independently specify the upstream 67-dimensional reset kernel.

Consequently no numerical `R_history_7x73`, full reset matrix, row norms,
cancellation factor or completed rank is reported. No arbitrary test
covectors enter physical outputs. The exact first numerical target remains
the named mixed boundary/launch object above, assembled with its true seven
material seeds and contracted internal response.

Producer: `scripts/derive_n12_gate7_mixed_boundary_launch_contract.py`.
Implementation: `src/bhsm/interface/heat_zeta_mixed_boundary_launch.py`.
Packet: `artifacts/flagship_integration/gate7_mixed_boundary_launch_20260927/`.
The report gives source-function lines and hashes. Focused tests check the
noncommuting heat derivative, coincident spectrum, mixed scalar/Dirac form
jets, moving-duration zeta, general objective adjoint and both seed signs.

Validation: **77 focused tests pass**, including the 66 current-center
checkpoint tests. Two independent derivation runs produce byte-identical
arrays and reports. The original prefix is unchanged.

`Gate7_closed=False`; `FULL_BHSM_COMPLETE=False`.
