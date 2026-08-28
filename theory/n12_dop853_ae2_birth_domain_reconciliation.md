# N12 DOP853 / AE2 birth-domain reconciliation

The adaptive DOP853 construction does not choose a normal-matter
self-adjoint extension.  Its bordered matrix is

\[
 K_{\rm border}=\begin{pmatrix}
 H_{\rm red}-\lambda_{24}I & \psi_{24}\\
 \psi_{24}^{T} & 0
 \end{pmatrix}\quad\hbox{on }\mathbb R^{62},
\]

where `H_red` is the 61-dimensional velocity/multiplier block of the exact
local-action Hessian.  The response right-hand side is assembled from the
same local action gradient and mixed Hessian.  No temporal trace space,
`Gamma0`, `Gamma1`, Cayley phase, Robin datum, or event/child Calderon graph
occurs in this matrix problem.  Consequently it is valid auxiliary geometry
data, but it is not the Gate-7 normal-matter seam operator.

The repository has two deliberately distinct action-version statements.

1. For the unchanged retained v6.7 action, the canonical no-go remains exact.
   Its zero normal-matter junction action leaves a non-gauge
   `U(1)_parent x U(1)_child` domain family, and the compact-source resolvent
   witness separates allowed members.  The DOP853 calculation does not
   supersede this result.
2. `BHSM-AE-2.0.0` is an already explicit, owner-selected action/domain
   version.  Its configuration space consists of sections of one reset-glued
   `Spin x G_SM` bundle, with

   \[
   \Gamma_{0,c}\Psi=U_R\Gamma_{0,e}\Psi,\qquad
   \Gamma_{1,c}\Psi=-U_R\Gamma_{1,e}\Psi
   \quad\hbox{on }\operatorname{Dom}(D_{\rm AE2}^{2}).
   \]

   The unitary transmission graph is maximal isotropic.  The old resolvent
   witness remains a valid proof that alternate phase domains define
   inequivalent theories; those alternatives are not members of the single
   AE2 configuration space.  Thus the old no-go is superseded only for the
   explicitly changed action version, never retracted for v6.7.

Phase B is therefore outcome B1 for the already owner-selected AE2 lineage.
This does not close Gate 7.  The DOP853 state/projector/response tubes must be
composed with the AE2 two-sided event/child Calderon seam, and the complete
heat-minus-zeta quotient covector must still be evaluated.  Under the
unchanged v6.7 lineage alone, outcome B2 remains terminal with the smallest
blocker

`UNCHANGED_RETAINED_ACTION_DOES_NOT_SELECT_A_UNIQUE_NORMAL_MATTER_BIRTH_DOMAIN_REQUIRED_BY_GATE_7`.

No phase, coefficient, scale, source, gate, or action term is introduced by
this reconciliation.
