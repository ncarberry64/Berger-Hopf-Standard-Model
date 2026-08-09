# BHSM v14.83 — Conservation-Consistent Volume-Work Source & Core-Softening Sign Gate

## Executive result

The black-hole/environment driver now has its first **sharp sign threshold** on
an existing BHSM radial action sector.

The recovered radial core is

\[
V_0(R)=aR^5+\frac{b}{R},
\qquad
M(R)=dR^5+\frac{e}{R},
\]

with

\[
R_*^6=\frac{b}{5a}.
\]

Its breathing stiffness is

\[
h_C(R)=\frac{V_0''(R)}{M(R)}.
\]

Introduce an outward generalized work source

\[
V_D(R)=V_0(R)-D_{\rm BH}B_0(R).
\]

The source variable here is not raw energy density. It is the quantity
conjugate to dilation/volume work—an effective outward spatial-stress or
pressure projection.

Differentiating stationarity gives

\[
\frac{dR_*}{dD_{\rm BH}}
=
\frac{B_0'(R_*)}{V_0''(R_*)}.
\]

Now define the fraction of the radial kinetic inertia carried by the \(p=2\)
piece,

\[
\boxed{
\zeta
=
\frac{dR_*^5}{dR_*^5+e/R_*}.
}
\]

At the stationary point, the exact identity is

\[
\boxed{
\frac{h_C'(R_*)}{h_C(R_*)}
=
\frac{2(1-3\zeta)}{R_*}.
}
\]

Therefore

\[
\boxed{
\chi_h
=
-\frac{dh_C}{dD_{\rm BH}}
=
\frac{
2(3\zeta-1)B_0'(R_*)
}{
R_*M(R_*)
}.
}
\]

For an outward source,

\[
B_0'(R_*)>0,
\]

the result is

\[
\boxed{
\chi_h>0
\iff
\zeta>\frac13.
}
\]

So the black-hole/environment drive softens the radial core if and only if the
\(p=2\) radial inertia contributes more than one third of the total inertia.

If

\[
\zeta<\frac13,
\]

the same outward drive stiffens the core.

This is an exact no-fit sign theorem.

## Seven-volume bridge

The minimal isotropic dilation-work normal form for the existing seven-spatial-
dimensional radial texture is

\[
B_0(R)\propto R^7.
\]

Absorbing the fixed geometric volume normalization into the definition of the
derived drive variable,

\[
B_0(R)=R^7
\]

gives

\[
B_0'(R)=7R^6.
\]

Hence

\[
\boxed{
\chi_h
=
\frac{
14R_*^5(3\zeta-1)
}{
M(R_*)
}.
}
\]

No phenomenological \(\chi\) has been introduced.

This \(R^7\) source is still a Bridge-And-Prove normal form. The actual
black-hole/accretion/jet spatial-stress projection must come from the action or
a controlled conserved open-system reduction.

## Why this is not raw black-hole energy

The relevant source is dilation work.

Under a metric dilation, the variational object conjugate to the deformation
is spatial stress/pressure. Positive energy density by itself does not fix the
sign of that work.

Therefore

\[
\text{black-hole luminosity}>0
\]

does not automatically imply

\[
D_{\rm BH}>0
\]

in the volume-work convention.

What must be derived is the projection of accretion, jet, horizon, matter and
gravitational response onto the effective outward spatial stress of the
dynamic BHSM background.

That preserves the v14.81 Raychaudhuri firewall.

## Transfer to the v11.4 attachment root

The common-attachment lower root is

\[
\mu_-=
\frac{
h_C+k_D-\sqrt{h_C^2-h_Ck_D+k_D^2}
}{3}.
\]

For \(h_C,k_D>0\),

\[
\frac{\partial\mu_-}{\partial h_C}>0,
\qquad
\frac{\partial\mu_-}{\partial k_D}>0.
\]

If \(k_D\) is temporarily held fixed,

\[
\boxed{
\chi_{\mu}
=
\frac{\partial\mu_-}{\partial h_C}\chi_h.
}
\]

Thus the same threshold

\[
\boxed{\zeta=\frac13}
\]

determines the sign of the attachment softening in that restricted chain.

The final physical calculation must also include the drive response of
\(k_D\).

## Can the existing archive decide the sign?

Not yet.

The v14.68 reconstruction provides

\[
R_*=2.2052964058317697,
\]

\[
V_{RR}=124387.78634175545,
\]

\[
M_{RR}=685741.3712834204,
\]

and

\[
h_C=0.18139169014836257
\]

for the archived fixed-profile proxy.

But

\[
M_{RR}
=
\kappa_1D_2R_*^5+\frac{D_8}{R_*}
\]

contains two pieces.

The sign theorem needs their ratio,

\[
\zeta
=
\frac{
\kappa_1D_2R_*^5
}{
M_{RR}
}.
\]

The archived total \(M_{RR}\) alone cannot recover that partition.

Therefore the physical sign remains open.

## Hindsight 20/20 ledger

### VALIDATED

- exact outward radial response;
- exact stiffness log-derivative;
- exact susceptibility;
- \(1/3\) kinetic-partition threshold;
- finite-difference verification;
- attachment-root sign inheritance when \(k_D\) is fixed;
- distinction between energy density and dilation work.

### INVALIDATED

- outward activity always softening the radial core;
- inferring the sign from total \(M_{RR}\) alone;
- using black-hole luminosity directly as the dilation-work source.

### RECLASSIFIED

The black-hole-driver sign is now a **kinetic-partition plus stress-projection
problem**.

The next missing physical data are

\[
\kappa_1D_2R_*^5,
\qquad
\frac{D_8}{R_*},
\qquad
B_0'(R_*),
\]

followed by the \(k_D\) response.

## Completion state

`CORE_SOFTENING_THEOREM = DERIVED`

`OUTWARD_SOFTENING_IFF = zeta > 1/3`

`SEVEN_VOLUME_WORK_SOURCE = PROVISIONAL BRIDGE`

`PHYSICAL_ZETA = OPEN`

`PHYSICAL_D_BH = OPEN`

`PHYSICAL_CHI_H = OPEN`

`PHYSICAL_ATTACHMENT_CHI = OPEN`

`PHYSICAL_EXECUTION_BLOCKED = TRUE`

`FULL_BHSM_COMPLETE = FALSE`

`MARK_III = NOT_REACHED`
