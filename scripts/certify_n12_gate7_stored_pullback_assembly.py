"""Enclose assembly rounding against the exact complete-center local tensors."""
import json
from pathlib import Path
import sys
import numpy as np
from flint import arb,ctx

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import certify_n12_gate7_resolved_coordinate_causal_transport as coordinate
import certify_n12_gate7_frozen_output_map_construction as output_certificate
from bhsm.interface import stored_pullback_assembly_error as assembly
from bhsm.interface import current_green_causal_error as causal_error

center=coordinate.center
RESULT=ROOT/'artifacts/flagship_integration/BHSM_N12_GATE7_STORED_PULLBACK_ASSEMBLY.json'
THEORY=ROOT/'theory/n12_gate7_stored_pullback_assembly.md'
_array_hash=output_certificate.maps_certificate._array_hash


def _verify_covariance(actual,expected,label):
    if not np.array_equal(actual,expected):
        raise RuntimeError(f'Reassembled center covariance differs: {label}')


def _stored_error(stored,alternative,record):
    difference=assembly.difference_frobenius_upper(stored,alternative)
    total=assembly._float_upper(arb(difference)+arb(record['assembly_error_frobenius_upper']))
    return dict(alternative_algorithm_error_frobenius_upper=record['assembly_error_frobenius_upper'],
                algorithm_difference_frobenius_upper=difference,
                stored_assembly_error_frobenius_upper=total)


