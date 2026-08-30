# N12 forward validated continuation cover

## Scope

This cover starts at the certified continuum child and propagates only the
existing forward child flow on the already gauge/time-quotiented admissible
manifold. It adds no selector, equation, physical gate, orientation choice,
parent section, or scale. The stored RK4 persistence path is not evidence in
the proof.

## Root-centered flow box

Let `B_r(Y_infinity)` be the existing action-coordinate neighborhood and let
`V_child` be the unchanged gauge-fixed Euler--Dirac vector field. The retained
action certificate supplies

    sup_B ||V_child||_G <= K_V,
    sup_B ||D V_child||_G <= K_J,

with the gauge-fixed Dirac inverse, eta, lapse, ordered eigenline, boundary,
and trace margins closed on the same neighborhood. Therefore the forward
solution cannot leave the ball before its action path length reaches `r`.
The existing inverse-square Galerkin tail obeys the already-derived Duhamel
bound

    e(t) <= exp(K_J t) e(0)
            + epsilon_ED (exp(K_J t)-1)/K_J.

Choosing a strict fraction of `r/K_V` and adding this tail error gives a
directed radius use strictly below `r`. This is an exact retained-map
enclosure, not a sampled trajectory.

The child ordered-event eigenvalue has the existing action-Lipschitz bound
`K_event`. Hence

    e_ord(t) >= e_ord(0) - K_event (path(t)+e(t)).

Its directed lower bound stays positive throughout the box. Eta, positive
lapse, the Dirac inverse, and the remaining existing domain margins also stay
strict. Thus neither a terminal event/reset hit nor a physical-domain exit
occurs on the certified interval.

## Regular chart overlap and matrix variational cover

The same-state overlap with `u=lambda^2` is certified before leaving the
original box. Subsequent boxes use the exact Euler--Dirac variational matrix
in raw action coordinates while retaining the regular `u` chart as an event
and domain monitor. A second-order center polynomial and a directed
logarithmic-norm remainder replace scalar action-norm wrapping. These boxes
are valid physical-flow enclosures, but they are not yet an interval enclosure
of the vector field pulled back to `(q,h,u)` coordinates. The retained flow,
physical state, domain, and event map are unchanged.

Seven overlapping boxes certify the forward interval

    0 <= t <= 8.026346778324657e-17,

an extension by `6.368221288063e12` over the original-coordinate box. On the
terminal certified box,

    e_ord >= 1.4307512234454108e-9,
    eta >= 0.9999880891417627,
    N_boundary >= 1.1294138121511845,

while the Dirac relative perturbation is at most `0.11529903237225454`, the
ordered eigenline gap is at least `3.487859876113841e-8`, and the continuum
tail forcing is at most `2.634972303216584e-68`.

The subsequent action-owned fixed-spectral Schur enclosure preserves the
soft/hard block identities instead of applying the smallest inverse to the
full forcing. On the `9.9e-10` physical-`u` overlap ball it certifies

    Schur denominator >= 1.4307512424232353e-9,
    ||r_hard|| <= 1.6713021281175368e5,
    ||V||_action <= 9.747072276456632e6,
    ||DV||_action <= 4.039149093315824e13.

The resulting recenterable box strictly extends the authoritative forward
interval to

    0 <= t <= 3.3902810011601674e-16.

No event or physical-domain exit occurs. At its proposal endpoint a new
same-action `9.9e-10` domain has independently closed with

    lambda_event >= 1.4307421780909107e-9,
    eta >= 0.999988208249346,
    boundary and Dirac domains closed,
    d u / d a >= 2.6860420484643547e-20,
    epsilon_ED <= 2.634972303216584e-68.

This supersedes the raw seven-box value only as the certified time frontier;
the earlier boxes remain valid provenance. The next finite-cover dependency
was to instantiate the same invariant identities at the new endpoint before
performing another enclosure.  That endpoint audit reproduced the unchanged
physical relation

    u_dot = 2 c_psi b_psi + 2 lambda_event R,

with `lambda_event = 1.4307439349306988e-9` and
`u_dot = 4.723744256824557e-14`.  On the strict `9.8e-10` subball of the
certified endpoint domain, it then closes

    sigma_soft(chart) >= 0.34761981491611965,
    Schur denominator >= 1.430742197040135e-9,
    ||V||_action <= 9.734368816831097e6,
    ||DV||_action <= 3.994460532765171e13.

The next recentered box therefore extends the authoritative interval to

    0 <= t <= 5.91213237665203e-16,

with endpoint tube at most `5.708390437944192e-10` and chart margin at least
`6.770527045720823e-11`.  It again has no terminal event/reset hit and no
physical-domain exit.  This is the same forward vector field and physical
event map in a recentered proof chart; no selector, equation, or gate has
changed.  The exact next dependency is to recertify the retained physical
domain at this endpoint before another overlapping box.

