from pathlib import Path
import json
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from radial_response import ScreenedExterior
data=json.loads((ROOT/'results/tracker_response.json').read_text())
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                     'savefig.dpi':180,'pdf.fonttype':42})
def save(fig,name):
    fig.savefig(ROOT/'figures'/f'{name}.pdf',bbox_inches='tight',
        metadata={'CreationDate':None,'ModDate':None,'Creator':'Reproducible Python calculation'})
    fig.savefig(ROOT/'figures'/f'{name}.png',bbox_inches='tight');plt.close(fig)
ex=ScreenedExterior()
rho=np.geomspace(.001,30,220);r=rho*ex.rV_pc
f=ex.radial(r);q,qp,qpp=ex.projected_quad(r)
fig,ax=plt.subplots(1,2,figsize=(9.4,3.4),layout='constrained')
ax[0].loglog(rho,f/f[0],color='#174f79',lw=2,label='Decaying quadrupole')
ax[0].loglog(rho[:90],rho[0]/rho[:90],':',color='#a95435',label=r'Deep $r^{-1}$ guide')
idx=170
ax[0].loglog(rho[idx:],f[idx]/f[0]*(rho[idx:]/rho[idx])**-3,'--',color='#237a70',label=r'Outer $r^{-3}$ guide')
ax[0].set(xlabel=r'$r/r_V$',ylabel=r'$f_2(r)/f_2(10^{-3}r_V)$');ax[0].legend(frameon=False,fontsize=9)
ax[1].semilogx(rho,r*qp/q,color='#174f79',lw=2,label='Projected phase slope')
ax[1].axhline(0,color='.6',ls=':');ax[1].axhline(-2,color='.6',ls=':')
ax[1].set(xlabel=r'Impact radius $b/r_V$',ylabel=r'$d\ln|q|/d\ln b$',ylim=(-2.1,.1))
ax[1].text(.002,-.3,'Deep: radially constant phase',fontsize=9)
ax[1].text(.15,-1.85,r'Outer: $b^{-2}$ phase',fontsize=9)
save(fig,'screened_transfer')

re=data['geometry']['rE_pc'];qref=float(ex.projected_quad(re)[0])
u=np.linspace(.3,2.1,150);s=np.sqrt(u*u+4);rp=(u+s)/2;rm=1/rp
h=.5*u*s+2*np.arcsinh(u/2)
def F(r):
    q,qp,qpp=ex.projected_quad(re*r)
    q,qp,qpp=np.array([q,qp*re,qpp*re**2])/qref
    ar=1+1/r**2;at=1-1/r**2
    return qpp/ar+(qp/r-4*q/r**2)/at+2*qp/(r**3*ar)*(1/ar-1/at)
delay=(ex.projected_quad(re*rp)[0]-ex.projected_quad(re*rm)[0])/qref
flux=F(rp)-F(rm)
K=delay/h-s*s/(4*h)*flux;Kstar=s**3/(u*h)
fig,ax=plt.subplots(1,2,figsize=(9.4,3.35),layout='constrained')
ax[0].plot(u,K/Kstar,label='Matched action response',color='#174f79',lw=2)
ax[0].axhline(1,label='Constant spin 2 = external shear',color='#a95435',ls='--')
ax[0].set(xlabel=r'Point-lens alignment $u$',ylabel=r'$\mathcal{K}_q/K_*$',ylim=(.999,1.002));ax[0].legend(frameon=False,fontsize=8)
ax[1].plot(u,delay*1e4,color='#174f79',lw=2)
ax[1].set(xlabel=r'Point-lens alignment $u$',ylabel=r'$10^4\,\delta\Delta\tau/\epsilon$ at $\cos2\varphi=1$')
ax[1].axhline(0,color='.6',ls=':')
save(fig,'tracker_blind_direction')

exp=data['experiment'];arr=np.load(ROOT/'results/design_arrays.npz')
raw=arr['signal'].reshape(9,6,2);res=arr['projected_signal'].reshape(9,6,2)
t=arr['times']
fig,ax=plt.subplots(1,2,figsize=(9.4,3.4),layout='constrained')
ax[0].plot(t,raw[:,4,0],'-o',color='#174f79',label='Raw flux response')
ax[0].plot(t,res[:,4,0],'-s',color='#a95435',label='After profiling nuisances')
ax[0].set(xlabel='Dimensionless scan coordinate',ylabel=r'$\partial\ln R/\partial\epsilon_+$');ax[0].legend(frameon=False,fontsize=8)
labels=['Joint pair','Astrometry','Apparent mass']
vals=[exp[k]['retained_signal_norm_fractions'] for k in ['full_pair','astrometry_only','mass_statistic_only']]
x=np.arange(3)
ax[1].bar(x-.17,[max(v[0],1e-16) for v in vals],width=.34,color='#174f79',label=r'$+$ orientation')
ax[1].bar(x+.17,[max(v[1],1e-16) for v in vals],width=.34,color='#a95435',label=r'$\times$ orientation')
ax[1].set_xticks(x,labels,fontsize=9);ax[1].set_yscale('log');ax[1].set_ylim(1e-16,1)
ax[1].set(ylabel='Retained response norm fraction');ax[1].legend(frameon=False,fontsize=8)
ax[1].text(.98,.07,'Roundoff floor at right',ha='right',transform=ax[1].transAxes,fontsize=8)
save(fig,'tracker_information')
print('Three PDF/PNG scientific figure pairs generated from declared model/results.')
