"""Actual released noisy-fit track, without using truth in its inference."""
from pathlib import Path
import json
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
PRODUCT=ROOT.parents[1]/'product'
sys.path.insert(0,str(PRODUCT))
from bhtracker import fit
from bhtracker.examples import make_example
raw,truth=make_example('nearby_motion')
r=fit(raw,starts=2)
out=ROOT/'results/product_example.json'
out.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
t=np.asarray(r['epochs_yr']);track=np.asarray(r['center_track_mas'])
sigma=np.asarray(r['center_track_sigma_mas'])
true=np.array(truth['center_mas'])+(t-raw['reference_epoch_yr'])[:,None]*np.array(truth['proper_motion_mas_yr'])
fig,axes=plt.subplots(1,2,figsize=(10,3.3),layout='constrained')
for j,(ax,name) in enumerate(zip(axes,['x','y'])):
    ax.errorbar(t,track[:,j],yerr=1.959964*sigma[:,j],fmt='o',color='#087f9b',label='Fit: local 95%')
    ax.plot(t,true[:,j],'--',color='#172b40',label='Synthetic truth')
    ax.set(xlabel='Observer epoch (year)',ylabel=f'{name} lens center (mas)')
    ax.ticklabel_format(useOffset=False,axis='x');ax.grid(alpha=.15)
axes[0].legend(frameon=False,fontsize=9)
fig.savefig(ROOT/'figures/product_track.pdf');fig.savefig(ROOT/'figures/product_track.png',dpi=180)
print(json.dumps({'status':r['status'],'mass':r['estimates']['mass_msun'],'chi2':r['chi2']}))