That recertification exposed an evaluator distinction before a third box was
accepted.  Binary cross-center eigensolver subtraction reported
`Delta lambda = -1.8256818709758094e-14`, whereas the exact retained-action
transport derivative and its certified Hessian remainder require

    Delta lambda in
    [-6.792248667214728e-17, 6.793058771199717e-17].

Reevaluating the same retained Hessian and the same selected simple branch
with the existing 80-digit action jet gives

    Delta lambda = 4.050538127609013e-21.

Thus the binary jump is numerical representation error and has no physical
transport authority.  The accurately evaluated target event minus its full
ball shift remains at least
`1.4307418064930009e-9`; the previously stored binary-domain lower bound
`1.4307239212553102e-9` is conservative.  Eta, Dirac, boundary, eigenline,
and continuum-tail gates all remain closed.  A second independently audited
step gives the same classification: its high-precision event change is
`3.943563116570196e-21` inside
`[-6.229426913134914e-17, 6.230215626708833e-17]`, while the binary difference
`2.1605551638252006e-14` is not physical motion.

At that third endpoint the independently rounded binary ball lower
`1.4307455268035592e-9` is slightly optimistic and is therefore not promoted.
Chaining the prior certified transport interval gives instead the authoritative

    lambda_event >= 1.4307418064935574e-9,
    d u / d a >= 2.686073124943402e-20.

These corrected bounds remain strictly positive.  The stored binary number is
retained only as provenance; it has no event-transport authority.

The third recentered overlap box extends the authoritative interval to

    0 <= t <= 8.327231167169652e-16,

with endpoint tube at most `5.878224213096761e-10` and chart margin at least
`6.517614252352391e-11`.  It has no event/reset hit and no physical-domain
exit.  Cross-center event monitoring from this point must use the invariant
action-Taylor transport (with high-precision same-action evaluation), not
subtraction of independently rounded binary eigenvalues.

## Exhaustion

The authorized seven-box raw-coordinate finite cover has exact Outcome C: no terminal
event/reset hit and no physical-domain exit. The first term limiting a further
effective raw-coordinate box is the full second-variation ball logarithmic
norm at action radius `1e-9`, not a retained-action obstruction.

The physical event coordinate is the ordered eigenvalue of the existing raw
reduced event Hessian. Its action-metric-congruent Euler--Dirac matrix has the
same zero boundary but a distinct nonzero eigenvalue coordinate. The earlier
provisional center chart conflated these values and therefore has no forward
proof authority. The raw boxes, physical event domain, and physical
`u=lambda_event^2` overlap remain certified. In raw reduced coordinates the
corrected same-state identity

    u_dot = 2 c_psi b_psi + 2 lambda_event R

is closed at the terminal center with
`lambda_event = 1.430752998333819e-9` and
`u_dot = 4.723772688930326e-14`. The retained event soft-amplitude chart
`(q,Q_event,0^T(z-z0),u)` is certified on the terminal `1e-9` action ball by

    lambda_event >= 1.4307512234454108e-9,
    |d lambda_event / d a| >= 9.366064201656395e-12,
    d u / d a >= 2.68010156280962e-20.

The initial full-gradient chart audit failed only because it replaced every
branchwise Kato denominator by the single smallest gap. Retaining the exact
termwise resolvent weights and bounding only their coupling remainder gives,
on the `1.5e-11` action ball containing the certified incoming
`1.1955557268695628e-11` endpoint tube,

    ||H(lambda_event)|| <= 0.44934538923360834,
    sigma_soft(chart) >= 0.9999961308026712,
    ||D chart^(-1)|| <= 1.0000077384245998.

Thus the physical `u` chart overlap and invertibility are certified. Extending
the cover now requires interval-enclosing the cancelled `u` rate, covariant
hard rate, pulled-back vector-field Jacobian, and nonlinear remainder on this
same chart ball.

The pole-free covariant decomposition now fixes the representation of that
next lemma.  On the ordered line and hard bundle,

    Q zdot = (Q D Q)^(-1) Q b,

and

    u_dot = 2 c_psi b_psi + 2 lambda_event R.

Only the hard inverse occurs.  The corresponding differentiated soft-source
identity also contains no inverse power of `lambda_event`.  A paired finite
difference of third-variation eigenvalue gradients failed to converge and is
therefore invalid as a center-matrix evaluation.  It is not an action
obstruction.

The required mixed fourth variation has instead been bounded directly from
the unchanged retained action:

    ||D4 L[psi_event,psi_event,V_child,·]|| <= 24.89295219839826.

Including the existing Kato eigenline term gives the certified center bounds

    ||D(u_dot)|| <= 7.129919867281734e-8,
    mu_action(DV_(hard,u)) <= 1.5841713491985116e9.

