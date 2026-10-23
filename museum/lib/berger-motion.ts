const TAU = Math.PI * 2;

// Presentation choreography, separate from the Hopf map and Berger spectrum.
// Integer beat periods keep visible accents on the music throughout the song.
export function bergerMotion(
  time: number,
  elapsed: number,
  beat: number | null,
  stage: number,
) {
  if (beat === null)
    return {
      fiberScale: 1 + 0.3 * Math.sin(elapsed * 0.65),
      orbit: time * (stage === 2 ? 1.1 : 0.65),
      angle: time * 0.12 + 0.55,
      dashOffset: -time * 12,
      accent: 0,
      pathway: Math.floor(time) % 5,
    };
  const fraction = ((beat % 1) + 1) % 1;
  return {
    fiberScale: 1 + 0.3 * Math.cos((TAU * beat) / 16),
    orbit: (TAU * beat) / (stage === 2 ? 8 : 16),
    angle: 0.55 + (TAU * beat) / 128,
    dashOffset: (-11 * beat) / 2,
    // A small light breath gives each audible attack a visible landing.
    accent: (1 + Math.cos(TAU * fraction)) / 2,
    pathway: ((Math.floor(beat / 2) % 5) + 5) % 5,
  };
}
