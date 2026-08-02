# BHSM v11.2 Support-Character Constraint System

The maximal exact homogeneous-character system justified by the explicit
frozen S8/S4 terms has 12 variables and 12 rows. Its rows are the D8
Einstein-Hilbert, cosmological, sigma mass/quartic, and chi kinetic terms;
non-Abelian curvature homogeneity; projector idempotency; and the localized
fermion kinetic, scalar kinetic, Yukawa, scalar quartic, and scalar mass terms.

Exact symbolic linear algebra gives:

```text
rank = 7
nullity = 5
forced zero = r_e, w_gauge, w_projector, w_chi, w_sigma, w_psi, w_phi
kernel = span(w_C, w_W, w_wall_embedding, w_compatibility, w_core)
```

These are five independent directions, not one common generator
normalization. Assigning support characters to existing coefficients as
spurions would add the missing datum rather than derive it.

