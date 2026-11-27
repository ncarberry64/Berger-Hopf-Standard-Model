"""Controlled test of an achromatic lens-equivalent boundary, not a derivation from electrostatics."""
import json
import numpy as np
import jackpot_physical_geometry as geo
u,ep,cw,P=geo.u,geo.ep,geo.cw,geo.P
def frac(x):
    x2=np.minimum(np.asarray(x)**2,1.)
    return x2/(1+np.sqrt(1-x2))
def main():
    geom=geo.set_up('closed_R1',True)
    dk=geom['lens_distance_kpc']*u.asc
    b0=1.43*dk
    basic=u.basic
    f=ep.fn('separate')
    seed=np.array(json.loads((P/'jackpot_physical_geometry.json').read_text())['closed_R1']['separate']['fit'])
    F0=ep.fit(f,[seed]+u.starts)
    fitvec=f(F0.x,60,True)*1e3
    assert abs(np.linalg.norm(fitvec)-58.84288454319)<0.001,(fitvec,F0.x,seed)
    rows=[]
    for M in [5e9,1e10,2e10]:
      for R in [8,15,30,60,float('inf')]:
        def af(t):
          r2=np.sum(t*t,axis=1)
          b=dk*np.sqrt(r2)
          proj= (b/b0)**2 if np.isinf(R) else frac(b/R)/frac(b0/R)
          return t*(4*cw.G*M/(cw.c**2*dk*u.asc)*np.divide(proj,r2,out=np.zeros_like(r2),where=r2>0))[:,None]
        assert np.allclose(af(np.array([[1.43,0.],[0.,1.43]])),np.eye(2)*4*cw.G*M/(cw.c**2*dk*u.asc*1.43))
        u.basic=lambda t:basic(t)+af(t)
        sh=ep.fn('separate')
        F=ep.fit(sh,[F0.x]+u.starts)
        v=sh(F.x,60,True)*1e3
        rows.append(dict(Mref=M,R_kpc=None if np.isinf(R) else R,
                         inner_rms_mas=float(np.linalg.norm(F.fun)*1000/np.sqrt(14)),
                         far_residual_mas=float(np.linalg.norm(v)),
                         refitted_far_vector_shift_mas=float(np.linalg.norm(v-fitvec)),
                         frozen_far_vector_shift_mas=float(np.linalg.norm(sh(F0.x,60,True)*1e3-fitvec))))
    u.basic=basic
    result=dict(b0_kpc=b0,baseline=dict(inner_mas=float(np.linalg.norm(F0.fun)*1000/np.sqrt(14)),
        far_mas=float(np.linalg.norm(fitvec))),rows=rows)
    (P/'jackpot_boundary_shell_screen.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
