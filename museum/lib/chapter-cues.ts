type ChapterMusic = {
  slideId: string;
  source: string;
  seconds: number;
  seeking?: boolean;
};

// The latest actual note attack, rather than elapsed animation time.
export function chapterCueIndex(cues: readonly number[], seconds: number) {
  let low = 0;
  let high = cues.length;
  while (low < high) {
    const mid = (low + high) >>> 1;
    if (cues[mid] <= seconds) low = mid + 1;
    else high = mid;
  }
  return low - 1;
}

export function createChapterSequence(
  cues: readonly number[],
  count = 3,
  silentSeconds = 10,
) {
  let chapter = 0;
  let silentTime = 0;
  let engaged = false;
  let previousTime: number | undefined;
  let previous: { key: string; seconds: number; cue: number } | undefined;
  function suspend() {
    previousTime = undefined;
    previous = undefined;
  }
  return {
    suspend,
    restart() {
      chapter = 0;
      silentTime = 0;
      suspend();
    },
    tick(time: number, music?: ChapterMusic) {
      const delta = previousTime === undefined ? 0 : time - previousTime;
      previousTime = time;
      if (delta < 0 || delta > 0.5) previous = undefined;
      if (!music) {
        previous = undefined;
        // A silent first visit keeps its automatic tour. Once music has been
        // used, pausing it holds the chapter until another real note arrives.
        if (!engaged && delta >= 0 && delta <= 0.5) {
          silentTime += delta;
          const steps = Math.floor(silentTime / silentSeconds);
          chapter = (chapter + steps) % count;
          silentTime -= steps * silentSeconds;
        }
        return chapter;
      }
      engaged = true;
      const key = `${music.slideId}:${music.source}`;
      const cue = chapterCueIndex(cues, music.seconds);
      const rebasing =
        !previous ||
        previous.key !== key ||
        music.seeking ||
        music.seconds < previous.seconds ||
        music.seconds - previous.seconds > 0.5;
      if (rebasing) {
        // A new recording or natural loop begins with the Hopf chapter.
        // Mid-song returns and replay wait for the next note without skipping
        // chapters the visitor has not seen.
        if (music.seconds < cues[0]) chapter = 0;
      } else if (cue > previous!.cue) {
        // The first note establishes Hopf; the second starts Berger, then BHSM.
        chapter = (chapter + cue - Math.max(0, previous!.cue)) % count;
      }
      previous = { key, seconds: music.seconds, cue };
      return chapter;
    },
  };
}
