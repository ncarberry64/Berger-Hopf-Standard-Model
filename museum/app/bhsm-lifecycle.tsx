'use client';

import { useState } from 'react';
import { ScienceConsole, useSceneClock } from './science-console';
import { lifecycleFrame, lifecycleOffset } from '../lib/lifecycle-tour';

const stages = [
  { name: 'Excitation', verb: 'A disturbance propagates.', question: 'What carries the signal?', text: 'A propagating spacetime signal is the starting idea. A photon supplies the example. Excitation alone does not imply an envelope or an encapsulated object.' },
  { name: 'Envelope formation', verb: 'An interface forms around organization.', question: 'What sustains the distinction?', text: 'An operative interface develops around an organized configuration in its environment. The inherited organization—the “baton”—belongs to its spacetime history.' },
  { name: 'Encapsulation', verb: 'Boundary support becomes dominant.', question: 'What supports the boundary?', text: 'At a declared scale and in a declared environment, the formed boundary becomes the dominant support relative to the continuing differential. The object can persist in this regime.' },
  { name: 'Decay', verb: 'A parent changes into successors.', question: 'Which outgoing channels are available?', text: 'An organized parent can relax or transform through permitted channels. A decay is not automatically complete boundary loss, and an unresolved channel is not a forbidden one.' },
  { name: 'Collisions', verb: 'Histories meet at a new event.', question: 'What survives or reorganizes?', text: 'An encounter can scatter, preserve, merge or disrupt configurations. Its outgoing history follows a new event; the collision does not rewind the earlier formation event.' },
  { name: 'De-encapsulation', verb: 'The enclosing organization is lost or converted.', question: 'What loses its surface manifestation?', text: 'Loss or conversion of an organized spacetime manifestation differs from the disappearance of every product. BHSM’s sustained “black-hole fire” is a proposed interface process; loss of an incoming object and loss of the whole configuration are different events.' },
];

const contextIndex = [0, 1, 2, 3, 4, 6];

