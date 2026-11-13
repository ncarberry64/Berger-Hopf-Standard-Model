# Source-reached cut diagonals and moving complement

Starting revision: `9425d997258a39f9d06ad95a32f7edf0eebe0684`.
Scientific reference: `524ed90689bd5923c249bba2e699abf627e703cd`.
This continuation uses the unchanged endpoint packet. No endpoint extraction,
old replay, normalization refinement, covariance test, or physical calibration
was repeated. The publication checkout was clean at entry; the primary live
checkout and its caches were untouched.

The new result is a **cut Dirac form**, including its diagonal, mixed and
connected-complement actions on actual retained sources. It is neither an
exterior stationary solution nor a physical muon anomaly. The coupled
assembly stops at a specified non-cut weak action, documented below.

## Evaluated actions and pairings

The source is the original `b`-coordinate insertion applied to the saved four
input spin coordinates: `p_Ac=(T_b chi_hat/r) Xi_A e_c`. Both n1/n3 sectors and
all 64 output Spin4 x SM16 coordinates are retained. Family identity remains
symbolic; there is no extra family, mode or action-index multiplier. The
independent photon source, common-A, spin and radial daughter-eta insertions
are unchanged. No precursor, static wall profile or new coupling was used.

The 32 supplied source columns have a separated **numerical** Haar image of
rank12. The retained eigenvalues are approximately 8/9, 4/3 and 16/9, each
fourfold; the largest discarded absolute eigenvalue is 9.26e-16. The map S
obeys `S^dagger G_Xi S=I` to 2.54e-15 in Frobenius norm. This quotient is a
computational source image, not the physical muon state or the whole exterior
trial space. No diagonal regularizer was introduced.

Additional full-cap second moments were evaluated over all 64 radial cells
with 8-point Gauss quadrature per cell. Spatial nodal interfaces remain
explicit. The retained instantaneous norm, source overlaps and volume Gram
certificates were reused. The endpoint action coefficients were evaluated
only on this cut, including direct Fourier L_nu, correlated C_tau/r_tau,
the action I_tau and inherited H. They were not extended constantly in time.

With `X=(W,p)`, save F=(D5 W,D5 p,iGamma0 W/nu,iGamma0 p/nu) and

    K_jet = integral_cap mu5 F^dagger F d rho,
    mu5 = 2 pi^2 nu C r^3,
    muSigma = 2 pi^2 C r^3.

The amplitude volume Gram is

    M_Wp = [[M4 I,T I],[T I,Mpp]],

where Mpp is the already-certified saved-source Gram in the quotient. The
temporal-Cauchy Gram uses G_Sigma and T_Sigma, with its own source diagonal.
Spin boosts have not been treated as Euclidean-unitary: these calculations
use the existing common-frame component pairing and its actual geometric
densities. Domain and cross-stratum terms have not been inferred from this
local positive square, nor was the Lorentz radial sign changed.

The differentiated bulk projection is evaluated as

    B = T/M4,
    B_tau = (T_tau - M4_tau B)/M4,
    chi = p - W B,
    D5 chi = D5 p - (D5 W) B - iGamma0 W B_tau/nu.

At the retained endpoint, in the retained proper tau coordinate:

| Quantity | Numerical cut result |
|---|---:|
| B_bulk | 0.024957654923079987 |
| B_bulk,tau | 8.940201733019005e10 |
| B_Sigma | 0.02560781115039166 |
| B_Sigma,tau | -2.623493418170599e10 |
| norm K_WW | 2.7729650038638504e26 |
| norm K_Wp | 3.861399940821987e13 |
| norm K_pp | 204.19422029061457 |
| norm K_chichi | 3.928153262992277e23 |

These are model-scoped form values, not physical units of magnetic moment,
operator bounds or anomaly uncertainties. B_bulk uses the volume pairing;
its complement is not Cauchy-orthogonal. The volume W/chi cross Gram norm is
1.93e-16 while its Cauchy cross Gram norm is 0.048564341805514666.

The material trace multiplier remains the inherited normalized radial value.
For the evaluated compact source, chi_wall=-B W_wall is nonzero. The full
sum B W_wall+chi_wall vanishes, as the original source does. An independently
zero complement trace, zero conormal, or reset range invariance was not imposed.
The global event/child trace arrays and stationary response remain unevaluated.

## Actual source application and cancellation

The first nonzero original column, A=0/input spin0, is used without a spectrum
or anomaly-based selection. Its **amplitude/time-jet form cotangent** and cut
source pairing are saved as `rhs_K` and `rhs_M`. In particular

    q_cut(p,p) = integral_cap mu5 (D5p)^dagger D5p d rho
               = 33.099937169683294,
    m_cut(p,p) = 0.052910303260018214.

The direct full-output energy agrees with its weak cotangent contraction.
This is not an evaluated P_strat p. Temporal integration by parts would also
consume the derivative of the velocity cotangent and the owned conormals:

    K_AA X + K_A,t X_tau
      - partial_tau(K_t,A X + K_t,t X_tau),

with the complete domain and additional owned contributions.

The moving-complement jet is converted algebraically before form application:

    (a,c,a_tau,c_tau) ->
      (a-Bc,c,a_tau-B_tau c-B c_tau,c_tau).

