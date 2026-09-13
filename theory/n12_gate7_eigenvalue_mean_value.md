# Mean-value enclosure of the selected eigenvalue

On the already certified normalized symmetric eigenpair family,
H(x) psi(x) = lambda(x) psi(x) and psi(x)^T psi(x) = 1.
Differentiate in a raw state direction v and multiply by psi^T. Symmetry
cancels the eigenvector derivative terms, giving

    D lambda[v] = psi^T DH[v] psi = D3S[(0,psi),(0,psi),v].

The projected eigenline solve's last coordinate is auxiliary. It is not
this slope, and integrating it would give an incorrect eigenvalue bound.

Use the verified point eigenvalue enclosure as anchor. On the actual
midpoint domain, integrate all 249 uniform scalar slopes along the radial
segment and apply the full five-group support bound. Saved directions
already include each group radius; support therefore uses unit radii.
Only the first 98 weighted coordinates are unweighted for the action;
the descriptor has no direct dependence in the raw state Hessian.

The existing paired midpoint eigenpair certificate supplies strict implicit
invertibility, orientation and simplicity. Independently paired primal
eigenvector bounds may tighten the input box without changing that family.
The resulting eigenvalue box encloses the same family even if it is wider
than the previous box. Select it for later work only if it is narrower,
and only after independent byte-identical reproduction. This step does not
change the action, fit observations, prove full-path contraction or close
Gate 7.
