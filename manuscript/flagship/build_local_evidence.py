"""Render already-reviewed local numerical evidence; no derivative evaluations."""
from fractions import Fraction
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
REVISION = '68a185556d786fc5e13ff533c358f1cbfaaf074f'


def retained(name):
    path = 'artifacts/flagship_integration/' + name + '.json'
    stored = subprocess.check_output(['git', 'show', REVISION + ':' + path], cwd=ROOT)
    local = (ROOT / path).read_bytes().replace(b'\r\n', b'\n')
    if local != stored.replace(b'\r\n', b'\n'):
        raise RuntimeError('Manuscript source differs from reviewed revision: ' + path)
    return json.loads(stored)


d = retained('BHSM_N12_GATE7_MIDPOINT_AND_BOOTSTRAP_INTEGRATION_20260913')
incidence = json.loads((Path(__file__).resolve().parent /
                       'generated/stored_margin_source.json').read_text())
if (d['Gate7_closed'] or d['FULL_BHSM_COMPLETE'] or d['measured_data_used']
        or d['interval'] != 13 or d['trial_column'] != 14):
    raise RuntimeError('Local evidence scope changed')
values = {}
for side, label in [('left', 'Left'), ('right', 'Right')]:
    report = d['midpoint'][side]['report']
    values['MidpointBefore' + label] = report['previous_maximum_radius']
    values['MidpointAfter' + label] = report['selected_maximum_radius']
for column, label in [('DL', 'Left'), ('DR', 'Right')]:
    values['LocalBefore' + label] = d['midpoint_only_local']['report']['columns'][column]['previous_maximum_radius']
    values['LocalAfter' + label] = d['local']['report']['columns'][column]['selected_maximum_radius']
witness = incidence['witness']
r = list(map(Fraction, witness['radius']))
c = incidence['coefficients']
for i in range(2):
    rhs = (Fraction(c['Y'][i]) + sum(Fraction(c['Z1'][i][j])*r[j] for j in range(2))
           + Fraction(c['central_quadratic'][i])*r[0]**2
           + 2*Fraction(c['mixed_quadratic'][i])*r[0]*r[1]
           + Fraction(c['transverse_quadratic'][i])*r[1]**2)
    if (rhs != Fraction(witness['exact_rhs'][i])
            or r[i]-rhs != Fraction(witness['exact_margin'][i]) or r[i]-rhs <= 0):
        raise RuntimeError('Exact stored-polynomial witness does not replay')
for i, label in enumerate(['Longitudinal', 'Transverse']):
    values['TrialRadius' + label] = witness['radius'][i]
    values['StoredMargin' + label] = float(Fraction(witness['exact_margin'][i]))


def tex(value):
    mantissa, *exponent = format(value, '.9g').split('e')
    return mantissa + (r'\times10^{' + str(int(exponent[0])) + '}' if exponent else '')


output = Path(__file__).resolve().parent / 'generated/local_values.tex'
output.write_text('% Local refinement revision: ' + REVISION + '\n'
                  '% Stored margins: exact replay of stored_margin_source.json\n' + ''.join(
    '\\newcommand{\\' + key + '}{' + tex(value) + '}\n' for key, value in values.items()
), encoding='utf-8')
print('Generated 12 inputs: reviewed local evidence and exact polynomial replay; no derivatives rerun.')
