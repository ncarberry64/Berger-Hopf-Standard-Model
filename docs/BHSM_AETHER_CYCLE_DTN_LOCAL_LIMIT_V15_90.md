# BHSM v15.90: local limit of the cycle DtN map

For either static sector, write the radial problem as

\[
 -(p u')'+\lambda w u=0,
 \qquad u|_{M_4}=1,
\]

with the regular pole condition. At \(\lambda=0\), \(u=1\) and the DtN map
vanishes. Differentiating with respect to \(\lambda\) gives

\[
 (p\,\partial_\lambda u')'=w,
\]

and therefore

\[
 N_T'(0)=\frac1{R_b}\int w_Td\chi,
 \qquad
 N_E'(0)=\frac1{R_b^3}\int w_Ed\chi.
\]

Thus

\[
 N_T(\lambda_T)=K_T\lambda_T+O(\lambda_T^2),
 \qquad
 N_E(\lambda_E)=K_E\lambda_E+O(\lambda_E^2).
\]

The controlled cycle averages are

\[
 \overline K_T=1394.790187,
 \qquad
 \overline K_E=1082.968994.
\]

A direct solve at \(\lambda=10^{-5}\) agrees with these variational
derivatives to better than \(5\times10^{-6}\) relative. Extending
\(\overline K_T\) with the same rank-16 carrier trace again gives

\[
 K_Y:K_2:K_3=\frac53:1:1.
\]

This derives a local spatial field-strength coefficient and a local Gauss
constraint coefficient from the same physical pushforward that generated the
nonzero Yukawa vertex. It does not yet identify a single Lorentzian Maxwell
coefficient: that requires the continuous boundary-frequency derivative
\(\partial N/\partial\omega^2\) of the same five-dimensional radial problem.
