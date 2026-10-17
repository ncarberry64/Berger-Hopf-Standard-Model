"""Literal same-action Maxwell transport, with unsupplied flux terms explicit.

Only saved compatible368 point/clock and wall data are consumed. No source,
profile, field, history, canonical or exterior integration is performed.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys


def point_transport(point, point_rate, density, density_rate, factor):
    """Canonical/covariant radial energy flux and its off-shell improvement.

    A_tau time motion comes from the actual clock; its unused packed time
    slot is never interpreted as zero physical time motion.
    """
    import numpy as np
    from flint import acb
    c = acb(float(1/np.sqrt(2)))
    def comm(a,b):
        return [c*(a[1]*b[2]-a[2]*b[1]),c*(a[2]*b[0]-a[0]*b[2]),c*(a[0]*b[1]-a[1]*b[0]),acb(0)]
    def add(*args):return [sum((a[j] for a in args),acb(0)) for j in range(4)]
    def mul(k,a):return [k*v for v in a]
    def dot(a,b):return sum((u*v for u,v in zip(a,b)),acb(0))
    def field(p,start):return [[p[start+4*i+j] for j in range(4)] for i in range(5)]
    A,At,Ar = (field(point,20*i) for i in range(3))
    Ad,Atd,Ard = (field(point_rate,20*i) for i in range(3))
    e,r,d,k,beta=density;ed,rd,dd,kd,bd=density_rate
    X=add(At[1],mul(-1,Ar[0]),comm(A[0],A[1]))
    Xd=add(Atd[1],mul(-1,Ard[0]),comm(Ad[0],A[1]),comm(A[0],Ad[1]))
    T=[add(At[i+2],comm(A[0],A[i+2])) for i in range(3)]
    R=[add(Ar[i+2],comm(A[1],A[i+2])) for i in range(3)]
    Y=[add(T[i],mul(-beta,R[i])) for i in range(3)]
    B=[add(mul(2,A[i+2]),comm(A[j+2],A[l+2])) for i,j,l in ((0,1,2),(1,2,0),(2,0,1))]
    q=mul(factor*k,X);qt=mul(factor,add(mul(kd,X),mul(k,Xd)))
    pi=[mul(-1,q),[acb(0)]*4]+[mul(factor,add(mul(-e*beta,Y[i]),mul(-r,R[i]))) for i in range(3)]
    pt=[[acb(0)]*4,q]+[mul(factor*e,Y[i]) for i in range(3)]
    gAr=add(comm(q,A[0]),*(comm(A[i+2],pi[i+2]) for i in range(3)))
    EulerAr=add(gAr,mul(-1,qt))
    canonical=sum((dot(pi[i],Ad[i]) for i in range(5)),acb(0))
    covariant=sum((dot(pi[i+2],T[i]) for i in range(3)),acb(0))
    corner=dot(A[0],q)
    corner_t=dot(Ad[0],q)+dot(A[0],qt)
    kinematic=sum((dot(pi[i+2],add(At[i+2],mul(-1,Ad[i+2]))) for i in range(3)),acb(0))
    remainder=covariant-canonical-corner_t-dot(A[0],EulerAr)-kinematic
    L=factor*(k*dot(X,X)+e*sum((dot(v,v)for v in Y),acb(0))-r*sum((dot(v,v)for v in R),acb(0))-d*sum((dot(v,v)for v in B),acb(0)))/2
    Ecov=dot(q,X)+sum((dot(pt[i+2],T[i])for i in range(3)),acb(0))-L
    Ecan=sum((dot(pt[i],Ad[i])for i in range(5)),acb(0))-L
    return dict(q=q,q_time_first=qt,radial_momentum=[v for row in pi for v in row],temporal_momentum=[v for row in pt for v in row],
        Ar_Euler=EulerAr,Ar_action_gradient=gAr,canonical_energy_flux=canonical,covariant_energy_flux=covariant,
        canonical_energy_density=Ecan,covariant_energy_density=Ecov,scalar_density=L,
        corner_At_q=corner,corner_time_first=corner_t,At_Ar_Euler_work=dot(A[0],EulerAr),
        dynamic_kinematic_contact=kinematic,canonical_covariant_improvement_defect=remainder)


def run(repository, output):
    root,out=Path(repository).resolve(),Path(output).resolve();out.mkdir(parents=True,exist_ok=False)
    workspace=Path(__file__).resolve().parent
    sys.path[:0]=[str(root/'src'),str(root/'scripts'),str(workspace)]
    import numpy as np
    from flint import acb,acb_mat,ctx
    from bhsm_exact_action_balls import parse_acb_exact_dyadic,export_acb_exact_dyadic
    from bhsm.interface.muon_stored_admission_correction import _upper
    from bhsm.interface.muon_birth_phase_continuation import _compressed_npz
    from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
    ctx.prec=256;pins={}
    def read(path):
        pins[str(path)]=sha256(path.read_bytes()).hexdigest()
        if path.suffix=='.json':return json.loads(path.read_text(encoding='utf8'))
        with np.load(path,allow_pickle=False)as z:return{k:z[k].copy()for k in z.files}
    base=root/'artifacts/muon_baton_zoo_maximal_current_realization_20261013'
    clockdir=base/'actual_same_cut_native_MP_matrixfree_continuous_clock_run_1'
    cr=read(clockdir/'result.json')
    z=read(clockdir/'actual_continuous_phase210_clock_and_same_owner_point_density_rate.npz')
    wf=workspace/'outputs/bhsm_actual_wall_exterior_flux_20261014/run_3'
    wr=read(wf/'result.json');w=read(wf/'actual_same_cut_Maxwell_worldtube_conormal_and_R7_proper_contacts.npz')
    for p,h in wr['input_hashes'].items():
        path=Path(p)
        if sha256(path.read_bytes()).hexdigest()!=h:raise ValueError('Retained wall input hash changed: '+p)
    if z['coordinate_time'].item()!=w['coordinate_time'].item():raise ValueError('No nearby clock/face substitution')
    if not np.array_equal(z['master368'],w['actual_master368']):raise ValueError('No different primal state substitution')
    def ex(packet,key):return parse_acb_exact_dyadic(packet,key+'_exact')
    p,pt,d,dt=(ex(z,key)for key in('child_point_coefficients','child_point_coefficients_directional_first','child_metric_density','child_metric_density_directional_first'))
    factor=acb(float(MAXWELL_TO_CAP));values=[]
    for i in range(p.nrows()):values.append(point_transport([p[i,j]for j in range(60)],[pt[i,j]for j in range(60)],
        [d[i,j]for j in range(5)],[dt[i,j]for j in range(5)],factor))
    packet={};scalar_keys=('canonical_energy_flux','covariant_energy_flux','canonical_energy_density','covariant_energy_density',
        'scalar_density','corner_At_q','corner_time_first','At_Ar_Euler_work','dynamic_kinematic_contact','canonical_covariant_improvement_defect')
    for key in scalar_keys:packet.update(export_acb_exact_dyadic(acb_mat([[v[key]]for v in values]),key))
    for key in('q','q_time_first','radial_momentum','temporal_momentum','Ar_Euler'):
        packet.update(export_acb_exact_dyadic(acb_mat([v[key]for v in values]),key))
    wp,wa,wd=(ex(w,key)for key in('wall_radial_Maxwell_conormal_density20','wall_total_connection20','wall_time_derivative_dynamic16'))
    wc=ex(z,'child_wall_connection_directional_first')
    wall_canonical=sum((wp[i,0]*wc[0,i]for i in range(20)),acb(0))
    wall_cov=ex(w,'wall_covariant_Maxwell_energy_flux_density')[0,0]
    wall_qY=-wp[3,0]
    for key,val in dict(wall_canonical_energy_flux=wall_canonical,wall_covariant_energy_flux=wall_cov,wall_central_Y_flux=wall_qY,
                       wall_canonical_covariant_difference=wall_cov-wall_canonical).items():packet.update(export_acb_exact_dyadic(acb_mat([[val]]),key))
    packet.update(coordinate_time=z['coordinate_time'],master368=z['master368'])
    archive=out/'actual_same_cut_literal_charge_energy_boundary_transport.npz';_compressed_npz(archive,packet)
    def pair(v):return[float(v.real.mid()),float(v.imag.mid())]
    defect=_upper(acb_mat([[v['canonical_covariant_improvement_defect']]for v in values]))
    kin=_upper(acb_mat([[pt[i,j]-p[i,20+j]for j in range(4,20)]for i in range(48)]))
    result=dict(classification='EVALUATED_SAME_ACTION_MATERIAL_CHARGE_AND_CANONICAL_COVARIANT_BOUNDARY_ENERGY_LEDGER_WITH_MISSING_PHYSICAL_SOURCES_EXPLICIT',
        input_sha256=pins,coordinate_time=pair(acb(complex(z['coordinate_time'].item()))),
        finite_compatible_clock_status=cr['status'],pointwise_dynamic_kinematic_bound=kin,
        pointwise_Atau_time_first_upper=_upper(acb_mat([[pt[i,j]for j in range(4)]for i in range(48)])),
        pointwise_canonical_covariant_energy_improvement_identity_upper=defect,
        wall_canonical_energy_flux=pair(wall_canonical),wall_covariant_Maxwell_energy_flux=pair(wall_cov),
        wall_central_Y_charge_flux=pair(wall_qY),wall_covariant_minus_canonical_flux=pair(wall_cov-wall_canonical),
        equations=dict(radial_charge='q_c=MAXWELL_TO_CAP*k*F_tau_r^c; pi_r^At=-q_c. q_Y is the unitTr16 HY channel, not automatically EMQ.',
            energy_improvement='S_cov-S_can=D_tau(A_tau dot q)+A_tau dot E_Ar+kinematic_contact. E_Ar is retained, not set0.',
            sourced_Gauss='partial_rho q_Y+j_Y_lepton+j_Y_Higgs+angular_divergence+interface_and_other_actual_loads=0.',
            incoming_weak_load='J_test=sum_nodes quadrature*test_tau^c*j_material_pair^c(U,V); use existing original_material_Gauss_source on actual normalized full18 sections and a common action spatial-density normalization.',
            moving_boundary='In a moving coordinate section, outward energy flux is S_r-b_dot*E_tau. Here the same-action material-rho face is fixed; its shift and proper conormal conversion already carry the wall motion. Do not add wall advection twice.',
            full_energy='Full cap/gravity + [Maxwell total minus owned mechanical reference] + Higgs + lepton/HS/other sectors + source/reference work + interfaces/exterior. Do not add the mechanical Maxwell reference twice.'),
        missing_physical_terms=dict(pair_local_material_source=None,pair_actual_full18_packet_sections=None,
            core_and_exterior_charge_flux=None,angular_source_loads=None,physical_outgoing_radiation=None,
            full_gravity_Higgs_lepton_event_energy_tractions=None,actual_common_collider_trace_and_event_pullback=None,
            wall_corner_time_first_and_wall_Ar_Euler_work=None),
        known_pair_total_EM_charge_zero_does_not_set_local_HY_source_or_each_face_flux_zero=True,
        AE4_binding='canonical_noether_flux_balance requires one actual common trace, anti-Hermitian generator and all same-action sector tractions; the old complex transpose finite3-port Green balance is not this full physical Noether value.',
        retained_complex_germ_not_new_real_collider_background=True,
        no_profile_source_history_D5_canonical_or_pairing_integrations_restarted=True,
        full_physical_conservation_or_muon_magnetic_moment_or_matching_correction_admitted=False,
        archive=dict(path=archive.name,sha256=sha256(archive.read_bytes()).hexdigest()),producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    (out/'executed_producer.py').write_bytes(Path(__file__).read_bytes())
    data=json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n';(out/'result.json').write_text(data,encoding='utf8',newline='\n')
    print(json.dumps(dict(result=str(out/'result.json'),sha256=sha256(data.encode()).hexdigest(),energy_identity_upper=defect)))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--repository',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.repository,a.output)
