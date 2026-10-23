# Independent optical-kernel and SIS calculation review

Date: 21 October 2026.

## Outcome

The executed first-order SIS prediction is internally consistent with the
declared angle-to-physical-separation Jacobi maps, fixed physical source,
fixed SIS deflection strength, fixed measured redshifts, and nodal quadrupole.
No correction to `code/strong_lensing_prediction.py` was required by this
review. This is an implementation and derivation review of a conditional
forward calculation, not empirical validation or physical-state selection.

The review independently checks the units, the original three-term stationary
Fermat variation, and an exact diagonal-map SIS identity. Its executable
receipt is `review/sis_independent_review.json`, produced by
`review/audit_sis_prediction.py`.

## Units and sign

For physical source displacement s, physical SIS deflection
b=4 pi (sigma_v/c)^2, and the positive inner-minus-outer delay,

    Delta t0 = 2 (1+z_l) b s (d_ol/d_os) / c.

This independently reconstructed SI expression agrees with all four saved
background delays to a maximum fractional difference of 6.24e-16. In
particular, the (0.3,1.0) example gives 669912.8932194336 seconds, or
7.753621449299 days, for s=0.8 kpc and sigma_v=200 km/s. H0 cancels from this
expression because the physical source displacement, rather than its angular
position, is fixed; H0 remains part of the declared normalization of the
background, distances, and perturbation coefficients.

With D_ab=d_ab(I+E_ab), the original stationary-image variation is

    delta F_i = 1/2 v_i^T delta T v_i
                - T0 v_i^T delta beta
                - (1+z_l) alpha_hat_i^T d_ol E_ol theta_i,

where delta T=T0(E_ol^T-E_ls+E_os), delta beta=-E_os beta, and
v_i=theta_i-beta. The separate timing-matrix, source, and physical-impact
terms were calculated directly, rather than starting from the simplified
SIS delay formula. Their difference between images agrees with the code's
reduced stationary derivative and the independent SIS expression

    delta Delta t / Delta t0 = e^T(E_ol-E_os)e

to 4.25e-15 of the baseline delay. The probes include symmetric off-diagonal
shear and isotropic map components, not only the code's diagonal nodal mode.
The lens-to-source term cancels in this specified SIS comparison. That
cancellation is not asserted for a general lens or a fixed angular source.

For the nodal quadrupole, E_ab=-sqrt(2)(g_ab dot q)diag(1,-1). Thus

    delta Delta t / Delta t0
      = sqrt(2)[(g_os-g_ol) dot q] cos(2 alpha).

The saved angular predictions agree with an independent reconstruction from
the temporal rows and SI baseline to 1.78e-15 seconds. At alpha=0 the four
illustrative offsets are approximately -0.35321609, -0.12311316,
-1.16339767, and -2.87129664 seconds, respectively, in the recorded
configuration order. The signs reverse at 90 degrees; the first-order
response vanishes at 45 degrees.

## Finite-map completion and scope

For a principal-axis source and diagonal maps, the exact SIS expression in
the chosen map completion obeys

    Delta t / Delta t0
      = (D_ol,axis/d_ol) / (D_os,axis/d_os).

The numerical image solver matches this identity to 4.68e-16 of the baseline
delay. This corroborates the image-solving, delay sign, source convention,
and map normalization. It does not promote the finite map completion to a
nonlinear solution of the cosmological field equations. In particular, the
small nonzero completed delay at 45 degrees is a higher-order property of
that completion and is not a claimed first-order physical prediction.

The module and saved artifact already distinguish this limit correctly.
The two solved roots are continuations of the unperturbed noncaustic SIS
branches. The calculation makes no global image-count assertion. The
effective-potential identity concerns one source plane and the declared
constant-map approximation; it does not establish unique recovery of the
BHSM state or a globally admissible matter model.

The generic optical provider supplies the tracefree map. The stronger use of
these maps as the full first-order propagation perturbation is restricted to
the nodal configuration, whose central ray has Q=grad Q=0 and vanishing
first-order scalar trace/frequency corrections. There is no conflict between
that restriction and `code/OPTICAL_KERNEL_README.md`.

## Original angular-geodesic replay and portability

The original angular Euler equation audit was rerun using its absolute script
path with `/tmp` as the current working directory. It completed successfully
and reproduced the saved results:

- Background fractional-map defect: 2.22e-16.
- Complex-step derivative versus the independently computed Green kernel:
  2.08e-15 maximum absolute difference.
- Weak real half-step derivative: 5.70e-13 maximum absolute difference.
- Constant-Weyl curved-space integral identity: 1.70e-15 maximum absolute
  difference.

The vendor source paths and output roots resolve from the script locations.
The import chain is acyclic: the angular audit imports the new provider;
the provider imports the original transport/action/background modules; those
modules do not import either new optical module. The strong-lens module reads
the saved kernel artifact and does not import the angular provider. No target
observations are read by these calculations.

Reproduce the independent SIS receipt from any working directory with the
absolute path to `review/audit_sis_prediction.py`. Reproduce the angular
receipt with the absolute path to `code/audit_nodal_angular_geodesic.py`.
Python 3.12.14, NumPy 2.3.5, and SciPy 1.17.0 were used for this review.

## Amplitude qualification retained

The illustrative number q_delta_m=0.001 multiplies a unit-L2 normalized
spatial harmonic in the action provider's H0=1 convention. It is not a
spatially uniform 0.1 percent density perturbation and is not inferred from
observations. Exact angular maxima sampled along the cone give maximum
2|Phi| approximately 3.27e-6 through z=1 and 2.04e-5 through z=2. These
checks support use of a small perturbation illustration but do not certify
a nonlinear error bound or a continuous maximum between radial samples.
