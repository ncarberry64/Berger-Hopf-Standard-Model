import ast,numpy as np,math,json
from functools import lru_cache
from pathlib import Path
p=Path(__file__).parent
src=ast.parse((p/'source_exact_response.py').read_text());wanted={'_Series3','_series_sin','_rule','_constraint_series','_constraints_and_jacobian','anchored_join_coefficients','_sigma_partials'}
ns=dict(np=np,math=math,lru_cache=lru_cache)
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in wanted],type_ignores=[]),'source-exact','exec'),ns)
# Literal positive cumulative normalization, no ratio to Taylor weight.
def exactweight(chi,delta):
 chart=ns['anchored_join_coefficients'](float(delta));x,w=ns['_rule'](96);c=chi[:,None]*x;aa=chart['coefficients'];f=c+aa[0]*np.sin(2*c)+aa[1]*np.sin(6*c);prob=chi*(.25*np.sin(2*f)**2@w)/chart['normalization']
 return 4*prob*(1-prob)
base=(p/'materialize_radial_graph_coefficients.py').read_text().split('records=[]')[0]
start=base.index(' delta=-.5*');end=base.index('\n common=',start)
base=base[:start]+' weight=exactweight(chi,s/cs)'+base[end:]
base=base.replace('(4*delta*(1-delta))','weight')
factorbase=base.replace('weight=exactweight(chi,s/cs)','weight=np.ones_like(chi)')
factors={'__file__':str(p/'source_exact_response.py')};exec(factorbase,factors)
def exactfirst(raw,rho):
 q=raw[:37];cs=(343./5.)**(1/6)*np.exp(q[0]+q[1:13]@((-1.)**np.arange(1,13))+q[13:25]@((-1.)**np.arange(12)))
 delta=raw[98]/cs;chi=rho/WALL*(np.pi/4+delta);chart=ns['anchored_join_coefficients'](float(delta))
 vals=[ns['_sigma_partials'](delta,float(c),chart) for c in chi];prob=np.array([v[3] for v in vals]);ps=np.array([v[1][0]+rho[i]/WALL*v[1][1] for i,v in enumerate(vals)])/cs
 w=4*prob*(1-prob);ws=4*(1-2*prob)*ps;f=factors['coeff'](raw,rho)[:,:4];fs=factors['coeff'](raw,rho,s=raw[98]+1e-20j).imag[:,:4]/1e-20
 return fs*w[:,None]+f*ws[:,None]
geom={'__file__':str(p/'source_exact_response.py'),'exactweight':exactweight};exec(base,geom);cf=geom['coeff']
old={'__file__':str(p/'materialize_radial_graph_coefficients.py')};exec((p/'materialize_radial_graph_coefficients.py').read_text().split('records=[]')[0],old)
known={ '__file__':str(p/'known_radial_kinetic_blocks.py')};exec((p/'known_radial_kinetic_blocks.py').read_text().split('results=[]')[0],known);basis=known['basis'];norm=known['norm'];WALL=np.pi/2
rec=[];arrays={}
for side in ['incoming','outgoing']:
 z=np.load(p/(side+'_history.npz'))
 for label in ['lo','q000','q001','q002','q003','hi']:
  raw=z[label+'_raw_fields'];mats=[]
  for order in [192,384]:
   x,w=np.polynomial.legendre.leggauss(order);rho=(x+1)*WALL/2;w=w*WALL/2;B=basis(rho);c=cf(raw,rho)
   def m(s):return B.T@((norm*w*cf(raw,rho,s=s)[:,0])[:,None]*B)
   M=m(raw[98]);ds=[]
   for h in [1e-4,5e-5]:ds.append((-m(raw[98]+2*h)+8*m(raw[98]+h)-8*m(raw[98]-h)+m(raw[98]-2*h))/(12*h))
   analytic=B.T@((norm*w*exactfirst(raw,rho)[:,0])[:,None]*B)
   mats.append((M,analytic));analyticcheck=float(np.max(abs(analytic-ds[-1])));check=float(np.max(abs(ds[1]-ds[0])))
   if order==192:
    rel=float(np.max(abs(c[:,:4]-old['coeff'](raw,rho)[:,:4])/c[:,:4]));arrays[side+'_'+label+'_exact_geometry']=c
  M,Ms=mats[0];arrays[side+'_'+label+'_known_M']=M;arrays[side+'_'+label+'_known_Ms']=Ms
  rec.append(dict(side=side,label=label,wall_wall=float(M[-1,-1]),wall_wall_shape_derivative=float(Ms[-1,-1]),min_eigenvalue=float(np.linalg.eigvalsh(M)[0]),Taylor_density_max_relative_difference=rel,derivative_step_halving_max=check,analytic_vs_difference_max=analyticcheck,quadrature_value_difference=float(np.max(abs(mats[0][0]-mats[1][0])))))
np.savez(p/'exact_radial_known_blocks.npz',**arrays)
out=dict(scope='exact finite anchored chart; known indices0,1,3 only; no induced or constraint solve',records=rec,physical_moment=None)
(p/'EXACT_RADIAL_KNOWN_BLOCKS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
