"""Render the two predeclared archival follow-ups from saved fits; never refit."""
import argparse
import json
from pathlib import Path
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

PAPER = Path(__file__).resolve().parents[1]
REPO = PAPER.parents[1]
product = REPO / 'products/blackhole_tracker'
if not product.is_dir():
    product = REPO / 'product'
sys.path.insert(0, str(product))
from bhtracker.observations import UnresolvedPhotometry

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--pilot-output', type=Path, required=True)
args = parser.parse_args()
for event in ['OGLE3-ULENS-0585', 'OGLE3-ULENS-3092']:
    result = json.loads((args.pilot_output / 'events' / event / 'baseline.json').read_text(encoding='utf8'))
    data = UnresolvedPhotometry.from_dict(result['dataset_input'])
    if data.sha256 != result['input_sha256']:
        raise ValueError('saved native source hash changed: ' + event)
    order = np.argsort(data.times, kind='stable')
    fig, axes = plt.subplots(2, 1, figsize=(8, 4.5), sharex=True,
                             gridspec_kw={'height_ratios': [2, 1]}, layout='constrained')
    axes[0].errorbar(data.times, data.magnitudes, yerr=data.errors, fmt='.', ms=2,
                     alpha=.45, lw=.35, color='#32658b', label='All native rows with published errors')
    axes[0].plot(data.times[order], np.asarray(result['predictions_magnitude'])[order],
                  color='#a24820', lw=1, label='Frozen PSPL fit')
    axes[0].invert_yaxis()
    axes[0].set(ylabel='Apparent magnitude', title=event + ' | actual observations; mass unresolved')
    axes[0].legend(fontsize=7, frameon=False)
    axes[1].plot(data.times, result['standardized_residuals'], '.', ms=2, alpha=.6)
    axes[1].axhline(0, color='.4', lw=.7)
    axes[1].set(ylabel='Residual / native error', xlabel='HJD - 2450000 (days); native clock scale unspecified')
    fig.savefig(PAPER / 'figures' / (event + '_native.pdf'))
    plt.close(fig)
