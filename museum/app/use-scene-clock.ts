'use client';

import { useEffect, useRef, useState } from 'react';
import { slides } from '../lib/museum-slides.mjs';
import {
  createSceneTransport,
  type MusicMotionMode,
} from '../lib/music-motion';

const slideSelector = slides.map(([id]) => `#${id}`).join(',');

export function useSceneClock<T extends HTMLElement = HTMLDivElement>(
  running: boolean,
  stopAt = Infinity,
  minimumVisibility = 0,
  musicMode: MusicMotionMode = 'musical',
) {
  const ref = useRef<T>(null);
  const [clock] = useState(() => createSceneTransport(musicMode));
  const [time, setTime] = useState(0);
  useEffect(() => {
    const scene = ref.current;
    if (!running || !scene) return;
    let visible = false;
    const slideId = scene.closest(slideSelector)?.id;
    const observer = new IntersectionObserver(
      ([entry]) => {
        visible =
          entry.isIntersecting && entry.intersectionRatio >= minimumVisibility;
        if (!visible) clock.suspend();
      },
      { threshold: minimumVisibility },
    );
    observer.observe(scene);
    const timer = window.setInterval(() => {
      const active =
        scene.closest('.museum-deck')?.getAttribute('data-active-slide') ===
        slideId;
      if (!visible || document.hidden || !active) {
        clock.suspend();
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
      const next = clock.tick(
        performance.now() / 1000,
        synchronized
          ? {
              slideId: slideId!,
              source: audio.currentSrc || audio.src,
              seconds: audio.currentTime,
              seeking: audio.seeking,
            }
          : undefined,
        stopAt,
      );
      scene.dataset.musicSync = synchronized ? 'on' : 'off';
      scene.dataset.sceneTime = next.toFixed(4);
      setTime(next);
      if (next >= stopAt) window.clearInterval(timer);
    }, 50);
    return () => {
      observer.disconnect();
      window.clearInterval(timer);
      clock.suspend();
      scene.dataset.musicSync = 'off';
    };
  }, [running, stopAt, minimumVisibility, musicMode, clock]);
  return { ref, time };
}
