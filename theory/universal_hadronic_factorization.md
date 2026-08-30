# Universal hadronic factorization bridge

For each ordered incoming parton pair, the collider readout evaluates

\[
 \sigma_{AB}(S)=\sum_{ij}\int_{\tau_0}^1d\tau
 \int_\tau^1\frac{dx}{x}\,
 f_{i/A}(x,\mu_F)f_{j/B}(\tau/x,\mu_F)
 \widehat\sigma_{ij}(\tau S;\mu_F,\mu_R).
\]

The channel list is explicit: reversed parton order is a separate channel
when required.  Thresholds come from the same-action partonic ledger, while
the PDF set, factorization scheme, and scale choices carry independent frozen
provenance.  Deterministic Gauss-Legendre quadrature is used for both
integrals.

Physical promotion requires Gate 7, a complete same-action partonic ledger, a
PDF input frozen before prediction, and a separately justified outward
quadrature-error bound.  Empirical PDF use is reported rather than relabelled
as an action-derived BHSM quantity.  The module contains no collider datum and
cannot select a BHSM branch, mode, or scale from observed cross sections.
