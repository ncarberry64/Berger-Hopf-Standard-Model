# N12 finite-history gluing-force provenance

Status: `GLUING_IDENTITY_DERIVED_CHILD_RESPONSE_DOES_NOT_LOCALIZE_OUT`.

Let the formation and child quadratic pencils be split into Dirichlet
interiors and their common AE2 seam trace.  In a compatible reset frame write

`P_f=[[A,C],[C^dagger,H]]`,

`P_c=[[G,E^dagger],[E,F]]`,

where `A` and `F` are the two Dirichlet interior blocks.  Including the
retained contact block `W`, the joint two-sided pencil is

`P_joint=[[A,C,0],[C^dagger,H+W,E^dagger],[0,E,F]]`.

Bordered elimination, not inversion of an Euler--Dirac block, gives

`M_f=H-C^dagger A^-1 C`,

`M_c=G-E^dagger F^-1 E`,

`S_AE2=M_f+M_c+W`,

and the exact determinant identity

`det P_joint=det A det F det S_AE2`.

For a formation-only action variation that fixes the terminal reset state,
the child pencil and `W` have zero variation, but the joint force is

`D log det P_joint`

`=D log det A+Tr[S_AE2^-1 D M_f]`.

Thus fixing `C2` removes `D M_c`; it does not remove the value of `M_c` from
the seam solve.  The same dependence occurs pointwise in the resolvent
representation of the heat-regulated force.  A relative determinant does not
make it local: it merely separates the Dirichlet bulk factors from the seam
determinant.

The deterministic witness uses one fixed formation pencil and variation with
two positive child pencils.  The determinant identity and its first
variation agree directly in both cases, while the formation contribution to
the joint force changes because the two seam values differ.  These are
information-sufficiency witnesses, not candidate BHSM endpoint theories.

Therefore the certified compact formation `K`, `D K`, `M_C`, and `D M_C`
cannot yield the physical zero-source force until the action-owned `C2`
Calderon response (or the equivalent joint operator) is supplied.  No
formation-history existence, reset recurrence, periodic endpoint, external
force, or boundary selector is introduced.

`FULL_BHSM_COMPLETE=false`.
