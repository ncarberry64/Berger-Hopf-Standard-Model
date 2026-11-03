# v68: prescribed pair charge enclosure and covariant pole-flux domain

2026-11-03. This checkpoint constructs a conditional bound for the adopted
finite-pair charge moments and extends the saved central regular-pole
source-energy result to the covariant radial Gauss equation. It also applies
the new weighted source diagnostic to the actual saved v66 load. No physical
dressed density, entering-port flux or matched surface load is fabricated.

The main remaining obstacle is precise: the complete physical forcing must
be realized in the radial weighted source space, with compatible entering
and surface conormals on the event-generated trace graph. The finite-pair
normalization and regular-pole theorem do not establish those facts.

## Recovery: what already exists, what is new

The ideal preparation's pinned archive was absent as a worktree file but
present in the current Git tree. It was recovered read-only from commit
1ef75378916644c34229da5c24148b85d9fba868, path
`artifacts/muon_collider_common_state_constraint_family_20261014/retained_preparation/actual_frozen_family_and_exact_pair_spin_CAR_preparation.npz`.
Its SHA256 matches the adopted preparation exactly:
20db0b3b1a5cb09be1979b0fb24027bbb70f713d4001bd8c50e9807137a136d3.
This recovers existing pair data; it selects no occupations. The saved
receipt and all arrays are included in `evidence/`. No Downloads Git log
was accessed or retried.

The records reconcile as follows:

* The exact unpolarized pair and later 500 MeV/100 fm/+/-1000 fm Gaussian
  design are fixed. The later design supersedes the older receipt's open
  packet-design entry. Neither supplies already-realized dressed physical
  columns or an empty/quasifree inherited reference.
* v27 already proves the central cumulative-source formula and excludes
  homogeneous flux at a regular pole. That result is reused, not newly
  claimed here. v28 supplies the actual electric pole weights rho^6/rho^4.
* v62's coupled background/source/domain contract and v63's scalar trace
  pullback remain unfinished. The v64 author interpretation allows newly
  formed child-boundary points. A regular pointwise pullback is only a
  possible solved-event branch; no full-boundary bijection is presumed.
* v67 supplies the temporal insertion V_phi and its exact negative-projector
  structure under radial compact-gauge transport. Its numerical initializer
  and all physical limitations remain unchanged.

The new results below use these facts rather than redoing their campaigns.
Eleven local source records plus the exact Git archive are pinned.

## 1. Construct the actual finite-pair operator coefficient

The recovered four-mode occupation matrix is I4/2. The owned signed relative
one-body current coefficient, with positron normal ordering, is

    S=diag(1/2,1/2,-1/2,-1/2),  Tr S=0,  ||S||_1=2.

This is the exact bilinear coefficient of the already-adopted Fock16 pair.
It is not a replacement of its higher ordered products by Wick products.
The full exact pair density is preserved for those higher products.

On the *realized complete canonical Cauchy Hilbert space*, let the four
prescribed dressed columns form F:C4 -> H_C, F^dagger F=I4, including the
actual normal inclusion and density/frame isometry. Then

    Delta C_pair=F S F^dagger,
    ||Delta C_pair||_1=2,
    J_pair[chi]=Tr4(S F^dagger M_(chi V_phi) F).

The normal-pair form of this same insertion is v67's
Tr18[V_phi(C_ss+C_nn)]; both diagonal normal sections remain. The local
normal restriction is not by itself the complete Cauchy isometry F.

Since the exact transported V_phi is a negative projector, its norm is one.
For any bounded real scalar test chi in that common domain,

    |J_pair[chi]| <= 2 ||chi||_infinity.

This bound does not require the actual column values. It does require the
owned canonical normalization and a nonzero Higgs chart with unitary radial
gauge transport. No extra Maxwell kappa, V^-2 factor, spin average or family
multiplicity is appended. It uses the exact projector theorem, not the
slightly inexact floating U1 matrix as an exact projector.

In the original normalized-Haar scalar test basis, the addition kernels have
K_n(x,x)=(n+1)^2. For the retained n=1 and n=3 multiplets, sum_h Y_h(x)^2
is 4 and 16 respectively. Thus the Euclidean moment-vector enclosures are

    ||J_pair,n1||_2 <= 4,
    ||J_pair,n3||_2 <= 8,
    ||J_pair,n1+n3||_2 <= 2 sqrt(20) = 8.94427190999916.

