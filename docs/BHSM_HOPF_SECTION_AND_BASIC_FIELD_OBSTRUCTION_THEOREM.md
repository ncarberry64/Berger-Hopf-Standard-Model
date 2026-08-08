# BHSM v14.30 Hopf-section and basic-field obstruction theorem

## Theorem

For the retained quaternionic Hopf reduction

\[
\operatorname{Sp}(1)\longrightarrow S^7\xrightarrow{p_H}S^4,
\qquad c_2(p_H)=+1,
\]

there is no global section over the full \(S^4\) base. A section of a
principal bundle trivializes it, while principal \(\operatorname{Sp}(1)\)
bundles over \(S^4\) are classified by \(c_2\in H^4(S^4;\mathbb Z)\). Hence
\(p_H\circ\iota=\mathrm{id}_{S^4}\) would imply \(c_2=0\), a contradiction.

The equatorial collar restriction is different. It is trivializable and has
local or collar-global sections, but v7.1 selects none. Such sections are gauge
choices and cannot extend over the full base. A representative in one
trivialization is not a global reduction theorem.

## Non-basic eta theorem

If the parent texture \(\eta:S^7\to S^7\) were basic, then
\(\mathcal L_V\eta=0\) for every vertical Hopf vector and
\(\eta=\bar\eta\circ p_H\) for a map \(\bar\eta:S^4\to S^7\). Since
\(\pi_4(S^7)=0\), this factorization is null-homotopic and has degree zero.
The retained degree-one sector is therefore non-basic. This conclusion does
not require a coordinate expression for \(\mathcal L_V\eta\).

Normalized averaging cannot preserve its action. For
\(X=|D\eta|^2\), the parent term requires \(\int_FX^4d\nu_F\), whereas a
zero-mode action would use \((\int_FX d\nu_F)^4\). The exact witness
\(X=(1,3)\) gives \(41\neq16\). Vertical energy, topology, and nonlinear
Clebsch--Gordan mode products must be retained.

## Status

- Global full-base section obstruction: `VALIDATED`.
- Collar trivializations: `VALIDATED`, but not action-selected.
- Degree-one non-basic theorem: `VALIDATED`.
- Simple normalized fiber averaging: `INVALIDATED`.
- Full Hopf preimage \(\widetilde C_\eta=p^{-1}(C_5)\): required replacement
  domain.

This theorem remains valid independently of the later effective-action result.
