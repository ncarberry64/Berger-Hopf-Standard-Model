# Same-domain gauge seam and M4 current ownership
Read-only audit, 2026-11-19. Main commit 551ce2c8e4e672538e520629b0d4a8962cbba968. No repository modifications.

## Result
The sources select an induced-action owner and exact variational/Schur architecture, but the inspected producers do not instantiate the nonzero-background, same-event M5/M8-to-M4 operator derivative needed to attach the native n0 spin-odd M4 current to the causal receiving region. This is a scoped audit, not a claim that every historical record has been searched.

## Primary equations and their status
1. [AE4 microscopic owner](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/551ce2c8e4e672538e520629b0d4a8962cbba968/src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py):
H_strat=H8 ⊕ H5+ ⊕ H5− ⊕ H4,
P_strat=D_strat† D_strat on the zero-mode/BRST quotient,
Gamma_ind=−(1/2) STr integral_[ell²,infinity] ds/s exp(−s P_strat), with relative zeta/eta logarithmic completion.
The M8/M5/M4 local actions are expansions of this ONE functional. The exact positive-order moments are F_p=−ell^(−p)/p. The global stratified domain and complete operator-valued Calderón–Wentzell seam are explicitly not constructed. This supersedes the old generic regulator-choice ambiguity, not the missing actual seam.

2. [Unified M5-to-M4 pushforward](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/551ce2c8e4e672538e520629b0d4a8962cbba968/src/bhsm/interface/aether_unified_m5_m4_pushforward_v15_69.py):
H5=diag(K_F^(5) Delta_Maxwell5,D5), with action-owned domains;
B=(Dirichlet trace, normal flux trace, normalized wall spinor trace), integral ds J |u0|²=1.
Gamma_boundary=−log integral_fixed_trace exp(−S5).
Gamma_tree=(K_F^(5)/2)<a,N_DtN a>−(1/(2K_F^(5)))<J,G_DtN J>.
K_A=delta_a² Gamma_boundary=K_F^(5) N_DtN+Pi_AA.
This is an exact required derivative ledger. The numerical finite_block_schur_witness uses H=((3,.4),(.4,2)) and is expressly NOT a physical coefficient prediction. It does not evaluate the actual current/exterior attachment.

3. [AE4 relative future domain](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/551ce2c8e4e672538e520629b0d4a8962cbba968/src/bhsm/interface/ae4_future_collapse_relative_boundary_domain.py) and [event assembly](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/551ce2c8e4e672538e520629b0d4a8962cbba968/src/bhsm/interface/ae4_c2_stratified_event_flux_assembly.py):
H_eff^R=H_pp−H_pc (H_cc^R)^−1 H_cp, omega→omega+i0.
Event KKT equations are H_pp q+H_pc c+C†lambda+J=0, H_cp q+H_cc^R c=0, Cq=d.
The assembly consumes supplied sector triples; it does not construct them from D_strat. Event parent/child H_pc is NOT automatically a stratum off-diagonal Pi4 D_strat iota5 or iota8. The birth/reset trace does not select outer quantum state.

4. [Geometric attachment](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/551ce2c8e4e672538e520629b0d4a8962cbba968/src/bhsm/interface/aether_diagonal_sp1_m4_attachment_v15_50.py):
S=A²+B², R4=AB/sqrt(S), L_F=sqrt(S);
omega=(A²/S)theta_u+(B²/S)theta_v;
F_omega=d(A²/S) wedge (theta_u−theta_v)−(A² B²/(2S²))[theta_u−theta_v,theta_u−theta_v].
K_F=(kappa1/2) Vol(S3_LF) S.
These fix actual quotient geometry and bulk connection normalization, not the full cross-stratum current incidence. Mechanical background curvature already belongs to parent R8.

5. [Earlier pushforward obstruction](https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/551ce2c8e4e672538e520629b0d4a8962cbba968/src/bhsm/interface/aether_m5_m4_gauge_higgs_ownership_v15_60.py):
For round quotient r=R_F sin chi cos chi,
I_E=int R_F r u² dchi, I_B=int R_F u²/r dchi.
Local Lorentz matching requires I_E=r_boundary² I_B.
For u=sin(2chi)^p, ratio=2p/(2p+1)<1.
Thus a smooth bulk profile cannot simply be relabeled as a local, equally normalized M4 gauge term. This is a round-quotient result, not a new no-go for the retained time-varying event. Later AE4 supplies a microscopic owner in principle, not numerical seam data.

## Smallest productive source-reached object
No need to construct every stratum matrix if the aim is one fixed-field spin-gap observable. Define on the SAME constrained domain:
- J_s: the already computed intrinsic n0 spin-odd source;
- I: the as-yet unevaluated variational incidence taking that intrinsic source into allowed bulk/seam loads;
- G_R: the full coupled retarded response with specified incoming preparation;
- r: an actual normalized exterior readout.

The minimal linear scalar is r† G_R I J_s. Equivalently solve the one adjoint problem G_R† r and evaluate <G_R† r,I J_s>. This is a conditional identity, not a new numerical result and not F2. The exact missing operand can be reduced to the action-owned directional contraction <z,I J_s> along that adjoint, rather than all entries of I.

For a physical magnetic derivative, differentiate the same scalar (including state/readout changes):
d_B[r† G I J]=(d_B r)†G I J−r†G(d_B L)G I J+r†G[(d_B I)J+I(d_B J)],
where G=L^−1 on the fixed compatible constrained domain. If the domain moves, its trace/contact terms belong in d_B L and d_B I; they cannot be discarded. The supplied event Schur algebra does not evaluate those terms.

Practical next test: recover or derive only the directional mixed variation of the AE4 functional along the native n0 current and the receiving adjoint, with common geometric L2 weights, opposite-normal fluxes and BRST constraints. The resolved material cut has continuous gauge trace and flux without an added sheet. Any nonzero jump assigned to the intrinsic M4 current must therefore be justified by the induced seam/source variation rather than inserted by hand. A causal pulse on a smooth collar can show receiver sensitivity, but cannot itself establish I.

## Claims preserved
No physical magnetic moment, no numerical cross-stratum coupling, no source-free receiving state, and no arbitrary surface term have been selected by this audit. The no-added-contact material-cut condition does not erase the M4 sector of the selected stratified functional.

