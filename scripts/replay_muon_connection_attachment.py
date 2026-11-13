"""Scoped action/attachment trace, without rerunning any scientific producer.

Extract the actual retained source equations by AST, and derive the new
Higgs integrability obligation. This is not a background solve, spectrum,
exterior response, or generic child-to-observable framework.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import sympy as sp

HERE=Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p,value):
    p.write_text(json.dumps(value,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8')


def source_equations(path,name):
    text=path.read_text(encoding='utf-8-sig');tree=ast.parse(text)
    node=next(n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name==name)
    literals=[]
    for n in ast.walk(node):
        if isinstance(n,ast.Dict):
            for key,val in zip(n.keys,n.values):
                if isinstance(key,ast.Constant) and isinstance(key.value,str):
                    try: value=ast.literal_eval(val)
                    except (ValueError,TypeError): continue
                    if isinstance(value,(str,int,float,bool)) or value is None:
                        literals.append({'key':key.value,'value':value,'line':val.lineno})
    return {'function':name,'line':node.lineno,'end_line':node.end_lineno,
            'source':ast.get_source_segment(text,node),'literal_equations':literals}


def higgs_integrability():
    """Required consequence IF the mechanical connection acts on H.

    H/nu=(0,1); e_a=-i sigma_a in its supplied weak doublet. This is
    the retained local Higgs branch, not a chosen physical global solution.
    Nonzero curvature has no parallel nonzero doublet. No mass/VEV is fitted.
    """
    L=sp.Symbol('lambda',real=True)
    sigma=[sp.Matrix([[0,1],[1,0]]),sp.Matrix([[0,-sp.I],[sp.I,0]]),sp.diag(1,-1)]
    e=[-sp.I*s for s in sigma];H=sp.Matrix([0,1])
    Q=sigma[2]/2+sp.eye(2)/2
    images=[2*L*(L-1)*v*H for v in e]
    gram=sp.simplify(sum((v.conjugate().T*v)[0] for v in images))
    parallel=[L*v*H for v in e]
    mixed=[sp.simplify(sp.I*Q*v*H) for v in e]
    derivative=sp.simplify(sum((v.conjugate().T*v)[0] for v in parallel))
    # In the fixed sigma0 local-Higgs chart, div Omega0=0 in the round
    # angular geometry and sum_a Omega0_a^2=-3lambda^2 I. Radius restored.
    lap=sp.simplify(sum((L*L*v*v*H for v in e),sp.zeros(2,1)))
    determinant=sp.factor((2*L*(L-1)*e[0]).det())
    return dict(curvature_H_images=[[str(t) for t in v] for v in images],
                curvature_H_norm2_over_nu2_unit_coframe=str(sp.factor(gram)),
                one_curvature_component_determinant=str(determinant),
                DH_norm2_over_nu2_unit_coframe=str(sp.factor(derivative)),
                covariant_angular_laplacian_H_over_nu_unit_coframe=[str(t) for t in lap],
                Q_H=[str(t) for t in Q*H],
                photon_Higgs_mixed_kernel_per_lambda_nu=[list(map(str,v)) for v in mixed],
                exact_checks=dict(curvature_identity=sp.simplify(gram-12*L**2*(L-1)**2)==0,
                    derivative_identity=sp.simplify(derivative-3*L**2)==0,
                    Q_annihilates_H=Q*H==sp.zeros(2,1)),
                conditional_equations=[
                    'H1=U_H H0; Q1=U_H Q0 U_H^-1; Q1 H1=0',
                    'Omega1=(lambda-1)e_a theta_R^a, dH1=e_a theta_R^a H1, D_Omega1 H1=lambda e_a theta_R^a H1',
                    'F_Omega1,*a=2lambda(lambda-1)e_a; sum ||F_*a H1||^2=12lambda^2(lambda-1)^2 ||H0||^2',
                    'R_angular^-2 Delta_Omega H0=-3lambda^2/R_angular^2 H0 in fixed sigma0 local-Higgs chart',
                    'No nonzero covariantly constant H exists where these curvature components span su2',
                    'For q_H(v,H)=<D v,D H> and a H=0, delta_a q_H(v,H)=<v,a^dagger D H>; this mixed Higgs row need not vanish',
                    'This does not exclude a nonconstant Higgs solution or prove any alternative background solves the full equations'])


def higgs_source_application(root,old):
    """NEW conditional mixed Higgs row on the eight supplied modes.

    Reuse saved Ad_w, Y and lambda, not the old transport/weak producer.
    Output is in sigma0, normalized by nu*T_b*lambda/R_angular^2.
    The corresponding Lorentz weight/sign belongs to the inherited action.
    This is not an evaluated exterior forcing or a physical Higgs solution.
    """
    sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_matched_mechanical_source import product
    with np.load(root/'artifacts/muon_matched_mechanical_source_20261002/replay_reference/matched_source_and_weak_actions.npz') as p:
        R=p['rotation_coefficients'];lam=p['mechanical_lambda']
    with np.load(root/'artifacts/muon_source_jet_20261002/replay_reference/local_source_actions.npz') as p:
        Y=p['real_mode_coefficients']
    if Y.shape!=(8,3,2,2):raise ValueError('supplied eight source lifts required')
    out={}
    norms=np.zeros(8)
    for n in (1,3):
        # i Q0 R_ad e_d H0 = (R_a1-i R_a2,0).
        row=sum((product(R[a,0]-1j*R[a,1],Y[:,a],1,n) for a in range(3)),
                np.zeros((8,n+1,n+1),complex))
        v=np.zeros((8,2,n+1,n+1),complex);v[:,0]=row
        out[f'Higgs_mixed_unit_n{n}']=v
        out[f'Higgs_mixed_cut_per_nu_Rminus2_n{n}']=float(old['T_b_reused'])*lam[:,None,None,None,None]*v[None]
        norms+=np.sum(abs(v)**2,axis=(1,2,3))
    out['unit_column_norm2']=norms
    return out,dict(scope='conditional mechanical associated connection and transported retained local H branch; positive angular pairing, prior Lorentz sign not reapplied here',
        equation='U_H^-1 a1^dagger D_Omega1 H1 = (T_b lambda nu/R_angular^2) sum_a Y_A,a (R_a1-i R_a2,0)',
        direct_fixed_H_photon_quadratic_column='zero since a H=0; does not remove this Higgs/gauge mixed row or its elimination response',
        unit_column_norm2=norms.tolist(),connected_levels=[1,3],
        source_coordinate='b; T_b inserted once in cut actions; no 2/3 or Tr16 multiplier',
        physical_Higgs_background_selected=False,exterior_response=False,
        error_scope='Binary64 finite Gaunt contractions, normalized Haar support exact; not a certified physical error enclosure')


def attachment_obligation():
    return dict(
        operand='Current action-to-carrier horizontal internal connection coefficient A_hor^(0), with its M5/M4 attachment',
        bundle_map='J5:S(g5) tensor E_SM,16 tensor C3_family -> E5_physical; J4:S(h4) tensor E_SM,16 tensor C3_family -> E4_physical; isometric Clifford intertwiners on the inherited trace/form domain',
        defining_equation='I_spin tensor A_hor^(0) tensor I3 = [J5^-1 nabla5_total[A_SM=0] J5 - nabla5_spin tensor I16 tensor I3]; T54 J5=J4 T54_canonical. A supplied contracted coefficient on the retained source/test space suffices; a complete kernel or new J reconstruction is not required.',
        coefficient_type='Omega5_SM,total in Omega^1(M5, rho16_*(ad P_SM)); trace to M4 by the retained connection-compatible T54. Any additional Clifford-degree zero potential must be recorded separately, not called another connection.',
        reference_substitution='v17.97 declares zero fluctuation about the mechanical connection. To implement that declaration in S_Dirac[e,omega_spin,A_SM,Psi], one needs the actual substitution A_hor^(0)=rho16_*(omega_mech), equivalently a connection-compatible attachment Phi of P_diag to the SM Sp1 factor. The retained action writes F_A and nabla_total without specifying this substitution. No alternative background is certified here.',
        horizontal_projection='If a parent spinor reduction is used: (A_ind,mu)_rs=<eta_r,nabla_parent,X_mu^H eta_s>_owned_fibre_wall - (base spin connection)_rs; X_mu^H=partial_mu-omega_mech,mu^a V_a. Neither eigenvalues alone nor trace index supplies eta_r and this projection.',
        source_tangent='delta_b Omega4_SM,total=T_b Y_A(-iQ) in saved sigma0/right coframe; after saved U, delta_b Omega4,1=U delta_b Omega4,0 U^-1. delta_b U=0 for that fixed source-independent frame; any attachment variation must be included if the actual action makes J source-dependent.',
        higgs_tangent='Transport H and Q together by the derived associated-bundle map; the electromagnetic tangent satisfies delta_b Omega_H H=0 because Q_H H=0. This does not make D_background H or curvature zero.',
        consumer='Current D_L,D_R/D_strat source action, background-compatible parent mixed weak operator, SAME-source prefix return j_ext and finite-E1 response',
        supplied='mechanical principal connection; rank16 representation and charge normalization; intended zero fluctuation; vertical Dirac eigenvalue blocks; local Dirac template; reset trace graph',
        not_supplied='expanded current nabla_total or connection-preserving J5/T54 establishing where the mechanical horizontal connection occurs; associated physical Higgs background on that attachment',
        classification='Reference/fluctuation meaning declared; current covariant attachment is not specified by the inspected retained action expressions. Computing a supplied attachment is not the blocker: the equation/embedding to compute is absent. No claim of an exhaustive absence theorem for all BHSM records.',
        no_new_interpolation_parameter=True)


def run(manifest,output):
    refs=json.loads(manifest.read_text())
    root=HERE.parent if (HERE.parent/'src').is_dir() else Path(refs['repository'])
    if output.exists(): raise FileExistsError('Use a new output; preserve earlier checkpoints')
    for row in refs['inputs']:
        p=Path(row['absolute_path']) if 'absolute_path' in row else root/row['repository_path']
        if sha(p)!=row['sha256']: raise ValueError('changed retained source '+str(p))
    output.mkdir(parents=True)
    equations=[]
    for row in refs['inputs']:
        p=Path(row['absolute_path']) if 'absolute_path' in row else root/row['repository_path']
        for name in row.get('functions',[]):
            equations.append(dict(path=row.get('repository_path',row.get('absolute_path')),
                sha256=row['sha256'],**source_equations(p,name)))
    save(output/'retained_equations.json',equations)
    algebra=higgs_integrability()
    save(output/'higgs_connection_obligation.json',algebra)
    save(output/'missing_attachment.json',attachment_obligation())
    old=json.loads((root/refs['previous_result_path']).read_text())
    actions,higgs_response=higgs_source_application(root,old)
    np.savez_compressed(output/'conditional_higgs_source_actions.npz',**actions)
    result=dict(checkpoint='BHSM_MUON_ACTION_CONNECTION_ATTACHMENT_20261002',
        reference='524ed90689bd5923c249bba2e699abf627e703cd',start_HEAD=refs['start_HEAD'],
        conclusion='The zero mechanical-sector amplitude is a fluctuation, as explicitly declared by v17.97. The actual fermion connection-preserving attachment is not specified by the inspected covariant action/interface expressions.',
        total_covariant_derivative='nabla_total=nabla_spin(e,omega_LC+C) tensor I_rep + I_spin tensor nabla_SM,total; family factor I3. C_star=-M_C^-1 J_S vanishes at zero classical Psi, not at a general quantum state.',
        declared_reference='Omega_SM,total=Omega_SM,ref+a_SM; Omega_SM,ref intended rho16_*(omega_mech); a_SM^(0)=0 in that declared sector. This is not an established current-D substitution.',
        field_zero_scope='v15.57 writes A_SM=H_SM=Psi=0 at reset; v17.97 identifies its gauge trace as a zero fluctuation. Neither fixes the current fermion horizontal attachment or a nonzero source response.',
        local_body='H_free=R^-1 diag(-D3,+D3)+m sigma1_LR tensor I; separate affine Q source. It omits an explicit rank16 mechanical connection and is documented as a parameterized free block, not an interacting background determination.',
        row_use=dict(saved_mechanical_angular_rows='exact primitive mechanical reference contributions if the declared associated connection is shown to enter the physical gauge operator; no recalculation',
            saved_curvature_and_constraint_contacts='required for that mechanical gauge reference; may not be dropped from a promoted Hessian',
            saved_electric_radial_coefficients='reusable inherited primitive weight/metric data, with same-owner matching still required',
            physical_complete_weak_operator=None,quantum_matching=None,physical_exterior_return=None,
            required_extra='actual background J5/T54; associated Higgs/current terms and any nonminimal horizontal potential from the owned parent action'),
        compatibility_obligation=algebra,first_unresolved_operand=attachment_obligation(),
        new_conditional_Higgs_source_application=higgs_response,
        prior_mechanical_result_sha256=refs['previous_result_sha256'],
        prior_mechanical_checks_preserved=old['checks'],frozen_local=old['frozen_local'],
        native_ledger=old['native_ledger'],physical_a_mu=None,physical_g_mu=None,
        actual_execution=dict(old_producers_rerun=0,old_source_or_weak_rows_recomputed=0,
            new_exact_Higgs_integrability_derivation=True,new_conditional_mixed_Higgs_source_columns=8,background_solution_evaluated=False,
            exterior_source_responses=0,native_evaluations=0,physical_transfer_directions=0),
        error_scope='Exact symbolic conditional compatibility identities and source-identity extraction, plus finite binary64 conditional Higgs source contractions. No new physical background, certified numerical native bound or state selection.')
    save(output/'result.json',result)
    save(output/'receipt.json',{'input_refs_sha256':sha(manifest),'replay_sha256':sha(Path(__file__)),
        'old_scientific_producers_called':False,'reused_helpers':['muon_matched_mechanical_source.product','muon_local_source_jet._gaunt'],
        'files':[{'path':p.name,'sha256':sha(p)} for p in sorted(output.iterdir()) if p.name!='receipt.json']})
    print(json.dumps({'output':str(output),'checks':algebra['exact_checks'],
        'reference_meaning':'zero fluctuation, not zero mechanical curvature','native_evaluations':0}))


if __name__=='__main__':
    p=argparse.ArgumentParser();default=HERE/'input_refs.json'
    if not default.exists(): default=HERE.parent/'artifacts/muon_connection_attachment_20261002/input_refs.json'
    p.add_argument('--inputs',type=Path,default=default);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.inputs,a.output)
