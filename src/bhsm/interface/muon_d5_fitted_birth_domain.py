"""Finite sigma-normal birth chart, evaluated only on the future child.

The curve is constructed by shooting OUTWARD from the actual t=0 face.
No child coefficient is evaluated at pre-birth time.  This is coordinate
incidence, not a choice of event transmission or a physical outer state.
"""
from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

from .muon_parent_retarded_hypercharge import WALL
from .muon_sigma_normal_collar_transport import sigma_geometry_point
from .muon_holomorphic_d5_trace_action import (
    d5_sigma_foliation_eta, d5_sigma_normal_flow_germ,
)
from .muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace


class SigmaNormalBirthDomain:
    """Invert the original normal flow on a finite future-domain strip.

    ``history.value(t)`` returns its OWN consistent raw268/time derivative;
    optional ``history.source(t)`` returns an independently declared source
    raw268/time derivative.  These callbacks must support analytic complex
    time inside their actual cells.  The source is never zero-filled.
    ``normal_jet`` is an explicit original-operator callback override used
    by independent chart tests, not a default physical normal selector.
    """

    def __init__(self, history, *, normal_jet=None, rtol=2e-10, atol=2e-13):
        self.history = history
        self.times = np.asarray(history.times, float)
        if (self.times.ndim != 1 or len(self.times) < 2
                or self.times[0] != 0 or np.any(np.diff(self.times) <= 0)):
            raise ValueError('actual future child history beginning at t=0 required')
        self.rtol, self.atol = float(rtol), float(atol)
        self._override = normal_jet
        self._gamma = full_d5_localized_lepton_trace()['gamma5D_particle']
        self.minimum_evaluated_time = np.inf
        self.maximum_evaluated_time = -np.inf
        self._birth_cache = {}

    def _normal(self, t, rho):
        """n, partial_t n, partial_rho n and optional declared source n_j."""
        t = complex(t)
        if t.real < 0 or t.real > self.times[-1] or not 0 < rho <= WALL:
            raise ValueError('original normal callback requested outside actual child domain')
        self.minimum_evaluated_time = min(self.minimum_evaluated_time, t.real)
        self.maximum_evaluated_time = max(self.maximum_evaluated_time, t.real)
        if self._override is not None:
            return self._override(t, rho)
        raw, rate = self.history.value(t)
        raw, rate = np.asarray(raw, complex), np.asarray(rate, complex)
        if raw.shape != (268,) or rate.shape != raw.shape:
            raise ValueError('complete original raw268 and its consistent time derivative required')
        c = sigma_geometry_point(raw, rate, rho)
        n = d5_sigma_foliation_eta(c, gamma=self._gamma, carrier_count=1,
            angular_count=1, sheet_orientation=1)
        flow = d5_sigma_normal_flow_germ(c, n, coordinate_time_first_slot=0)
        out = dict(value=flow['sigma_flow_coordinate_velocity'][0],
            time=flow['sigma_flow_coordinate_velocity_time'][0],
            radial=flow['sigma_flow_coordinate_velocity_radial'][0])
        if hasattr(self.history, 'source'):
            direction, direction_rate = self.history.source(t)
            direction = np.asarray(direction, complex)
            if direction.shape != (268,) or np.asarray(direction_rate).shape != direction.shape:
                raise ValueError('complete independent history source and its derivative required')
            if np.array_equal(direction,rate):
                # Exact equality of operands, not an assumed identification
                # of a general source with time translation.
                out['source']=out['time'].copy()
                return out
            cj = sigma_geometry_point(raw, direction, rho)
            nj = d5_sigma_foliation_eta(cj, gamma=self._gamma, carrier_count=1,
                angular_count=1, sheet_orientation=1)
            N, C, z = (cj[k][0] for k in ('lapse','radial_coframe','coordinate_shift'))
            Nj, Cj, zj = (cj[k+'_first'][0,0] for k in ('lapse','radial_coframe','coordinate_shift'))
            n0, n4 = (nj[k][0] for k in ('sigma_normal_timelike_component','sigma_normal_radial_component'))
            n0j, n4j = (nj[k+'_first'][0,0] for k in ('sigma_normal_timelike_component','sigma_normal_radial_component'))
            nt, ntj = n0/N, n0j/N-n0*Nj/N**2
            out['source'] = np.array([ntj, n4j/C-n4*Cj/C**2-zj*nt-z*ntj])
        return out

    def _ratios(self, t, rho, *, second=False, require_source=False):
        n = self._normal(t, rho)
        v, vt, vr = (np.asarray(n[k],complex) for k in ('value','time','radial'))
        if len(v) != 2 or v[1].real <= 0 or v[0].real < 0:
            raise ValueError('this finite chart requires the actual positive outward radial/time branch')
        f, h = v[0]/v[1], 1/v[1]
        ft, ht = (vt[0]-f*vt[1])/v[1], -vt[1]/v[1]**2
        fr, hr = (vr[0]-f*vr[1])/v[1], -vr[1]/v[1]**2
        values = dict(f=f,h=h,ft=ft,ht=ht,fr=fr,hr=hr)
        if 'source' in n:
            vs = np.asarray(n['source'],complex)
            values.update(fj=(vs[0]-f*vs[1])/v[1],hj=-vs[1]/v[1]**2)
        elif require_source:
            raise ValueError('unknown normal source may not be replaced by zero')
        if second:
            # Holomorphic derivatives of the ORIGINAL callback, not finite
            # differences of a fitted curve.  This germ is local within its
            # actual one-sided temporal cell, never a physical error bound.
            step = 1e-20
            z = self._ratios(complex(t)+1j*step,rho,require_source=require_source)
            values.update(ftt=z['ft'].imag/step,htt=z['ht'].imag/step)
            if 'fj' in values:
                values.update(ftj=z['fj'].imag/step,htj=z['hj'].imag/step)
        if complex(t).imag == 0:
            for key, value in values.items():
                if abs(complex(value).imag) > 2e-11*max(1.,abs(value)):
                    raise ValueError('real child branch required for finite birth incidence')
            return {k:float(complex(v).real) for k,v in values.items()}
        return values

    def _shoot(self, initial_time, birth_rho, *, source=False):
        """Outward rho-parameterized flow stays inside t>=0,rho<=WALL."""
        t0, r0 = float(initial_time), float(birth_rho)
        if t0 < 0 or not 0 < r0 <= WALL:
            raise ValueError('actual future point and positive interior radius required')
        p0 = self._ratios(t0,r0,second=source,require_source=source)
        # t,l,A=dq/dt0,S=dl/dt0.  Remaining entries are source,
        # initial-rho and initial-time derivatives of A,S respectively.
        initial = np.array([t0,0.,1.,0.] + ([0.,0.,0.,0.,-p0['ft'],-p0['ht'],0.,0.] if source else []))
        def rhs(r, y):
            a=self._ratios(y[0],r,second=source,require_source=source)
            t,l,A,S=y[:4]
            base=[a['f'],a['h'],a['ft']*A,a['ht']*A]
            if not source:return base
            tj,lj,Aj,Sj,Ab,Sb,At,St=y[4:]
            tb=-p0['f']*A
            return base+[a['ft']*tj+a['fj'],a['ht']*tj+a['hj'],
                (a['ftt']*tj+a['ftj'])*A+a['ft']*Aj,
                (a['htt']*tj+a['htj'])*A+a['ht']*Aj,
                a['ftt']*tb*A+a['ft']*Ab,a['htt']*tb*A+a['ht']*Ab,
                a['ftt']*A*A+a['ft']*At,a['htt']*A*A+a['ht']*At]
        if r0 == WALL:
            y=initial
        else:
            sol=solve_ivp(rhs,(r0,WALL),initial,method='DOP853',rtol=self.rtol,
                atol=self.atol,max_step=(WALL-r0)/4,dense_output=True)
            if not sol.success:raise ArithmeticError(sol.message)
            y=sol.y[:,-1]
        t,l,A,S=y[:4]
        J=np.array([[A,-p0['f']*A],[S,-p0['h']-p0['f']*S]])
        out=dict(wall_time=t,normal_length=l,original_point=np.array([t0,r0]),
            forward_jacobian=J,shoot_state=y,initial_ratios=p0)
        if source:
            tj,lj,Aj,Sj,Ab,Sb,At,St=y[4:]
            out.update(source=np.array([tj,lj]),
                jacobian_source=np.array([[Aj,-p0['fj']*A-p0['f']*Aj],
                    [Sj,-p0['hj']-p0['fj']*S-p0['f']*Sj]]),
                jacobian_time=np.array([[At,-p0['ft']*A-p0['f']*At],
                    [St,-p0['ht']-p0['ft']*S-p0['f']*St]]),
                jacobian_radial=np.array([[Ab,-p0['fr']*A-p0['f']*Ab],
                    [Sb,-p0['hr']-p0['fr']*S-p0['f']*Sb]]))
        return out

    def _point_at_time_depth(self, initial_time, depth, *, source=False):
        depth=float(depth)
        if depth < 0:raise ValueError('nonnegative inward normal depth required')
        if not depth:return self._shoot(initial_time,WALL,source=source)
        nrad=self._normal(initial_time,WALL)['value'][1].real
        lower=WALL-2*depth*nrad
        if lower<=0:raise ValueError('finite normal strip may not cross its owned polar domain')
        for _ in range(12):
            if self._shoot(initial_time,lower)['normal_length']>=depth:break
            lower=WALL-2*(WALL-lower)
            if lower<=0:raise ValueError('no valid finite strip bracket before polar boundary')
        else:raise ArithmeticError('could not bracket original finite normal length')
        def equation(r):return self._shoot(initial_time,r)['normal_length']-depth
        r=brentq(equation,lower,WALL,xtol=4*np.finfo(float).eps*WALL,
            rtol=4*np.finfo(float).eps)
        out=self._shoot(initial_time,r,source=source)
        out['normal_length_residual']=out['normal_length']-depth
        return out

    def birth(self, depth, *, source=False):
        """Finite q_birth(s), slope and declared source at fixed proper s."""
        key=(float(depth),bool(source))
        if key in self._birth_cache:return self._birth_cache[key]
        if not source and (float(depth),True) in self._birth_cache:
            return self._birth_cache[(float(depth),True)]
        if source and (float(depth),False) in self._birth_cache:
            cached=self._birth_cache[(float(depth),False)]
            a=self._shoot(0.,cached['birth_rho'],source=True)
            a['normal_length_residual']=a['normal_length']-float(depth)
        else:
            a=self._point_at_time_depth(0.,depth,source=source)
        J=a['forward_jacobian'];slope=J[0,1]/J[1,1]
        out=dict(depth=float(depth),wall_label=a['wall_time'],birth_rho=a['original_point'][1],
            slope=slope,imposed_birth_time=0.,normal_length_residual=a['normal_length_residual'] if depth else 0.,
            outward_shoot=a,source=None,slope_source=None)
        if source:
            rbj=-a['source'][1]/J[1,1]
            qj=a['source'][0]+J[0,1]*rbj
            totalJ=a['jacobian_source']+a['jacobian_radial']*rbj
            slopej=(totalJ[0,1]-slope*totalJ[1,1])/J[1,1]
            out.update(source=qj,slope_source=slopej,birth_rho_source=rbj)
        self._birth_cache[key]=out
        return out

    def verify_birth(self, depth):
        """Independent inverse characteristic, with t as the valid parameter.

        Its original level face is t=0 by parameterization.  Agreement of
        the independently returned NORMAL LENGTH with the requested s,
        not that imposed zero alone, verifies the finite incidence.
        This is an arithmetic cross-check, not a continuum enclosure.
        """
        birth=self.birth(depth)
        q=float(birth['wall_label'])
        if not depth:
            return dict(imposed_birth_time=0.,normal_length_residual=0.,
                birth_radius_residual=0.,original_radial_rows=0.,
                original_length_rows=0.,independent_method='RK45, coordinate time parameter')
        def rhs(t,y):
            n=self._normal(t,WALL+y[0])['value'].real
            if n[0]<=0:raise ValueError('inverse birth clock became characteristic')
            return [n[1]/n[0],-1/n[0]]
        # Integrate the radial displacement, avoiding subtraction of two
        # order-one radii in this independent derivative check.
        sol=solve_ivp(rhs,(q,0.),[0.,0.],method='RK45',rtol=self.rtol,
            atol=self.atol,max_step=q/7,dense_output=True)
        if not sol.success:raise ArithmeticError(sol.message)
        # Independently differentiate the RK dense polynomial at actual
        # off-stage times.  Five-point differences report their arithmetic
        # floor explicitly instead of replacing them with defining rows.
        rows=[]
        for j in range(len(sol.t)-1):
            lo,hi=sol.t[j:j+2];mid=(lo+hi)/2;h=abs(hi-lo)/16
            if abs(hi-lo)<q*1e-9:
                continue  # possible rounded final RK remainder has no useful difference scale
            samples=[sol.sol(mid+k*h) for k in (-2,-1,1,2)]
            derivative=(samples[0]-8*samples[1]+8*samples[2]-samples[3])/(12*h)
            rows.append(derivative-rhs(mid,sol.sol(mid)))
        rows=np.asarray(rows)
        return dict(imposed_birth_time=0.,normal_length_residual=float(sol.y[1,-1]-depth),
            birth_radius_residual=float(WALL+sol.y[0,-1]-birth['birth_rho']),
            original_radial_rows=float(np.max(abs(rows[:,0]))),
            original_length_rows=float(np.max(abs(rows[:,1]))),
            independent_method='RK45, coordinate time parameter; off-stage five-point dense-polynomial derivative',
            derivative_error_scope='finite-difference arithmetic and RK dense-polynomial errors; no continuum bound')

    def point(self, vartheta, depth, *, source=False):
        """X(vartheta+q_birth(s),s) and complete coordinate first/source maps."""
        theta=float(vartheta)
        if theta<0:raise ValueError('boundary-fitted child time vartheta must be nonnegative')
        birth=self.birth(depth,source=source)
        target=theta+birth['wall_label']
        if theta==0:
            a=birth['outward_shoot']
        else:
            # The two original endpoint equations are solved JOINTLY.
            # This reuses the finite birth solution as the initializer,
            # rather than nesting many separate radial shooting roots.
            t,r=theta,birth['birth_rho']
            for _ in range(10):
                a=self._shoot(t,r)
                residual=np.array([a['wall_time']-target,a['normal_length']-depth])
                # A unit-radius float cannot resolve an arbitrarily small
                # proper-depth correction.  Its induced wall-clock floor
                # is retained explicitly; this is not physical admission.
                clock_floor=abs(a['forward_jacobian'][0,1])*np.spacing(abs(r))
                if abs(residual[0])<max(1e-18,abs(target)*2e-13,clock_floor) and abs(residual[1])<4*np.finfo(float).eps*WALL:
                    break
                step=np.linalg.solve(a['forward_jacobian'],residual)
                fraction=1.
                while not (0<=t-fraction*step[0]<=self.times[-1] and 0<r-fraction*step[1]<=WALL):
                    fraction*=.5
                    if fraction<2**-30:raise ValueError('fitted chart Newton step leaves actual child domain')
                t,r=np.array([t,r])-fraction*step
            else:raise ArithmeticError('original finite fitted-point equations did not converge')
            if source:a=self._shoot(t,r,source=True)
            a['normal_length_residual']=a['normal_length']-depth
        J=a['forward_jacobian'];Q=np.array([[1.,-birth['slope']],[0.,1.]])
        Jfit=Q@J;Xfit=np.linalg.inv(Jfit)
        out=dict(original_point=a['original_point'],wall_label=target,
            fitted_point=np.array([theta,float(depth)]),birth=birth,
            forward_jacobian=Jfit,inverse_jacobian=Xfit,
            coordinate_inverse_residual=Jfit@Xfit-np.eye(2),
            actual_normal_length_residual=a.get('normal_length_residual',0.),
            wall_label_residual=a['wall_time']-target,
            radial_float_wall_clock_floor=abs(J[0,1])*np.spacing(abs(a['original_point'][1])),
            original_point_source=None,forward_jacobian_source=None,inverse_jacobian_source=None)
        if source:
            xj=np.linalg.solve(J,np.array([birth['source'],0.])-a['source'])
            dJ=a['jacobian_source']+a['jacobian_time']*xj[0]+a['jacobian_radial']*xj[1]
            Qj=np.array([[0.,-birth['slope_source']],[0.,0.]])
            dJfit=Qj@J+Q@dJ
            out.update(original_point_source=xj,forward_jacobian_source=dJfit,
                inverse_jacobian_source=-Xfit@dJfit@Xfit)
        return out


