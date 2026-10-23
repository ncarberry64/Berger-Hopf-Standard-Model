"""Find measured, sparse low-piano chapter cues in Time and Space.

Offline authoring dependencies: numpy, scipy, imageio-ffmpeg (or --ffmpeg).
Run from the repository root:
  python museum/scripts/analyze-exhibit3-chapters.py
  python museum/scripts/analyze-exhibit3-chapters.py --check

The source is the local museum MP3. Cues mark actual strong deep-note attacks,
with a readable minimum spacing. They are not a tempo grid or a speed envelope.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy import ndimage, signal


ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "public" / "audio" / "scott-buckley-time-and-space.mp3"
OUTPUT = ROOT / "lib" / "exhibit3-chapters.json"
SAMPLE_RATE = 11025
ANALYSIS_STEP = 0.005
MINIMUM_CUE_GAP = 6.0


def analyze(ffmpeg):
    decoded = subprocess.run(
        [ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-i", str(AUDIO),
         "-map", "0:a:0", "-ac", "1", "-ar", str(SAMPLE_RATE),
         "-f", "f32le", "pipe:1"],
        check=True, capture_output=True,
    )
    samples = np.frombuffer(decoded.stdout, dtype="<f4")
    duration = len(samples) / SAMPLE_RATE
    # The deep component separates the phrase notes from most of the denser
    # 80-160 Hz activity later in the track. Forward/backward filtering avoids
    # group delay; centered smoothing keeps timestamps aligned with media time.
    sections = signal.butter(4, [30, 80], btype="bandpass", fs=SAMPLE_RATE, output="sos")
    deep = signal.sosfiltfilt(sections, samples)
    rms = np.sqrt(ndimage.gaussian_filter1d(deep * deep, SAMPLE_RATE * 0.01))
    times = np.arange(0, duration, ANALYSIS_STEP)
    energy = np.interp(times, np.arange(len(samples)) / SAMPLE_RATE, rms)
    scale = max(float(np.percentile(energy, 95)), 1e-9)
    energy /= scale
    preceding = np.concatenate((np.full(16, energy[0]), energy[:-16]))
    rise = ndimage.gaussian_filter1d(np.maximum(energy - preceding, 0), 2)
    candidates, _ = signal.find_peaks(rise, height=0.8, prominence=0.3, distance=60)

    # Strongest-neighbour suppression is a presentation curation rule. Every
    # retained time remains a measured attack; no weak/missing note is filled
    # in and no nominal eight-second interval is used to generate timestamps.
    selected = []
    for index in sorted(candidates, key=lambda i: (-rise[i], i)):
        if all(abs(times[index] - times[other]) >= MINIMUM_CUE_GAP for other in selected):
            selected.append(index)
    selected.sort()

    def attack_start(index, fraction):
        # Backtrack from the rising-energy crest to the last crossing of a
        # fraction of its local RMS rise. This corrects the measured crest's
        # 30-60 ms delay without subtracting a guessed constant lead.
        baseline = float(np.percentile(energy[max(0, index - 40):max(1, index - 20)], 20))
        threshold = baseline + fraction * (energy[index] - baseline)
        start = max(0, index - 24)
        crossings = np.flatnonzero(
            (energy[start:index] < threshold) & (energy[start + 1:index + 1] >= threshold)
        )
        if not len(crossings):
            raise ValueError(f"No measured attack-start crossing near {times[index]:.3f}s")
        before = start + int(crossings[-1])
        fraction_of_step = (threshold - energy[before]) / (energy[before + 1] - energy[before])
        return round(float(times[before] + fraction_of_step * ANALYSIS_STEP), 3)

    evidence = []
    for index in selected:
        evidence.append({
            "timeSeconds": attack_start(index, 0.1),
            "fivePercentRiseSeconds": attack_start(index, 0.05),
            "twentyPercentRiseSeconds": attack_start(index, 0.2),
            "deepRiseCrestSeconds": round(float(times[index]), 3),
            "normalizedDeepRise": round(float(rise[index]), 3),
        })
    cue_times = [row["timeSeconds"] for row in evidence]
    gaps = np.diff(cue_times)
    return {
        "slideId": "berger-hopf",
        "trackTitle": "Time and Space",
        "source": "./audio/scott-buckley-time-and-space.mp3",
        "audioSha256": hashlib.sha256(AUDIO.read_bytes()).hexdigest(),
        "durationSeconds": round(duration, 6),
        "method": "Local MP3 decoded mono at 11025 Hz. A fourth-order Butterworth 30-80 Hz bandpass is applied forward/backward (zero group delay), followed by centered Gaussian RMS with 10 ms sigma. At 5 ms analysis steps, positive 80 ms RMS rises are normalized to the recording's 95th-percentile deep RMS; candidate crests require height>=0.8 and prominence>=0.3. Strongest-neighbour suppression retains measured attacks at least six seconds apart for readable chapter changes. Each cue backtracks its crest to the last crossing of 10% of the local RMS rise; 5% and 20% crossings document threshold sensitivity. No tempo grid, synthetic fill, repeated timer, fixed lead, or speed modulation is used. Presentation cues only, not scientific data.",
        "confidence": {
            "timing": "Measured low-note attack starts; 5 ms analysis resolution, with per-cue threshold sensitivity retained below",
            "instrument": "Deep attacks in the mixed recording matching the requested low-piano notes; an isolated piano stem is unavailable",
            "selection": "Sparse strong-note presentation selection; omitted attacks and the quiet outro intentionally hold the current chapter",
        },
        "analysisStepSeconds": ANALYSIS_STEP,
        "minimumCueGapSeconds": MINIMUM_CUE_GAP,
        "fixedTempoBpm": None,
        "cueTimesSeconds": cue_times,
        "selectedAttackEvidence": evidence,
        "summary": {
            "candidateCount": int(len(candidates)),
            "selectedCount": len(cue_times),
            "medianCueGapSeconds": round(float(np.median(gaps)), 3),
            "minimumCueGapSeconds": round(float(np.min(gaps)), 3),
            "maximumCueGapSeconds": round(float(np.max(gaps)), 3),
            "holdFinalChapterAfterSeconds": cue_times[-1],
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
            raise SystemExit("Chapter analysis differs from saved JSON; regenerate it.")
        print("Chapter analysis reproduced identical bytes.")
    else:
        args.output.write_bytes(encoded)
    print(f'{len(result["cueTimesSeconds"])} measured chapter cues; {len(encoded):,} bytes')
    print(f'Cue times: {result["cueTimesSeconds"]}')
    print(f'JSON SHA256: {hashlib.sha256(encoded).hexdigest()}')


if __name__ == "__main__":
    main()
