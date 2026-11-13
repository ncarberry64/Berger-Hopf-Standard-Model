"""Executed canonical inverse on the inherited image of the Lorentz contour.

The continued action is assembled before Gauss and the temporal inverse.
Its contour is tau=i*(t-t0), with canonical initial/return conditions.
It supplies no real-positive exterior heat or terminal Dirichlet domain.
"""
from __future__ import annotations
from hashlib import sha256
import json
from pathlib import Path
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.linalg import lu_factor,lu_solve

from .muon_parent_gauge_geometry_correction import ROOT
from .muon_wick_temporal_action import wick_temporal_forms,analytic_gauss_reduction
from .muon_parent_maxwell_full_retarded import constrained_gauss_schur
from .muon_electromagnetic_soft_magnetic_source import magnetic_turn_on_profile
from .muon_birth_phase_continuation import _compressed_npz

RESPONSE='artifacts/muon_corrected_profile_magnetic_response_20261011/run_1'


def continued_canonical_cell(forms,step,state,source_value,source_rate):
    """Original signed action midpoint inverse, including source momentum.

    All arrays are analytic transpose bilinears.  M,K are literal symmetric
    action Hessians; B may be nonsymmetric.  A complex LU of the original
    cell operator replaces neither its sign nor its endpoint condition.
    """
    M,B,K=(np.asarray(a,complex)for a in forms);s=np.asarray(state,complex)
    b,bt=(np.asarray(a,complex)for a in(source_value,source_rate));n=len(s)//2;k=len(b)
    if (s.ndim!=2 or len(s)!=2*n or b.shape!=bt.shape or b.ndim!=2 or
            M.shape!=(n+k,n+k) or B.shape!=M.shape or K.shape!=M.shape or not np.isfinite(step)):
        raise ValueError('complete canonical state, literal reduced action and source jets required')
    if max(np.max(abs(M-M.T)),np.max(abs(K-K.T)))>1e-10*max(1.,np.max(abs(M)),np.max(abs(K))):
        raise ValueError('M,K must be symmetric analytic action Hessians')
    h=complex(step);x,p=s[:n],s[n:]
    mass,mixed,stiffness=M[:n,:n],B[:n,:n],K[:n,:n]
    source_p=B[n:,:n].T@b+M[:n,n:]@bt
    source_f=K[:n,n:]@b+B[:n,n:]@bt
    matrix=mass+h*(mixed.T-mixed)/2-h*h*stiffness/4
    P=-mixed.T+h*stiffness/2
    rhs=p+P@x-source_p+h*source_f/2
    factor=lu_factor(matrix);v=lu_solve(factor,rhs);xm=x+h*v/2
    force=mixed@v+stiffness@xm+source_f
    final=np.r_[x+h*v,p+h*force]
    momentum_parts=(mass@v,mixed.T@xm,source_p)
    midpoint_p=sum(momentum_parts)
    canonical_residual=midpoint_p-p-h*force/2
    inverse_residual=matrix@v-rhs
    return dict(final_state=final,midpoint_values=xm,midpoint_rates=v,
        original_midpoint_canonical_residual=canonical_residual,
        original_cell_inverse_residual=inverse_residual,
        original_midpoint_relative_residual=float(np.max(abs(canonical_residual))/(1+
            sum(np.max(abs(a))for a in (*momentum_parts,p,h*force/2)))),
        original_cell_inverse_relative_residual=float(np.max(abs(inverse_residual))/(1+
            np.max(abs(matrix@v))+np.max(abs(rhs)))),
        matrix=matrix,factor=factor,P=P,source_p=source_p,source_f=source_f,
        mixed=mixed,stiffness=stiffness,step=h)


def canonical_cell_adjoint(cell,terminal_dual):
    """Literal transpose recursive adjoint and inhomogeneous source pairing."""
    a=np.asarray(terminal_dual,complex);n=len(a)//2;rx,rp=a[:n],a[n:]
    h=cell['step'];B,K=cell['mixed'],cell['stiffness']
    q=h*rx+h*(B+h*K/2).T@rp
    vdual=lu_solve(cell['factor'],q,trans=1)
    previous=np.r_[rx+h*K.T@rp+cell['P'].T@vdual,rp+vdual]
    contraction=vdual.T@(-cell['source_p']+h*cell['source_f']/2)+h*rp.T@cell['source_f']
    return dict(previous_dual=previous,source_pairing=contraction,
        inverse_adjoint_residual=cell['matrix'].T@vdual-q)


def _source(t,side,duration):
    p,pt,_=magnetic_turn_on_profile(float(t),duration)if side=='incoming'else(1.,0.,0.)
    return p*np.eye(8),pt*np.eye(8)


