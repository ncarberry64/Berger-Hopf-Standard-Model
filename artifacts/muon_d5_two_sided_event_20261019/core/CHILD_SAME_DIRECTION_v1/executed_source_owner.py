"""Missing child-normal source on the saved finite birth/operator domain.

The saved value chart and prescribed-Xi source are inputs, not recalculated
physical solutions. Two additional columns are evaluated: the executed
normal displacement and the coefficient of the still free normal rate.
Inherited additional columns are held explicitly while their nonzero
prescribed jets remain in the cached baseline.
"""
from __future__ import annotations
import numpy as np

from .muon_actual_normal_shape_source import proper_normal_shape_coefficient
from .muon_d5_fitted_birth_domain import SigmaNormalBirthDomain,fitted_d5_coefficients
from .muon_d5_event_bundle_incidence import original_event_coefficients
from .muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace,moving_d5_material_trace_frame
from .muon_combined_f_eta_contact import combined_f_eta_contact
from .muon_full_d5_source_first import full_d5_differential_source_first
from .muon_sigma_normal_collar_transport import sigma_geometry_point


class ChildNormalCorrectionHistory:
    """A mathematical normal correction column, never the physical source.

    Column0 uses psi(t)=psi_E1; column1 uses psi(t)=t, its coefficient
    being the unassigned D_t psi_E1. Neither column removes the prescribed
    Xi or the inherited-state/source data of the completed application.
    """
    def __init__(self,history,psi_e1,*,free_rate_column=False):
        self.history=history;self.times=np.asarray(history.times,float)
        if self.times[0]!=0:raise ValueError('actual future child beginning at E1 required')
        self.psi_e1=complex(psi_e1);self.free_rate=bool(free_rate_column)
        self.original_phase_operands=history.original_phase_operands
        self.original_radial_representation=history.original_radial_representation
        self.P=np.asarray(self.original_phase_operands['resolved_phase_coordinate_lift'])
        self._cache={}
        rates=[np.asarray(history.value(t)[1]) for t in self.times]
        if any(not np.array_equal(rates[0],rate) for rate in rates[1:]):
            raise ValueError('this provisional correction owns the recovered affine child value history')

    def value(self,time):return self.history.value(time)

    def source(self,time):
        key=complex(time)
        if key not in self._cache:
            raw,rate=self.history.value(time);a=proper_normal_shape_coefficient(raw,self.P)
            r=np.asarray(rate)[:100];at=a['raw_gradient']@r;att=r@a['raw_hessian']@r
            psi=complex(time) if self.free_rate else self.psi_e1
            psit=1. if self.free_rate else 0.
            b=np.zeros(268,complex);bt=np.zeros_like(b)
            b[98],b[99]=a['value']*psi,at*psi+a['value']*psit
            bt[98],bt[99]=b[99],att*psi+2*at*psit
            self._cache[key]=(b,bt)
        return tuple(x.copy() for x in self._cache[key])


