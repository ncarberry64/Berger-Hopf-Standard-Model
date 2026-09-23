"""Exact-zero and scalar shortcuts for the existing Arb mixed-jet algebra."""
from contextlib import contextmanager
import numpy as np
from flint import arb


def _scalar_zero(value):
    return isinstance(value,arb) and value.is_zero()


def _finite(value):
    if isinstance(value,arb):return value.is_finite()
    array=np.asarray(value,dtype=object)
    return all(v.is_finite() if isinstance(v,arb) else bool(np.isfinite(v)) for v in array.flat)


def optimized_mixed_class(module):
    """Make an interval-algebra alternative without editing the frozen source.

    Zero products are omitted only when the other factor is finite. Their
    broadcast shapes are retained. A per-multiplication finiteness cache is
    discarded immediately; mutable arrays are never trusted across calls.
    """
    base=module.Mixed

    class SparseMixed(base):
        def __add__(self,other):
            if isinstance(other,base):
                if len(self.d)!=len(other.d):raise ValueError('Mixed-jet orders differ')
                return SparseMixed(tuple(a+b for a,b in zip(self.d,other.d)))
            constant=module._a(other)
            return SparseMixed((self.d[0]+constant,*self.d[1:]))

        __radd__=__add__

        def __mul__(self,other):
            if not isinstance(other,base):
                constant=module._a(other)
                return SparseMixed(tuple(value*constant for value in self.d))
            if len(self.d)!=len(other.d):raise ValueError('Mixed-jet orders differ')
            if all(_scalar_zero(v) for v in self.d[1:]):
                return SparseMixed(tuple(self.d[0]*v for v in other.d))
            if all(_scalar_zero(v) for v in other.d[1:]):
                return SparseMixed(tuple(v*other.d[0] for v in self.d))
            finite_cache={}
            def finite(value):
                key=id(value)
                if key not in finite_cache:finite_cache[key]=_finite(value)
                return finite_cache[key]
            data=[]
            for mask in range(len(self.d)):
                total=None
                zero_shape=()
                subset=mask
                while True:
                    a,b=self.d[subset],other.d[mask^subset]
                    if (_scalar_zero(a) and finite(b)) or (_scalar_zero(b) and finite(a)):
                        # A skipped factor is scalar zero, so the product
                        # shape is simply the other factor's array shape.
                        shape=a.shape if isinstance(a,np.ndarray) else b.shape if isinstance(b,np.ndarray) else ()
                        if shape:
                            zero_shape=shape if not zero_shape else zero_shape if shape==zero_shape else np.broadcast_shapes(zero_shape,shape)
                    else:
                        term=a*b
                        total=term if total is None else total+term
                    if subset==0:break
                    subset=(subset-1)&mask
                if total is None:total=arb(0)
                current_shape=total.shape if isinstance(total,np.ndarray) else ()
                if zero_shape and zero_shape!=current_shape:
                    shape=np.broadcast_shapes(current_shape,zero_shape)
                    if shape!=current_shape:
                        total=np.broadcast_to(np.asarray(total,dtype=object),shape).copy()
                data.append(total)
            return SparseMixed(tuple(data))

        __rmul__=__mul__

    return SparseMixed


@contextmanager
def use_optimized_mixed(module):
    """Use in one isolated numerical process; restore even after failure."""
    original=module.Mixed
    replacement=optimized_mixed_class(module)
    module.Mixed=replacement
    try:
        yield replacement
    finally:
        module.Mixed=original
