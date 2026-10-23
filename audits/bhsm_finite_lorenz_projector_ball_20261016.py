"""Finite one-form Lorenz projector from exact saved MP moment operands.

The 320x320 FP kinetic block is distinct from the pure ghost norm. The
projector acts on the existing common1200 coefficient representation;
it neither constructs the native BRST quotient nor a retarded exterior.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import mpmath as mp
import numpy as np
from flint import arb,arb_mat,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'audits')]
import bhsm_changing_lorenz_tensor_precision_20261016 as tensor
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def decode(text):
    sign,man,ex,bits=str(text).split(':')
    parts=(int(sign),int(man,16),int(ex),int(bits))
    if parts[0] not in (0,1) or parts[1].bit_length()!=parts[3]:
        raise ValueError('Exact finite working-binary MP tuple required')
    return mp.make_mpf(parts)


def dyadic(value):
    s,m,e,b=value._mpf_
    return arb(((-1 if s else 1)*m,e))


def bounds(A):
    maximum=arb(0);infinity=arb(0)
    for i in range(A.nrows()):
        row=arb(0)
        for j in range(A.ncols()):
            a=abs(A[i,j]);row+=a
            if a.upper()>maximum.upper():maximum=a
        if row.upper()>infinity.upper():infinity=row
    return dict(max_entry_upper=float(np.nextafter(float(maximum.upper()),np.inf)),
                infinity_norm_upper=float(np.nextafter(float(infinity.upper()),np.inf)))


def execute(moment_file,prefix,E_file,output,bits):
    moment_file,E_file,out=map(Path,(moment_file,E_file,output))
    if out.exists():raise FileExistsError('Preserve each independent finite solve')
    moment_raw=moment_file.read_bytes();Eraw=E_file.read_bytes()
    with np.load(E_file,allow_pickle=False)as z:
        name='EW4_real_angular_derivatives'
        if name not in z:name='EW4_real_harmonic_derivatives'
        E=z[name].copy()
    if E.shape!=(3,20,20) or not np.isrealobj(E):raise ValueError('Complete held binary angular coefficients required')
    with mp.workdps(80),np.load(moment_file,allow_pickle=False)as z:
        moments={}
        for name,template in tensor.tensors().items():
            encoded=z[prefix+'moment_'+name+'_exact_MP_tuple']
            if encoded.shape!=template.shape:raise ValueError('Same retained coefficient tensors required')
            moments[name]=np.array([decode(x) for x in encoded.flat],dtype=object).reshape(encoded.shape)
        B=tensor.assemble(moments,E)
        if B.shape!=(320,1200) or any(x!=0 for x in B[:,1120:].flat):
            raise ValueError('Actual one-form representative and scalar padding required')
        if not np.array_equal(tensor.as_float(B),tensor.load_matrix(z,prefix+'B')):
            raise ValueError('Exact saved moments did not reproduce the complete original rounded B')
    old=ctx.prec;ctx.prec=bits
    try:
        Bb=arb_mat(320,1200,[dyadic(x) for x in B.flat])
        S=arb_mat(320,320,[Bb[i,800+j] for i in range(320) for j in range(320)])
        print(json.dumps(dict(stage='actual_finite_FP_kinetic_solve',bits=bits,rows=320,all_right_columns=1200)),flush=True)
        X=S.solve(Bb)
        residual=bounds(S*X-Bb)
        identity=arb_mat(320,320,[int(i==j) for i in range(320) for j in range(320)])
        Xghost=arb_mat(320,320,[X[i,800+j] for i in range(320) for j in range(320)])
        idempotence=bounds((Xghost-identity)*X)
        hi=np.zeros((320,1200));lo=hi.copy();conversion=arb(0)
        for i in range(320):
            for j in range(1200):
                v=X[i,j]
                if not v.is_finite():raise ArithmeticError('Unresolved finite FP inverse')
                h=float(v.mid());l=float((v-arb(h)).mid())
                if not np.isfinite([h,l]).all():raise ArithmeticError('Nonfinite output representation')
                hi[i,j],lo[i,j]=h,l
                error=abs(v-arb(h)-arb(l))
                if error.upper()>conversion.upper():conversion=error
        conversion_upper=float(np.nextafter(float(conversion.upper()),np.inf))
    finally:ctx.prec=old
    out.mkdir(parents=True)
    _compressed_npz(out/'finite_projector_action.npz',dict(X_high=hi,X_low=lo,
        ghost_coordinate_indices=np.arange(800,1120),full_common_dimension=np.array(1200)))
    pins={}
    for name,module in list(sys.modules.items()):
        p=getattr(module,'__file__',None)
        if p and (name.startswith('bhsm.') or name.startswith('bhsm_')) and Path(p).is_relative_to(ROOT):
            pins[Path(p).relative_to(ROOT).as_posix()]=sha256(Path(p).read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(ROOT).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    result=dict(classification='FINITE_ONEFORM_LORENZ_PROJECTOR_FROM_SAVED_MP_COEFFICIENT_MOMENTS',
        arithmetic=f'MP80 reconstruction of saved dyadic tensors, then ARB{bits} solve on that exact finite B',
        input_moment_sha256=sha256(moment_raw).hexdigest(),input_E_sha256=sha256(Eraw).hexdigest(),moment_prefix=prefix,
        source_and_owner_sha256=dict(sorted(pins.items())),
        numerical_sha256=sha256((out/'finite_projector_action.npz').read_bytes()).hexdigest(),
        projector_definition='Pi=I1200-embed_ghost X; S X=B; S=B[:,800:1120]',
        inverse_is_FP_kinetic_not_pure_ghost_Gram=True,
        all_common1200_columns_and_ghost320_rows_retained=True,
        exact_finite_B_times_Pi_residual=residual,exact_finite_Pi_idempotence_residual=idempotence,
        X_high_low_max_entry_conversion_error_upper=conversion_upper,
        arithmetic_ball_enclosures_exclude_upstream_fields_and_quadrature=True,
        physical_native_BRST_or_outgoing_domain_selected=False,all15_physical_convergence=False,
        physical_energy_field_source_domain_derivative_pass=False,original_coupled_matching_corrections=0,
        physical_normalized_muon_spins=None,physical_muon_magnetic_moment=None)
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(result_sha256=sha256((out/'result.json').read_bytes()).hexdigest(),residual=residual,
        idempotence=idempotence,conversion_upper=conversion_upper)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--moment-file',required=True)
    p.add_argument('--moment-prefix',default='');p.add_argument('--E-file',required=True)
    p.add_argument('--output',required=True);p.add_argument('--bits',type=int,default=384)
    a=p.parse_args()
    if a.bits<320:raise ValueError('Precision must exceed retained MP80 operand mantissas')
    execute(a.moment_file,a.moment_prefix,a.E_file,a.output,a.bits)
