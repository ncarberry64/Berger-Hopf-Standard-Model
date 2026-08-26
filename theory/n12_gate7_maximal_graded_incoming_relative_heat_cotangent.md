# Gate-7 maximal graded incoming relative heat cotangent

Status: `MAXIMAL_GRADED_INCOMING_RELATIVE_HEAT_COTANGENT_SUMMABLE`.

The fixed-channel Krein theorem leaves one possible obstruction: summing its
rank-one relative heat cotangents over the retained angular ledger.  For the
incoming-amplitude direction this sum is controlled by the certified C2
collar adjacent to the E1/C2 seam and does not require any assumption on the
unknown far tail.

Let `ell_0>0` be the certified proper duration of the first C2 element and let
`x=log R4` on that collar.  Put

`a=exp(-2 x_max)`, `b=exp(-x_min)||D_tau x||_infinity`.

For either product-Dirac chirality the exact factorized form gives

`P_mu >= -D_tau^2+a mu^2-b mu`.

Every retained Weyl level satisfies `mu>=2b/a`, so on the collar

`P_mu >= -D_tau^2+(a/2)mu^2`.

Split the spectral integral at `E_mu=a mu^2/4`.  Below `E_mu`, the collar is
an Agmon barrier with action at least

`A_mu>=ell_0 sqrt(a) mu/2=ell_0 mu/(2 R_max)`.

The two Poisson factors in the rank-one Krein derivative therefore contribute
the squared transmission factor

`exp(-2 A_mu)<=exp(-ell_0 mu/R_max)`.

Above `E_mu`, the heat kernel contributes

`exp(-E_mu)<=exp(-a mu^2/4)`.

The incoming compliance generator has only the already-certified degree-four
polynomial angular loss and the linear transfer factor `exp(c_f mu)`.  The
stored numbers satisfy

`ell_0/R_max-c_f>0`.

Hence both absolute majorants

`(1+mu)^4 exp(-(ell_0/R_max-c_f)mu)`

and

`(1+mu)^4 exp(c_f mu-a mu^2/4)`

are summable after multiplication by every retained quadratic angular
multiplicity.  Scalar, transverse-gauge, and Hubbard--Stratonovich channels
have no adverse Dirac-linear term and obey the same or a stronger estimate.
The longitudinal/ghost pair continues to cancel mode by mode.

This closes the complete graded angular direct sum of the maximal
fixed-terminal incoming relative heat cotangent.  It is a boundary-local
source theorem: it neither contradicts nor reopens the existing counterexample
for a different interior log-radius source on an arbitrary finite-optical
tail.  No spatial Galerkin estimate is repurposed as a temporal tail.

The theorem proves existence and absolute summability, not the numerical
value or sign of the maximal heat coefficient.  The remaining Gate-7 object
is the complete signed joint covector in all physical quotient directions,
its reverse-adjoint Cauchy limit, and the KKT root (or an actual finite later
event/canonical stop).

Only the external Cauchy/birth datum is zero.  No internal response is zeroed,
and no source, selector, endpoint, recurrence condition, scale, fit, gate, or
chord is introduced.
