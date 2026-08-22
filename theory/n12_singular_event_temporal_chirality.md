# Singular ordered-event temporal chirality

Status: **the retained action supplies a one-sided hitting orientation, but the
event-to-child equations do not select its sign and formal reflection is not a
quotient**.

## 1. Why the ordinary event derivative is not defined

Write (z=(v,\ell,s)) for the velocity, lapse-multiplier, and shift variables.
The retained Euler--Dirac equation used by the child evolution is

\[
 D(Y)\dot z=b(Y),\qquad
 D=L_{zz},\qquad
 b=\binom{L_q-L_{vq}v}{-L_{(\ell,s)q}v}.
\]

The existing ordered event is precisely a simple zero eigenvalue of this same
Dirac block:

\[
 D(E)\psi(E)=0.
\]

Consequently the unbordered solve defining the regular Euler--Dirac vector
field is unavailable at (E).  The formerly used expression
(D e_{\rm ord}(E)V(E)) is therefore not a finite event invariant unless an
additional Fredholm-compatible or bordered event dynamics has first been
derived.  No such time-dynamics border exists in the retained implementation.
The existing Calderón bordered solves concern boundary matching and do not
supply it.

## 2. Action-owned one-sided hitting invariant

Let (\lambda=e_{\rm ord}), let (\psi) be its normalized simple eigenvector,
and define

\[
 b_\psi=\langle\psi,b\rangle,
 \qquad
 c_\psi=D^3L[(0,\psi),(0,\psi),(0,\psi)].
\]

On the regular side (\lambda\ne0), the soft component of the Euler--Dirac
solve is (\langle\psi,\dot z\rangle=b_\psi/\lambda).  If the hard inverse,
coefficients, and simple eigenline have one-sided limits, standard eigenvalue
perturbation gives

\[
 \lambda\dot\lambda\longrightarrow c_\psi b_\psi,
 \qquad
 \frac{d}{dt}\lambda^2\longrightarrow 2c_\psi b_\psi.
\]

Thus the finite action-owned temporal-orientation candidate at a singular
event is

\[
 \chi_{\rm hit}(E)=\operatorname{sgn}(c_\psi b_\psi),
\]

not (\operatorname{sgn}(D e_{\rm ord}V)).  Negative sign denotes a
forward-terminal approach to the event; positive sign denotes a forward
emergent side.  This is a derived label, not a new event row or acceptance
condition.

At the retained N12 center the unchanged action gives

\[
 b_\psi=-1.1191241572294786\times10^{-4},\quad
 c_\psi=3.3576407978503900\times10^{-11},
\]

and hence (c_\psi b_\psi=-3.757616928173632\times10^{-15}).  The same signs
persist in the 192- and 384-point cross-quadrature evaluations.  Existing
action-ball, simple-eigenline, and radii-polynomial bounds keep both factors
away from zero on a (2\times10^{-13}) root enclosure.  These finite-N values
identify the represented sector; they are not used to select it.

## 3. Formal-reflection parity

For

\[
 \mathcal R(q,v,\ell,s)=(q,-v,\ell,-s)
\]

let (S=\operatorname{diag}(-I_v,+I_\ell,-I_s)) on (z).  Exact retained-action
invariance implies

\[
 D(\mathcal RY)=S D(Y)S,\qquad
 \psi(\mathcal RY)=S\psi(Y),\qquad
 b(\mathcal RY)=-S b(Y).
\]

It follows that (b_\psi) is odd, (c_\psi) is even, and

\[
 \chi_{\rm hit}(\mathcal RE)=-\chi_{\rm hit}(E).
\]

The canonical momentum and shift current are likewise odd, while the Hopf
degree, spatial boundary orientation, attachment configuration, and ordered
event eigenvalue are even.  These structures distinguish the two candidate
forward-time sectors but do not identify them.

## 4. Event-to-child conclusion

Every retained finite event-to-child row has the established even/odd parity,
so

\[
 F_N(E,C)=0\Longrightarrow F_N(\mathcal RE,\mathcal RC)=0.
\]

The continuum graph inherits the same local equivariance.  No retained row
requires (c_\psi b_\psi<0), (c_\psi b_\psi>0), an outgoing momentum sign,
or a signed shift current.  Therefore the correspondence does **not**
action-select one temporal-chirality sector, and equivariance does **not** prove
physical equivalence.  Neither sector may be quotiented.

The corrected next mathematical dependency precedes an ordinary return-map
theorem:

`DERIVE_AND_CERTIFY_THE_EXISTING_ACTION_OWNED_ONE_SIDED_SINGULAR_ORDERED_EVENT_HITTING_LAW_AND_ITS_EVENT_TO_CHILD_RESET_REGULARITY_OR_LOCALIZE_THE_FIRST_RETAINED_ACTION_FAILURE`.

Only after that boundary-hitting/reset theorem is available may nonemptiness,
continuity, or periodic points of the forward return relation be proved.

