"""Exact source-to-conormal kernel checks. No physical state is selected.

Run with C:\\Python314\\python.exe -I -S. Only the inspected stdlib is used.
The Laurent variables X,Y,H stand for exp(k*x), exp(k*y), exp(k*h).
All assertions are polynomial identities over Q, not floating-point tests.
"""
import sys
if not (sys.flags.isolated and sys.flags.no_site and sys.flags.no_user_site):
    raise RuntimeError('Require -I -S')
from pathlib import Path
PREFIX = Path('C:/Python314').resolve()
if Path(sys.base_prefix).resolve() != PREFIX or any(
    not p or not (Path(p).resolve() == PREFIX or PREFIX in Path(p).resolve().parents)
    for p in sys.path
):
    raise RuntimeError('Unbounded Python startup path')
import argparse
from fractions import Fraction as F
import hashlib
import json

NAMES = ('X', 'Y', 'H', 'k', 'w', 'h', 'x', 'y')
ZERO = (0,) * len(NAMES)

class P:
    def __init__(self, value=0):
        self.d = {a:F(b) for a,b in value.items() if b} if isinstance(value,dict) else ({ZERO:F(value)} if value else {})
    def __add__(self, b):
        b = b if isinstance(b,P) else P(b)
        d = self.d.copy()
        for a,c in b.d.items(): d[a] = d.get(a,0)+c
        return P(d)
    __radd__ = __add__
    def __neg__(self): return P({a:-c for a,c in self.d.items()})
    def __sub__(self,b): return self + -(b if isinstance(b,P) else P(b))
    def __rsub__(self,b): return P(b)-self
    def __mul__(self,b):
        b = b if isinstance(b,P) else P(b)
        d = {}
        for a,c in self.d.items():
            for e,f in b.d.items():
                key = tuple(i+j for i,j in zip(a,e))
                d[key] = d.get(key,0)+c*f
        return P(d)
    __rmul__ = __mul__
    def __pow__(self,n):
        if n < 0:
            if len(self.d) != 1: raise ValueError('Only monomial inversion')
            a,c = next(iter(self.d.items()))
            return P({tuple(n*i for i in a):c**n})
        out = P(1)
        for _ in range(n): out = out*self
        return out
    def partial(self,name):
        j=NAMES.index(name); d={}
        for a,c in self.d.items():
            if a[j]:
                b=list(a); b[j]-=1; d[tuple(b)]=c*a[j]
        return P(d)
    def sub(self, repl):
        out=P()
        for a,c in self.d.items():
            term=P(c)
            for name,power in zip(NAMES,a):
                if power: term=term*repl.get(name,V[name])**power
            out=out+term
        return out

V={name:P({tuple(int(i==j) for i in range(len(NAMES))):1}) for j,name in enumerate(NAMES)}
X,Y,H,k,w,h,x,y = (V[n] for n in NAMES)
def dx(p): return p.partial('x')+k*X*p.partial('X')
def dh(p): return p.partial('h')+k*H*p.partial('H')
def dk(p): return p.partial('k')+x*X*p.partial('X')+y*Y*p.partial('Y')+h*H*p.partial('H')
def primitive_y(p):
    # Inputs here have no explicit y; integrate their exponential Laurent modes.
    out=P(); j=NAMES.index('Y')
    for a,c in p.d.items():
        term=P({a:c}); n=a[j]
        out=out+(term*k**-1*F(1,n) if n else term*y)
    return out
def endpoints_y(p): return p.sub({'Y':H,'y':h})-p.sub({'Y':P(1),'y':P(0)})
CHECKS=[]
def eq(name,a,b=0):
    residual=a-(b if isinstance(b,P) else P(b))
    if residual.d: raise AssertionError((name,residual.d))
    CHECKS.append({'name':name,'exact':True,'residual_terms':0})

