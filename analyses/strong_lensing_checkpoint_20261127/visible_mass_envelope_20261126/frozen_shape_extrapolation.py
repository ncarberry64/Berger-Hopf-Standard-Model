"""Sensitivity to unknown profile outside the Jackpot-measured band."""
exec(open('frozen_radial_transfer.py').read().split("s0=score(")[0])
caps={}
for outer_eta in [0.,.5,eta]:
 def law(t,R,a):
  x=R/t['Re']
  growth=(x/x0)**eta if x<=x1 else (x1/x0)**eta*(x/x1)**outer_eta
  return t['logSalp']+np.log10(starfrac(x)+a*growth)
 def ff(rows):
  err=lambda c:[law(t,t['R'],np.exp(c[0]))-t['L'] for t in rows]
  return np.exp(least_squares(err,[-2.4]).x[0])
 A=ff(slacs); studies={}
 for label,rs in [('SLACS',slacs),('SL2S',iv)]:
  err=[]
  for t in rs:
   a=A if label=='SL2S' else ff([s for s in slacs if s['name']!=t['name']])
   rp=ring(t,lambda R:law(t,R,a)); err.append(rp/t['R']-1)
  studies[label]=dict(n=len(err),signed=float(np.median(err)),absolute=float(np.median(abs(np.asarray(err)))))
 print(outer_eta,A,studies)
 caps[str(outer_eta)]=dict(A=A,studies=studies)
Path('frozen_shape_extrapolation.json').write_text(json.dumps(caps,indent=2)+'\n')
