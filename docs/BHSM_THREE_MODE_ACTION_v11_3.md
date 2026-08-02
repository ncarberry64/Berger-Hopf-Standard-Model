# BHSM v11.3 Three-Mode Action

The three action slots remain `(q_C,q_W,x_D=q_D/lambda_D)`. In whitened action-normalized local coordinates the kinetic matrix is `K=I_3`. Linearizing the attachment constraint at the unit reference gives `B=(-1,1,1)`.

A simple tangent basis is `N=((1,1,0),(1,0,1))`, giving the positive reduced kinetic matrix

`N^T K N = ((2,1),(1,2))`

with eigenvalues `1,3`. The exact KKT second variation is `((H,B^T),(B,0))`. Its reduced symbolic Hessian is defined, but numerical/operator stability still requires the common-domain core/wall response Gram–Hessian. No mass scale or mass prediction is emitted.

