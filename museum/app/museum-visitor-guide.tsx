'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { followExhibit } from '../lib/exhibit-navigation';
import {
  maleEnglishNarrationVoices,
  narrationVoiceKey,
  selectNarrationVoice,
} from '../lib/narration-voices';

const tourStops = [
  {
    label: 'Excitation',
    title: 'Begin with a field excitation.',
    caption:
      'Follow a disturbance as it becomes a localized mode, propagates and reaches a decay event.',
    narration:
      'Start with the lifecycle scene. BHSM interprets particle structure through geometric organization. The field lines make an excitation visible, and the changing pattern introduces the idea of a localized mode. Follow this illustrative unstable excitation through propagation to a decay event, where daughter excitations appear. The animation supplies a visual sequence; its durations, paths and outgoing modes are schematic. Use the pause button or select a phase to examine what changes. A physical decay calculation would also need the permitted interaction channels, conservation laws and a quantitative rate.',
    prompt: 'Look for the moment when the parent becomes outgoing states.',
    href: '#particle-lifecycle-theatre',
    link: 'Explore the lifecycle',
  },
  {
    label: 'Seven scales',
    title: 'Read the map from the core upward.',
    caption:
      'Seven slices connect the proposed foundation with familiar structures at increasingly large scales.',
    narration:
      'Read the scale map from bottom to top: hypersphere core; excitations and moiré-like modes; Standard Model particles; atoms and the periodic table; molecules; planets and stars; and cosmic structure. The Standard Model occupies one slice in this broader BHSM picture. The core is a proposed foundation without an assigned ordinary diameter or internal travel time. The slices organize ideas across scales, while the moiré pattern illustrates the proposed organization of modes. Select each slice to see its meaning and evidence status. Each connection still needs its own physical explanation and tests.',
    prompt:
      'Notice where the labels change from BHSM proposal to established science.',
    href: '#bhsm-scale-map',
    link: 'Explore the seven slices',
  },
  {
    label: 'Claims & context',
    title: 'Distinguish the framework from the proposal.',
    caption:
      'The particle chart presents the conventional Standard Model; its placement in BHSM is a proposed connection.',
    narration:
      'Open the Standard Model chart and look at the quarks, leptons, interaction bosons and Higgs. This is the established particle framework used as a reference in the museum. BHSM proposes a geometric interpretation and conditionally reproduces the matter and gauge ledger under stated assumptions. That conditional structural result has a specific scope. Particle masses, interaction probabilities and cosmological responses each require further physical constructions and independent checks. The conventional minimal Standard Model also leaves neutrino masses outside its original field content. Use the exhibit labels to keep established references, conditional results and proposed interpretations distinct.',
    prompt:
      'Ask which parts are measured references and which are BHSM claims.',
    href: '#standard-model-chart',
    link: 'Inspect the particle chart',
  },
  {
    label: 'Evidence & tests',
    title: 'Turn a picture into a testable question.',
    caption:
      'Trace a claim to its assumptions, calculation, comparison and remaining open questions.',
    narration:
      'Finish at the evidence guide. Choose one claim and follow its source. Look for what was assumed, what was calculated, the result’s stated scope and the observations used for comparison. A physical prediction must be fixed independently of the measured answer it will face. Historical numerical screens and certified calculations on specified backgrounds retain those classifications. Useful questions include: which observable follows from the construction, what could falsify it, and can another researcher reproduce the result? Follow the current research record for the unresolved steps. The museum invites careful exploration, independent checking and specific criticism.',
    prompt: 'Choose one claim you would like to reproduce or test.',
    href: '#museum-evidence-guide',
    link: 'Inspect the evidence guide',
  },
] as const;

