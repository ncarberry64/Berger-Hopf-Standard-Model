type ImpactMusic = {
  slideId: string;
  source: string;
  seconds: number;
  seeking?: boolean;
};

// Keep the incoming approach and outgoing reveal, placing their meeting point
// on a measured soundtrack attack. The reading hold absorbs variable spacing.
export function createImpactSequence(cues: readonly number[]) {
  const lead = 1.4;
  const reveal = 2.2;
  const cycle = 8;
  let value = 0;
  let engaged = false;
  let previousTime: number | undefined;
  let previous: { key: string; seconds: number } | undefined;
  let anchor: { index: number; base: number } | undefined;
  function suspend() {
    previousTime = undefined;
    previous = undefined;
    anchor = undefined;
  }
  return {
    suspend,
    restart() {
      value = 0;
      suspend();
    },
    tick(time: number, music?: ImpactMusic) {
      const delta = previousTime === undefined ? 0 : time - previousTime;
      previousTime = time;
      if (delta < 0 || delta > 0.5) {
        previous = undefined;
        anchor = undefined;
      }
      if (!music) {
        previous = undefined;
        anchor = undefined;
        if (!engaged && delta >= 0 && delta <= 0.5) value += delta;
        return value;
      }
      if (!engaged) value = Math.floor(value / cycle) * cycle;
      engaged = true;
      const key = `${music.slideId}:${music.source}`;
      if (
        !previous ||
        previous.key !== key ||
        music.seeking ||
        music.seconds < previous.seconds ||
        music.seconds - previous.seconds > 0.5
      ) {
        const index = cues.findIndex((cue) => cue >= music.seconds + lead);
        anchor =
          index < 0
            ? undefined
            : { index, base: Math.floor(value / cycle) * cycle };
      }
      previous = { key, seconds: music.seconds };
      if (!anchor || music.seeking) return value;
      while (
        anchor.index + 1 < cues.length &&
        music.seconds >= cues[anchor.index + 1] - lead
      ) {
        anchor = { index: anchor.index + 1, base: anchor.base + cycle };
      }
      const impact = cues[anchor.index];
      const elapsed = music.seconds - (impact - lead);
      if (elapsed < 0) return value;
      let phase = elapsed;
      if (elapsed > lead + reveal) {
        const nextStart = cues[anchor.index + 1] - lead;
        const reading = nextStart - impact - reveal;
        phase = Number.isFinite(reading)
          ? lead +
            reveal +
            ((elapsed - lead - reveal) / reading) * (cycle - lead - reveal)
          : Math.min(cycle - 1e-6, elapsed);
      }
      value = anchor.base + phase;
      return value;
    },
  };
}
