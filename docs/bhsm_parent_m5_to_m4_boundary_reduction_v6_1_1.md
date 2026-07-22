# BHSM v6.1.1 parent M5 to physical-boundary M4 reduction

## Result and scope

Primary result:
`BHSM_ROUND_EQUATORIAL_M4_ZERO_MODE_ARCHITECTURE_DERIVED`.

Boundary-action status: `BHSM_M5_TO_M4_BOUNDARY_ACTION_PARTIAL`.

The selected round P1 trajectory and all v6.1 bosonic normalizations are
preserved.  This sprint derives the exact equatorial Lorentzian geometry,
Gauss--Codazzi and GHY ledgers, the normal Sturm--Liouville problem, its scalar
zero mode, formal profile normalizations, boundary domains, and the permanent
fermionic/Clifford and no-monopole firewall.

The equator is an exact control hypersurface and may become the boundary of a
selected hemisphere or a Z2 fixed surface.  The parent action does not select
that interpretation or supply independent boundary kinetic terms.  Moreover,
the S4 polar geometry is warped rather than a product `M4 x interval`.
Smooth bulk profiles give unequal temporal and S3-gradient weights, and no
regular massless tangential vector or product-graviton zero mode exists.
Consequently the complete physical Lorentzian M4 action is conditional on an
explicit boundary or collar-localization action with unsourced coefficients.

## Permanent firewall

`BHSM_FERMIONIC_CLIFFORD_AND_NO_MONOPOLE_FIREWALL_FROZEN` remains permanent.
BHSM assumes neither a foundational physical Dirac equation nor a physical
magnetic-monopole sector.  Spin structures, Clifford multiplication, spin
connections, and first-order spinorial operators are mathematical geometry
until a BHSM-native fermionic action, domain, and physical map are derived.

Hopf winding, principal U1 bundles, curvature two-forms, transition functions,
and first Chern classes remain bundle data.  They are not magnetic charge.
Dirac strings, monopole harmonic mode bases, magnetic-charge quantization,
monopole-induced chirality, and monopole-generated generations are excluded.

## Exact M5 and equatorial geometry

The effective M5 metric is

\[
ds_5^2=-dt^2+a(t)^2\left[d\chi^2+\sin^2\chi\,d\Omega_3^2\right],
\qquad 0\le\chi\le\pi.
\]

Thus the S3 level-set radius and measure are

\[
r_3=a\sin\chi,\qquad
\sqrt{-g_5}=a^4\sin^3\chi\sqrt{\gamma_3}.
\]

The poles are `chi=0,pi`; the equator is `chi=pi/2`.  The relevant volumes
are

\[
\operatorname{Vol}(S^4_a)=\frac{8\pi^2}{3}a^4,
\quad
\operatorname{Vol}(S^4_{a,+})=\frac{4\pi^2}{3}a^4,
\quad
\operatorname{Vol}(S^3_a)=2\pi^2a^3.
\]

With unit normal \(n=\pm a^{-1}\partial_\chi\), a constant-chi surface has

\[
K_{tt}=0,\qquad K_{ij}=\frac{\cot\chi}{a}h_{ij},
\qquad K=\frac{3\cot\chi}{a}.
\]

At the equator, \(K_{\mu\nu}=K=0\).  It is totally geodesic, minimal, and
fixed by \(\chi\mapsto\pi-\chi\) for every value of the dynamic scale factor.
The exact induced metric is

\[
ds_4^2=-dt^2+a(t)^2d\Omega_3^2.
\]

Its intrinsic curvature and Einstein tensor are

\[
R_4=6\left(\frac{\ddot a}{a}+H^2+\frac1{a^2}\right),
\]

\[
G_{00}=3\left(H^2+\frac1{a^2}\right),\qquad
G_{ij}=-\left(2\frac{\ddot a}{a}+H^2+\frac1{a^2}\right)h_{ij}.
\]

These are induced kinematics.  They are not a standalone M4 Einstein equation
or an observed-cosmology claim.  The lapse and proper time are inherited from
M5 without rescaling.

