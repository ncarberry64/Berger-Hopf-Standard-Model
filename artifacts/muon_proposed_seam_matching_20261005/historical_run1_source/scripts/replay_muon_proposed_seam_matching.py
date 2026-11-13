"""New full-cap direct action matching; no old parent calculation replay."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np


def load(p):
    with np.load(p,allow_pickle=False) as z:return {k:np.array(z[k]) for k in z.files}


def save(p,d):p.write_bytes((json.dumps(d,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def references(root):
    a=root/'artifacts'
    return dict(point=a/'muon_retained_tail_core_20261005/run_1/points/node_03.npz',
        point_receipt=a/'muon_retained_tail_core_20261005/run_1/points/node_03.json',
        wall=a/'muon_wall_input_attachment_20261005/run_1/node3_projected_intrinsic_kinetic.npz',
        cut=a/'muon_coupled_cut_forms_20261004/run_1/coupled_cut_source_actions.npz',
        geometry=a/'muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz',
        radial=a/'muon_radial_inclusion_action_20261004/replay_reference/radial_source_action_and_interface.npz',
        contact=a/'muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz',
        proposed=a/'muon_proposed_dynamic_seam_20261005/run_2/proposed_seam_actions.npz',
        intrinsic=a/'action_extension/BHSM_AE31_C2_INTRINSIC_M4_LEPTON_ACTION.json',
        norm_producer=root/'src/bhsm/interface/muon_wall_input_attachment.py',
        point_producer=root/'src/bhsm/interface/muon_prefix_time_element.py',
        metric_producer=root/'src/bhsm/interface/muon_parent_maxwell_velocity.py',
        premode_action=root/'src/bhsm/interface/completion/foundational_dirac_spin_glue_v14_45.py',
        boundary_pushforward=root/'src/bhsm/interface/aether_unified_m5_m4_pushforward_v15_69.py',
        owner=root/'src/bhsm/interface/ae4_stratified_dirac_zeta_induced_owner.py',
        proposed_producer=root/'src/bhsm/interface/muon_proposed_dynamic_seam.py',
        module=root/'src/bhsm/interface/muon_proposed_seam_matching.py',
        report=root/'theory/muon_proposed_seam_matching_20261005.md',
        tests=root/'tests/test_muon_proposed_seam_matching.py',script=Path(__file__).resolve())


def calculate(root):
    sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_proposed_seam_matching import (
        coefficients,actual_maps,cached_action_comparison,enclosure)
    refs=references(root)
    d={k:load(refs[k]) for k in ('point','wall','cut','geometry','radial','contact','proposed')}
    receipt=json.loads(refs['point_receipt'].read_text())
    intrinsic=json.loads(refs['intrinsic'].read_text())
    Y=np.array(intrinsic['charged_lepton_yukawa_operator']['family_operator'])
    c,fields,guards=coefficients(d['point'],d['wall'],d['cut'],receipt['attachment'],d['geometry']['rho'])
    maps,identity=actual_maps(c,d['wall'],d['radial'],d['contact'],d['proposed'],Y)
    comparison=cached_action_comparison(c,d['wall'],d['point'],d['radial'],d['cut'])
    vals={k:enclosure(v) for k,v in c.items()}
    return refs,c,fields,maps,guards,identity,comparison,vals,intrinsic


def run(root,out):
    if out.exists():raise FileExistsError('new dedicated directory required')
    refs,c,fields,maps,guards,identity,comparison,vals,intrinsic=calculate(root)
    out.mkdir(parents=True)
    np.savez_compressed(out/'localized_matching_maps.npz',**fields,**maps)
    save(out/'coefficients.json',vals)
    ledger=dict(parent='existing geometric/common-A/radial-eta S5 symmetric kinetic action; NO independent second Yukawa bridge',
        intrinsic='existing S4 kinetic and SAME v14.45/AE31 Y_l H bridge, owned once; Z_H=1 for this direct proposal',
        seam='explicit proposed normal bilinear; zero on smooth Rw=(Ww,w), G1 Rw=0; no alteration or installation',
        restriction='direct pullback along R; not stationary complement elimination or effective boundary action',
        complement='retained connected outputs; no complement determinant/Schur response claimed or dropped from native operator',
        field_norm='M4+Wdag M5 W in volume; M4+Wdag M_Cauchy W on temporal slice, not interchangeable',
        chiral='one correctly typed bulk orientation per physical chirality; e_R is charge conjugate of e_c; no Nambu or sheet trace duplication',
        Jacobian='formal Grassmann logJ=Tr_physical(logZ) for the scalar C=Z^-1/2 with bar dual transformed; no regulated infinite trace evaluated',
        suggested_compensation='none selected; Delta S_c=S_R,canonical-S_retained is evaluated; its negative would be an extra proposed action, not a derived subtraction')
    save(out/'contribution_ledger.json',ledger)
    equations=dict(
        direct='S_R=S5_sym[Ww]+S4[w]+S_seam[Ww,w]; S_seam=0 on smooth matched trace',
        norm='Nvol=1+<1>_P; NCauchy=Zt=1+<1/nu>_P',
        Z='Z_L=Z_R=Zt; Z_H=1; NOT an independently verified full e_R/global domain',
        P='radial probability dP=(w_rho mu5 u^2/M4), all64 cells',
        kinetic='Zs=1/Rb+<1/r>_P; Zg=b_g,wall+<b_g>_P',
        canonical='w=C w_c, barw=barw_c Cdag, C=Zt^-1/2; C_tau=-Z_tau C/(2Z)',
        time_symmetric='i/2 mu4 Z (wdag d_tau w-d_tau wdag w); canonical Euler i d_tau+3iH/2',
        raw_comparison='beta_raw=<a0>+3H/2; compare with (Z_tau+3HZ)/2; never a mass',
        Yukawa='Y_c=Z_L^-1/2 Y_owned Z_R^-1/2; H kinetic unchanged; no Y refit',
        source='V_b,raw=T_b Zs V_unit; V_b,c=V_b,raw/Z; V_b,target=(T_b/Rb)V_unit',
        source_derivative='D_b(Csharp A_R C)=C_b^sharp A_R C+Csharp (A_R)_b C+Csharp A_R C_b; operators act on C and its spacetime derivatives',
        full_total_jets='retain source/frame/trace/normal/pairing/domain derivatives; Z_b total is unevaluated, direct fixed-history partial Z_b=0 by declared geometry independence',
        compact_source='F_L(W Bp)+F_L(p-W Bp)=F_L p=0; canonical rescaling preserves the full sum',
        residual='Delta Zs=Zs/Z-1/Rb; Delta Zg=Zg/Z-b_g,wall; Delta(YH)=(1/Z-1)YH; photon residual shares Delta Zs, not an extra addend',
        elimination='A_eff=A_RR-A_RQ solve(A_QQ,A_QR), with same domain/field/source/subtraction; not evaluated by this restriction')
    save(out/'equations.json',equations)
    result=dict(classification='PROPOSED_SEAM_DIRECT_LOCALIZED_MATCHING_RESIDUAL_NOT_NATIVE',
        continuation='00dac33bd0d42434315b4b46e76e70b2d47f1c74',
        action_history='current C2 node3/action_arc6, branch24, saved proper clock',
        domain_scope='smooth matched material traces under proposed law; inherited reset/past-prefix/canonical-stop unchanged; global realization not completed',
        commonA_resolved=True,eta_profile_unchanged=True,old_J_arrays_reused=True,
        old_production_checks_repeated=0,new_parent_or_tail_solves=0,new_field_actions=0,
        ZL_and_ZR='equal radial scalar principal residues conditional on proposed common inclusion; e_R global mapping not completed',
        Yukawa_ownership=intrinsic['charged_lepton_yukawa_operator'],
        instantaneous_metric_reconstruction_only=True,guards=guards,diagnostic_field_identity=identity,
        cached_parent_action_checks=comparison,
        same_photon='eight saved b-source lifts, same T_b/r extension, no index2/3 or contact-fraction multiplier',
        photon_total_jet_evaluated=False,subtraction_installed=False,proposal_adopted=False,native_operator_updated=False,
        direct_matching_established=False,
        residual='canonical angular/photon ratio differs from1 and once-owned Yukawa factor differs from1; field norm or scalar field rescaling cannot establish equality',
        error_scope=dict(arithmetic='192-bit Arb enclosures of stated frozen binary and saved nodal-model scalar inputs; reconstructed metric scalars frozen after binary64 evaluation',
            spatial_quadrature='same full-cap512-point/8-per-cell Gauss model; NO new quadrature or continuum bound',
            history='cached node3 numerical state/clock; no endpoint tube or certified continuum enclosure promoted',
            canonical_map_arrays='binary64 representatives of enclosed coefficients; not certified operator norm bounds',
            field_measure='formal regulated functional trace remains unevaluated; no new counterterm chosen'),
        native_ledger={k:None for k in ('native_bulk_heat','state_variation','contact','domain_boundary','completion_counterterm','strong_within_native')},
        parent_solution_unchanged=True,frozen_locals_unchanged=True,
        physical_a_mu=None,physical_g_mu=None,native_uncertainty=None,
        next='action-owned replacement/compensation or evaluated same-owner complementary response that cancels the joint kinetic AND interaction residual; none supplied by normalization or the average-trace law')
    save(out/'result.json',result)
    save(out/'input_hashes.json',{k:dict(path=str(p),sha256=sha(p)) for k,p in refs.items()})
    git=lambda *a:subprocess.check_output(['git','-C',str(root),*a],text=True).strip()
    save(out/'workspace.json',dict(head=git('rev-parse','HEAD'),branch=git('branch','--show-current'),status=git('status','--short'),
        scientific_reference='524ed90689bd5923c249bba2e699abf627e703cd'))
    save(out/'checkpoint.json',dict(id='BHSM_MUON_PROPOSED_SEAM_LOCALIZED_MATCHING_20261005',
        outcome='explicit canonical action residual; native proposal remains unadopted',
        next=result['next'],source_identity='full compact source zero; no added J_chi source'))
    save(out/'output_hashes.json',{p.name:sha(p) for p in out.iterdir() if p.is_file()})
    print(json.dumps(dict(coefficients={k:vals[k] for k in ('joint_volume_norm','Z_L','Z_R','spatial_ratio','canonical_Yukawa_factor','canonical_photon','target_photon','raw_time_comparison_defect')},
        identity=identity,cached_actions=comparison),indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1]);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.repository.resolve(),a.output.resolve())
