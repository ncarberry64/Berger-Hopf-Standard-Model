# Universal three-body decay phase space

The universal decay readout now integrates a scalar-parent `1 -> 3` BHSM
amplitude without importing a flat-space particle mass, fitted coupling, or
experimental channel assignment.

For parent mass `M`, daughter masses `m1,m2,m3`, pair invariant `s12`, and the
daughter-1 helicity angle `theta*` in the 12-pair rest frame, the implemented
identity is

`Gamma = 1/(512 pi^3 M^3) integral ds12 [sqrt(lambda(M^2,s12,m3^2)) sqrt(lambda(s12,m1^2,m2^2))/s12] integral dcos(theta*) |A(s12,cos(theta*))|^2`.

Initial-state averaging and identical-final-state symmetry factors divide the
right-hand side.  The invariant limits are `(m1+m2)^2` and `(M-m3)^2`.
Tensor-product Gauss-Legendre quadrature is deterministic; thresholds,
nonfinite values, and negative amplitude squares fail closed.  In the
massless constant-amplitude limit the code reproduces
`Gamma = |A|^2 M/(512 pi^3)`.

The amplitude, LSZ residues, spin/internal sums, masses, action version, and
physical channel identity remain upstream action-owned inputs.  This closes
the universal three-body phase-space formula only.  It does not instantiate a
BHSM decay width and does not close four-or-more-body channels.
