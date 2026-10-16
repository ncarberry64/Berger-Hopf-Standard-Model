"""Independent fourth-order MP solve of the retained material constraints.

The sine Taylor coefficients are obtained by exponential recurrence, rather
than the phase evaluator's explicit trigonometric fourth-order formula.
The original nodes, weights and binary pi constants are unchanged.
"""
from flint import acb,acb_mat,ctx
import math
import numpy as np


def C(x):return x if isinstance(x,acb)else acb(complex(x))


class Series:
    def __init__(self,c):
        self.c=[C(x)for x in c]
        if len(self.c)!=5:raise ValueError('fourth-order factorial-divided coefficients required')
    @classmethod
    def constant(cls,v):return cls([v,0,0,0,0])
    @classmethod
    def variable(cls,v):return cls([v,1,0,0,0])
    def __add__(self,o):
        o=o if isinstance(o,Series)else Series.constant(o)
        return Series([x+y for x,y in zip(self.c,o.c)])
    __radd__=__add__
    def __neg__(self):return Series([-v for v in self.c])
    def __sub__(self,o):return self+(-o if isinstance(o,Series)else -C(o))
    def __rsub__(self,o):return -self+o
    def __mul__(self,o):
        o=o if isinstance(o,Series)else Series.constant(o)
        return Series([sum((self.c[j]*o.c[k-j]for j in range(k+1)),C(0))for k in range(5)])
    __rmul__=__mul__
    def reciprocal(self):
        b=[1/self.c[0]]
        for k in range(1,5):b.append(-sum((self.c[j]*b[k-j]for j in range(1,k+1)),C(0))/self.c[0])
        return Series(b)
    def __truediv__(self,o):return self*(o.reciprocal()if isinstance(o,Series)else 1/C(o))
    def exp(self):
        b=[self.c[0].exp()]
        for k in range(1,5):b.append(sum((j*self.c[j]*b[k-j]for j in range(1,k+1)),C(0))/k)
        return Series(b)
    def sin(self):return ((C(1j)*self).exp()-(-C(1j)*self).exp())/(2j)


def constraints(a,delta,points):
    from bhsm.interface.muon_exact_material_response import _rule
    nodes,weights=_rule(points);wall=C(float(np.pi/4))+delta
    Z=Series.constant(0);N=Series.constant(0)
    for x,w in zip(nodes,weights):
        chi=C(float(np.pi*float(x)/2))
        f=Series.constant(chi)+a[0]*(2*chi).sin()+a[1]*(6*chi).sin()
        s=(2*f).sin();Z+=C(float(w))*s*s*C(.25)*C(float(np.pi/2))
        c=wall*C(float(x));fp=c+a[0]*(2*c).sin()+a[1]*(6*c).sin()
        sp=(2*fp).sin();N+=C(float(w))*sp*sp*C(.25)*wall
    fw=wall+a[0]*(2*wall).sin()+a[1]*(6*wall).sin()
    return [fw-C(float(np.pi/4)),N/Z-C(.5)],Z


_cache={}


def anchored_material_chart4(delta,*,points=96,derivative_order=4,**unused):
    delta=C(delta);points=int(points)
    key=(str(delta),points,int(ctx.prec))
    if key in _cache:return _cache[key]
    if float(abs(delta).upper())>=2/9:raise ValueError('retained local anchored chart required')
    if derivative_order not in (3,4):raise ValueError('third or fourth material derivative requested')
    a=[-21*delta/16,-5*delta/16]
    def equations(av):
        E,_=constraints([Series.constant(v)for v in av],Series.constant(delta),points)
        J=acb_mat(2,2)
        for j in range(2):
            values=[Series.constant(v)for v in av];values[j]=Series.variable(av[j])
            dE,_=constraints(values,Series.constant(delta),points)
            for i in range(2):J[i,j]=dE[i].c[1]
        return acb_mat([[v.c[0]]for v in E]),J
    tolerance=2.**(-min(int(ctx.prec)-40,900))
    for iteration in range(16):
        E,J=equations(a)
        if max(float(abs(E[i,0]).upper())for i in range(2))<=tolerance:break
        step=J.solve(-E);a=[a[i]+step[i,0]for i in range(2)]
    else:raise ArithmeticError('independent material constraint solve did not converge')
    E,J=equations(a)
    if max(float(abs(E[i,0]).upper())for i in range(2))>tolerance:raise ArithmeticError('implicit material residual failed')
    t=[[v,0,0,0,0]for v in a]
    for order in range(1,5):
        partial,_=constraints([Series(v)for v in t],Series.variable(delta),points)
        step=J.solve(acb_mat([[-v.c[order]]for v in partial]))
        for i in range(2):t[i][order]=step[i,0]
    partial,Z=constraints([Series(v)for v in t],Series.variable(delta),points)
    result=dict(coefficients=np.asarray(a,dtype=object),
        derivatives=np.asarray([[math.factorial(k)*C(v[k])for k in range(1,5)]for v in t],dtype=object),
        normalization=Z.c[0],normalization_derivatives=np.asarray([math.factorial(k)*Z.c[k]for k in range(1,5)],dtype=object),
        points=points,implicit_residual=E,implicit_jacobian=J,
        implicit_Taylor_residual=np.asarray([v.c for v in partial],dtype=object),
        same_original_quadrature_and_constraint_law=True,arithmetic_precision_bits=int(ctx.prec),
        independent_exponential_recurrence=True)
    _cache[key]=result;return result


