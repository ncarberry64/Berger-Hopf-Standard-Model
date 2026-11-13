"""Small normalization/resolvent controls, never physical BHSM energies."""
from __future__ import annotations
import numpy as np
from scipy.linalg import eigh
from bhsm.interface.muon_native_impedance_energy_response import generalized_simple_mode_jets


def control_data():
    M=np.diag([1.3,.9,1.1]);H=np.diag([2.6,4.5,9.9])
    psi=np.array([1/np.sqrt(1.3),0,0]);E=2.
    Hx=np.array([[.2,.14,-.07],[.14,-.1,.03],[-.07,.03,.06]])
    Hy=np.array([[-.12,.05,.08],[.05,.07,-.02],[.08,-.02,.03]])
    Hxy=np.array([[.05,.01,-.02],[.01,.04,.006],[-.02,.006,-.01]])
    Mx=np.array([[.03,.02,0],[.02,-.01,.005],[0,.005,.02]])
    My=np.array([[-.02,0,.01],[0,.015,0],[.01,0,-.01]])
    Mxy=np.array([[.004,.003,0],[.003,.002,-.001],[0,-.001,-.003]])
    return H,M,psi,E,Hx,Hy,Hxy,Mx,My,Mxy


def execute_control():
    H,M,psi,E,Hx,Hy,Hxy,Mx,My,Mxy=control_data()
    out=generalized_simple_mode_jets(*control_data())
    def branch(x,y):
        h=H+x*Hx+y*Hy+x*y*Hxy;m=M+x*Mx+y*My+x*y*Mxy
        values,columns=eigh(h,m)
        # Match the analytically supplied control eigenline by overlap,
        # never assign a physical branch by sorted eigenvalue index.
        overlaps=abs(psi.conj()@M@columns)
        index=int(np.argmax(overlaps))
        return float(values[index]),float(overlaps[index]),float(abs(np.vdot(columns[:,index],m@columns[:,index])-1))
    fd=[]
    for h in (1e-3,5e-4,2.5e-4):
        plus=branch(h,0);minus=branch(-h,0)
        yplus=branch(0,h);yminus=branch(0,-h)
        mixed=(branch(h,h)[0]-branch(h,-h)[0]-branch(-h,h)[0]+branch(-h,-h)[0])/(4*h*h)
        fd.append(dict(step=h,E_x=(plus[0]-minus[0])/(2*h),E_y=(yplus[0]-yminus[0])/(2*h),
            E_xy=mixed,mixed_error=abs(mixed-out['E_xy'].real),
            x_error=abs((plus[0]-minus[0])/(2*h)-out['E_x'].real),
            y_error=abs((yplus[0]-yminus[0])/(2*h)-out['E_y'].real),
            min_branch_overlap=min(plus[1],minus[1],yplus[1],yminus[1]),
            max_M_normalization_residual=max(plus[2],minus[2],yplus[2],yminus[2])))
    fixed=generalized_simple_mode_jets(H,M,psi,E,Hx,Hy,Hxy,np.zeros_like(M),np.zeros_like(M),np.zeros_like(M))
    return dict(classification='ARITHMETIC_CONTROL_ONLY__NO_PHYSICAL_ENERGY',dimension=3,
        E=E,E_x=float(out['E_x'].real),E_y=float(out['E_y'].real),E_xy=float(out['E_xy'].real),
        checks=out['checks'],finite_differences=fd,
        fixed_M_mixed=float(fixed['E_xy'].real),moving_M_changes_mixed=float(abs(fixed['E_xy']-out['E_xy'])),
        M_x_norm=float(np.linalg.norm(Mx)),M_y_norm=float(np.linalg.norm(My)),M_xy_norm=float(np.linalg.norm(Mxy)),
        explicit_inverse_formed=False,selected_physical_mode=False),out
