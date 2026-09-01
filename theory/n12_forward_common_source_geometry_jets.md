# N12 forward common-source geometry jets

Status: `LOCAL_COMMON_SOURCE_LOG_RADIUS_JETS_DERIVED`.

Write `x(tau)=log R4(tau)`. In the current retained forward source
representation, every spatial geometry coefficient is a homogeneous function
of `R4`. The rank-16 Dirac blocks and gauge/HS first-order source vertices
scale as `exp(-x)`, while scalar and de Rham Laplacians scale as `exp(-2x)`.
The seagull contact matrices are radius-independent. Therefore

\[
 D_x D_{sp}[h]=-hD_{sp},\qquad
 D_x^2D_{sp}[h,k]=hkD_{sp},
\]

and

\[
 D_x L_{sp}[h]=-2hL_{sp},\qquad
 D_x^2L_{sp}[h,k]=4hkL_{sp}.
\]

For the squared Weyl operator, the noncommuting product rule is retained in
full:

\[
 D_h(D^2)=D_hD\,D+D\,D_hD,
\]

\[
 D_{hk}(D^2)=D_{hk}D\,D+D_hD\,D_kD+D_kD\,D_hD+D\,D_{hk}D.
\]

The implementation supplies base, first, and mixed-second matrices for the
rank-16 Weyl/coexact-gauge and unit Einstein--Cartan HS blocks, the complex HS
doublet, and the non-Abelian one-form minus complex-ghost system. Independent
centered and mixed finite differences validate every operator, pair vertex,
and contact block below `1e-6`; first variations close below `1e-8`.

This removes the local `R4`-variation algebra from the Gate-7 blocker. It does
not choose a temporal graph, source profile, endpoint, or maximal history.
`D_tau` and `Delta_tau` remain supplied domain parameters, and no
maximal-forward tube for `log R4` or its first and second geometry variations
is yet owned. Hence the exterior Weyl bundle, zero-source force, and
same-action saddle remain open.

The next action-native object is a maximal-forward tube for
`(log R4,D_tau,Delta_tau)` and their required first/second geometry variations,
or a direct enclosure of the equivalent Weyl oracle bundle. Gate 7 remains
active, Gate 8 remains locked, and chord 3 remains unauthorized.
