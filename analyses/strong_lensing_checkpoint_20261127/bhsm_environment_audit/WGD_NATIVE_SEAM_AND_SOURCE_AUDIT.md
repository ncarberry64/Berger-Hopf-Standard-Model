# WGD native environmental-source and seam audit

**Finding:** A separate archival sharp-seam law exists, but does not
independently fix WGD response. Its gravity-only reference branch is
too small on both the circularized stellar profile and a conservative
HST-light bound. This does not rule out a distinct, unevaluated
coupled-forming or anisotropic environmental branch.

## Exact source ownership

- BHSM pinned main 551ce2c8e4e672538e520629b0d4a8962cbba968:
  `products/blackhole_tracker/bhtracker/theory/bhsm_sources/BHSM_Topographic_Galaxy_Encapsulation_Solution_v0_3.md`
  and `BHSM_Galaxy_Gravity_Loaded_Schur_Hessian_v0_5.md`
  contain the pre-existing positive exterior neighborhood law and its
  constrained seam-normalization problem. The filed rotation result
  assumes constant enclosed ordinary mass outside the seam, a particular
  flux and its outward support. A conditional light deflection still
  needs metric slip and the finite/compensated global continuation.
- At the same commit,
  `src/bhsm/interface/owner_authorized_encapsulation_interface_action.py`
  supplies the IF5 functional class and Euler operators, but explicitly
  leaves universal invariant functions W_s, the physical carrier, complete
  reduced symplectic domain and Hessian/transversality unselected.
  `action_extension_ae2_nonfermion_threshold.py` is a consumer of supplied
  two-arm DtN and Wentzell lower bounds. It does not generate WGD A_dir,
  b or K. Degree-one/Z6 shape and n=3/n=12 child certificates retain
  their own carriers; no source-owned WGD embedding was located in
  the inspected code, certificates, or relevant chat.
- The R1 paper's pinned source derivation explicitly distinguishes
  the archive's distributed 1/r metric-force tail from the isolated
  R1 exterior 1/r² tail. Do not identify them or stack them by default.
  Its existing ambient Hessian equation can be evaluated only after
  supplying 3-D environmental density, scalar state/outer data and
  matching. A recognized two-dimensional convergence/shear is not
  that scalar Hessian.
- Older cumulative sea history defines a possible multi-enclosure
  effective-action/stress route but does not supply a WGD state-to-Weyl
  source. The separately released BHSM angular lens paper is a
  conditional transfer on prescribed SIS and does not fix a galaxy's
  physical mode amplitude.

## Sharp-seam geometry and rigorous conditional projection bound

Use the normalized archived outward extra enclosed mass
m_enc(r)=A M_* (r/r_*−1)_+, where M_* denotes the ordinary enclosed
mass at the seam, not the whole galaxy mass by definition. In this
section M symbols are masses, not geometric lengths. At impact b,
the projected extra equals A M_* I(b/r_*), with

- I(x)=sqrt(1−x²)+x asin(x)−1 for x≤1;
- I(x)=πx/2−1 for x≥1.

The two branches agree at x=1. This is direct shell integration; the
analytic expression was checked by independent quadrature. For x≤1,
I(x)/x² is increasing, since its integral representation is
int_1^∞ dy/[y² (1+sqrt(1−x²/y²))]. For x≥1 it is maximized at
x=4/π, with global maximum π²/16. Truncating that *same* positive
sphere family reduces its projected mass; it is not a bound on an
arbitrary independently gravitating outer component.

The exact geometric Brown–York crossing gives
G M_*/c² = r_*²/R_H − r_*³/(2 R_H²). Inserting the preceding global
maximum therefore gives the radius-independent bound
δM_cyl ≤ A π² c² b²/(16 G R_H).
For constant slip ratio γ=Ψ_enc/Φ_enc, multiply the optical equivalent
mass by (1+γ)/2 (assuming a nonnegative Weyl response). Under a generalized
weak-field threshold Xi=xi_c, the same inequality scales linearly in
xi_c. This is a necessary combined normalization in the same shell
ansatz, not an inferred parameter or endorsement of extending a local
Schur expansion to xi_c far from 1.

Under the common frozen R1 distance example (z_l=.230,z_s=.777), b=4.9212
kpc and the circular critical mass is 2.46863e11 solar masses. The A=1,
Φ=Ψ, unit gravity-only threshold cap is 3.8145% of the circular critical
mass for today's curvature radius and 4.6918% if the physical curvature
radius scales to lens epoch. The HST F160W fraction .29075938 at 1.36
arcsec gives a conservative upper stellar fraction at 1.30 arcsec by
monotonic positive integrated light under constant M/L. Keeping HST
photometric log masses 11.57 and 11.82 as fixed inputs, those upper
stellar fractions are .4376 and .7782. The resulting minimum combined
A × (1+γ)/2 × xi_c needed to account for the remainder is at least
14.74 / 5.82 (present curvature-radius convention) or 11.99 / 4.73
(physical lens epoch). No adjustment was made to meet those values.
F160W fraction source: pinned TDCOSMO notebook, cells 37/39/40,
85ee2127a7f668f0642f17ad52d09ed9da73e443.

## Extended body and existence/uniqueness conditions

As a distinct check use the DES circularized Sérsic radial shape and
the two HST mass scales, not a point-mass exterior inside the stars.
Insert M(<r) into the static spherical spatial-curvature deficit.
Numerical outer geometric roots (logM 11.57 / 11.82) are
18.5125 / 28.1058 kpc (today curvature radius) and 15.5874 / 24.3898
kpc (physical lens epoch). The computed central crossings are within
8 pc, on the rising acceleration side, and rely on unresolved inward
profile extrapolation. They are not candidates for the outward
weakening handoff and neither geometric crossing is a physical
Hessian zero. The projected extra at the outer geometric roots is
only 3.10–3.84% of critical across these cases.

Define the dimensionless action load C_Q(r)=(b†K⁻¹b−A_dir)/Z_g
for the same normalized mode and transported constraint quotient.
A conditional root of F(r)=Xi(r)−xi_g(r)−C_Q(r) exists if a regular
continuous common block has opposite signs at initially fixed exterior
bracket endpoints. A sufficient uniqueness condition is F'<0 throughout,
e.g. dXi/dlnr plus the absolute derivative of xi_g+C_Q is strictly
negative throughout. If positive K≥k_min I and ||b||≤B_b, then the
relaxation term lies in [0,B_b²/k_min]. Quantifying F and its derivative
also requires A_dir and its derivative, the varying normalized profile,
and transport of the complement. One local restored slope cannot
certify a whole interval. On the DES geometric outer roots alone,
dXi_newton/dlnr ranges from −1.153 to −1.501 (normalized at unit Xi).
The independent action term can shift this crossing either way;
positivity of the isolated topographic K_T just controls one sign,
not the magnitude or full derivative.

The next scientific operand is therefore the galaxy's jointly selected
carrier, parent/child and exterior state, monopole deformation and
same-domain projected (Z_g,A_dir,b,K) with numerical bounds, then
the action-owned export covector and its response in Φ+Ψ. This is
narrower than fitting a halo or assuming a lens aperture supplies
a seam. No timings were used and no external update was performed.

Replays: `wgd_extended_seam_bracket.py`, `wgd_archived_seam_control.py`,
and `wgd_uniform_hessian_r1_control.py`; each writes its same-base JSON.