def build_payload():
    prior=json.loads(coordinate.RESULT.read_text())
    prior_rows=output_certificate._coordinate_rows(prior)
    output_prior=json.loads(output_certificate.RESULT.read_text())
    if (output_prior.get('artifact')!='BHSM_N12_GATE7_FROZEN_OUTPUT_MAP_CONSTRUCTION'
            or output_prior.get('validation_passed') is not True
            or output_prior.get('coverage')!=dict(intervals=370,nodes=371,complete=True)):
        raise RuntimeError('Complete output-map certificate required')
    inputs={}
    for record in (prior,output_prior):
        for name,digest in coordinate._verified_inputs(record).items():
            if name in inputs and inputs[name]!=digest:
                raise RuntimeError('Conflicting assembly input binding')
            inputs[name]=digest
    sources=(Path(__file__).resolve(),THEORY,coordinate.RESULT,output_certificate.RESULT,
        Path(assembly.__file__),Path(causal_error.__file__),Path(coordinate.__file__),
        Path(output_certificate.__file__),Path(assembly._exact_matrix.__code__.co_filename),
        Path(assembly._real_binary64.__code__.co_filename))
    for path in sources:
        name,digest=path.relative_to(ROOT).as_posix(),center._sha(path)
        if name in inputs and inputs[name]!=digest:
            raise RuntimeError('Conflicting assembly source binding')
        inputs[name]=digest
    geometry=center.supplemental._load_geometry()
    axes=center.component._load_axes()
    midaxes=geometry['inputs']['midpoint'][3]
    with np.load(center.JACOBIAN.with_suffix('.npz')) as d:
        tangents=d['endpoint_physical_tangent_action'].copy()
        midtangents=d['midpoint_physical_tangent_action'].copy()
    with np.load(center.PRECONDITIONER.with_suffix('.npz')) as d:
        right=d['reduced_right_Newton_blocks'].copy();left=d['left_Newton_blocks'].copy()
    with np.load(center.ENDPOINT.with_suffix('.npz')) as d:times=d['collocation_arc_parameters'].copy()
    with np.load(center.AMBIENT.with_suffix('.npz')) as d:ambient=d['ambient_DF_mid'].copy()
    with np.load(center.DATA) as d:
        expected_covariances=d['local_pair_output_covariances'].copy()
        expected_adjacent=d['adjacent_right_left_output_cross_covariances'].copy()
        expected_maps=d['causal_maps_center'].copy()
    maps=center.component._causal_maps(tangents,left,right)
    _verify_covariance(maps,expected_maps,'causal maps')
    if _array_hash(maps)!=prior.get('causal_maps_SHA256'):
        raise RuntimeError('Assembly maps differ from prior error transport')
    previous_right=None
    rows=[]
    previous_precision=ctx.prec
    ctx.prec=512
    try:
        for i,prior_row in enumerate(prior_rows):
            h=float(times[i+1]-times[i])
            midpoint=center._kinematic_midpoint_map(i,h,axes,tangents,midtangents)
            test=center.cert._frame(tangents[i+1],center.cert.TEST_DESCRIPTOR_SCALE).T
            b=-np.linalg.solve(right[i],test)
            incidence=b@ambient[i]
            outputs=[h*b/6+h*h*incidence/12,h*b/6-h*h*incidence/12,2*h*b/3]
            local=np.zeros((74,148,148))
            parts=[]
            for node,label,out,selection in ((i,'left',outputs[0],slice(0,74)),
                                             (i+1,'right',outputs[1],slice(74,148))):
                if node==0:continue
                uu,basis=center._tensor('endpoint',node)
                stored=center._transformed(out,uu,basis.T)
                alternative,bound=assembly.assemble_pullback_with_error(out,uu,basis.T)
                part=_stored_error(stored,alternative,bound)
                part.update(kind='endpoint',index=node,output_label=label)
                parts.append(part)
                local[:,selection,selection]+=stored  # Addition to zero is exact.
            uu,basis=center._tensor('midpoint',i)
            stored,_=center._supplemental_midpoint_pullback(i,outputs[2],uu,basis,midaxes[i],
                center.cert._frame(midtangents[i],center.cert.TRIAL_DESCRIPTOR_SCALE),midpoint.augmented)
            completion,_=center.supplemental._completion(i,geometry)
            x=np.linalg.solve(completion.full_basis,midpoint.augmented)
            with np.load(center.supplemental._aggregate_path(i)) as d:
                cu=d['complement_retained'].copy();cc=d['complement_complement'].copy()
            operand_hashes=dict(basis=_array_hash(completion.full_basis),target=_array_hash(midpoint.augmented),
                approximate_coordinates=_array_hash(x),retained_retained=_array_hash(uu),
                complement_retained=_array_hash(cu),complement_complement=_array_hash(cc))
            if (operand_hashes!=prior_row['operand_binary64_SHA256']
                    or _array_hash(outputs[2])!=prior_row['output_map_SHA256']):
                raise RuntimeError('Midpoint assembly operands differ from completed coordinate proof')
            full=np.empty((99,99,99))
            full[:,:73,:73]=uu;full[:,73:,:73]=cu
            full[:,:73,73:]=cu.transpose(0,2,1);full[:,73:,73:]=cc
            alternative,bound=assembly.assemble_pullback_with_error(outputs[2],full,x,symmetrize=True)
            part=_stored_error(stored,alternative,bound)
            part.update(kind='midpoint',index=i,output_label='midpoint')
            parts.append(part)
            final_add=assembly.addition_rounding_frobenius_upper(local,stored)
            local+=stored
            # The complete center stores the sum of the two cross blocks as
            # one bilinear block, introducing one more addition to enclose.
            cross_add=assembly.addition_rounding_frobenius_upper(
                local[:,:74,74:],local[:,74:,:74].transpose(0,2,1))
            covariances=center._covariance_blocks(local)
            covariance_difference=assembly.difference_frobenius_upper(covariances,expected_covariances[i])
            pair_blocks=center._pair_blocks(local)
            left_flat=pair_blocks[0].reshape(74,-1)
            adjacent=np.zeros((74,74)) if previous_right is None else previous_right@left_flat.T
            adjacent_difference=assembly.difference_frobenius_upper(adjacent,expected_adjacent[i])
            previous_right=pair_blocks[2].reshape(74,-1)
            tensor_error=sum(arb(r['stored_assembly_error_frobenius_upper']) for r in parts)+arb(final_add)
            # The tensor acts on a concatenated pair (factor 2); the cross
            # block acts on one left/right pair (factor 1).
            coefficient=assembly._float_upper(2*tensor_error+arb(cross_add))
            rows.append(dict(interval=i,components=parts,local_tensor_SHA256=_array_hash(local),
                local_covariances_SHA256=_array_hash(covariances),adjacent_covariance_SHA256=_array_hash(adjacent),
                saved_local_covariances_SHA256=_array_hash(expected_covariances[i]),
                saved_adjacent_covariance_SHA256=_array_hash(expected_adjacent[i]),
                local_covariance_reconstruction_difference_frobenius_upper=covariance_difference,
                adjacent_covariance_reconstruction_difference_frobenius_upper=adjacent_difference,
                final_addition_rounding_frobenius_upper=final_add,
                cross_block_addition_rounding_frobenius_upper=cross_add,
                local_uniform_quadratic_coefficient_upper=coefficient))
            if (i+1)%50==0:
                print(json.dumps(dict(certified_assembly_intervals=i+1)),flush=True)
        transport=causal_error.transport_local_errors(maps,
            np.asarray([r['local_uniform_quadratic_coefficient_upper'] for r in rows]))
    finally:
        ctx.prec=previous_precision
    coordinate._verified_inputs({'inputs':inputs})
    return dict(artifact='BHSM_N12_GATE7_STORED_PULLBACK_ASSEMBLY',
        scope='RECONSTRUCTED_LOCAL_TENSOR_ASSEMBLY_THROUGH_EXACT_STORED_CAUSAL_MAPS_ONLY',
        coverage=dict(intervals=370,nodes=371,complete=True),inputs=inputs,rows=rows,
        causal_maps_SHA256=_array_hash(maps),transport=transport,
        maximum_causal_assembly_error_coefficient_upper=transport['maximum_node_error_norm_upper'],
        covariance_reconstruction_mismatch_count=sum(
            r['local_covariance_reconstruction_difference_frobenius_upper']>0 or
            r['adjacent_covariance_reconstruction_difference_frobenius_upper']>0 for r in rows),
        validation_passed=True,claim_boundary=dict(stored_pullback_assembly_rounding_enclosed=True,
            saved_center_covariance_reconciliation_required=True,
            center_covariance_rounding_enclosed=False,physical_operand_errors_enclosed=False,
            physical_Hessian_error_enclosed=False,neighborhood_remainder_enclosed=False,
            Gate7_closed=False,FULL_BHSM_COMPLETE=False))


def main():
    payload=build_payload()
    RESULT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(maximum_causal_assembly_error_coefficient_upper=payload['maximum_causal_assembly_error_coefficient_upper'],
                         validation_passed=payload['validation_passed'])),flush=True)


if __name__=='__main__':main()
