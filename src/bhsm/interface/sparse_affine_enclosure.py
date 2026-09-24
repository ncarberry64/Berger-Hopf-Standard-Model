"""Sparse storage of the existing first-order Taylor enclosure arithmetic."""
from flint import arb,arb_mat
from bhsm.interface.shared_parameter_residual import validate_groups


class SparseDomain:
    def __init__(self,groups,dimension):
        validate_groups(groups,dimension)
        self.groups,self.dimension=tuple(groups),dimension
    def affine(self,c,a=None,r=0):
        co={} if a is None else {i:arb(x) for i,x in enumerate(a) if not arb(x).is_zero()}
        return SparseAffine(self,arb(c),co,arb(r).upper())


class SparseAffine:
    def __init__(self,d,c,a,r):
        self.domain,self.c,self.coefficients,self.r=d,c,a,r
        self._linear=None
    @property
    def a(self):
        return arb_mat(1,self.domain.dimension,[self.coefficients.get(i,arb(0)) for i in range(self.domain.dimension)])
    def linear_bound(self):
        if self._linear is None:
            total=arb(0)
            for start,stop,kind in self.domain.groups:
                values=[abs(v).upper() for i,v in self.coefficients.items() if start<=i<stop]
                total += sum((x*x for x in values),arb(0)).sqrt() if kind=='euclidean' else sum(values,arb(0))
            self._linear=total.upper()
        return self._linear
    def enclosure(self):return self.c+arb(0,(self.linear_bound()+self.r).upper())
    def support(self):return (abs(self.c).upper()+self.linear_bound()+self.r).upper()
    def __add__(self,b):
        if not isinstance(b,SparseAffine):b=self.domain.affine(b)
        if b.domain is not self.domain:raise ValueError('shared sparse domain required')
        co=self.coefficients.copy()
        for i,x in b.coefficients.items():
            co[i]=co.get(i,arb(0))+x
            if co[i].is_zero():del co[i]
        return SparseAffine(self.domain,self.c+b.c,co,(self.r+b.r).upper())
    __radd__=__add__
    def __neg__(self):return SparseAffine(self.domain,-self.c,{i:-v for i,v in self.coefficients.items()},self.r)
    def __sub__(self,b):return self+(-b)
    def __mul__(self,b):
        if not isinstance(b,SparseAffine):
            b=arb(b)
            return SparseAffine(self.domain,self.c*b,{i:v*b for i,v in self.coefficients.items() if not (v*b).is_zero()},(self.r*abs(b).upper()).upper())
        if b.domain is not self.domain:raise ValueError('shared sparse domain required')
        a=self*b.c+b*self.c
        la,lb=self.linear_bound(),b.linear_bound()
        r=la*lb+(abs(self.c).upper()+la)*b.r+(abs(b.c).upper()+lb)*self.r+self.r*b.r
        return SparseAffine(self.domain,self.c*b.c,a.coefficients,r.upper())
    __rmul__=__mul__
    def _unary(self,value,first,second):
        width=(self.linear_bound()+self.r).upper()
        r=(abs(first).upper()*self.r+second*width*width/2).upper()
        return SparseAffine(self.domain,value,{i:a*first for i,a in self.coefficients.items() if not (a*first).is_zero()},r)
    def reciprocal(self):
        full=self.enclosure()
        if full.contains(0):raise ArithmeticError('sparse Taylor reciprocal crosses zero')
        return self._unary(1/self.c,-1/self.c**2,(2/abs(full)**3).upper())
    def exp(self):return self._unary(self.c.exp(),self.c.exp(),self.enclosure().exp().upper())
    def log(self):
        full=self.enclosure()
        if not full>0:raise ArithmeticError('sparse Taylor logarithm is not positive')
        return self._unary(self.c.log(),1/self.c,(1/full**2).upper())
