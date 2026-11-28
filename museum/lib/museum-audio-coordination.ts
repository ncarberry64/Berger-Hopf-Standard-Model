type MusicAudio = Pick<HTMLAudioElement, 'volume'>;
type MusicController = {
  play: () => Promise<void>;
  pause: () => void;
};

/** Coordinate visitor intent without restarting music when narration finishes. */
export function coordinateMuseumAudio({
  target,
  audio,
  player,
  isLifecycleActive,
}: {
  target: EventTarget;
  audio: MusicAudio;
  player: MusicController;
  isLifecycleActive: () => boolean;
}) {
  let originalVolume: number | undefined;
  const playMusic = () => {
    // Do not defer play(): mobile browsers require the original click gesture.
    void player.play().catch(() => {});
  };
  const playLifecycle = () => {
    if (isLifecycleActive()) playMusic();
  };
  const pauseLifecycle = () => {
    if (isLifecycleActive()) player.pause();
  };
  const duck = () => {
    if (originalVolume !== undefined) return;
    originalVolume = audio.volume;
    audio.volume = originalVolume * 0.18;
  };
  const restoreVolume = () => {
    if (originalVolume === undefined) return;
    audio.volume = originalVolume;
    originalVolume = undefined;
    // No play() here: explicit pause, hidden tabs and suspended sessions win.
  };
  const events = [
    ['bhsm:play-music', playMusic],
    ['bhsm:lifecycle-play', playLifecycle],
    ['bhsm:lifecycle-pause', pauseLifecycle],
    ['bhsm:narration-start', duck],
    ['bhsm:narration-end', restoreVolume],
  ] as const;
  events.forEach(([name, listener]) => target.addEventListener(name, listener));
  return () => {
    events.forEach(([name, listener]) =>
      target.removeEventListener(name, listener),
    );
    restoreVolume();
  };
}