The latter is only about `1.009061954` times the raw action-coordinate center
logarithmic norm. Thus the earlier apparent `1e17` regularized growth is
invalidated as subtractive directional-D4 error. The mixed-action
contraction, Kato term, and physical-chart transversality are therefore
closed on the incoming terminal set. The exact remaining lemma is to enclose
only the pole-free vector-field matrix remainder and its recenterable endpoint
tube.

Intrinsic state selection therefore remains open. Gauge, scale, flavor,
neutrino, common-observable, blind-prediction, and release-integration gates
remain downstream and may not be promoted from this continuation result.

## First persistence chord: invariant Hermite reduction

Before another ambient enclosure, the first persistence chord was reduced to
the exact geometry owned by its cubic Hermite interpolant.  Put

    Delta = x1 - x0,
    d0 = T f(x0) - Delta,
    d1 = T f(x1) - Delta.

Then the unchanged cubic proposal satisfies the algebraic identity

    p(tau) - ((1-tau)x0 + tau x1)
      = tau(1-tau)((1-tau)d0 - tau d1).

Relative to the linear midpoint it therefore lies in the three-direction
action ellipsoid with projection

    P = (Delta/2, d0, -d1).

This containment is exact, not sampled: with `x=tau(1-tau)`, the squared
coefficient norm is

    (2 tau-1)^2 + tau^2(1-tau)^4 + tau^4(1-tau)^2
      = 1 - x(4-x+2x^2) <= 1.

The stored center replays this identity to `1.9337143078299663e-15` in
binary action coordinates.  The half-chord norm is
`0.006769530723135425`, while the two endpoint-consistency directions have
norms `8.326684516621527e-7` and `8.326639063863699e-7`.  Thus the prior
`1e-11` ambient transverse tube was not the correct enclosure for this
proposal, but no new physical direction is present.

The retained action was then reevaluated with the independently checked
80-digit local 13-variable jet assembly and Dirac solve.  The sampled Hermite
defect is smooth, has maximum `0.004340005934005917` at `tau=1/2`, and is
within `0.0014561467841591527` relative vector variation of the factorized
profile

    4 tau(1-tau) e_mid.

This factor profile is diagnostic until its remainder is interval enclosed.
It invalidates the jagged legacy binary profile as cancellation loss; it does
not by itself prove shadowing.

On the exact three-direction ellipsoid, direct retained-action majorants now
certify

    metric Euler--Dirac soft lower >= 1.427258034793824e-9,
    selected-to-hard gap >= 3.542701882199474e-8,
    hard zero gap >= 3.685821258181377e-8,
    eta >= 0.9999999996881591,
    boundary lapse >= 1.1294138124970994.

All 61 termwise spectral bootstraps close.  Congruence is used only to
exclude the existing physical event zero boundary; the nonzero metric Dirac
eigenvalue is not relabelled as the physical ordered-event coordinate.

The exact remaining lemma for this chord is now narrowly stated:

    interval-enclose the pole-free hard-plus-physical-u defect-factor
    remainder and the conjugated transverse variational propagator on the
    certified exact three-direction Hermite span.

This pole-free wording is forced by a further exact same-point identity, not
by a solver preference.  At the Hermite midpoint the raw defect has action
norm `0.004340005934005917`, including raw event-soft rate defect
`-0.003918115560080775`.  But the actual soft Euler--Dirac equation residual
is only `-5.606283370245828e-12`.  For the existing physical coordinate
`u=lambda_event^2`, the defect identity is

    delta u_dot
      = 2 c_psi (lambda_event delta s_soft)
        + 2 lambda_event delta R_hard.

No inverse event eigenvalue occurs.  Direct evaluation and the cancelled
formula agree at the same retained-action state, giving

    delta u_dot = 1.2990139949975814e-22,
    ||delta u_dot||_action-normalized = 2.5933275591811196e-8.

After retaining the configuration and event-hard complement, the complete
pole-free midpoint defect norm is `0.0018645553851845541`.  The raw soft rate
is therefore invalid as a physical obstruction or as the quantity to feed
to a whole-interval inverse bound.  The hard-plus-`u` remainder still needs
an interval enclosure and a shadowing argument before the chord has forward
proof authority.

The targeted 65-point same-state profile confirms that this is the right
interval object: the hard-plus-configuration defect is maximized at the
midpoint at `0.001864553828127277`, and after division by
`4 tau(1-tau)` its sampled relative range is only
`0.0005197096843873897`.  The corresponding soft event-equation residual is
at most `5.606107776143178e-12`.  These are measured profiles, not interval
bounds; they localize the remaining work to the factor remainder rather than
to another raw-rate solver or ambient-ball campaign.

