'use client';

import { Music2, Pause, Play, Volume2, VolumeX } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { exhibitSoundtracks } from '../lib/exhibit-soundtracks.mjs';
import { followExhibit } from '../lib/exhibit-navigation';
import { createExhibitSoundtrack } from '../lib/exhibit-soundtrack';
import { manageSoundtrackSession } from '../lib/soundtrack-session';

export function MuseumSoundtrack() {
  const audioRef = useRef<HTMLAudioElement>(null);
  const controller = useRef<ReturnType<typeof createExhibitSoundtrack> | null>(
    null,
  );
  const [trackIndex, setTrackIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [muted, setMuted] = useState(false);
  const track = exhibitSoundtracks[trackIndex];

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    const isActive = () => !document.hidden && document.hasFocus();
    const player = createExhibitSoundtrack({
      audio,
      isActive,
      onChange: setPlaying,
      // Only an explicitly requested music action can start or retry playback.
      onNeedGesture: () => {},
    });
    controller.current = player;
    player.select(exhibitSoundtracks[0].source);
    const playMusic = () => {
      void player.play().catch(() => {});
    };
    // The entrance's explicitly labeled music action shares the Play control.
    window.addEventListener('bhsm:play-music', playMusic);
    const stopFollowing = followExhibit(window, (slideId) => {
      const index = exhibitSoundtracks.findIndex(
        (soundtrack) => soundtrack.slideId === slideId,
      );
      if (index < 0) return;
      setTrackIndex(index);
      audio.dataset.exhibitMusic = exhibitSoundtracks[index].slideId;
      player.select(exhibitSoundtracks[index].source);
    });
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
      players: [audio],
      isActive,
      channel,
      owner: crypto.randomUUID(),
      onChange: setPlaying,
      onBeforeSuspend: player.suspend,
      onSuspend: () => {},
    });
    return () => {
      window.removeEventListener('bhsm:play-music', playMusic);
      stopFollowing();
      player.dispose();
      stopSession();
      controller.current = null;
    };
  }, []);

  function togglePlayback() {
    const player = controller.current;
    const audio = audioRef.current;
    if (!player || !audio) return;
    if (!audio.paused) player.pause();
    else void player.play().catch(() => {});
  }

  function toggleMute() {
    const nextMuted = !muted;
    if (audioRef.current) audioRef.current.muted = nextMuted;
    setMuted(nextMuted);
  }

  return (
    <aside className="soundtrack-dock" aria-label="Exhibit soundtrack">
      {/* Reuse the visitor-started element and loop this exhibit's music. */}
      {/* oxlint-disable-next-line jsx-a11y/media-has-caption -- Instrumental music has no speech. */}
      <audio
        ref={audioRef}
        data-exhibit-music={track.slideId}
        src={exhibitSoundtracks[0].source}
        preload="none"
        playsInline
        loop
      />
      <div className="soundtrack-mark" aria-hidden="true">
        <Music2 />
      </div>
      <div className="soundtrack-copy" aria-live="polite" aria-atomic="true">
        <small>
          Exhibit music · {trackIndex + 1}/{exhibitSoundtracks.length}
        </small>
        <strong title={track.title}>{track.title}</strong>
        <span className="soundtrack-credit">
          <a href={track.creditUrl} target="_blank" rel="noreferrer">
            {track.artist} ↗
          </a>
          <a href={track.licenseUrl} target="_blank" rel="noreferrer">
            License ↗
          </a>
          {/* oxlint-disable-next-line next/no-html-link-for-pages -- Static credit record. */}
          <a href="./soundtrack-credits.html" target="_blank" rel="noreferrer">
            Credits ↗
          </a>
        </span>
      </div>
      <div className="soundtrack-controls">
        <button
          type="button"
          onClick={togglePlayback}
          aria-label={playing ? 'Pause exhibit music' : 'Play exhibit music'}
          aria-pressed={playing}
        >
          {playing ? <Pause aria-hidden="true" /> : <Play aria-hidden="true" />}
        </button>
        <button
          type="button"
          onClick={toggleMute}
          aria-label={muted ? 'Unmute exhibit music' : 'Mute exhibit music'}
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
