"""Finite complex collar-current contributions at saved split poles.

Only frozen K0+E KE matrices, normal inclusions, radial maps and quadrature
are consumed.  No coefficient, profile, history, or pole is recomputed.
The unchanged complex current measure is never replaced by real/absolute
weights.  This finite collar diagnostic is not a physical full-state norm.
"""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import os
import sys
os.environ["OPENBLAS_NUM_THREADS"] = "2"
os.environ["OMP_NUM_THREADS"] = "2"
sys.dont_write_bytecode = True
import numpy as np

WORK = Path(r"C:/Users/carbe/OneDrive/Documents/CODEX")
REPO = Path(r"C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001")
SOURCE = WORK/"outputs/bhsm_finite_pole_point_spin_diagnostic_20261015/run_1"
BASE = WORK/"outputs/bhsm_finite_pole_collar_current_20261015"
OLD = "artifacts/muon_d5_finite_trace_pole_match_20261012/trial_0000_stage_pair_run_3"
sys.path.insert(0,str(REPO/"src"))
from bhsm.interface.muon_holomorphic_d5_trace_action import normalized_two_sheet_point_action
from bhsm.interface.muon_full_d5_localized_lepton_trace import full_d5_localized_lepton_trace


def clean(x):
    if isinstance(x,dict):return {k:clean(v)for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v)for v in x]
    if isinstance(x,np.ndarray):return clean(x.tolist())
    if isinstance(x,(complex,np.complexfloating)):return [float(x.real),float(x.imag)]
    if isinstance(x,np.generic):return x.item()
    return x


