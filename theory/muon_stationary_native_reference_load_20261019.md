# A computed native component on the saved coupled background

This application starts from `e8477cc0` and consumes the saved
`run_2/provisional_iterate151` without another interior solve, subtraction
calculation or known-subtotal Newton step. It evaluates a previously missing
constant-angular fermion component and its field-dependent Jacobian. The
complete physical residual remains **unevaluated**. This is conditional
progress at a declared numerical cutoff, not admission under the physical
`2e-10` guard.

The adopted stationary-past incoming prescription remains in force. Its
stationary comparison is not a claim that the prepared beams, event or muon
are static. It does not set the inherited occupation or higher correlations.
The computation below needs no new vacuum or fitted state contraction.

The original canonical-density field is `chi=R4^(3/2) psi`. On the intrinsic
material chart the constant right-body scalar harmonic carries all18 Weyl
components, including all three fixed-Y lepton families. Its normalized
Cauchy Gram is identity; spatial Haar/R4 cubed factors cancel in an operator
trace. This is an exact reducing angular block of this homogeneous reference
operator. It is not the complete lowest Dirac energy level: a spin-harmonic
partner can lie in another scalar angular sector. It is also not the entire
collider Cauchy domain. The cap S3 has not been identified with that domain.

The same-action coefficients, evaluated freshly at the saved moved fields,
are

\[
 W={3\gamma_5/2-i\alpha^a A_{a,\mathrm{total}}\over R_4}+M_Y(H),
 \quad \Omega={A_{t,\mathrm{ref}}\over N_{\mathrm{ind}}},
 \quad A_{a,\mathrm{total}}=a_a+\sqrt8(\lambda-1)T_a.
\]

Here `A` includes the actual unit-trace lepton representation generators;
`W` is Hermitian and `Omega` anti-Hermitian on the real action chart.
The temporal native vertex is `G/N_ind`; the causal Hamiltonian vertex is
`-i G/N_ind`. The native product is not the square of that Hamiltonian.
Independent gauge profiles are traced at fixed **material** `rho_ref=WALL`.
The moving physical wall and connection enter the original `R4`, induced
lapse and mechanical-lambda two-jets. Sampling these material profiles at
`chi_wall` would confuse coordinates and double the material conversion.
Ambient lapse is `1.1103758411139943`; induced lapse is
`1.1101523328051457`. Their derivatives and values are kept distinct.

The temporal domain used for this component is `H1(R_proper)` with its
Fourier spectral measure, evaluated as a density per unit stationary proper
duration. It supplies neither a finite-event boundary condition nor an
inherited CAR state. It is a bulk comparison component of the native
functional; the actual stratified/event domain and relative phase are still
required. No old Euclidean heat array or old background is imported.

The native real factor and its analytic continuation are explicitly

\[
 A(\omega)=i\omega+W+\Omega,
 \qquad P_z(\omega)=(-i\omega+W-z\Omega)(i\omega+W+z\Omega),
 \quad z=e^{-i\theta},\quad 0\leq\theta\leq\pi/2.
\]

`z=1` is exactly `A^dagger A`. Proper-time Wick continuation gives
`Omega_E=-i Omega_L`, hence `z=-i`; the original real-action adjoint branch
is continued analytically as well. Re-taking a Hilbert adjoint after
complexification would change it. In particular the right factor becomes
`i omega+H_can`, while the left factor is not its new Hilbert adjoint.
The continuation therefore returns this native E1 segment and does **not**
prove equivalence to the complete causal determinant or incoming current.
The relative zeta/eta phase and domain completion remain explicit operands.

For `b=||Omega||`, `B=-i Omega`, and a lower bound `w0` for the singular
gap of `W`, the whole continuation is controlled by

\[
 \operatorname{Re}P_z\succeq\tfrac12\omega^2 I+
 [w_0^2-3b^2-\|[W,B]\|]I,\quad |z|\leq1.
\]

The implemented conservative norms use `w0=1/||W^-1||_F` and Frobenius
upper bounds. The resulting margins are `1.597697862839309e-4` on the actual
fields and `1.4478554651487947e-4` on the same-geometry mechanical anchor.
Both are positive at every frequency along the path under these finite
matrix bounds. They are floating point estimates, not outward-rounded
continuum or reference-background certificates. At the endpoint,
`Re P=omega^2+W^2-B^2`. This also gives Gaussian omitted-frequency bounds.
The spectra of `P(-omega)` and `P(omega)^dagger` coincide by factor
interchange. Thus the paired trace is real; the positive-frequency trace
alone has a nonzero imaginary part and is not silently treated as real.

