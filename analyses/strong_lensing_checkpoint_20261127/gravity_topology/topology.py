"""Source-led HE 0435 lens topology. No fitted halo, gap parameter or quasar refitting."""
from pathlib import Path
import sys,contextlib,io,json
from functools import lru_cache
import numpy as np
from scipy.integrate import quad
from scipy.interpolate import CubicSpline
from matplotlib import pyplot as plt,colors,patheffects
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'bhsm_environment_audit'))
with contextlib.redirect_stdout(io.StringIO()):
    import he0435_joint_projected as jp
    from he0435_joint_field_control import d1,d2,d12,w1,w2,xrad,theta_g,g_photo,positions,names
star=jp.Obj('sersic')
I=np.eye(2)
g=(jp.sep*jp.axis)/(d1*xrad)
tg=theta_g/xrad
obs=np.array([positions[n]-positions['G'] for n in names])
@lru_cache(maxsize=4000)
def cyl(R):
    def fn(th):
        s,c=np.sin(th),np.cos(th)
        return star.rho(min(R/c,4.))*R**3*s/c**2/(1+s)
    return star.mt*(star.enclosed(R)+quad(fn,0,np.pi/2,epsabs=2e-10,epsrel=5e-7)[0])
def make(n):
    rd=np.geomspace(.00001,.08,n)
    spl=CubicSpline(rd,[cyl(float(r)) for r in rd])
    def local(theta):
        x=np.asarray(theta)*d1*xrad
        r=np.linalg.norm(x,axis=-1)
        rr=np.clip(r,rd[0],rd[-1])
        mr=np.where(r<rd[0],spl(rd[0])*(r/rd[0])**2,spl(rr))
        den=np.where(r<rd[0],2*spl(rd[0])/rd[0]**2,spl(rr,1)/rr)
        return radial(theta,np.zeros(2),mr,den)
    return local
def radial(theta,center,M,den):
    X=(np.asarray(theta)-center)*d1*xrad
    R2=np.sum(X*X,axis=-1)
    m2=np.divide(M,R2,out=np.asarray(den/2).copy(),where=R2>0)
    u=X/np.sqrt(np.where(R2>0,R2,1))[...,None]
    f=4*m2
    H=f[...,None,None]*I+4*(den-2*m2)[...,None,None]*(u[...,None]*u[...,None,:])
    return f[...,None]*X/xrad,H*d1
def env(theta):
    x=(np.asarray(theta)-g)*d1*xrad
    r2=np.sum(x*x,axis=-1)
    c,b=np.sqrt(r2+.025**2),np.sqrt(r2+jp.r200**2)
    C=np.pi*jp.gamma/2
    return radial(theta,g,C*r2*(1/(c+.025)-1/(b+jp.r200)), C*(1/c-1/b))
e0,h0=env([0,0])
def affine(theta):return e0+np.asarray(theta)@h0.T,h0
def noenv(theta):return np.zeros_like(theta),np.zeros((2,2))
def full_ray(t,s,environment):
    a,h=s(t)
    aa,hh=environment(t)
    ag,_=s(tg)
    aeg,_=environment(tg)
    x=d2*xrad*(t-tg)-d12*xrad*(a+aa-ag-aeg)
    rear,hr=g_photo.apply(x,False)
    beta=t-w1*(a+aa)-w2*rear/xrad
    J=I-w1*(h+hh)-w2*hr@(d2*I-d12*(h+hh))
    return beta,J
def batch(s,envm):
    tmp=[full_ray(t,s,envm) for t in obs]
    return np.array([a for a,b in tmp]),np.array([b for a,b in tmp])
def rms(s):return float(np.sqrt(np.mean(np.sum((s-s.mean(axis=0))**2,axis=1))))
def maxpair(s):return float(np.max(np.linalg.norm(s[:,None]-s,axis=-1)))
s,s2=make(850),make(500)
raw,J=batch(s,env)
flat,_=batch(s,affine)
none,_=batch(s,noenv)
oth,_=batch(s2,env)
assert np.max(np.abs(raw-oth))<5e-6
for t,j in zip(obs,J):
    fd=np.column_stack([(full_ray(t+e*1e-4,s,env)[0]-full_ray(t-e*1e-4,s,env)[0])/2e-4 for e in I])
    assert np.max(abs(j-fd))<8e-7, (j,fd,j-fd)