def control(repository,output):
    from pathlib import Path
    from hashlib import sha256
    import json
    import sys
    root,out=Path(repository).resolve(),Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    sys.path[:0]=[str(root/'src'),str(Path(__file__).parent)]
    from bhsm_baton_zoo_phase_clock_analytic_jet import anchored_material_chart_mp
    from bhsm.interface.muon_holomorphic_normal_geometry import _geometry_variables
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    cases=[root/'artifacts/muon_baton_zoo_radial_completion_20261013/action_gauge_degree2_run_1/birth_current288_connected_action_and_rate_operands.npz',
           root/'artifacts/muon_baton_zoo_augmented_source_domain_derivative_20261013/first_cell_column0_run_1/same_augmented_first_cell_original_action_base.npz']
    pins={};records=[];archives={};ctx.prec=192
    for ci,path in enumerate(cases):
        pins[str(path)]=sha256(path.read_bytes()).hexdigest()
        with np.load(path,allow_pickle=False)as z:raw=z['raw_pair'].copy()
        for arm in range(2):
            delta=_geometry_variables(raw[arm,:100])[3].value
            a=anchored_material_chart4(delta);b=anchored_material_chart_mp(delta,derivative_order=4)
            arrays={};differences=[]
            for key in ('coefficients','derivatives','normalization','normalization_derivatives','implicit_Taylor_residual'):
                val=np.asarray(a[key],dtype=object)
                if val.ndim==0:val=val.reshape(1,1)
                elif val.ndim==1:val=val.reshape(1,-1)
                matrix=acb_mat(val.tolist());arrays[key+'_high'],arrays[key+'_low']=_split(matrix)
                if key!='implicit_Taylor_residual':
                    ov=np.asarray(b[key],dtype=object).reshape(val.shape);differences.append(_upper(matrix-acb_mat(ov.tolist())))
            maximum=max(differences)
            residual=_upper(acb_mat(a['implicit_Taylor_residual'].tolist()))
            if maximum>1e-25 or residual>1e-25:raise ArithmeticError('independent fourth material chart control failed')
            arrays['material_delta']=np.asarray(delta);name=f'case_{ci:02d}_arm_{arm}_independent_fourth_material_chart.npz'
            p=out/name;_compressed_npz(p,arrays);archives[name]=sha256(p.read_bytes()).hexdigest()
            records.append(dict(case=ci,arm=arm,independent_chart_and_fourth_derivative_difference_upper=maximum,
                implicit_fourth_Taylor_residual_upper=residual))
    for name in ('last_independent_fourth_chart.npz','deterministic_serialization_control.npz'):
        p=out/name;_compressed_npz(p,arrays);archives[name]=sha256(p.read_bytes()).hexdigest()
    if archives['last_independent_fourth_chart.npz']!=archives['deterministic_serialization_control.npz']:raise RuntimeError('serialization differs')
    report=dict(classification='INDEPENDENT_EXPONENTIAL_RECURRENCE_FOURTH_MATERIAL_CHART_PRECISION_CONTROL',
        input_hashes=pins,archives=archives,records=records,retained_quadrature_and_binary_constants=True,
        physical_outgoing_or_derivative_admission=False,producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    (out/'executed_producer.py').write_bytes(Path(__file__).read_bytes())
    p=out/'result.json';p.write_text(json.dumps(report,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(records=records)),flush=True)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();control(a.repository,a.output)
