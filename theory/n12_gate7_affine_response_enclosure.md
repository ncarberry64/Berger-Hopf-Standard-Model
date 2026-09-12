# Physical response from the coupled affine eigenpair contraction

The retained value formula solves K*u=(b,0), where
K=[H-lambda*I,p; p^T,0] and u=(h,bpsi). Its normalized-eigenpair Jacobian is
J=[H-lambda*I,-p; p^T,0]. Thus K=J*D for D=diag(I,-1), and z=D*u solves J*z=(b,0).
The same fixed preconditioner R and weighted contraction estimate for I-R*J
therefore establish invertibility for this actual coupled family.

For a fixed exact center z0, let e enclose R*((b,0)-J*z0). If the weighted row
bounds are V_i with positive exact weights r_i, set

    q = max_i V_i/r_i < 1,
    eta = max_i |e_i|/r_i.

The Neumann estimate gives |z_i-z0_i| <= r_i*eta/(1-q). Applying D returns an
enclosure of the physical response. All arithmetic bounds are outward. This
does not require an independent-entry matrix hull to be nonsingular; the
residual and contraction bounds must refer to the same actual coupled domain.

An entrywise residual enclosure is legitimate but may be too wide to normalize
the resulting physical field. A sharper residual can keep the original affine
state directions inside the retained action derivatives. Write the reduced
response source as

    b_i = redW_i*(1_{i<37}*qW_i*S_i/w_i
          - sum_j S_(37+i,j)*qW_j*x_(37+j)/(w_(37+i)*w_j)).

For row k of R, define fixed raw action legs g_k (upper coordinates), a_k and
c_k (lower coordinates), and the state-dependent configuration leg d(x):

    (g_k)_i = R_(k,i)*redW_i*qW_i/w_i, i<37;
    (a_k)_(37+i) = R_(k,i)*redW_i/w_(37+i);
    (c_k)_(37+i) = R_(k,i);
    d_j(x) = qW_j*x_(37+j)/w_j, j<37.

All unspecified components are zero. With fixed response center (h0,b0) and
raw lower-coordinate leg h0, the state-dependent part of the preconditioned
response residual is

    S'(x)[g_k] - S''(x)[a_k,d(x)] - S''(x)[c_k,h0].

Its derivative along any signed raw affine input direction v is

    S''[g_k,v] - S'''[a_k,d(x),v]
      - S''[a_k,Dd*v] - S'''[c_k,h0,v].

The entire signed expression is summed before taking absolute values, then
bounded by the longitudinal interval plus the transverse Euclidean-ball norm.
The configuration leg depends on x; omitting the S''[a_k,Dd*v] term is invalid.
The remaining independent eigenpair uncertainty contributes at most

    r_lambda*|sum_j R_(k,j)*h0_j|
      + sum_j |b0*R_(k,j)+R_(k,n)*h0_j|*r_p,j.

The fixed-center residual must also be included. This is an enclosure strategy
for the original response equation, with no new action or physical assumption.
An independently reproduced application, a positive norm for G, and the full
retained third-action terms in the descriptor rate are still needed before a
uniform physical value certificate can be claimed. None of this alone closes
HS midpoint neighborhoods, uniform derivatives, the quotient, or Gate7.
