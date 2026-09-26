// Keep listening until playback actually succeeds. A rejected early gesture
// must not consume the visitor's later click or completed touch gesture.
export function startSoundtrackOnInteraction(
  target: EventTarget,
  audio: Pick<
    HTMLMediaElement,
    'play' | 'addEventListener' | 'removeEventListener'
  >,
  shouldStart: (event: Event) => boolean = () => true,
) {
  const events = ['click', 'pointerup', 'touchend', 'keydown'];
  let finished = false;

  function finish() {
    finished = true;
    events.forEach((name) => target.removeEventListener(name, attempt, true));
    audio.removeEventListener('play', finish);
  }

  function attempt(event: Event) {
    if (finished || !shouldStart(event)) return;
    // Call play synchronously inside the gesture to retain user activation.
    try {
      void audio
        .play()
        .then(finish)
        .catch(() => {
          // Browser permission or loading may fail; the next gesture can retry.
        });
    } catch {
      // Some media implementations throw synchronously; retain the fallback.
    }
  }

  events.forEach((name) => target.addEventListener(name, attempt, true));
  audio.addEventListener('play', finish);
  return finish;
}
