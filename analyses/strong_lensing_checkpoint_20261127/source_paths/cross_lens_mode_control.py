"""Freeze dimensionless broad-bend and stretch family; test contrasts at three lenses."""
from pathlib import Path
import json,sys
import numpy as np
from scipy.linalg import helmert
from scipy.optimize import least_squares
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'bhsm_environment_audit'/'pinned_extra'))
from r1_background_geometry import D
cs=json.loads((P/'cswa31_paths.json').read_text())
csR={x['feature_family']:(x['redshift'],np.array(x['EN_arcsec'])) for x in cs['source_families']}
heA=json.loads((P.parent/'bhsm_environment_audit'/'he0435_courbin_astrometry.json').read_text())['astrometry']['data']
heX=np.array([[r['delta_alpha'],r['delta_delta']] for r in heA]);heX=heX[:4]-heX[4]
jack1={k:(.609,np.array(v)) for k,v in {
 'S1a':[[.34,-1.50],[-.94,.68],[1.52,.19]],
 'S1b':[[-1.16,.22],[1.44,.88]],
 'S1c':[[-.43,-1.42],[-1.10,.67],[1.23,.88]],
 'S1d':[[-.14,-1.68],[-.57,.96]]}.items()}
jack2={'S2':(2.035,np.array([[-1.51,-1.78],[1.56,-1.19],[1.55,1.65],[-1.34,1.32]]))}
# Jackpot inner and outer knot measurements use the same Gavazzi native axes
# (neither is rotated); S3's independent astrometry not mixed across frames.
# HE: A,B,C train, D held out, anchored at A (index 0).
cases={
 'CSWA31':(.6828,{k:csR[k] for k in ('S0','S1','S2','S3')},{k:csR[k] for k in ('S4','S5')}),
 'Jackpot':(.222,jack1,jack2),
 'HE0435':(.4546,{'ABC':(1.693,heX[:3])},{'AD':(1.693,heX[[0,3]])})}
def build(N,tag,transfer=None):
    zl,train,test=cases[N]
    R=float(np.median(np.concatenate([np.linalg.norm(v,axis=1) for z,v in train.values()])))
    w={k:D(zl,z)/D(0,z) for k,(z,_) in (train|test).items()}
    def bend(x,b,s,g,angle):
        r=np.linalg.norm(x,axis=1);assert min(r)>0
        A=np.array([[np.cos(2*angle),np.sin(2*angle)],[np.sin(2*angle),-np.cos(2*angle)]])
        return b*((r/R)**s)[:,None]*x/r[:,None]+b/R*g*x@A.T
    def residual(args):
        return np.concatenate([(helmert(len(v))@(v-w[k]*bend(v,*args))).ravel() for k,(z,v) in train.items()])
    bo=R/max(w.values()) # scale initializer only
    if tag=='radial':
        unpack=lambda x:(x[0],x[1],0.,0.)
        low,hi,params=[.03*R,-.65],[12*R,.65],[[bo,s] for s in (-.4,0,.4)]
    elif transfer is None:
        unpack=lambda x:tuple(x)
        low,hi,params=[.03*R,-.65,0.,-np.pi],[12*R,.65,.45,2*np.pi],[[bo,s,.10,a] for a in np.linspace(0,np.pi,8,endpoint=False) for s in (-.3,.3)]
    else:
        s,g=transfer
        angles=np.linspace(0,np.pi,12,endpoint=False)
        if s is None:
            unpack=lambda x:(x[0],x[1],g,x[2])
            low,hi,params=[.03*R,-.65,-np.pi],[12*R,.65,2*np.pi],[[bo,t,a] for a in angles for t in (-.3,.3)]
        elif g is None:
            unpack=lambda x:(x[0],s,x[1],x[2])
            low,hi,params=[.03*R,0.,-np.pi],[12*R,.45,2*np.pi],[[bo,.1,a] for a in angles]
        else:
            unpack=lambda x:(x[0],s,g,x[1])
            low,hi,params=[.03*R,-np.pi],[12*R,2*np.pi],[[bo,a] for a in angles]
    o=min([least_squares(lambda x:residual(unpack(x)),t,bounds=(low,hi),max_nfev=2000,ftol=1e-11,xtol=1e-11,gtol=1e-11) for t in params],key=lambda z:z.cost)
    p=unpack(o.x)
    scores={}
    for k,(z,v) in test.items():
        a=v-w[k]*bend(v,*p)
        q=a[1:]-a[0]
        scores[k]=dict(anchor_closure_RMS=float(np.sqrt(np.mean((q*q).sum(axis=1)))),
            max_pair_source_gap=float(np.max(np.linalg.norm(a[None]-a[:,None],axis=2))),individual_anchor_miss=np.linalg.norm(q,axis=1).tolist())
    s=np.linalg.svd(o.jac,compute_uv=False)
    return dict(test=N,mode=tag,fit_parameters=[float(x) for x in p],train_radius_scale_arcsec=R,active_bounds=o.active_mask.tolist(),
       training_num_contrasts=len(o.fun),training_rms_source_component_arcsec=float(np.sqrt(np.mean(o.fun**2))),local_design_singular_values=s.tolist(),held_scores=scores)
rows=[]
# Quantitative restriction: transfer the dimensionless broad slope and
# fractional stretch only. Train amplitude and azimuth to nearer rays,
# not transport an absolute sky orientation.
master=build('CSWA31','radial_plus_stretch')
transfer=master['fit_parameters'][1:3]
for k in cases:
    rows.extend([build(k,'radial'),master if k=='CSWA31' else build(k,'radial_plus_stretch')])
    if k!='CSWA31':
        rows.extend([build(k,'freeze_CSWA_slope_and_stretch_fraction',transfer),
                     build(k,'freeze_CSWA_slope_only',(transfer[0],None)),
                     build(k,'freeze_CSWA_stretch_fraction_only',(None,transfer[1]))])
obj=dict(scope='Reduced one-plane projected modes, radially symmetric bending proportional to r^s and symmetric trace-free affine stretch. No ordinary foreground or secondary-plane propagation; mode family and transfer are diagnostic, not a physical BHSM law or full conventional comparator. Held scores are source-plane angular differences, not predicted image-plane locations. CSWA S4/S5 are held out; Jackpot tests S2 in same coordinate frame with updated z, not farthest S3; HE tests D with anchor A. Amplitude and angle calibrate on development per target, only fractional stretch and radial exponent transferred in joint transfer; in ablations the other shape parameter is refit from development.',models=rows)
(P/'cross_lens_mode_control.json').write_text(json.dumps(obj,indent=2)+'\n')
for a in rows:
 print(a['test'],a['mode'],a['fit_parameters'][:3],a['active_bounds'],a['training_rms_source_component_arcsec'],{k:round(v['anchor_closure_RMS'],6) for k,v in a['held_scores'].items()})
