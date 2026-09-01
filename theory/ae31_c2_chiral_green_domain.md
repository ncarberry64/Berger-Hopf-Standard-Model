# AE3.1 current-C2 chiral operator and Green-domain theorem

## Result

The missing object after the local charged-lepton pole theorem is not another
mass model and is not the old pre-AE2 Cayley phase. BHSM-AE-2.0.0 replaced the
old independent parent/child phase family by one reset-glued spin--gauge
bundle:

\[
 \Gamma_0^{\rm child}\Psi=U_R\Gamma_0^{\rm event}\Psi,
 \qquad
 \Gamma_1^{\rm child}\Psi=-U_R\Gamma_1^{\rm event}\Psi.
\]

The graph of the unitary reset lift is maximal isotropic in the two-sided
Green trace space. The older no-go remains a correct statement about the
unchanged pre-AE2 action, but those alternative phase domains are not members
of the selected AE2 successor domain.

AE3 introduces no second fermion wall. Its enclosure surface is a resolved
internal material level set of one smooth action. The fermion trace is smooth
there and the opposite-normal Green forms cancel. Treating the enclosure
restriction alone as an autonomous boundary problem would introduce a new
boundary condition not selected by the action.

## Same-domain chiral operator

The AE3.1 charged-lepton mass operator is a bounded Hermitian zero-order
endomorphism on the finite family fiber. It therefore preserves the
first-order domain and does not change the Dirac Green boundary form. The
current-C2 operator is now assembled as

\[
 \mathcal D_{\ell,C2}=
 \begin{pmatrix}
  D_L & \mathbb M_\ell^{\rm BH}\\
  (\mathbb M_\ell^{\rm BH})^\dagger & D_R
 \end{pmatrix}
\]

on the AE2 reset-glued domain with smooth AE3 internal transmission. Since
the reset acts on the spin--gauge factor and \(\mathbb M_\ell^{\rm BH}\) acts
on the family factor,

\[
 [U_R\otimes I_F,I_{\rm spin\times gauge}\otimes
 \mathbb M_\ell^{\rm BH}]=0.
\]

No Cayley phase, surface density, fitted wavefunction factor, measured lepton
mass, or new family coefficient is introduced.

## Causal Green theorem and the live obstruction

A Dirac-type operator with this bounded mass term has a normally hyperbolic
square at principal-symbol level. The current finite-core C2 family already
has the intrinsic closed-FLRW geometry

\[
 M_4=I_\tau\times S^3,\qquad
 h=-d\tau^2+R_4(\tau)^2d\Omega_3^2,
\]

with strictly positive proper duration and a certified strictly positive
radius on every member through the 1,222-segment compact cover. Each
constant-\(\tau\) \(S^3\) is therefore a Cauchy surface. The finite-core
development is globally hyperbolic member by member, so the standard causal
theorem gives unique advanced and retarded Green operators for compact
sources. This is an existence and uniqueness theorem; no explicit kernel has
yet been evaluated.

The history also carries a radial/proper-history product-Dirac construction.
Its native resolvent parameter is \(z\), not physical \(p^2\), so it is not a
Lorentzian pole oracle.

Nor is a global frequency pole presently defined. A continuous Fourier
frequency requires time-translation invariance or suitable asymptotic
stationarity, and a Feynman two-point function additionally requires a state
or vacuum prescription. None is silently supplied here.

Thus the strongest current statement is:

- the same-domain family-resolved first-order charged-lepton operator is
  derived and assembled;
- the finite-core C2 development is globally hyperbolic familywise and its
  advanced/retarded Green operators exist uniquely;
- an actual global/dressed kernel, Feynman state, and global pole residues
  remain open;
- the first live pole obstruction is selection or maximal continuation of a
  physical C2 history together with a Feynman/asymptotic state class, not the
  mass operator and not the AE2 reset seam.

- `CURRENT_C2_FIRST_ORDER_CHARGED_LEPTON_LR_OPERATOR_ASSEMBLED = TRUE`
- `CURRENT_C2_CHIRAL_OPERATOR_DOMAIN_PRESERVED_BY_MASS_BLOCK = TRUE`
- `FINITE_CORE_CURRENT_C2_GLOBAL_HYPERBOLICITY_DERIVED_FAMILYWISE = TRUE`
- `FINITE_CORE_ADVANCED_RETARDED_GREEN_EXISTENCE_DERIVED = TRUE`
- `GLOBAL_CURRENT_C2_CHARGED_LEPTON_GREEN_OPERATOR_DERIVED = FALSE`
- `GLOBAL_OR_DRESSED_CURRENT_C2_CHARGED_LEPTON_POLES_DERIVED = FALSE`
- `PROPER_HISTORY_Z_PROMOTED_TO_P_SQUARED = FALSE`