All great S3 equators lie in one symmetry-equivalent SO(5) orbit.  Geometry
therefore provides no preferred equator or axis.  Choosing a hemisphere and
outward normal is additional boundary/orientation data.

## Boundary and variational status

The uncut equator is a control surface, not a boundary.  Cutting to
`0<=chi<=pi/2` creates a mathematical hemisphere boundary.  A Z2 quotient or
interface is another conditional boundary interpretation.  None of these
operations alone creates independent fields on the equator.

After the completed S3-fiber pushforward, the M5 Einstein--Hilbert coefficient
is

\[
C_5=\frac{\kappa_1\operatorname{Vol}(S^3_a)}2
   =8\pi^2\kappa_1a^3.
\]

In the declared convention, with
\(K_{\mu\nu}=\mathcal L_nh_{\mu\nu}/2\) and normal acceleration
\(a_n^A=n^B\nabla_Bn^A\), the curvature decomposition is

\[
R_5=R_4+K^2-K_{\mu\nu}K^{\mu\nu}
    -2\nabla_A(Kn^A-a_n^A).
\]

Although the extrinsic terms vanish at the equator, the normal-curvature and
total-divergence content does not.  On the round background,

\[
R_5=8\ddot a/a+12(H^2+a^{-2}),\qquad
R_4=6(\ddot a/a+H^2+a^{-2}).
\]

Restriction therefore does not create an independent M4 Einstein--Hilbert
action.

For an actual boundary the required variational completion is

\[
S_{\rm GHY}=2C_5\int_{M_4}\sqrt{-h}\,K.
\]

Its background value, canonical momentum, and Brown--York stress vanish at
the totally geodesic equator.  Its variation must nevertheless be retained to
cancel normal metric-derivative variations.  GHY is not an intrinsic boundary
kinetic action.

## Normal spectrum and exact zero-mode gate

For a scalar normal profile the exact dimensionless operator is

\[
\mathcal L_\chi u=-\frac1{\sin^3\chi}
\partial_\chi\left(\sin^3\chi\,\partial_\chi u\right),
\]

with weight \(w=\sin^3\chi\).  Its Green form is

\[
\left[\sin^3\chi\,(u^*v'-u'^*v)\right]_{\partial I}.
\]

Regular full-S4 zonal modes have
\(\mu_\ell=\ell(\ell+3)\) and physical normal mass
\(\mu_\ell/a^2\).  On a hemisphere, even Z2 modes obey Neumann conditions and
odd modes obey Dirichlet conditions at the equator.  The even constant scalar
is an exact zero mode.  The lowest odd zonal mode is proportional to
\(\cos\chi\) and has \(\mu=4\).

The exact zero-mode audit is asymmetric:

- The neutral scalar singlet has an even constant zero profile.
- A connected compact S4 has no nonconstant scalar zero mode.
- There is no regular global tangential vector zero mode: `H1(S4)=0`, and a
  constant S3 component is singular where the S3 orbit collapses.
- There is no product-factor M4 graviton zero mode because the S3 directions
  collapse at both poles.

The latter sectors therefore need an action-supported boundary or collar
profile.  A low positive mode is not relabeled as a zero mode.

## Warped-weight obstruction

For the constant scalar profile, comparison with the equatorial M4 metric
gives

\[
L_t=a\int_I\sin^3\chi\,d\chi,
\qquad
L_s=a\int_I\sin\chi\,d\chi.
\]

On the full S4, \(L_t=4a/3\), \(L_s=2a\); on a hemisphere,
\(L_t=2a/3\), \(L_s=a\).  In both cases

\[
\frac{L_s}{L_t}=\frac32.
\]

More generally, for every nonzero smooth bulk profile,
\(\sin^3\chi<\sin\chi\) away from the equator, so a single standard
Lorentzian M4 kinetic coefficient cannot be obtained from smooth bulk support.
Exact equality requires equatorial support or a compensating boundary action.
This obstruction is independent of the v6.1 time-control floor.

For a tangential connection the electric and magnetic weights are still more
restrictive:

