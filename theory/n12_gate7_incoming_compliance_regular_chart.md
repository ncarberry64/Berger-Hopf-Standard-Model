# Gate-7 incoming compliance regular chart

Status: `INCOMING_COMPLIANCE_REGULAR_CHART_AND_LINEAR_AMPLITUDE_JET_CERTIFIED`.

The compact incoming transfer matrix, in the retained conormal convention, is

`Phi_f=[[a,b],[c,d]]`.

After the external birth Dirichlet reference is imposed, the internal event
response is `M_f=d/b`.  This Dirichlet-to-Neumann chart has the familiar
short-arm Laurent pole.  The equivalent Neumann-to-Dirichlet chart is

`C_f=M_f^(-1)=b/d`.

It is regular as the incoming proper duration tends to zero.  The transfer
equation gives `b=T+O(T^2)` and `d=1+O(T)`, hence

`C_f=T+O(T^2)`.

For every positive member of the certified family the negative-axis form
bound makes `M_f>0`, so this scalar/channel inverse is legitimate.  It is not
an inverse of the Euler--Dirac descriptor or kinetic block.  Differentiating
either chart gives the exact identity

`D C_f=-C_f (D M_f) C_f=(D b*d-b*D d)/d^2`.

The action-owned duration law satisfies

`D_lambda T=lambda/(-Delta(lambda))`,

with `0<d_-<=-Delta<=d_+`.  The normalized coefficient-path theorem also
gives `D_lambda x=O(lambda)`.  Consequently, for every fixed retained angular
channel and every fixed negative resolvent probe,

`D_lambda C_f=lambda/(-Delta(lambda))+O(lambda^3)=O(lambda)`.

In particular, the apparent `D_lambda M_f=O(lambda^-3)` divergence is removed
by the two compliance factors in the exact reverse identity.  The limiting
coefficient obeys

`1/d_+ <= liminf |D_lambda C_f|/lambda`

and

`limsup |D_lambda C_f|/lambda <= 1/d_-`.

The joint seam can therefore be parameterized near the zero-length incoming
arm by the regular compliance `C_f`, and the functional-calculus variation of
each fixed channel is pointwise `O(lambda)`.  This does not yet prove the
uniform graded heat derivative: interchanging the amplitude derivative with
the infinite retained angular supertrace still requires an action-owned
summable domination bound.  No componentwise KKT condition follows from this
chart change, and the internal incoming response is not set to zero.

No source, selector, endpoint, recurrence condition, scale, gate, or chord is
introduced.
