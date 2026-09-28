'use client';
/* oxlint-disable jsx-a11y/prefer-tag-over-role -- The canvas is a dynamically drawn probability-density image. */
import { useEffect, useRef, useState } from 'react';
import { orbitals, orbitalPixels } from '../lib/orbital-density';

function DensityPlot({
  orbital,
  time,
  miniature = false,
}: {
  orbital: number;
  time: number;
  miniature?: boolean;
}) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const context = ref.current?.getContext('2d');
    if (!context) return;
    const size = miniature ? 64 : 192;
    context.putImageData(
      new ImageData(orbitalPixels(orbitals[orbital], size), size, size),
      0,
      0,
    );
  }, [orbital, miniature]);
  return (
    <div className={miniature ? 'orbital-thumbnail' : 'orbital-density-frame'}>
      <canvas
        ref={ref}
        width={miniature ? 64 : 192}
        height={miniature ? 64 : 192}
        style={
          miniature
            ? undefined
            : { transform: `rotate(${(time * 3) % 360}deg)` }
        }
        aria-label={`${orbitals[orbital].label} probability-density cross-section`}
        role="img"
      />
      {!miniature && (
        <span className="orbital-nucleus" aria-label="Nucleus at the center" />
      )}
    </div>
  );
}

export function OrbitalStudy({
  atom,
  time,
  id,
}: {
  atom: 'hydrogen' | 'carbon';
  time: number;
  id: string;
}) {
  const available = atom === 'hydrogen' ? [0, 1, 2, 3, 4, 5, 6] : [0, 1, 2];
  const [chosen, setChosen] = useState(atom === 'carbon' ? 2 : 0);
  const orbital = available.includes(chosen) ? chosen : available[0];
  return (
    <div className="orbital-study" id={id}>
      <DensityPlot orbital={orbital} time={time} />
      <div className="orbital-legend">
        <span /> Low → high · relative |ψ|²
      </div>
      <div className="orbital-picker" role="group" aria-label="Orbital shapes">
        {available.map((i) => (
          <button
            type="button"
            key={i}
            aria-pressed={orbital === i}
            aria-label={`Show ${orbitals[i].label} orbital`}
            onClick={() => setChosen(i)}
          >
            <DensityPlot orbital={i} time={0} miniature />
            <span>{orbitals[i].label}</span>
          </button>
        ))}
      </div>
      <p className="orbital-description" aria-live="polite">
        {orbitals[orbital].label} · {orbitals[orbital].detail}
      </p>
      <small>
        Rotating view of a stationary density. Each image has its own brightness
        and spatial scale.{' '}
        {atom === 'hydrogen'
          ? 'Hydrogen examples include ground and excited states.'
          : 'Hydrogen-like shapes illustrate individual occupied orbitals; this is not the full many-electron density.'}
      </small>
    </div>
  );
}
