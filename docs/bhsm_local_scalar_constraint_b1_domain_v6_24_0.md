# BHSM v6.24.0 local scalar constraint and moving-B1-domain audit

## Result

The frozen action does not select a physical \(x\)-dependent B1 endpoint
domain. It contains a fixed embedding \(\iota\), and its declared variation
acts on the bulk metric, independent intrinsic B1 metric, matcher multiplier,
and scalar fields—not on \(\iota\). In the doubled geometry, replacing the
fixed reflection center by \(\rho=\rho_J+\zeta(x)\) also requires an
\(x\)-dependent cap-exchange/reflection extension. The inherited domain does
not store that datum.

The earliest-stop verdicts are therefore

```text
BHSM_LOCAL_SCALAR_CONSTRAINT_SYSTEM_BLOCKED_BY_UNSTORED_X_DEPENDENT_EMBEDDING_DOMAIN
BHSM_B1_MOVING_ENDPOINT_DOMAIN_BLOCKED_BY_UNSTORED_X_DEPENDENT_GLUE_REFLECTION_DATUM
BHSM_FOLD_COMPLETE_LOCAL_MIXED_SOURCE_BLOCKED_BY_UNSTORED_X_DEPENDENT_EMBEDDING_DOMAIN
BHSM_FOLD_SCHUR_REDUCTION_BLOCKED_BY_UNSTORED_X_DEPENDENT_EMBEDDING_DOMAIN
BHSM_FOLD_KINETIC_SIGN_REMAINS_UNRESOLVED_BY_UNSTORED_X_DEPENDENT_EMBEDDING_DOMAIN
```

No missing operator or source component is set to zero. No endpoint equation,
boundary matrix, inverse, Schur number, or kinetic sign is emitted.

## Frozen action and critical background

The retained action is

\[
 S_{\rm tot}
 =S_{{\rm P1},+}+S_{{\rm P1},-}
 +S_{{\rm GHY},+}+S_{{\rm GHY},-}
 +S_{\rm B1}+S_{\rm match}+S_\sigma .
\]

The cap action and GHY completion are

\[
S_{\rm P1}
=\int\sqrt{-g}\left[
{\kappa_1\over2}R_5-{\kappa_0\over2}
-{Z_5\over2}(\nabla\sigma)^2-U_5(\sigma)\right],
\qquad
S_{\rm GHY}=\kappa_1\int_{\partial M}\sqrt{-h}\,K ,
\]

with \(U_5=A_5\sigma^2/2+G_5\sigma^4/4\). There are two capwise
GHY terms. The one common intrinsic B1 action in the primary freeze is

\[
S_{\rm B1}=\int_{\rm B1}\sqrt{-h}\left[
C_\partial R_4-{\tau_A\over4}{\rm Tr}(F^2)
-{Z_\partial\over2}(\partial\sigma_\partial)^2\right].
\]

\(U_\partial\) is absent in the primary freeze. The exact matcher is

\[
S_{\rm match}=\int_{\rm B1}\sqrt{-h}\,
\Lambda^{ab}\bigl(h_{ab}-\iota^*g_{ab}\bigr).
\]

There is no tunable matcher coefficient, hidden matcher stress, or
propagating multiplier mode.

The normalized critical cap is

\[
a_0(t)=\sqrt2\sin{\pi t\over4},\qquad N_0={\pi\over4},
\qquad 0\leq t\leq1,\qquad \sigma_0=0,\qquad X_c=2.
\]

The pole is at \(t=0\), B1 at \(t=1\), and
\(K_{ab}=\tfrac12{\cal L}_n\gamma_{ab}\). The scalar-wall reference uses
\({\rm Ric}(\bar h)=3X_c\bar h\), rather than the distinct static
\(\mathbb R\times S^3\) diagnostic branch.

## Moving-graph geometry

Let \(p_{AB}=\delta g_{AB}\), and displace the hypersurface by
\(\zeta n+v^ae_a\). With \(n^2=1\) and the preceding convention for \(K\),
the induced metric varies as

\[
\delta\gamma_{ab}
=p_{ab}+2\zeta K_{ab}+2D_{(a}v_{b)}.
\]

The unit normal variations are

\[
\delta n_A={p_{nn}\over2}n_A-(D_a\zeta)e^a_A,
\qquad
\delta n^A=-{p_{nn}\over2}n^A-(p_n{}^a+D^a\zeta)e_a^A .
\]

The pure shape parts of the extrinsic-curvature variations are

\[
\delta_\zeta K_{ab}
=-D_aD_b\zeta
+\zeta\bigl(K_a{}^cK_{cb}-R_{nanb}\bigr),
\]

\[
\delta_\zeta K
=-D^2\zeta-\bigl(K_{ab}K^{ab}+{\rm Ric}_{nn}\bigr)\zeta .
\]

The measure and scalar pullback obey

\[
{\delta\sqrt{|\gamma|}\over\sqrt{|\gamma|}}
={1\over2}p^a{}_a+K\zeta+D_av^a ,
\]

\[
\delta\sigma_{\rm ind}
=\delta\sigma+\zeta\,n(\sigma_0)+v^aD_a\sigma_0.
\]

At the critical background, \(\sigma_0=0\), hence
\(\delta\sigma_{\rm ind}=\delta\sigma\). The retained connection background
also vanishes, so its moving-pullback term vanishes at first order.

In radial ADM variables the graph has relative shift
\(V_\mu=N_\mu+N^2D_\mu\zeta\), and the stored scalar invariant is