The actually executed functional and signed return are

\[
 \gamma_0(c)={1\over2}\int_{\mathbb R}{d\omega\over2\pi}
                 \operatorname{Tr}_{18}E_1(cP_{-i}(\omega)),
 \qquad L_{0,L}=-N_{\mathrm{ind}}\gamma_0(c).
\]

The fermionic supertrace sign gives the positive one-half in `gamma0`.
The static return follows `S_E=-i S_L`, `dt=-i d tau_E`. There is no extra
charge, Haar volume, embedding factor8, GeV conversion or incoming pair
spin average in this closed trace. The physical-cutoff equation remains
`c=I_total/R_total` with the required surface and bulk impedances. Here
`c=1` is an explicitly declared numerical coordinate at which the function
and its derivatives are evaluated. It has not been adopted as a physical
cutoff. No precision sweep or physical-scale calibration is performed.

The consumed contractions can be written without an occupation guess.
Writing `L=W-z Omega-i omega`, `R=W+z Omega+i omega` and
`F=f'(P)=-P^-1 exp(-cP)`, they are

\[
 D\gamma_0={1\over2}\int {d\omega\over2\pi}
 \operatorname{Tr}\{(RF)\,DL+(FL)\,DR\},
\]
\[
 D^2\gamma_0={1\over2}\int {d\omega\over2\pi}
 \operatorname{Tr}\{L_{f'}(P)[DP]\,DP+f'(P)D^2P\}.
\]

Both factor insertions, both second-contact orders, spectral-weight changes
and vertex derivatives are evaluated. These are regulated **native
functional** contractions, not assigned occupations or `C_plus`.
`local_wall_Higgs_covector24` records the derived temporal4/radial4/spatial12/
Higgs4 cotangents; the radial intrinsic four are exactly zero. The
20-dimensional point-fiber vertex span has not been fitted. Distinct radius
and lapse stress partials are evaluated, and are not identified with those
20 state contractions. Other angular sectors, other species and stratified
bulk stress remain separate requirements.

The full fixed-cutoff151 gradient and Hessian include the geometry/normal,
gauge, scalar and outer induced-lapse chain. The exported189 extension
also retains the original37 geometry-rate and source-rate contacts through
the local stationary symbol. These are **not** the complete nonlocal
history/domain endpoint momenta. Gauge/scalar time-rate and actual history
endpoint derivatives still require the time-dependent functional.
The cutoff gradient, second derivative and all field/cutoff mixed entries
are saved; physical `Dc,D2c` remain uncomputed. Total physical derivatives
must add those chain terms, rather than interpreting the fixed-cutoff
partials as a completed derivative.

Numerical outputs at the actual saved background:

| Evaluated quantity | Value |
|---|---:|
| Full native0 Lorentz density | -0.9296234796937343 |
| Same-geometry mechanical-anchor density | -0.9313418844591831 |
| Source-relative density | +0.0017184047654488221 |
| Native0 common151 load maximum | 5.075445541323785 |
| Wall-gauge load maximum | 0.5980192618684432 |
| Higgs Re H2 load | -3.632506409790966e-5 |
| Fixed-wall radius stress partial | -0.22058948955178995 |
| Fixed-wall induced-lapse stress partial | -0.83738371052624 |
| Cutoff cotangent | +0.5710419824158771 |
| Cutoff second derivative | -1.1380996135556902 |
| Local-symbol geometry-rate contact maximum | 2.052597559458919e-4 |
| Local-symbol source-rate contact | -0.016804831687614555 |

The anchor sets independent fields and H to zero only inside its explicitly
evaluated bookkeeping branch at identical geometry, clock, domain and
cutoff. It selects no physical vacuum. Both the anchor and relative
component have been evaluated; the full actual component is consumed once.
Neither the anchor nor the classical residual supplies an inferred load.

The local-overlap accounting is essential. The retained sourced action
already contains original background-subtracted Maxwell and material
Higgs terms. Their matched subtraction is a full-dimensional/tower
operation. There is no canonical allocation of a fraction of those local
Wilson coefficients to this single angular block. A finite-block Taylor
moment is not the continuum local heat coefficient. The exact ledger is

\[
 \Gamma_{\mathrm{replacement}}=
 \Gamma_{0,\mathrm{actual}}+
 [\Gamma_{\mathrm{complement,domain,phase}}
 +\Gamma_{\mathrm{matched\ state}}-\Gamma_{\mathrm{retained\ local\ overlap}}].
\]

The bracket is **unevaluated**, not zero. This avoids adding the native
piece as an already disjoint physical force atop the local EFT. Matching
its reference contraction to the inherited state also remains necessary:
adding a complete occupation contraction separately could double the
native reference contribution. Any separate state correction must be a
matched difference derived from the same functional/domain. The adopted
polarization alone does not authorize an empty or filled sea, `C_plus` as
occupation, deletion of inherited correlations or fitting20 contractions.

At the unchanged saved fields the executed coupled equation is a partial
row assembly, `R_partial=R_known+dL0`, `J_partial=K_known+d2L0`. The saved
**moved-background** known two-jet is reused exactly. The old seed52
factorization is not used. No new minimization or coupled correction is
claimed.

| Original coordinate residual | Saved known subtotal | After adding native0 |
|---|---:|---:|
| Maximum of150 original rows | 258.64940382332156 | 258.46988194393947 |
| Held radial/wall32 maximum | 0.7195718466916636 | 1.3175911054024225 |
| Higgs4 maximum | 2.4291480209972893e-6 | 3.875421211890695e-5 |
| Multiplier component outside area direction | 27.63919050148927 | 27.63919050148927 |
| Active52 maximum | 6.931784795969269e-6 | 6.931784795969269e-6 |

The wall and Higgs rows worsen; the native contribution was not chosen to
cancel them. The intrinsic zero-wall52 native derivative and Hessian rows
vanish exactly, while their existing moved-background nonpass is retained.
The27.639 component still excludes repair by gamma alone. The complete
physical residual has no numerical value yet and is not identified with
either column of this table.

Original-factor checks give zero native real-product and temporal-vertex
defects. The continued-product defect is below `4.46e-16`; the original
Lorentz Hamiltonian coefficient is checked independently. Symmetric-frequency
trace defects are below `1.26e-15`, global gauge Ward contractions below
`1.80e-14`, and differentiated Ward contractions below `1.78e-13`.
These global checks do not erase the historical local gauge-reconstruction
nonpasses. The wrong re-daggered Hamiltonian-square product differs by
`1.43e-7` on these actual nonzero fields, so the distinction matters.

Frequency panels are `[0,.02,.1,.5,2,8]`, with24 Gauss points per panel
and a32-point comparison. Actual load151 differences reach `1.56e-13`;
actual Hessian151 differences reach `6.54e-11`. Anchor differences reach
`3.84e-13` and `1.42e-10`, respectively. These are quadrature comparison
defects, not rigorous total error bounds. Finite-input Gaussian tail
estimates for the actual value, full189 gradient norm and Hessian norm
are `4.46e-31`, `9.85e-27` and `2.02e-22`. Roundoff, physical cutoff,
continuum/angular/stratum completion, time/domain, inherited state, local
overlap and phase errors remain distinct. The existing membrane finite-step
`9.34e-8` and gauge reconstruction `7.29e-10/6.33e-10` limitations remain.

The physical-unit equation is still
`GF exp(2e)-cF[background,Cauchy incidence,normalized external legs]=0`.
It is not `dS/de=0`. The saved scale initializer, adopted500MeV beams,
100fm per-axis widths, centers at+-1000fm, exact pair statistics and
independent calibration are unchanged. Successive cap histories remain
distinct from the two incoming beams. No pair conversion, outgoing
occupation or magnetic readout is inferred from this native component;
no direct magnetic term is added a second time.

`NEXT_OPERAND`: bind the continued native component to the actual
incoming/event stratified domain and physical cutoff with `Dc,D2c`; consume
compatible complementary/phase/local-overlap and matched inherited-state
contractions at the same fields. Preserve the complete current pullback,
including both `(D C_current)n` and `C_current Dn`, when that state
application is available. Only after complete physical derivative admission
may a coupled correction and fresh original Maxwell/all226 checks precede
normalized magnetic readout, native completion, overlap subtraction and
uncertainty. This checkpoint does not claim any of those later results.
