"""Dipolar redistribution of a positive effective shell, not an electrostatic law."""
import json
import numpy as np
import jackpot_physical_geometry as geo
from jackpot_boundary_shell_screen import frac
u,ep,cw,P=geo.u,geo.ep,geo.cw,geo.P

def dipole_potential(t,R,d):
    x=np.linalg.norm(t,axis=-1)/R
    mu=np.sqrt(1-np.minimum(x*x,1))
    J=(1-mu)**2*(mu+2)/3
    return (1-mu-np.divide(J,x*x,out=np.zeros_like(x),where=x>0))*(t@d)/(2*R)
def dipole(t,R,d):
    r=np.linalg.norm(t,axis=-1)
    n=np.divide(t,r[:,None],out=np.zeros_like(t),where=r[:,None]>0)
    x=r/R
    mu=np.sqrt(1-np.minimum(x*x,1))
    J=(1-mu)**2*(mu+2)/3
    Jx=np.divide(J,x*x,out=np.zeros_like(x),where=x>0)
    return ((1-mu-Jx)[:,None]*d/2+Jx[:,None]*(n@d)[:,None]*n)/R
def main():
    pts=np.array([[.8,.2],[.4,-1.1],[2.0,-.3]])
    d=np.array([.6,.8]); h=1e-5
    fd=np.array([(dipole_potential(pts+h*e,1.3,d)-dipole_potential(pts-h*e,1.3,d))/(2*h) for e in np.eye(2)]).T
    assert np.allclose(fd,dipole(pts,1.3,d),atol=1e-9)
    dk=geo.set_up('closed_R1',True)['lens_distance_kpc']*u.asc
    basic=u.basic
    seed=np.array(json.loads((P/'jackpot_physical_geometry.json').read_text())['closed_R1']['separate']['fit'])
    f=ep.fn('separate'); ref=ep.fit(f,[seed]+u.starts)
    data={}
    for Rk,Mref in [(15.,1e10),(30.,2e10),(60.,2e10)]:
      R=Rk/dk
      K=4*cw.G*Mref/(cw.c**2*dk*u.asc*frac(1.43/R))
      results={}
      for axis,d in {'uniform_or_line_of_sight':[0.,0.],'east':[.5,0.],'west':[-.5,0.],'north':[0.,.5],'south':[0.,-.5]}.items():
        def extra(t):
          r=np.linalg.norm(t,axis=-1)
          r2=r*r
          return K*(np.divide(frac(r/R),r2,out=np.zeros_like(r),where=r2>0)[:,None]*t+dipole(t,R,np.array(d)))
        u.basic=lambda t:basic(t)+extra(t)
        ff=ep.fn('separate')
        F=ep.fit(ff,[ref.x]+u.starts)
        v=ff(F.x,60,True)*1e3
        results[axis]=dict(vector_mas=v.tolist(),far_mas=float(np.linalg.norm(v)),inner_mas=float(np.linalg.norm(F.fun)*1000/np.sqrt(14)))
      b=np.array(results['uniform_or_line_of_sight']['vector_mas'])
      for row in results.values():row['delta_from_uniform_vector_mas']=float(np.linalg.norm(np.array(row['vector_mas'])-b))
      data[str(Rk)]=results
    u.basic=basic
    (P/'jackpot_leading_edge_screen.json').write_text(json.dumps(data,indent=2)+'\n')
    for R,val in data.items():print(R,[(k,round(v['far_mas'],2),round(v['delta_from_uniform_vector_mas'],2),round(v['inner_mas'],2)) for k,v in val.items()])
if __name__=='__main__':main()