def checks():
    S=H-H**-1; C=H+H**-1
    n0=H*Y**-1-Y*H**-1; nh=Y-Y**-1
    gm=(X-X**-1)*n0
    gp=nh*(H*X**-1-X*H**-1)
    # Both Green numerators have the denominator 2*k*S.
    eq('left bulk equation',-dx(dx(gm))+k*k*gm)
    eq('right bulk equation',-dx(dx(gp))+k*k*gp)
    eq('left Dirichlet face',gm.sub({'X':P(1),'x':P(0)}))
    eq('right Dirichlet face',gp.sub({'X':H,'x':h}))
    eq('diagonal continuity',(gm-gp).sub({'X':Y,'x':y}))
    eq('unit delta jump',(dx(gp)-dx(gm)).sub({'X':Y,'x':y}),-2*k*S)
    eq('outward source conormal at zero',-dx(gm).sub({'X':P(1),'x':P(0)}),-2*k*n0)
    eq('outward source conormal at h',dx(gp).sub({'X':H,'x':h}),-2*k*nh)
    eq('K0 length derivative numerator',dh(n0)*S-n0*dh(S),2*k*nh)
    eq('Kh length derivative numerator',dh(nh)*S-nh*dh(S),-k*C*nh)
    eq('K0 spectral derivative numerator',dk(n0)*S-n0*dk(S),
       (h-y)*(H*Y**-1+Y*H**-1)*S-h*C*n0)
    eq('Kh spectral derivative numerator',dk(nh)*S-nh*dk(S),
       y*(Y+Y**-1)*S-h*C*nh)
    a=S*C*k**-1*F(1,2)-2*h
    b=h*C-S*k**-1
    eq('K0 Gram integral',endpoints_y(primitive_y(n0*n0)),a)
    eq('Kh Gram integral',endpoints_y(primitive_y(nh*nh)),a)
    eq('cross Gram integral',endpoints_y(primitive_y(n0*nh)),b)
    # q = -N^-1 j for the auxiliary homogeneous native-conormal problem.
    # mu^2 is k^2-w^2. N^-1 numerators below use that exact determinant.
    eq('forced q0 kernel numerator',(k*C+w*S)*n0+2*k*nh,
       S*(k*(H*Y**-1+Y*H**-1)+w*n0))
    eq('forced qh kernel numerator',2*k*n0+(k*C-w*S)*nh,
       S*(k*(Y+Y**-1)-w*nh))
    eq('native boundary determinant',(k*C-w*S)*(k*C+w*S)-4*k*k,(k*k-w*w)*S*S)
    # Exact independent analytic-dual/source formula, via noncommuting words.
    def add(*ps):
        d={}
        for p in ps:
            for key,c in p.items(): d[key]=d.get(key,0)+c
        return {key:c for key,c in d.items() if c}
    def mul(*ps):
        out={():1}
        for p in ps:
            d={}
            for a,c in out.items():
                for b,e in p.items(): d[a+b]=d.get(a+b,0)+c*e
            out=d
        return out
    def atom(s): return {(s,):1}
    def neg(p): return {a:-c for a,c in p.items()}
    A,B,Cc,G,rr,bb=(atom(s) for s in ('A','B','C','G','r','b'))
    source=add(rr,neg(mul(Cc,bb)))
    dsource=add(atom('rY'),neg(mul(atom('CY'),bb)),neg(mul(Cc,atom('bY'))))
    direct=add(mul(atom('AY'),bb),mul(A,atom('bY')),mul(atom('BY'),G,source),
               mul(B,neg(mul(G,atom('DY'),G)),source),mul(B,G,dsource),atom('aY'))
    z=mul(G,source)
    adjoint=add(mul(atom('AY'),bb),mul(A,atom('bY')),mul(atom('BY'),z),atom('aY'),
                 mul(B,G,add(dsource,neg(mul(atom('DY'),z)))))
    if add(direct,neg(adjoint)): raise AssertionError('forced independent dual source')
    CHECKS.append({'name':'forced independent analytic-dual source formula','exact':True,'residual_terms':0})
    # Source-layer test is symbolic in t=w*h>0; no numerical mode/state is selected.
    # d_x exp(-w*x)=-w exp(-w*x), hence A phi=0 and (A* A+mu^2)phi=mu^2 phi.
    eq('factor-kernel amplitude',(dx(X)+w*X).sub({'k':-w}))
    eq('factor-kernel bulk response',(-dx(dx(X))+w*w*X).sub({'k':-w}))
    # Now X=exp(-w*x), H=exp(-w*h), with w>0. Integrate the actual norm.
    primitive=-F(1,2)*w**-1*X*X
    eq('factor-layer norm integral',primitive.sub({'X':H})-primitive.sub({'X':P(1)}),
       F(1,2)*w**-1*(1-H*H))
    return CHECKS

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',required=True); args=ap.parse_args()
    out=Path(args.out).resolve(); allowed=Path(__file__).resolve().parent
    if allowed not in out.parents: raise RuntimeError('Output must be a fresh child of artifact directory')
    out.mkdir(exist_ok=False)
    result={
      'schema':'bhsm.forced-event-kernel-recall.v83','classification':'exact owned product-factor component; conditional physical application',
      'checks':checks(),'physical_guard':2e-10,'method_tolerance_unchanged':2e-11,
      'numerical_physics_runs':0,'new_resolution':None,'physical_background_used':False,
      'source_kernel':'j_i = - integral_0^h K_i(y) f(y) dy',
      'K0':'sinh(k(h-y))/sinh(kh)','Kh':'sinh(ky)/sinh(kh)',
      'green':'sinh(k min(x,y))*sinh(k(h-max(x,y)))/(k sinh(kh))',
      'source_range_bound':'sum_j k_j ||j_j||^2 <= sum_j ||f_j||_L2^2 on the product component',
      'auxiliary_neumann_layer_trace_squared':'2*w*coth(w*h)/mu^4 for a unit factor-kernel source, w>0',
      'physical_neumann_condition_adopted':False,'physical_occupations_assigned':False,
      'complete_matched_observable_dependence_proved':False,'reconnection':None,'a_mu':None,'g_mu':None,
      'physical_total_uncertainty':None,
      'remaining':'common constrained coefficients and forced event relation on actual propagated source/dual range, with relative completion',
      'environment':{'executable':sys.executable,'base_prefix':sys.base_prefix,'sys_path':sys.path,'isolated':sys.flags.isolated,'no_site':sys.flags.no_site},
      'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'exact_checks':len(CHECKS),'out':str(out),'physical_result':False}))
if __name__=='__main__': main()
