"""Unfitted truncation sensitivity for the velocity-dispersion-normalized proxy."""
exec(open('registered_tide_check.py').read().split('out={}')[0])
out={}
for rt in (25,50,100,200,400,1e7):
 J=np.zeros((2,2));full=np.zeros(2)
 for id in (39628027746848157,39628027746848720):
  a,=t['METADATA'][t['METADATA']['TARGETID']==id];b,=t['SPECPHOT'][t['SPECPHOT']['TARGETID']==id]
  z=a['Z'];D=chi(z)/(1+z)*1000
  p=3600*np.array([(a['RA']-lens[0])*np.cos(np.radians(lens[1])),a['DEC']-lens[1]])
  d=np.linalg.norm(p); n=p/d
  w=1-chi(z)/chi(5.975);b0=4*np.pi*(float(b['VDISP'])/c)**2*w*asr
  t0=rt/D*asr
  def f(r):return 1-r/(t0+np.hypot(r,t0))
  df=-t0/(np.hypot(d,t0)*(t0+np.hypot(d,t0)))
  J+=b0*(f(d)/d*(np.eye(2)-np.outer(n,n))+df*np.outer(n,n))
  v=theta-p; rr=np.linalg.norm(v,axis=1)
  aa=b0*(f(rr)/rr)[:,None]*v
  full+=aa[0]-aa[1]
 out[str(rt)]=[np.linalg.norm(full)*1000,np.trace(J)/2,np.linalg.norm(full-J@diff)*1000]
 print(rt,out[str(rt)])
assert np.allclose(out[str(1e7)],[69.02414345918005,.00787033195,1.1274341252],rtol=5e-5)
Path('tide_truncation.json').write_text(json.dumps(out,indent=2)+'\n')