def additional_cached_chart_source(correction_history,cached):
    """New variational shoots at saved endpoints; no birth/root replay.

    The value path is evaluated as a dependency of the newly changed source
    direction. Saved birth radius, point and chart matrices stay fixed.
    """
    depth=float(cached['fitted_coordinates'][1]);q0,slope=np.asarray(cached['child_birth'])[:2]
    birth_rho=float(cached['child_birth_radius']);point=np.asarray(cached['original_child_coordinates'])
    domain=SigmaNormalBirthDomain(correction_history)
    birth=domain._shoot(0.,birth_rho,source=True)
    Jb=birth['forward_jacobian'];rbj=-birth['source'][1]/Jb[1,1]
    qj=birth['source'][0]+Jb[0,1]*rbj
    dJb=birth['jacobian_source']+birth['jacobian_radial']*rbj
    slopej=(dJb[0,1]-slope*dJb[1,1])/Jb[1,1]
    shoot=domain._shoot(*point,source=True)
    Jfit=np.asarray(cached['child_fitted_forward_jacobian'])
    Xfit=np.asarray(cached['child_fitted_inverse_jacobian'])
    Q=np.array([[1.,-slope],[0.,1.]])
    J=np.linalg.solve(Q,Jfit)
    xj=np.linalg.solve(J,np.array([qj,0.])-shoot['source'])
    dJ=shoot['jacobian_source']+shoot['jacobian_time']*xj[0]+shoot['jacobian_radial']*xj[1]
    Qj=np.array([[0.,-slopej],[0.,0.]])
    dJfit=Qj@J+Q@dJ;dXfit=-Xfit@dJfit@Xfit
    out=dict(original_point=point.copy(),forward_jacobian=Jfit.copy(),inverse_jacobian=Xfit.copy(),
        original_point_source=xj,forward_jacobian_source=dJfit,inverse_jacobian_source=dXfit,
        birth_source=np.array([qj,slopej]),birth_radius_source=np.array(rbj),
        birth_source_constraint_rows=np.array([birth['source'][1]+Jb[1,1]*rbj,
            qj-birth['source'][0]-Jb[0,1]*rbj]),
        point_source_constraint_rows=J@xj+shoot['source']-np.array([qj,0.]),
        inverse_source_rows=dJfit@Xfit+Jfit@dXfit)
    report=dict(cached_birth_label_difference=float(abs(birth['wall_time']-q0)),
        cached_birth_slope_difference=float(abs(Jb[0,1]/Jb[1,1]-slope)),
        cached_birth_normal_length_residual=float(birth['normal_length']-depth),
        cached_point_jacobian_difference_max=float(np.max(abs(shoot['forward_jacobian']-J))),
        cached_point_normal_length_residual=float(shoot['normal_length']-depth),
        original_birth_source_constraint_max=float(np.max(abs(out['birth_source_constraint_rows']))),
        original_point_source_constraint_max=float(np.max(abs(out['point_source_constraint_rows']))),
        coordinate_inverse_source_max=float(np.max(abs(out['inverse_source_rows']))),
        minimum_evaluated_child_time=float(domain.minimum_evaluated_time),
        maximum_evaluated_child_time=float(domain.maximum_evaluated_time),
        finite_birth_root_repeated=False,cached_point_Newton_repeated=False,
        value_trajectory_scope='original callbacks evaluated only along the new source variational shoots at saved endpoints; cached values are retained',
        physical_admission=False)
    return out,report,domain


def recover_cached_original_coefficients(cached,prefix):
    """Undo the completed chart/source pullback, retaining saved finite jets."""
    J=np.asarray(cached['child_fitted_forward_jacobian']);X=np.asarray(cached['child_fitted_inverse_jacobian'])
    Jx=np.asarray(cached['child_fitted_forward_jacobian_source']);xj=np.asarray(cached['original_child_coordinates_source'])
    tf,nf,A=(cached[prefix+key+'64'] for key in ('time','normal','body'))
    T=tf*X[0,0]+nf*X[0,1];R=tf*X[1,0]+nf*X[1,1]
    st=cached[prefix+'time_source64']-T*Jx[0,0]-R*Jx[0,1]
    sn=cached[prefix+'normal_source64']-T*Jx[1,0]-R*Jx[1,1]
    total=(st*X[0,0]+sn*X[0,1],st*X[1,0]+sn*X[1,1],cached[prefix+'body_source64'])
    radial=tuple(cached[prefix+key+'_original_radial64'] for key in ('time','radial','body'))
    if abs(1+xj[0])<1e-12:raise ValueError('cached translation-source recovery is singular')
    time=tuple((a-b*xj[1])/(1+xj[0]) for a,b in zip(total,radial))
    return (T,R,A),time,radial


def _differential_columns(c,full,column_count):
    output={}
    for eps in (1,-1):
        eta={};first={}
        for branch in ('particle','conjugate'):
            e=combined_f_eta_contact(c,gamma=full['gamma5D_'+branch],carrier_count=16,angular_count=1,sheet_orientation=eps)
            eta[branch]=e['combined_f_eta_contact'];first[branch]=e['combined_f_eta_contact_first']
        output[eps]=[full_d5_differential_source_first(c,np.zeros((3,1,1)),source_slot=j,
            sheet_orientation=eps,full_representation=full,eta_contacts=eta,
            eta_contacts_first={branch:a[j] for branch,a in first.items()}) for j in range(column_count)]
    return output


