"""Exploratory equal-potential QUMOND-style collective correction, not full BHSM.
Keep the independently located sources. Retain their contributions plus precisely
the inclusion-exclusion joint correction, not a second copy of their gravity.
Fixed sky positions and stellar masses; no fit to Jackpot's residual.
"""
import json
import numpy as np
from scipy.integrate import quad
from scipy.fft import rfft2, irfft2, fftfreq, rfftfreq
from scipy.ndimage import map_coordinates
from pathlib import Path
from numpy.polynomial.legendre import leggauss
c,G=299792.458,4.30091727e-6
H0,Om,z=70,.3,.2219305
arad=np.pi/648000
arat=arad
root=Path(__file__).resolve().parent
def chi(z):
    return c/H0*quad(lambda x:1/np.sqrt(Om*(1+x)**3+1-Om),0,z)[0]
dk=1000*chi(z)/(1+z)*arad
# Archived curvature-scale ansatz uses aH=c²/R_H(z); screen at declared Ωk=-.018.
aH=c*H0*np.sqrt(.018)*(1+z)/1000
centers=np.array([(0.,0.),(-42.090,33.410),(68.634,-18.458)])*dk
# Use exact catalog sky coordinates rather than rounded centers above.
radec=np.array([[146.73617048,10.11469530],[146.72429349593472,10.12397580741827],[146.75563948937295,10.109567005967516]])
centers=(radec-radec[0])*3600*dk*[np.cos(np.deg2rad(radec[0,1])),1]
A=np.array([[-3.,-1.91],[1.03,.87]])
ab=A[0]-A[1]
star_near=[4.78e10,7.49e10]
main_m=10**np.array([11.13,11.52])
scale=np.array([[.066,.50],[.082,6.05]])*dk
def mt(r,j):
    if j==0:
        return 1.6e9*(r/np.hypot(r,.05))**3+sum(m*2/np.pi*(b*np.arctan(r/b)-a*np.arctan(r/a))/(b-a) for m,(a,b) in zip(main_m,scale))
    return star_near[j-1]*(r/np.hypot(r,3.))**3
def response(x,y,z,scale):
    g=np.sqrt(x*x+y*y+z*z)
    # Stable form sqrt((1+sqrt(1+4(aH/g)^2))/2)-1; cap g=0 only for arithmetic.
    t=scale/np.maximum(g,1e-100)
    q=2*t*t/(np.hypot(1,2*t)+1)
    h=q/(1+np.sqrt(1+q))
    return np.array([h*x,h*y])
def integrate(box,n,limit,nq,depth,scale_a=1,project=True,nearby=True,field_file=None):
    step=2*box/n
    grid=np.arange(n)*step-box
    X,Y=np.meshgrid(grid,grid,indexing='ij',sparse=True)
    parts=[(X-x,Y-y) for x,y in (centers if nearby else centers[:1])]
    radii=[xx*xx+yy*yy for xx,yy in parts]
    xx,ww=leggauss(nq); H=np.arcsinh(limit/5.)
    pi=np.zeros((2,n,n))
    for hh,weight in zip(H*xx,H*ww):
        d=5*np.sinh(hh); wt=weight*5*np.cosh(hh)
        V=[]
        for i,((x,y),rsq) in enumerate(zip(parts,radii)):
            l=d-depth[i]
            r=np.sqrt(rsq+l*l)
            r=np.maximum(r,1e-10)
            f=G*mt(r,i)/r**3
            V.append((f*x,f*y,f*l))
        T=[sum(v[i] for v in V) for i in range(3)]
        pi+=wt*(response(*T,aH*scale_a)-sum(response(*v,aH*scale_a) for v in V))
    pos=(A*dk+box).T/step
    G0=np.array([map_coordinates(field,pos,order=3) for field in pi]).T*2/(c*c*arad)
    if project:
        kx,ky=fftfreq(n)[:,None],rfftfreq(n)[None,:]
        denom=kx*kx+ky*ky
        denom[0,0]=1
        # Periodic Helmholtz projection; report box and integration convergence.
        pot=(kx*rfft2(pi[0])+ky*rfft2(pi[1]))/denom
        fields=[irfft2(k*pot,s=(n,n)) for k in [kx,ky]]
        def alpha(a):
            return np.array([map_coordinates(F,((a*dk+box)/step).T,order=3) for F in fields]).T*2/(c*c*arad)
        G1=alpha(A)
        if field_file:
            np.savez_compressed(field_file, field=np.stack(fields)*2/(c*c*arad), step=step, box=box,
                                dk=dk, depths=np.array(depth))
        eps=.2*np.eye(2)
        J=(alpha(eps)-alpha(-eps)).T/.4
    else:G1=G0; J=np.zeros((2,2))
    v=G1[0]-G1[1]
    def out(zs):
        w=1-chi(z)/chi(zs)
        return dict(diff_mas=(1000*w*v).tolist(), norm_mas=float(1000*w*np.linalg.norm(v)), local_kappa=float(w*np.trace(J)/2),local_shear=(w*np.array([(J[0,0]-J[1,1])/2,(J[0,1]+J[1,0])/2])).tolist(),local_affine_vector_mas=(1000*w*J@ab).tolist(), beyond_local_affine_mas=float(1000*w*np.linalg.norm(v-J@ab)), raw_force_proxy_mas=float(1000*w*np.linalg.norm(G0[0]-G0[1])))
    return dict(box_kpc=box,cell_kpc=step,n=n,los_kpc=limit,nq=nq,depths_kpc=depth,pair={str(s):out(s) for s in [.609,2.035,5.975]})
def main():
    low=integrate(260,96,350,36,[0,0,0],nearby=False)
    assert low['pair']['5.975']['norm_mas']==0
    rows=[]
    for par in [(400,640,2200,92,[0,0,0]),(400,896,2200,108,[0,0,0]),(650,1024,3500,108,[0,0,0]),(650,1024,3500,116,[0,-200,200]),(650,1024,3500,116,[0,-500,500])]:
        r=integrate(*par);rows.append(r);print(r,flush=True)
        (root/'coupled_well_screen.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
