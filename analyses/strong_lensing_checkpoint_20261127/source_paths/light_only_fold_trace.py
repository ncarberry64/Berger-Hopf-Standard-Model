"""Predict held-out images using a straight or mapped midpoint locus.
Line-fit inputs: paired light features only. The midpoint locus is not
assumed to be the physical critical curve.
"""
import numpy as np, json
from light_only_mirror_catalog import macs,cl
def replay(a,b):
  errors=np.zeros((len(a),3))
  for i in range(len(a)):
    tr=np.arange(len(a))!=i
    _,_,v=np.linalg.svd(b[tr]-a[tr],full_matrices=False)
    n,t=v
    m=(a[tr]+b[tr])/2
    for d in range(3):
      c=np.polynomial.polynomial.polyfit(m@t,m@n,d)
      pred=a[i]+2*(np.polynomial.polynomial.polyval(a[i]@t,c)-a[i]@n)*n
      errors[i,d]=np.linalg.norm(pred-b[i])
  return np.sqrt(np.mean(errors**2,axis=0)),errors
sets={'MACS12':macs,'MACS12_no_closest':macs[:,[0,1,2,4,5]], 'CL_1_2':cl[[0,1]],'CL_1_4':cl[[0,3]]}
res={}
for label,(a,b) in sets.items():
  err,es=replay(a,b)
  mid=(a+b)/2
  _,s,v=np.linalg.svd(b-a,full_matrices=False)
  n,t=v
  span=float(np.ptp(mid@t))
  res[label]={'rms_reflection_normal_displacement_by_locus_degree':err.tolist(),
    'point_errors':es.tolist(),'midpoint_span_arcsec':span,
    'connector_direction_concentration':float(s[0]**2/(s@s)),
    'midpoint_transverse_scatter':float(np.std(mid@n)),
    'transverse_connector_rms':float(np.sqrt(np.mean(((b-a)@t)**2)))}
print(json.dumps(res,indent=2))
