"""Fast scale-covariant evaluation of the pinned conditional R1 exterior.

The universal radial functions are interpolated once. Actual mass and flux
change the Vainshtein radius and worldtube normalization, not photon coupling.
"""
import numpy as np
from scipy.interpolate import BPoly
from scipy.special import roots_legendre
from .theory.radial_response import ScreenedExterior,_shape_components

class R1Runtime:
    def __init__(self,engine):
        self.e=engine
        # Auxiliary reference radius is a numerical normalization only; rays
        # always obey the physical worldtube radius in LensEngine.
        ref_r0=engine.r0/1000
        h0=engine.data.geometry.get('H0',engine.data.analysis.get('H0',67.4))
        self.ref=ScreenedExterior(M_msun=engine.ref_mass,z_l=engine.data.geometry['z_l'],r0_pc=ref_r0,H0=h0)
        lo=ref_r0;hi=max(100*self.ref.rV_pc,1000*engine.rE)
        self.report=self.ref.prepare_tables(lo,hi,n=641,include_axial=True)
        self.normref=float(_shape_components(ref_r0/self.ref.rV_pc,2)[0])
        self._actual_exteriors={}
        # Integrate the interpolated alpha over each log-radius segment, then
        # Hermite-interpolate its potential with exact projected derivatives.
        grid=np.linspace(np.log(lo),np.log(hi),641);b=np.exp(grid)
        nodes,weights=roots_legendre(12)
        mid=(grid[1:]+grid[:-1])/2;half=np.diff(grid)/2
        xx=mid[:,None]+half[:,None]*nodes
        a=self.ref.monopole_deflection(np.exp(xx))[0]
        increments=half*np.sum(a*np.exp(xx)*weights,axis=1)
        values=np.r_[0.,np.cumsum(increments)]
        alpha,ap,app=self.ref.monopole_deflection(b)
        self.phase=BPoly.from_derivatives(grid,np.column_stack([values,b*alpha,b*alpha+b*b*ap]))

    def _scale(self,massratio,flux):
        if not np.isfinite(flux) or flux<0:raise ValueError('scalar flux must be finite and nonnegative')
        if flux==0:return 0.,0.
        return (massratio*flux)**(1/3),massratio*flux

    def monopole(self,r,massratio,flux):
        scale,pref=self._scale(massratio,flux)
        if scale==0:return tuple(np.zeros_like(r) for _ in range(3))
        b=self.e.rE*r/scale
        alpha,ap,app=self.ref.monopole_deflection(b)
        phase=self.phase(np.log(b))*pref/(4*self.e.mref_pc)
        return phase,alpha*pref/scale*self.e.rE/(4*self.e.mref_pc),ap*pref/scale**2*self.e.rE**2/(4*self.e.mref_pc)

    def quadrupole(self,r,massratio,flux,axial=False):
        scale,pref=self._scale(massratio,flux)
        b=self.e.rE*r
        if scale==0:
            if axial:return tuple(np.zeros_like(r) for _ in range(3))
            # Pure harmonic exterior; no division by a zero monopole state.
            from .theory.radial_response import N2
            q=-4*self.ref.beta_hat*N2*self.e.r0**3/(3*b*b)/(4*self.e.mref_pc)
            return q,-2*q/r,6*q/r**2
        rv=self.ref.rV_pc*scale
        if np.any(b/rv<.003):
            # Deep plateaus can round away the tiny radial correction in
            # tabulated phase values. Direct analytic projected jets retain
            # that correction. This path is used for optional response/state
            # evaluation, not every monopole-only optimizer step.
            key=(float(massratio),float(flux))
            if key not in self._actual_exteriors:
                self._actual_exteriors[key]=ScreenedExterior(M_msun=self.e.ref_mass*massratio,
                    z_l=self.ref.z_l,H0=self.ref.H0,r0_pc=self.e.r0,flux_ratio=flux)
            actual=self._actual_exteriors[key]
            q,qp,qpp=(actual.projected_axial if axial else actual.projected_quad)(b)
            factor=1/(4*self.e.mref_pc)
            return q*factor,qp*factor*self.e.rE,qpp*factor*self.e.rE**2
        norm=float(_shape_components(self.e.r0/rv,2)[0])
        factor=scale*self.normref/norm/(4*self.e.mref_pc)
        q,qp,qpp=(self.ref.projected_axial if axial else self.ref.projected_quad)(b/scale)
        return q*factor,qp*factor/scale*self.e.rE,qpp*factor/scale**2*self.e.rE**2