These are conditional dimensionless bounds on the finite relative pair
block. They are not values of the physical charge moments, a physical
uncertainty, or bounds on the complete inherited/native/matched source.
Tr S=0 for the identity test does not imply vanishing weighted Q_H moments.

Independent analytic left sources are not reset to F^dagger. The above is a
base physical-density bound. On a fixed common Hilbert realization its
tangent contains F_Y^dagger M F+F^dagger M_Y F+F^dagger M F_Y, in addition
to any owned domain/isometry contacts. A conditional estimate involves
2(2||M|| ||F_Y||+||M_Y||), so the unevaluated physical response F_Y is not
bounded by the base CAR identity alone. Higher responses retain the exact
pair state and all ordered placements; no quasifree closure is made.

## 2. Covariant radial flux: the genuine pole is not an entering port

Write the complete canonical Gauss equation on a regular material patch as

    D_rho P=-F_total,
    D_rho=partial_rho+ad(A_rho),
    F_total=D_i Pi^i+rho_complete,
    rho_complete=rho_pair+rho_native/relative+other owned bulk terms.

Sources and moving-domain/contact variations use their corresponding full
linearized equation. Angular derivatives, including all higher harmonics,
remain in F_total; this formula asserts no angular closure.

On the real compact gauge domain, ad(A_rho) is skew and its radial transport
is an isometry. For an integrable connection, the transported flux has a
limit at a regular pole whenever F_total is integrable there. The original
radial electric energy has k~kappa rho^6. A nonzero limiting flux would give
integral |P|^2/k ~ integral rho^-6, which diverges. Consequently its homogeneous
pole flux is zero on the owned regular finite-energy domain.

This does not mean that the initial electric field or an entering flux is
zero. At a physical inner face rho=a>0, the affine solution is

    P(rho)=U(rho,a)P(a)-integral_a^rho U(rho,s) F_total(s) ds.

P(a) is the inherited canonical trace. It cannot be eliminated by a theorem
about rho=0. At an interior edge with an actual delta source q_edge,
P(rho_edge+)-P(rho_edge-)=-q_edge, in compatible oriented traces. No released
edge source is assigned zero, nor is a weak conormal split with a sharp mask.

## 3. New weighted return and photon-flux bounds

For a genuine regular pole assume the complete source lies in
L2(rho^-4 d rho dHaar), and k>=kappa_minus rho^6 with kappa_minus>0 on the
patch. Let

    I=integral rho^-6 ||P||^2,
    J=integral rho^-4 ||F_total||^2,
    B=[rho^-5 ||P||^2]_0^R.

Skewness removes the connection from Re<P,D_rho P>. Exact integration by
parts gives the completed-square identity

    J = integral rho^-4 ||F_total+(5/2)P/rho||^2
        +(25/4) I +(5/2) B.

The regular-pole lower term is zero. In fact the weighted source condition
implies ||P(rho)||^2/rho^5 <= (1/5) integral_0^rho s^-4||F_total||^2 ->0.
The outer term is nonnegative. Hence

    I <= (4/25) J,
    integral ||P||^2/k <= 4/(25 kappa_minus) J.

The physical radial electric energy includes an additional factor 1/2.
The displayed norm bound uses the complete canonical coefficient k, with
the original action normalization once. This extends the earlier central
formula to arbitrary angularly dependent compact radial gauge transport;
it does not prove the full coupled scalar/interface problem is coercive.

Cauchy-Schwarz also gives

    ||P(R)||_L2(Omega) <= R^(5/2)/sqrt(5) sqrt(J).

For the twenty complete-domain photon moments Q_h(R)=<Y_h phi(R),P(R)>,
Bessel's inequality and ||s_H||^2=16/3 give

    ||Q_20(R)||_2 <= sqrt(16/3) R^(5/2)/sqrt(5) sqrt(J).

