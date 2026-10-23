"""Source-pinned investigation priorities; no classification or physical fitting."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

PROGRAM=Path(__file__).resolve().parent/'theory/PRIMARY_TARGET_PROGRAM.json'
PROGRAM_SHA256='175c4b11279bb0397b48eb76d38b556b30eb246ef005bb1cb1cfab510dd32f48'


def target_program():
    raw=PROGRAM.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PROGRAM_SHA256:
        raise ValueError('Primary-target program differs from the reviewed source; no priority or publication status was admitted')
    value=json.loads(raw)
    if value.get('schema')!='bhtracker.primary_target_program.v1':
        raise ValueError('Unsupported target-program schema')
    primary=value['primary_investigation_target']
    if (primary['investigation_category']!='Potential black hole'
            or any(v is not None for v in primary['engine_measurements'].values())
            or value['publication_gate']['ready'] is not False
            or value['known_black_hole_validation_benchmark']['independent_engine_recovery_accepted'] is not False):
        raise ValueError('Target-program evidence and publication qualifications are inconsistent')
    return deepcopy({**value,'program_sha256':PROGRAM_SHA256})
