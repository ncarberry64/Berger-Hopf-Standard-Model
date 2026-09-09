'use client';

import { Music2, Pause, Play, Volume2, VolumeX } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

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
  const audioRefs = useRef<Array<HTMLAudioElement | null>>([]);
  const [trackIndex, setTrackIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [muted, setMuted] = useState(false);
  const track = TRACKS[trackIndex];

  useEffect(() => {
    const firstTrack = audioRefs.current[0];
    if (!firstTrack) return;

    function attemptPlayback() {
      void firstTrack?.play().catch(() => {
        setPlaying(false);
      });
    }

    function removeInteractionFallback() {
      window.removeEventListener('pointerdown', startAfterInteraction, true);
      window.removeEventListener('keydown', startAfterInteraction, true);
      window.removeEventListener('touchstart', startAfterInteraction, true);
    }

    function startAfterInteraction() {
      attemptPlayback();
      removeInteractionFallback();
    }

    attemptPlayback();
    window.addEventListener('pointerdown', startAfterInteraction, true);
    window.addEventListener('keydown', startAfterInteraction, true);
    window.addEventListener('touchstart', startAfterInteraction, true);

    return removeInteractionFallback;
  }, []);

  async function play(index: number) {
    const audio = audioRefs.current[index];
    if (!audio) return;

    try {
      await audio.play();
      setPlaying(true);
    } catch {
      setPlaying(false);
    }
  }

  function togglePlayback() {
    const audio = audioRefs.current[trackIndex];
    if (!audio) return;

    if (playing) {
      audio.pause();
      setPlaying(false);
      return;
    }

    void play(trackIndex);
  }

  function advancePlaylist(endedIndex: number) {
    const endedTrack = audioRefs.current[endedIndex];
    if (endedTrack) endedTrack.currentTime = 0;

    const nextIndex = (endedIndex + 1) % TRACKS.length;
    setTrackIndex(nextIndex);
    void play(nextIndex);
  }

  function toggleMute() {
    const nextMuted = !muted;
    audioRefs.current.forEach((audio) => {
      if (audio) audio.muted = nextMuted;
    });
    setMuted(nextMuted);
  }

  return (
    <aside className="soundtrack-dock" aria-label="Museum soundtrack">
      {TRACKS.map((item, index) => (
        // oxlint-disable-next-line jsx-a11y/media-has-caption -- The soundtrack is instrumental and contains no speech.
        <audio
          key={item.source}
          ref={(element) => {
            audioRefs.current[index] = element;
          }}
          src={item.source}
          preload="auto"
          autoPlay={index === 0}
          onPlay={() => setPlaying(true)}
          onPause={() => setPlaying(false)}
          onEnded={() => advancePlaylist(index)}
        />
      ))}
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
          aria-label={playing ? 'Pause museum soundtrack' : 'Play museum soundtrack'}
          aria-pressed={playing}
        >
          {playing ? <Pause aria-hidden="true" /> : <Play aria-hidden="true" />}
        </button>
        <button
          type="button"
          onClick={toggleMute}
          aria-label={muted ? 'Unmute museum soundtrack' : 'Mute museum soundtrack'}
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
