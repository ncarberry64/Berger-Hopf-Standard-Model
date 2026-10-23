from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                     'savefig.dpi':180,'pdf.fonttype':42})
out=ROOT/'figures';out.mkdir(exist_ok=True)

def save(fig,name):
    fig.savefig(out/(name+'.pdf'),bbox_inches='tight',
                metadata={'CreationDate':None,'ModDate':None,'Creator':'Reproducible Python calculation'})
    fig.savefig(out/(name+'.png'),bbox_inches='tight')
    plt.close(fig)

kap=np.linspace(0,1,301);a=np.linspace(.5,1.5,301)
fig,ax=plt.subplots(1,2,figsize=(9.6,3.35),layout='constrained')
ax[0].plot(kap,(1+kap**2)/2,color='#174f79',lw=2.4)
ax[0].axhline(.5,color='.5',ls=':',lw=1)
ax[0].set(xlabel=r'Absolute Kähler cosine $\kappa$',ylabel=r'Charged power fraction $f_2$',
          xlim=(0,1),ylim=(.45,1.04))
ax[0].text(.04,.92,'Stationary-nodal degree-two states',fontsize=9)
lower=6+2*a*a;upper=4+4*a*a
ax[1].fill_between(a,np.minimum(lower,upper),np.maximum(lower,upper),color='#b7d7ea',alpha=.8)
ax[1].plot(a,lower,label=r'$\kappa=0$',lw=2,color='#237a70')
ax[1].plot(a,upper,label=r'$\kappa=1$ (Hopf fibre)',lw=2,color='#a95435')
ax[1].axvline(1,color='.5',ls=':',lw=1)
ax[1].set(xlabel=r'Inverse relative fibre scale $a$',ylabel=r'$R^2\,\mathscr{R}_a$ at fixed $R$')
ax[1].legend(frameon=False,fontsize=9,loc='upper left')
save(fig,'hopf_bound')

j=json.loads((ROOT/'results/rotation_response.json').read_text())
pairs=j['all_coordinate_pairs_at_z1']
fig,ax=plt.subplots(1,2,figsize=(9.6,3.4),layout='constrained')
values=np.array([p['omega2_for_1e_minus3_each'] for p in pairs])
labels=[str(p['i'])+','+str(p['j']) for p in pairs]
ax[0].bar(np.arange(len(pairs)),abs(values),color=np.where(values>=0,'#237a70','#a95435'))
ax[0].set_yscale('log');ax[0].set_xticks(np.arange(len(pairs)),labels,rotation=65,fontsize=8)
ax[0].set(xlabel='Anchor pair (zero-based indices)',ylabel=r'$|\omega^{(2)}|$, each coefficient $10^{-3}$')
ax[0].text(.02,.96,'Green: positive; brown: negative',transform=ax[0].transAxes,va='top',fontsize=8)
rs=[r for r in j['segments'] if r['z_a']==0]
ax[1].plot([r['z_b'] for r in rs],[r['omega2']/1e-18 for r in rs],'-o',color='#174f79')
ax[1].set(xlabel='Source redshift',ylabel=r'$\omega^{(2)}_{m r}$ in units of $10^{-18}$')
ax[1].axhline(0,color='.7',lw=.8)
save(fig,'state_response')
print('Generated two PDF/PNG figure pairs from exact geometry and recorded response.')
