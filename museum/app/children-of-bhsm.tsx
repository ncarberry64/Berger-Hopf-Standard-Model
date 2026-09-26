const foundations = [
  ['Core / topology', 'Knots · fundamental structure'],
  ['Modes', 'Vibrations · harmonics · fields'],
  ['Geometry', 'Symmetry · space · dimensions'],
];
const families = [
  { name: 'Quarks', particles: ['u', 'c', 't', 'd', 's', 'b'], tone: 'quarks' },
  {
    name: 'Leptons',
    particles: ['e', 'μ', 'τ', 'νₑ', 'νμ', 'ντ'],
    tone: 'leptons',
  },
  {
    name: 'Gauge bosons',
    particles: ['g', 'γ', 'Z', 'W⁺', 'W⁻'],
    tone: 'bosons',
  },
  { name: 'Scalar', particles: ['H'], tone: 'scalar' },
];
const structures = [
  ['Hadrons', 'Quarks & gluons'],
  ['Nuclei', 'Protons & neutrons'],
  ['Atoms', 'Nuclei & electrons'],
  ['Molecules', 'Chemical bonds'],
  ['Matter', 'Solid · liquid · gas · plasma'],
  ['Astronomical structures', 'Planets · stars · galaxies · cosmic web'],
];

function StructureMark({ kind }: { kind: number }) {
  return (
    <svg viewBox="0 0 80 54" aria-hidden="true" focusable="false">
      {kind === 1 ? (
        <g fill="none" stroke="currentColor">
          <path d="M3 27Q12 2 21 27T39 27T57 27T75 27" />
          <path d="M3 27Q21 47 39 27T75 27" opacity=".55" />
        </g>
      ) : kind === 2 ? (
        <g fill="none" stroke="currentColor">
          <circle cx="40" cy="27" r="23" />
          <ellipse cx="40" cy="27" rx="10" ry="23" />
          <ellipse cx="40" cy="27" rx="23" ry="9" />
          <path d="M17 27H63M40 4V50" opacity=".5" />
        </g>
      ) : kind === 0 || kind === 5 ? (
        <g fill="none" stroke="currentColor" strokeWidth="1">
          {Array.from({ length: 5 }, (_, i) => (
            <ellipse
              key={i}
              cx="40"
              cy="27"
              rx={27 - i * 3}
              ry="12"
              transform={`rotate(${i * 36} 40 27)`}
            />
          ))}
        </g>
      ) : kind === 4 ? (
        <g fill="currentColor" fillOpacity=".25" stroke="currentColor">
          {[
            [32, 17],
            [45, 17],
            [25, 28],
            [39, 28],
            [52, 28],
            [32, 39],
            [45, 39],
          ].map(([x, y], i) => (
            <circle key={i} cx={x} cy={y} r="7" />
          ))}
        </g>
      ) : kind === 8 ? (
        <g fill="none" stroke="currentColor">
          {[0, 1, 2, 3].map((i) => (
            <ellipse
              key={i}
              cx="40"
              cy="27"
              rx={9 + i * 8}
              ry={3 + i * 4}
              transform="rotate(-20 40 27)"
            />
          ))}
          <circle cx="40" cy="27" r="4" fill="currentColor" />
        </g>
      ) : (
        <g stroke="currentColor" fill="none">
          <path d="M18 34L33 17L51 31L65 14M33 17L38 42L51 31" opacity=".65" />
          {[
            [18, 34],
            [33, 17],
            [51, 31],
            [65, 14],
            [38, 42],
          ]
            .slice(0, kind === 3 ? 3 : 5)
            .map(([x, y], i) => (
              <circle
                key={i}
                cx={x}
                cy={y}
                r={i === 1 ? 6 : 4}
                fill="currentColor"
                fillOpacity=".2"
              />
            ))}
        </g>
      )}
    </svg>
  );
}

export function ChildrenOfBHSM() {
  return (
    <section className="bhsm-children" aria-labelledby="children-title">
      <header className="children-heading">
        <div>
          <p className="eyebrow">Different scales · one connected story</p>
          <h2 id="children-title">
            Children <em>of</em> BHSM
          </h2>
        </div>
        <p>From deep structure to a universe of structure.</p>
      </header>
      <div className="children-map">
        <div className="children-foundations">
          <h3>
            01 <span>Proposed foundations</span>
          </h3>
          <ol>
            {foundations.map(([name, caption], i) => (
              <li key={name}>
                <StructureMark kind={i} />
                <div>
                  <strong>{name}</strong>
                  <small>{caption}</small>
                </div>
                {i < 2 && (
                  <span className="children-step" aria-hidden="true">
                    ↓
                  </span>
                )}
              </li>
            ))}
          </ol>
        </div>
        <span className="children-bridge" aria-hidden="true">
          →
        </span>
        <div className="children-particles">
          <h3>
            02 <span>Standard Model particle table</span>
          </h3>
          <p>One layer in the proposed BHSM child graph</p>
          <div className="children-families">
            {families.map(({ name, particles, tone }) => (
              <div className={`children-family children-${tone}`} key={name}>
                <h4>{name}</h4>
                <div>
                  {particles.map((p) => (
                    <span key={p}>{p}</span>
                  ))}
                </div>
                {tone === 'scalar' && <small>Higgs boson</small>}
              </div>
            ))}
          </div>
        </div>
        <span className="children-bridge" aria-hidden="true">
          →
        </span>
        <div className="children-structures">
          <h3>
            03 <span>Structure across scales</span>
          </h3>
          <ol>
            {structures.map(([name, caption], i) => (
              <li key={name}>
                <StructureMark kind={i + 3} />
                <div>
                  <strong>{name}</strong>
                  <small>{caption}</small>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </div>
      <p className="children-scope">
        A conceptual map inspired by Children of BHSM. The core–modes–geometry
        connections are proposed BHSM relationships; a complete physical
        derivation remains open. Particle families and larger structures are
        established categories, not new predictions of this diagram.
      </p>
    </section>
  );
}
