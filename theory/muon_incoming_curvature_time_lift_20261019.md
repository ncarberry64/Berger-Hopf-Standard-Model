# Pointwise comparison time lift and the charge contact requiring dressing

This application fixes the represented U(2) lift of the stipulated proper
material clock on the saved stationary comparison component and evaluates
the nonzero one-body charge contact which its coupled dressing equations
must consume. It does not produce physical incoming packet data. In
particular, neither `d_in` nor `Psi_prepared|Sigma(t0)` has been assigned.
The adopted conditional stationary-past incoming prescription and collider
preparation remain unchanged.

The exact input is `input_iterate151`, `actual_theta` and
`actual_theta_gradient` in
`artifacts/muon_stationary_native_reference_load_20261019/run_5/native_reference_load.npz`
(SHA256 `1663a7d19350412cae236345974e9c48f07ace8f54b29752bd5e2956a8221753`).
The iterate matches the completed coupled replacement bitwise. The
preparation hash is
`dcc4ad850ea38dcd405637d24b306efe8789ab08e144f559d7cc294cd72e8f0f`.
The comparison has 22 intrinsic coefficients: radius, induced lapse,
four temporal connection coefficients, twelve spatial connection
coefficients and four real Higgs components. Its source is their saved
complete pullback to the declared 151-coordinate stationary family.

## Versioned correction to the constant-compensator argument

`COMPARISON_TIME_LIFT_v1` evaluated the constant-compensator restriction
`[A_mu,lambda]=0`, `lambda_H H=0`. Its rank four excludes only a spatially
constant compensator. Covariantly parallel, spatially varying
compensators require a separate argument. All v1 arrays, numerical
results and the exact executed owner snapshot remain historical evidence.
The active v1 source now labels that restricted proof scope explicitly.

For the stationary coefficient comparison and its stipulated proper
material observer

\[
 K=\ell^{-1}\partial_t,
 \qquad \mathcal L_K A-D_A\lambda=0,
 \qquad \mathcal L_K H+\lambda_HH=0,
\]

ordinary Lie derivatives vanish. The original symmetry equations therefore
require `D_A lambda=0` and `lambda_H H=0`. Without imposing any spatial
constancy on `lambda`, integrability implies

\[
 [F_{\mu\nu},\lambda]=0,
 \qquad \lambda_H H=0.
 \tag{1}
\]

The unit-Tr16 generators are the existing anti-Hermitian Higgs
representation, with `[H_a,H_b]=epsilon_abc H_c/sqrt(2)`.
The original right-body frame obeys `[E_i,E_j]=-2 epsilon_ijk E_k`.
With `A_i` the unit-S3 one-form components and `A_0=A_t/ell`, the proper
frame curvature is

\[
 F_{0i}=\frac{[A_0,A_i]}{R},\qquad
 F_{ij}=\frac{2\epsilon_{ijk}A_k+[A_i,A_j]}{R^2}.
 \tag{2}
\]

The linear Maurer-Cartan term includes the central connection. It cannot
be replaced by a matrix commutator alone. These normalizations agree with
`muon_parent_maxwell_background_euler._bracket/_curl_linear` and the
original right-Maurer spin-coframe convention.

The executed real matrix for (1) has 52 rows and four real U(2)
coefficients. Its singular values are

`[0.8632388628306662, 0.851981796833088, 0.8519817967987628, 0.26075580990341585]`.

Four original component rows, indices `[51,24,50,13]`, form the square
pivot with condition number `3.0273665285133515`. Pointwise rank four
forces `lambda=0`. A covariantly parallel section vanishing at one point
vanishes on its connected component; zero also satisfies all the original
symmetry equations. This conclusion excludes nonconstant parallel U(2)
compensators for this component. It does not infer full interacting
background stationarity or identify the physical preparation clock.

The saved derivatives retain the radius and lapse contributions in (2):

\[
 \begin{aligned}
 \delta F_{0i}&=\frac{[\delta A_0,A_i]+[A_0,\delta A_i]}R
                     -F_{0i}\frac{\delta R}R,\\
 \delta F_{ij}&=\frac{2\epsilon_{ijk}\delta A_k+
             [\delta A_i,A_j]+[A_i,\delta A_j]}{R^2}
                     -2F_{ij}\frac{\delta R}R,\\
 \delta A_0&=\frac{\delta A_t}{\ell}
                     -A_t\frac{\delta\ell}{\ell^2}.
 \end{aligned}
\]

If `C` denotes (1), its source equation is
`C Dlambda+(DC)lambda=0`; the same square pivot yields
`Dlambda=0` throughout this declared stationary coefficient family.
Actual nonstationary Lie-time sources are not supplied by this identity.

