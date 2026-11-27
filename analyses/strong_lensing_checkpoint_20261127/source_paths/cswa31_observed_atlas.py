"""Observation-only differential-deflection constraints, with no mass-field fit."""
import json
from pathlib import Path
from math import atan2
import numpy as np
from scipy.spatial import ConvexHull
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.lines import Line2D
P=Path(__file__).resolve().parent
d=json.loads((P/'cswa31_paths.json').read_text())
groups=d['source_families']; pts={f['feature_family']:np.array(f['EN_arcsec']) for f in groups}
F={}
for g in groups:
    k=g['feature_family']; x=pts[k]
    # For matching images the same unlensed coordinate cancels:
    # alpha_eff(x_i,z_s)-alpha_eff(x_j,z_s) = x_i-x_j.
    # alpha_eff already includes multi-plane ray ordering and source-distance factors.
    F[k]=dict(z=g['redshift'],disposition=g['use'],observations_EN_arcsec=x.tolist(),
        anchor=k+'a',relative_effective_deflection_to_a_EN_arcsec=(x[1:]-x[0]).tolist(),
        maximum_pair_difference_arcsec=g['max_pair_arcsec'])
assert sum(len(x['relative_effective_deflection_to_a_EN_arcsec']) for x in F.values())==12
u=pts['S1'][0]-pts['S0'][1]
v=pts['S1'][1]-pts['S0'][2]
cross=lambda d,e: d[...,0]*e[...,1]-d[...,1]*e[...,0]
ratio=float(np.linalg.norm(v)/np.linalg.norm(u))
ang=float(np.rad2deg(atan2(float(cross(u,v)),u@v)))
rng=np.random.default_rng(83915)
sample1=u+rng.normal(0,np.sqrt(2)*.14,(150000,2))
sample2=v+rng.normal(0,np.sqrt(2)*.14,(150000,2))
ra=np.linalg.norm(sample2,axis=-1)/np.linalg.norm(sample1,axis=-1)
an=np.rad2deg(np.arctan2(cross(sample1,sample2),(sample1*sample2).sum(axis=-1)))
out={'source':'https://doi.org/10.1051/0004-6361/202243600 Table 1 and Fig. 2',
     'scope':'Angular sky positions only. Measured pair differences constrain effective integrated deflection, not individual 3D trajectories or mass. Same-source astrometric IDs condition each equality; S4 and S5d have model-assisted confirmation. The pair list is an independent contrast basis within each feature family, not a statement about noise correlations.',
     'feature_families':F,'counts':dict(paths=18,source_galaxies=5,feature_families=6,anchor_contrasts=12),
     'spiral_local_shape':dict(first_patch='S0b to S1a',first_vector_EN_arcsec=u.tolist(),second_patch='S0c to S1b',
       second_vector_EN_arcsec=v.tolist(),second_over_first_length=ratio,second_relative_to_first_deg=ang,
       illustrative_ratio_16_84=np.percentile(ra,[16,84]).tolist(),
       illustrative_angle_16_84_deg=np.percentile(an,[16,84]).tolist(),
       uncertainty_scope='Illustrative independent isotropic 0.14 arcsec error per point, using the major positional modeling allowance in Wang Table 1. Covariance not supplied here; angular and stretch diagnostics describe one direction over a finite separation, not a full local shear tensor.')}
(P/'cswa31_observed_atlas.json').write_text(json.dumps(out,indent=2)+'\n')
print('Spiral',u,v,ratio,ang,out['spiral_local_shape']['illustrative_ratio_16_84'],out['spiral_local_shape']['illustrative_angle_16_84_deg'])
plt.rcParams.update({'font.family':'DejaVu Sans','text.color':'#182638','axes.labelcolor':'#26384c',
                     'xtick.color':'#52647a','ytick.color':'#52647a'})