Three already-owned exact-action Jacobi centers are also sufficient to avoid
a many-node derivative campaign.  Relative to the Hermite midpoint, the two
endpoint Jacobi matrices change by `195798.233808874` and
`195036.02914599` in operator norm against a center norm near `3.14e9`.
After conjugation by the midpoint fundamental matrix, their half-interval
products are only `0.000978973461053591` and
`0.000975197840974787`.  The symmetric three-center growth is
`31.42714599598494`, versus `31.42714408027551` for the midpoint matrix, a
ratio of `1.0000000609571593`.

The supporting second-Jacobi identity has therefore been written directly
on the covariant event-hard bundle and physical `u` coordinate.  Both its
first and second variations contain only the certified hard inverse and Kato
selected-to-hard gaps; neither contains an inverse soft eigenvalue.  The
exact Hermite span supplies, among the required retained-action inputs,

    D4[full,full,P,P] <= 2.501788116872369e-5,
    D5[full,full,P,P,V] <= 0.0398322621259115,
    D5[full,full,P,P,P] <= 1.9916131178167707e-10.

The generic reduced `D3` norm is intentionally not multiplied by the single
smallest hard gap: that would repeat the already-invalidated ambient norm
collapse.  The remaining interval assembly must retain the certified
termwise hard spectrum and source alignment while bounding the between-center
second-Jacobi remainder.  This is the sole missing constant before the
piecewise conjugated shadowing radius can be tested.

That source audit identifies a two-line retained event cluster as the correct
finite principal block.  The nearest event neighbor carries at least
`0.9987815572715458` of the nonselected rate norm, so treating it as generic
hard remainder was the last avoidable worst-gap loss.  Keeping branches
23--24 in the principal Jacobi evolution leaves a complement with certified
zero gap `9.885537843066749e-7` and inverse at most
`1011578.7486478069`, improving the remainder inverse by about `27.56`.
The whole-span raw-event cluster projector is certified with cluster-to-rest
gap `9.496888895429862e-7` and graph bound `0.15660032522215767`.

This is a proof decomposition only.  The ordered physical event remains
branch 23; branch 24 has not been promoted to a selector, state, equation, or
gate.  The exact remaining constant is now the cluster-complement plus
physical-`u` second-Jacobi majorant used in the piecewise conjugated shadowing
radius.

The cluster complement has additionally closed in the correct
center-preconditioned norm.  Its whole-span relative perturbation is at most
`0.12891336649872243`, so the Neumann factor is at most
`1.147991441540738` and the absolute complement inverse is at most
`1160624.2322921816`.  The exact Hermite coefficient derivatives give
preconditioned first, second, and third block-path bounds
`0.31094894715286564`, `0.8430238112166885`, and
`1.407032481952159`.  This closes the inverse/block half of the remaining
constant without a many-center derivative campaign.  The only unassembled
part is now the covariant complement source/Jacobi derivative plus the
physical-`u` second variation.

That covariant complement Jacobi has now been evaluated at the three owned
centers after explicitly subtracting Kato cluster-projector motion.  Its norm
stays near `1.8379e7`; endpoint-to-midpoint changes are below `661`, and its
centered second difference is `40.02274284466455`.  This is diagnostic rather
than interval authority, but it confirms that the preconditioned D5 remainder
is being applied to the correct smooth object.  The remaining proof step is
only its between-center interval enclosure combined with the already-derived
physical-`u` second variation.

Until that shadowing lemma closes, the Hermite curve remains proposal
geometry, the authoritative forward interval is unchanged, and intrinsic
state selection remains open.

## First persistence chord promotion

The pole-free shadowing lemma is now closed by the exact finite aligned
identity

    <Q_t(y(t)-y0),S(t)>
      = <Q_t(G(t)-A(t)y0),A_h(t)^(-1)S(t)>.

Here `S` is the invariant sum of the five signed Euler--Lagrange outputs.
The identity eliminates the artificial branch-24 eigenline enclosure and
closes all 64 subspans with maximum Green/local-radius ratio
`0.6446088519467095`. The Hermite proposal is therefore promoted to exact
shadowed forward flow on

    0 <= t <= 1e-8.

Eta, ordered-event, Dirac, boundary, nonzero-velocity, and continuum-tail
margins remain certified. No terminal/reset hit or physical-domain exit
occurs. This closes the first-chord proof dependency but not the maximal
forward-history dependency: Gate 7 remains open until an existing terminal
outcome or a summable global tail is certified.

The first-chord certificate is local and cannot be extrapolated over the
remaining stored proposal nodes. In the exact first-chord three-direction
coordinates, proposal node 2 already has coefficient norm
`3.461183499280721 > 1`, and node 10 has norm `243.61376037811283`.
Consequently chord 2 requires an unchanged action recenter and a fresh local
certificate; no later proposal chord has been promoted from the first-chord
constants.
