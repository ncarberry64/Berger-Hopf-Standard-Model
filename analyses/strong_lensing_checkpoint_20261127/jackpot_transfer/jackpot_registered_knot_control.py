"""Fixed profile, orientation hypotheses ranked solely on Gavazzi ring knots."""
from pathlib import Path
import ast,json,numpy as np
from astropy.io import fits
from astropy.wcs import WCS
P=Path(__file__).resolve().parent
obs=P.parent/'visible_mass_envelope_20261126/external_weak/jackpot_neighbor'
f=obs/'u_phot/f814w.fits'
with fits.open(f) as h:
    im=h[0].data.copy(); ww=WCS(h[0].header)
    md=ww.pixel_scale_matrix.tolist()
    px=np.array(ww.all_world2pix(146.73617048,10.11469530,0))
    pixscale=float(np.sqrt(abs(np.linalg.det(md)))*3600)
assert .01<pixscale<.1
src=obs/'inner_rings_shared_well.py'
groups=next(ast.literal_eval(n.value) for n in ast.parse(src.read_text()).body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='GROUPS')
d=np.deg2rad(180-161.348)
rot=np.array([[-np.sin(d),-np.cos(d)],[-np.cos(d),np.sin(d)]])
rings=[np.array(t)@rot.T for t in groups]
# Confirm the archived image WCS covers all registered knot positions.
kn=np.vstack(rings)
pa,pd=146.73617048,10.11469530
xy=np.column_stack(ww.all_world2pix(pa+kn[:,0]/(3600*np.cos(np.deg2rad(pd))),pd+kn[:,1]/3600,0))
assert (xy>=0).all() and (xy<np.array(im.shape[::-1])).all()
sg=P/'jackpot_s3_lens_geometry.py'
g={'__file__':str(sg),'__name__':'geom'}
exec(compile(sg.read_text().split('out={}',1)[0],str(sg),'exec'),g)
j,z,z1,z2,z3,w,th=(g[k] for k in ('j','z','z1','z2','z3','w','th'))
out={}
for label,ms in [('Chabrier',[10.85,11.27]),('Salpeter',[11.13,11.52]),('CA14 power control',None)]:
  rows={}
  for tag,f in g['pats'].items():
    if ms is not None:K=lambda r:g['stage1'](r,label,ms)
    else:K=lambda r:(2-1.027)*.5*(g['R0']/r)**1.027
    mat=g['matrix'](f(-27.20))
    sh=mat.T@np.diag([.069,-.069])@mat
    def main(t): return np.array([g['ell'](v,.946,f(30.6),K) for v in t])+t@sh
    def unit(v): return v/np.maximum(1e-12,np.linalg.norm(v,axis=1))[:,None]
    e1=[t-main(t) for t in rings[:4]]
    c1=np.mean([t.mean(axis=0) for t in e1],axis=0)
    def prop(t,zs):
      a=main(t)
      b=.161*unit(t-a-c1)
      return t-a*w(z,zs)/w(z,z1)-b*w(z1,zs)/w(z1,z2)
    e2=prop(rings[4],z2)
    c2=e2.mean(axis=0)
    e3=prop(th,z3)
    x2=prop(th,z2)
    train=np.vstack([x-x.mean(axis=0) for x in e1+[e2]])
    rows[tag]=dict(ring_source_centered_rms_arcsec=float(np.sqrt(np.mean(np.sum(train*train,axis=1)))),
       c1_EN_arcsec=c1.tolist(),c2_EN_arcsec=c2.tolist(),
       s3_pair_arcsec={str(s):g['pair'](e3-g['b2'](s)*unit(x2-c2)) for s in (0,60,150)})
  out[label]={'preferred_by_inner_knots':min(rows,key=lambda k:rows[k]['ring_source_centered_rms_arcsec']),'rows':rows}
out['image_check']={'filter':'F814W','pixel_arcsec':pixscale,'cd_deg_per_pixel':md,'archival_lens_center_zero_based_pixel':px.tolist(),
                   'all_14_knots_in_bounds':True,'knot_positions':'Gavazzi Table 1 using its published frame transform; no exact CA14 pixel centroid registration'}
(P/'jackpot_registered_knot_control.json').write_text(json.dumps(out,indent=2)+'\n')
for name,v in out.items():
 print(name,v.get('preferred_by_inner_knots'),v['rows'][v['preferred_by_inner_knots']] if 'rows' in v else v)
