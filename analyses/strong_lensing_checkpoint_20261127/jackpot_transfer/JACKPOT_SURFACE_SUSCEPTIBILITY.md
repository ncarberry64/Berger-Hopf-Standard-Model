# Jackpot: persistent pin plus responsive massive surface (quadratic control)

Norman Works gives one abstract core and separate surface entrances. It does not specify an optical susceptibility. This control keeps the previous positive local operator A = -Delta + ell² Delta², adds one point entrance C0 and one surface averaging trace Cs at independently named stellar scales (0.50 and 6.05 arcsec). A centered spherical shell is a radial closure proxy, not a discovered object or inferred selection of the true geometry. The ordinary stellar and compact deflection stays in the baseline exactly once. No extra ordinary halo is used in the envelope arms.

Use E = 0.5 u A u - j u + k (C0 u-d)²/2 + m²/(2 lambda) - m Cs u; the beta=0 case deletes m. Eliminating m yields H = A - lambda Cs*Cs; H is strictly positive relative to A for beta = lambda Gss < 1, with margin 1-beta in the A metric. The core-on Hessian adds a positive rank-one term. For the same ordinary load j and same lambda, the optical increment stems from q H^-1 C0*, where H^-1 C0* = G0 + beta Gs0/[(1-beta) Gss] Gs. The two-dimensional trace solve independently reproduces that increment. The attraction stays on in the coupled arm; core off is a calculation only. Adding an ordinary load at fixed H changes only q in a one-channel linear response. Changing H creates a distinct radial mode. Neither the auxiliary m nor the regular preferred trace d is an interior core coordinate.

Two explicitly different accounting arms:
- Matched increment sets the target to the core-dependent difference and discards the off-arm induced response from the toy optical map. It tests the interaction, not the full physical field.
- Full response retains the off-arm induced field as well as the core-dependent increment, so the optical excess over known ordinary matter includes every modeled term. This is the more relevant control for this lens. Ordinary gravity is not added twice in either case.

For each of two radii and five beta values, only the two lower-source aperture targets set ell and q; ring knots alone set the three shared nuisance parameters. The nominal Salpeter excess targets are 1.3373e11 and 2.3401e11 solar masses in equivalent projection. No third-source B coordinate informs these solves; A and a fixed root seed forecast B afterward. Two screened-force projections agree against direct quadrature and exterior analytic controls; stability, aperture matching, full and differenced reaction solves are asserted. No covariance or physical coefficient inference is attempted.

| Arm | Radius, kpc | beta | Equivalent slope | B error, mas |
|---|---:|---:|---:|---:|
| Point entrance only | n/a | 0 | 1.157 | 223 |
| Matched increment | 1.843 | .90 | 1.129 | 241 |
| Matched increment | 22.300 | .90 | 1.229 | 73 |
| Full response | 22.300 | .50 | 1.175 | 166 |
| Full response | 22.300 | .75 | 1.230 | 76 |
| Conventional comparator, same geometry | n/a | n/a | not tested here | 97 |

At full-response beta .75 the wider susceptibility improves the nominal B position but makes the inner lens slope worse. The measured model-equivalent slope is 0.96 ± 0.02 ([Turner et al.](https://arxiv.org/abs/2401.08771)); this is a consistency check, not a formal significance estimate. At .90, the compact-shell full model requires a negative point reaction and the wider-shell full model has no bracketing root over the declared 0.3–100 kpc range. Neither is a global exclusion. Every admissible row misses the inner slope benchmark. The beta ladder is a sensitivity study, not a best-fit parameter estimate or an untouched validation set for choosing beta. The improvement is a diagnostic of changing shape, not a validated model, not evidence for an actual susceptibility shell, and not a result to transfer to HE 0435. The next scientific test would use the archived action to supply the spatial response of nonsingular structures, and make it satisfy inner kinematics before reusing B. Do not tune an arbitrary susceptibility against B.

Replay: OPENBLAS_NUM_THREADS=1 python jackpot_surface_susceptibility.py; result jackpot_surface_susceptibility.json.
