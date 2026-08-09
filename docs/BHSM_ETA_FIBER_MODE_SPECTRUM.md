# BHSM v14.30 eta fiber-mode spectrum

## Exact retained fiber theorem

The Hopf fiber is \(F=\operatorname{Sp}(1)\simeq S^3\). Peter--Weyl gives

\[
L^2(F)=\widehat\bigoplus_{J\in\frac12\mathbb N_0}V_J\otimes V_J^*.
\]

In the repository convention the orthonormal matrix elements
\(Y^J_{n,m}\) obey

\[
\int_F\overline{Y^J_{n,m}}Y^{J'}_{n',m'}d\nu_F
=\delta_{JJ'}\delta_{nn'}\delta_{mm'}.
\]

For
\(g_F=L_2^2(\sigma_1^2+\sigma_2^2)+L_1^2\sigma_3^2\),

\[
\lambda_{J,m}=\frac{J(J+1)}{L_2^2}
+m^2\left(\frac1{L_1^2}-\frac1{L_2^2}\right).
\]

Fixed \((J,m)\) has multiplicity and associated-bundle rank \(2J+1\).
The full spin-\(J\) matrix-element space has dimension \((2J+1)^2\).
Nontrivial coefficients are sections of the \(Sp(1)\)-associated bundle, not
ordinary scalars. The closed fiber contributes no endpoint boundary form.

## What is not identified

The parent eta field is a unit triality spinor and its derivative uses the
induced Spin connection. The repository does not specify the restriction of
that exact eta bundle/operator to the above scalar multiplets in a way that
also carries the independent physical \(SU(3)\) action. Therefore:

- the basic scalar mode is mathematically known but is not a physical eta
  particle assignment;
- the lowest non-basic \(J=1/2\) doublets are known as Hopf multiplets;
- no \(J,m\) label is proved to be the degree-one eta texture;
- no mode is assigned a physical \(\mathbf3\) or \(\bar{\mathbf3}\);
- v13.1 is a flat \(\mathbb R^7\) cohomogeneity-one texture, not a solution of
  this full-preimage spectral problem;
- the \(p=8\) nonlinearity generically couples an infinite tower.

## Classification

Peter--Weyl completeness, orthogonality, eigenvalues, and multiplicities are
`VALIDATED`. Their application to the parent triality-spinor eta Hessian is
`OPEN` pending the action-owned eta/color bundle morphism and a full-preimage
stationary background.