A regression checks the missing distinction: for the flat pure-gauge
right-body connection `Ai=-sqrt(8) H_i`, the old constant-class matrix has
rank four but (1) has rank three and retains the Higgs stabilizer. The new
routine preserves that unresolved one-dimensional pointwise family.

## The actual charge-stationarity application

The causal generator remains the original proper-clock operator

\[
 h=W-i\Omega,\quad
 W=-\frac{i\alpha^i(E_i+A_i)}R
      +\frac{3\gamma_5}{2R}+M_Y(H).
\]

The positive-current variable is `chi=R^(3/2) psi`. Its constant-Haar
component has the complete Cauchy Gram, with physical constant section
`I18/sqrt(2 pi^2 R^3)`. These statements concern the retained constant
right-body scalar harmonic times the full eighteen-component fiber, not
the full collar/collider Cauchy space or a complete lowest Dirac shell.

The existing exact six-dimensional electron-family block is retained,
including its neutral component. No charged four-dimensional projector is
imposed as an invariant incoming space. Let

\[
 P_H=\frac{HH^\dagger}{H^\dagger H},\qquad
 Q_H|_L=-P_H\otimes I,\qquad Q_H|_{e_R}=-I.
\]

The exact original one-body charge contact is

\[
 \mathcal E_Q
 =\partial_\tau Q_H+i[h,Q_H]
 =D_\tau Q_H+i[W,Q_H],
 \qquad D_\tau Q_H=\partial_\tau Q_H+[\Omega,Q_H].
 \tag{3}
\]

On this stationary coefficient comparison only, ordinary
`partial_tau Q_H=0`. Its covariant rate is retained:
`D_tau H=Omega_H H` and `D_tau Q_H=[Omega,Q_H]`.
Adding `D_tau Q_H+i[h,Q_H]` would count the temporal connection twice.
The 151 source placements actually executed are

\[
 \delta\mathcal E_Q=[\delta\Omega,Q_H]+[\Omega,\delta Q_H]
                +i[\delta W,Q_H]+i[W,\delta Q_H].
 \tag{4}
\]

The evaluated maximum component norms are:

| Original quantity | Maximum absolute component |
| --- | ---: |
| `D_tau H` | `7.77235626185852e-9` |
| `D_tau Q_H` | `1.9975363994438342e-13` |
| `E_Q` | `1.0526790664568093` |
| full151 `D E_Q` | `2.089511066807966` |
| covariance of the Higgs-derived charge rate | `6.310887241768095e-30` |
| equality of the two original forms of (3) | `2.524354896707238e-29` |
| equality of their full151 source forms | `1.1102230246251565e-16` |

The nonzero contact is a concrete same-background operator contribution
for the coupled gauge/Higgs charge and dressed transition. A bare charged
fiber alone is not reducing here. This result does not prove that the
adopted selector fails or is nonunique, and does not choose a dressed
charge by diagonalizing away the mixing.

The v1 causal coefficients, sign-sector matrices, their Sylvester source
and all 24 current-vertex operator blocks were reused **bitwise**, without
a new native calculation or spectrum. Their current blocks are operator
maps, not an occupation, state expectation or an interacting pair-conversion
amplitude. No electron-to-muon transport or physical homogeneous
coefficient assignment occurs.

## Checkpoint and remaining operand

New owner: `muon_incoming_curvature_time_lift.py`, executed SHA256
`c0415f5649d7bc5d06259d976932305e9a1521d3e3cbaf21fbdba639886278c0`.
External checkpoint:
`BHSM_CAUSAL_DATA_20261019/COMPARISON_TIME_LIFT_v2/application.npz`, SHA256
`8b509b08a66680d7e04ffd327b149186bcdd40325bb855e752657d0879f13381`.
The original integrability rows and their source equations are zero to
finite arithmetic. The six focused v1/v2 tests pass, including the flat
pure-gauge counterexample, original frame/source finite variations and
all charge-clock derivative placements.

`NEXT_OPERAND`: consume (3)-(4) with the same-background prepared
Gauss/dressing equations, then construct the same-domain physical
collider/Cauchy incidence and the prepared interacting mode amplitudes.
The complete full-cap/collar extension, localized normal normalization,
stationary-past extension and scattering boundary range remain distinct
obligations. No source or occupation has been chosen to cancel a wall
residual. Physical `d_in`, initial Cauchy data and packet sections remain
unset. There is no physical admission or continuum bound; the unchanged
criterion is `2e-10`. All prior bulk, source, event, native and physical-unit
nonpasses, beam preparation, independent calibration and once-only local
subtraction remain intact.