export function MuseumVisitorGuide() {
  const [stopIndex, setStopIndex] = useState(0);
  const [voiceAvailable, setVoiceAvailable] = useState(false);
  const [maleVoices, setMaleVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [voicePreference, setVoicePreference] = useState('');
  const [narrationSource, setNarrationSource] = useState<'recorded' | 'device'>(
    'recorded',
  );
  const [narrating, setNarrating] = useState(false);
  const [caption, setCaption] = useState('');
  const [captionFailed, setCaptionFailed] = useState(false);
  const [voiceStatus, setVoiceStatus] = useState(
    'Andrew’s recorded natural male narration is ready. Select Read this stop aloud to begin.',
  );
  const audioRef = useRef<HTMLAudioElement>(null);
  const captionTrackRef = useRef<HTMLTrackElement>(null);
  const audioActiveRef = useRef(false);
  const audioRevisionRef = useRef(0);
  const narrationSourceRef = useRef<'recorded' | 'device'>('recorded');
  const voicePreferenceRef = useRef('');
  const refreshVoicesRef = useRef<() => void>(() => {});
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);
  const voiceTimeoutRef = useRef<number | null>(null);
  const stop = tourStops[stopIndex];
  const recordedTrack = `./learn/narration/tour-${String(stopIndex + 1).padStart(2, '0')}-andrew`;
  const selectedVoice = selectNarrationVoice(maleVoices, voicePreference);

  const stopNarration = useCallback((message = 'Narration stopped.') => {
    setCaption('');
    const utterance = utteranceRef.current;
    if (!utterance && !audioActiveRef.current) return;
    audioRevisionRef.current++;
    audioActiveRef.current = false;
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    utteranceRef.current = null;
    if (utterance) {
      utterance.onstart = null;
      utterance.onend = null;
      utterance.onerror = null;
      window.speechSynthesis.cancel();
    }
    if (voiceTimeoutRef.current !== null) {
      window.clearTimeout(voiceTimeoutRef.current);
      voiceTimeoutRef.current = null;
    }
    setNarrating(false);
    setVoiceStatus(message);
  }, []);

  useEffect(() => {
    const element = captionTrackRef.current;
    if (!element) return;
    const track = element.track;
    setCaption('');
    setCaptionFailed(false);
    // Audio elements do not draw a caption overlay. Hidden mode loads and
    // advances cues; render the active text in the visible pane below instead.
    track.mode = 'hidden';
    const onCueChange = () => {
      if (
        !audioActiveRef.current ||
        narrationSourceRef.current !== 'recorded'
      ) {
        setCaption('');
        return;
      }
      setCaption(
        Array.from(track.activeCues ?? [])
          .map((cue) => ('text' in cue ? String(cue.text) : ''))
          .filter(Boolean)
          .join('\n'),
      );
    };
    track.addEventListener('cuechange', onCueChange);
    return () => track.removeEventListener('cuechange', onCueChange);
  }, [stopIndex]);

  useEffect(() => {
    const audio = audioRef.current;
    const available =
      'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window;
    setVoiceAvailable(available);
    const refreshVoices = () => {
      if (!available) return;
      let discovered: SpeechSynthesisVoice[];
      try {
        discovered = maleEnglishNarrationVoices(
          window.speechSynthesis.getVoices(),
        );
      } catch {
        setMaleVoices([]);
        if (narrationSourceRef.current === 'device') {
          stopNarration(
            'Your browser could not load narration voices. Use recorded Andrew or the transcript.',
          );
          setVoiceStatus(
            'Your browser could not load narration voices. Use recorded Andrew or the transcript.',
          );
        }
        return;
      }
      if (
        voicePreferenceRef.current &&
        !discovered.some(
          (voice) => narrationVoiceKey(voice) === voicePreferenceRef.current,
        )
      ) {
        voicePreferenceRef.current = '';
        setVoicePreference('');
      }
      const nextVoice = selectNarrationVoice(
        discovered,
        voicePreferenceRef.current,
      );
      const speakingVoice = utteranceRef.current?.voice;
      if (
        utteranceRef.current &&
        (!nextVoice ||
          !speakingVoice ||
          narrationVoiceKey(nextVoice) !== narrationVoiceKey(speakingVoice))
      ) {
        stopNarration(
          'Available voices changed. Select Read this stop aloud to hear the selected male voice.',
        );
      }
      setMaleVoices(discovered);
      if (!utteranceRef.current && narrationSourceRef.current === 'device')
        setVoiceStatus(
          nextVoice
            ? `Ready: ${nextVoice.name}. Select Read this stop aloud to begin.`
            : 'No recognized male English voice is available in this browser yet. Refresh voices or read the complete transcript.',
        );
    };
    refreshVoicesRef.current = refreshVoices;
    refreshVoices();
    if (available)
      window.speechSynthesis.addEventListener('voiceschanged', refreshVoices);
    const stopForMusic = () =>
      stopNarration('Narration stopped while music plays.');
    const stopWhenHidden = () => {
      if (document.hidden)
        stopNarration(
          'Narration stopped when you left the page. Select Read this stop aloud to restart.',
        );
    };
    const stopFollowing = followExhibit(window, (slideId) => {
      if (slideId !== 'potential')
        stopNarration('Narration stopped when you moved to another exhibit.');
    });
    window.addEventListener('bhsm:play-music', stopForMusic);
    document.addEventListener('visibilitychange', stopWhenHidden);
    return () => {
      // React may clear the ref before passive unmount cleanup runs.
      audio?.pause();
      window.removeEventListener('bhsm:play-music', stopForMusic);
      document.removeEventListener('visibilitychange', stopWhenHidden);
      if (available)
        window.speechSynthesis.removeEventListener(
          'voiceschanged',
          refreshVoices,
        );
      refreshVoicesRef.current = () => {};
      stopFollowing();
      stopNarration();
    };
  }, [stopNarration]);

  function selectStop(next: number) {
    stopNarration(
      'Narration stopped. Select Read this stop aloud to hear the selected stop.',
    );
    setStopIndex(next);
  }

  function chooseVoice(key: string) {
    stopNarration();
    voicePreferenceRef.current = key;
    setVoicePreference(key);
    const nextVoice = selectNarrationVoice(maleVoices, key);
    setVoiceStatus(
      nextVoice
        ? `Selected: ${nextVoice.name}. Select Read this stop aloud to begin.`
        : 'No recognized male English voice is available. The complete transcript remains available.',
    );
  }

  function chooseNarrationSource(source: 'recorded' | 'device') {
    stopNarration();
    narrationSourceRef.current = source;
    setNarrationSource(source);
    setVoiceStatus(
      source === 'recorded'
        ? 'Andrew’s recorded natural male narration is ready. Select Read this stop aloud to begin.'
        : selectedVoice
          ? `Selected: ${selectedVoice.name}. Select Read this stop aloud to begin.`
          : 'No recognized male English device voice is available. Use recorded Andrew or read the transcript.',
    );
  }

  function readStop() {
    if (narrating) {
      stopNarration();
      return;
    }
    if (narrationSource === 'recorded') {
      const audio = audioRef.current;
      if (!audio) return;
      const revision = ++audioRevisionRef.current;
      audioActiveRef.current = true;
      setNarrating(true);
      setVoiceStatus('Starting Andrew’s recorded natural male narration…');
      window.dispatchEvent(new Event('bhsm:narration-start'));
      // Keep play() in the click handler to retain mobile media permission.
      void audio
        .play()
        .then(() => {
          if (audioRevisionRef.current !== revision) {
            if (!audioActiveRef.current) audio.pause();
            return;
          }
          setVoiceStatus(
            `Reading stop ${stopIndex + 1} with recorded Andrew. The visible text is the narration transcript.`,
          );
        })
        .catch(() => {
          if (audioRevisionRef.current !== revision) return;
          stopNarration(
            'Recorded Andrew could not play. Try again, choose an available male device voice, or read the transcript.',
          );
        });
      return;
    }
    if (!voiceAvailable || !selectedVoice) return;
    // Bind the actual discovered voice: leaving this unset lets the browser
    // silently choose its default, which may be a female or unidentified voice.
    const voice = selectedVoice;
    const utterance = new SpeechSynthesisUtterance(
      `${stop.title} ${stop.narration} ${stop.prompt}`,
    );
    utterance.voice = voice;
    utterance.lang = voice.lang;
    utterance.rate = 0.95;
    utteranceRef.current = utterance;
    setNarrating(true);
    setVoiceStatus(`Starting ${voice.name}…`);
    const clearTimer = () => {
      if (voiceTimeoutRef.current !== null)
        window.clearTimeout(voiceTimeoutRef.current);
      voiceTimeoutRef.current = null;
    };
    utterance.onstart = () => {
      if (utteranceRef.current !== utterance) return;
      clearTimer();
      setVoiceStatus(
        `Reading stop ${stopIndex + 1} with ${voice.name}. The visible text is the narration transcript.`,
      );
    };
    utterance.onend = () => {
      if (utteranceRef.current !== utterance) return;
      clearTimer();
      utteranceRef.current = null;
      setNarrating(false);
      setVoiceStatus(
        'Narration finished. Continue to the next stop when you are ready.',
      );
    };
    utterance.onerror = () => {
      if (utteranceRef.current !== utterance) return;
      clearTimer();
      utteranceRef.current = null;
      setNarrating(false);
      setVoiceStatus(
        `${voice.name} could not read this stop aloud. Choose another available male voice or read the complete transcript.`,
      );
    };
    window.dispatchEvent(new Event('bhsm:narration-start'));
    try {
      voiceTimeoutRef.current = window.setTimeout(() => {
        if (utteranceRef.current === utterance) {
          stopNarration(
            `${voice.name} did not start. Try another male voice or read the complete transcript below.`,
          );
        }
      }, 8000);
      window.speechSynthesis.speak(utterance);
    } catch {
      stopNarration(
        'Device narration is unavailable. Read this stop or the complete transcript below.',
      );
    }
  }

  return (
    <section
      id="museum-visitor-guide"
      className="museum-visitor-guide"
      aria-labelledby="visitor-guide-title"
    >
      <div className="visitor-guide-heading">
        <h2 id="visitor-guide-title">Choose your way in.</h2>
        <p>Start with the picture or follow the scientific record.</p>
      </div>
      <div className="visitor-paths">
        <a className="visitor-path visitor-path-idea" href="#bhsm-scale-map">
          <span className="visitor-path-number" aria-hidden="true">
            01
          </span>
          <span>
            <strong>
              Explore the idea <span aria-hidden="true">↗</span>
            </strong>
            <small>See how the seven scales fit into the BHSM picture.</small>
          </span>
        </a>
        <a
          className="visitor-path visitor-path-evidence"
          href="#museum-evidence-guide"
        >
          <span className="visitor-path-number" aria-hidden="true">
            02
          </span>
          <span>
            <strong>
              Inspect the evidence <span aria-hidden="true">↗</span>
            </strong>
            <small>Find the sources, claim boundaries and open tests.</small>
          </span>
        </a>
      </div>

      <details
        className="visitor-tour"
        onToggle={(event) => {
          if (!event.currentTarget.open)
            stopNarration('Narration stopped when the tour closed.');
        }}
      >
        <summary>
          <span>First visit? Take the three-minute tour.</span>
          <small>4 stops · about 45 seconds each</small>
        </summary>
        <div className="visitor-tour-body">
          <p className="visitor-tour-intro">
            Read a stop, explore its exhibit, then return here for the next.
            Move at your own pace; the tour advances only when you choose.
          </p>
          <div className="visitor-tour-stops" aria-label="Tour stops">
            {tourStops.map((item, index) => (
              <button
                key={item.label}
                type="button"
                aria-pressed={index === stopIndex}
                aria-controls="visitor-tour-current"
                onClick={() => selectStop(index)}
              >
                <span>{String(index + 1).padStart(2, '0')}</span>
                {item.label}
              </button>
            ))}
          </div>

          <article
            id="visitor-tour-current"
            className="visitor-tour-current"
            aria-live="polite"
            aria-atomic="true"
          >
            <p className="visitor-tour-counter">STOP {stopIndex + 1} OF 4</p>
            <h3>{stop.title}</h3>
            <p className="visitor-tour-caption">{stop.caption}</p>
            <p className="visitor-tour-narration">{stop.narration}</p>
            <p className="visitor-tour-prompt">
              <strong>Look closer.</strong> {stop.prompt}
            </p>
            <a className="visitor-tour-exhibit" href={stop.href}>
              {stop.link} <span aria-hidden="true">→</span>
            </a>
          </article>

          <div className="visitor-tour-voice">
            <div className="visitor-voice-picker">
              <label htmlFor="visitor-narration-source">Narration</label>
              <select
                id="visitor-narration-source"
                value={narrationSource}
                onChange={(event) =>
                  chooseNarrationSource(
                    event.target.value as 'recorded' | 'device',
                  )
                }
              >
                <option value="recorded">
                  Andrew · recorded natural male voice
                </option>
                <option value="device">Choose a male device voice</option>
              </select>
              <p>
                AI-generated narration · Microsoft Andrew Online (Natural).{' '}
                <a href="./learn/narration/credits.json">
                  Voice credits and recording details ↗
                </a>
              </p>
            </div>
            <audio
              ref={audioRef}
              src={`${recordedTrack}.mp3`}
              preload="none"
              onEnded={() => {
                if (!audioActiveRef.current) return;
                audioActiveRef.current = false;
                setCaption('');
                setNarrating(false);
                setVoiceStatus(
                  'Narration finished. Continue to the next stop when you are ready.',
                );
              }}
              onError={() => {
                if (audioActiveRef.current)
                  stopNarration(
                    'Recorded Andrew could not load. Choose an available male device voice or read the transcript.',
                  );
              }}
            >
              <track
                key={stopIndex}
                ref={captionTrackRef}
                kind="captions"
                src={`${recordedTrack}.vtt`}
                srcLang="en"
                label="English narration captions"
                onLoad={(event) => {
                  event.currentTarget.track.mode = 'hidden';
                }}
                onError={() => {
                  setCaption('');
                  setCaptionFailed(true);
                }}
                default
              />
            </audio>
            {narrationSource === 'recorded' && (
              <div
                className="visitor-live-captions"
                aria-label="Synchronized narration captions"
              >
                <span>CAPTIONS · STOP {stopIndex + 1}</span>
                <p>
                  {caption ||
                    (captionFailed
                      ? 'Captions could not load. The complete transcript is above.'
                      : narrating
                        ? 'Narration is playing. The complete transcript is above.'
                        : 'Select Read this stop aloud to follow synchronized captions.')}
                </p>
              </div>
            )}
            {narrationSource === 'device' && (
              <>
                <div className="visitor-voice-picker">
                  <label htmlFor="visitor-narration-voice">
                    Male narration voice
                  </label>
                  <select
                    id="visitor-narration-voice"
                    value={voicePreference}
                    disabled={!maleVoices.length}
                    onChange={(event) => chooseVoice(event.target.value)}
                    aria-describedby="visitor-voice-explanation"
                  >
                    <option value="">
                      {maleVoices.length
                        ? `Recommended · ${maleVoices[0].name}`
                        : 'No male English voice available'}
                    </option>
                    {maleVoices.map((voice) => (
                      <option
                        key={narrationVoiceKey(voice)}
                        value={narrationVoiceKey(voice)}
                      >
                        {voice.name} · {voice.lang}
                      </option>
                    ))}
                  </select>
                  <p id="visitor-voice-explanation">
                    Natural and neural male voices are preferred when your
                    browser offers them. Availability varies by device.
                  </p>
                  {selectedVoice && (
                    <p className="visitor-selected-voice">
                      <strong>Selected:</strong> {selectedVoice.name}
                    </p>
                  )}
                </div>
              </>
            )}
            <button
              type="button"
              disabled={
                narrationSource === 'device' && !selectedVoice && !narrating
              }
              onClick={readStop}
              aria-pressed={narrating}
            >
              {narrating ? '■ Stop narration' : '▶ Read this stop aloud'}
            </button>
            {narrationSource === 'device' && (
              <button
                type="button"
                className="visitor-refresh-voices"
                disabled={!voiceAvailable}
                onClick={() => refreshVoicesRef.current()}
              >
                Refresh voices
              </button>
            )}
            <p className="visitor-voice-status" role="status">
              {voiceStatus}
            </p>
            <div className="visitor-narration-downloads">
              <a
                href={`${recordedTrack}.mp3`}
                download={`BHSM-tour-stop-${stopIndex + 1}-Andrew.mp3`}
              >
                Download this stop · MP3 ↓
              </a>
              <a
                href={`${recordedTrack}.vtt`}
                download={`BHSM-tour-stop-${stopIndex + 1}-captions.vtt`}
              >
                Download captions · VTT ↓
              </a>
            </div>
          </div>

          <div className="visitor-tour-controls">
            <button
              type="button"
              disabled={stopIndex === 0}
              onClick={() => selectStop(Math.max(0, stopIndex - 1))}
            >
              ← Previous stop
            </button>
            {stopIndex < tourStops.length - 1 ? (
              <button
                type="button"
                onClick={() =>
                  selectStop(Math.min(tourStops.length - 1, stopIndex + 1))
                }
              >
                Next stop →
              </button>
            ) : (
              <button type="button" onClick={() => selectStop(0)}>
                Return to the first stop ↺
              </button>
            )}
          </div>

          <details className="visitor-tour-transcript">
            <summary>Read the complete tour transcript</summary>
            <ol>
              {tourStops.map((item) => (
                <li key={item.label}>
                  <h4>{item.title}</h4>
                  <p>{item.narration}</p>
                  <p>{item.prompt}</p>
                </li>
              ))}
            </ol>
          </details>
        </div>
      </details>
      <div className="visitor-guide-resource">
        <span>For visitors, teachers and discussion groups</span>
        <a
          href="./learn/bhsm-visitor-guide.html"
          download="BHSM-visitor-guide.html"
        >
          Download the visitor &amp; teacher guide <span>(HTML)</span> ↓
        </a>
      </div>
    </section>
  );
}
