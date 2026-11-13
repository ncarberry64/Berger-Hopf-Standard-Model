"""Consume derived leading-cap modes in additional original-action rows.

Preserves original histories, their source profiles and all historical rows.
This adds a transverse lambda4 variation/test frame, not a new physical state
or a completed native/retarded domain.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np

REPO=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(REPO/'src'),str(REPO/'scripts')]
from evaluate_em_carrier_original_maxwell_20261016 import PHASES,snapshot,rows,direction,real,atomic
from bhsm.interface.electromagnetic_carrier_cap_domain import coexact_radial_jacobi,coexact_indicial_data
from bhsm.interface.electromagnetic_carrier_original_maxwell import even_angular_space
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_parent_mean_causal_action import MAXWELL_TO_CAP
from bhsm.interface.muon_parent_retarded_hypercharge import WALL
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def execute(output):
    out=Path(output).resolve()
    if out.exists():raise FileExistsError('preserve previous evidence')
    out.mkdir(parents=True);space=even_angular_space();arrays={};records=[];pins={}
    for side,path in PHASES.items():
        phase=load_profile_preserving_phase(path,repository=REPO);pins.update(phase['input_hashes'])
        previous=None;table=[]
        for order in (96,192):
            snap=snapshot(phase,phase['receipt']['span']/2,order,space)
            original_fields=[x.copy() for x in snap['fields']]
            b,br=coexact_radial_jacobi(snap['rho'],3,curl_squared=4,wall=WALL)
            snap['b'],snap['br']=b,br
            # Reconstructed background fields and inherited/source profiles
            # remain the originals. Only an ADDITIONAL variation frame changes.
            if not all(np.array_equal(a,z)for a,z in zip(original_fields,snap['fields'])):
                raise ValueError('original fields changed during enrichment')
            baseline=rows(snap);value=real(baseline['value_rows']).ravel();momentum=real(baseline['rate_rows']).ravel()
            kinetic=np.kron(np.einsum('r,ra,rb->ab',MAXWELL_TO_CAP*snap['wr']*snap['densities'][:,0,0],b,b),np.eye(4))*np.dot(snap['charge'],snap['charge'])
            columns=[]
            for is_rate in (False,True):
                for radial in range(4):
                    for mode in range(4):
                        delta=direction(snap,radial,mode,rate=is_rate)
                        applied=rows(snap,[v.astype(complex)+1e-20j*d for v,d in zip(snap['fields'],delta)])
                        columns.append(np.r_[applied['value_rows'].imag.ravel(),applied['rate_rows'].imag.ravel()]/1e-20)
            operator=np.column_stack(columns)
            current={'value':value,'rate':momentum,'kinetic':kinetic,'operator':operator}
            record={'radial_order':order,'value_max':float(np.max(abs(value))),
                'local_rate_max':float(np.max(abs(momentum))),'operator_max':float(np.max(abs(operator))),
                'Gauss_value_max':float(np.max(abs(value.reshape(4,5,4,10)[:,0]))),
                'actual_kinetic_min_eigenvalue':float(np.linalg.eigvalsh(kinetic)[0]),
                'original_primal_and_source_profiles_unchanged':True}
            if previous is not None:
                record['whole_array_absolute_changes']={k:float(np.max(abs(current[k]-previous[k])))for k in current}
            prefix=f'{side}_q{order}_'
            arrays.update({prefix+k:v for k,v in current.items()})
            arrays[prefix+'new_basis']=b;arrays[prefix+'new_basis_radial']=br
            previous=current;table.append(record)
            _compressed_npz(out/'application.npz.tmp',arrays);(out/'application.npz.tmp').replace(out/'application.npz')
            atomic(out/(side+'_progress.json'),table)
            print(side,order,'additional cap-frame original application saved',flush=True)
        records.append({'side':side,'additional_variation_radial_profiles':4,'table':table})
    for name,module in list(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if path and Path(path).is_relative_to(REPO) and(name.startswith('bhsm.')or name.startswith('evaluate_em_')or name.startswith('bhsm_real_')):
            pins[Path(path).relative_to(REPO).as_posix()]=sha256(Path(path).read_bytes()).hexdigest()
    pins[Path(__file__).relative_to(REPO).as_posix()]=sha256(Path(__file__).read_bytes()).hexdigest()
    result={'classification':'ADDITIONAL_LEADING_CAP_DOMAIN_TESTS_CONSUMED_BY_ORIGINAL_MAXWELL',
        'indicial_data':coexact_indicial_data(4),'records':records,
        'interpretation':'new lambda4 leading-coexact Jacobi variation frame; every original row and source profile preserved separately',
        'comparison_scope':'96-to192 quadrature on added finite test/field frame; not radial completeness or a physical mode solve',
        'old_basis_and_historical_before_states_changed':False,'actual_primal_fields_changed':False,
        'matching_guard':2e-10,'full_physical_outgoing_derivative_passed':False,'coupled_corrections':0,
        'fresh_adopted_preparation_Maxwell':None,'fresh_adopted_preparation_226_rows':None,
        'physical_packets':None,'physical_muon_pole':None,'a_mu':None,'g_mu':None,'total_uncertainty':None,
        'input_and_source_sha256':dict(sorted(pins.items())),
        'numerical_sha256':sha256((out/'application.npz').read_bytes()).hexdigest()}
    atomic(out/'result.json',result)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    execute(p.parse_args().output)
