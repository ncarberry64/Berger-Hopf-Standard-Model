# Integrating endpoint and midpoint-center mean-value bounds

Use independently paired endpoint actions A=DF_E(E_j) and midpoint center
actions B0=DF_M(w0), each enclosed on its original physical domain. The midpoint
mean-value producer must use exactly the paired center direction w0 that the
original split calculation used. Require complete uniform mixed graphs and
same-family smoothness before consuming either mean-value bound.

The existing preconditioned split formula applies unchanged. With P=R^-1 T,
Q=P DF_M, A0 the exact midpoint of A, and sigma the left/right sign, retain

    fixed + h P A0/6 + 2h P B0/3
      + (h P/6 + sigma h^2 Q/12)(A-A0)
      + 2h Q(E_j/2 + sigma h A0/8 - w0)/3.

The original full midpoint derivative encloses Q. Keep all uncertainty and
center-construction rounding in the last term. Changing the enclosure of B0
does not change w0 or remove its remainder. Compare against the paired local
column with endpoint-only mean-value improvement and retain whichever valid
coordinate enclosure is narrower. Preserve the prior bound and all candidates.

This algebra evaluates no new action derivatives. Pair its exact output bytes
before further use. It covers one fixed-frame local trial column; the full
trial basis, moving-frame derivatives, physical quotient, full-path contraction
and BHSM completion remain open.
