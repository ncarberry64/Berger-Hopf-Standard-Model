"""New original-two-boundary equations on archived full-spin wall germs.

Reads already computed trace/normal/geometry operands. No D5 action,
history, normal-profile integration, quadrature campaign or state solve is
rerun. The two source axes are the recorded time germ and a declared
partial ReH2 insertion, not the physical outgoing E/B derivative.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys

import numpy as np
from scipy.linalg import lu_factor, lu_solve

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_two_collar_weak_domain import two_collar_weak_domain_jets
from bhsm.interface.muon_full_d5_localized_lepton_trace import (
    full_d5_localized_lepton_trace, moving_d5_material_trace_frame,
)
from bhsm.interface.muon_continued_action_reality import _higgs_mass_realified
from bhsm.interface.muon_holomorphic_normal_geometry import _geometry_variables,_fields,_sqrt


KEYS = ('value','x','y','xy')


def jet(a,x=None,y=None,xy=None):
    a=np.asarray(a,complex)
    return {k:np.zeros_like(a) if v is None else np.asarray(v,complex)
            for k,v in zip(KEYS,(a,x,y,xy))}


def mul(a,b):
    # Independent ordered product for the ORIGINAL two-boundary pencil.
    return dict(value=a['value']@b['value'],
        x=a['x']@b['value']+a['value']@b['x'],
        y=a['y']@b['value']+a['value']@b['y'],
        xy=a['xy']@b['value']+a['x']@b['y']+a['y']@b['x']+a['value']@b['xy'])


def literal_solve(a,b):
    lu=lu_factor(a['value'])
    r=dict(value=lu_solve(lu,b['value']))
    r['x']=lu_solve(lu,b['x']-a['x']@r['value'])
    r['y']=lu_solve(lu,b['y']-a['y']@r['value'])
    r['xy']=lu_solve(lu,b['xy']-a['xy']@r['value']-a['x']@r['y']-a['y']@r['x'])
    return r


def evaluate(output):
    out=Path(output).resolve()
    if out.exists():raise FileExistsError(out)
    pins={}
    def pin(path,expected=None):
        path=Path(path);h=sha256(path.read_bytes()).hexdigest()
        if expected is not None and h!=expected:raise ValueError('Frozen input changed: '+str(path))
        pins[path.relative_to(ROOT).as_posix()]=h
    old=ROOT/'artifacts/muon_trial_d5_trace_action_20261012/trial_0000_corrected_sigma_energy_0_run_2'
    old_report=json.loads((old/'result.json').read_bytes());pin(old/'result.json')
    rep=full_d5_localized_lepton_trace();g=rep['gamma5D_self_dual128']
    lift=lambda m:np.kron(np.eye(3),m)
    g0=lift(g[0]);pl=np.diag(np.r_[np.ones(12),np.zeros(6)]);pr=np.eye(18)-pl
    records=[]
    for stage in range(2):
        path=old/f'stage_{stage:04d}_current_geometry_normal_and_material_trace.npz'
        pin(path,old_report['archives'][path.name]['sha256'])
        with np.load(path,allow_pickle=False)as z:a={k:z[k]for k in z.files}
        raw_path=ROOT/old_report['trial']/f'stage_{stage:04d}.npz'
        pin(raw_path,old_report['input_hashes'][raw_path.relative_to(ROOT).as_posix()])
        with np.load(raw_path,allow_pickle=False)as z:raw=z['stage_raw']
        q,v,m,_,wall_rate,wall,_=_geometry_variables(raw[:100])
        fields=_fields(12,q,v,m,wall)
        radius=fields['A']*fields['B']/_sqrt(fields['A']**2+fields['B']**2)
        velocity=fields['C']*(wall_rate+fields['beta'])/fields['N']
        clock=fields['N']*_sqrt(1-velocity**2)
        time=a['canonical_raw_coordinate_time_direction'][:100]
        vel,dvel=velocity.value,velocity.gradient@time
        plus=moving_d5_material_trace_frame(-vel,-dvel,full_representation=rep)
        minus=moving_d5_material_trace_frame(vel,dvel,full_representation=rep)
        sp,spi=plus['spin_boost128'],plus['spin_boost_inverse128']
        sm,smi=minus['spin_boost128'],minus['spin_boost_inverse128']
        dsp,dspi=plus['spin_boost_first128'],plus['spin_boost_inverse_first128']
        dsm,dsmi=minus['spin_boost_first128'],minus['spin_boost_inverse_first128']
        u,ui=lift(sm@spi),lift(sp@smi)
        du,dui=lift(dsm@spi+sm@dspi),lift(dsp@smi+sp@dsmi)
        rho=a['actual_intrinsic_surface_density'].item()
        drho=(clock.gradient@time)*radius.value**3+3*clock.value*radius.value**2*(radius.gradient@time)
        gn=[a[f'eta_{side}_original_principal_normal_Clifford128']for side in('plus','minus')]
        dgn=[dvel*(vel*g[4]-g[0])/(np.sqrt(1-vel*vel)**3),
             -dvel*(vel*g[4]+g[0])/(np.sqrt(1-vel*vel)**3)]
        greens=[jet(1j*rho*g0@lift(n),1j*g0@lift(drho*n+rho*dn))for n,dn in zip(gn,dgn)]
        trace=[jet(a[f'eta_{side}_normalized_right_Gamma0'],
                   a[f'eta_{side}_normalized_right_Gamma0_first'][0])for side in('plus','minus')]
        source=[jet(g0@a[f'eta_{side}_normalized_Dirac_bar_left_Gamma0'],
                    g0@a[f'eta_{side}_normalized_Dirac_bar_left_Gamma0_first'][0])for side in('plus','minus')]
        m0=a['fixedY_Higgs_intrinsic_seam_matrix']
        mx=_higgs_mass_realified(a['intrinsic_H_realified_first'][0]);my=_higgs_mass_realified([0,1,0,0])
        kernel=jet(rho*m0,drho*m0+rho*mx,rho*my,drho*my)
        uj,uij,usj=jet(u,du),jet(ui,dui),jet(g0@ui@g0,g0@dui@g0)
        result=two_collar_weak_domain_jets(plus_green=greens[0],minus_green=greens[1],
            geometric_right=uj,geometric_right_inverse=uij,geometric_left_dual=usj,
            plus_normalized_trace=trace[0],minus_normalized_trace=trace[1],
            plus_canonical_source=source[0],minus_canonical_source=source[1],
            surface_kernel=kernel,left_chiral_projector=pl)
        cs=result['common_frame_canonical_source'];ct=mul(cs,kernel)
        bl={k:pl@trace[0][k]for k in KEYS};br={k:pr@trace[1][k]for k in KEYS}
        ju=mul(greens[0],uij);ctr=mul(ct,br);ctl=mul(ct,bl)
        lhs={k:ju[k]-ctr[k]for k in KEYS}
        rhs={k:greens[0][k]+ctl[k]for k in KEYS}
        literal=literal_solve(lhs,rhs)
        residual_names=('original_weak_surface_rows','original_split_trace_rows',
            'original_two_trace_domain_graph_rows','original_two_trace_green_rows',
            'geometric_green_alignment_rows','geometric_inverse_rows',
            'geometric_reverse_inverse_rows','plus_selected_trace_jump_rows',
            'minus_selected_trace_jump_rows','isotropy_rows','nilpotence_rows',
            'Higgs_left_left_rows','Higgs_right_right_rows')
        records.append(dict(stage=stage,full_spin_SM_family_fiber=384,
            original_two_boundary_traces=768,additional_trace_copies=0,
            independent_literal_two_boundary_comparison={k:float(np.max(abs(literal[k]-result['right_minus_from_plus'][k])))for k in KEYS},
            original_equation_rows={name:{k:float(np.max(abs(result[name][k])))for k in KEYS}for name in residual_names},
            nonzero_free_hard_graph_surface_defect_norm=float(np.linalg.norm(result['original_free_graph_surface_defect']['value'])),
            interacting_transfer_minus_geometric_norm=float(np.linalg.norm(result['right_minus_from_plus']['value']-u)),
            mixed_two_boundary_map_norm=float(np.linalg.norm(result['right_minus_from_plus']['xy'])),
            original_particle_Green_match=float(np.max(abs(greens[0]['value'][:64,:64]-a['original_Dirac_bar_Green_matrix']))),
            original_particle_Green_time_match=float(np.max(abs(greens[0]['x'][:64,:64]-a['original_Dirac_bar_Green_matrix_first'][0]))),
            input_is_saved_complex_off_shell_germ=True,
            x_axis='recorded canonical time germ with inherited wall contacts',
            y_axis='partial ReH2 with geometry and normalized trace held fixed',
            supplied_partial_zero_contacts_are_not_physical_E_B_domain_zeros=True))
    for rel in ('audits/bhsm_original_two_collar_domain_application_20261016.py',
        'src/bhsm/interface/muon_two_collar_weak_domain.py',
        'src/bhsm/interface/muon_isotropic_seam_transfer.py',
        'src/bhsm/interface/muon_full_d5_localized_lepton_trace.py',
        'src/bhsm/interface/muon_continued_action_reality.py',
        'src/bhsm/interface/muon_holomorphic_normal_geometry.py',
        'src/bhsm/interface/muon_local_source_jet.py',
        'src/bhsm/interface/particle_chirality_anomaly_normalization.py',
        'src/bhsm/interface/bhsm_standard_model_gauge_vertices.py',
        'src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py'):
        pin(ROOT/rel)
    payload=dict(classification='ORIGINAL_TWO_COLLAR_WEAK_DOMAIN_ON_ARCHIVED_FULL384_GERMS',
        records=records,input_and_source_sha256=dict(sorted(pins.items())),
        new_D5_profile_history_or_quadrature_integrations=0,
        earlier_isotropic_Cayley_campaign_rerun=False,
        local_original_two_trace_domain_equations_evaluated=True,
        complete_common_native_graded_domain_realized=False,
        physical_radial_convergence_established=False,
        physical_outgoing_energy_magnetic_domain_derivatives_evaluated=False,
        full_physical_derivative_passed_at_2e_minus_10=False,
        original_coupled_corrections_applied=0,
        Maxwell_all226_after_correction_validated=False,
        physical_two_spin_normalization=None,physical_muon_magnetic_moment=None)
    out.mkdir(parents=True)
    path=out/'result.json';path.write_text(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256(path.read_bytes()).hexdigest(),records=records)))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True)
    evaluate(parser.parse_args().output)