def same_contour_arm(raw_splines,scalar_stiffness,*,side,length,duration,steps,
                     initial_state_L=None,initial_state_E=None):
    """Solve both original and continued action before comparing inverse images."""
    n=400;stateL=np.zeros((800,8))if initial_state_L is None else np.asarray(initial_state_L,float).copy()
    stateE=np.r_[stateL[:400],-1j*stateL[400:]]if initial_state_E is None else np.asarray(initial_state_E,complex).copy()
    h=length/steps;times=np.linspace(0,length,steps+1);statesL=[stateL.copy()];statesE=[stateE.copy()]
    cellsL=[];cellsE=[];gaussL=[];gaussE=[];atL=[];atE=[];rateL=[];rateE=[];local_residual=[]
    gauss_relative=[];local_relative=[]
    for j in range(steps):
        t=(j+.5)*h;raw=tuple(s(t)for s in raw_splines);move=wick_temporal_forms(raw,80)
        # Continue the unreduced action first.  Both original Gauss rows
        # are then solved on their own forms, before temporal inversion.
        L=constrained_gauss_schur(*raw,80);E=analytic_gauss_reduction(move['forms'],80)
        b,bt=_source(t,side,duration)
        cL=continued_canonical_cell(tuple(L[k]for k in('M','B','K')),h,stateL,b,bt)
        cE=continued_canonical_cell(tuple(E[k]for k in('M','B','K')),1j*h,stateE,b,-1j*bt)
        for label,red,c,forms,bbt,gauss,ats,rates in(
            ('L',L,cL,raw,bt,gaussL,atL,rateL),('E',E,cE,move['forms'],-1j*bt,gaussE,atE,rateE)):
            z=np.r_[c['midpoint_values'],b];zd=np.r_[c['midpoint_rates'],bbt]
            at=red['At_value_map']@z+red['At_velocity_map']@zd
            x=np.r_[at,z];v=np.r_[np.zeros_like(at),zd]
            parts=((forms[2]@x)[:80],(forms[1]@v)[:80]);gauss.append(sum(parts));ats.append(at);rates.append(c['midpoint_rates'])
            gauss_relative.append(float(np.max(abs(sum(parts)))/(1+sum(np.max(abs(a))for a in parts))))
        if np.any(cL['final_state'].imag):raise ArithmeticError('original real contour action produced complex fields')
        stateL=cL['final_state'].real;stateE=cE['final_state']
        statesL.append(stateL.copy());statesE.append(stateE.copy());cellsL.append(cL);cellsE.append(cE)
        local_residual.append(max(np.max(abs(cE[k]))for k in('original_midpoint_canonical_residual','original_cell_inverse_residual')))
        local_relative.append(max(cE['original_midpoint_relative_residual'],cE['original_cell_inverse_relative_residual']))
    # The actually reached terminal intrinsic-scalar wall-current cotangent,
    # not an invented soft Pauli projector. Its analytic action rotation is -1.
    readout=scalar_stiffness(length)[480:488,80:480]
    dualL=np.r_[readout.T,np.zeros((400,8))];dualE=-dualL.astype(complex)
    pairL=np.zeros((8,8),complex);pairE=pairL.copy();adjL=[dualL.copy()];adjE=[dualE.copy()];adjdef=0.
    for cL,cE in zip(reversed(cellsL),reversed(cellsE)):
        aL=canonical_cell_adjoint(cL,dualL);aE=canonical_cell_adjoint(cE,dualE)
        pairL+=aL['source_pairing'];pairE+=aE['source_pairing'];dualL=aL['previous_dual'];dualE=aE['previous_dual']
        adjL.append(dualL.copy());adjE.append(dualE.copy());adjdef=max(adjdef,float(np.max(abs(aE['inverse_adjoint_residual']))))
    outputL=readout@stateL[:400];outputE=-readout@stateE[:400]
    initialL=statesL[0];initialE=statesE[0]
    return dict(times=times,state_L=np.array(statesL),state_E=np.array(statesE),
        midpoint_rate_L=np.array(rateL),midpoint_rate_E=np.array(rateE),
        midpoint_At_L=np.array(atL),midpoint_At_E=np.array(atE),
        Gauss_L=np.array(gaussL),Gauss_E=np.array(gaussE),
        adjoint_L=np.array(adjL[::-1]),adjoint_E=np.array(adjE[::-1]),
        source_adjoint_pairing_L=pairL,source_adjoint_pairing_E=pairE,
        initial_boundary_pairing_L=dualL.T@initialL,initial_boundary_pairing_E=dualE.T@initialE,
        terminal_readout_L=outputL,terminal_readout_E=outputE,
        inverse_continuation_residual=np.array(statesE)-np.array(statesL)*np.r_[np.ones(400),-1j*np.ones(400)][None,:,None],
        full_action_adjoint_residual_L=outputL-pairL-dualL.T@initialL,
        full_action_adjoint_residual_E=outputE-pairE-dualE.T@initialE,
        midpoint_equation_residual_max=float(max(local_residual)),adjoint_inverse_residual_max=adjdef,
        original_and_continued_Gauss_relative_max=float(max(gauss_relative)),
        midpoint_equation_relative_residual_max=float(max(local_relative)),
        readout_scope='same intrinsic-H wall-current cotangent; neither Pauli nor full native trace',
        continued_contour='tau=i*(t-t0); h_E=i h_L',
        temporal_conditions='canonical incoming zero-before-source; outgoing inherits computed incoming x/p; outer canonical face output',
        terminal_Dirichlet_selected=False)