For the original source `(a,c,a_tau,c_tau)=(B c,c,B_tau c,0)` this is exactly
`(0,c,0,0)`. The code applies the known Dp in those coordinates. Omitting
B_tau changes the reached action by a volume-weighted norm approximately
3.6313671389720654e11. Summing the large already-evaluated Dchi/DW terms in
binary64 produces a 1.3372e-5 weighted error even though the algebra cancels.
The stored K_chichi is therefore not used to reconstruct the small source
value by subtraction of quadratic forms. Neither matrix inversion nor heat
of this cut matrix was performed.

## Assembly stop and the one next action

The first missing block consumed by the coupled weak solve is

    (K_ext,chichi+s M_ext,chichi)_ij
      = integral_Iext <D5 v_chi,i,D5 chi_j>_5 d tau
        + s integral_Iext <v_chi,i,chi_j>_5 d tau
        + owned interface/seam/domain terms.

Its immediately needed temporal coefficient at non-cut source-reached points is

    a0(tau,rho) = [-I_tau/(2I)-L_nu/2+3H/2+C_tau/(2C)
      -zeta C_rho/(2C)-zeta_rho/2+zeta nu_rho/(2nu)
      -zeta cot(rho/2)/2]/nu.

The non-cut L_nu must use rows74:86 of the SAME current action field,

    Y_tau = W_Y^-1(b_psi Psi_w+sigma V_w)/(N_b sigma),
    L_nu = sum_k Y_tau[74+k-1] (cos(2k rho)-(-1)^k),

with q_tau=v/N_b for the other metric and normalization derivatives. The
shared Delta cancels before numerical enclosure. The endpoint packet contains
these cut actions; the geometry cache contains 48 nodal geometry snapshots,
not the corresponding non-cut owned action-jet family. Its first right-cell
reconstruction cannot be identified with the very large action lapse rate.

Producer: the retained v14.45 Dirac action and same common-A/radial-eta
realization; cancellation-preserving selected-field actions from
`audit_n12_c2_exact_center_fixed_s_field_matrix.py`, with the proper-clock
prescription in `certify_n12_c2_cancelled_field_lohner_step.py`. Only their
first actions required at the consumed history points are needed, not the
98-direction derivative campaign. The input/output is the source-reached
connected form-domain section and its dual weak functional.

Consumer: `(K_ext+s M_ext)u=p`, including total fields in the AE2 graph

    Gamma0_child(W_child psi_child+chi_child)
      = U_R Gamma0_event(W_event psi_event+chi_event),

and material matching, inherited step1222 past prefix and future canonical
stop, followed by `Gamma1^owner u` and the stratified fermion-family retarded
block. `assemble_stratified_direct_sum`/`solve_retarded_event_kkt` consume
supplied actions; they do not supply this history action. The assembly attempt
records its exact stop before inversion. Solution, stationary residual and
conormal output remain null. This is an uncomputed prescribed action/domain
realization, not a newly unspecified physical parameter or boundary law.

## Error scope and delivery

A single 4/8-point per-cell comparison was made for the NEW second moments.
The source energy difference is 9.24e-14; the full jet-form difference is
9.954e12, relative 3.590e-14. The latter is dominated by large inclusion
terms. Neither is a rigorous quadrature bound. The new full-cap action
builder agrees with stored source-support Dp arrays to 2.40e-16 relative,
and DW arrays to 2.29e-16 relative; the absolute DW discrepancy reaches
0.02865. These are comparisons, not certified arithmetic residual bounds.

Endpoint point/tube uncertainty, direct/nodal interpolation differences,
matrix roundoff, weak quadrature, history reconstruction, continuum and
interface/domain errors are separately retained. The previous endpoint
certificate was not extended to the new quadratic forms. Higgs/seam,
connected exterior propagation, grading/BRST, finite-E1 length/completion
and physical native anomaly terms remain explicitly unevaluated.

Five targeted checks of these NEW saved forms passed. They cover source-image
coverage, distinct pairings, full material trace, direct full-output/form
agreement, and refusal to substitute the cut block for the missing history
action. They are not old endpoint checks or physical-operator evaluations.
The first run passed four and failed an exact-floating-zero assertion on the
material trace sum (maximum component 3.47e-18). The assertion was corrected
to a two-epsilon relative rounding check; only that check was rerun and passed.
No scientific array changed. The focused rerun disabled the repository-wide
conftest snapshot because these checks only read the saved new arrays.

Evidence: `artifacts/muon_coupled_cut_forms_20261004`, mirrored in
`C:\Users\carbe\Downloads\BHSM_muon_coupled_cut_forms_20261004`.
`run_1` preserves the evaluated fields/diagonals; `run_2` derives small
complement blocks from that cache. Executed source snapshots and hashes are
retained. `semantic_scope.json` corrects two initial report labels without
rerunning or overwriting those arrays: rhs_K is a jet cotangent, and q_cut
is not the temporal-integrated D^dagger D pairing. Current replay code uses
those corrected labels. The exact working diff/publication revision and
standalone reproduction scripts are included.

Reproduce only this new work in unused directories:

```powershell
python scripts/replay_muon_coupled_cut_forms.py --output <new-run1>
python scripts/extend_muon_coupled_cut_forms_receipt.py --source <new-run1> --output <new-run2>
python -m pytest --noconftest -q tests/test_muon_coupled_cut_forms.py
```

Frozen locals remain a_QED=0.00116550200495813, calibration-only standard
uncertainty1.79e-13 under its original alpha convention, and the already
combined selected-local interval (0.0011655039493,0.0011655109506).
They were neither recalculated nor added again. Physical a_mu and
g_mu=2(1+a_mu) remain unevaluated; no experimental anomaly was consulted.
