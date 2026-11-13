"""Literal MP evaluation of the retained fixed radial coefficient laws.

Frozen projection/norm/reference states and numerical constants are
preserved exactly as saved. This refines polynomial/transcendental
arithmetic and exports every field derivative; it is not a new action,
propagation, Cauchy-state correction or physical exterior.
"""
from pathlib import Path
import argparse
import json


def literal_profiles(rep,rho,degree,precision=192):
    import numpy as np
    from flint import acb,ctx,acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix
    from bhsm.interface.muon_parent_retarded_hypercharge import WALL,ALPHA
    from bhsm_baton_zoo_compatible_radial_complex import derivative_profiles,exact_legendre_derivative_quotients
    ctx.prec=precision
    scalar=lambda z:_matrix([[z]])[0,0]
    wall,alpha=scalar(WALL),scalar(ALPHA)
    norms=derivative_profiles(rep,np.array([WALL/2]))['norms'];c0,c1=map(scalar,norms)
    proj=map(scalar,rep['affine_interior_projection']);p0,p1=proj
    wc,fn=scalar(rep['affine_wall_coefficient']),scalar(rep['affine_complement_norm'])
    class D:
        def __init__(self,value,first=0,second=0):self.v,self.d,self.dd=scalar(value),scalar(first),scalar(second)
        @classmethod
        def exact(cls,v,d=0,dd=0):
            obj=object.__new__(cls);obj.v,obj.d,obj.dd=v,d if isinstance(d,acb)else scalar(d),dd if isinstance(dd,acb)else scalar(dd);return obj
        def __add__(self,o):
            o=o if isinstance(o,D)else D(o);return D.exact(self.v+o.v,self.d+o.d,self.dd+o.dd)
        __radd__=__add__
        def __neg__(self):return D.exact(-self.v,-self.d,-self.dd)
        def __sub__(self,o):return self+(-o if isinstance(o,D)else-D(o))
        def __rsub__(self,o):return D(o)+(-self)
        def __mul__(self,o):
            o=o if isinstance(o,D)else D(o)
            return D.exact(self.v*o.v,self.d*o.v+self.v*o.d,self.dd*o.v+2*self.d*o.d+self.v*o.dd)
        __rmul__=__mul__
        def reciprocal(self):return D.exact(1/self.v,-self.d/self.v**2,2*self.d**2/self.v**3-self.dd/self.v**2)
        def __truediv__(self,o):return self*(o.reciprocal()if isinstance(o,D)else D(o).reciprocal())
        def __rtruediv__(self,o):return self.reciprocal()*o
        def __pow__(self,p):
            if isinstance(p,int):
                if p==0:return D(1)
                if p==1:return self
                return D.exact(self.v**p,p*self.v**(p-1)*self.d,
                    p*self.v**(p-1)*self.dd+p*(p-1)*self.v**(p-2)*self.d**2)
            p=p if isinstance(p,acb)else scalar(p)
            z=(p*self.v.log()).exp()
            return D.exact(z,z*p*self.d/self.v,z*(p*self.dd/self.v+p*(p-1)*self.d**2/self.v**2))
        def exp(self):
            z=self.v.exp();return D.exact(z,z*self.d,z*(self.dd+self.d**2))
        def sin(self):return D.exact(self.v.sin(),self.v.cos()*self.d,self.v.cos()*self.dd-self.v.sin()*self.d**2)
        def cos(self):return D.exact(self.v.cos(),-self.v.sin()*self.d,-self.v.sin()*self.dd-self.v.cos()*self.d**2)
    def lam(state,r):
        chi=r/2;q=[D(v)for v in state[:37]]
        shape=(2*chi).sin()**2*sum((q[25+j]*(4*j*chi).cos()for j in range(12)),D(0))
        AA=(4*shape).exp()*chi.cos()**2;BB=chi.sin()**2
        return AA/(AA+BB)
    rows=[]
    for rr in rho:
        r=D.exact(scalar(rr),scalar(1));x=r/D.exact(wall);y=2*x-1
        regular=x**alpha;B0=D.exact(c0)*regular*(1-x)
        t,s=5+2*alpha,8+2*alpha
        B1=D.exact(c1)*regular*(1-x)*(-D.exact(t)+D.exact(s)*x)
        f=(lam(rep['affine_profile_reference_states'][0],r)-lam(rep['affine_profile_reference_states'][1],r)-D.exact(p0)*B0-D.exact(p1)*B1-D.exact(wc)*regular)/D.exact(fn)
        phi=(1-y*y)**2;P=[D(1),y]
        for l in range(1,degree):P.append(((2*l+1)*y*P[-1]-l*P[-2])/(l+1))
        profiles=[B0,B1,f,regular]+[phi*P[l]for l in range(degree+1)]
        rows.append(profiles)
    values=acb_mat([[p.v for p in row]for row in rows]);first=acb_mat([[p.d for p in row]for row in rows]);second=acb_mat([[p.dd for p in row]for row in rows])
    # Four added Ar profiles and their spatial first derive from exactly
    # the SAME old/phi expression evaluated above.
    psi=acb_mat([[row[3].d,row[2].d,row[4].d,row[5].d]for row in rows])
    psir=acb_mat([[row[3].dd,row[2].dd,row[4].dd,row[5].dd]for row in rows])
    derivative_coeff=acb_mat(degree+9,degree+5)
    derivative_coeff[degree+5,0]=c0;derivative_coeff[3,0]=-c0*(alpha+1)/wall
    derivative_coeff[degree+5,1]=-c1*(5+2*alpha)
    derivative_coeff[0,1]=c1*(8+2*alpha)*(alpha+2)/(wall*c0)
    derivative_coeff[3,1]=c1*((5+2*alpha)*(alpha+1)-(8+2*alpha))/wall
    derivative_coeff[degree+6,2]=1;derivative_coeff[degree+5,3]=1
    for l,coeffs in enumerate(exact_legendre_derivative_quotients(degree)):
        derivative_coeff[degree+7+l%2,4+l]=1
        for k,c in enumerate(coeffs):derivative_coeff[4+k,4+l]=2*acb(str(c.numerator))/acb(str(c.denominator))/wall
    allvalues=acb_mat([[values[i,j]for j in range(values.ncols())]+[psi[i,j]for j in range(4)]for i in range(values.nrows())])
    identity=allvalues*derivative_coeff-first
    return dict(values=values,first=first,second=second,psi=psi,psi_first=psir,
        derivative_coefficients=derivative_coeff,allvalues=allvalues,derivative_identity=identity)


