'use client';

import {
  type ReactNode,
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react';

import { slides } from '../lib/museum-slides.mjs';
import { announceExhibit } from '../lib/exhibit-navigation';
import { MuseumSoundtrack } from './museum-soundtrack';
const aliases: Record<string, string> = {
  top: 'potential',
  exhibits: 'science-predictions',
  comparisons: 'science-test',
};

function retainSlideFragment(index: number) {
  const fragment = document.getElementById(location.hash.slice(1));
  const slide = document.getElementById(slides[index][0]);
  if (!fragment || !slide?.contains(fragment))
    history.replaceState(null, '', `#${slides[index][0]}`);
}

export function MuseumDeck({ children }: { children: ReactNode }) {
  const track = useRef<HTMLDivElement>(null);
  const numberLinks = useRef<HTMLElement>(null);
  const activeIndex = useRef(0);
  const trackWidth = useRef(0);
  const navigationTarget = useRef<number | null>(null);
  const [active, setActive] = useState(0);
  const go = useCallback((index: number, smooth = true) => {
    const element = track.current;
    if (!element) return;
    const next = Math.max(0, Math.min(slides.length - 1, index));
    // A deep link may already have scrolled before hydration, so no scroll
    // event is guaranteed. Synchronize the controls and accessible slide too.
    const adjacent = Math.abs(next - activeIndex.current) === 1;
    setActive(next);
    activeIndex.current = next;
    navigationTarget.current = next;
    announceExhibit(window, slides[next][0]);
    const reduce = window.matchMedia(
      '(prefers-reduced-motion: reduce)',
    ).matches;
    element.scrollTo({
      left: next * element.clientWidth,
      behavior: smooth && adjacent && !reduce ? 'smooth' : 'instant',
    });
  }, []);

  useEffect(() => {
    const element = track.current;
    if (!element) return;
    let focusFrame = 0;
    const navigateFragment = (hash: string) => {
      const id = aliases[hash] ?? hash;
      const target = document.getElementById(id);
      const index = slides.findIndex(
        ([slideId]) =>
          slideId === id ||
          (target && document.getElementById(slideId)?.contains(target)),
      );
      if (index < 0) return false;
      go(index, false);
      // Shared atlas/tour links can point inside a slide. Reveal the owning
      // exhibit before scrolling its own vertical reading pane.
      if (target && id !== slides[index][0]) {
        const owner = document.getElementById(slides[index][0]);
        if (owner)
          owner.scrollTo({
            top:
              owner.scrollTop +
              target.getBoundingClientRect().top -
              owner.getBoundingClientRect().top -
              16,
            behavior: 'instant',
          });
        cancelAnimationFrame(focusFrame);
        focusFrame = requestAnimationFrame(() => {
          if (!target.hasAttribute('tabindex')) target.tabIndex = -1;
          target.focus({ preventScroll: true });
        });
      }
      return true;
    };
    const fromHash = () => navigateFragment(location.hash.slice(1));
    const click = (event: MouseEvent) => {
      if (
        event.defaultPrevented ||
        event.metaKey ||
        event.ctrlKey ||
        event.shiftKey ||
        event.altKey ||
        event.button !== 0
      )
        return;
      const link = (event.target as HTMLElement).closest<HTMLAnchorElement>(
        'a[href^="#"]',
      );
      if (!link) return;
      const id = link.hash.slice(1);
      if (!navigateFragment(id)) return;
      event.preventDefault();
      // Direct destinations must not animate through unrelated exhibits or
      // race a second numbered selection against an unfinished swipe.
      history.replaceState(null, '', `#${id}`);
    };
    fromHash();
    announceExhibit(window, slides[activeIndex.current][0]);
    window.addEventListener('hashchange', fromHash);
    document.addEventListener('click', click);
    trackWidth.current = element.clientWidth;
    const resize = new ResizeObserver(() => {
      trackWidth.current = element.clientWidth;
      go(activeIndex.current, false);
    });
    resize.observe(element);
    const settled = () => {
      navigationTarget.current = null;
      const index = Math.round(element.scrollLeft / element.clientWidth);
      if (index < 0 || index >= slides.length) return;
      activeIndex.current = index;
      setActive(index);
      announceExhibit(window, slides[index][0]);
      retainSlideFragment(index);
    };
    element.addEventListener('scrollend', settled);
    return () => {
      cancelAnimationFrame(focusFrame);
      window.removeEventListener('hashchange', fromHash);
      document.removeEventListener('click', click);
      resize.disconnect();
      element.removeEventListener('scrollend', settled);
    };
  }, [go]);

  useEffect(() => {
    const bar = numberLinks.current;
    const selected = bar?.querySelector<HTMLElement>('a[aria-current]');
    if (bar && selected) {
      const barBox = bar.getBoundingClientRect();
      const linkBox = selected.getBoundingClientRect();
      if (linkBox.left < barBox.left || linkBox.right > barBox.right) {
        bar.scrollTo({
          left:
            bar.scrollLeft +
            linkBox.left -
            barBox.left -
            (bar.clientWidth - linkBox.width) / 2,
          behavior: 'instant',
        });
      }
    }
    slides.forEach(([id], index) => {
      const slide = document.getElementById(id);
      if (slide) {
        slide.inert = index !== active;
        slide.setAttribute(
          'aria-label',
          `${slides[index][1]} · slide ${index + 1} of ${slides.length}`,
        );
      }
    });
  }, [active]);

  return (
    <div className="museum-deck" data-active-slide={slides[active][0]}>
      <nav className="deck-controls" aria-label="Exhibit slides">
        <button
          onClick={() => go(active - 1)}
          disabled={active === 0}
          aria-label="Previous exhibit"
        >
          ← <span>Previous</span>
        </button>
        <label>
          <span>
            EXHIBIT {String(active + 1).padStart(2, '0')} / {slides.length}
          </span>
          <select
            aria-label="Choose an exhibit"
            value={active}
            onChange={(event) => go(Number(event.target.value))}
          >
            {slides.map(([id, title], index) => (
              <option value={index} key={id}>
                {title}
              </option>
            ))}
          </select>
        </label>
        <p>
          Swipe to explore <span aria-hidden="true">↔</span>
        </p>
        <button
          onClick={() => go(active + 1)}
          disabled={active === slides.length - 1}
          aria-label="Next exhibit"
        >
          <span>Next</span> →
        </button>
      </nav>
      <nav
        ref={numberLinks}
        className="deck-numbers"
        aria-label="Jump to an exhibit"
      >
        {slides.map(([id, title], index) => (
          <a
            key={id}
            href={`#${id}`}
            title={`${String(index + 1).padStart(2, '0')} · ${title}`}
            aria-label={`Exhibit ${index + 1}: ${title}`}
            aria-current={active === index ? 'step' : undefined}
          >
            {String(index + 1).padStart(2, '0')}
          </a>
        ))}
      </nav>
      <div className="deck-progress" aria-hidden="true">
        <i style={{ width: `${((active + 1) / slides.length) * 100}%` }} />
      </div>
      {/* A focusable carousel region supports arrow-key navigation between exhibits. */}
      {/* oxlint-disable jsx-a11y/no-noninteractive-element-interactions, jsx-a11y/no-noninteractive-tabindex */}
      <section
        ref={track}
        className="museum-track"
        aria-roledescription="carousel"
        aria-label="Museum exhibits"
        tabIndex={0}
        onScroll={() => {
          const el = track.current;
          if (!el) return;
          if (el.clientWidth !== trackWidth.current) return;
          const index = Math.round(el.scrollLeft / el.clientWidth);
          // Smooth next/previous movement must not briefly select the slide
          // being left. A new swipe releases this destination immediately.
          if (
            navigationTarget.current !== null &&
            Math.abs(
              el.scrollLeft - navigationTarget.current * el.clientWidth,
            ) >= 2
          )
            return;
          navigationTarget.current = null;
          if (index >= 0 && index < slides.length) {
            activeIndex.current = index;
            setActive(index);
            announceExhibit(window, slides[index][0]);
            if (Math.abs(el.scrollLeft - index * el.clientWidth) < 2)
              retainSlideFragment(index);
          }
        }}
        onPointerDown={() => {
          navigationTarget.current = null;
        }}
        onWheel={(event) => {
          if (Math.abs(event.deltaX) > Math.abs(event.deltaY))
            navigationTarget.current = null;
        }}
        onKeyDown={(event) => {
          if (
            (event.target as HTMLElement).closest(
              'input,select,button,textarea,a,summary,[contenteditable="true"]',
            )
          )
            return;
          if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
            event.preventDefault();
            go(active + (event.key === 'ArrowRight' ? 1 : -1));
          }
        }}
      >
        {children}
      </section>
      {/* oxlint-enable jsx-a11y/no-noninteractive-element-interactions, jsx-a11y/no-noninteractive-tabindex */}
      <MuseumSoundtrack />
      <span className="sr-only" aria-live="polite">
        {slides[active][1]}, exhibit {active + 1} of {slides.length}
      </span>
    </div>
  );
}