const scales = [
  {
    name: 'Quantum', caption: 'Signals & particle organization',
    contexts: [
      'A photon supplies the signal example. Cancellation at one detector output, absorption and transfer are different outcomes.',
      'Fermionic organization is the BHSM envelope example. This is a proposed description, not a claim that fermions cannot interfere.',
      'A proposed boundary must specify which interaction channels are blocked. Particle statistics alone cannot establish hard isolation.',
      'A conventional negative-muon decay produces an electron, an electron antineutrino and a muon neutrino.',
      'Incoming particle states can scatter or produce new outgoing states. A geometric picture does not supply the event’s probability.',
      'For μ− → e− + ν̄e + νμ, all three outgoing particles count, including the two neutrinos.',
      'The proposed loss and return of surface manifestation needs a phase-compatible correspondence. No trajectory or elapsed time is assigned inside the core.',
    ],
    anchor: 'Muon decay gives a concrete daughter ledger: an electron and two neutrinos.',
    anchorURL: 'https://pdg.lbl.gov/2025/reviews/rpp2025-rev-muon-decay-params.pdf',
    anchorLabel: 'Conventional reference · PDG muon decay',
  },
  {
    name: 'Matter', caption: 'Bound systems & material organization',
    contexts: [
      'Energy and disturbances can pass through a material system. The signal and the object carrying it are separate levels of description.',
      'A bound system has internal organization and interactions with its surroundings. An ordinary material surface generally transmits through some channels.',
      'Persistence provides a question to investigate, not a measured isolation threshold. Material enclosure and BHSM hard encapsulation are distinct.',
      'Dissociation or relaxation redistributes an initial configuration into fragments, radiation or heat; the governing channels depend on the system.',
      'A molecular encounter can preserve, rearrange or break bonds. These are material mechanisms viewed through the common organizational questions.',
      'Count fragments alongside emitted radiation and energy transferred to the environment. A visible fragment count is only part of the ledger.',
      'Breakup illustrates loss of organization. Identifying a BHSM de-encapsulation or core transition requires an additional physical construction.',
    ],
    anchor: 'Large molecules can interfere. Organization and coherence must be assessed separately.',
    anchorURL: 'https://doi.org/10.1038/s41567-019-0663-9',
    anchorLabel: 'Experimental anchor · molecular interference',
  },
  {
    name: 'Stars', caption: 'Stellar support & compact configurations',
    contexts: [
      'Radiation and disturbances propagate in and around a star. The star’s collective organization is a larger-scale question.',
      'Stellar structure depends on support, gravity and environment. A drawn surface is a schematic interface, not an identified BHSM hard boundary.',
      'BHSM asks when boundary support could dominate. Frame dragging alone does not prove encapsulation, a horizon or an isolation threshold.',
      'Stellar evolution can redistribute matter and radiation and leave a remnant. “Decay” is an organizational comparison here, with its own stellar physics.',
      'A compact-star merger is a useful collision example: the outgoing history includes radiation, ejecta and a remnant.',
      'Include emitted light, gravitational radiation and ejected matter. Observed outgoing flux and a complete daughter inventory are different quantities.',
      'The sustained black-hole process and quiet neutron-star endpoint are separate proposed processes within this theory in work. Neither has a rate or maximum mass supplied here.',
    ],
    anchor: 'GW170817 connects a neutron-star merger with gravitational waves and electromagnetic counterparts.',
    anchorURL: 'https://dcc.ligo.org/LIGO-P1700294-v7/public',
    anchorLabel: 'Observational anchor · GW170817 collaboration',
  },
  {
    name: 'Galaxies & cosmos', caption: 'Collective history & cosmic organization',
    contexts: [
      'Light carries information between systems. Collective organization and the propagation of one signal occupy different descriptive scales.',
      'BHSM proposes a role for collective history, rotation and boundary formation. A galactic outline in this drawing is not a measured enclosing skin.',
      'The proposal must face rotation, dispersion, lensing and global balance together. Neither current rotation nor size alone establishes encapsulation.',
      'Relaxation and dispersal can spread structure into a smoother spacetime state. Local smoothness or heat death still has spacetime; it is not the core.',
      'Galaxy encounters redistribute stars and gas. Shocked gas and renewed star formation illustrate reorganization at this scale.',
      'Follow remnants, new structures, radiation and dispersed material. A new organized system can become the parent in another history.',
      'A terminal cosmic core correspondence is a proposed special branch. It cannot be inferred from ordinary dispersal or from a quiet detector.',
    ],
    anchor: 'Gas shocks in the interacting Antennae galaxies illustrate collective reorganization.',
    anchorURL: 'https://arxiv.org/abs/astro-ph/0502464',
    anchorLabel: 'Observational anchor · Antennae gas shocks',
  },
];

function Organization({ scale, x, y, size = 1, phase }: { scale: number; x: number; y: number; size?: number; phase: number }) {
  return (
    <g transform={`translate(${x} ${y}) scale(${size})`} className="lifecycle-organization">
      <g transform={`rotate(${phase * 9})`}>
        {scale === 0 && <><ellipse rx="38" ry="12" /><ellipse rx="16" ry="38" transform="rotate(35)" /><ellipse rx="16" ry="38" transform="rotate(-35)" /><circle r="4" fill="currentColor" /></>}
        {scale === 1 && <><path d="M-26 18L0-25L28 18Z" />{[[-26, 18], [0, -25], [28, 18]].map(([cx, cy], i) => <circle key={i} cx={cx} cy={cy} r="13" fill="#121924" />)}</>}
        {scale === 2 && <><circle r="29" />{Array.from({ length: 12 }, (_, i) => <path key={i} transform={`rotate(${i * 30})`} d="M0-35V-44" />)}<circle r="18" opacity=".4" /></>}
        {scale === 3 && <>{[0, 1, 2].map(i => <path key={i} transform={`rotate(${i * 120})`} d="M0 0C-10-28 28-42 39-18C51 8 24 42-13 34" />)}<circle r="6" fill="currentColor" /></>}
      </g>
    </g>
  );
}

