'use client';

import { Music2, Pause, Play, Volume2, VolumeX } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { startSoundtrackOnInteraction } from '../lib/start-soundtrack';
import { manageSoundtrackSession } from '../lib/soundtrack-session';
import { advanceSoundtrack } from '../lib/advance-soundtrack';

const TRACKS = [
  {
    title: 'Inspiring Epic',
    artist: 'PaulYudin',
    source: './audio/paulyudin-inspiring-epic-164829.mp3',
  },
  {
    title: 'Epic Cinematic Victory',
    artist: 'PaulYudin',
    source: './audio/paulyudin-epic-cinematic-victory-155790.mp3',
  },
] as const;

export function MuseumSoundtrack() {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [trackIndex, setTrackIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [muted, setMuted] = useState(false);
  const currentTrack = useRef(0);
  const manuallyPaused = useRef(false);
  const stopGesture = useRef<() => void>(() => {});
  const armPlayback = useRef<() => void>(() => {});
  const track = TRACKS[trackIndex];

  useEffect(() => {
    const players = audioRef.current ? [audioRef.current] : [];
    const isActive = () => !document.hidden && document.hasFocus();
    const shouldStart = (event: Event) => {
      if (!isActive()) return false;
      // The final-slide player handles its own buttons. Do not start and
      // toggle playback twice on the same click.
      if (
        event.target instanceof Element &&
        event.target.closest('.soundtrack-controls')
      )
        return false;
      return !(
        event instanceof KeyboardEvent &&
        (event.repeat ||
          ['Shift', 'Control', 'Alt', 'Meta', 'Escape'].includes(event.key))
      );
    };
    const armGesture = () => {
      stopGesture.current();
      const audio = audioRef.current;
      if (audio && !manuallyPaused.current)
        stopGesture.current = startSoundtrackOnInteraction(
          window,
          audio,
          shouldStart,
        );
    };
    armPlayback.current = armGesture;
    let channel: BroadcastChannel | undefined;
    try {
      if (typeof BroadcastChannel !== 'undefined')
        channel = new BroadcastChannel('bhsm-museum-soundtrack');
    } catch {
      /* Focus and visibility guards still apply if channels are unavailable. */
    }
    const stopSession = manageSoundtrackSession({
      windowTarget: window,
      documentTarget: document,
      players,
      isActive,
      channel,
      owner: crypto.randomUUID(),
      onChange: setPlaying,
      onSuspend: armGesture,
    });
    armGesture();
    return () => {
      stopGesture.current();
      stopSession();
    };
  }, []);

  async function play() {
    const audio = audioRef.current;
    if (!audio || document.hidden || !document.hasFocus()) return;

    try {
      await audio.play();
    } catch {
      setPlaying(false);
      armPlayback.current();
    }
  }

  function togglePlayback() {
    const audio = audioRef.current;
    if (!audio) return;

    if (playing) {
      manuallyPaused.current = true;
      stopGesture.current();
      audio.pause();
      setPlaying(false);
      return;
    }

    manuallyPaused.current = false;
    void play();
  }

  function advancePlaylist() {
    const audio = audioRef.current;
    if (
      !audio ||
      manuallyPaused.current ||
      document.hidden ||
      !document.hasFocus()
    )
      return;
    const nextIndex = (currentTrack.current + 1) % TRACKS.length;
    currentTrack.current = nextIndex;
    setTrackIndex(nextIndex);
    void advanceSoundtrack(audio, TRACKS[nextIndex].source).catch(() => {
      setPlaying(false);
      armPlayback.current();
    });
  }

  function toggleMute() {
    const nextMuted = !muted;
    if (audioRef.current) audioRef.current.muted = nextMuted;
    setMuted(nextMuted);
  }

  return (
    <aside className="soundtrack-dock" aria-label="Museum soundtrack">
      {/* Keep the same user-activated media element for every playlist track.
          A second element can require a fresh playback gesture on iOS. */}
      {/* oxlint-disable-next-line jsx-a11y/media-has-caption -- Instrumental music has no speech. */}
      <audio
        ref={audioRef}
        src={TRACKS[0].source}
        preload="metadata"
        playsInline
        onEnded={advancePlaylist}
      />
      <div className="soundtrack-mark" aria-hidden="true">
        <Music2 />
      </div>
      <div className="soundtrack-copy" aria-live="polite">
        <small>
          Museum soundtrack · {trackIndex + 1}/{TRACKS.length}
        </small>
        <strong>{track.title}</strong>
        <a
          href="https://pixabay.com/users/paulyudin-30043746/"
          target="_blank"
          rel="noreferrer"
        >
          {track.artist} · Pixabay ↗
        </a>
      </div>
      <div className="soundtrack-controls">
        <button
          type="button"
          onClick={togglePlayback}
          aria-label={
            playing ? 'Pause museum soundtrack' : 'Play museum soundtrack'
          }
          aria-pressed={playing}
        >
          {playing ? <Pause aria-hidden="true" /> : <Play aria-hidden="true" />}
        </button>
        <button
          type="button"
          onClick={toggleMute}
          aria-label={
            muted ? 'Unmute museum soundtrack' : 'Mute museum soundtrack'
          }
          aria-pressed={muted}
        >
          {muted ? (
            <VolumeX aria-hidden="true" />
          ) : (
            <Volume2 aria-hidden="true" />
          )}
        </button>
      </div>
    </aside>
  );
}
