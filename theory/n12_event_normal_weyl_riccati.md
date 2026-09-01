# N12 event-normal Weyl Riccati system

Status: `EVENT_NORMAL_WEYL_INITIAL_VALUE_SYSTEM_DERIVED_COEFFICIENT_CONTINUATION_OPEN`.

The retained finite event graph fixes the terminal value of the exterior
Weyl--Calderon map.  With `s` the nonnegative physical distance from the
terminal event into the finite exterior,

`M(0,z)=W_phys`.

For the source operator `-D_s^2+L_spatial(Y(s))`, its inward continuation is
the exact matrix Riccati equation

`D_s M=(L_spatial(Y(s))-z I)-M^2`.

The geometry variation required by the zero-source force satisfies

`D_s(delta M)=delta L-M delta M-delta M M`,

with terminal value `delta M(0,z)=delta W_phys`.  Thus the event graph fixes
the correct initial condition and removes an arbitrary Robin or validation-
cover endpoint.  Near the event,

`M(s,z)=W_phys+s(L_event-zI-W_phys^2)+O(s^2)`.

The orientation is verified against the closed scalar constant-coefficient
solution, and the linearized equation is checked by a centered geometry
finite difference.  The actual N12 Weyl value remains open because the
spatial operator, its geometry jet, and the action-owned distance to the
source boundary have not yet been pulled back and interval-enclosed along
the desingularized event-normal branch.

The next object is that pole-free coefficient pullback and Riccati enclosure.
It is an evaluation of the existing operator, not a new endpoint, source
profile, spectral-to-momentum map, selector, scale, or gate.