def run(repository,output,stage=None,precision=192):
    from bhsm_baton_zoo_radial_convergence import environment
    root,out,read,save,finish=environment(repository,output)
    import numpy as np
    from flint import ctx
    from evaluate_muon_continued_current_factor import retained_input
    from bhsm.interface.muon_stored_admission_correction import _mid,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    from bhsm.interface.muon_birth_trace_enriched_action import trace_enriched_radial_basis
    from bhsm_baton_zoo_radial_completion import radial_profile_lifts
    phase,_=retained_input('outgoing',{});rep=phase['representation'];rho=rep['rho']if stage is None else read(stage)['rho']
    records=[];ctx.prec=precision
    for degree in(2,4,6,8):
        p=literal_profiles(rep,rho,degree,precision);arrays=dict(rho=np.asarray(rho),profile_degrees=np.arange(degree+1),arithmetic_precision_bits=np.asarray(precision))
        for key,value in p.items():arrays[key+'_high'],arrays[key+'_low']=_split(value)
        oldB,oldBr=trace_enriched_radial_basis(rep,rho);phi=radial_profile_lifts(rho,range(1,degree+1))
        xx=np.asarray(rho)/(np.pi/2);ph0=16*xx**2*(1-xx)**2;phr0=32*xx*(1-xx)*(1-2*xx)/(np.pi/2)
        v=np.c_[oldB,ph0,phi['profile_values']];dv=np.c_[oldBr,phr0,phi['profile_radial_first']]
        # Wall values and radial derivatives have their own exact evaluation.
        face=literal_profiles(rep,np.array([np.pi/2]),degree,precision)
        for key in('values','first','second','psi','psi_first'):
            arrays['wall_'+key+'_high'],arrays['wall_'+key+'_low']=_split(face[key])
        arrays['binary_value_minus_literal']=v-_mid(p['values']);arrays['binary_first_minus_literal']=dv-_mid(p['first'])
        save(f'degree_{degree:02d}_literal_MP_radial_profiles_and_derivative_complex.npz',arrays)
        records.append(dict(degree=degree,derivative_complex_identity_upper=_upper(p['derivative_identity']),
            binary_value_difference_max=float(np.max(abs(arrays['binary_value_minus_literal']))),
            binary_derivative_difference_max=float(np.max(abs(arrays['binary_first_minus_literal']))),
            literal_affine_wall_profile_abs=float(abs(_mid(face['values'])[0,2]))))
    finish(dict(classification='LITERAL_HIGH_PRECISION_RADIAL_FUNCTION_AND_DERIVATIVE_COMPLEX_EVALUATED',
        arithmetic_precision_bits=precision,records=records,frozen_basis_reference_projection_norm_constants_preserved=True,
        physical_Cauchy_state_or_gauge_source_changed=False,chronological_application_performed=False,
        numerical_error_enclosure_is_arithmetic_not_quadrature=True),producer_paths=(Path(__file__),))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--stage',type=Path);p.add_argument('--precision',type=int,choices=(192,384),default=192)
    a=p.parse_args();run(a.repository,a.output,a.stage,a.precision)