arch=json.loads((P.parent/'bhsm_environment_audit/he0435_joint_projected.json').read_text())
baseline=arch['runs'][-1]['LOS_half_length_Mpc']['0.8']
assert np.max(abs(raw-np.array(baseline['ordinary_sources_arcsec'])))<1e-5
K=w1*np.trace(h0)/2
shear=w1*np.hypot((h0[0,0]-h0[1,1])/2,h0[0,1])
e,H=env(obs)
k=w1*np.trace(H,axis1=-2,axis2=-1)/2
rem=(e-affine(obs)[0])*w1*1000
report=dict(scope='Conditional ordinary projected field from archived cored stellar input, associated group proxy and separate rear stellar G1. R1 readout is the archived same-input scalar comparison, not native BHSM field closure.',
    group_center_east_north_arcsec=g.tolist(),group_local_kappa=K,group_local_shear=shear,
    per_observed_ray={n:dict(theta=t.tolist(),group_kappa=float(kk),non_affine_group_mas=r.tolist(),source_arcsec=b.tolist(),J_det=float(np.linalg.det(j))) for n,t,kk,r,b,j in zip(names,obs,k,rem,raw,J)},
    four_ray_rms_arcsec=dict(full_group=rms(raw),constant_group_curvature=rms(flat),no_group=rms(none),archived_joint_R1=baseline['joint_R1_common_source_RMS_arcsec']),
    pairwise_source_difference_group_vs_no_group_mas=1000*maxpair(raw-none),
    pairwise_source_difference_group_vs_constant_curvature_mas=1000*maxpair(raw-flat),
    source_scatter_max_pair_arcsec=maxpair(raw),
    grid_refinement_arcsec=float(np.max(abs(raw-oth))),
    joint_R1_vs_isolated_R1_differential_microarcsec=baseline['joint_minus_isolated_after_G1_pairwise_source_shift_microarcsec'],
    delays='Not computed: four observed rays fail to return to common source.')
(P/'he0435_gravity_topology.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'text.color':'#19263c','axes.labelcolor':'#19263c','axes.titlecolor':'#19263c','axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(2,2,figsize=(10.8,9.1),layout='constrained')
fig.suptitle('HE 0435−1223  |  Gravity terrain across scales',x=.055,ha='left',fontsize=20,fontweight='bold')
def grid(lo,hi,n):
    u=np.linspace(lo,hi,n)
    return u,np.stack(np.meshgrid(u,u),-1)
def trace(A):return np.trace(A,axis1=-2,axis2=-1)
def label(a,t,points,c,offsets=None):
    offsets=offsets or [(6,5)]*len(points)
    for n,pt,d in zip(t,points,offsets):
        a.annotate(n,pt,xytext=d,textcoords='offset points',color=c,weight='bold',path_effects=[patheffects.withStroke(linewidth=2.5,foreground='white',alpha=.9)])
def xy(a):
    a.set_xlabel('East offset (arcsec)')
    a.set_ylabel('North offset (arcsec)')
    a.set_aspect('equal')
a=ax[0,0]; u,xyg=grid(-85,85,301); _,H=env(xyg)
im=a.pcolormesh(u,u,np.maximum(w1*trace(H)/2,1e-3),cmap='viridis',norm=colors.LogNorm(vmin=.006,vmax=.55),shading='auto')
a.contour(u,u,w1*trace(H)/2,levels=[.02,.04,.08,.16,.32],colors='white',linewidths=.65,alpha=.7)
a.plot(0,0,'w+',ms=9); a.plot(*g,marker='x',color='white',ms=7)
label(a,['Lens','Group'],[(0,0),g],'#163644')
a.set_title('1  The group shapes the broad terrain',loc='left',weight='bold')
fig.colorbar(im,ax=a,label='Group convergence  κ',shrink=.82);xy(a)
a=ax[0,1];u,xyg=grid(-2,2,301); _,Hs=s(xyg);_,Hg=env(xyg)
im=a.pcolormesh(u,u,w1*trace(Hs+Hg)/2,cmap='magma',norm=colors.LogNorm(vmin=.06,vmax=1.8),shading='auto')
a.scatter(*obs.T,color='white',edgecolors='#19263c',s=35,zorder=5);label(a,names,obs,'#19263c')
a.set_title('2  The lens galaxy shapes the local terrain',loc='left',weight='bold')
fig.colorbar(im,ax=a,label='Foreground convergence  κ',shrink=.82);xy(a)
a=ax[1,0];u,xyg=grid(-2,2,225); E,_=env(xyg)
im=a.pcolormesh(u,u,1000*w1*np.linalg.norm(E-affine(xyg)[0],axis=-1),cmap='cividis',shading='auto')
a.scatter(*obs.T,color='white',edgecolors='#19263c',s=35,zorder=5);label(a,names,obs,'#19263c')
a.set_title('3  What the smooth group approximation misses',loc='left',weight='bold')
fig.colorbar(im,ax=a,label='Extra bending (mas)',shrink=.82);xy(a)
a=ax[1,1]
centered=raw-raw.mean(axis=0)
a.scatter(*centered.T,c=['#005A82','#B45614','#276E53','#914A88'],s=58)
a.scatter(0,0,marker='+',c='#566378',s=68)
label(a,names,centered,'#19263c',[(6,-11),(6,5),(-15,6),(5,7)])
a.set_xlim(-1.13,1.13);a.set_ylim(-1.13,1.13);a.grid(alpha=.2)
a.set_xlabel('East of mean source (arcsec)');a.set_ylabel('North of mean source (arcsec)');a.set_aspect('equal')
a.set_title('4  The four rays still miss one common source',loc='left',weight='bold')
fig.text(.98,.996,'Fixed inputs • diagnostic only • no lens fit',ha='right',va='top',color='#526178',fontsize=9)
fig.savefig(P/'HE0435-1223_Gravity_Topology.png',dpi=183,facecolor='white',bbox_inches='tight',pad_inches=.18)
