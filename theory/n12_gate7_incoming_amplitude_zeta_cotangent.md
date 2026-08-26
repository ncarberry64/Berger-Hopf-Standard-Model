# Gate-7 incoming-amplitude zeta cotangent

Status: `INCOMING_AMPLITUDE_ZETA_COTANGENT_STRICT_SIGN_CERTIFIED`.

The certified two-sided local family has, for every sufficiently small
`lambda_0>0`, an event `E0(lambda_0)` whose child reaches the fixed terminal
event `E1=C_*`; the forward event-child glue then creates the fixed child
`C2=E_*`.  Thus varying `lambda_0` changes only the incoming C1 prefix in
this family.  It is an action-owned family coordinate, not a selected history.

On the incoming regularized branch,

`d tau/d lambda=lambda/(-Delta(lambda))`,

with `-Delta>0`.  The formation part of the retained zeta functional is

`Gamma_form^zeta(lambda_0)=-(59/30) integral_0^lambda0
 exp(-x(lambda))*lambda/(-Delta(lambda)) d lambda`.

The fundamental theorem of calculus therefore gives the exact covector

`D_lambda0 Gamma_form^zeta=-(59/30) exp(-x(lambda_0))
 lambda_0/(-Delta(lambda_0))<0`.

Equivalently, the replacement contribution `-D Gamma_form^zeta` is strictly
positive for every `lambda_0>0`.  The certified terminal tube bounds its
coefficient after division by `lambda_0`; the resulting positive interval is
stored in the artifact.  The derivative tends to zero linearly as
`lambda_0` tends to zero, so no uniform positive lower bound is claimed on
the open amplitude interval.

Because `E1` and `C2` are fixed along this particular family coordinate, the
C2 and interface zeta terms have zero amplitude derivative.  This does not
separately impose a KKT condition on the zeta component.  The physical test
still uses the complete joint covector.  The exact remaining comparison on
this direction is the incoming-arm graded heat derivative.  It must be
bounded with the shrinking-arm operator calculus; the finite-core heat seed
is not set to zero and a coarse fixed-gap bound is not promoted through a
singular `lambda_0 -> 0` geometry jet.

No source, selector, fitted cutoff, endpoint, recurrence, scale, gate, or
chord is introduced.
