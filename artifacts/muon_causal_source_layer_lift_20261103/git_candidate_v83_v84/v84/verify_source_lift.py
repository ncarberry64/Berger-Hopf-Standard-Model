"""Exact causal/source-to-native layer construction, no physical datum chosen.
Use the bounded C:\\Python314\\python.exe -I -S invocation; stdlib only.
"""
import sys
if not(sys.flags.isolated and sys.flags.no_site and sys.flags.no_user_site): raise RuntimeError('Require -I -S')
from pathlib import Path
PREFIX=Path('C:/Python314').resolve()
if Path(sys.base_prefix).resolve()!=PREFIX or any(not p or not(Path(p).resolve()==PREFIX or PREFIX in Path(p).resolve().parents) for p in sys.path): raise RuntimeError('Unbounded startup')
import argparse,hashlib,json
from fractions import Fraction as F

# Gaussian-rational noncommuting word algebra. i is central, i*i=-1.
def cleanword(word):
    n=word.count('i'); w=tuple(x for x in word if x!='i')
    return (('i',)+w if n%2 else w),(-1)**(n//2)
def add(*ps):
    out={}
    for p in ps:
        for w,c in p.items():
            w,s=cleanword(w);out[w]=out.get(w,F(0))+s*c
    return {w:c for w,c in out.items() if c}
def atom(x):return {(x,):F(1)}
def scale(c,p):return {w:F(c)*v for w,v in p.items() if c*v}
def mul(*ps):
    out={():F(1)}
    for p in ps:
        q={}
        for a,c in out.items():
            for b,d in p.items():
                w,s=cleanword(a+b);q[w]=q.get(w,F(0))+s*c*d
        out={w:c for w,c in q.items() if c}
    return out
def sub(a,b):return add(a,scale(-1,b))
def deriv(p,rules):
    out=[]
    for word,c in p.items():
        for j,s in enumerate(word):
            if s in rules:out.append(mul({word[:j]:c},rules[s],{word[j+1:]:F(1)}))
    return add(*out)
CHECKS=[]
def nc_eq(name,a,b=None):
    r=sub(a,b or {})
    if r:raise AssertionError((name,r))
    CHECKS.append({'name':name,'exact':True,'residual_terms':0})

# Laurent algebra for exponential kernel identities, with the same exact i.
NAMES=('X','Y','Z','H','E','L','k','w','v','lam','x','h','i')
ZERO=(0,)*len(NAMES);IJ=NAMES.index('i')
class P:
    def __init__(self,value=0):
        raw=value if isinstance(value,dict) else ({ZERO:F(value)} if value else {})
        self.d={}
        for a,c in raw.items():
            b=list(a);n=b[IJ];b[IJ]=n%2;sign=(-1)**(n//2)
            b=tuple(b);self.d[b]=self.d.get(b,F(0))+sign*F(c)
        self.d={a:c for a,c in self.d.items() if c}
    def __add__(self,b):
        b=b if isinstance(b,P) else P(b);d=self.d.copy()
        for a,c in b.d.items():d[a]=d.get(a,F(0))+c
        return P(d)
    __radd__=__add__
    def __neg__(self):return P({a:-c for a,c in self.d.items()})
    def __sub__(self,b):return self+-(b if isinstance(b,P) else P(b))
    def __rsub__(self,b):return P(b)-self
    def __mul__(self,b):
        b=b if isinstance(b,P) else P(b);d={}
        for a,c in self.d.items():
            for z,f in b.d.items():
                key=tuple(i+j for i,j in zip(a,z));d[key]=d.get(key,F(0))+c*f
        return P(d)
    __rmul__=__mul__
    def __pow__(self,n):
        if n<0:
            if len(self.d)!=1:raise ValueError('Only monomial inversion')
            a,c=next(iter(self.d.items()));return P({tuple(n*j for j in a):c**n})
        out=P(1)
        for _ in range(n):out=out*self
        return out
    def partial(self,name):
        j=NAMES.index(name);d={}
        for a,c in self.d.items():
            if a[j]:
                b=list(a);b[j]-=1;d[tuple(b)]=c*a[j]
        return P(d)
    def sub(self,repl):
        out=P()
        for a,c in self.d.items():
            t=P(c)
            for name,power in zip(NAMES,a):
                if power:t=t*repl.get(name,V[name])**power
            out=out+t
        return out
V={name:P({tuple(int(i==j) for i in range(len(NAMES))):F(1)}) for j,name in enumerate(NAMES)}
X,Y,Z,H,E,L,k,w,v,lam,x,h,I=(V[n] for n in NAMES)
def dx(p):return p.partial('x')+k*X*p.partial('X')-I*w*Y*p.partial('Y')-I*v*Z*p.partial('Z')-lam*L*p.partial('L')
def primitive_exp_x(p):
    out=P();j=NAMES.index('X')
    for a,c in p.d.items():
        term=P({a:c});n=a[j]
        out=out+(term*k**-1*F(1,n) if n else term*x)
    return out
def interval_exp_x(p):return p.sub({'X':H,'x':h})-p.sub({'X':P(1),'x':P(0)})
def eq(name,a,b=0):
    r=a-(b if isinstance(b,P) else P(b))
    if r.d:raise AssertionError((name,r.d))
    CHECKS.append({'name':name,'exact':True,'residual_terms':0})

def checks():
    i=atom('i');W,u,r,ell,s=(atom(n) for n in ('W','u','r','ell','s'))
    Du=scale(-1,mul(i,add(mul(W,u),r)))
    Dl=mul(i,add(mul(ell,W),s))
    pR=add(Du,mul(W,u));pL=add(Dl,mul(ell,W))
    nc_eq('native right partner from causal equation',pR,add(mul(add({():F(1)},scale(-1,i)),W,u),scale(-1,mul(i,r))))
    nc_eq('independent native left partner',pL,add(mul(add({():F(1)},i),ell,W),mul(i,s)))
    Wd,rd,sd=(atom(n) for n in ('DW','Dr','Ds'))
    rules={'u':Du,'ell':Dl,'W':Wd,'r':rd,'s':sd}
    Pu=add(scale(-1,deriv(pR,rules)),mul(W,pR))
    lP=add(scale(-1,deriv(pL,rules)),mul(pL,W))
    right=add(scale(2,mul(W,W,u)),scale(-1,mul(add({():F(1)},scale(-1,i)),Wd,u)),mul(W,r),mul(i,rd))
    left=add(scale(2,mul(ell,W,W)),scale(-1,mul(add({():F(1)},i),ell,Wd)),mul(s,W),scale(-1,mul(i,sd)))
    nc_eq('complete variable-W native right source',Pu,right)
    nc_eq('complete variable-W independent left source',lP,left)
    nc_eq('causal product-current balance',add(mul(Dl,u),mul(ell,Du)),add(mul(i,s,u),scale(-1,mul(i,ell,r))))
    green=add(scale(-1,mul(ell,pR)),mul(pL,u))
    nc_eq('native product Green endpoint',green,add(scale(2,mul(i,ell,W,u)),mul(i,ell,r),mul(i,s,u)))
    nc_eq('native Green bulk and endpoint balance',deriv(green,rules),sub(mul(ell,Pu),mul(lP,u)))
    uy,wy,ry,eu=(atom(n) for n in ('uY','WY','rY','E_u'))
    Duy=add(scale(-1,mul(i,add(mul(W,uy),mul(wy,u),ry))),scale(-1,eu))
    actualpy=add(Duy,mul(W,uy),mul(wy,u),eu)
    nc_eq('total right partner source including clock-connection motion',actualpy,
          add(mul(add({():F(1)},scale(-1,i)),add(mul(W,uy),mul(wy,u))),scale(-1,mul(i,ry))))
    ly,sy,el=(atom(n) for n in ('ellY','sY','E_ell'))
    Dly=add(mul(i,add(mul(ly,W),mul(ell,wy),sy)),scale(-1,el))
    nc_eq('total independent left partner source',add(Dly,mul(ly,W),mul(ell,wy),el),
          add(mul(add({():F(1)},i),add(mul(ly,W),mul(ell,wy))),mul(i,sy)))
    # Exact unitary causal column and full off-diagonal constant source.
    eq('causal column equation',I*dx(Y)-w*Y)
    eq('off-diagonal causal source kernel',(I*dx(Z-Y)-w*(Z-Y)),(v-w)*Z)
    eq('degenerate source kernel',I*dx(-I*x*Y)-w*(-I*x*Y),Y)
    eq('zero entering trace of source kernel',(Z-Y).sub({'Y':P(1),'Z':P(1)}))
    # Exact source correlation with the native graph, NOT a homogeneous native inverse.
    eq('causal column native normal',dx(Y)+w*Y,(1-I)*w*Y)
    eq('native volume source of causal column',-dx(dx(Y))+k*k*Y,(k*k+w*w)*Y)
    S=H-H**-1;C=H+H**-1
    n0=H*X**-1-X*H**-1;nh=X-X**-1
    pr0=(dx(n0)+I*w*n0)*Y;prh=(dx(nh)+I*w*nh)*Y
    eq('entered source integral primitive',dx(pr0),(k*k+w*w)*n0*Y)
    eq('far source integral primitive',dx(prh),(k*k+w*w)*nh*Y)
    I0=k*C-I*w*S-2*k*E;Ih=(k*C+I*w*S)*E-2*k
    ep={'X':H,'Y':E};start={'X':P(1),'Y':P(1)}
    eq('entered complete bulk-source integral',pr0.sub(ep)-pr0.sub(start),I0)
    eq('far complete bulk-source integral',prh.sub(ep)-prh.sub(start),Ih)
    eq('entered conormal equality with correlated native source',(k*C-w*S)-2*k*E-I0,-(1-I)*w*S)
    eq('far conormal equality with correlated native source',-2*k+(k*C+w*S)*E-Ih,(1-I)*w*E*S)
    # Exact positive-form comparison: N-mu^2 K* K is the Gram of A K.
    # This proves the bulk-source dual-energy bound, not an L2 trace inverse.
    ga=S*C*k**-1*F(1,2)-2*h;gb=h*C-S*k**-1
    AK0=dx(n0)+w*n0;AKh=dx(nh)+w*nh
    eq('entered source Gram energy remainder',interval_exp_x(primitive_exp_x(AK0*AK0)),
       (k*C-w*S)*S-(k*k-w*w)*ga)
    eq('cross source Gram energy remainder',interval_exp_x(primitive_exp_x(AK0*AKh)),
       -2*k*S-(k*k-w*w)*gb)
    eq('far source Gram energy remainder',interval_exp_x(primitive_exp_x(AKh*AKh)),
       (k*C+w*S)*S-(k*k-w*w)*ga)
    # Native-layer overlap: denominator lam+i*w; all zero limits handled analytically.
    eq('positive-face normal-layer integral',dx(1-L*Y),(lam+I*w)*L*Y)
    # For the reflected integral, an x-dependent exp(+lam*x) is L^-1.
    eq('negative-face normal-layer integral',dx(Y*L**-1),(-I*w+lam)*Y*L**-1)
    eq('normal-layer positive and negative norm numerators',(1-L*E)*(1-L*E**-1),(E-L)*(E**-1-L))
    # Divided-difference moment follows by integrating the exact source kernel.
    # This equality explicitly retains both spectral channels rather than setting v=w.
    eq('off-diagonal normal-layer source integral numerator',
       (1-L*Z)*(lam+I*w)-(1-L*Y)*(lam+I*v),
       (lam+I*w)-(lam+I*v)-L*Z*(lam+I*w)+L*Y*(lam+I*v))
    return CHECKS

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args()
    here=Path(__file__).resolve().parent;out=Path(a.out).resolve()
    if here not in out.parents:raise RuntimeError('Fresh artifact child output required')
    out.mkdir(exist_ok=False)
    result={'schema':'bhsm.causal-source-layer-lift.v84','checks':checks(),
      'classification':'exact local native/causal source identities and conditional product-patch incoming lift',
      'right_partner':'p_R=(1-i)W u-i r','left_partner':'p_L=(1+i)ell W+i s',
      'native_right_source':'A* A u=2 W^2 u-(1-i)[D,W]u+W r+i D r',
      'normal_layer_lift':'m_a(u)=J_a(w_a) g_a-i integral T_a(w_a;t) r_a(t) dt',
      'four_column_bound_squared':8,'bound_scope':'normalized four-column input, constant transported W0, homogeneous causal equation, positive/negative spectral layer weight |W0|^(1/2)',
      'native_bulk_source_energy_bound':'||N^(-1/2) j_bulk|| <= ||f||/mu; positive product component, mu>0, no inherited/event load omitted in physical use',
      'physical_input_lift_realized':False,'native_factor_partner_is_D5_normal_companion':False,
      'independent_left_preserved':True,'mixed_native_relative_terms_eliminated':False,
      'actual_shared_physical_background':False,'new_occupations':False,'physical_guard':2e-10,
      'physical_reconnection':None,'physical_a_mu':None,'physical_g_mu':None,'total_uncertainty':None,
      'remaining':'prescribed joint comparison/domain identification g=J U_as P_as G g_as and event-generated retained/released graph, with nonconstant coefficient and total source jets',
      'new_numerical_physics_runs':0,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      'environment':{'executable':sys.executable,'base_prefix':sys.base_prefix,'sys_path':sys.path,'isolated':sys.flags.isolated,'no_site':sys.flags.no_site}}
    (out/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'exact_checks':len(CHECKS),'physical_input_realized':False,'out':str(out)}))
if __name__=='__main__':main()