def materialize_wick_canonical_inverse(output,*,repository=ROOT,refinements=(16,32,64)):
    root=Path(repository);out=Path(output);out=out if out.is_absolute()else root/out
    if out.exists():raise FileExistsError('preserve earlier contour inverse applications')
    p=root/RESPONSE;md=json.loads((p/'result.json').read_bytes());refs=dict(md['input_hashes'])
    refs[RESPONSE+'/result.json']=sha256((p/'result.json').read_bytes()).hexdigest();data={}
    for side in('incoming','outgoing'):
        forms=[];scalar=None
        for stem in('operator_M','operator_B','operator_K','phase'):
            path=p/(side+'_'+stem+'.npz');digest=md['array_archives'][path.name]['sha256']
            if sha256(path.read_bytes()).hexdigest()!=digest:raise ValueError('consumed chronological action changed')
            refs[path.relative_to(root).as_posix()]=digest
            with np.load(path,allow_pickle=False)as a:values={k:a[k].copy()for k in a.files}
            if stem=='phase':saved=values
            else:
                name=stem.removeprefix('operator_');forms.append(CubicSpline(values['times'],values['raw_'+name]))
                if name=='K':scalar=CubicSpline(values['times'],values['scalar_K'])
        data[side]=dict(forms=forms,scalar=scalar,saved=saved,length=float(saved['times'][-1]))
    arrays={};records=[];previous={}
    for steps in refinements:
        inheritedL=inheritedE=None
        for side in('incoming','outgoing'):
            d=data[side];a=same_contour_arm(d['forms'],d['scalar'],side=side,length=d['length'],
                duration=md['turn_on_duration'],steps=steps,initial_state_L=inheritedL,initial_state_E=inheritedE)
            inheritedL=a['state_L'][-1];inheritedE=a['state_E'][-1]
            prefix=side+'_'+str(steps)+'_';arrays.update({prefix+k:v for k,v in a.items()if isinstance(v,np.ndarray)})
            saved=d['saved']['state'][-1]
            row=dict(side=side,steps=steps,original_Gauss_max=float(np.max(abs(a['Gauss_L']))),
                continued_Gauss_max=float(np.max(abs(a['Gauss_E']))),
                inverse_continuation_max=float(np.max(abs(a['inverse_continuation_residual']))),
                original_midpoint_inverse_residual=a['midpoint_equation_residual_max'],
                original_and_continued_Gauss_relative_max=a['original_and_continued_Gauss_relative_max'],
                original_midpoint_inverse_relative_residual=a['midpoint_equation_relative_residual_max'],
                literal_transpose_adjoint_residual=a['adjoint_inverse_residual_max'],
                action_adjoint_max=float(np.max(abs(a['full_action_adjoint_residual_E']))),
                terminal_response_difference_from_saved_DOP853=float(np.linalg.norm(inheritedL-saved)),
                terminal_response_norm=float(np.linalg.norm(inheritedL)),
                readout_norm=float(np.linalg.norm(a['terminal_readout_L'])),
                temporal_refinement_difference=None if side not in previous else float(np.linalg.norm(inheritedL-previous[side])))
            records.append(row);previous[side]=inheritedL.copy();print(json.dumps(dict(stage='continued_same_domain_canonical_inverse',**row),sort_keys=True),flush=True)
    for name in('muon_wick_canonical_inverse','muon_wick_temporal_action'):
        path='src/bhsm/interface/'+name+'.py';refs[path]=sha256((root/path).read_bytes()).hexdigest()
    for path,h in refs.items():
        if sha256((root/path).read_bytes()).hexdigest()!=h:raise RuntimeError('consumed source changed: '+path)
    out.mkdir(parents=True);_compressed_npz(out/'application.npz',arrays)
    result=dict(classification='EVALUATED_CONTINUED_SAME_CANONICAL_CONTOUR_FULL488_INVERSE',records=records,input_hashes=refs,
        numerical_sha256=sha256((out/'application.npz').read_bytes()).hexdigest(),
        continuation='action and source time slots first; original complex Gauss then complex midpoint inverse; tau=i*(t-t0)',
        inherited_birth_graph='computed common canonical x/p in the unchanged numerical angular/body-frame restriction',
        far_face_role='original canonical continuation output, not E0 or a terminal homogeneous boundary condition',
        readout='actual intrinsic-H wall-current coefficient cotangent, no physical Pauli promotion',
        real_positive_heat_or_sectorial_exterior_domain_identified=False,physical_native_Pauli_completed=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='binary64 midpoint refinements and action-adjoint original-row checks; upstream coefficient interpolation and full contour/relative heat completion not enclosed')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    return result
