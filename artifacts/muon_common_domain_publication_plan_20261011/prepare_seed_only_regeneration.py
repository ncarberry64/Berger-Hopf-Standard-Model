"""Optional setup for regeneration; never changes the source checkout.

This command has NOT been executed as part of the publication audit.
"""
from hashlib import sha256
import argparse
import ast
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def copy_path_audit():
    """Close selected tests and utilities without copying generated streams."""
    plan_path = HERE/'publication_plan.json'
    plan = json.loads(plan_path.read_text())
    original = set(plan['seed_only_regeneration_copy_paths'])
    selected_python = {row['path'] for row in plan['selected_files']
                       if row['path'].endswith('.py')}
    paths = original | selected_python | set(plan['selected_test_paths'])
    queue = list(paths)
    visited = set()
    while queue:
        name = queue.pop()
        if name in visited or not name.endswith('.py'):
            continue
        visited.add(name)
        # Preserve regular-package resolution in isolation; an installed
        # editable bhsm package otherwise wins over a copied namespace.
        parent = Path(name).parent
        while parent != Path('.'):
            package_init = parent/'__init__.py'
            if (ROOT/package_init).is_file() and package_init.as_posix() not in paths:
                paths.add(package_init.as_posix())
                queue.append(package_init.as_posix())
            parent = parent.parent
        tree = ast.parse((ROOT/name).read_text(encoding='utf8'))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                if node.level:
                    base = Path(name).parent
                    for _ in range(node.level-1):
                        base = base.parent
                    candidates = ([base/Path(module.replace('.', '/')).with_suffix('.py')]
                                  if module else
                                  [base/Path(a.name.replace('.', '/')).with_suffix('.py')
                                   for a in node.names])
                    modules = []
                else:
                    modules = [module]
            else:
                continue
            if not isinstance(node, ast.ImportFrom) or not node.level:
                candidates = [Path(base)/Path(module.replace('.', '/')).with_suffix('.py')
                              for module in modules for base in ('src', 'scripts', 'tests')]
            for candidate in candidates:
                if (ROOT/candidate).is_file() and candidate.as_posix() not in paths:
                    paths.add(candidate.as_posix())
                    queue.append(candidate.as_posix())
    files = []
    for name in sorted(paths):
        source = (ROOT/name).resolve()
        if ROOT not in source.parents or not source.is_file():
            raise ValueError('dependency path escaped its tree or is absent: '+name)
        files.append(dict(path=name, bytes=source.stat().st_size,
                          sha256=sha256(source.read_bytes()).hexdigest()))
    selected_expected = {row['path']: row['sha256'] for row in plan['selected_files']}
    conflicts = [row['path'] for row in files
                 if row['path'] in selected_expected and
                 row['sha256'] != selected_expected[row['path']]]
    if conflicts:
        raise ValueError('selected immutable source bytes changed: '+repr(conflicts))
    return dict(classification='ADDITIVE_REGENERATION_COPY_TEST_IMPORT_AUDIT',
                plan_sha256=sha256(plan_path.read_bytes()).hexdigest(),
                files=files, file_count=len(files), bytes=sum(row['bytes'] for row in files),
                added_paths=sorted(paths-original),
                added_import_closure_paths=sorted(paths-original-selected_python-set(plan['selected_test_paths'])),
                selected_test_files=len(plan['selected_test_paths']),
                selected_source_byte_conflicts=conflicts,
                raw_response_streams_added=False,
                publication_plan_modified=False,
                clean_checkout_regeneration_proved=False)

def prepare(destination, *, rebuild_coordinate_cache=False):
    target = Path(destination).resolve()
    if not target.is_absolute() or target.exists() or target == ROOT or ROOT in target.parents:
        raise ValueError('use a new absolute scratch directory outside the source checkout')
    plan = json.loads((HERE/'publication_plan.json').read_text())
    audit = copy_path_audit()
    paths = [row['path'] for row in audit['files']]
    if not rebuild_coordinate_cache:
        paths += [plan['coordinate_cache_reuse']['path'], plan['coordinate_cache_reuse']['owner_receipt']]
    target.mkdir(parents=True, exist_ok=False)
    copied = []
    for name in sorted(set(paths)):
        source = (ROOT/name).resolve(); dest = (target/name).resolve()
        if ROOT not in source.parents or target not in dest.parents or not source.is_file():
            raise ValueError('dependency path escaped its tree or is absent: '+name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        copied.append(dict(path=name, bytes=source.stat().st_size, sha256=sha256(source.read_bytes()).hexdigest()))
    receipt = dict(classification='COPIED_EXACT_DEPENDENCIES_TO_NEW_REGENERATION_SCRATCH',
                   source=str(ROOT), destination=str(target), files=copied,
                   source_checkout_modified=False, old_arrays_removed=False,
                   physical_or_clean_checkout_regeneration_proved=False,
                   copy_audit=audit,
                   reused_coordinate_cache=not rebuild_coordinate_cache)
    (target/'regeneration_setup.json').write_text(json.dumps(receipt, sort_keys=True, indent=2)+'\n', encoding='utf8')
    print(json.dumps(dict(files=len(copied), bytes=sum(x['bytes'] for x in copied), destination=str(target))))

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--destination', type=Path)
    p.add_argument('--rebuild-coordinate-cache', action='store_true')
    p.add_argument('--audit-only', action='store_true')
    a = p.parse_args()
    if a.audit_only:
        print(json.dumps(copy_path_audit(), sort_keys=True, indent=2))
    elif a.destination is None:
        p.error('--destination is required unless --audit-only is set')
    else:
        prepare(a.destination, rebuild_coordinate_cache=a.rebuild_coordinate_cache)
