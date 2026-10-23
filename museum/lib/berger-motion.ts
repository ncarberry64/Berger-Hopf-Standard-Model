// Original geometry motion. Its shared clock controls speed; the drawing does
// not add metronome pulses or replace the orbit with fixed beat choreography.
export function bergerMotion(time: number, elapsed: number, stage: number) {
  return {
    fiberScale: 1 + 0.3 * Math.sin(elapsed * 0.65),
    orbit: time * (stage === 2 ? 1.1 : 0.65),
    angle: time * 0.12 + 0.55,
    dashOffset: -time * 12,
    pathway: Math.floor(time) % 5,
  };
}
