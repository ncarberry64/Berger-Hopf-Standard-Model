# Gate 7 readout-symbol provenance correction

Status:
`READOUT_SYMBOL_PROVENANCE_CLOSED_NATIVE_SPECTRAL_CONSTRUCTION_OPEN`.

This correction does not change Gate 7. It closes the prerequisite question
of what the inherited symbols (p), (p^2), (K_A(p)), (a_T), (a_i),
“residue,” and “pole” actually mean after the periodic cycle is retired.

## Exact lineage

The v15.60 action ledger first uses (Z_g) as a target coefficient in a local
(M_4) gauge action, while explicitly saying that the parent/child action has
not selected it. V15.61 supplies the geometric scale
(mu_star=1/R_4=2/R_F), but explicitly does not select the absolute (M_4)
normalization or finite local counterterm.

V15.65--68 derive static spatial Dirichlet-to-Neumann operators:

\[
 \mathcal N_T=(\Delta^{\mathrm{coexact}}_1)^{1/2},\qquad
 \mathcal N_0=\Omega-\frac{\Omega^{-1}}{R_4^2}.
\]

These are action-native spatial spectral operators. They are not a local
Lorentzian Maxwell operator and do not define an external four-momentum.

V15.69 is the first occurrence of the advertised formula

\[
 Z_g=\left.\partial_{p^2}\langle a_T,K_A(p)a_T\rangle
 \right|_{p^2=\mu_\star^2}.
\]

Its implementation stores that formula as a string. No function accepts
(p) or (p^2), and the focused test checks only that the string starts with
`Z_g=`. The same artifact says that the absolute local gauge residue and the
common subtraction remain underived. V15.72--75 reuse the formula at modeled
crossings but still construct neither (K_A(p)) nor a normalized source
family (a_i(p)).

V15.78--86 replace the readout by derivatives of a one-period functional.
V15.89 then explicitly refuses to identify the resulting DtN form factor with
a local zero-momentum coupling. V15.90 says that the dynamic
(omega^2) response and the Lorentzian (F_{\mu\nu}F^{\mu\nu}) coefficient
remain open; v15.91--92 retain the same Lorentz/frequency gap. V15.96 supplies
the first common numerical gauge/ghost/Weyl/HS operator, but its domain is
(L^2(S^1_\tau\times S^3)) with periodic event gluing. V15.99 supplies the
abstract pair-plus-contact Fréchet Hessian while leaving the physical
radial-angular source matrices and the quantum saddle open.

The current N12 lineage owns a maximal-forward Friedrichs/reset domain, not a
periodic (S^1) domain. It supplies no retained translation generator,
asymptotic measurement region, or physical map from the forward operator to
four-momentum.

## Required classification

The inherited advertised (p^2) is classified exactly as:

`D_RETIRED_PERIODIC_FOURIER_ARTIFACT`.

This classification has a precise caveat. The text symbol itself first
appears in v15.69 as an imported low-momentum QFT convention. Its only
domain-level lineage is the later periodic (S^1) construction, and no
physical meaning survives its retirement. Therefore it is not action-native
(A), not an asymptotic readout (B), and not yet the spectral coordinate of the
true forward operator (C).

The native spectral parameter (z) is a class-C object, but it is a different
object. No theorem currently identifies (z) with (p^2).

## Symbol distinctions

The letter (p) is overloaded in the historical record. The v15.60 integer
profile exponent, the v15.78 event-law exponent, and the v15.92 radial
Sturm--Liouville coefficient are unrelated to the undefined external argument
of (K_A(p)).

The gauge “residue” is a formal derivative coefficient, not a proved
propagator-pole residue. The Yukawa/Higgs residue is a projection and canonical
field rescaling. The v15.67 pole is a UV Laurent pole whose local operator is
(H^\dagger H). Other “pole” uses are geometric collapse endpoints. No
physical gauge-particle pole is derived, and pole language is not a native
Gate-7 dependency.

The action owns the coexact/BRST physical source space, but it does not own a
plane-wave or (p)-indexed normalized source family. The weakest sufficient
source object is an admissible supplied section
(a_i\in\mathcal H_{\mathrm{BRST}}^{\mathrm{phys}}).

## Native replacement and downstream dependencies

Let (K_C) be the self-adjoint operator represented by the retained closed
form on the actual maximal-forward BRST domain. The next native objects are

\[
 R_C(z)=(K_C-z)^{-1},\qquad
 K_C=\int \lambda\,dE_C(\lambda),
\]

and, for supplied admissible sources,

\[
 H_{ij}(z)=\langle a_i,R_C(z)a_j\rangle+H^{\mathrm{contact}}_{ij}(z),
\]

or the exact retained heat-Fréchet equivalent. Exterior dependence must be
compressed into the action-owned Weyl--Calderón response (M_C(z)). The
parameter (z) must not be called momentum squared.

The remaining Gate-7 order is therefore: construct the resolvent/spectral
measure; assemble admissible gauge/ghost/rank-16/HS incidence without a
(p)-label; derive or enclose (M_C(z)); evaluate the zero-source force;
certify the same-action saddle; evaluate the pair-plus-contact Hessian; close
Ward/BRST and continuum/relative-trace control; and finally derive an
action-owned, basis-independent scalar observable map or reclassify the
scalar-coupling claim.

One terminal-reaching history remains an existence-only finite-endpoint
route. Universal terminal reachability is neither required nor derived.
Gate 7 stays open, Gate 8 stays locked, chord 3 stays unauthorized, frozen
predictions are unchanged, and no physics is added.
