"""Nonlinear two-primary-image lens model in physical angular/time units.

Distances, redshifts and an absolute tangent-plane astrometric frame are
supplied calibrations. Motion is angular per observer year. Free source
positions at each row do not imply a known unlensed trajectory.
"""
import numpy as np
from .data import load_dataset

# IAU nominal solar mass parameter, rather than uncertain G and Msun factors.
GM_SUN=1.3271244e20
C=299792458.
PC=3.085677581491367e16
RAD_MAS=206264806.24709636
YEAR=31557600.

class LensEngine:
    def __init__(self,dataset,family='gr',reference_mass=None):
        self.data=load_dataset(dataset)
        if family not in ['gr','r1']:raise ValueError('family must be gr or r1')
        self.family=family;g=self.data.geometry
        self.ref_mass=float(reference_mass or self.data.analysis.get('reference_mass_msun',1e5))
        self.mref_pc=GM_SUN*self.ref_mass/(C*C*PC)
        self.theta=np.sqrt(4*self.mref_pc*g['D_ls_pc']/(g['D_l_pc']*g['D_s_pc']))*RAD_MAS
        self.rE=self.theta/RAD_MAS*g['D_l_pc']
        self.time=4*GM_SUN*self.ref_mass/C**3*(1+g['z_l'])
        self.tscale=max(float(np.ptp(self.data.epochs))/2,1.)
        self.tau=(self.data.epochs-self.data.t0)/self.tscale
        self.origin=np.mean(self.data.observations[:,:4].reshape(-1,2),axis=0)
        self.r0=float(self.data.analysis.get('r0_pc',self.rE*1e-3))
        # Admission and propagation must use the identical physical worldtube.
        self.physics_config={**self.data.raw,'analysis':{**self.data.analysis,'r0_pc':self.r0}}
        self.parallax=np.asarray(self.data.analysis.get('lens_parallax_factors',np.zeros((self.data.n,2))))*(1000/g['D_l_pc'])
        self._r1=None
        if family=='r1':
            from .r1_runtime import R1Runtime
            self._r1=R1Runtime(self)

    def potential(self,x,massratio,shear,compact,kappa,flux=1.,boundary=None):
        r=np.linalg.norm(x,axis=-1)
        if np.any(r*self.rE<self.r0):raise ValueError('ray enters unresolved worldtube')
        e=x/r[...,None];t=np.stack([-e[...,1],e[...,0]],axis=-1)
        ee=e[..., :,None]*e[...,None,:];tt=t[..., :,None]*t[...,None,:]
        I=np.eye(2)
        p=massratio*np.log(r)
        grad=massratio*x/r[...,None]**2
        H=massratio*(I/r[...,None,None]**2-2*ee/r[...,None,None]**2)
        gm=np.array([[shear[0],shear[1]],[shear[1],-shear[0]]])+kappa*I
        p=p+.5*np.einsum('...i,ij,...j->...',x,gm,x)
        grad=grad+x@gm.T;H=H+gm
        cs=e[...,0]**2-e[...,1]**2;sn=2*e[...,0]*e[...,1]
        def add_quadrupole(q,qp,qpp,coeff):
            co=coeff[0]*cs+coeff[1]*sn;si=coeff[0]*sn-coeff[1]*cs
            pp=q*co
            gg=qp[...,None]*co[...,None]*e-2*(q/r*si)[...,None]*t
            hh=(qpp*co)[...,None,None]*ee+(qp/r-4*q/r**2)[...,None,None]*co[...,None,None]*tt
            hh=hh-2*((qp/r-q/r**2)*si)[...,None,None]*(e[..., :,None]*t[...,None,:]+t[..., :,None]*e[...,None,:])
            return pp,gg,hh
        if np.any(np.asarray(compact)!=0):
            pp,gg,hh=add_quadrupole(r**-2,-2*r**-3,6*r**-4,compact)
            p+=pp;grad+=gg;H+=hh
        if self._r1 is not None:
            values=self._r1.monopole(r,massratio,flux)
            pv,alpha,ap=values
            p+=pv;grad+=alpha[...,None]*e
            H+=(alpha/r)[...,None,None]*I+(ap-alpha/r)[...,None,None]*ee
            if boundary is not None and np.any(boundary):
                q,qp,qpp=self._r1.quadrupole(r,massratio,flux)
                pp,gg,hh=add_quadrupole(q,qp,qpp,np.asarray(boundary)[:2])
                p+=pp;grad+=gg;H+=hh
                if len(boundary)>2 and boundary[2]!=0:
                    q,qp,qpp=self._r1.quadrupole(r,massratio,flux,axial=True)
                    p+=boundary[2]*q;grad+=boundary[2]*qp[...,None]*e
                    H+=boundary[2]*((qp/r)[...,None,None]*I+(qpp-qp/r)[...,None,None]*ee)
        return p,grad,H

    def calculate(self,parameters,admit=True):
        d=self.data
        if self.family=='r1' and any(key in parameters for key in ['boundary_amplitudes','conormal_coefficients']):
            from .physics_admission import resolve_boundary_amplitudes
            parameters={**parameters,'boundary_amplitudes':resolve_boundary_amplitudes(self.physics_config,parameters)}
        mass=float(parameters['mass_msun'])
        if not np.isfinite(mass) or mass<=0:raise ValueError('mass_msun must be positive and finite')
        mr=mass/self.ref_mass
        center=np.asarray(parameters.get('center_mas',[0.,0.]),dtype=float)
        motion=np.asarray(parameters.get('proper_motion_mas_yr',[0.,0.]),dtype=float)
        sources=np.asarray(parameters['source_mas'],dtype=float)
        if center.shape!=(2,) or motion.shape!=(2,) or sources.shape!=(d.n,2):raise ValueError('center/motion need two values and source_mas needs N two-vectors')
        if not np.all(np.isfinite(np.r_[center,motion,sources.ravel()])):raise ValueError('parameters must be finite')
        centers=center+(d.epochs-d.t0)[:,None]*motion+self.parallax
        y=(sources-centers)/self.theta
        u=np.linalg.norm(y,axis=1)
        if np.any(u<1e-5):raise ValueError('near-critical aligned source is outside the primary-pair contract')
        e=y/u[:,None];s=np.sqrt(u*u+4*mr)
        images=np.stack([.5*(u+s)[:,None]*e,.5*(u-s)[:,None]*e],axis=1)
        shear=np.asarray(parameters.get('shear',[0.,0.]),dtype=float)
        compact=np.asarray(parameters.get('compact_quad',[0.,0.]),dtype=float)
        kappa=float(parameters.get('convergence',0.))
        flux=float(parameters.get('flux_ratio',d.analysis.get('flux_ratio',1.)))
        boundary=parameters.get('boundary_amplitudes')
        if shear.shape!=(2,) or compact.shape!=(2,) or not np.all(np.isfinite(np.r_[shear,compact,kappa,flux])):raise ValueError('finite shear/compact vectors and scalar parameters required')
        # Damped Newton continuation of the two point-lens primary branches.
        for _ in range(24):
            p,g,H=self.potential(images,mr,shear,compact,kappa,flux,boundary)
            residual=images-y[:,None,:]-g
            A=np.eye(2)-H
            try:step=np.linalg.solve(A,residual[...,None])[...,0]
            except np.linalg.LinAlgError as error:raise ValueError('critical image Jacobian') from error
            norms=np.linalg.norm(step,axis=-1)
            limit=.3*np.maximum(np.linalg.norm(images,axis=-1),self.r0/self.rE)
            step*=np.minimum(1.,limit/np.maximum(norms,1e-30))[...,None]
            images-=step
            if np.max(abs(residual))<2e-12:break
        p,g,H=self.potential(images,mr,shear,compact,kappa,flux,boundary)
        residual=images-y[:,None,:]-g
        determinants=np.linalg.det(np.eye(2)-H)
        if np.max(abs(residual))>1e-9:raise ValueError('primary-image continuation did not converge')
        if np.any(determinants[:,0]<=1e-7) or np.any(determinants[:,1]>=-1e-7):raise ValueError('primary parity or critical-curve admission failed')
        tau=.5*np.sum((images-y[:,None,:])**2,axis=-1)-p
        logratio=np.log(abs(determinants[:,1]/determinants[:,0]))
        delay=(tau[:,1]-tau[:,0])*self.time
        if np.any(delay<=0):raise ValueError('primary image time ordering reversed')
        sky=images*self.theta+centers[:,None,:]
        result=np.column_stack([sky.reshape(d.n,4),logratio,delay])
        if not np.all(np.isfinite(result)):raise ValueError('nonfinite primary-pair prediction')
        if admit:
            from .physics_admission import assess_physics
            admission=assess_physics(self.physics_config,parameters,np.linalg.norm(images,axis=-1)*self.rE)
            key='r1_boundary_conditional' if self.family=='r1' else 'baseline_point_mass'
            if not admission['allowed_physics_models'].get(key):
                raise ValueError('prediction outside admitted '+key+' domain: '+', '.join(admission.get('reasons',[])))
        return result,{'impact_pc':(np.linalg.norm(images,axis=-1)*self.rE).tolist(),
                      'max_stationary_residual':float(np.max(abs(residual))),
                      'minimum_abs_Jacobian_determinant':float(np.min(abs(determinants)))}

def predict(dataset,parameters,family='gr'):
    return LensEngine(dataset,family,reference_mass=parameters.get('reference_mass_msun')).calculate(parameters)[0]
