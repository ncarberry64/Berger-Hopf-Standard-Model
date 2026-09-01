# N12 C2 outgoing local transfer germ

Status: `ACTUAL_C2_CHANNEL_TRANSFER_AND_FIRST_QUOTIENT_JET_GERM_DERIVED`.

The certified C2 birth data give, for each physical reset-quotient direction
`xi`,

`x0=log R4(0)`, `H0=D_tau x(0)`, `h0=D_xi x0`, and
`hH0=D_xi H0`.

The retained scalar and factorized product-Dirac channel generators depend
only on the actual BHSM radius coefficient.  Their proper-time Cauchy jets
are therefore fixed algebraically by these data.

For a scalar channel with `V=c exp(-2x)` and

`G_s=[[0,1],[V-z,0]]`,

the exact birth identities are

`D_tau V=-2 H0 V`,

`D_xi V=-2 h0 V`,

`D_xi D_tau V=(4 H0 h0-2 hH0)V`.

For a product-Dirac channel with `s=chi lambda exp(-x)` and

`G_D=[[-s,1],[-z,s]]`,

the corresponding diagonal coefficients are

`D_tau G_D=diag(H0 s,-H0 s)`,

`D_xi G_D=diag(h0 s,-h0 s)`,

`D_xi D_tau G_D=diag((hH0-H0 h0)s,-(hH0-H0 h0)s)`.

These are BHSM coefficients inserted into a general transfer identity.  If
`T'=G T`, `T(0)=I`, then

`T(tau)=I+tau G0+(tau^2/2)(G0^2+D_tau G0)+o(tau^2)`,

and

`D_xi T(tau)=tau D_xi G0`

` +(tau^2/2)(D_xi G0 G0+G0 D_xi G0+D_xi D_tau G0)+o(tau^2)`.

This is an inverse-free outgoing `C2` transfer and first quotient-jet germ.
It is a genuine local realization of the already matched `C2` leg, not a
terminal response: both ends remain free traces, and no downstream load has
been selected.  The exact terminal-load Schur reduction can later compose
this germ with whatever later AE2 event or canonical Friedrichs response the
retained maximal history supplies.

Numerical checks integrate the affine Cauchy history for two successively
halved proper durations.  The value and parameter-jet residuals exhibit the
expected cubic-order halving, and the transfer determinant remains one to
integration accuracy in scalar and both product-Dirac chiralities.

The remaining step is a validated nonzero outgoing `C2` coefficient segment
with remainder control.  The local germ itself does not promote a validation
edge to a physical endpoint, determine the maximal response, synthesize the
heat force, or introduce a selector, scale, action term, recurrence, gate, or
chord.

`FULL_BHSM_COMPLETE=false`.