def evaluate_child_same_direction(history,cached,psi_e1):
    """Consume the missing child normal source and its free-rate coefficient."""
    corrections=[ChildNormalCorrectionHistory(history,psi_e1),
        ChildNormalCorrectionHistory(history,psi_e1,free_rate_column=True)]
    charts=[];chart_reports=[];domains=[]
    for correction in corrections:
        chart,report,domain=additional_cached_chart_source(correction,cached)
        charts.append(chart);chart_reports.append(report);domains.append(domain)
    t,r=np.asarray(cached['original_child_coordinates'])
    normal=np.column_stack([correction.source(t)[0] for correction in corrections])
    directions=dict(raw=normal,parent=np.zeros((268,2),complex),references=np.zeros((2,268,2),complex))
    c=original_event_coefficients(history,float(t),[r],side='child',directions=directions)
    full=full_d5_localized_lepton_trace();differential=_differential_columns(c,full,2)
    out={key:a.copy(order='K') for key,a in cached.items()}
    out.update(child_additional_normal_source_columns268=normal,
        child_prescribed_raw_source268=np.asarray(history.source(t)[0]),
        child_corrected_particular_raw_source268=np.asarray(history.source(t)[0])+normal[:,0],
        child_free_normal_rate_raw_source268=normal[:,1])
    value_checks=[];operator_source_checks=[]
    for eps,name in ((1,'plus'),(-1,'minus')):
      for branch in ('particle','conjugate'):
        prefix='child_'+name+'_'+branch+'_'
        values,time,radial=recover_cached_original_coefficients(cached,prefix)
        live=differential[eps][0]['value']['blocks'][branch]
        value_checks.extend(float(np.max(abs(value-live[key][0]))) for value,key in zip(values,('time','radial','body')))
        for j,chart in enumerate(charts):
            normal_source=tuple(differential[eps][j]['first']['blocks'][branch][key][0]
                +dt*chart['original_point_source'][0]+dr*chart['original_point_source'][1]
                for key,dt,dr in zip(('time','radial','body'),time,radial))
            app=fitted_d5_coefficients(*values,chart,source=normal_source)
            tag='normal_displacement' if j==0 else 'free_normal_rate'
            for key in ('time','normal','body'):
                increment=app[key+'_source'];out[prefix+key+'_'+tag+'_source64']=increment
                if j==0:out[prefix+key+'_source64']=cached[prefix+key+'_source64']+increment
            # Inverse differentiation independently reconstructs each
            # original principal source including the moving chart term.
            J=chart['forward_jacobian'];X=chart['inverse_jacobian'];dX=chart['inverse_jacobian_source']
            recT=app['time_source']*X[0,0]+app['normal_source']*X[0,1]+app['time']*dX[0,0]+app['normal']*dX[0,1]
            recR=app['time_source']*X[1,0]+app['normal_source']*X[1,1]+app['time']*dX[1,0]+app['normal']*dX[1,1]
            operator_source_checks.extend([float(np.max(abs(recT-normal_source[0]))),float(np.max(abs(recR-normal_source[1])))])
    raw,rate=history.value(t);ctime=sigma_geometry_point(raw,rate,r)
    N,C,z=(ctime[key][0] for key in ('lapse','radial_coframe','coordinate_shift'))
    Nt,Ct,zt=(ctime[key+'_first'][0,0] for key in ('lapse','radial_coframe','coordinate_shift'))
    Nr=N*ctime['lapse_log_radial'][0];Cr=C*ctime['radial_coframe_log_radial'][0];zr=ctime['coordinate_shift_radial'][0]
    mu=complex(cached['child_original_density']);mut=complex(cached['child_original_density_time']);mur=complex(cached['child_original_density_radial'])
    X=np.asarray(cached['child_fitted_inverse_jacobian']);volume=float(cached['child_coordinate_volume_jacobian'])
    for j,(chart,domain) in enumerate(zip(charts,domains)):
        tag='normal_displacement' if j==0 else 'free_normal_rate';xj=chart['original_point_source']
        out['child_'+tag+'_point_source']=xj
        out['child_'+tag+'_forward_jacobian_source']=chart['forward_jacobian_source']
        out['child_'+tag+'_inverse_jacobian_source']=chart['inverse_jacobian_source']
        out['child_'+tag+'_birth_source']=chart['birth_source']
        out['child_'+tag+'_birth_radius_source']=chart['birth_radius_source']
        for key in ('birth_source_constraint_rows','point_source_constraint_rows','inverse_source_rows'):
            out['child_'+tag+'_'+key]=chart[key]
        muj=c['volume_density_first'][j,0]+mut*xj[0]+mur*xj[1]
        volj=volume*np.trace(np.linalg.solve(X,chart['inverse_jacobian_source']))
        out['child_'+tag+'_coefficient_density_source']=np.array(muj)
        out['child_'+tag+'_coordinate_volume_jacobian_source']=np.array(volj)
        out['child_'+tag+'_fitted_integration_density_source']=np.array(muj*volume+mu*volj)
        n=domain._normal(t,r);v,vt,vr=(np.asarray(n[key]) for key in ('value','time','radial'))
        dv=n['source']+vt*xj[0]+vr*xj[1]
        dN=c['lapse_first'][j,0]+Nt*xj[0]+Nr*xj[1]
        dC=c['radial_coframe_first'][j,0]+Ct*xj[0]+Cr*xj[1]
        dz=c['coordinate_shift_first'][j,0]+zt*xj[0]+zr*xj[1]
        n0,n4=N*v[0],C*(v[1]+z*v[0]);U=n0/n4
        dn0=dN*v[0]+N*dv[0];dn4=dC*(v[1]+z*v[0])+C*(dv[1]+dz*v[0]+z*dv[0]);dU=(dn0-U*dn4)/n4
        for eps,name in ((1,'plus'),(-1,'minus')):
            frame=moving_d5_material_trace_frame(-eps*U,-eps*dU,full_representation=full)
            out['child_'+name+'_'+tag+'_normal_frame_source128']=frame['spin_boost_first128']
            value_checks.append(float(np.max(abs(frame['spin_boost128']-cached['child_'+name+'_normal_frame128']))))
            if j==0:out['child_'+name+'_normal_frame_source128']=cached['child_'+name+'_normal_frame_source128']+frame['spin_boost_first128']
        if j==0:
            out['original_child_coordinates_source']=cached['original_child_coordinates_source']+xj
            out['child_fitted_forward_jacobian_source']=cached['child_fitted_forward_jacobian_source']+chart['forward_jacobian_source']
            out['child_fitted_inverse_jacobian_source']=cached['child_fitted_inverse_jacobian_source']+chart['inverse_jacobian_source']
            out['child_birth'][2:]=cached['child_birth'][2:]+chart['birth_source']
            out['child_birth_radius_source']=cached['child_birth_radius_source']+chart['birth_radius_source']
            out['child_coefficient_density_source']=cached['child_coefficient_density_source']+muj
            out['child_coordinate_volume_jacobian_source']=cached['child_coordinate_volume_jacobian_source']+volj
            out['child_fitted_integration_density_source']=cached['child_fitted_integration_density_source']+muj*volume+mu*volj
    report=dict(classification='EVALUATED_CHILD_SAME_DIRECTION_NORMAL_ADDITION_ON_CACHED_VALID_DOMAIN',
        psi_child_E1=float(np.real(psi_e1)),free_child_normal_rate=None,
        source_family='Xi_child_corrected=Xi_prescribed+B_normal*psi_child_E1+nu_child*B_normal_rate; nu_child=D_t psi_child_E1 remains free',
        extension_scope='provisional psi(t)=psi_E1+t*nu; no formation mode or physical rate selected',
        prescribed_Xi_source_reused=True,cached_value_operator_and_chart_reused=True,
        moving_child_evaluation_included_once=True,
        inherited_scope='cached nonzero prescribed born-parent/reference jets retained; additional normal-induced inherited jets held explicitly and remain separate physical unknown columns',
        normal_columns=chart_reports,original_value_identity_max=max(value_checks),
        original_principal_source_recovery_max=max(operator_source_checks),
        inherited_profile='unchanged original pp-rp+rc composed before restriction',
        radial_derivative_scope='reused saved finite five-point original-coefficient derivatives; recorded radial/domain errors retained',
        child_D5_section=None,child_D5_solution_residual=None,outer_conditions_solved=False,
        normal_profile_normalization=None,homogeneous_coordinates_selected=False,
        full_physical_derivative=False,physical_admission=False,physical_guard=2e-10,
        native_or_local_accounting_reapplied=False,
        error_scope='finite original operator/source and birth-domain application; no continuum/angular/exterior or full-state bound')
    return out,report
