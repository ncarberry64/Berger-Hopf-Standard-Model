"""Retain a signed expression DAG alongside outward affine Taylor bounds.

The DAG, not its affine enclosure, is the restart authority. Products and
repeated error leaves retain identity. Supporting a compiled enclosure is an
explicit relaxation; it never deletes the underlying expression.
"""
import json
import hashlib
from flint import arb, arb_mat, fmpq
from bhsm.interface.shared_action_taylor import Taylor, TaylorDomain
from bhsm.interface.sparse_affine_enclosure import SparseDomain


def pair(x):
    return [str(x.mid().fmpq()), str(x.rad().fmpq())]


def restore(x):
    return arb(fmpq(x[0])) + arb(0, arb(fmpq(x[1])))


class ExpressionDomain:
    flatten_limit_default=32
    def __init__(self, groups, names):
        if len(set(names)) != len(names):
            raise ValueError('unique physical parameter names required')
        self.names = tuple(names)
        self.dimension = len(names)
        self.backend = SparseDomain(groups, len(names))
        self.groups = self.backend.groups
        self.nodes, self.lookup, self.bounds, self.leaf_provenance = [], {}, {}, {}
        self.digest=hashlib.sha256()
        self.flatten_limit=self.flatten_limit_default

    def node(self, data):
        key = json.dumps(data, separators=(',', ':'), sort_keys=True)
        if key not in self.lookup:
            self.lookup[key] = len(self.nodes)
            self.nodes.append(data)
            self.digest.update(key.encode()+b'\n')
        return Expression(self, self.lookup[key])

    def affine(self, constant, coefficients=None, remainder=0, *, provenance=None):
        c, r = arb(constant), arb(remainder)
        a = [arb(0)]*self.dimension if coefficients is None else list(map(arb, coefficients))
        if len(a) != self.dimension or not r >= 0:
            raise ValueError('complete coefficients and nonnegative outward remainder required')
        if all(x.is_zero() for x in a) and r.is_zero() and c.rad().is_zero():
            return self.node(['constant', str(c.fmpq())])
        # Do not identify two equal-looking enclosure leaves. Their physical
        # errors need not be equal. Reuse the returned object for shared use.
        index = len(self.nodes)
        z = self.node(['leaf', index, pair(c), [[i, pair(x)] for i,x in enumerate(a) if not x.is_zero()], str(r.upper().fmpq())])
        self.leaf_provenance[str(z.index)] = provenance or {'role':'outward_model_leaf', 'dependency_unresolved':True}
        return z

    def variable(self, index, center=0, scale=1, *, provenance=None):
        a = [arb(0)]*self.dimension
        a[index] = arb(scale)
        return self.affine(center, a, provenance=provenance or {'parameter':self.names[index]})

    def coerce(self, value):
        if isinstance(value, Expression):
            if value.domain is not self:
                raise ValueError('one common physical parameter namespace required')
            return value
        if isinstance(value,(int,fmpq)):
            return self.node(['constant',str(fmpq(value))])
        return self.affine(value)

    def linear(self, terms):
        combined = {}
        constant = fmpq(0)
        for x, coefficient in terms:
            x = self.coerce(x)
            coefficient = fmpq(coefficient)
            n = self.nodes[x.index]
            if n[0] == 'constant':
                constant += coefficient*fmpq(n[1])
            else:
                rows = n[1] if n[0] == 'linear' and (self.flatten_limit is None or len(n[1])<=self.flatten_limit) else [[x.index,'1']]
                for i, c in rows:
                    combined[i] = combined.get(i,fmpq(0))+coefficient*fmpq(c)
        if constant:
            i = self.node(['constant',str(constant)]).index
            combined[i] = combined.get(i,fmpq(0))+1
        rows = [[i,str(c)] for i,c in sorted(combined.items()) if c]
        if not rows:
            return self.affine(0)
        if len(rows)==1 and rows[0][1]=='1':
            return Expression(self,rows[0][0])
        return self.node(['linear', rows])

    def multiply(self, x, y):
        x,y = self.coerce(x),self.coerce(y)
        factors=[]
        scalar=fmpq(1)
        for z in (x,y):
            n=self.nodes[z.index]
            if n[0]=='constant':
                scalar*=fmpq(n[1])
            elif n[0]=='product':
                factors.extend(n[1])
            else:
                factors.append(z.index)
        if not scalar:
            return self.affine(0)
        if not factors:
            return self.node(['constant',str(scalar)])
        z=Expression(self,factors[0]) if len(factors)==1 else self.node(['product',sorted(factors)])
        return z if scalar==1 else self.linear([(z,scalar)])

    def compiled(self, root):
        """Compile only ancestors; preserve DAG for later stronger support."""
        pending=[(root.index,False)]
        while pending:
            i,ready=pending.pop()
            if i in self.bounds:
                continue
            n=self.nodes[i];op=n[0]
            children=([v[0] for v in n[1]] if op=='linear' else n[1] if op=='product' else [n[1]] if op in ('exp','log','inverse','sqrt_positive') else [])
            if not ready and any(j not in self.bounds for j in children):
                pending.append((i,True))
                pending.extend((j,False) for j in reversed(children) if j not in self.bounds)
                continue
            d=self.backend
            if op=='constant':
                value=d.affine(arb(fmpq(n[1])))
            elif op=='leaf':
                a=[arb(0)]*d.dimension
                for j,v in n[3]:
                    a[j]=restore(v)
                value=d.affine(restore(n[2]),a,arb(fmpq(n[4])))
            elif op=='linear':
                value=sum((self.bounds[j]*arb(fmpq(c)) for j,c in n[1]),d.affine(0))
            elif op=='product':
                value=d.affine(1)
                for j in n[1]:
                    value=value*self.bounds[j]
            else:
                x=self.bounds[n[1]]
                if op=='exp': value=x.exp()
                elif op=='log': value=x.log()
                elif op=='inverse':
                    if len(n)==2: value=x.reciprocal()
                    else:
                        low=arb(fmpq(n[2]));safe=min(low,x.c.lower())
                        if not safe>0: raise ArithmeticError('positive inverse center and same-domain lower required')
                        value=x._unary(1/x.c,-1/x.c**2,(2/safe**3).upper())
                elif op=='sqrt_positive':
                    center=x.c.sqrt();safe=min(arb(fmpq(n[2])),center.lower())
                    if not safe>0: raise ArithmeticError('positive square-root center and same-domain lower required')
                    value=x._unary(center,1/(2*center),(1/(4*safe**3)).upper())
                else: raise ValueError('unknown expression operation')
            self.bounds[i]=value
        return self.bounds[root.index]

    def export(self, roots, *, include_bounds=True):
        models={}
        if include_bounds:
            for name,x in roots.items():
                v=self.compiled(x)
                models[name]=dict(c=pair(v.c),a=[[i,pair(c)] for i,c in enumerate(v.a.entries()) if not c.is_zero()],r=str(v.r.fmpq()))
        return dict(format='SHARED_EXPRESSION_DAG_V1',parameter_order=self.names,groups=self.groups,
            nodes=self.nodes,roots={k:v.index for k,v in roots.items()},affine_enclosures=models,
            leaf_provenance=self.leaf_provenance,higher_order_expression_retained=True,
            affine_support_preserves_all_higher_order_cancellation=False)

    @classmethod
    def from_payload(cls,payload):
        if payload['format']!='SHARED_EXPRESSION_DAG_V1':
            raise ValueError('known shared expression format required')
        d=cls([tuple(g) for g in payload['groups']],payload['parameter_order'])
        for i,n in enumerate(payload['nodes']):
            op=n[0]
            children=([v[0] for v in n[1]] if op=='linear' else n[1] if op=='product' else [n[1]] if op in ('exp','log','inverse','sqrt_positive') else [])
            if op not in ('constant','leaf','linear','product','exp','log','inverse','sqrt_positive') or any(type(j) is not int or not 0<=j<i for j in children):
                raise ValueError('acyclic supported expression required')
            if d.node(n).index!=i:
                raise ValueError('noncanonical duplicate node')
        d.leaf_provenance=payload['leaf_provenance']
        roots={k:Expression(d,i) for k,i in payload['roots'].items()}
        if any(type(i) is not int or not 0<=i<len(d.nodes) for i in payload['roots'].values()):
            raise ValueError('valid named roots required')
        return d,roots