At an entering face a>0 add its actual transported flux norm and replace
R^5 by R^5-a^5 in the bulk estimate. Actual interior edge loads add their
corresponding transported terms. For partial-envelope weak conormals the
actual common trace/dual norm and bounded test lifts are needed instead;
no L2 surface density or complete-sphere bound is silently assigned to them.

The projected boundary equation is still

    -Q_wall + <Y_h s_H,rho_Gamma,rest+retained/released ports>=0,

after the proven classical Higgs-range identity. Thus the bound above can
control that compatibility row only after the complete J and the actual
graph/port contributions are supplied. It does not determine their values.

## 4. Application to saved data, without a new physical source

The v66 direct-velocity coefficient is K=kappa e B_p G, with e=O(rho^4),
B_p=rho^alpha times its fixed polynomial, alpha=(sqrt(45)-3)/2, and bounded
G on the owned regular gauge chart. Therefore

    K=O(rho^(4+alpha)),
    P_known=O(rho^(5+alpha)),
    rho^-4 ||K||^2=O(rho^(4+2alpha)).

The last exponent is about 7.7082, above -1. Thus this already-known forcing
component belongs to the new sufficient weighted source class on that
regular coefficient chart. This is not a statement about its unevaluated
native or interface remainder.

The existing 48-node quadrature is used once to compute J_known for its
four radial profiles and eight sources. The largest diagnostic is
67.69001016295357. The corresponding (4/25) times diagnostic is saved.
These are fixed-rule values, not certified continuum integrals. Neither
a physical kappa_minus nor a complete physical energy/error bound is
reported from them. No radial basis, resolution, field or packet changed.

## 5. Exact remaining obstruction and smallest useful continuation

The bound reduces a real domain obligation but does not construct the common
physical slice. Three distinct pieces must not be conflated:

1. **Known preparation coefficient:** S and the external Gaussian are fixed.
   Their physical image F=Omega_minus J U_as P_as G g_as still needs the
   same-background comparison, normalized D5 inclusion, inherited domain
   and its actual source jets. No bare Gaussian density is substituted.
2. **Unrealized complete forcing:** finite-pair normalization controls
   bounded smeared bilinears. It does not establish the weighted L2(rho^-4)
   norm of the complete local Gauss source. Native/relative bulk terms,
   induced background and independent source legs still require their
   common causal-domain application and single overlap subtraction.
3. **Unrealized event trace:** a genuine regular pole has no free homogeneous
   flux, but the physical entering face and retained/released conormal
   live on the solved envelope/reformation graph. The action's local
   matching equations and author least-action interpretation do not supply
   its numerical trace map, bounded lifts or edge load before that solve.

The available records therefore do not yet supply a closed numerical
source/domain instance to evaluate these three physical contractions.
This is an uncompleted coupled mathematical construction, not proof of a
missing author selection rule, inconsistency or full observable state
dependence. The previous complete-observable closure obligation still
prevents inferring dependence from an isolated source term or choosing rho.

The next substantive calculation must realize the actual incoming Cauchy
isometry/source application and event trace for the reduced charge row,
then test the complete weighted residual and port matching. Recomputing
the local charge projector, known radial kernel, CAR statistics or their
derivatives cannot supply that instance. A broad coupled background solve
is not launched: its complete source/domain residual is not yet evaluable.
No new packet, occupation, flux, boundary-point correspondence or physical
selection law is chosen or requested.

## Verification and retained limits

Six focused tests cover the recovered signed pair, harmonic bound, exact
weighted identity, owned pole powers, independent contraction of the new
weighted diagnostic and null physical results. Nine rational identities
are checked exactly. Six numerical consistency checks have maximum defect
4.263256414560601e-14, below the unchanged 2e-11 method tolerance.

Final run_2/run_3 are deterministic and the portable extraction replays
them; receipts record verification. run_1 is preserved with the note adding
the wall-flux bound. The bounded C:\Python314\python.exe -I -S invocation
uses only the previously inspected package roots and guarded owned source.
No uninspected custom startup/import paths or extra worker were used.

The physical guard remains 2e-10 and temporal baseline remains t=2^-9;
neither is a full physical state. Reconnection, the complete residual,
physical a_mu/g_mu and total uncertainty remain uncomputed. Nothing is
committed or pushed by this stage.
