"""Exact cubic center directions plus complete endpoint perturbation balls."""
import numpy as np
from flint import arb


def displacement_directions(left,right,rates,step,chart,low,high):
    """Enclose Hermite image minus the half-chart line without boxing its bend.

    Columns 0..5 are constant, shared t/t2/t3, and two longitudinal inputs;
    6..79 and 80..153 retain the two full transverse balls; 154..251 are
    uniform rate-error boxes. The quadratic parameter is shifted from [0,1].
    Enlarging the three time powers independently is safe and explicit.
    """
    a,b,half=chart
    low,high=arb(low),arb(high)
    if not (0<=low<high<=1 and arb(half)/2<=low and high<=arb(half+1)/2):
        raise ValueError('time cell inside its local chart required')
    mid,rad=(low+high)/2,(high-low)/2
    A=lambda t:1-3*t*t+2*t**3
    B=lambda t:3*t*t-2*t**3
    C=lambda t:step*t*(1-t)**2
    D=lambda t:step*t*t*(1-t)
    amax,bmax=A(low).upper(),B(high).upper()
    cmax=max(C(low).upper(),C(high).upper())
    dmax=max(D(low).upper(),D(high).upper())
    if low<=arb(1)/3<=high:cmax=max(cmax,C(arb(1)/3).upper())
    if low<=arb(2)/3<=high:dmax=max(dmax,D(arb(2)/3).upper())
    rows=[]
    for i in range(98):
        x,y=left['x'][i],right['x'][i];delta=y-x
        f,g=rates[0][i].mid(),rates[1][i].mid()
        chord=b['x'][i]-a['x'][i]
        c0=x-a['x'][i]+half*chord
        c1=step*f-2*chord
        c2=3*delta-step*(2*f+g)
        c3=step*(f+g)-2*delta
        p0=c0+mid*(c1+mid*(c2+mid*c3))
        p1=rad*(c1+2*mid*c2+3*mid*mid*c3)
        p2=rad*rad*(c2+3*mid*c3)
        p3=rad**3*c3
        rate_error=(cmax*rates[0][i].rad()+dmax*rates[1][i].rad()).upper()
        rows.append([p0+p2/2,p1,p2/2,p3,
                     amax*left['scaled'][i][0],bmax*right['scaled'][i][0]]+
                    [amax*v for v in left['scaled'][i][1:]]+
                    [bmax*v for v in right['scaled'][i][1:]]+
                    [rate_error if i==j else arb(0) for j in range(98)])
    return np.array(rows,dtype=object)
