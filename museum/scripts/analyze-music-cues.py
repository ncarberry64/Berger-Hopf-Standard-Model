"""Derive presentation timing cues from the museum's local delivery MP3s.

Run from the repository root:
  python museum/scripts/analyze-music-cues.py

Offline authoring dependencies: numpy, scipy and imageio-ffmpeg (or --ffmpeg).
The browser only consumes the generated JSON; no analysis libraries ship in it.
Tempo is an approximate pulse estimate, not a score transcription. Cinematic and
ambient recordings can change tempo or have no unambiguous beat. The measured
energy envelope remains tied to their actual recorded audio in either case.
These are presentation cues, never scientific measurements or simulation input.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy import ndimage, optimize, signal


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_RATE = 11025
HOP = 256
ENERGY_STEP = 0.25


def decode(path, ffmpeg):
    result = subprocess.run(
        [ffmpeg, "-nostdin", "-hide_banner", "-loglevel", "error", "-i", str(path),
         "-map", "0:a:0", "-ac", "1", "-ar", str(SAMPLE_RATE),
         "-f", "f32le", "pipe:1"],
        check=True, capture_output=True,
    )
    return np.frombuffer(result.stdout, dtype="<f4")


def envelope(samples):
    """Centered 250 ms RMS at t=i*0.25s, normalized per recording (0..1)."""
    # Sample boundaries are calculated from absolute media time. Repeatedly
    # rounding a 2756.25-sample interval would otherwise accumulate timing drift.
    centers = np.arange(int(np.ceil(len(samples) / SAMPLE_RATE / ENERGY_STEP))) * ENERGY_STEP
    starts = np.maximum(0, np.rint((centers - ENERGY_STEP / 2) * SAMPLE_RATE).astype(int))
    ends = np.minimum(len(samples), np.rint((centers + ENERGY_STEP / 2) * SAMPLE_RATE).astype(int))
    integral = np.concatenate(([0.0], np.cumsum(samples.astype(np.float64) ** 2)))
    rms = np.sqrt((integral[ends] - integral[starts]) / np.maximum(ends - starts, 1))
    scale = max(float(np.percentile(rms, 95)), 1e-8)
    return np.round(np.clip(rms / scale, 0, 1), 3).tolist()


def pulse(samples):
    """Estimate pulse from spectral-flux repetition, then fit recorded onsets."""
    frequencies, times, transform = signal.stft(
        samples, fs=SAMPLE_RATE, nperseg=1024, noverlap=1024 - HOP,
        boundary="zeros", padded=True,
    )
    magnitude = np.abs(transform)
    # Log compression prevents only the loud orchestral climax setting the grid.
    compressed = np.log1p(magnitude * 1000)
    flux_bands = []
    for lower, upper in [(40, 250), (250, 2000), (2000, 5500)]:
        band = compressed[(frequencies >= lower) & (frequencies < upper)]
        flux = np.maximum(np.diff(band, axis=1, prepend=band[:, :1]), 0).mean(axis=0)
        flux /= max(float(np.percentile(flux, 90)), 1e-8)
        flux_bands.append(flux)
    onset = np.mean(flux_bands, axis=0)
    baseline = ndimage.median_filter(onset, size=43)
    onset = np.maximum(onset - baseline * 0.75, 0)
    onset = ndimage.gaussian_filter1d(onset, 0.6)
    frame_rate = SAMPLE_RATE / HOP

    # Average normalized autocorrelations of overlapping windows. This detects
    # local musical repetition without requiring a perfectly fixed whole song.
    window_size = round(32 * frame_rate)
    correlations = []
    for start in range(0, max(1, len(onset) - window_size + 1), window_size // 2):
        section = onset[start:start + window_size].astype(np.float64)
        section -= section.mean()
        correlation = signal.correlate(section, section, mode="full", method="fft")
        correlation = correlation[len(section) - 1:]
        if correlation[0] > 1e-9:
            correlations.append(correlation[:100] / correlation[0])
    mean_correlation = np.mean(correlations, axis=0)
    tempos = np.arange(64, 160.001, 0.05)
    lags = 60 * frame_rate / tempos
    score = np.interp(lags, np.arange(len(mean_correlation)), mean_correlation)
    score += 0.4 * np.interp(2 * lags, np.arange(len(mean_correlation)), mean_correlation)
    score += 0.15 * np.interp(3 * lags, np.arange(len(mean_correlation)), mean_correlation)
    initial_tempo = float(tempos[np.argmax(score)])

    # Refine in a narrow neighbourhood by searching coherent onset phase over
    # the whole recording. A Hann window softens fades and credits silence.
    weighted = onset * np.hanning(len(onset))
    weighted /= max(float(weighted.sum()), 1e-8)
    candidates = np.arange(initial_tempo * 0.98, initial_tempo * 1.02, 0.005)
    # Dominant pulses may be double or half time; this convention deliberately
    # stays within a comfortable presentation range, not a musicological label.
    strengths = []
    phases = []
    for tempo in candidates:
        circular = np.sum(weighted * np.exp(-2j * np.pi * times * tempo / 60))
        strengths.append(abs(circular))
        phases.append(np.angle(circular))
    best = int(np.argmax(strengths))
    tempo = float(candidates[best])
    period = 60 / tempo
    offset = float((-phases[best] / (2 * np.pi)) % 1 * period)
    coherence = float(strengths[best])
    # Coherence is the circular concentration of measured positive onsets on the
    # fitted grid, not a probability. Low concentration means there is no useful
    # fixed grid. Do not expose an arbitrary tempo for those ambient/rubato files.
    confidence = "high" if coherence >= 0.12 else "medium" if coherence >= 0.045 else "low"
    reliable = confidence != "low"
    return (round(tempo, 3) if reliable else None,
            round(offset, 3) if reliable else None,
            confidence, round(coherence, 4))


def refine_attack_grid(samples, tempo, offset):
    """Fit strong attack peaks instead of the later average onset centroid.

    Only already-reliable pulse estimates enter here. A 5.8 ms hop resolves
    attacks within the coarse grid's beat neighbourhood. Robust regression
    estimates both phase and accumulated tempo drift; there is no manually
    selected lead or constant latency subtraction. Every fourth nominal beat
    is withheld while checking that both median and 90th-percentile residuals
    improve. The published grid then uses all retained attacks.
    """
    hop = 64
    frequencies, times, transform = signal.stft(
        samples, fs=SAMPLE_RATE, nperseg=1024, noverlap=1024 - hop,
        boundary="zeros", padded=True,
    )
    compressed = np.log1p(np.abs(transform) * 1000)
    bands = []
    for lower, upper in [(40, 250), (250, 2000), (2000, 5500)]:
        band = compressed[(frequencies >= lower) & (frequencies < upper)]
        flux = np.maximum(np.diff(band, axis=1, prepend=band[:, :1]), 0).mean(axis=0)
        flux /= max(float(np.percentile(flux, 90)), 1e-8)
        bands.append(flux)
    onset = np.mean(bands, axis=0)
    onset = np.maximum(onset - ndimage.median_filter(onset, size=173) * 0.75, 0)
    onset = ndimage.gaussian_filter1d(onset, 2.4)
    peaks, _ = signal.find_peaks(
        onset, prominence=float(np.percentile(onset, 70)) * 0.5,
        distance=round(0.15 * SAMPLE_RATE / hop),
    )
    period = 60 / tempo
    attack_times = times[peaks]
    beat_numbers = np.rint((attack_times - offset) / period).astype(int)
    nominal_times = offset + beat_numbers * period
    residuals = attack_times - nominal_times
    keep = (
        (np.abs(residuals) < 0.08) & (attack_times > 1)
        & (attack_times < len(samples) / SAMPLE_RATE - 5)
    )
    peaks = peaks[keep]
    attack_times = attack_times[keep]
    beat_numbers = beat_numbers[keep]
    nominal_times = nominal_times[keep]
    residuals = residuals[keep]
    train = beat_numbers % 4 != 0
    holdout = ~train
    if np.count_nonzero(train) < 20 or np.count_nonzero(holdout) < 10:
        return tempo, offset, {"applied": False, "reason": "Too few strong attacks"}
    center = float(np.median(nominal_times))
    weights = np.sqrt(onset[peaks] / max(float(np.percentile(onset[peaks], 75)), 1e-8))

    def fit(mask):
        solution = optimize.least_squares(
            lambda parameters: (
                residuals[mask] - parameters[0]
                - parameters[1] * (nominal_times[mask] - center)
            ) * weights[mask],
            [0, 0], loss="soft_l1", f_scale=0.015,
        )
        shift, drift = solution.x
        refined_tempo = tempo / (1 + drift)
        refined_offset = (offset + shift + drift * (offset - center)) % (60 / refined_tempo)
        return round(float(refined_tempo), 3), round(float(refined_offset), 3)

    def errors(mask, bpm, phase):
        beat_period = 60 / bpm
        values = attack_times[mask]
        nearest = phase + np.rint((values - phase) / beat_period) * beat_period
        return np.abs(values - nearest) * 1000

    def metrics(values):
        return {
            "medianAbsoluteResidualMs": round(float(np.median(values)), 3),
            "p90AbsoluteResidualMs": round(float(np.quantile(values, 0.9)), 3),
        }

    trained_tempo, trained_offset = fit(train)
    before = errors(holdout, tempo, offset)
    after = errors(holdout, trained_tempo, trained_offset)
    accepted = bool(np.median(after) < np.median(before)
                    and np.quantile(after, 0.9) < np.quantile(before, 0.9))
    diagnostics = {
        "applied": accepted,
        "method": "5.805 ms-hop three-band spectral attack peaks within 80 ms of the baseline grid; amplitude-weighted soft-L1 fit of phase and tempo drift. Every fourth nominal beat held out before the final all-attack fit. Residuals measure detected attacks, not a perceptual latency guarantee.",
        "baselineTempoBpm": tempo,
        "baselineBeatOffsetSeconds": offset,
        "detectedAttacks": int(len(attack_times)),
        "holdoutAttacks": int(np.count_nonzero(holdout)),
        "trainedTempoBpm": trained_tempo,
        "trainedBeatOffsetSeconds": trained_offset,
        "holdoutBefore": metrics(before),
        "holdoutAfter": metrics(after),
    }
    if not accepted:
        return tempo, offset, diagnostics
    refined_tempo, refined_offset = fit(np.ones(len(attack_times), dtype=bool))
    for label, mask in [
        ("allAttacks", np.ones(len(attack_times), dtype=bool)),
        ("first20Seconds", attack_times < 20),
    ]:
        diagnostics[label] = {
            "count": int(np.count_nonzero(mask)),
            "before": metrics(errors(mask, tempo, offset)),
            "after": metrics(errors(mask, refined_tempo, refined_offset)),
        }
    return refined_tempo, refined_offset, diagnostics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ffmpeg", help="Path to an existing local FFmpeg executable")
    parser.add_argument("--output", type=Path, default=ROOT / "lib" / "music-cues.json")
    args = parser.parse_args()
    if args.ffmpeg:
        ffmpeg = args.ffmpeg
    else:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    manifest = json.loads((ROOT / "public" / "audio" / "exhibit-soundtracks.json").read_text())
    # The attribution manifest is the sole mapping of exhibits to audio files.
    rows = manifest if isinstance(manifest, list) else manifest["tracks"]
    tracks = {}
    for row in rows:
        path = ROOT / "public" / row["source"].removeprefix("./")
        samples = decode(path, ffmpeg)
        tempo, offset, confidence, coherence = pulse(samples)
        attack_fit = None
        if confidence == "high":
            tempo, offset, attack_fit = refine_attack_grid(samples, tempo, offset)
        tracks[row["slideId"]] = {
            "tempoBpm": tempo,
            "beatOffsetSeconds": offset,
            "durationSeconds": round(len(samples) / SAMPLE_RATE, 3),
            "confidence": confidence,
            "pulseCoherence": coherence,
            "audioSha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "energyStepSeconds": ENERGY_STEP,
            "energy": envelope(samples),
        }
        if attack_fit:
            tracks[row["slideId"]]["attackRefinement"] = attack_fit
        grid = f'{tempo:.3f} BPM, offset {offset:.3f}s' if tempo else 'energy cues only'
        print(f'{row["slideId"]}: {grid}, {confidence} ({coherence:.4f})', flush=True)
    result = {
        "method": "Offline 11025 Hz mono decode; three-band positive log-spectral flux, 32 s window autocorrelation, narrow whole-track phase fit. High-confidence grids are refined to strong attack peaks at 5.805 ms hops using robust phase/tempo-drift regression, with every fourth beat held out to verify lower median and p90 timing residuals. Pulse coherence is onset circular concentration: high >=0.12, medium >=0.045, low otherwise; low grids are null. Tempo/phase are approximate presentation cues (half/double-time ambiguity and rubato possible), not scientific data. Centered 250 ms RMS at t=i*energyStepSeconds is normalized to each track's 95th percentile; energy follows the recorded waveform.",
        "tracks": tracks,
    }
    # Compact arrays keep the entire local cue set comfortably below 200 KiB.
    args.output.write_text(json.dumps(result, separators=(",", ":")) + "\n", encoding="utf-8")
    assert args.output.stat().st_size < 200 * 1024


if __name__ == "__main__":
    main()