def fitted_d5_coefficients(time, radial, body, chart, *, source=None):
    """Pull back the FULL ambient D5; no field/frame/density rescaling.

    If Q=q, s is the unfitted normal chart, this is precisely
    partial_s|Q=partial_s|vartheta-q_birth'(s) partial_vartheta.
    Any field, frame or density coefficient supplied in body is pulled
    back at the SAME original point.  Its source must already include
    vertex source plus original-coordinate derivative times X_source.
    """
    T,R,A=(np.asarray(k,complex) for k in (time,radial,body))
    if T.shape!=R.shape or T.shape!=A.shape:
        raise ValueError('same full original D5 coefficient shapes required')
    J=np.asarray(chart['forward_jacobian'])
    out=dict(time=T*J[0,0]+R*J[0,1],normal=T*J[1,0]+R*J[1,1],body=A)
    if source is not None:
        dJ=chart.get('forward_jacobian_source')
        if dJ is None:raise ValueError('full source-dependent fitted chart required')
        Tj,Rj,Aj=(np.asarray(k,complex) for k in source)
        if Tj.shape!=T.shape or Rj.shape!=T.shape or Aj.shape!=T.shape:
            raise ValueError('complete same-shape original coefficient sources required')
        out.update(time_source=Tj*J[0,0]+Rj*J[0,1]+T*dJ[0,0]+R*dJ[0,1],
            normal_source=Tj*J[1,0]+Rj*J[1,1]+T*dJ[1,0]+R*dJ[1,1],body_source=Aj)
    return out