pal=['#215f92','#348ba4','#20826f','#996100','#9168a9','#b43f55']
fig=plt.figure(figsize=(12.0,8.15),facecolor='#f3f6fb')
fig.text(.054,.950,'CASSOWARY 31',size=25,weight='bold')
fig.text(.055,.911,'An observation-first map of relative light bending',size=15,color='#415a73')
fig.text(.055,.862,'18 image positions     /     5 background galaxies     /     12 within-feature deflection comparisons',size=11,weight='bold',color='#294760')
ax=fig.add_axes([.075,.182,.51,.63])
ax.set_facecolor('#ffffff')
dev=np.vstack([pts[k] for k in ['S0','S1','S2','S3']]); h=ConvexHull(dev)
ax.add_patch(Polygon(dev[h.vertices],closed=True,facecolor='#dbe8f4',edgecolor='#91a9bf',ls=(0,(4,4)),lw=1.25,alpha=.64))
for i,(k,X) in enumerate(pts.items()):
    c=pal[i]
    for q in X[1:]:ax.plot(*np.stack([X[0],q]).T,ls=(0,(2,4)),lw=1.05,alpha=.55,c=c,zorder=2)
    ax.scatter(*X.T,s=62,marker='o' if i<4 else 'D',edgecolors=c,facecolors=c if i<4 else '#ffffff',linewidth=1.55,zorder=4)
    ax.scatter(*X[0],s=155,marker='o' if i<4 else 'D',edgecolors=c,facecolors='none',linewidth=1.2,zorder=3)
    labels={'S0':[(6,7),(-18,-13),(7,2),(5,7)],'S1':[(7,-11),(8,-12)],'S2':[(-9,7),(-10,-13),(10,2)],'S3':[(7,7),(6,7)],'S4':[(-12,8),(-7,-13),(5,6)],'S5':[(-5,-13),(7,-12),(7,6),(7,6)]}[k]
    for n,(q,dr) in enumerate(zip(X,labels)):
        ax.annotate(k+chr(97+n),q,xytext=dr,textcoords='offset points',size=7.8,color=c,weight='bold',zorder=7)
ax.scatter(0,0,s=115,marker='+',linewidth=2,c='#313c49',zorder=5)
ax.annotate('main galaxy',(0,0),xytext=(7,5),textcoords='offset points',size=8,color='#424f60')
ax.set(xlim=(-29,30),ylim=(-24,23),xlabel='East of main galaxy (arcsec)',ylabel='North of main galaxy (arcsec)')
ax.set_aspect('equal');ax.set_axisbelow(True);ax.grid(color='#e5ebf2',lw=.6)
for s in ax.spines.values():s.set_color('#9aabba')
fig.text(.615,.799,'How to read the map',size=14,weight='bold')
fig.text(.615,.770,'Filled: development paths   •   Hollow: held-out paths\nRinged symbols mark each feature’s reference image.\nDotted lines compare matched images; they are not ray tracks.\nThe shaded outline is coverage, not inferred gravity.',size=9.5,linespacing=1.6,va='top')
fig.text(.615,.620,'One spiral, two measured views',size=14,weight='bold')
fig.text(.615,.582,'Same bulge-to-blue-knot feature pair in two images',size=9.9,color='#415a73')
ins=fig.add_axes([.645,.349,.274,.206]);ins.set(xlim=(-1.22,2.45),ylim=(-1.54,1.13));ins.set_aspect('equal');ins.set_facecolor('#f3f6fb')
ins.axhline(0,color='#d1dbe5',lw=.8);ins.axvline(0,color='#d1dbe5',lw=.8)
for vec,col,txt,offset in [(u,pal[0],'View b',(4,6)),(v,pal[2],'View c',(-14,-15))]:
    ins.annotate('',xy=vec,xytext=(0,0),arrowprops=dict(arrowstyle='-|>',lw=2.6,color=col))
    ins.annotate(txt,vec,xytext=offset,textcoords='offset points',color=col,fontsize=9,weight='bold')
ins.set_xticks([-1,0,1,2]);ins.set_yticks([-1,0,1]);ins.tick_params(labelsize=8,length=3,pad=1)
ins.set_xlabel('Relative east offset (arcsec)',fontsize=8.5,labelpad=1)
for s in ins.spines.values():s.set_visible(False)
fig.text(.615,.247,f'View c shows {ratio:.2f}× the separation of view b.\nThe direction changes by {abs(ang):.0f}° in projection.',size=10.5,linespacing=1.5,weight='bold')
fig.text(.615,.164,'This measures relative distortion along one direction.\nIt does not identify the mass or its depth along the sightline.',size=9.2,linespacing=1.5,color='#415a73')
fig.text(.057,.068,'Source: Wang et al., A&A 668, A162 (2022), Table 1 and Fig. 2.  •  No mass model, 3D paths, or field interpolation.',size=9,color='#52647a')
fig.savefig(P/'CASSOWARY31_Observed_Path_Map.png',dpi=165,facecolor=fig.get_facecolor())
