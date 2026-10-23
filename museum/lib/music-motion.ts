import cues from './music-cues.json' with { type: 'json' };

export type MusicMotionMode = 'musical' | 'cadence' | 'independent';
export type MusicSample = {
  slideId: string;
  source: string;
  seconds: number;
  seeking?: boolean;
};

type Cue = {
  tempoBpm: number | null;
  beatOffsetSeconds: number | null;
  confidence: string;
  energyStepSeconds: number;
  energy: number[];
};
const tracks = cues.tracks as Record<string, Cue>;
const integrals = new Map<string, { values: number[]; mean: number }>();
const clamp = (value: number, low: number, high: number) =>
  Math.max(low, Math.min(high, value));

export function musicBeat(slideId: string, seconds: number) {
  const cue = tracks[slideId];
  if (
    !cue ||
    cue.confidence !== 'high' ||
    !cue.tempoBpm ||
    cue.beatOffsetSeconds === null
  )
    return null;
  return {
    beat: ((seconds - cue.beatOffsetSeconds) * cue.tempoBpm) / 60,
    tempoBpm: cue.tempoBpm,
  };
}

// Reading sequences launch from the actual beat, not the gently rejoining
// finite-animation clock. Rejoining repeats the current entry, never skips it.
export function createPhraseSequence(stageSeconds = 8) {
  let value = 0;
  let previousTime: number | undefined;
  let previousBeat: number | undefined;
  let anchor: { beat: number; value: number } | undefined;
  function suspend() {
    previousTime = undefined;
    previousBeat = undefined;
    anchor = undefined;
  }
  return {
    suspend,
    restart() {
      value = 0;
      suspend();
    },
    tick(time: number, beat: number | null) {
      const delta =
        previousTime === undefined ? 0 : Math.max(0, time - previousTime);
      previousTime = time;
      if (beat === null) {
        anchor = undefined;
        previousBeat = undefined;
        value += delta;
        return value;
      }
      if (
        !anchor ||
        previousBeat === undefined ||
        beat < previousBeat ||
        beat - previousBeat > 2
      ) {
        anchor = {
          beat: Math.ceil((beat - 1e-9) / 4) * 4,
          value: Math.floor(value / stageSeconds) * stageSeconds,
        };
      }
      previousBeat = beat;
      if (beat >= anchor.beat) value = anchor.value + (beat - anchor.beat) / 2;
      return value;
    },
  };
}

// Musical presentation coordinates only. No scientific values or physical
// clocks depend on these locally measured soundtrack cues.
export function musicPosition(
  slideId: string,
  seconds: number,
  mode: MusicMotionMode = 'musical',
) {
  const cue = tracks[slideId];
  const t = Math.max(0, seconds);
  if (!cue || mode !== 'musical') return { position: t, grid: false };
  if (
    cue.confidence === 'high' &&
    cue.tempoBpm &&
    cue.beatOffsetSeconds !== null
  ) {
    const beats = Math.max(
      0,
      ((t - cue.beatOffsetSeconds) * cue.tempoBpm) / 60,
    );
    return { position: beats / 2, grid: true };
  }
  let integral = integrals.get(slideId);
  if (!integral) {
    const values = [0];
    for (let i = 1; i < cue.energy.length; i++)
      values.push(
        values[i - 1] +
          ((cue.energy[i - 1] + cue.energy[i]) * cue.energyStepSeconds) / 2,
      );
    integral = {
      values,
      mean:
        values.at(-1)! /
        Math.max(
          cue.energyStepSeconds,
          (cue.energy.length - 1) * cue.energyStepSeconds,
        ),
    };
    integrals.set(slideId, integral);
  }
  const bounded = Math.min(t, (cue.energy.length - 1) * cue.energyStepSeconds);
  const i = Math.min(
    cue.energy.length - 2,
    Math.floor(bounded / cue.energyStepSeconds),
  );
  const dt = bounded - i * cue.energyStepSeconds;
  const slope = (cue.energy[i + 1] - cue.energy[i]) / cue.energyStepSeconds;
  const area = integral.values[i] + cue.energy[i] * dt + (slope * dt * dt) / 2;
  // Ambient scores have no trustworthy fixed beat. Follow their measured
  // swells instead, keeping the average choreography speed unchanged.
  return { position: t + 0.3 * (area - integral.mean * bounded), grid: false };
}

export function createSceneTransport(mode: MusicMotionMode = 'musical') {
  let time = 0;
  let wall: number | undefined;
  let previous:
    | { key: string; seconds: number; position: number; bias: number }
    | undefined;
  function suspend() {
    wall = undefined;
    previous = undefined;
  }
  return {
    suspend,
    tick(now: number, music?: MusicSample, stopAt = Infinity) {
      const delta = wall === undefined ? 0 : now - wall;
      wall = now;
      if (delta < 0 || delta > 0.5) {
        previous = undefined;
        return time;
      }
      if (!music || mode === 'independent') {
        previous = undefined;
        time = Math.min(stopAt, time + delta);
        return time;
      }
      const sample = musicPosition(music.slideId, music.seconds, mode);
      const key = `${music.slideId}:${music.source}`;
      if (
        !previous ||
        previous.key !== key ||
        music.seeking ||
        music.seconds < previous.seconds ||
        music.seconds - previous.seconds > 0.5
      ) {
        previous = {
          key,
          seconds: music.seconds,
          position: sample.position,
          bias: sample.grid
            ? Math.round((time - sample.position) / 2) * 2
            : time - sample.position,
        };
        return time;
      }
      const advance = Math.max(0, sample.position - previous.position);
      const error = sample.position + previous.bias - time - advance;
      // Join a reliable phrase grid gently; starting music or resuming an
      // inspected scene must never rewind, jump or skip its reveal.
      const correction = sample.grid
        ? clamp(error, -advance * 0.25, advance * 0.25)
        : 0;
      time = Math.min(stopAt, time + advance + correction);
      previous = {
        ...previous,
        seconds: music.seconds,
        position: sample.position,
      };
      return time;
    },
  };
}