def pullback_value_first(value, original_first, chart, *, source=None,
        original_second=None,source_first=None):
    """Same chart for arbitrary source/frame/density values and derivatives.

    This is a coefficient-density pullback. A coordinate integration
    density additionally consumes abs(det inverse_jacobian), whose
    independent source is returned rather than discarded.
    """
    v=np.asarray(value);dv=np.asarray(original_first)
    if dv.shape!=(2,)+v.shape:raise ValueError('both original t/rho derivatives required')
    X=np.asarray(chart['inverse_jacobian'])
    out=dict(value=v,first=np.einsum('i...,ij->j...',dv,X),
        volume_jacobian=abs(np.linalg.det(X)))
    if source is not None:
        xj=chart.get('original_point_source');Xj=chart.get('inverse_jacobian_source')
        if xj is None or Xj is None:raise ValueError('unknown source/domain contact may not be zero-filled')
        sj=np.asarray(source)
        if sj.shape!=v.shape:raise ValueError('same-shape original coefficient source required')
        out.update(source=sj+np.einsum('i...,i->...',dv,xj),
            volume_jacobian_source=out['volume_jacobian']*np.trace(np.linalg.solve(X,Xj)))
        if (original_second is None)!=(source_first is None):
            raise ValueError('source-first pullback requires both original Hessian and source gradient')
        if original_second is not None:
            ddv=np.asarray(original_second);ds=np.asarray(source_first)
            if ddv.shape!=(2,2)+v.shape or ds.shape!=dv.shape:
                raise ValueError('complete original two-coordinate Hessian/source gradient required')
            d_at_point=ds+np.einsum('ij...,j->i...',ddv,xj)
            out['first_source']=np.einsum('i...,ij->j...',d_at_point,X)+np.einsum('i...,ij->j...',dv,Xj)
    return out


