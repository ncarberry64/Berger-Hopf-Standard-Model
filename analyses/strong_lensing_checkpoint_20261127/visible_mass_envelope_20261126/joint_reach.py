"""Amplitude profiled on SLACS strong lensing; radial observables held separate."""
exec(open('frozen_radial_transfer.py').read().split("s0=score(")[0])
from scipy.special import gammaln
from itertools import product
T=Path('gavazzi_wl.txt').read_text()
tab=T.split('TABLE 1',1)[1].split('Apparent I band',1)[0]
stack=[]
for line in tab.splitlines():
 q=line.split()
 if not(q and q[0].startswith('SDSSJ')):continue
 n=q[0];m=re.fullmatch(r'(SDSSJ\d{4})\d\d\.\d([+-]\d{4})\d\d',n); assert m,n
 a,b=m.groups();n=a+b.replace('-','−')
 obj=next((t for t in slacs if t['name']==n),None)
 z=float(q[3]);d0=d(0,z)
 if obj is None:
  tp=next(l.split() for l in Path('auger09.txt').read_text().split('                                                                      Table 4',1)[1].splitlines() if l.split() and l.split()[0]==n and '±' in l)
  obj=dict(logSalp=float(tp[7].split('±')[0]),Re=float(q[-6])*d0*np.pi/648.)

 row=dict(name=n,weakgeo=float(q[-1]),dl=d0,z=z,dispersion=float(q[4]),angular_Re=float(q[-6]),angular_R=float(q[-7]),photometry=obj)
 stack.append(row)
assert len(stack)==22
Q=T.split('TABLE 2',1)[1].split('The curl component',1)[0]
data=[]
for l in Q.splitlines():
 q=l.split()
 if len(q)==7 and re.fullmatch(r'\d+\.\d+',q[0]):data.append([float(q[j]) for j in [0,1,3]])
assert len(data)==9
R,Dobs,sigma=np.array(data).T
Rphys=R/.7
known=[t for t in stack if t['photometry'] is not None]
print('matched',len(known),'missing',[t['name'] for t in stack if t['photometry'] is None])
def g(x,L):
 # Normalized at Jackpot inner aperture x0.
 return (x/x0)**eta * ((1+(x0/L)**4)/(1+(x/L)**4))**(eta/4)
def slope(x,L):return eta/(1+(x/L)**4)
def mass(t,R,A,L):
 x=R/t['Re'];return t['logSalp']+np.log10(starfrac(x)+A*g(x,L))
def find_amp(L):
 def err(q):return [mass(t,t['R'],np.exp(q[0]),L)-t['L'] for t in slacs]
 o=least_squares(err,[-2.3])
 return np.exp(o.x[0]),float(np.sqrt(np.mean(o.fun**2)))
def contrast(t,rr,A,L):
 x=rr/t['Re'];z=7.6692494425*x**.25;stellar=starfrac(x)
 Md=(.25*np.exp(8*np.log(z)-z-gammaln(8))) # derivative d Mstar fraction/d log(radius)
 term=2*stellar-Md+A*g(x,L)*(2-slope(x,L))
 # Msun/kpc^2 -> h Msun/pc^2
 return 10**t['logSalp']*term/(2*np.pi*rr**2)/1e6/.7
def we(w,x):
 if w==0:return 1.
 if w==1:return x['weakgeo']**2
 return (x['weakgeo']*x['dl'])**2
out={}
for L in [.5,.88,1.25,2,3,5,10,20,50,100,1e9]:
 A,rm=find_amp(L)
 err=np.array([ring(t,lambda R:mass(t,R,A,L))/t['R']-1 for t in iv])
 weak=[]
 for w in range(3):
  yy=np.average(np.stack([contrast(t['photometry'],Rphys,A,L) for t in known]),axis=0,weights=[we(w,t) for t in known])
  wig=(R>=30.8)&(R<=164.5)
  chi=((yy[wig]-Dobs[wig])/sigma[wig])**2
  weak.append(dict(y=yy.tolist(),diag_chi=float(chi.sum())))
 out[str(L)]=dict(A=A,strong_slacs_rms_dex=rm,outer_sl2s_median_abs=float(np.median(abs(err))),weak=weak)
 print(L,round(A,4),round(rm,4),round(np.median(abs(err)),4),
   np.round([w['diag_chi'] for w in weak],2),np.round(weak[0]['y'][4:8],1))
print('observed 30.8->164.5',Dobs[4:8],sigma[4:8])
Path('joint_reach.json').write_text(json.dumps(dict(results=out,table2=data,matched=[x['name'] for x in known]),indent=2)+'\n')
