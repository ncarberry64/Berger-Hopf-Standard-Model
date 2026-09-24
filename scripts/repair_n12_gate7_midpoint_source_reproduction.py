"""Rebuild only the fourteen raw source terms and dependent response record.

Both serial runs must have identical complete operands and exact output balls.
The original source files stay immutable. An overlay holds repaired terms;
unaffected terms remain in the already computed independent repeat directory.
"""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ROWS = (28, 30, 33, 36, 38, 41, 44, 46, 49, 52, 54, 57, 59, 61)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def evaluate(root, work, out):
    sys.path[:0] = [str(root/'scripts'), str(root/'src')]
    import numpy as np
    from flint import arb, arb_mat, ctx
    import certify_n12_gate7_coupled_endpoint_uniform_derivatives as engine
    import bhsm.interface
    bhsm.interface.__path__.insert(0, str(ROOT/'src/bhsm/interface'))
    from bhsm.interface.shared_action_taylor import Taylor, TaylorDomain
    from bhsm.interface.componentwise_weighted_response import enclose_response_rows
    from bhsm.interface.exact_arb_ball_restore import restore_exact_ball
    ctx.prec = 512
    ctx.threads = 1
    p = engine.p
    first = work/'interval14_midpoint14_base_taylor_first'
    repeat = work/'interval14_midpoint14_base_taylor_repeat_schedule'
    raw = [work/('interval14_midpoint14_raw_serial_'+suffix) for suffix in ('first', 'repeat')]
    originals = [json.loads((path/'record.json').read_bytes()) for path in (first, repeat)]
    sources = {}

    def read(path):
        sources[str(path.resolve())] = sha(path)
        return json.loads(path.read_bytes())

    comparisons = []
    for i in ROWS:
        name = f'response_{i:02d}_source'
        values = [read(path/(name+'.json')) for path in raw]
        inputs = [path/(name+'_inputs.json') for path in raw]
        if inputs[0].read_bytes() != inputs[1].read_bytes():
            raise ValueError('Complete raw inputs differ: '+name)
        if any(sha(path) != record['complete_input_SHA256'] for path, record in zip(inputs, values)):
            raise ValueError('Raw operand digest mismatch')
        if (raw[0]/(name+'.json')).read_bytes() != (raw[1]/(name+'.json')).read_bytes():
            raise ValueError('Raw serial output balls differ: '+name)
        if values[0]['values'] != read(first/(name+'.json'))['values']:
            raise ValueError('Serial raw result differs from original term: '+name)
        for path in inputs:
            sources[str(path.resolve())] = sha(path)
        comparisons.append(dict(term=name, complete_inputs_SHA256=sha(inputs[0]),
            exact_output_SHA256=sha(raw[0]/(name+'.json')), raw_bytes_identical=True,
            original_ball_reproduced_exactly=True))
    for path in first.glob('*.json'):
        if not path.name.startswith(('rayleigh', 'eigen_', 'response_')) or path.stem in {f'response_{i:02d}_source' for i in ROWS}:
            continue
        if path.read_bytes() != (repeat/path.name).read_bytes():
            raise ValueError('Unrelated action term differs: '+path.name)
        sources[str(path.resolve())] = sha(path)
        sources[str((repeat/path.name).resolve())] = sha(repeat/path.name)
    for key in ('eigenpair_error_upper_exact', 'eigenpair_proof', 'eigenvalue_predictor'):
        if originals[0][key] != originals[1][key]:
            raise ValueError('Previously reproduced eigenpair prerequisite differs')
    out.mkdir(exist_ok=False)
    for path in (Path(__file__), Path(restore_exact_ball.__code__.co_filename),
                 Path(enclose_response_rows.__code__.co_filename), first/'record.json', repeat/'record.json'):
        sources[str(path.resolve())] = sha(path)
    operands = work/'interval14_midpoint14_point_first'
    predictors = work/'interval14_midpoint14_seven_first'

    def load(folder, name):
        record = read(folder/'record.json')
        sources[str((folder/name).resolve())] = sha(folder/name)
        if sha(folder/name) != record['data_SHA256']:
            raise ValueError('Original raw operands changed')
        with np.load(folder/name, allow_pickle=False) as z:
            arrays = {k[:-6]: p.hs.restore_balls(z[k], z[k[:-6]+'_rad_q']) for k in z.files if k.endswith('_mid_q')}
        return record, arrays

    ore, a = load(operands, 'operands.npz')
    pre, s = load(predictors, 'predictors.npz')
    p.verify_sources(ore['binding'])
    if pre['stage'] != 'midpoint' or pre['interval'] != 14:
        raise ValueError('Original midpoint 14 required')
    results = []
    recovered_modes = {i: (7 if i < 8 else 2 if i in ROWS else 0) for i in range(62)}
    schedule_recovery = []
    for index, (cached, raw_path) in enumerate(zip((first, repeat), raw)):
        domain = TaylorDomain(pre['parameter_groups'], 249)
        ep = [arb(v) for v in pre['point_checks'][0]['target_midpoints_rational']]
        psi = [domain.affine(ep[i].mid(), [s['point_solve_3'][i,j].mid() for j in range(249)]) for i in range(61)]
        hard = [domain.affine(s['point_solve_0'][i,0].mid(), [s['point_solve_4'][i,j].mid() for j in range(249)]) for i in range(62)]
        eig = [arb(v) for v in originals[index]['eigenpair_error_upper_exact']]
        psi = [Taylor(domain, v.c, v.a, eig[i]) for i,v in enumerate(psi)]
        lv = [restore_exact_ball(m,r) for m,r in originals[index]['eigenvalue_predictor']]
        lam = Taylor(domain, lv[0], arb_mat(1,249,lv[1:-1]), eig[61])
        dot = lambda x,y: sum((v*w for v,w in zip(x,y,strict=True)), arb(0))
        modes = {}

        def action(i, kind, mask):
            name = f'response_{i:02d}_{kind}'
            selected = i in ROWS and kind == 'source'
            values = read((raw_path if selected else cached)/(name+'.json'))['values']
            # Rows 0..7 and these 14 source contractions were evaluated in
            # the producer process, with no save/reload before accumulation.
            exact = bool(mask & (1 << ('gradient','source','action').index(kind)))
            vv = [restore_exact_ball(m,r) if exact else arb(m)+arb(0,arb(r)) for m,r in values]
            modes[name] = 'exact in-memory ball' if exact else 'original outward cache reload'
            return Taylor(domain,vv[0],arb_mat(1,249,vv[1:-1]),vv[-1])

        def residual(i, mask):
            v = list(a['paired_rm'][i,:61])
            bottom = a['paired_rm'][i,61]
            source = action(i,'gradient',mask)-action(i,'source',mask)
            return (action(i,'action',mask)-lam*dot(v,hard[:61])+hard[61]*dot(v,psi)-source
                 +bottom*dot(psi,hard[:61]))
        forcing = np.array([residual(i,recovered_modes[i]).support() for i in range(62)], dtype=object)
        def enclose(forcing):
            return enclose_response_rows(np.array([arb(0)]*62,dtype=object),forcing,a['paired_radii'],a['paired_variation'])[1]
        proof = enclose(forcing)
        if index == 0:
            # Recover only the historical serialization schedule. Every one
            # of the eight candidates is a rigorous evaluation of the same
            # expression with the same saved balls. No operand, equation,
            # radius target, or physical parameter is changed or fitted.
            # Equality below is exact rational equality, never a tolerance.
            target = originals[0]['response_proof']
            for i in range(62):
                if proof['component_radii_upper_rational'][i] == target['component_radii_upper_rational'][i]:
                    continue
                matches = []
                for mask in range(8):
                    trial = forcing.copy()
                    trial[i] = residual(i,mask).support()
                    candidate = enclose(trial)
                    if (candidate['component_radii_upper_rational'][i] == target['component_radii_upper_rational'][i]
                            and all(candidate[k] == target[k] for k in ('weighted_error_upper_rational','weighted_residual_upper_rational'))):
                        matches.append(mask)
                if not matches:
                    raise ValueError('No exact historical cache schedule recovered for row '+str(i))
                recovered_modes[i] = matches[0]
                schedule_recovery.append(dict(response_row=i, exact_matching_masks=matches,
                    selected_mask=matches[0], selected_by='fixed lowest-mask order after exact equality'))
                forcing[i] = residual(i,matches[0]).support()
                proof = enclose(forcing)
            # Re-evaluate with the now fixed schedule; the second independent
            # input set uses this schedule directly and performs no search.
            forcing = np.array([residual(i,recovered_modes[i]).support() for i in range(62)],dtype=object)
            proof = enclose(forcing)
        values = [arb(v) for v in proof['component_radii_upper_rational']]
        result = dict(originals[0], response_error_upper_exact=[str(v.fmpq()) for v in values],
                      response_proof=proof, response_max_error=float(max(values)))
        results.append(result)
        (out/f'rebuilt_record_{index}.json').write_bytes(p.geometry.encoded(result))
    if results[0] != results[1]:
        raise ValueError('Independent repaired response accumulations differ')
    if results[0] != originals[0]:
        (out/'accumulation_difference.json').write_bytes(p.geometry.encoded(dict(
            changed_fields=[k for k in results[0] if results[0][k] != originals[0][k]],
            repaired_record=results[0], certification_resumed=False)))
        raise ValueError('Repaired exact accumulation differs from original; no repair accepted')
    for i in ROWS:
        name = f'response_{i:02d}_source'
        original = read(first/(name+'.json'))
        original['values'] = read(raw[1]/(name+'.json'))['values']
        (out/(name+'.json')).write_bytes(p.geometry.encoded(original))
        if sha(out/(name+'.json')) != sha(first/(name+'.json')):
            raise ValueError('Rebuilt source record is not byte-identical')
    (out/'record.json').write_bytes(p.geometry.encoded(results[1]))
    if sha(out/'record.json') != sha(first/'record.json'):
        raise ValueError('Rebuilt aggregate record is not byte-identical')
    receipt = dict(algorithm='MIDPOINT14_SERIAL_RAW_EXACT_REPAIR_RECEIPT_V1',
        comparisons=comparisons, response_evaluation_modes=modes,
        recovered_serialization_schedule=recovered_modes,
        exact_schedule_recovery=schedule_recovery,
        cache_schedule_identifies_equivalent_rigorous_evaluations=True,
        complete_operand_hashes_equal=True, raw_ball_bytes_identical=True,
        canonical_coarsening_used=False, numerical_tolerance_used=False,
        repaired_base_record_SHA256=sha(out/'record.json'),
        source_term_repair_SHA256={f'response_{i:02d}_source':sha(out/f'response_{i:02d}_source.json') for i in ROWS},
        unchanged_repeat_directory=str(repeat), original_first_directory=str(first),
        original_domain_unchanged=True, interval13_recomputed=False,
        transverse_ledger_debited=False, full_entry_certified=False,
        actual_execution_source_SHA256=sources)
    if any(sha(Path(path)) != digest for path,digest in sources.items()):
        raise ValueError('Repair input changed during assembly')
    (out/'repair_receipt.json').write_bytes(p.geometry.encoded(receipt))
    print(json.dumps({'repaired_terms':len(ROWS),'base_record_byte_identical':True,
                      'canonical_coarsening_used':False}),flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for key in ('evidence-root','work','out'):
        parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args()
    evaluate(args.evidence_root.resolve(),args.work.resolve(),args.out.resolve())
