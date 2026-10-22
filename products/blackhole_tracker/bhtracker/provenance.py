"""Content-based provenance works in installed wheels without a Git checkout."""
from functools import lru_cache
import hashlib
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path
import platform

VERSION='0.2.0rc2'

@lru_cache(maxsize=1)
def software_provenance():
    root=Path(__file__).resolve().parent
    files={str(p.relative_to(root)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
           for p in sorted(root.rglob('*')) if p.is_file() and
           '__pycache__' not in p.parts and p.suffix in ('.py','.json','.html','.css','.js','.tex')}
    dependencies={}
    for name in ('numpy','scipy','matplotlib'):
        try:dependencies[name]=version(name)
        except PackageNotFoundError:dependencies[name]='unavailable'
    return {'product_version':VERSION,'python':platform.python_version(),
            'dependencies':dependencies,'package_files_sha256':files,
            'source_identity':'SHA-256 of installed package contents; the release receipt records its reviewed Git commit'}
