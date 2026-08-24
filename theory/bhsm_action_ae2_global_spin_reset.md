# BHSM-AE-2.0.0 global-spin reset action/domain

Decision type: `OWNER_AUTHORIZED_THEORY_VERSION_DECISION`.

This is a new BHSM action/domain version. It does not retract the theorem that
the unchanged retained action fails to select the normal-matter domain.

## Selected geometry

The last regular event trace and first regular child trace are glued by

\[
 U_R=\rho(\operatorname{SpinLift}\Lambda_R)\otimes G_R,
\]

where `Lambda_R` is the oriented reset coframe map and `G_R` is the returned
SM-bundle isomorphism. The pregeometric core still carries no metric, proper
time, spinor trace, or continuous flux. The extension acts only between the
two regular boundary traces.

The exact action is the retained canonically normalized Dirac action on
sections of the glued bundle:

\[
 S_F^{\rm AE2}=\frac12\int_{M_e\cup_R M_c}
 \left(\bar\Psi iD\Psi-\overline{iD\Psi}\,\Psi\right)d\mu,
 \qquad S_{\Sigma,F}^{\rm AE2}=0.
\]

The zero surface term is action-owned in AE2: the reset locus is an internal
glue of one global field domain and carries no delta-supported matter density.

## Variation and domain

Admissible fields and variations obey

\[
 \Gamma_{0,c}\Psi=U_R\Gamma_{0,e}\Psi,
 \qquad
 \Gamma_{0,c}\delta\Psi=U_R\Gamma_{0,e}\delta\Psi.
\]

Opposite boundary orientations give

\[
 J_c=-U_RJ_eU_R^\dagger,
\]

so the two Green forms cancel. This proves self-adjointness of the first-order
Dirac operator on the transmission trace domain.

Gate 7 uses the squared/Calderon operator. Its domain is

\[
 \operatorname{Dom}(D_{\rm AE2}^2)
 =\{\Psi\in\operatorname{Dom}(D_{\rm AE2}):
 D_{\rm AE2}\Psi\in\operatorname{Dom}(D_{\rm AE2})\}.
\]

Applying the same transmission law to `D Psi` gives the corresponding
opposite-conormal relation

\[
 \Gamma_{1,c}\Psi=-U_R\Gamma_{1,e}\Psi.
\]

The graph of a unitary `U_R` is half-dimensional and maximal isotropic;
therefore the glued Dirac operator is self-adjoint on the complete physical
transmission domain.

The old `U(1)_parent x U(1)_child` family belonged to two independent
terminal-domain choices. AE2 has one global section and hence no independent
Cayley phase. A common gauge-frame change and the global spin sign remain,
but neither is a relative self-adjoint extension parameter.

Matched BRST generators satisfy

\[
 c_c=U_Rc_eU_R^\dagger,
\]

which preserves the trace constraint. No gauge/ghost sector is deleted or
retuned.

## Gate-7 consequence

For AE2, the independent local fermion attachment block is exactly zero. The
existing transverse gauge DtN block remains nonzero and unchanged, and the
resolved scalar/geometry flux law remains in force. There is no double
counting.

This closes action ownership of the fermion birth domain, but not Gate 7. The
next theorem is to assemble or enclose the nonzero two-sided event and child
Calderon maps and prove a strict zero-energy matrix Wronskian margin. Only
then can the already-assembled local source incidence be used to evaluate the
zero-source weak geometry force.

Frozen predictions are unchanged. Gate 7 remains active, Gate 8 remains
locked, chord 3 is not authorized, and `FULL_BHSM_COMPLETE = FALSE`.
