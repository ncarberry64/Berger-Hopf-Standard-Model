"""Recenter bright cores and outer #7 on HST SCI cutouts.
Figure 12 supplies identification only (including search windows), not the
measured #7 positions. Inner figure features alone supply relative map.
The HST filters were also used by the authors; this is not new independent data.
"""
from snl_light_audit import *
from scipy.optimize import least_squares
from scipy.ndimage import map_coordinates
from pathlib import Path
D=Path(__file__).parent
A=json.loads((D/'hamilton_landmark_holdout.json').read_text())
m={k:(np.array(v)-[612.5,866.5])*[-1/67,-2.2/67] for k,v in A['marker_pixels'].items()}
def mapfunc(a,b,x,name):
  al,bl=a[:6],b[:6]; l=al.mean(0); r=bl.mean(0); al=al-l; bl=bl-r
  if name=='mirror':
    u,s,v=np.linalg.svd(al.T@bl); q=np.diag([1,-np.linalg.det(u@v)])
    j=u@q@v*(s@q.diagonal())/np.sum(al**2)
  elif name=='affine':j=np.linalg.lstsq(al,bl,rcond=None)[0]
  else:j=np.eye(2)
  return (x-l)@j+r
def center(img,x,seed,off,bound=.7,rr=.75):
  xx,yy=np.meshgrid(x-seed[0]-off[0],x-seed[1]-off[1])
  q=np.hypot(xx,yy)<rr
  u,v,z=xx[q],yy[q],img[q]
  def f(p):
    h,i,j,s,base,dx,dy=p
    return h*np.exp(-((u-i)**2+(v-j)**2)/(2*s*s))+base+dx*u+dy*v-z
  p=least_squares(f,[max(z)-np.median(z),0,0,.12,np.median(z),0,0],
    bounds=([0,-bound,-bound,.06,-np.inf,-np.inf,-np.inf],[np.inf,bound,bound,.35,np.inf,np.inf,np.inf]),
    x_scale='jac')
  ans=p.x
  return np.array(seed)+off+ans[1:3],float(ans[0]),float(ans[3]),float(np.std(p.fun))
records={}
for f in sorted((D/'hamilton_inputs').glob('*fits')):
 x,d=sky_cutout(f,337.54041667,-8.161111111,.09,23)
 cores=[center(d,x,m[k][0],np.zeros(2),1.2,1.5)[0] for k in ('A','B','C')]
 print(f.name, 'core shifts: ',np.round(cores-np.array([m[k][0] for k in ('A','B','C')]),3))
 offsets={k: cores[i]-m[k][0] for i,k in enumerate(('A','B','C'))}
 outer={k:center(d,x,m[k][6],offsets[k],.43,.72) for k in m}
 rec={}
 for ab in ('AB','BA','AC','BC'):
  a,b=ab
  rec[ab]={q:float(np.linalg.norm(mapfunc(m[a],m[b],outer[a][0]-offsets[a],q)+offsets[b]-outer[b][0])) for q in ('mirror','affine','shift')}
 print('outer',[(k,np.round(z[0],3),round(z[1]/z[3],2),round(z[2],3)) for k,z in outer.items()])
 print(rec)
 records[f.name]=dict(outer_model_replays=rec,translation={k:o.tolist() for k,o in offsets.items()},peak_fit={k:[z[0].tolist(),*z[1:]] for k,z in outer.items()})
(D/'hamilton_native_outer.json').write_text(json.dumps(records,indent=2)+'\n')
