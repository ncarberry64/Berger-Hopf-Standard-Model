"""Measure sparse collision-impact cues from the local Race The Sun MP3.

Offline authoring dependencies: numpy, scipy, imageio-ffmpeg (or --ffmpeg).
Run from the repository root:
  python museum/scripts/analyze-collision-cues.py
  python museum/scripts/analyze-collision-cues.py --check

Each cue is a measured attack start. Strongest-neighbour exclusion leaves
reading time between impacts; no tempo grid or repeated interval creates cues.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy import ndimage, signal


ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "public" / "audio" / "scott-buckley-race-the-sun.mp3"
OUTPUT = ROOT / "lib" / "collision-cues.json"
SAMPLE_RATE = 11025
ANALYSIS_STEP = 0.005
MINIMUM_CUE_GAP = 6.0
BANDS = [(35, 180), (180, 2000), (2000, 5000)]
WEIGHTS = [0.5, 0.25, 0.25]


def analyze(ffmpeg):
    decoded = subprocess.run(
        [ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-i", str(AUDIO),
         "-map", "0:a:0", "-ac", "1", "-ar", str(SAMPLE_RATE),
         "-f", "f32le", "pipe:1"],
        check=True, capture_output=True,
    )
    samples = np.frombuffer(decoded.stdout, dtype="<f4")
    duration = len(samples) / SAMPLE_RATE
    times = np.arange(0, duration, ANALYSIS_STEP)
    sample_times = np.arange(len(samples)) / SAMPLE_RATE
    energies = []
    rises = []
    normalization = []
    for band in BANDS:
        # Forward/backward filtering and centered smoothing avoid introducing
        # filter delay or an assumed lead relative to the local media clock.
        sections = signal.butter(4, band, btype="bandpass", fs=SAMPLE_RATE, output="sos")
        filtered = signal.sosfiltfilt(sections, samples)
        rms = np.sqrt(ndimage.gaussian_filter1d(
            filtered * filtered, SAMPLE_RATE * 0.008,
        ))
        energy = np.interp(times, sample_times, rms)
        rise = np.maximum(energy - np.interp(times - 0.06, times, energy), 0)
        scale = max(float(np.percentile(rise, 98)), 1e-9)
        energies.append(energy / scale)
        rises.append(rise / scale)
        normalization.append(round(scale, 9))
    energy = sum(weight * values for weight, values in zip(WEIGHTS, energies))
    strength = sum(weight * values for weight, values in zip(WEIGHTS, rises))
    candidates, _ = signal.find_peaks(
        strength, height=0.2, prominence=0.15, distance=50,
    )

    # Curation uses actual mixed-recording accents. A stronger neighbouring
    # orchestral/drum attack can replace a weaker pulse; no missing pulse is
    # filled in, and the quiet outro intentionally supplies no extra impacts.
    selected = []
    for index in sorted(candidates, key=lambda i: (-strength[i], i)):
        if all(abs(times[index] - times[other]) >= MINIMUM_CUE_GAP for other in selected):
            selected.append(index)
    selected.sort()

    def attack_start(index, fraction):
        # Measure the local rising front instead of taking the later crest.
        # The baseline is the 20th percentile from 120 to 60 ms before the
        # candidate. Each threshold crossing is interpolated from the samples,
        # rather than subtracting a constant latency correction.
        baseline = float(np.percentile(energy[max(0, index - 24):max(1, index - 12)], 20))
        threshold = baseline + fraction * (energy[index] - baseline)
        start = max(0, index - 30)
        crossings = np.flatnonzero(
            (energy[start:index] < threshold) & (energy[start + 1:index + 1] >= threshold)
        )
        if not len(crossings):
            raise ValueError(f"No measured attack crossing near {times[index]:.3f}s")
        before = start + int(crossings[-1])
        portion = (threshold - energy[before]) / (energy[before + 1] - energy[before])
        return round(float(times[before] + portion * ANALYSIS_STEP), 3)

    evidence = []
    for index in selected:
        evidence.append({
            "timeSeconds": attack_start(index, 0.1),
            "fivePercentRiseSeconds": attack_start(index, 0.05),
            "twentyPercentRiseSeconds": attack_start(index, 0.2),
            "riseCrestSeconds": round(float(times[index]), 3),
            "normalizedAttackStrength": round(float(strength[index]), 3),
            "normalizedBandRise": [round(float(values[index]), 3) for values in rises],
        })
    impact_times = [row["timeSeconds"] for row in evidence]
    gaps = np.diff(impact_times)
    assert len(impact_times) >= 2
    assert np.all(gaps >= MINIMUM_CUE_GAP)
    return {
        "slideId": "science-decays",
        "trackTitle": "Race The Sun",
        "source": "./audio/scott-buckley-race-the-sun.mp3",
        "audioSha256": hashlib.sha256(AUDIO.read_bytes()).hexdigest(),
        "durationSeconds": round(duration, 6),
        "method": "Local MP3 decoded mono at 11025 Hz. Fourth-order Butterworth bandpasses at 35-180, 180-2000 and 2000-5000 Hz are applied forward/backward (zero group delay), followed by centered Gaussian RMS with 8 ms sigma. At 5 ms analysis steps, each band's positive 60 ms RMS rise is divided by that band's whole-recording 98th-percentile rise. The combined attack score weights low percussion 0.5, orchestral range 0.25 and bright range 0.25. Candidate crests require score>=0.2, prominence>=0.15 and separation>=250 ms. Strongest-neighbour exclusion retains actual strong accents with at least six seconds between crests for approach, reveal and inspection. The impact is the last 10% crossing of the combined local RMS rise before the crest, using a 20th-percentile baseline from 120 to 60 ms before the crest and linear interpolation; 5% and 20% crossings document timing sensitivity. No BPM, tempo grid, fixed interval, synthetic opening event or guessed latency lead is used. Presentation timing only, not scientific data.",
        "confidence": {
            "timing": "Measured recorded-attack starts; 5 ms analysis resolution with per-impact threshold sensitivity below",
            "instrument": "Mixed low percussion and orchestral rises; isolated instrument stems are unavailable",
            "selection": "Sparse strongest-neighbour accents leave reading time; weaker intervening notes and the quiet outro do not create extra collisions",
        },
        "analysisStepSeconds": ANALYSIS_STEP,
        "minimumCueGapSeconds": MINIMUM_CUE_GAP,
        "fixedTempoBpm": None,
        "bandRangesHz": [list(band) for band in BANDS],
        "bandWeights": WEIGHTS,
        "bandRiseNormalizationPercentile": 98,
        "bandRiseNormalizationRms": normalization,
        "impactTimesSeconds": impact_times,
        "selectedAttackEvidence": evidence,
        "summary": {
            "candidateCount": int(len(candidates)),
            "selectedCount": len(impact_times),
            "medianCueGapSeconds": round(float(np.median(gaps)), 3),
            "minimumCueGapSeconds": round(float(np.min(gaps)), 3),
            "maximumCueGapSeconds": round(float(np.max(gaps)), 3),
            "firstImpactSeconds": impact_times[0],
            "holdFinalEventAfterSeconds": impact_times[-1],
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ffmpeg", help="Path to an existing local FFmpeg executable")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true", help="Verify existing JSON without rewriting it")
    args = parser.parse_args()
    if args.ffmpeg:
        ffmpeg = args.ffmpeg
    else:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    result = analyze(ffmpeg)
    encoded = (json.dumps(result, indent=2, allow_nan=False) + "\n").encode("utf-8")
    assert len(encoded) < 200 * 1024
    if args.check:
        if not args.output.exists() or args.output.read_bytes() != encoded:
            raise SystemExit("Collision analysis differs from saved JSON; regenerate it.")
        print("Collision analysis reproduced identical bytes.")
    else:
        args.output.write_bytes(encoded)
    print(f'{len(result["impactTimesSeconds"])} measured impact cues; {len(encoded):,} bytes')
    print(f'Impact times: {result["impactTimesSeconds"]}')
    print(f'JSON SHA256: {hashlib.sha256(encoded).hexdigest()}')


if __name__ == "__main__":
    main()
