'use client';

import { useEffect, useRef, useState } from 'react';
import { slides } from '../lib/museum-slides.mjs';
import {
  createSceneTransport,
  createPhraseSequence,
  musicBeat,
  type MusicMotionMode,
} from '../lib/music-motion';

const slideSelector = slides.map(([id]) => `#${id}`).join(',');

export function useSceneClock<T extends HTMLElement = HTMLDivElement>(
  running: boolean,
  stopAt = Infinity,
  minimumVisibility = 0,
  musicMode: MusicMotionMode = 'musical',
  phraseSeconds?: number,
) {
  const ref = useRef<T>(null);
  const [clock] = useState(() => createSceneTransport(musicMode));
  const [sequence] = useState(() =>
    phraseSeconds ? createPhraseSequence(phraseSeconds) : null,
  );
  const [frame, setFrame] = useState<{
    time: number;
    beat: number | null;
    phraseTime: number;
  }>({
    time: 0,
    beat: null,
    phraseTime: 0,
  });
  const rhythm = useRef<{
    beat: number;
    time: number;
    tempoBpm: number;
  } | null>(null);
  useEffect(() => {
    const scene = ref.current;
    if (!running || !scene) return;
    let visible = false;
    const slideId = scene.closest(slideSelector)?.id;
    const observer = new IntersectionObserver(
      ([entry]) => {
        visible =
          entry.isIntersecting && entry.intersectionRatio >= minimumVisibility;
        if (!visible) {
          clock.suspend();
          sequence?.suspend();
        }
      },
      { threshold: minimumVisibility },
    );
    observer.observe(scene);
    let request = 0;
    let paintedAt = -Infinity;
    const animate = (now: number) => {
      request = window.requestAnimationFrame(animate);
      const active =
        scene.closest('.museum-deck')?.getAttribute('data-active-slide') ===
        slideId;
      if (!visible || document.hidden || !active) {
        clock.suspend();
        sequence?.suspend();
        scene.dataset.musicSync = 'off';
        return;
      }
      const audio = document.querySelector<HTMLAudioElement>(
        'audio[data-exhibit-music]',
      );
      const synchronized =
        musicMode !== 'independent' &&
        audio &&
        !audio.paused &&
        !audio.ended &&
        audio.dataset.exhibitMusic === slideId;
      const mediaSeconds = audio?.currentTime ?? 0;
      const next = clock.tick(
        now / 1000,
        synchronized
          ? {
              slideId: slideId!,
              source: audio.currentSrc || audio.src,
              seconds: mediaSeconds,
              seeking: audio.seeking,
            }
          : undefined,
        stopAt,
      );
      const measured =
        synchronized && musicMode === 'musical'
          ? musicBeat(slideId!, mediaSeconds)
          : null;
      if (measured) rhythm.current = { ...measured, time: next };
      const beat =
        measured?.beat ??
        (rhythm.current
          ? rhythm.current.beat +
            ((next - rhythm.current.time) * rhythm.current.tempoBpm) / 60
          : null);
      const phraseTime = sequence?.tick(next, beat) ?? next;
      scene.dataset.musicSync = synchronized ? 'on' : 'off';
      scene.dataset.sceneTime = next.toFixed(4);
      if (sequence) scene.dataset.phraseTime = phraseTime.toFixed(4);
      if (beat !== null) scene.dataset.musicBeat = beat.toFixed(4);
      // Beat accents render on every display frame. Expensive ambient diagrams
      // keep their existing 20-fps budget while sampling the media every frame.
      if (beat !== null || now - paintedAt >= 50 || next >= stopAt) {
        setFrame({ time: next, beat, phraseTime });
        paintedAt = now;
      }
      if (next >= stopAt) window.cancelAnimationFrame(request);
    };
    request = window.requestAnimationFrame(animate);
    return () => {
      observer.disconnect();
      window.cancelAnimationFrame(request);
      clock.suspend();
      sequence?.suspend();
      scene.dataset.musicSync = 'off';
    };
  }, [running, stopAt, minimumVisibility, musicMode, clock, sequence]);
  function restartSequence() {
    sequence?.restart();
    setFrame((previous) => ({ ...previous, phraseTime: 0 }));
  }
  return { ref, ...frame, restartSequence };
}
