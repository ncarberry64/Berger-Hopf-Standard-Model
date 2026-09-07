# AE3.1 intrinsic M4 charged-lepton action transport

The frozen internal hierarchy operator now lives over the actual current-C2
carrier. The next action step is therefore a composition, not a new mass
model. `BHSM-AE-3.1.0` retains the complete AE3.0 localization action and adds
the already defined v11.3 intrinsic M4 lepton--Higgs block:

\[
 S_{\rm AE3.1}=S_{\rm AE3.0}+S_{4,\ell H}^{\rm BHSM}.
\]

The Higgs and charged-lepton fields remain intrinsic M4 fields. The frozen
operator acts only on the family factor, and the current C2 history remains
the carrier factor. No field changes stratum.

## Action and variation

The transported Yukawa operator is

\[
 \mathbb Y_\ell^{\rm BH}
 =\frac{16\sqrt{2\pi}}{3969}
 \exp\!\left[-\frac{\mathcal L_{a,\ell}}{4\pi}\right].
\]

The completed charged-lepton block is

\[
 \begin{aligned}
 S_{4,\ell H}^{\rm BHSM}=\int_{M_4}d\mu_4\,[
 &|D H|^2-V_{\rm BH}(H)
 +i\bar L_L\gamma^\mu D_\mu L_L+i\bar e_R\gamma^\mu D_\mu e_R\\
 &-(\bar L_L\mathbb Y_\ell^{\rm BH}H e_R+\mathrm{h.c.})],
 \end{aligned}
\]

with

\[
 V_{\rm BH}(H)=\lambda_H(H^\dagger H-\nu_{\rm BH}^2)^2,
 \qquad \lambda_H>0.
\]

Variation gives

\[
 i\!\not\!D L_L-\mathbb Y_\ell^{\rm BH}H e_R=0,
 \qquad
 i\!\not\!D e_R-(\mathbb Y_\ell^{\rm BH})^\dagger H^\dagger L_L=0.
\]

The independent charged-lepton matrix is not retained, and no separate mass
term is added after symmetry breaking. Up and down terms are not added by
analogy: their ratio operators are attached, but their action-owned
prefactors require separate derivations.

## Conditional tree-level operator

Using the inherited single universal energy calibration gives the stationary
branch

\[
 v_{\rm BH}=2\sqrt2 E_\star
 \exp\!\left[-4\pi^2-\frac{a-1}{4\pi^2}\right].
\]

This does not use the measured Higgs vacuum expectation value. It remains
conditional because the absolute universal unit is not first-principles
derived in the current action chain.

The action variation yields

\[
 \mathbb M_\ell^{\rm BH}
 =\frac{v_{\rm BH}}{\sqrt2}\mathbb Y_\ell^{\rm BH},
\]

with the no-lepton-input conditional eigenvalues

\[
 (1.758930614523592,\ 0.10566682607467498,\
 0.0005229143548875549)\ {\rm GeV}
\]

in the frozen heavy, middle, light slots. These reproduce the historical
action result; they are not promoted as current-C2 physical pole masses.

## Local enclosure poles

At every regular interior point of the AE3 enclosure, the action-selected
Lorentzian induced metric supplies an orthonormal tetrad. The composed action
therefore has the local symbol

\[
 \mathcal D_\ell(x,p)=\gamma^a e_a{}^\mu(x)p_\mu-\mathbb M_\ell^{\rm BH}.
\]

On each frozen family projector,

\[
 \det\mathcal D_f=(h^{\mu\nu}p_\mu p_\nu-m_f^2)^2,
 \qquad
 S_f(p)=\frac{i(\gamma\cdot p+m_f)}{p^2-m_f^2+i0}.
\]

Thus the three conditional tree operators define three distinct local mass
shells. At rest the positive and negative frequency roots are
\(\omega=\pm m_f\), and each energy root is simple. The residue follows from
the canonical kinetic term; no independent wavefunction factor is fitted.
This closes the local enclosure identification bridge for the charged-lepton
family at conditional tree level.

## Exact remaining global pole calculation

The attached current-C2 data contains separate squared chiral pencils. Those
pencils do not yet contain the new family-noncentral left--right mass block.
The next operator is the same-domain first-order chiral matrix

\[
 \mathcal D_{\ell,C2}=
 \begin{pmatrix}
  D_L & \mathbb M_\ell^{\rm BH}\\
  (\mathbb M_\ell^{\rm BH})^\dagger & D_R
 \end{pmatrix}
\]

on the retained maximal-isotropic current-C2 domain. The existing product-
Dirac pencils are radial/proper-history squared forms and are not a Lorentzian
momentum-space propagator. A global or dressed Green operator and its residues
must therefore be evaluated separately, without a fitted wavefunction factor.
Only that calculation, or an equivalent matched-parent relative charge, can
promote the conditional local tree masses to full physical mass claims.

- `AE31_CHARGED_LEPTON_M4_SEMIGROUP_COUPLING_ACTION_OWNED = TRUE`
- `AE31_CONDITIONAL_TREE_CHARGED_LEPTON_MASS_OPERATOR_DERIVED = TRUE`
- `CURRENT_C2_LOCAL_TANGENT_FRAME_TREE_POLES_DERIVED = TRUE`
- `LOCAL_ENCLOSURE_PARTICLE_IDENTIFICATION_BRIDGE_CLOSED_CONDITIONALLY = TRUE`
- `CURRENT_C2_PHYSICAL_CHARGED_LEPTON_POLES_DERIVED = FALSE`
- `ABSOLUTE_UNIT_FIRST_PRINCIPLES_DERIVED = FALSE`