function LifecycleScene({ stage, scale, time, progress }: { stage: number; scale: number; time: number; progress: number }) {
  const pulse = Math.sin(time * 1.5);
  const wave = Array.from({ length: 100 }, (_, i) => `${i ? 'L' : 'M'}${35 + i * 2.2},${155 + Math.sin(i * .2 - time * 2) * Math.exp(-(((i - 50) / 31) ** 2)) * 22}`).join(' ');
  const decay = stage === 3;
  const release = stage === 5;
  const reveal = Math.max(0, Math.min(1, (progress - .35) / .3));
  const parentX = decay ? 230 : 330;
  const formation = Math.min(1, progress * 1.4);
  const meet = Math.min(1, progress * 2);
  const scatter = Math.max(0, progress * 2 - 1);
  const daughterLabels = [
    ['e−', 'ν̄e', 'νμ'],
    ['Fragments', 'Radiation', 'Heat'],
    ['Remnant', 'Radiation', 'Ejecta'],
    ['Structures', 'Radiation', 'Dispersed'],
  ][scale];
  return (
    // oxlint-disable-next-line jsx-a11y/prefer-tag-over-role -- This computed SVG is the image; an HTML img cannot contain its drawing.
    <svg className="lifecycle-scene" viewBox="0 0 760 310" role="img" aria-labelledby="lifecycle-scene-title lifecycle-scene-desc">
      <title id="lifecycle-scene-title">{`${stages[stage].name} at the ${scales[scale].name.toLowerCase()} scale`}</title>
      <desc id="lifecycle-scene-desc">A conceptual spacetime-side animation. The envelope forms around organization, boundary support strengthens, decay transforms the parent and reveals daughter products within the decay scene, two incoming histories collide, and an opening contour represents de-encapsulation. No physical time, size, core interior or calculated rate is shown.</desc>
      <path className="lifecycle-guide" d="M30 155H730" />
      <text x="34" y="285" className="lifecycle-scene-note">SPACETIME-SIDE SCHEMATIC · NO PHYSICAL SIZE OR TIME SCALE</text>
      {stage === 0 ? <>
        <path d={wave} className="lifecycle-signal" />
        <path d="M290 155H630M619 148L630 155L619 162" className="lifecycle-signal" opacity=".55" />
        <circle cx={290 + progress * 340} cy="155" r="5" fill="#71e5eb" />
        <text x="35" y="230">Signal</text><text x="450" y="115">Propagation</text>
      </> : <>
        {stage === 4 && <>
          <Organization scale={scale} x={170 + 170 * meet - 100 * scatter} y={155 - 70 * scatter} size={.8} phase={time} />
          <ellipse cx={170 + 170 * meet - 100 * scatter} cy={155 - 70 * scatter} rx="59" ry="66" className="lifecycle-boundary" />
          <Organization scale={scale} x={590 - 170 * meet + 100 * scatter} y={155 + 70 * scatter} size={.8} phase={time} />
          <ellipse cx={590 - 170 * meet + 100 * scatter} cy={155 + 70 * scatter} rx="59" ry="66" className="lifecycle-boundary" />
          <circle cx="380" cy="155" r={18 + 20 * Math.sin(Math.PI * progress)} fill="#ffbc77" opacity={Math.sin(Math.PI * progress) * .2} />
          <text x="280" y="40">Encounter → new history</text>
          <text x="270" y="285">Preserve · scatter · reorganize</text>
        </>}
        {stage !== 4 && <>
          <g opacity={decay ? 1 - reveal * .55 : 1}>
            <Organization scale={scale} x={parentX} y={155} size={decay ? 1.1 - reveal * .4 : release ? .75 : 1.15} phase={time} />
            <ellipse cx={parentX} cy="155" rx={stage === 1 ? 60 + formation * 23 : 83 + pulse * 2} ry={stage === 1 ? 66 + formation * 22 : 88 + pulse * 2}
              className={`lifecycle-boundary ${stage === 2 ? 'lifecycle-hard' : ''} ${release ? 'lifecycle-open' : ''}`}
              style={release ? { strokeDasharray: `${270 - progress * 150} ${40 + progress * 90}` } : undefined}
              strokeDasharray={stage === 1 ? '560' : undefined} strokeDashoffset={stage === 1 ? 560 * (1 - formation) : undefined}
              strokeWidth={stage === 2 ? 2 + progress * 4 : undefined} />
          </g>
          {stage === 2 && <ellipse cx="330" cy="155" rx="95" ry="100" className="lifecycle-boundary lifecycle-outer" opacity={.2 + progress * .5} />}
        </>}
        {decay && <>
          <text x="135" y="40">{scale === 0 ? 'Parent: μ−' : 'Parent configuration'}</text>
          <path d="M325 155H420M409 147L420 155L409 163" className="lifecycle-outgoing" strokeDasharray="110" strokeDashoffset={110 * (1 - Math.min(1, progress * 2.5))} />
          <text x="340" y="122">Decay</text>
          <g opacity={reveal} data-result-of="decay">
            <path d="M455 60H440V255H455" className="lifecycle-outgoing" />
            <text x="470" y="35">Result: daughters</text>
            <Organization scale={scale} x={510} y={82} size={.45} phase={time} />
            <path d="M484 155q8-18 16 0t16 0t16 0t16 0" className="lifecycle-signal" />
            <g className="lifecycle-products">{[0, 1, 2, 3, 4].map(i => <circle key={i} cx={484 + i * 13} cy={226 + Math.sin(i * 3 + time) * 9} r="3" />)}</g>
            <text x="580" y="88">{daughterLabels[0]}</text><text x="580" y="160">{daughterLabels[1]}</text><text x="580" y="232">{daughterLabels[2]}</text>
          </g>
          <text x="140" y="285">Parent transforms</text>
        </>}
        {release && <>
          <path d="M440 155H605M595 147L605 155L595 163" className="lifecycle-outgoing" opacity={.3 + progress * .7} />
          <path d="M470 100q15-24 30 0t30 0M480 215q15-24 30 0t30 0" className="lifecycle-signal" opacity={progress} />
          <text x="470" y="60">Conversion / release</text>
          <text x="245" y="275">Enclosure opens</text>
        </>}
        {!decay && !release && stage !== 4 && <>
          <path d="M440 155H535M525 148L535 155L525 162" className="lifecycle-outgoing" />
          <text x="475" y="117">{stage === 2 ? 'Persistence' : 'Exchange'}</text>
          <text x="255" y="40">{stage === 2 ? 'Boundary support' : 'Interface forms'}</text>
          <text x="245" y="275">{stage === 2 ? 'Dominant boundary' : 'Organized state'}</text>
        </>}
      </>}
    </svg>
  );
}