def evaluate_child_fitted_operator(history, depth, vartheta, *, domain=None,
        verify_birth=True):
    """Apply the finite child chart to its ORIGINAL inherited full D5.

    This evaluates an actual operator/domain/source operand.  No child
    section, mechanical formation mode, normal profile, event base map or
    U_R is supplied by this coordinate application.  In particular equal
    numerical parent/child radii do not identify their physical event map.
    """
    from .muon_birth_inherited_finite_normal_phase import affine_geometry_germ
    from .muon_holomorphic_d5_trace_action import d5_trial_stage_coefficients
    from .muon_combined_f_eta_contact import combined_f_eta_contact
    from .muon_full_d5_source_first import full_d5_differential_source_first
    from .muon_full_d5_localized_lepton_trace import moving_d5_material_trace_frame
    from .muon_parent_maxwell_full_weak import FIELD_ORDER
    from .muon_birth_trace_enriched_action import trace_enriched_radial_basis
    if not hasattr(history,'original_phase_operands') or not hasattr(history,'original_radial_representation'):
        raise ValueError('actual original child parent/reference and radial-frame operands required')
    operands=history.original_phase_operands
    pair=np.asarray(operands['initial_pair']);refs0=np.asarray(operands['reference_pair'])
    if pair.shape!=(2,268) or refs0.shape!=pair.shape:
        raise ValueError('complete original inherited parent/reference pair required')
    full=full_d5_localized_lepton_trace()
    if domain is None:domain=SigmaNormalBirthDomain(history)
    chart=domain.point(vartheta,depth,source=True)
    t,r=chart['original_point'];tj,rj=chart['original_point_source']
    def geometry_rate(x):
        out=np.zeros_like(x);out[:37]=x[37:74];out[98]=x[99]
        return out
    def original_point(radial):
        raw,rate=history.value(t)
        source,source_rate=history.source(t)
        if not np.array_equal(source,rate) or np.any(source_rate):
            raise ValueError('this child application retains the recovered original common translation source only')
        p=affine_geometry_germ(pair[0],t)
        refs=np.array([affine_geometry_germ(x,t) for x in refs0])
        dp=geometry_rate(pair[0])[:,None]
        drefs=np.array([geometry_rate(x)[:,None] for x in refs0])
        rho=np.array([radial])
        basis,br=trace_enriched_radial_basis(history.original_radial_representation,rho)
        B=np.zeros((1,80,1,5,4));Br=np.zeros_like(B)
        for k,l in enumerate(history.original_radial_representation['gauge_labels']):
            f,i,j=FIELD_ORDER.index(l['field']),l['internal'],l['radial']
            B[:,k,0,f,i]=basis[:,j];Br[:,k,0,f,i]=br[:,j]
        rep=dict(rho=rho,gauge_basis=B,gauge_radial_basis=Br)
        c=d5_trial_stage_coefficients(raw,rate[:,None],p,dp,refs,drefs,rep,rho,side='child')
        differential={}
        for eps in (1,-1):
            eta,etaj={},{}
            for branch in ('particle','conjugate'):
                e=combined_f_eta_contact(c,gamma=full['gamma5D_'+branch],carrier_count=16,
                    angular_count=1,sheet_orientation=eps)
                eta[branch]=e['combined_f_eta_contact'];etaj[branch]=e['combined_f_eta_contact_first'][0]
            differential[eps]=full_d5_differential_source_first(c,np.zeros((3,1,1)),source_slot=0,
                sheet_orientation=eps,full_representation=full,eta_contacts=eta,eta_contacts_first=etaj)
        return c,differential
    c,base=original_point(r)
    # The original coefficient routine owns real radial points. This
    # independent local five-point derivative is explicitly finite; it is
    # not a continuum enclosure or a zero radial/domain contact.
    step=min((WALL-r)/3,r/8,1e-4)
    if step<=16*np.finfo(float).eps*WALL:
        raise ValueError('finite radial coefficient derivative requires an interior fitted point')
    probes=[original_point(r+k*step)[1] for k in (-2,-1,1,2)]
    out=dict(fitted_coordinates=np.array([vartheta,depth]),original_child_coordinates=chart['original_point'],
        original_child_coordinates_source=chart['original_point_source'],
        child_fitted_forward_jacobian=chart['forward_jacobian'],
        child_fitted_inverse_jacobian=chart['inverse_jacobian'],
        child_fitted_forward_jacobian_source=chart['forward_jacobian_source'],
        child_fitted_inverse_jacobian_source=chart['inverse_jacobian_source'],
        child_coordinate_inverse_rows=chart['coordinate_inverse_residual'],
        child_birth=np.array([chart['birth']['wall_label'],chart['birth']['slope'],chart['birth']['source'],chart['birth']['slope_source']]),
        child_birth_radius=np.array(chart['birth']['birth_rho']),
        child_birth_radius_source=np.array(chart['birth']['birth_rho_source']),
        child_birth_normal_length_residual=np.array(chart['birth']['normal_length_residual']))
    principal_checks=[]
    for eps,name in ((1,'plus'),(-1,'minus')):
        for branch in ('particle','conjugate'):
            blocks=base[eps]['value']['blocks'][branch]
            firsts=base[eps]['first']['blocks'][branch]
            values=[];sources=[];radials=[]
            for key in ('time','radial','body'):
                value=blocks[key][0];time_first=firsts[key][0]
                radial_first=(probes[0][eps]['value']['blocks'][branch][key][0]
                    -8*probes[1][eps]['value']['blocks'][branch][key][0]
                    +8*probes[2][eps]['value']['blocks'][branch][key][0]
                    -probes[3][eps]['value']['blocks'][branch][key][0])/(12*step)
                values.append(value);radials.append(radial_first)
                sources.append(time_first*(1+tj)+radial_first*rj)
            app=fitted_d5_coefficients(*values,chart,source=tuple(sources))
            prefix='child_'+name+'_'+branch+'_'
            for key,value in app.items():out[prefix+key+'64']=value
            for key,value in zip(('time','radial','body'),radials):out[prefix+key+'_original_radial64']=value
            # Recover original principal coefficients from the fitted ones
            # using the separately solved inverse coordinate differential.
            X=chart['inverse_jacobian']
            reconstructed_t=app['time']*X[0,0]+app['normal']*X[0,1]
            reconstructed_r=app['time']*X[1,0]+app['normal']*X[1,1]
            principal_checks.extend([np.max(abs(reconstructed_t-values[0])),np.max(abs(reconstructed_r-values[1]))])
    mu=c['volume_density'][0]
    mut=c['volume_density_first'][0,0]
    mur=mu*(c['lapse_log_radial'][0]+c['radial_coframe_log_radial'][0]+3*c['radius_log_radial'][0])
    density=pullback_value_first(np.asarray(mu),np.array([mut,mur]),chart,source=np.asarray(mut))
    out.update(child_original_density=np.array(mu),child_original_density_time=np.array(mut),
        child_original_density_radial=np.array(mur),child_coefficient_density_source=np.array(density['source']),
        child_coordinate_volume_jacobian=np.array(density['volume_jacobian']),
        child_coordinate_volume_jacobian_source=np.array(density['volume_jacobian_source']),
        child_fitted_integration_density=np.array(mu*density['volume_jacobian']),
        child_fitted_integration_density_source=np.array(density['source']*density['volume_jacobian']+mu*density['volume_jacobian_source']))
    # The SAME actual sigma-normal frame and its source product are used
    # throughout; these are trace numerators, with u_R/u_L still independent.
    n=domain._normal(t,r);v,vt,vr=(np.asarray(n[k]).real for k in ('value','time','radial'))
    N,C,z=(c[k][0].real for k in ('lapse','radial_coframe','coordinate_shift'))
    Nt,Ct,zt=(c[k+'_first'][0,0].real for k in ('lapse','radial_coframe','coordinate_shift'))
    Nr=N*c['lapse_log_radial'][0].real;Cr=C*c['radial_coframe_log_radial'][0].real;zr=c['coordinate_shift_radial'][0].real
    n0,n4=N*v[0],C*(v[1]+z*v[0]);U=n0/n4
    def Ufirst(dv,dN,dC,dz):
        dn0=dN*v[0]+N*dv[0]
        dn4=dC*(v[1]+z*v[0])+C*(dv[1]+dz*v[0]+z*dv[0])
        return (dn0-U*dn4)/n4
    Ut=Ufirst(vt,Nt,Ct,zt);Ur=Ufirst(vr,Nr,Cr,zr);Uj=Ut*(1+tj)+Ur*rj
    for eps,name in ((1,'plus'),(-1,'minus')):
        frame=moving_d5_material_trace_frame(-eps*U,-eps*Uj,full_representation=full)
        out['child_'+name+'_normal_frame128']=frame['spin_boost128']
        out['child_'+name+'_normal_frame_source128']=frame['spin_boost_first128']
    check=domain.verify_birth(depth) if verify_birth else None
    report=dict(classification='PROVISIONAL_ACTUAL_INHERITED_CHILD_D5_FITTED_OPERATOR_AND_SOURCE_APPLICATION',
        original_coordinates=[float(t),float(r)],fitted_coordinates=[float(vartheta),float(depth)],
        birth_label=float(chart['birth']['wall_label']),birth_slope=float(chart['birth']['slope']),
        birth_label_source=float(chart['birth']['source']),birth_slope_source=float(chart['birth']['slope_source']),
        original_normal_length_residual=float(chart['actual_normal_length_residual']),wall_label_residual=float(chart['wall_label_residual']),
        radial_float_wall_clock_floor=float(chart['radial_float_wall_clock_floor']),
        coordinate_inverse_max=float(np.max(abs(chart['coordinate_inverse_residual']))),
        original_principal_recovery_max=float(max(principal_checks)),independent_birth_check=check,
        minimum_evaluated_child_time=float(domain.minimum_evaluated_time),maximum_evaluated_child_time=float(domain.maximum_evaluated_time),
        background_scope='recovered original provisional outgoing affine history, inherited pp-rp+rc connection, exact stored old radial frame',
        radial_coefficient_derivative=dict(method='local five-point original-callback derivative',step=float(step),continuum_bound=None),
        source_scope='exact original common translation Xi plus full moving fitted-coordinate Jacobian and frame/density contacts; complete physical source remains held',
        carrier='all3families particle/conjugate Spin4xSM16, repeated64 blocks; constant angular truncation',
        child_physical_section_assigned=False,mechanical_mode_assigned=False,U_R_assigned=False,event_basepoint_map_assigned=False,
        child_D5_solution_residual=None,event_residual=None,physical_outer_residual=None,normal_profile_normalization_residual=None,
        physical_admission=False,Higgs_seam_added_as_bulk_mass=False,local_Maxwell_Higgs_removed_again=False,
        error_scope='finite coordinate/unsquared-operator application; no continuum/angular/exterior/source-bound or physical admission')
    return out,report
