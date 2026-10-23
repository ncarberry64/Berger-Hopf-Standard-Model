"""Extract Time and Space's actual low-bass envelope for exhibit 3's speed.

Offline authoring dependencies: numpy, scipy, imageio-ffmpeg (or --ffmpeg).
Run from the repository root:
  python museum/scripts/analyze-exhibit3-bass.py
  python museum/scripts/analyze-exhibit3-bass.py --check

This measures the local delivery MP3. It does not borrow the full-spectrum
beat grid, assign a lap to each bass hit, or change any scientific data.
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
OUTPUT = ROOT / "lib" / "exhibit3-bass.json"
SAMPLE_RATE = 11025
ENERGY_STEP = 0.025
BASS_BAND_HZ = (30, 160)
RMS_SIGMA_SECONDS = 0.015


def analyze(ffmpeg):
    decoded = subprocess.run(
        [ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-i", str(AUDIO),
         "-map", "0:a:0", "-ac", "1", "-ar", str(SAMPLE_RATE),
         "-f", "f32le", "pipe:1"],
        check=True, capture_output=True,
    )
    samples = np.frombuffer(decoded.stdout, dtype="<f4")
    duration = len(samples) / SAMPLE_RATE
    # Forward/backward filtering removes group delay. The centered RMS window
    # is likewise aligned with media time, with no guessed lead/lag correction.
    sections = signal.butter(
        4, BASS_BAND_HZ, btype="bandpass", fs=SAMPLE_RATE, output="sos",
    )
    bass = signal.sosfiltfilt(sections, samples)
    rms = np.sqrt(ndimage.gaussian_filter1d(
        bass * bass, SAMPLE_RATE * RMS_SIGMA_SECONDS,
    ))
    sample_times = np.arange(len(samples)) / SAMPLE_RATE
    # Include one sample beyond the final partial interval so linear playback
    # interpolation covers the complete media duration.
    times = np.arange(int(np.ceil(duration / ENERGY_STEP)) + 1) * ENERGY_STEP
    measured = np.interp(times, sample_times, rms)
    scale = max(float(np.percentile(measured, 95)), 1e-9)
    energy = np.round(np.clip(measured / scale, 0, 1), 3)
    track_mean = float(np.trapezoid(energy, dx=ENERGY_STEP) / times[-1])

    # Inspection landmarks only: crests of strong positive 80 ms RMS rises.
    # An amplitude threshold suppresses the many small ripples in a bass note's
    # decay. These measured events are deliberately not snapped to any tempo.
    inspection_times = np.arange(0, duration, 0.01)
    inspection_energy = np.interp(inspection_times, sample_times, rms) / scale
    preceding = np.concatenate((np.full(8, inspection_energy[0]), inspection_energy[:-8]))
    rise = ndimage.gaussian_filter1d(np.maximum(inspection_energy - preceding, 0), 1)
    peaks, _ = signal.find_peaks(rise, height=0.3, prominence=0.2, distance=22)
    events = [round(float(inspection_times[index]), 3) for index in peaks]
    result = {
        "slideId": "berger-hopf",
        "trackTitle": "Time and Space",
        "source": "./audio/scott-buckley-time-and-space.mp3",
        "audioSha256": hashlib.sha256(AUDIO.read_bytes()).hexdigest(),
        "durationSeconds": round(duration, 6),
        "method": "Local MP3 decoded mono at 11025 Hz; fourth-order Butterworth 30–160 Hz bandpass applied forward/backward (zero group delay); centered Gaussian RMS with 15 ms sigma. Bass energy sampled at exact t=i*0.025 s, divided by the recording's 95th-percentile bass RMS and clipped to 0..1. trackMean is the trapezoidal time mean of the published energy samples. No full-spectrum beat grid, guessed latency correction, or fixed bass tempo is used. Optional majorOnsetTimesSeconds are crests of positive 80 ms bass-RMS rises measured at 10 ms steps, with normalized height>=0.3, prominence>=0.2 and separation>=220 ms; they are inspection landmarks, not forced animation events. Presentation timing only, not scientific data.",
        "confidence": {
            "bassEnvelope": "Measured directly from the identified local audio",
            "fixedBeatGrid": "Not assumed; sparse intro bass blooms and denser later bass pulses differ",
        },
        "fixedTempoBpm": None,
        "bassBandHz": list(BASS_BAND_HZ),
        "energyStepSeconds": ENERGY_STEP,
        "normalizationPercentile": 95,
        "normalizationRms": round(scale, 9),
        "trackMean": round(track_mean, 6),
        "majorOnsetTimesSeconds": events,
        "energy": energy.tolist(),
    }
    return result


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
            raise SystemExit("Bass analysis differs from the saved JSON; regenerate it.")
        print("Bass analysis reproduced identical bytes.")
    else:
        args.output.write_bytes(encoded)
    print(f'{len(result["energy"])} measured energy samples; mean={result["trackMean"]:.6f}; '
          f'{len(result["majorOnsetTimesSeconds"])} major bass rises; {len(encoded):,} bytes')
    print(f'First 60 s rise landmarks: {[t for t in result["majorOnsetTimesSeconds"] if t < 60]}')
    print(f'JSON SHA256: {hashlib.sha256(encoded).hexdigest()}')


if __name__ == "__main__":
    main()