export function BHSMLifecycle({ motion, setMotion }: { motion: boolean; setMotion: (value: boolean) => void }) {
  const [tour, setTour] = useState(true);
  const [anchor, setAnchor] = useState({ offset: 0, time: 0 });
  const { ref, time } = useSceneClock(motion && tour);
  const position = anchor.offset + (tour ? Math.max(0, time - anchor.time) : 0);
  const { stage, scale, progress, daughtersVisible } = lifecycleFrame(position);
  const hold = (nextScale: number, nextStage: number) => {
    setAnchor({ offset: lifecycleOffset(nextScale, nextStage, .85), time });
    setTour(false);
  };
  const toggleTour = () => {
    setAnchor({ offset: position, time });
    if (!motion) { setMotion(true); setTour(true); }
    else setTour(!tour);
  };
  return (
    <ScienceConsole id="bhsm-lifecycle" number="02" label="Fundamental BHSM · the common frame" title="One frame. Across the scales." intro="Excitation, maintained organization and boundary change: BHSM uses a common frame to connect signals, matter, stars and cosmic structure. Follow the same questions as the scale changes." accent="cyan">
      <div className="lifecycle" ref={ref} data-stage={stage} data-scale={scale} data-playing={tour && motion}>
        <p className="lifecycle-proposal">BHSM — theory in work · 22 October 2026</p>
        <fieldset className="lifecycle-scale" aria-label="Choose a scale">
          {scales.map((s, i) => <button key={s.name} type="button" onClick={() => hold(i, stage)} aria-pressed={scale === i}>{s.name}</button>)}
        </fieldset>
        <div className="lifecycle-playback" aria-live="polite"><span>{tour && motion ? 'Auto-playing' : 'Paused'} · {scales[scale].name} · {stage + 1} / {stages.length}</span><span>Next scale: {scales[(scale + 1) % scales.length].name}</span></div>
        <div className="lifecycle-theatre">
          <LifecycleScene stage={stage} scale={scale} time={time} progress={progress} />
          <div className="lifecycle-focus" aria-live="polite" aria-atomic="true">
            <p className="eyebrow">{stages[stage].name}</p>
            <h4>{stages[stage].verb}</h4>
            <p>{stages[stage].text}</p>
            <p className="lifecycle-context"><b>{scales[scale].name}:</b> {scales[scale].contexts[contextIndex[stage]]}</p>
            {stage === 3 && <div className="lifecycle-daughter-result" data-visible={daughtersVisible}>
              <span>Decay result → Daughters</span>
              <h5>{daughtersVisible ? 'The outgoing descendants' : 'The parent transforms first'}</h5>
              <p>{daughtersVisible ? 'Daughters are the products of this decay: descendant excitations, matter, radiation and distributed thermal products.' : 'The decay is the change of the parent. Its resulting daughters appear as the transformation develops.'}</p>
              {daughtersVisible && <p>{scales[scale].contexts[5]}</p>}
            </div>}
          </div>
        </div>
        <p className="lifecycle-diagram-caption">Spacetime-side schematic · shapes identify the selected scale; no physical size or time scale is shown.</p>
        <fieldset className="lifecycle-stages" aria-label="Explore the common frame">
          {stages.map((s, i) => <button type="button" key={s.name} aria-pressed={stage === i} onClick={() => hold(scale, i)}>{s.name}{i === 3 && <small>Result: daughters</small>}</button>)}
        </fieldset>
        <div className="lifecycle-tour">
          <p>The tour starts automatically, then repeats at the next scale. Select a scene or scale to pause and inspect it. Presentation order is a reading guide; physical histories can branch.</p>
          <button type="button" onClick={toggleTour} aria-pressed={tour && motion}>{tour && motion ? 'Pause tour' : 'Play tour'}</button>
        </div>
        <div className="lifecycle-branches">
          <div><span>Organization</span><p>Excitation → operative envelope → possible encapsulation</p></div>
          <div><span>Possible histories</span><p>Persistence · decay · collision · conversion or release</p></div>
          <div><span>Decay outcome</span><p>Parent → decay → daughter products. Those products can start new organized histories.</p></div>
        </div>
        <div className="lifecycle-common">
          <p className="eyebrow">What stays common</p>
          <h4>What propagates? What maintains the boundary? What survives?</h4>
          <p>The frame repeats these questions across scales. The mechanisms, environment, interaction channels and physical equations must be specified for each system.</p>
          <p className="lifecycle-selected-question">Now asking: {stages[stage].question}</p>
        </div>
        <p className="lifecycle-anchor"><b>{scales[scale].anchorLabel}:</b> {scales[scale].anchor} <a href={scales[scale].anchorURL}>Read the source ↗</a></p>
        <details className="console-details">
          <summary>The core, hard boundaries and the exceptional terminal branch</summary>
          <p>In this theory in work the common core has no ordinary space or time: no distance, duration, trajectory or clock. Abstract harmonic labels do not become frequencies in hertz until a spacetime reconstruction and clock calibration are supplied. The drawing shows only the spacetime side.</p>
          <p>A hard boundary means bilateral noninteraction through the specified interior/exterior channels. An ordinary transmitting surface is different. Exterior gravity and boundary response are separate questions.</p>
          <p>The exceptional terminal proposal can have exactly zero newly produced spacetime daughters. It requires a derived core correspondence and conservation accounting; it does not erase earlier radiation or matter, and cannot be inferred from silence in a detector.</p>
          <p>These are configuration, environment and scale regimes, not exclusive particle-statistics classes or a mandatory sequence. The animation supplies no physical rate, lifetime or threshold.</p>
          {/* oxlint-disable-next-line next/no-html-link-for-pages -- This source is a static Markdown file, not a Next.js page. */}
          <a href="./research/lifecycle-core-surface-amendment-20261022.md">Read the complete October 22 core/surface source ↗</a>
        </details>
        <div className="lifecycle-next"><a href="#berger-hopf">Explore the geometry behind the frame →</a><a href="#science-decays">Follow collisions and daughters →</a><a href="#cosmology-original">Explore the cosmic proposal →</a></div>
      </div>
    </ScienceConsole>
  );
}
