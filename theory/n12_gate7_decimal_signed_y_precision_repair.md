# N12 Gate-7 Decimal signed-Y precision repair

## Scope

This milestone repairs the numerical evaluation of the already-derived Gate-7
signed source. It changes no action term, event definition, selector, scale,
time orientation, reset law, or physical ontology.

The retained quarter-step center is \(\widehat y\), with signed defect

\[
d=\widehat y'-F(\widehat y).
\]

The correlated linear correction continues to use

\[
c'=Jc-d,
\]

so the source is signed before any norm is taken.

## Cause of the former failure

The previous Gauss-8/12/16/20 comparison rebuilt the nearly singular selected
eigenline from a binary64 reduced Hessian at every quadrature node. The retained
line remains simple, but its small complement gap amplifies last-bit Hessian
summation changes into a noisy source coordinate. Changing Gauss order therefore
changed the numerical source representation; it did not reveal a physical event
or a failure of the retained action.

## Precision repair

The pre-existing Decimal velocity jet remains the owner of the reduced
\((v,m)\) Hessian. The new narrow module evaluates only the missing retained
action blocks

\[
L_q,\qquad L_{(v,m),q}
\]

with the same 96-point quadrature, bulk term, nonlocal inertia term, and boundary
Casimir. The already-selected branch is named in binary64, then its eigenpair is
refined by a Decimal bordered Newton solve. The hard complement response is also
obtained from a Decimal bordered solve. Only the final normalized field is
rounded to binary64 for storage.

The new blocks reproduce the production retained-action blocks at separated
history nodes to less than \(4\times10^{-14}\) relative error. No protected
high-precision scratch artifact is used as certificate authority.

## Complete-history numerical results

On every one of the 370 retained quarter-step cells, Gauss-6 and Gauss-8 evaluate
the same stored dense center and the same retained action. Branch 24 is selected
at every node. The largest Decimal eigenpair residual is

\[
1.413\times10^{-58}.
\]

The largest local signed-source integral increment is

\[
7.146\times10^{-15},
\]

which uses 0.5745% of the current nonlinear halo
\(r=1.243972269022099\times10^{-12}\). The sum of all local increment norms is
\(4.239\times10^{-13}\).

Both signed source tables were then replayed through the same retained PROP16
Green operator, with projection only at the retained macro constraint seams.
The maximum correction-profile increment is

\[
6.9191\times10^{-14}=0.055621\,r,
\]

and the terminal increment is \(6.5526\times10^{-14}\).

Therefore the former binary Gauss nonconvergence is superseded as a numerical
conditioning artifact. A stable correlation-preserving signed-Y center is now
available for the next proof step.

## Claim boundary

This milestone certifies complete-history numerical cross-quadrature convergence
of the signed source and its retained Green image. It does not yet provide:

- outward interval enclosure of \(Y\);
- an interval tail for the variable-generator propagator \(Z_1\);
- transfer of the existing \(Z_2\) certificate to a newly frozen center;
- the radii-polynomial promotion or scalar first-hit interval Newton proof.

Gate 7 therefore remains active. The shortest remaining route is to freeze the
Gauss-8 Decimal correction center, attach outward source and PROP16 tail
remainders, rebuild only center-dependent cone objects, and then perform the
strict preterminal margin and scalar first-hit transfer.

## Frozen Gauss-8 linear carrier

The converged Gauss-8 PROP16 state profile is now frozen as the unique numerical
linear carrier. Its descriptor component is assembled without a new source:

\[
q_{\mathrm{new}}=D\lambda[c_{\mathrm{Gauss8}}]
  +\left(q_{\mathrm{old}}-D\lambda[c_{\mathrm{old}}]\right).
\]

Thus the existing direct descriptor source is retained exactly once while only
the state-induced term is rebased. The state correction has maximum norm
\(3.3913443901129416\times10^{-6}\). Descriptor cross-order variation is at
most \(1.9221817061916492\times10^{-16}\).

At the former stored-center stop, the rebased descriptor is
\(9.350435266485474\times10^{-16}\). With the retained transverse crossing
\(-2.8366383530768354\times10^{-11}\), its linearized zero shifts later by
\(3.296308553518384\times10^{-5}\), well inside the remaining
\(0.19486075959935079\) terminal-cell action time. The last complete-node
descriptor margin remains \(1.5631135180446963\times10^{-12}\).

The minimum complete preterminal value, however, occurs at the birth end and is
only \(1.7739272048543877\times10^{-20}\). Consequently the continuous margin
transfer must retain the causal Volterra radius, which vanishes at the reset.
A uniform-in-time use of the terminal nonlinear halo would be invalid. This is
the exact remaining margin coordinate after freezing the center.
