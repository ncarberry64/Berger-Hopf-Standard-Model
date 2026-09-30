'use client';
import { useState } from 'react';
import benchmark from '../lib/cms-benchmark.json';
import { useSceneClock } from './science-console';
import { SCIENCE } from './exhibits';

const kernels = [
  ['branchy_cylindrical_scalar', 'Scalar branch-heavy control'],
  ['cylindrical_vectorized_control', 'Vectorized cylindrical control'],
  ['bhsm_boundary_vectorized', 'BHSM-inspired direct map'],
] as const;

export function ComputeAchievement({ motion }: { motion: boolean }) {
  const [playing, setPlaying] = useState(true);
  const { ref, time } = useSceneClock(motion && playing);
  const maximum = benchmark.results.branchy_cylindrical_scalar.median_seconds;
  const elapsed = (time / 3) % (maximum + 0.8);
  return (
    <section
      className="compute-achievement evidence-feature"
      ref={ref}
      aria-label="Recorded computing benchmark"
    >
      <p className="eyebrow">
        Measured computing achievement · same coordinate workload
      </p>
      <h4>
        {benchmark.comparisons.speedup_vs_vectorized_control.toFixed(3)}× the
        throughput of the vectorized control.
      </h4>

      <p className="data-label">
        2,000,000 vectors per pass · 200,000 unique CMS vectors repeated 10× ·
        median of 7 runs
      </p>
      <div className="benchmark-race">
        {kernels.map(([id, name]) => {
          const row = benchmark.results[id];
          const fraction = motion
            ? Math.min(1, elapsed / row.median_seconds)
            : 1;
          return (
            <div
              key={id}
              className={
                id === 'bhsm_boundary_vectorized' ? 'benchmark-bhsm' : ''
              }
            >
              <span>{name}</span>
              <b>{row.median_seconds.toFixed(6)} s</b>
              <div className="benchmark-track">
                <i style={{ width: `${fraction * 100}%` }} />
              </div>
            </div>
          );
        })}
      </div>
      <button className="evidence-play" onClick={() => setPlaying(!playing)}>
        {playing ? 'Pause timing replay' : 'Replay timings'}
      </button>
      <p>
        The BHSM-inspired direct map processed{' '}
        {(
          benchmark.results.bhsm_boundary_vectorized.vectors_per_second / 1e6
        ).toFixed(2)}{' '}
        million four-vectors per second in this recorded test. It reduces
        coordinate-conversion overhead by expressing the transformation directly
        instead of routing it through the benchmark’s cylindrical calculation.
        The gain creates room for more analysis on the tested hardware.
      </p>
      <p className="console-caption">
        Bar progress is computed from the recorded median runtimes, slowed 3×
        for viewing; this is not a live benchmark. The{' '}
        {benchmark.comparisons.speedup_vs_scalar.toFixed(3)}× scalar comparison
        also includes Python-loop versus NumPy-vectorization effects. The
        scale-aware error test passed; the stricter absolute/relative 10⁻¹² test
        did not. These results demonstrate an advantage for this coordinate
        kernel, not an inadequacy of all current computing or a measured speedup
        over production detector software.
      </p>
      <a href={`${SCIENCE}/docs/cern_open_data_benchmark.md`}>
        Workload, hardware, accuracy and reproduction ↗
      </a>
    </section>
  );
}
