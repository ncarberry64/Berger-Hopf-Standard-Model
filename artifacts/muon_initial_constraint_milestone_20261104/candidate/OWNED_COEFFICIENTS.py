"""Exact extracted pure coefficient functions; provenance in PROVENANCE.json.
The verifier supplies math, cmath, dot and the saved wall_trace_map.
No module top-level calculations or dependency imports.
"""

def intrinsic(x):
    q,v,m=x[:37],x[37:74],x[74:98]
    ellvec=[1.]+[(-1.)**k for k in range(1,13)]+[(-1.)**k for k in range(12)]+[0.]*12
    cs=(343/5)**(1/6)*cmath.exp(dot(q,ellvec));rad=(343/5)**(1/6)*cmath.exp(q[0])
    chi=math.pi/4+x[98]/cs;wr=(x[99]-x[98]*dot(v,ellvec))/cs
    ck0=[cmath.cos(4*k*chi) for k in range(1,13)];cj=[cmath.cos(4*k*chi) for k in range(12)]
    window=cmath.sin(2*chi)**2;u=dot(q[1:13],ck0);w=window*dot(q[13:25],cj);b=window*dot(q[25:37],cj)
    Ce=rad*cmath.exp(u+w);A=rad*cmath.exp(u+b)*cmath.cos(chi);B=rad*cmath.exp(u-b)*cmath.sin(chi)
    rho=A**3*B**3;R=A*B/cmath.sqrt(A*A+B*B);N=cmath.exp(dot(m[:12],ck0))
    beta=cmath.sin(4*chi)*dot(m[12:],cj);V=Ce*(wr+beta);ell=cmath.sqrt(N*N-V*V)
    gl=[0.]*38+ck0+[0.]*12
    gv=[-Ce*x[98]*e/cs for e in ellvec]+[Ce/cs]+[0.]*12+[Ce*cmath.sin(4*chi)*c for c in cj]
    n=[N*N/ell*l-V/ell*z for l,z in zip(gl,gv)]
    return dict(R=R,ell=ell,lam=A*A/(A*A+B*B),ell_rate=n)

def theta(p,reference):
    geo=[intrinsic(x) for x in p];ref=[intrinsic(x) for x in reference]
    lambdas=[geo[0]['lam'],geo[0]['lam']-ref[0]['lam']+ref[1]['lam']]
    result=[]
    for side,x in enumerate(p):
        vals=[[dot(row,x[100:180]) for row in f] for f in wm]
        for i in range(3):vals[i+2][i]+=math.sqrt(8)*(lambdas[side]-1)
        result.append([geo[side]['R'],geo[side]['ell']]+vals[0]+sum(vals[2:],[])+x[260:264])
    return result

def area_value_rate_gradient(x):
    """Original -rho*sqrt(N^2-V^2) and its62 rate/multiplier derivatives."""
    q,v,m=x[:37],x[37:74],x[74:98]
    ell=[1.]+[(-1.)**k for k in range(1,13)]+[(-1.)**k for k in range(12)]+[0.]*12
    dotf=lambda a,b:sum(u*w for u,w in zip(a,b))
    rad=(343/5)**(1/6)*cmath.exp(q[0]);cs=(343/5)**(1/6)*cmath.exp(dotf(q,ell))
    chi=math.pi/4+x[98]/cs;wr=(x[99]-x[98]*dotf(v,ell))/cs
    ck=[cmath.cos(4*k*chi) for k in range(1,13)];cj=[cmath.cos(4*k*chi) for k in range(12)]
    window=cmath.sin(2*chi)**2;u=dotf(q[1:13],ck);w=window*dotf(q[13:25],cj);b=window*dotf(q[25:37],cj)
    Ce=rad*cmath.exp(u+w);AA=rad*cmath.exp(u+b)*cmath.cos(chi);BB=rad*cmath.exp(u-b)*cmath.sin(chi)
    rho=AA**3*BB**3;N=cmath.exp(dotf(m[:12],ck));beta=cmath.sin(4*chi)*dotf(m[12:],cj)
    V=Ce*(wr+beta);proper=cmath.sqrt(N*N-V*V)
    gl=[0.]*38+ck+[0.]*12
    gv=[-Ce*x[98]*e/cs for e in ell]+[Ce/cs]+[0.]*12+[Ce*cmath.sin(4*chi)*c for c in cj]
    grad=[-rho*N*N/proper*l+rho*V/proper*w for l,w in zip(gl,gv)]
    return -rho*proper,grad