\[
L_E=a\int\sin\chi\,|u_A|^2d\chi,
\qquad
L_B=a\int\frac{|u_A|^2}{\sin\chi}d\chi.
\]

Pole regularity excludes a constant tangential vector profile.  Hence the
formula \(g_4^2=g_5^2/L_{\rm eff,A}\) is valid only after an action derives a
regular profile with one common M4 coefficient.  No `L_eff,A` is invented.

## Scalar normalization and potential

For the full-S4 even constant singlet,

\[
Z_{4,t}=\frac{64\pi^2}{3}Z_\sigma a^4,
\qquad
Z_{4,s}=32\pi^2Z_\sigma a^4.
\]

The exact homogeneous canonical variable is
\(s_4=\sqrt{Z_{4,t}}\,\sigma\).  At the minimum slice its field-redefinition
pump is \(-\lambda/21\).  The parent mass remains \(A_0/Z_\sigma\), and the
temporally normalized quartic is

\[
G_{4,\rm can}=\frac{3G_0}{64\pi^2Z_\sigma^2a^4}.
\]

These formulas do not make the inhomogeneous bulk mode a standard Lorentzian
M4 scalar; that still requires localization.  Sigma is selected only as the
even bulk zero mode restricted to the equator.  An independent boundary,
collar, displacement, or interface role is not derived.  The values
`A_ST=-2`, `G_ST=8`, and `sigma=1/2` remain absent as inputs and outputs.

## Required localization action

The narrow constructive source family is explicit:

- An intrinsic \(C_\partial\int\sqrt{-h}R_4\) term for independent M4
  gravitational dynamics, with \([C_\partial]=L^{-2}\).
- A boundary \(-\tau_A\int\sqrt{-h}F^2/4\) term for a common connection
  normalization, with dimensionless \(\tau_A\).
- A boundary \(-Z_\partial\int\sqrt{-h}(D\sigma)^2/2\) term, with
  \([Z_\partial]=L^{-2}\) for dimensionless sigma.
- A collar mass profile \(V_{\rm loc}(\chi)\) or real Robin coefficient
  \(r\), with dimensions \(L^{-2}\) and \(L^{-1}\), respectively.

None is added in this sprint.  Their action origin and coefficients are the
next theorem target.  Dirichlet, Neumann, real Robin, and matched-interface
domains make the scalar Green form vanish.  Gauge boundary conditions must
also preserve gauge covariance, constraints, and the allowed transformation
domain.

## Currents, aperture, and fermionic readiness

Geometric Sp1 generators and nested U1 weights provide formal current
operators after common gauge and matter profiles close.  The canonical
interaction coefficient remains profile-conditional.  No observed or
magnetic charge operator is produced.

The aperture profile architecture now has an exact normal domain and scalar
profile, but it still lacks a localized regular vector profile, common K4,
projector, and physical matter profile.  Therefore `e_eff` and alpha remain
unevaluated.

The induced `I_t x S3` geometry is spin, and its Clifford bundle, induced
frame, and Levi--Civita spin connection are mathematically available.  The
equatorial background has no extrinsic-curvature correction because
\(K_{\mu\nu}=0\).  This is
`BHSM_FERMIONIC_CLIFFORD_BOUNDARY_READINESS_DERIVED`; the fermionic action,
physical first-order equation, chirality mechanism, and particle map remain
open and have no monopole dependency.

## Scale and stop condition

All geometric normal lengths are multiples of the existing dynamic radius:
the full meridian is \(\pi a\), the hemisphere is \(\pi a/2\), and the scalar
temporal profile factors are \(4a/3\) or \(2a/3\).  They introduce no new
geometric primitive and no absolute unit.  Boundary/localization coefficients
would be new unsourced action primitives.

Completion gate:
`V6_1_1_EQUATORIAL_GEOMETRY_AND_ZERO_MODE_ARCHITECTURE_DERIVED_LOCALIZATION_ACTION_REQUIRED`.

Recommended next branch:
`bhsm-m4-boundary-localization-action-source-v6-1-2`.

Frozen predictions and official prediction logic are unchanged.
`FULL_BHSM_NOT_COMPLETE`.
