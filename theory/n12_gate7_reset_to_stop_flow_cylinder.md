# N=12 Gate-7 reset-to-stop flow-cylinder theorem

Status: `EXACT_EXISTENCE_ONLY_FLOW_CYLINDER_REDUCTION_DERIVED; FINITE_INTERVAL_WITNESS_OPEN`.

## Retained objects

Let `M_C2` be the regular gauge/time-quotiented constrained-child manifold.
The reset-generated launch theorem gives `dim M_C2=73` and a local chart

`L(xi,s)=Flow_s(E(xi))`,  `xi in R^72`, `s>0`.

Here `s` is the retained selected descriptor, not a new time or a fitted
amplitude.  Let `V` be the denominator-free forward action-arclength field
and let

`Sigma_ED={y in M_C2 : s(y)=0, Delta(y)<0}`

with every other retained regular-domain margin strict.  Along the exact
field,

`D s[V]=Delta/||G||`.

Consequently `D s[V]` is nonzero on `Sigma_ED`.  The regular-value theorem
makes `Sigma_ED` a 72-dimensional face of `M_C2`, transverse to `V`.

## Proof-only reverse cylinder

For any local stop-face chart `iota:Z subset R^72 -> Sigma_ED`, define

`C(z,a)=Phi_{-a}(iota(z))`,  `a>=0`,

where `Phi` is the same retained flow.  Backward evaluation here is only the
inverse of the local forward-flow diffeomorphism used in a proof.  It is not
a second physical time orientation or a reflected physical history.

At `a=0`,

`D C=[D iota,-V]`.

The first 72 columns lie in `ker D s`, while `D s[-V]` is nonzero.  Hence
`D C` has rank 73 and the inverse-function theorem makes `C` a local
73-dimensional flow cylinder.  A launch state in the image of this cylinder
has, by uniqueness, a forward history reaching the retained Euler--Dirac
stop in finite positive action length.

## Exact existence-only reduction

Gate 7 does not require every point of the 73-dimensional launch family to
reach this stop.  The physical ontology requires at least one certified
forward complete-child history to reach a finite encapsulation endpoint or
an already retained canonical stop.  Therefore any one of the following is
sufficient:

1. strict interval inclusion of a nonempty validated launch set in the
   reverse stop cylinder;
2. a square coordinate matching map with boundary exclusion and nonzero
   degree; or
3. a validated single witness orbit from the reset relation, together with
   a scalar interval-Newton first hit of `s=0` and strict earlier domain
   margins.

The third alternative is the minimal theorem for the present numerical
route.  Fixing proof coordinates to isolate one witness does not add a
physical selector: no action, observable, or later member-selection rule is
defined from those coordinates.  It proves the existential statement and
nothing universal about the remaining reset family.

For a finite multiple-shooting mesh in intrinsic 73-state coordinates, use
the already-derived Green/Hermite or sheared-Lohner local flow residuals.
The last block adds the scalar equation `s(y_N)=0`; its interval Jacobian
contains the nonzero time column `D s[V]`.  The reset/root block supplies the
initial exact member, all seams use the same forward field, and the stop
block uses the existing Euler--Dirac rank-loss surface.  An inverse-free
bordered Krawczyk or interval Newton enclosure of this one finite system
therefore proves the required history without a full kinetic/Dirac inverse.

## Current numerical center and claim boundary

The refined center reaches `s=0` at action length
`92.3033209053828` after the certified 1222-segment core.  At that center,

- `Delta=-6.965831811826919e-15`;
- `D s[V]=-2.8365049372603952e-11`;
- the selected-line gap is `1.7341678902683903e-7`;
- boundary lapse is `0.7057304510598463`;
- boundary radius is `0.9949297505914222`.

These center values establish a well-conditioned transverse target and
preserve the sampled physical domain.  They do not enclose the path between
the certified core and the target.  The exact remaining object is one finite
correlated multiple-shooting/flow-cylinder enclosure with boundary exclusion
for every earlier canonical stopping locus.  After that certificate, the
finite-endpoint operator theorem may replace the former maximal-tail
obligation, and Gate 7 proceeds to the already-derived complete closed-system
heat-minus-zeta force, KKT root, and constrained physical Hessian.

No selector, recurrence, new endpoint, chord, action term, scale, phase,
coupling, or physical time direction is introduced.