\[
\mathcal S_\Sigma
=B+N_0^2\zeta-a_0^2\partial_\rho E .
\]

For the repository convention
\(\delta g\mapsto\delta g-{\cal L}_\xi g\),

\[
B\mapsto B-N_0^2\xi^\rho-a_0^2\partial_\rho L,\quad
\zeta\mapsto\zeta+\xi^\rho|_\Sigma,\quad
E\mapsto E-L ,
\]

so \(\mathcal S_\Sigma\) is invariant.

This proves fixed-endpoint and moving-coordinate descriptions of one fixed
support are equivalent. It does not prove that changing the embedded
submanifold is gauge. A physical displacement changes the action domain and,
for the double cap, the reflection/gluing map.

## Why the endpoint equation cannot be varied

The matcher includes the symbol \(\iota\), but the frozen local variational
configuration space does not include \(\iota(x)\) as a field. The earlier
one-dimensional reduced cap problem does vary its homogeneous upper limit
along the solved cap family and obtains transversality/shape response. That
restricted variation supports the stored homogeneous relation
\(\delta a'_J=\delta X/2\); it does not declare arbitrary
\(\iota_\zeta(x)\). In particular, it supplies none of the
\(D_\mu\zeta\), \(D_\mu q\), or \(D_\mu D_\nu q\) terms needed for a local
extension.

The v6.13 domain ledger explicitly records

```text
embedding_varied = false
x_dependent_embedding_variation = false
```

and the v6.15 double-cap ledger classifies an \(x\)-dependent reflection
center as additional orbifold/gluing data. Consequently
\(\delta S/\delta\zeta\) is not an Euler–Lagrange derivative of the frozen
theory. Computing a formal shape derivative after silently enlarging the
configuration space would choose a new free-boundary problem.

For a coordinate displacement of the fixed support, diffeomorphism
invariance relates the pullback variation to the bulk equations and the
tangential Ward identities. This coordinate identity supplies no independent
normal endpoint law. Conversely, a genuine physical shape variation requires
the missing declaration of which embeddings are allowed, how both cap
domains and their reflection extension vary, and whether any corner data are
needed.

The smallest missing object is therefore:

> An off-shell family \(\iota_\zeta\), together with its Z2
> cap-exchange/reflection extension, declared as part of the variational
> domain.

## Operator and threading consequences

The inherited fixed-domain checks remain valid:

\[
L_{A\psi}^{\rm crit}
={6\kappa_1\over a_0^2}
\begin{pmatrix}0&1\\1&2\end{pmatrix},
\qquad
d\mu_{\rm rad}=N_0a_0^4dt
=\pi\sin^4{\pi t\over4}\,dt .
\]

GHY cancels normal derivatives of \(\delta g\) cap by cap for the stored
fixed-embedding variation, matcher elimination gives
\(h_{ab}=\iota^*g_{ab}\), and the tensor junction remains

\[
\kappa_1[Q_{ab}]+2C_\partial G^{(4)}_{ab}=T_{\partial,ab}.
\]

These facts are insufficient to declare the missing moving-endpoint blocks.
In particular, the complete lower-order radial Hessian, scalar B1
projections, endpoint dependency matrix, boundary matrix, formal adjoint,
kernel, and compatibility condition are not derived.

The v6.18 threading theorem covers the round-\(S^3\), spatially
nonhomogeneous modes:

\[
\Pi_\perp\bar{\mathcal S}_\Sigma
=-\tau{\pi\chi_1\over16}\Pi_\perp q ,
\]

and adopts \(C_\Sigma=0\) for the time-independent homogeneous kernel. Its
displayed kernel is spatial. It does not cover a time-dependent,
spatially-homogeneous Lorentzian M4 response, the general Lorentzian scalar
sector, or the physical moving-endpoint trace. The projected spatial inverse
therefore cannot stand in for the complete local threading block.

## Source, adjoint, and Schur status

The bookkeeping choice is to treat the homogeneous radial profiles as affine
shifts of the constraint variables, not also as direct source terms. The
identity

\[
K'-\langle J',L^{-1}J'\rangle
=K-\langle J,L^{-1}J\rangle
\]

is verified algebraically, with the same operator and domain on both sides.
Its use is blocked because that operator and domain do not close.

The established statements

\[
K_{\rm scalar}=2\int a_0^2u_1^2\,d\rho\ge2,\qquad
K_{\rm Weyl}={3\chi_1^2(4-\pi)^2\over16\pi}
\]

are preserved but not combined. The moving-endpoint, matcher, complete
intrinsic-curvature, time-dependent threading, scalar-orthogonal, and
lower-order metric source components remain undefined.

There is consequently no final \(Y_{\rm phys}\), operator pencil
\(L_0+\lambda L_1\), adjoint domain, kernel count, inverse, Schur complement,
or kinetic-sign result.

## Integrity

This audit introduces no measured input, fitted coefficient, primitive,
scale, action term, corner term, boundary parameter, global Green state,
local \(X_{\rm FRW}(x)\) field, scalar-curvature inverse, conformal action
ansatz, chat-only numerical candidate, physical mass, or stability claim.
Frozen predictions and official prediction logic are unchanged.

The next construction target is to declare or derive the off-shell
\(x\)-dependent B1 embedding and Z2 reflection/gluing variational domain,
then derive its endpoint equation before reopening the full quadratic
operator.
