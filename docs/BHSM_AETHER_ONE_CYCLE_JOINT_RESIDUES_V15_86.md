# BHSM one-cycle joint residues v15.86

The reset map is constant on the selected event component, so its Fréchet
derivative contributes no gauge or composite kinetic term.  Both residues are
therefore derivatives of

\[
 \Gamma_{\rm cyc}=\int_0^{T_*}dt\,\Gamma_\partial[\Phi_*(t)]
 +\Gamma_{\rm reset}
\]

with the reset derivative equal to zero.

The constraint-solved reset endpoint and four controlled child slices give a
monotone PCHIP quadrature

\[
 \overline N_T=3166.08,qquad
 \overline N_E=2345.29,qquad
 Z_H^{\rm cyc}=0.00175714,qquad
 Y^{\rm cyc}=23.8559.
\]

Endpoint envelopes are retained in the artifact, so positivity and nonzero
Yukawa do not depend on interpolation details.  On the symmetric branch
(H_*(t)=0), hence the mass part of the fermionic monodromy is the identity
and (M_F=0_3), while the vertex matrix is
(Y^{\rm cyc}I_3\ne0).  Zero mass and nonzero Yukawa are consistent because
they are different derivatives of the same effective action.
