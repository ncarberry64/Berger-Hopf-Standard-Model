# N12 intrinsic first-return section

Status: **the local singular hitting/reset relation is certified; global
forward reachability and the nonempty return domain are open**.

This note uses only the retained Euler–Dirac flow, the existing ordered-event
functional, the certified event-to-complete-child relation, and the existing
gauge/time quotient. It adds no period, clock, event equation, physical row,
or acceptance gate.

The construction instantiates the already-typed v15.6/v15.7 persistence arrow
\(P\), whose theorem class was retained while its physical orbit remained
unselected. It does not reopen formation or introduce a de-envelopment map.

## 1. The normal certificate is not a state selector

Let

\[
F_{12}:X_{12}=\mathbb R^{196}\longrightarrow\mathbb R^{57}
\]

be the unchanged joint event-child map at the certified root. The stored full
same-state Jacobian has rank 57. Hence its linearized kernel has dimension

\[
196-57=139.
\]

The action-norm radii proof restricts this derivative to a chosen 57-dimensional
normal complement and proves contraction there. By the regular-level-set
theorem, this supplies a local section transverse to the full root set. It does
not make the full root set zero-dimensional. This agrees with the retained
single-child dimension law: at resolution \(N\), the complete-child tangent
kernel has dimension \(6N-6\), giving 66 physical tangent directions at N12.
These directions cannot be removed or bounded as numerical defects.

Thus the certified continuum child is an action-defined local solution
manifold with a certified normal representative. A physical point or orbit on
that manifold is not yet action-selected.

## 2. Action-owned boundary-return candidate

Let \(\varphi_t\) be the retained gauge-fixed Euler–Dirac flow on its existing
eta/Dirac-admissible domain. Let \(e_{\rm ord}\) be the already-selected simple
ordered Euler–Dirac eigenvalue, and let

\[
\Sigma=\{Y\in\mathcal M_\infty:e_{\rm ord}(Y)=0\}
\]

denote the existing complete-event section in the continuum complete-child
manifold. For a complete pair \([E,C]\), with
\(C\in\mathfrak C_\infty(E)\), define, when it exists,

\[
\tau(Y)=\inf\{t>0:e_{\rm ord}(\varphi_t(C))=0\}.
\]

Writing \(E'=\lim_{t\uparrow\tau(Y)}\varphi_t(C)\), when that limit exists
in the certified event chart, the only action-owned return candidate is

\[
\mathcal P([E,C])=\{[E',C']:C'\in\mathfrak C_\infty(E')\},
\]

where \(\mathfrak C_\infty\) is the certified regular continuum
event-to-complete-child relation. Its fixed-event fiber is 67-dimensional,
or 66-dimensional after the existing whole-system time quotient. The
numerical normal chart chooses a reproducible representative; it is not an
action-owned physical selector. The brackets quotient only the existing gauge and
whole-system time-translation equivalences. The use of the first positive
ordered event removes any arbitrary solver-time or externally chosen period.

## 3. Why the ordinary section theorem is unavailable

