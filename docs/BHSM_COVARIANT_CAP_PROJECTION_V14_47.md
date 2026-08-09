# BHSM v14.47 — Covariant Compact-Cap Projection and Multiscale Matching Gate

## Primary result

For a stationary divergence-free coexact shift on the curved compact cap, write

\[
q_L=(L-1)(L+3).
\]

The exact **structural** covariant projection of the two independent local
curvature-squared operators has the form

\[
\mathcal H_L[R^2]=Aq_L,
\]

\[
\mathcal H_L[R_{\mu\nu}R^{\mu\nu}]
=Bq_L+Cq_L^2.
\]

Here `A` and `C` are nonzero on the curved cap:

- the `R^2` term has no independent `q_L^2` column because the first scalar-
  curvature variation vanishes in the stationary transverse sector; its
  quadratic contribution is background scalar curvature times the ordinary
  second-order shift form;
- the Ricci-squared term necessarily has a four-spatial-derivative contribution
  from the square of the first-order mixed Ricci/momentum-constraint block,
  giving `C != 0`;
- `B` contains lower-derivative background and convention-dependent pieces but
  cannot affect the rank test.

For `L=2,3`, `q_2=5` and `q_3=12`. Therefore

\[
\det
\begin{pmatrix}
Aq_2&Bq_2+Cq_2^2\\
Aq_3&Bq_3+Cq_3^2
\end{pmatrix}
=ACq_2q_3(q_3-q_2)
=420AC.
\]

Thus the exact covariant/constraint projection remains rank two whenever the
operator basis is genuinely present. The earlier normalized matrix

\[
\begin{pmatrix}5&25\\12&144\end{pmatrix}
\]

was not an accidental overcount: the determinant `420` survives an arbitrary
Ricci-squared lower-order `Bq_L` term.

## Consequences

1. Smooth cap regularity does not remove either coefficient.
2. One dynamical Berger modulus gives one stationarity equation and leaves one
   coefficient direction open.
3. The full compact-cap projection does not internally collapse the
   renormalization plane.
4. A second independent microscopic condition or a declared two-observable
   renormalization prescription is still required.

## Neutron-star protocol

The external route is retained only as a preregistered matching or bounding
program. It must specify before data evaluation:

- the covariant coefficient normalization and matching scale;
- the EOS family and prior;
- calibration observables;
- held-out observables;
- regularity, causality, radial-stability and tidal-response kill screens.

Star-by-star retuning or post-hoc EOS selection is forbidden. Astrophysical
matching may define effective renormalized coefficients, but it is not a
microscopic derivation.

## Verdicts

`BHSM_COVARIANT_R2_AND_RICCI2_COMPACT_CAP_PROJECTION_REMAINS_RANK_TWO_IN_THE_L2_L3_COEXACT_SECTOR`

`CAP_REGULARITY_AND_ONE_BERGER_MODULUS_EQUATION_DO_NOT_FIX_THE_TWO_RENORMALIZED_LOCAL_GRAVITATIONAL_COEFFICIENTS`

## Exact next object

`MICROSCOPIC_OR_TWO_CONDITION_RENORMALIZATION_PRESCRIPTION_FIXING_THE_TWO_LOCAL_CURVATURE_COEFFICIENTS_TOGETHER_WITH_NORMALIZED_L2_L3_KOSMANN_SPECTRAL_SUMS_OR_PREREGISTERED_NEUTRON_STAR_MATCHING`

BHSM remains incomplete. Frozen predictions are unchanged. No physical
counterterm, neutron-star, CKM, CP, mass, radius or scale value is emitted.
