# Direct physical Hermite-Simpson second variation

Status: conditional arithmetic integration of caller-certified physical rate
derivatives. This is neither a completed Hessian campaign nor a neighborhood
or physical quotient certificate. The retained action and frozen inverse are
unchanged.

For endpoints z0,z1, exact stored step h and the actual physical HS midpoint,

    M = (z0+z1)/2 + h*(f(z0)-f(z1))/8,
    r = z1-z0 - h*(f(z0)+4*f(M)+f(z1))/6.

The first midpoint direction maps are

    B0 = I/2 + h*DF(z0)/8,
    B1 = I/2 - h*DF(z1)/8.

Let u=(u0,u1), v=(v0,v1), where the endpoint components are already embedded
in the weighted ambient coordinates using the frozen trial frames. Define

    L = D2f(z0)[u0,v0],
    R = D2f(z1)[u1,v1],
    H = D2f(M)[B0*u0+B1*u1, B0*v0+B1*v1].

Then the complete second chain rule is

    D2M[u,v] = h*(L-R)/8,
    D2r[u,v] = -h*(L+4*H+R)/6 - (2*h/3)*DF(M)*D2M[u,v].

The final term is essential. A rate Hessian evaluated at the midpoint is not
by itself the Hessian of the composite midpoint rate. Multiplication by the
midpoint Jacobian occurs on the output of D2M, in the displayed order.

`physical_hs_second_residual` accepts matrices whose columns are matching
bilinear contractions L,H,R. It performs the chain rule in Arb and returns
both D2M and D2r. The caller owns their input certificates, common evaluation
points and direction maps. Missing contractions fail; they are not zero
defaults. For a fixed initial endpoint, u0=v0=0 makes its left contraction
exactly zero by bilinearity, rather than by an assumption about its Hessian.

For the fixed test frame T and frozen right block R_frozen, the quadratic
source of the frozen Newton map is

    Q_local[u,v] = -R_frozen^-1 * T * D2r[u,v] / 2.

`frozen_newton_quadratic_source` encloses this solve with no orthonormal-frame
assumption. The inverse and test frame are fixed, so this formula supplies
no state-dependent frame derivatives. Global composition uses the same
frozen causal recurrence as the residual and linear-defect stages; this
helper does not carry out that global computation.

The factor one-half is the Taylor coefficient, not a removal of the mixed
term: for u=rL*uL+rT*uT, the quadratic form contains

    rL^2*Q[uL,uL] + 2*rL*rT*Q[uL,uT] + rT^2*Q[uT,uT].

Tests differentiate the complete nonlinear vector HS residual independently
with SymPy, including cross-endpoint direction pairs, and compare exact
rational values with the Arb result. They also check a nonorthogonal test
frame and non-diagonal frozen inverse, interval coefficient corners, the
midpoint curvature correction, zero curvature for a linear rate, and the
mixed Taylor factor. Reference rational enclosures use greater precision
than the result under test. Singular solves and incompatible/missing inputs
fail without changing the caller's arithmetic precision.

To promote a full integration result, a consumer must still verify paired
direct DF and direct physical-point Hessian data, common frozen operands,
complete interval coverage and independent reproducibility. The older
stored-point Hessian caches do not establish those direct physical-point
inputs. Even a complete finite-history quadratic calculation does not
establish branch continuation, physical quotient identification or bounds
over the full nonlinear proof neighborhood. Gate7 and full BHSM remain open.