def upper(x):return float(np.max(np.abs(x)))


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--run",type=int,required=True)
    args=p.parse_args();out=BASE/f"run_{args.run}";out.mkdir(parents=True,exist_ok=False)
    pins={};archives={}
    def read(p,expected=None):
        p=Path(p);b=p.read_bytes();h=sha256(b).hexdigest()
        if expected is not None and h!=expected:raise ValueError("Frozen input changed: "+str(p))
        pins[str(p)]=h
        if p.suffix=='.npz':
            with np.load(p,allow_pickle=False)as a:return {k:a[k].copy()for k in a.files}
        return json.loads(b)if p.suffix=='.json'else b.decode('utf-8-sig')
    read(REPO/'AGENTS.md')
    for name in ['muon_holomorphic_d5_trace_action','muon_full_d5_localized_lepton_trace','muon_coupled_phase_trace_projection']:
        read(REPO/f'src/bhsm/interface/{name}.py')
    read(REPO/'scripts/evaluate_muon_trial_d5_trace_action.py')
    sm=read(SOURCE/'result.json');old=read(REPO/OLD/'result.json');source=old['source']
    md=read(REPO/source/'result.json')
    basis_rel='artifacts/muon_parent_gauge_geometry_correction_20261010/finite_moving_trace_run_1/application.npz'
    base=read(REPO/basis_rel,md['input_hashes'][basis_rel])
    rho,w,B=base['rho'],base['radial_quadrature'],base['radial_value_map']
    full=full_d5_localized_lepton_trace();G0=full['gamma5D_self_dual128'][0]
    ids=np.array([2,3,8,9,14,15]);amb=np.arange(128,256)
    records=[]
    for stage in range(2):
        cn=f'stage_{stage:04d}_current_geometry_normal_and_material_trace.npz'
        c=read(REPO/source/cn,md['archives'][cn]['sha256'])
        assert np.array_equal(rho,c['radial_points']) and np.all(w>0)
        u=c['original_normal_inclusion'];V=u[:,None]*B
        density=c['Cauchy_density'];ell_clock=c['surface_proper_clock_rate'][0]
        assert upper(c['surface_proper_clock_rate']-ell_clock)<1e-14
        kernel=(V.T*(w*density))@V
        expectedKE=ell_clock*np.kron(kernel,np.eye(64))
        blocks={};kernel_controls={}
        for eps in (1,-1):
            for branch in ('particle','conjugate'):
                fn=f'stage_{stage:04d}_eta_{eps:+d}_{branch}_original_radial_field_action.npz'
                a=read(REPO/source/fn,md['archives'][fn]['sha256'])
                blocks[eps,branch]=(a['original_unsquared_radial_action'],a['original_unsquared_radial_action_energy'])
                kernel_controls[f'eta{eps:+d}_{branch}']=upper(blocks[eps,branch][1]-expectedKE)
        M=c['fixedY_Higgs_intrinsic_seam_matrix'][np.ix_(ids,ids)]
        tr=[]
        for label in ('plus','minus'):
            t={}
            for k in ('normalized_right_Gamma0','normal_mode_Dirac_bar_left_point_lift'):
                t[k]=c[f'eta_{label}_'+k][np.ix_(ids,amb)]
            for k in ('normalized_Dirac_bar_left_Gamma0','normal_mode_right_point_lift'):
                t[k]=c[f'eta_{label}_'+k][np.ix_(amb,ids)]
            tr.append(t)
        uw=c['actual_normalized_Gamma0_multiplier'].item()
        rights=[];lefts=[];root_controls=[]
        for spin_branch in range(2):
            fn=f'stage_{stage:04d}_branch_{spin_branch}_unit_point_coefficient_spin.npz'
            pole=read(SOURCE/fn,sm['archives'][fn])
            E=pole['energy'].item();r=pole['unit_point_right6'][:,0];l=pole['reciprocally_rescaled_literal_left6'][0]
            sheets=[];sheetsE=[];poisson={};left_poisson={};original_rows=0.
            for eps in (1,-1):
                ss=[];dd=[]
                for branch in ('particle','conjugate'):
                    K0,KE=blocks[eps,branch];K=K0+E*KE
                    A,Cross,C,D=K[:192,:192],K[:192,192:],K[192:,:192],K[192:,192:]
                    X=np.linalg.solve(A,Cross)
                    XE=np.linalg.solve(A,KE[:192,192:]-KE[:192,:192]@X)
                    ss.append(D-C@X);dd.append(KE[192:,192:]-KE[192:,:192]@X-C@XE)
                    poisson[eps,branch]=np.r_[-X,np.eye(64)]
                    left_poisson[eps,branch]=np.c_[-np.linalg.solve(A.T,C.T).T,np.eye(64)]
                    original_rows=max(original_rows,upper(A@X-Cross))
                z=np.zeros((64,64),complex)
                sheets.append(np.block([[ss[0],z],[z,ss[1]]])/(uw*uw))
                sheetsE.append(np.block([[dd[0],z],[z,dd[1]]])/(uw*uw))
            a=normalized_two_sheet_point_action(np.array(sheets),np.array(sheetsE),tr,M,
                c['actual_intrinsic_surface_density'].item(),G0,left_trace_count=4)
            action=a['eta_two_sheet_Dirac_bar_action'];BT=a['normalized_two_sheet_right_trace'];CT=a['normalized_two_sheet_Dirac_bar_left_trace']
            border=np.block([[action,CT],[BT,np.zeros((6,6),complex)]])
            rhs=np.r_[np.zeros((256,6),complex),np.eye(6)]
            transpose_solution=np.linalg.solve(border.T,rhs)
            yR=a['full_complementary_field_Poisson']@r
            yL=l@transpose_solution[:256].T
            fieldsR=[];fieldsL=[];coefsR=[];coefsL=[]
            kinetic=0j;action_energy=0j
            for sheet_index,eps in enumerate((1,-1)):
                # Point action is Gamma0*S/uw^2. Undo its precise canonical
                # Dirac-bar and point-amplitude conversion on the left once.
                bR=yR[sheet_index*128:(sheet_index+1)*128]/uw
                bL=yL[sheet_index*128:(sheet_index+1)*128]@G0/uw
                for copy_index,branch in enumerate(('particle','conjugate')):
                    sl=slice(copy_index*64,(copy_index+1)*64)
                    v=poisson[eps,branch]@bR[sl]
                    z=bL[sl]@left_poisson[eps,branch]
                    fieldsR.append(V@v.reshape(4,64));fieldsL.append(V@z.reshape(4,64))
                    coefsR.append(v);coefsL.append(z)
                    action_energy+=z@blocks[eps,branch][1]@v
            fieldsR=np.array(fieldsR);fieldsL=np.array(fieldsL)
            kinetic=np.einsum('q,cqi,cqi->',w*density,fieldsL,fieldsR)
            rights.append(fieldsR);lefts.append(fieldsL)
            G,GE=a['finite_normalized_field_Gamma'],a['finite_normalized_field_Gamma_energy']
            root_controls.append({
                'branch':spin_branch,'energy':E,
                'Gamma_reproduction_max':upper(G-pole['gamma6']),
                'Gamma_energy_reproduction_max':upper(GE-pole['gamma_energy6']),
                'radial_original_interior_rows_max':original_rows,
                'two_sheet_original_rows_max':upper(a['original_full_field_and_trace_rows']),
                'left_two_sheet_original_rows_max':upper(border.T@transpose_solution-rhs),
                'pole_energy_pairing':l@GE@r,
                'reconstructed_action_energy_pairing':action_energy,
                'radial_current_times_clock':ell_clock*kinetic,
                'action_current_identity_max':float(abs(action_energy-ell_clock*kinetic)),
                'pole_action_identity_max':float(abs(action_energy-l@GE@r)),
                'finite_analytic_current_diagonal':kinetic,
            })
        R,L=np.array(rights),np.array(lefts)
        # All4 contributions are the original block direct sum: eta+/- and
        # SM16/conjugate representation. No extra species/loop multiplier.
        current_by_copy=np.einsum('q,scqi,tcqi->cst',w*density,R.conj(),R)
        analytic_by_copy=np.einsum('q,scqi,tcqi->cst',w*density,L,R)
        current=current_by_copy.sum(axis=0);analytic=analytic_by_copy.sum(axis=0)
        anti=current-current.conj().T
        fn=f'stage_{stage:04d}_finite_complex_collar_current_contributions.npz'
        np.savez_compressed(out/fn,radial_points=rho,radial_weights=w,radial_value_map=B,
            original_normal_inclusion=u,Cauchy_density=density,proper_surface_clock=np.array(ell_clock),
            right_field_at_saved_poles=R,independent_analytic_left_field_at_saved_poles=L,
            point_coefficient_collar_current_Gram=current,
            point_coefficient_current_per_original_copy=current_by_copy,
            analytic_left_right_current_Gram=analytic,analytic_current_per_original_copy=analytic_by_copy,
            current_anti_Hermitian_part=anti,analytic_radial_kernel=kernel)
        archives[fn]=sha256((out/fn).read_bytes()).hexdigest()
        records.append({'stage':stage,'roots':root_controls,'KE_current_kernel_controls':kernel_controls,
            'finite_collar_current_Gram':current,'finite_collar_current_per_original_copy':current_by_copy,
            'analytic_left_right_current_Gram':analytic,'current_anti_Hermitian_max':upper(anti),
            'current_diagonal_imaginary':np.diag(current).imag,
            'Cauchy_density_imaginary_max':upper(density.imag),
            'same_saved_radial_sigma_mode_residual_norm':float(np.linalg.norm(c['radial_trial_sigma_normal_mode_rows'])),
            'positive_current_admitted':False})
        if max(kernel_controls.values())>2e-10:raise ArithmeticError('Original KE current ownership failed')
        if max(v['action_current_identity_max']for v in root_controls)>2e-10:raise ArithmeticError('Recovered radial current failed original energy identity')
    for path,h in pins.items():assert sha256(Path(path).read_bytes()).hexdigest()==h,path
    result={'classification':'EVALUATED_FINITE_COMPLEX_COLLAR_AND_N0_ANGULAR_CURRENT_AT_SAVED_SPLIT_POLES',
        'records':records,'archives':archives,'input_hashes':pins,
        'current_definition':'M_st=sum_original_eta_and_SM_conjugate_blocks integral w C_rho R^3 (Psi_s)^dagger Psi_t on fixed material constant-time slice; n0 angular Haar norm1 inherited from original single harmonic action. Complex density retained.',
        'independent_analytic_current':'J_st=sum integral w C_rho R^3 left_s Psi_t; clock*J_ss equals l_s Gamma_E r_s under original KE ownership. This is not a positive state norm.',
        'copy_order':['eta+ particle','eta+ conjugate representation','eta- particle','eta- conjugate representation'],
        'copy_weights':[1,1,1,1],
        'joining_owner':'Original two-sheet block-diagonal action and per-family self-dual representation, each active block once; no independent conjugate species or loop degeneracy added. Exact energy-current contraction verifies joining.',
        'finite_sum_scope':'Only four radial trial functions and the owned n0 angular harmonic on the saved complex material slice. No normal-flow, radial/angular continuum or exterior remainder is discarded.',
        'physical_positive_norm':None,'finite_quadrature_or_continuum_error_bound':None,
        'exterior_current_contribution':None,'exterior_current_error_bound':None,
        'precise_missing_physical_operand':'Real/independently reflected same-domain physical Cauchy-current pairing and sigma-normal-flow density/inclusion onto the actual formed-state slice, plus the action-selected retarded exterior mode/current return. The current complex germ cannot supply these by replacing its density with real or absolute values.',
        'interpretation':'Non-real/non-Hermitian finite collar current diagnoses the declared complex off-shell germ. It does not prove absence of a physical full-BHSM state, and is not normalized to hide its imaginary part.',
        'no_profile_action_root_or_history_rebuild':True,'physical_corrections_applied':0,
        'physical_magnetic_moment':None,'whole_physical_derivative_admitted':False,
        'repeat_scope':'New finite matrix and current applications repeated twice on identical frozen coefficients; original completed D5/source/history campaigns not rerun.',
        'producer_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
    rp=out/'result.json';rp.write_text(json.dumps(clean(result),sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'out':str(out),'result_sha256':sha256(rp.read_bytes()).hexdigest(),'stages':2}))


if __name__=='__main__':main()
