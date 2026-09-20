"""Run the bounded interval-14 reproduction chain and fail closed on differences.

Every numerical job uses a fresh output directory and a fresh Python process. Frozen
point proposals are reused; no interval-13 computation is invoked.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2)+'\n').encode()


def evaluate(root, work, workers):
    repo = Path(__file__).resolve().parents[1]
    evidence = root.resolve()
    work = work.resolve()
    comparisons = []
    commands = []
    driver_hash = sha(Path(__file__))

    def folder(name):
        name = {'endpoint15_base_taylor_repeat': 'endpoint15_base_taylor_repeat_serial',
                'midpoint14_base_taylor_repeat': 'midpoint14_base_taylor_repeat_schedule'}.get(name, name)
        return work / ('interval14_'+name)

    def run(script, **kwargs):
        argv = [sys.executable, str(repo/'scripts'/script), '--evidence-root', str(evidence)]
        for key, value in kwargs.items():
            argv.extend(['--'+key.replace('_', '-'), str(value)])
        commands.append(argv)
        print(json.dumps({'starting': script, 'out': str(kwargs.get('out'))}), flush=True)
        subprocess.run(argv, cwd=repo, check=True)

    def verify_sources(record):
        for path, digest in record.get('input_source_SHA256', {}).items():
            if sha(Path(path)) != digest:
                raise ValueError('Proof source changed: '+path)

    def compare_files(first, repeat, wrapper=False):
        a, b = first.read_bytes(), repeat.read_bytes()
        if wrapper:
            x, y = json.loads(a), json.loads(b)
            verify_sources(x)
            verify_sources(y)
            old = str((repeat.parent/'refinement.json').resolve())
            new = str((first.parent/'refinement.json').resolve())
            y['input_source_SHA256'][new] = y['input_source_SHA256'].pop(old)
            if x != y:
                raise ValueError('Non-provenance wrapper difference: '+str(first))
        elif a != b:
            raise ValueError('Numerical reproduction differs: '+str(first))
        comparisons.append(dict(first=str(first), repeat=str(repeat),
            first_SHA256=sha(first), repeat_SHA256=sha(repeat),
            byte_identical=a == b, only_refinement_location_differs=wrapper and a != b))

    def compare_folder(name, refined=False):
        first, repeat = folder(name+'_first'), folder(name+'_repeat')
        for path in sorted(first.glob('*.json')):
            data = json.loads(path.read_bytes())
            if path.name in ('record.json', 'sources.json', 'refinement.json') or ('binding' in data and 'values' in data):
                compare_files(path, repeat/path.name, refined and path.name == 'record.json')
        verify_sources(json.loads((first/'record.json').read_bytes()))
        verify_sources(json.loads((repeat/'record.json').read_bytes()))

    # Arb's public radius constructor adds outward rounding on serialization.
    # Match the original serial/cache boundary, not just operation order inside
    # each contraction. The failed all-parallel trial is retained separately.
    def reproduce_base(stage):
        common = dict(operands=folder(stage+'_point_first'), predictors=folder(stage+'_seven_first'))
        if stage == 'midpoint14':
            original = folder(stage+'_base_taylor_first')
            target = folder(stage+'_base_taylor_repeat')
            target.mkdir(exist_ok=False)
            sources = json.loads((original/'sources.json').read_bytes())
            if any(sha(Path(path)) != digest for path, digest in sources.items()):
                raise ValueError('Original base sources changed')
            (target/'sources.json').write_bytes((original/'sources.json').read_bytes())
            original_receipt = json.loads((original/'parallel_response_receipt.json').read_bytes())
            expected = {f'response_{i:02d}_{kind}' for i in range(8, 62)
                        for kind in ('gradient', 'source', 'action')}
            if set(original_receipt['scalar_term_SHA256']) != expected:
                raise ValueError('Original midpoint execution boundary changed')
            run('prefetch_n12_gate7_interval14_base_response.py', **common,
                out=target, start_row=8, workers=workers)
        run('certify_n12_gate7_interval14_base_taylor.py', **common,
            out=folder(stage+'_base_taylor_repeat'))

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(reproduce_base, stage) for stage in ('endpoint15', 'midpoint14')]
        for future in futures:
            future.result()
    for stage in ('endpoint15', 'midpoint14'):
        compare_folder(stage+'_base_taylor')

    common = dict(operands=folder('endpoint15_point_first'), predictors=folder('endpoint15_seven_first'),
        base=folder('endpoint15_base_taylor_first')/'record.json')
    run('certify_n12_gate7_interval14_direction_taylor.py', **common,
        out=folder('endpoint15_direction_taylor_repeat'), workers=workers)
    compare_folder('endpoint15_direction_taylor')
    run('refine_n12_gate7_interval14_descriptor_taylor.py', **common,
        direction=folder('endpoint15_direction_taylor_first')/'record.json',
        adjoint=folder('endpoint_descriptor_adjoint_first.json'),
        out=folder('endpoint_descriptor_refined_repeat'), workers=workers)
    compare_folder('endpoint_descriptor_refined', refined=True)

    common = dict(operands=folder('midpoint14_point_first'), predictors=folder('midpoint14_seven_first'),
        base=folder('midpoint14_base_taylor_first')/'record.json')
    run('certify_n12_gate7_interval14_shared_tail_taylor.py', **common,
        endpoint=folder('endpoint_descriptor_refined_first')/'record.json',
        out=folder('midpoint14_refined_chain_repeat'), workers=workers)
    compare_folder('midpoint14_refined_chain')
    run('refine_n12_gate7_interval14_midpoint_scalar_taylor.py', **common,
        direction=folder('midpoint14_refined_chain_first')/'record.json',
        adjoint=folder('midpoint_scalar_adjoint_first.json'),
        out=folder('midpoint_scalar_refined_repeat'), workers=workers)
    compare_folder('midpoint_scalar_refined', refined=True)
    run('assemble_n12_gate7_interval14_entry_taylor.py',
        endpoint=folder('endpoint_descriptor_refined_first')/'record.json',
        midpoint=folder('midpoint14_refined_chain_first')/'record.json',
        midpoint_scalar=folder('midpoint_scalar_refined_first')/'record.json',
        budget=folder('entry_budget_first.json'), jet=folder('entry_first_jet_first.json'),
        out=folder('entry_assembly_repeat.json'))
    compare_files(folder('entry_assembly_first.json'), folder('entry_assembly_repeat.json'))
    result = json.loads(folder('entry_assembly_first.json').read_bytes())
    verify_sources(result)
    if not result['strict_entry_target_pass'] or not result['strict_transport_allocation_pass']:
        raise ArithmeticError('Strict entry and transport targets must both pass')
    if sha(Path(__file__)) != driver_hash:
        raise ValueError('Reproduction driver changed during execution')
    receipt = dict(algorithm='INTERVAL14_ENTRY_INDEPENDENT_PROCESS_REPRODUCTION_V1',
        interval=14, output_coordinate=73, input_coordinate=14,
        independent_process_recomputation=True, comparisons=comparisons,
        numerical_artifacts_byte_identical=True, wrapper_provenance_differences_explicit=True,
        commands=commands, original_domain_unchanged=True, interval13_recomputed=False,
        driver_SHA256=driver_hash, Gate7_closed=False, transverse_ledger_debited=False)
    for suffix in ('first', 'repeat'):
        with folder('entry_reproduction_'+suffix+'.json').open('xb') as stream:
            stream.write(encoded(receipt))
    print(json.dumps({'independent_reproduction_completed': True,
        'comparison_count': len(comparisons), 'transverse_ledger_debited': False}), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=10)
    args = parser.parse_args()
    evaluate(args.evidence_root, args.work, args.workers)
