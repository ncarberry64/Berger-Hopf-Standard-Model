"""Fixed installed provider roles; no caller source execution or bare aliases."""
import importlib
from pathlib import Path
import sys
import types


def check_live_source(module):
    """Check loaded local function code against the pinned file on this runtime."""
    path = Path(module.__file__).resolve()
    compiled = compile(path.read_bytes(), str(path), 'exec', dont_inherit=True,
                       optimize=sys.flags.optimize)
    codes = {}
    def collect(code):
        for value in code.co_consts:
            if isinstance(value, types.CodeType):
                codes[value.co_qualname] = value
                collect(value)
    collect(compiled)
    def same_code(expected, actual):
        # Windows can import the pinned file through its 8.3 spelling. Keep
        # source identity strict while accepting aliases of that same file.
        try:
            if Path(actual.co_filename).resolve(strict=True) != path:
                return False
        except (OSError, RuntimeError, ValueError):
            return False
        fields = ('co_argcount', 'co_posonlyargcount', 'co_kwonlyargcount',
                  'co_nlocals', 'co_stacksize', 'co_flags', 'co_code',
                  'co_names', 'co_varnames', 'co_name', 'co_qualname',
                  'co_firstlineno', 'co_linetable', 'co_exceptiontable',
                  'co_freevars', 'co_cellvars')
        if any(getattr(expected, n) != getattr(actual, n) for n in fields):
            return False
        if len(expected.co_consts) != len(actual.co_consts):
            return False
        for left, right in zip(expected.co_consts, actual.co_consts):
            if isinstance(left, types.CodeType) or isinstance(right, types.CodeType):
                if not (isinstance(left, types.CodeType) and isinstance(right, types.CodeType)
                        and same_code(left, right)):
                    return False
            elif left != right:
                return False
        return True
    def inspect(value, expected_name=None):
        if isinstance(value, types.FunctionType) and (expected_name in codes or value.__module__ == module.__name__):
            # Python 3.14 stores the compiler-generated annotation function
            # under __annotate_func__, while its actual source qualname is
            # __annotate__. Prefer a declared member name, then its qualname.
            expected = codes.get(expected_name) or codes.get(value.__qualname__)
            # Marshal encodings can differ solely in string-intern/reference
            # layout despite equal code. Compare the actual code fields instead.
            if expected is None or not same_code(expected, value.__code__):
                raise ValueError('Loaded provider function differs: ' + value.__qualname__)
        elif isinstance(value, type) and (expected_name in codes or value.__module__ == module.__name__):
            if value.__module__ != module.__name__:
                raise ValueError('Loaded provider class differs: ' + str(expected_name))
            for name, item in vars(value).items():
                if (hasattr(value, '__dataclass_fields__') and name in
                        {'__init__', '__repr__', '__eq__', '__setattr__', '__delattr__', '__hash__'} and
                        value.__qualname__ + '.' + name not in codes):
                    continue  # Standard dataclass-generated glue, not a source function.
                if isinstance(item, (classmethod, staticmethod)):
                    item = item.__func__
                if isinstance(item, property):
                    for function in (item.fget, item.fset, item.fdel):
                        if function is not None: inspect(function, value.__qualname__ + '.' + name)
                    continue
                inspect(item, value.__qualname__ + '.' + name)
    for name, value in vars(module).items():
        inspect(value, name)


def load_provider(path, expected):
    from ..known_system_v3 import verify_sources
    manifest = verify_sources()
    path = Path(path).resolve()
    root = Path(__file__).resolve().parent
    roles = {'core_snapshot_v2.py', 'student_ou.py', 'student_ou_banded.py'}
    records = {r['filename']: r for r in manifest['files']}
    if (path.parent != root or path.name not in roles or
            records[path.name]['sha256'] != expected):
        raise ValueError('Only the pinned installed provider roles are supported')
    module = importlib.import_module('.' + path.stem, __package__)
    if (Path(module.__file__).resolve() != path or module.__spec__ is None or
            module.__spec__.name != __package__ + '.' + path.stem):
        raise ValueError('Unexpected qualified provider module')
    check_live_source(module)
    verify_sources()
    return module
