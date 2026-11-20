# Complex pole derivative: native ownership and useful validation

Pinned source4a650a61a6e0e4cd3674650c399b435c106d66c3.
- muon_unsquared_pole_clock_matching.py::semisimple_pole_parameter_response already computes full H_a=−Z^-1 L Gamma_a R for2x2 spin frames, exporting traceless splitting separately. Inputs must already be same-retarded-domain physical pole/null frames. This algebra supplies no exterior or pole selection.
- muon_d5_finite_trace_pole_match.py uses a fixed charged trace section, not physical null vectors. Its scalar trace root does not establish a two-spin pole and physical_retarded_pole_or_charge_admitted=False.
- muon_normalized_seam_schur_jets.py differentiates full bare/full border with supplied value/x/y/xy jets for Kbulk,right B,left C,rho,M. Left trace is independently supplied, not guessed conjugate. This is a reusable differentiation engine, not a receiver constructor.
- muon_d5_pole_admissibility.py concerns regularity at the GEOMETRIC radial cap pole (Frobenius+1/−2), not an admitted muon resonance in energy. Do not confuse these two meanings of pole.

## Full exterior energy derivative
For Gamma(E,B)=Gamma_inner(E,B)+N_ext(E,B) in a correctly pulled-back common trace chart,
 Z=L[Gamma_inner,E+N_ext,E]R,
 T=L[Gamma_inner,B+N_ext,B]R.
For a simple pole E_B=−T/Z; for a semisimple two-spin pole branch slopes are eigenvalues of−Z^-1 T, not its trace alone. If exterior and interior share eliminated modes, differentiate the JOINT Schur operator instead. For Gamma=A−C Q^-1 B, Gamma_x=A_x−C_x Q^-1 B−C Q^-1 B_x+C Q^-1 Q_x Q^-1 B. All moving trace/constraint contacts remain included.

## One decisive reusable validation recipe
1. Require full original boundary/null residuals Gamma R and L Gamma small, Z nonsingular, same physical sheet/retarded domain, and isolated relevant pole cluster. A trace-center root alone does not pass.
2. Supply x=E,y=magnetic field into the existing four-jet border engine, including exterior frequency derivative and moving source maps. Verify differentiated original border rows, not merely internal algebraic identities.
3. Re-solve full boundary pole branches at ±epsilon B on the SAME sheet/domain and incident conditions; compare centered complex slopes to eigenvalues of−Z^-1 T over decreasing epsilon, with independent residual control. Never compare to separately fitted mass/width or determinant roots from a mismatched truncated domain.
4. Rechart equations Gamma'=U Gamma V with analytic invertible U,V. At exact nulls L'=L U^-1,R'=V^-1R, derivative terms containing Gamma vanish, so L'Gamma'_xR'=LGamma_xR for x=E,B. Test invariance to expose missing moving-trace terms or non-null selected states. Null-frame spin basis changes give similarity of−Z^-1T, preserving eigenvalues.

Under explicitly chosen exp(−iEt) convention, E_p=m−i width/2 and width_B=−2Im(E_B). Real slope measures energy shift; imaginary slope measures width change. A frequency-dependent exterior can affect both through Z, even if its explicit magnetic derivative vanishes. This is a conditional exact consequence, not an evaluated BHSM result.

Native common_pole_mass_width_clock_equations uses one positive clock kappa for mass and width together. Therefore width/mass=−2Im(E_p)/Re(E_p) is clock-independent. A failed width/mass test cannot be repaired by choosing separate lifetime units. This provides an additional validation once an actual pole exists; it does not select one from measured lifetime.

The saved weak-decay audit still finds action-owned family-diagonal charged currents and a phase-space integrator consuming amplitudes, not an evaluated same-domain physical decay kernel/pole. Its polarized angular integration limitation remains. No new physical exterior/pole admission found in this bounded source pass.

Primary sources:
https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/4a650a61a6e0e4cd3674650c399b435c106d66c3/src/bhsm/interface/muon_unsquared_pole_clock_matching.py
https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/4a650a61a6e0e4cd3674650c399b435c106d66c3/src/bhsm/interface/muon_normalized_seam_schur_jets.py
https://github.com/ncarberry64/Berger-Hopf-Standard-Model/blob/4a650a61a6e0e4cd3674650c399b435c106d66c3/src/bhsm/interface/muon_d5_finite_trace_pole_match.py