The ordered event is a simple zero eigenvalue of the same Dirac block that the
regular Euler--Dirac vector field inverts.  Hence \(V(E')\) and
\(D e_{\rm ord}(E')V(E')\) are not defined by the unbordered retained
equations.  The ordinary Poincare-section implicit-function formula previously
written here is therefore retracted.

On the regular side, let \(\psi\) be the selected eigenvector,
\(b_\psi=\langle\psi,b_{\rm ED}\rangle\), and
\(c_\psi=D^3L[(0,\psi)^3]\).  Under the existing hard-inverse and coefficient
limit hypotheses,

\[
\frac d{dt}e_{\rm ord}^2\longrightarrow 2c_\psi b_\psi .
\]

A regular boundary-hitting/reset theorem requires:

1. a one-sided admissible flow with a finite event limit;
2. nonzero \(c_\psi b_\psi\) and the associated square-root hitting law;
3. controlled dependence of the hitting time and limiting event on initial
   data in the appropriate desingularized coordinates;
4. landing inside the certified continuum event-to-child chart; and
5. regularity of the composition with \(\mathfrak C_\infty\).

The retained pole decomposition proves these obligations locally on the
certified terminal chart, and the full-action/tail bounds transfer them to the
continuum child graph. No new dynamics or sign gate is introduced. This local
theorem does not prove that an existing forward child reaches that chart.

## 4. Exact remaining dependency

The repository proves only local positive-duration persistence and explicitly
does not contain an action-selected stable cycle or relative periodic
monodromy. Therefore the domain of \(\mathcal P\) has not been shown nonempty.

The exact next dependency is:

`PROVE_THAT_AT_LEAST_ONE_EXISTING_FORWARD_COMPLETE_CHILD_HISTORY_REACHES_THE_CERTIFIED_TERMINAL_SINGULAR_EVENT_CHART_BEFORE_ANY_EXISTING_PHYSICAL_DOMAIN_EXIT_OR_PROVE_THAT_NO_SUCH_HISTORY_DOES`.

Only after that result may fixed points or primitive periodic orbits be
classified as action-selected intrinsic states. No observable, mass, family,
prediction, or held-out comparison is promoted here.

## 5. Existing positive-duration witness

The already-certified N12 persistence history gives one bounded adjudication;
it is not a return search. Its stored initial and final child states were
evaluated with the existing ordered eigenline. Both endpoints are strictly off
the complete-event section, and the final endpoint is farther from zero across
96-, 192-, and 384-point quadrature. The certified history itself preserves
constraints and eta admissibility. The result is recorded in
`BHSM_N12_EXISTING_PERSISTENCE_EVENT_RETURN_AUDIT.json`.

Consequently the existing local persistence artifact records no state that
executes the first-return relation. Because its intermediate states were not
stored, the endpoint audit does not exclude an interior singular hit; nor can
it establish that no later hit exists. The local singular hitting/reset
theorem is now closed. The remaining issue is the global retained-flow theorem:
prove or disprove that an existing forward complete-child history reaches its
terminal chart before a physical-domain exit, without inventing a parent
section or using numerical continuation as a selection rule.

## 6. Earliest analytic ownership lemma

For a normalized simple ordered eigenpair

\[
H(Y)\psi(Y)=e_{\rm ord}(Y)\psi(Y),
\]

and the retained child vector field \(\dot Y=V(Y)\) on the regular
\(e_{\rm ord}\ne0\) domain, standard simple-eigenvalue perturbation gives

\[
\frac{d}{dt}e_{\rm ord}(Y(t))
=\langle\psi(Y),D H(Y)[V(Y)]\psi(Y)\rangle .
\]

Here \(D H\) is the third variation of the retained action.  This identity may
be integrated only before the singular event.  Its finite event replacement is
the one-sided identity

\[
\lim_{e_{\rm ord}\to0}\frac12\frac d{dt}e_{\rm ord}^2
=D^3L[(0,\psi)^3]\langle\psi,b_{\rm ED}\rangle .
\]

Both are lemmas in the return proof, not new physical equations.

The currently certified continuum result transfers the static complete-child
normal tail and a positive-duration admissible neighborhood. It does not give
a global continuum flow bound. In particular, the existing N3 retained-action
history crosses the eta-Legendre boundary transversely; this prevents treating
eta-domain invariance as an automatic consequence of the action architecture,
although it does not prove that the N12/continuum anchor exits.

The first analytic obligation is therefore a continuation-or-exit dichotomy
for the continuum retained child flow with uniform action-graph, eta, Dirac,
constraint, and ordered-eigenline control. Only on that controlled interval
may the displayed transport identity be bounded or integrated to prove either
a finite transverse return or nonreturn up to physical-domain exit. No
compact invariant finite-measure child set or action-selected reference cycle
is currently available, so recurrence is not a valid shortcut.
