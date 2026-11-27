"""Vanzella et al. 2021 A&A 646 A57, Table A.1, System 5 of MACS J0416."""
import contextlib,io,json
import numpy as np
with contextlib.redirect_stdout(io.StringIO()):
 from light_only_fold_trace import replay
from light_only_mirror_catalog import run
a=np.array([[47367,-68671],[47462,-68823],[47483,-68851],[47583,-68884],[47650,-68971],[47737,-69012]])
b=np.array([[43479,-63523],[43075,-63084],[43021,-63021],[42908,-62865],[42762,-62771],[42571,-62628]])
c=np.array([[40783,-61609],[41083,-61802],[41162,-61848],[41479,-61979],[41704,-62128],[42071,-62319]])
X=(np.array([a,b,c])-a[0])*.0036*np.array([np.cos(np.deg2rad(24.07)),1])
out={}
for p,q in [(1,2),(2,1),(0,1),(0,2)]:
 for use in [list(range(6)),list(range(5))]:
  x,y=X[[p,q]][:,use]; err,pts=replay(x,y)
  da=y-x; s=np.linalg.svd(da,compute_uv=False); dt=np.linalg.lstsq(x-x.mean(0),y-y.mean(0),rcond=None)[0]
  out[f'{p}->{q}, n={len(use)}']={'rms':err.tolist(),'affine_rms':run(x,y,len(use)-1)['rms']['affine'],'det':float(np.linalg.det(dt)),'directionality':float(s[0]**2/(s@s)),'min_sep':float(np.min(np.linalg.norm(da,axis=1)))}
print(json.dumps(out,indent=2))
