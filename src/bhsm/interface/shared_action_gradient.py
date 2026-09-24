"""Reverse-over-mixed action gradient with a single common Taylor domain.

Returns all raw rows of D^(m+1)S[.,legs], treating the prescribed legs as
pointwise constants for the outer action gradient. Their physical variations
are separate terms. No eigenpair or point Hessian is calculated here.
"""
import math
from flint import arb
from bhsm.interface.shared_action_taylor import Taylor,scalar_taylor_action
from bhsm.interface.factored_arb_integrand import factored_local_algebra


class Node:
    def __init__(self,tape,value,parents=()):
        self.tape,self.value,self.parents=tape,value,parents
        self.index=len(tape);tape.append(self)
    def __add__(self,b):
        if isinstance(b,Node):return Node(self.tape,self.value+b.value,((self,1),(b,1)))
        return Node(self.tape,self.value+b,((self,1),))
    __radd__=__add__
    def __neg__(self):return Node(self.tape,-self.value,((self,-1),))
    def __sub__(self,b):return self+(-b)
    def __rsub__(self,b):return (-self)+b
    def __mul__(self,b):
        if isinstance(b,Node):return Node(self.tape,self.value*b.value,((self,b.value),(b,self.value)))
        return Node(self.tape,self.value*b,((self,b),))
    __rmul__=__mul__
    def reciprocal(self):
        v=self.value.reciprocal();return Node(self.tape,v,((self,-v*v),))
    def __truediv__(self,b):return self*(b.reciprocal() if isinstance(b,Node) else 1/arb(b))
    def __rtruediv__(self,b):return self.reciprocal()*b
    def __pow__(self,n):
        if n<0:return (self**(-n)).reciprocal()
        if n==0:return self*0+1
        result=self;index=1
        while index<n:result=result*self;index+=1
        return result
    def exp(self):
        v=self.value.exp();return Node(self.tape,v,((self,v),))
    def positive_power(self,p):
        return Node(self.tape,self.value.positive_power(p),
                    ((self,p*self.value.positive_power(p-1)),))


def reverse(output,inputs):
    # Adjoints are mixed jets, so multiplication performs all formal product
    # rules, including the legs' action-direction dependence of local factors.
    adj={output.index:1}
    for node in reversed(output.tape):
        if node.index not in adj:continue
        value=adj[node.index]
        for parent,factor in node.parents:
            term=value*factor
            adj[parent.index]=adj.get(parent.index,0)+term
    return [adj.get(node.index,0) for node in inputs]


def gradient(module,state,legs,progress=None):
    if len(state)!=module.STATE or not 1<=len(legs)<=4:
        raise ValueError('complete raw state and one through four action legs required')
    if any(not isinstance(v,Taylor) for v in state):raise ValueError('shared Taylor state required')
    d=state[0].domain
    if any(v.domain is not d for v in state):raise ValueError('one common state namespace required')
    if any(len(v)!=module.STATE for v in legs):raise ValueError('complete action legs required')
    if any(isinstance(a,Taylor) and a.domain is not d for leg in legs for a in leg):
        raise ValueError('state and legs must use identical shared parameters')
    geometry=[module._integrand([arb(0)]*module.STATE,j,0) for j in range(module.POINTS)]
    boundary_maps,_=module._boundary([arb(0)]*module.STATE,0)
    m=len(legs)
    with scalar_taylor_action(module):
        def zero():return module.Mixed.constant(0,m)
        def variables(maps,offsets):
            tape=[];items=[]
            for mapping,c in zip(maps,offsets,strict=True):
                value=sum((state[k]*a for k,a in mapping),d.affine(c))
                local=[sum((leg[k]*a for k,a in mapping),arb(0)) for leg in legs]
                items.append(Node(tape,module.Mixed.affine(value,local)))
            return items
        bulk_grad=[zero() for _ in state];inertia_grad=[zero() for _ in state];inertia=zero()
        for j,base in enumerate(geometry):
            z=variables(base.maps,base.values)
            x=float(module._BASIS[0][j]);sigma=-0.5+2*x/math.pi-math.sin(4*x)/(2*math.pi)
            constants=[module.RADIUS0,module.RADIUS0*math.cos(x),module.RADIUS0*math.sin(x),
                3*math.cos(x)**2,3*math.sin(x)**2,0.5*(15*5**(1/3)/4),1-4*sigma**2]
            bulk,I=factored_local_algebra(z,*map(arb,constants),lambda a:a.exp())
            weight=float(module._BASIS[1][j]);inertia+=weight*I.value
            for mapping,b,g in zip(base.maps,reverse(bulk,z),reverse(I,z),strict=True):
                for k,a in mapping:
                    bulk_grad[k]+=weight*a*b;inertia_grad[k]+=weight*a*g
            if progress and (j+1)%16==0:progress(j+1,module.POINTS)
        if not inertia.d[0].enclosure()>0:raise ArithmeticError('positive global inertia required')
        z=variables(boundary_maps,[0]*3);a,b,n=z
        A=module.RADIUS0*a.exp()/math.sqrt(2.0);B=module.RADIUS0*b.exp()/math.sqrt(2.0)
        r4=A*B/(A**2+B**2).positive_power(0.5)
        boundary=-module.standard_model_casimir_coefficient()*n.exp()/r4
        boundary_grad=[zero() for _ in state]
        for mapping,g in zip(boundary_maps,reverse(boundary,z),strict=True):
            for k,a in mapping:boundary_grad[k]+=a*g
        c=0.25/(2.0*module.HOPF_ORBIT_VOLUME**2)
        factor=c/(inertia*inertia)
        result=[(a+factor*b+c).d[-1] for a,b,c in zip(bulk_grad,inertia_grad,boundary_grad)]
        result=[v if isinstance(v,Taylor) else d.affine(v) for v in result]
    return result