class Expression(Taylor):
    # Subclass only for compatibility with the frozen scalar action adapter.
    # Arithmetic is always on the retained expression graph.
    def __init__(self,domain,index): self.domain,self.index=domain,index
    @property
    def c(self): return self.domain.compiled(self).c
    @property
    def a(self): return self.domain.compiled(self).a
    @property
    def r(self): return self.domain.compiled(self).r
    def enclosure(self): return self.domain.compiled(self).enclosure()
    def support(self): return self.domain.compiled(self).support()
    def linear_bound(self): return self.domain.compiled(self).linear_bound()
    def __add__(self,b): return self.domain.linear([(self,1),(b,1)])
    __radd__=__add__
    def __neg__(self): return self.domain.linear([(self,-1)])
    def __sub__(self,b): return self.domain.linear([(self,1),(b,-1)])
    def __rsub__(self,b): return self.domain.linear([(b,1),(self,-1)])
    def __mul__(self,b): return self.domain.multiply(self,b)
    __rmul__=__mul__
    def __truediv__(self,b): return self*self.domain.coerce(b).reciprocal()
    def __rtruediv__(self,b): return b*self.reciprocal()
    def __pow__(self,n):
        if type(n) is not int: return NotImplemented
        if n<0: return (self**(-n)).reciprocal()
        result=self.domain.affine(1)
        for _ in range(n): result=result*self
        return result
    def reciprocal(self):
        n=self.domain.nodes[self.index]
        if n[0]=='constant': return self.domain.node(['constant',str(1/fmpq(n[1]))])
        return self.domain.node(['inverse',self.index])
    def reciprocal_positive(self,lower):
        if not arb(lower)>0: raise ValueError('positive lower required')
        return self.domain.node(['inverse',self.index,str(arb(lower).lower().fmpq())])
    def sqrt_positive(self,lower):
        if not arb(lower)>0: raise ValueError('positive norm lower required')
        return self.domain.node(['sqrt_positive',self.index,str(arb(lower).lower().fmpq())])
    def exp(self): return self.domain.node(['exp',self.index])
    def log(self): return self.domain.node(['log',self.index])
    def _unary(self,*args):
        raise ValueError('name the exact unary expression; a Taylor bound alone is not expression authority')
