# Centered physical variation residuals

This is an algebraic enclosure method for the retained action and the already
paired physical domains. It supplies neither a new physical assumption nor a
Gate 7 closure certificate. The diagnostic consumer evaluates selected columns
only and explicitly reports that it is not independently reproduced.

Let the original physical bordered system be

\[
K=\begin{pmatrix}H-\lambda I&p\\p^T&0\end{pmatrix},\qquad
J=K D,\quad D=\operatorname{diag}(I,-1).
\]

The paired eigenpair evidence supplies a fixed exact preconditioner \(R\),
positive exact weights \(r\), and row bounds \(V\) for the same family
\(I-RJ\), with \(q=\max_i V_i/r_i<1\).
For any fixed exact physical variation center \(u_0\), use the existing
weighted response enclosure with center \(D u_0\) and residual
\(R(b-Ku_0)\), then multiply its output by \(D\).
The center can be any exact vector; the diagnostic obtains it from a fresh
verified point solve at the unchanged domain anchor. This does not shrink the
physical domain or assert invertibility of its independent-entry matrix hull.

Write \(c_k\) for the raw lower-coordinate embedding of row
\(R_{k,:n}\), \(v\) for a raw input direction, and
\(\ell=S^{(3)}[p,p,v]\). For a selected-line variation center
\(u_0=(a_0,d_0)\), the signed preconditioned residual is

\[
-S^{(3)}[c_k,p,v]-S^{(2)}[c_k,a_0]
+\lambda R_{k,:n}a_0+(\ell-d_0)R_{k,:n}p
-R_{k,n}p^Ta_0.
\]

It is exactly row \(k\) of \(R(b_p-Ku_0)\) for the original
\(b_p=(-H'[v]p+\ell p,0)\). The preconditioner enters action legs
before interval evaluation, retaining signed contractions.

For the response variation use the paired response \((h,b)\), the just
enclosed selected-line variation \(dp\), and the complete source legs
\(g_k,a_k,d(x),Dd[v]\) from `affine_response_residual.response_legs`.
For a separate fixed center \((a_0,d_0)\), its residual is

\[
\begin{aligned}
&S^{(2)}[g_k,v]-S^{(3)}[a_k,d(x),v]-S^{(2)}[a_k,Dd[v]]\\
&-S^{(3)}[c_k,h,v]-S^{(2)}[c_k,a_0]
+\ell R_{k,:n}h-bR_{k,:n}dp\\
&+\lambda R_{k,:n}a_0-d_0R_{k,:n}p
-R_{k,n}(dp^Th+p^Ta_0).
\end{aligned}
\]

The configuration derivative and both bottom-row terms are required. The
formula is checked against direct bordered matrices for a small polynomial
action with nontrivial metric weights, two directions and a non-diagonal
preconditioner. A rational such as 1/31 has nonzero Arb rounding radius and
must be replaced by its exact midpoint when used as a fixed preconditioner;
the production helper rejects uncertain preconditioners and centers.

The diagnostic retains the original physical rate's four complete D3/D4
contraction groups and both variation solves. Its extra residual contractions
bypass the four-group capture used by the previously paired normalization
refinement. It requires overlap with the zero-center variation enclosures
and containment of the freshly verified point derivative. These comparisons
are consistency checks; the enclosure rests on the signed identities and
the same-family weighted contraction proof.

Full-basis independent reproduction, acceptable uniform integration bounds,
physical quotient identification and all remaining completion dependencies
remain separate requirements.

## Affine state integration diagnostic

The second diagnostic fixes the eigenpair and response operands at arbitrary
members of their proved boxes, splits each residual at the exact state anchor,
and integrates its state derivative over the original affine domain. Thus

\[
e(x,\theta)=e(x_0,\theta)+\int_0^1 D_xe(x_0+t(x-x_0),\theta)[x-x_0]dt.
\]

Here \(\theta\) includes the eigenpair, physical response, selected-line
variation and border. Their interval values are held fixed while taking
\(D_x\), but their complete boxes are used when evaluating both terms.
This identity is valid for each fixed choice, including the actual values
at the final physical state. No derivative of \(\theta(x)\) is omitted:
the split does not differentiate that composite function.

For a raw domain direction \(d\), the selected-line residual derivative is

\[
-S^{(4)}[c_k,p,v,d]-S^{(3)}[c_k,a_0,d]
+S^{(4)}[p,p,v,d]R_{k,:n}p.
\]

The response residual derivative is

\[
\begin{aligned}
&S^{(3)}[g_k,v,d]-S^{(4)}[a_k,d(x),v,d]\\
&-S^{(3)}[a_k,Dd[d],v]-S^{(3)}[a_k,Dd[v],d]\\
&-S^{(4)}[c_k,h,v,d]-S^{(3)}[c_k,a_0,d]
+S^{(4)}[p,p,v,d]R_{k,:n}h.
\end{aligned}
\]

Both configuration terms are present. Exact polynomial centered differences
check both identities independently. The endpoint domain uses its original
one longitudinal interval and 74-dimensional transverse ball. The actual
midpoint domain uses all 249 original columns and all five domain groups,
including its field remainder box. Signed directional contractions are
bounded with the existing complete group support function before addition
to the anchor residual. The fixed-domain interval action evaluations cover
every segment in this mean-value identity.
