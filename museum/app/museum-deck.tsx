'use client';

import {
  type ReactNode,
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react';

const slides = [
  ['potential', 'Welcome'],
  ['science-predictions', 'Matter'],
  ['science-decays', 'Collisions'],
  ['science-magnetic', 'Magnetism'],
  ['science-test', 'Comparisons'],
  ['science-unification', 'Forces'],
  ['research-exhibit', 'CMS & research'],
  ['details', 'Evidence & methods'],
  ['creator', 'Scientific record'],
  ['other-work', 'Cosmology · response'],
  ['cosmology-original', 'Cosmology · original'],
  ['museum-exit', 'Sources & links'],
];
const aliases: Record<string, string> = {
  top: 'potential',
  exhibits: 'science-predictions',
  comparisons: 'science-test',
};

export function MuseumDeck({ children }: { children: ReactNode }) {
  const track = useRef<HTMLDivElement>(null);
  const activeIndex = useRef(0);
  const trackWidth = useRef(0);
  const [active, setActive] = useState(0);
  const go = useCallback((index: number, smooth = true) => {
    const element = track.current;
    if (!element) return;
    const next = Math.max(0, Math.min(slides.length - 1, index));
    // A deep link may already have scrolled before hydration, so no scroll
    // event is guaranteed. Synchronize the controls and accessible slide too.
    setActive(next);
    activeIndex.current = next;
    const reduce = window.matchMedia(
      '(prefers-reduced-motion: reduce)',
    ).matches;
    element.scrollTo({
      left: next * element.clientWidth,
      behavior: smooth && !reduce ? 'smooth' : 'instant',
    });
  }, []);

  useEffect(() => {
    const element = track.current;
    if (!element) return;
    const fromHash = () => {
      const hash = location.hash.slice(1);
      const id = aliases[hash] ?? hash;
      const index = slides.findIndex(([slideId]) => slideId === id);
      if (index >= 0) go(index, false);
    };
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
      const index = slides.findIndex(
        ([slideId]) => slideId === (aliases[id] ?? id),
      );
      if (index < 0) return;
      event.preventDefault();
      go(index);
    };
    fromHash();
    window.addEventListener('hashchange', fromHash);
    document.addEventListener('click', click);
    trackWidth.current = element.clientWidth;
    const resize = new ResizeObserver(() => {
      trackWidth.current = element.clientWidth;
      go(activeIndex.current, false);
    });
    resize.observe(element);
    return () => {
      window.removeEventListener('hashchange', fromHash);
      document.removeEventListener('click', click);
      resize.disconnect();
    };
  }, [go]);

  useEffect(() => {
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
    <div className="museum-deck">
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
          if (index >= 0 && index < slides.length) {
            activeIndex.current = index;
            setActive(index);
            if (Math.abs(el.scrollLeft - index * el.clientWidth) < 2)
              history.replaceState(null, '', `#${slides[index][0]}`);
          }
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
      <span className="sr-only" aria-live="polite">
        {slides[active][1]}, exhibit {active + 1} of {slides.length}
      </span>
    </div>
  );
}
