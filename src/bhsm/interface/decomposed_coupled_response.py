"""Iterate component bounds using the paired coupled defect decomposition."""
import numpy as np
from flint import arb
from bhsm.interface.affine_eigenpair_contraction import _balls


class CoupledDefectBound:
    """Bound (I-RJ) on arbitrary error boxes, keeping the action domain fixed.

    S bounds the state-dependent Hessian difference acting on the lower
    coordinates of the original eigenpair radius box. It does not include
    the center defect or nonlinear p/lambda dependence; those enter separately.
    The caller must bind all these operands to the same certified family.
    """
    def __init__(self,center_defect,preconditioner,domain_radii,state_variation):
        D,R,r,S=map(_balls,(center_defect,preconditioner,domain_radii,state_variation))
        if r.ndim!=1 or r.size<2 or D.shape!=(r.size,r.size) or R.shape!=D.shape or S.shape!=r.shape:
            raise ValueError('complete compatible coupled defect decomposition required')
        if not all(v>0 and v.rad().is_zero() for v in r) or not all(v>=0 for v in S):
            raise ValueError('exact positive domain radii and nonnegative state bounds required')
        if not all(v.rad().is_zero() for v in R.flat):raise ValueError('fixed exact preconditioner required')
        self.D=np.array([abs(v).upper() for v in D.flat],dtype=object).reshape(D.shape)
        self.R=np.array([abs(v).upper() for v in R.flat],dtype=object).reshape(R.shape)
        self.r=r;self.S=S
        self.p_column=self.R[:,:-1]@r[:-1]

    def apply(self,error_radii):
        w=_balls(error_radii);r=self.r
        if w.shape!=r.shape or not all(v>=0 for v in w):raise ValueError('matching nonnegative error radii required')
        # The state term has no last (lambda) input column.
        lower_scale=max((a/b).upper() for a,b in zip(w[:-1],r[:-1],strict=True))
        result=self.D@w+self.S*lower_scale
        result+=r[-1]*(self.R[:,:-1]@w[:-1])+w[-1]*self.p_column
        result+=self.R[:,-1]*sum((a*b for a,b in zip(r[:-1],w[:-1],strict=True)),arb(0))
        return np.array([v.upper() for v in result],dtype=object)

    def enclose(self,center,preconditioned_residual,iterations=32):
        if type(iterations) is not int or not 1<=iterations<=256:raise ValueError('bounded positive iteration count required')
        z,e=map(_balls,(center,preconditioned_residual));r=self.r
        if z.shape!=r.shape or e.shape!=r.shape or not all(v.rad().is_zero() for v in z):
            raise ValueError('matching exact center and finite residual required')
        V=self.apply(r);q=max((v/w).upper() for v,w in zip(V,r,strict=True))
        if not q<1:raise ArithmeticError('strict decomposed weighted contraction required')
        absolute=np.array([abs(v).upper() for v in e],dtype=object)
        scale=(max((v/w).upper() for v,w in zip(absolute,r))/(1-q)).upper()
        w=np.array([(v*scale).upper() for v in r],dtype=object)
        for _ in range(iterations):
            candidate=absolute+self.apply(w)
            w=np.array([min(a,b.upper()) for a,b in zip(w,candidate,strict=True)],dtype=object)
        box=np.array([v+arb(0,d) for v,d in zip(z,w,strict=True)],dtype=object)
        return box,dict(weighted_contraction_upper_rational=str(q.fmpq()),
            initial_weighted_error_upper_rational=str(scale.fmpq()),component_iterations=iterations,
            component_radii_upper_rational=[str(v.fmpq()) for v in w],
            physical_domain_radii_changed=False,action_domain_bound=False,FULL_BHSM_COMPLETE=False)
