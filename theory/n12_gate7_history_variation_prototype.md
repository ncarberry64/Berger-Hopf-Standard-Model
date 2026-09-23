# Gate-7 connecting-history variation prototype

Scope: interval 18 joins endpoints 18 and 19. Anchor 18 is reused without a
point Hessian, eigenpair, endpoint-19 prototype, or frozen local calculation.
There is no physical budget debit. Gate 7 and both kappa bounds remain open.

## Original connecting domain

For the two original affine endpoint tubes z0,z1 and their independently
certified uniform physical rates f0,f1, put d=z1-z0 and h=1/4. The cubic is

    z(t)=z0+t*d+t*(1-t)*[(1-t)*(h*f0-d)-t*(h*f1-d)],  0<=t<=1.

Large straight-line terms cancel before Taylor enclosure. At t=1/2 this is
exactly (z0+z1)/2+h*(f0-f1)/8, the owned HS midpoint equation. The original
midpoint-domain receipt binds the same endpoint and rate inputs. Physical
state weights are removed when passing raw state/velocity legs to the action.

Both endpoint longitudinal/transverse groups retain their original radii.
The 409 parameters comprise t, the mean-value integration parameter s, two
75-parameter endpoint groups, 196 auxiliary errors from the inherited rate
balls, and a 61-component weighted operator-test box. Repeated occurrences
use the same symbols. The rate-ball errors enlarge the actual family; no
additional rate correlations are asserted, and no spherical state domain is
substituted. Subdivision partitions t and s without reducing physical radii.

## Action-owned variation and exact row test

At x0=x18, H is the reduced block of the action Hessian. For each candidate
history state x=z(t), the new computation encloses

    R0*(H(x)-H(x0))*eta
      = integral_0^1 R0*D3S(x0+s*(x-x0))[.,eta,x-x0] ds.

One contraction uses eta=psi0 for the residual; the other uses every
|eta_i|<=w_i for the derivative. Raw action gradients are preconditioned and
summed before support. The signed affine coefficient of each centered s
cell integrates to zero exactly. Nonlinear Taylor tails remain outward
enclosures; they do not retain all higher-degree shared cancellations.

Affine local maps have zero third derivative. The quadratic gravity
prefactor has zero third derivative before multiplication by its exponential.
Cubic polynomial pieces have constant third derivative; the ADM and xeta
powers have sparse polynomial derivatives. Products with exponentials are
differentiated completely. The global inertia reciprocal and boundary square
root retain their analytic derivatives and positive-denominator checks.
No finite-difference or new point Hessian is used.

Let D0=I-R0*J0 be the saved point defect. For row i define

    P_i = sum_j |D0_ij| w_j,
    S_i >= sup |(R0*(DeltaH*eta,0))_i|,
    T_i >= sup |(R0*(DeltaH*psi0,0))_i|,
    N_i = 2*w_lambda*sum_j |R0_ij|*w_psi,j
          + |R0_i,last|*sum_j w_psi,j^2.

The two eigenpair contributions and normalization border are absorbed by
this existing nonlinear Banach bound. They are not independent physical
error budgets. With a possible scalar witness enlargement alpha>=1,

    Y_i = Y_anchor,i + T_i,
    V_i = alpha*(P_i+S_i) + alpha^2*N_i,
    q = max_i V_i/(alpha*w_i).

Self-inclusion requires Y_i+V_i<alpha*w_i in every row, as well as positive
original-reference overlap. The inherited Y_anchor conservatively bounds
the point residual, including its old local-state allowance. This does not
add q0 twice. An eigenpair witness enlargement changes no physical radius.

## Prototype results

The frozen local-domain q0 is approximately 0.5676731292420298. The unsplit
first-run diagnostic gives q<=70627.33891009308. Splitting both t and the
integration parameter into halves gives these approximate outward bounds:

| History parameter | Preconditioned Hessian variation | Complete q | Lower bound on 1-q |
|---|---:|---:|---:|
| [0,1/2] | 25967.91155616929 | 25967.911558321965 | -25966.911558321965 |
| [1/2,1] | 26240.098717294095 | 26240.09871944677 | -26239.09871944677 |

Both tests fail to certify continuation. Row 30 dominates these upper bounds;
the nonlinear border adds only about 2.15e-6 to its weighted derivative bound.
All eight new action blocks and the complete subdivided report independently
reproduced byte-for-byte. Positive inertia is bounded below by 23.14195
throughout these enclosures. The initial
unsplit experiment is a checkpointed diagnostic, not a frozen reproduced lemma.

## Rigorous obstruction to subdivision alone

The saved endpoint-19 data already give D19=I-R19*J19. Hence verified Arb
linear algebra recovers J19=R19^-1*(I-D19), without an action evaluation.
The frozen normalized point eigenpair enclosure supplies delta_psi and
delta_lambda relative to this stored predictor. Add

    (-delta_lambda*I, -delta_psi; delta_psi^T, 0)

to attach the actual endpoint-19 branch root. Componentwise lower absolute
bounds then prove

    ||W18^-1*(I-R18*J19_actual)*W18||_infinity > 6.05413 > 1.

Row 46 supplies the largest certified lower bound. This calculation reproduced
byte-for-byte. The physical symmetric K convention is sign-conjugate to J
and has exactly the same weighted infinity defect.

Every full interval cover includes endpoint 19. Therefore no subdivision can
make this SAME fixed R18/W18 pair contract throughout interval 18. This is a
failure of that preconditioner/norm criterion, not failure of the simple
eigenline or of BHSM. A changed norm/inverse is not ruled out. Endpoint 19
already has a certified inverse, so a new point eigenpair must not be inferred
to be necessary from this obstruction.

## Coverage consequence

No complete interval was added: the current cover remains 0/370. No new
anchor was evaluated. The minimum new-anchor set and the overlap obtainable
from existing anchors 18 and 19 remain undetermined. A two-anchor or varying
inverse construction needs its own uniform residual, inverse-defect and
overlap certificate before any further history coverage is claimed.

All new action blocks are atomically saved with input and payload hashes.
Fresh and resumed blocks use identical outward saved-ball decoding before
assembly. No physical rate, kappa, self-map or contraction ledger is debited.
