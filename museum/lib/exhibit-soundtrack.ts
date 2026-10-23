type Player = Pick<
  HTMLAudioElement,
  | 'src'
  | 'paused'
  | 'play'
  | 'pause'
  | 'load'
  | 'addEventListener'
  | 'removeEventListener'
>;

// One element retains mobile playback permission and mute state. A revision
// makes old play() completions harmless after navigation, pause or suspension.
export function createExhibitSoundtrack({
  audio,
  isActive,
  onChange,
  onNeedGesture,
}: {
  audio: Player;
  isActive: () => boolean;
  onChange: (playing: boolean) => void;
  onNeedGesture: () => void;
}) {
  let disposed = false;
  let manuallyPaused = false;
  let requested = false;
  let revision = 0;
  let source = '';
  let pending: Promise<void> | undefined;

  function stop() {
    revision++;
    pending = undefined;
    requested = false;
    audio.pause();
    onChange(false);
  }

  function suspend() {
    if (disposed) return;
    stop();
    if (!manuallyPaused) onNeedGesture();
  }

  function attempt(): Promise<void> {
    if (disposed || manuallyPaused || !isActive()) return Promise.resolve();
    requested = true;
    if (pending) return pending;
    const attemptRevision = ++revision;
    let result: Promise<void>;
    try {
      // Keep this call synchronous with the visitor's gesture.
      result = audio.play();
    } catch (error) {
      result = Promise.reject(error);
    }
    const attemptResult = result.then(
      () => {
        if (disposed || !requested || manuallyPaused || !isActive())
          audio.pause();
        if (attemptRevision === revision) pending = undefined;
      },
      (error: unknown) => {
        if (attemptRevision === revision && !disposed) {
          pending = undefined;
          requested = false;
          onChange(false);
          if (!manuallyPaused) onNeedGesture();
        }
        throw error;
      },
    );
    pending = attemptResult;
    return attemptResult;
  }

  const onPlay = () => {
    if (disposed || !requested || manuallyPaused || !isActive()) {
      audio.pause();
      onChange(false);
      return;
    }
    onChange(true);
  };
  const onPause = () => onChange(false);
  audio.addEventListener('play', onPlay);
  audio.addEventListener('pause', onPause);
  audio.addEventListener('error', suspend);

  return {
    select(nextSource: string) {
      if (disposed || source === nextSource) return;
      const resume = requested && !manuallyPaused && isActive();
      stop();
      source = nextSource;
      audio.src = nextSource;
      audio.load();
      if (resume) void attempt().catch(() => {});
    },
    play() {
      if (disposed) return Promise.resolve();
      manuallyPaused = false;
      return attempt();
    },
    pause() {
      manuallyPaused = true;
      stop();
    },
    suspend,
    isManuallyPaused: () => manuallyPaused,
    dispose() {
      disposed = true;
      stop();
      audio.removeEventListener('play', onPlay);
      audio.removeEventListener('pause', onPause);
      audio.removeEventListener('error', suspend);
    },
  };
}
