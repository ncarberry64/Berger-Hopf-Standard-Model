'use client';
import { ForceGeometry } from './force-geometry';
import { ForceLines } from './force-lines';
import references from './reference-data.json';
import { SCIENCE } from './exhibits';

export function ForceTree({
  motion,
  setMotion,
}: {
  motion: boolean;
  setMotion: (value: boolean) => void;
}) {
  return (
    <div className="force-tree">
      <ForceGeometry motion={motion} setMotion={setMotion} />
      <section
        className="force-lines-restored"
        aria-label="Original force lines"
      >
        <p className="eyebrow">The original geometric hierarchy</p>
        <h4>Follow the force lines.</h4>
        <ForceLines motion={motion} />
      </section>
      <details className="console-details">
        <summary>
          Explore the science · interpretation and conventional references
        </summary>
        <p>
          In BHSM’s geometric picture, condensed Aether manifests as energy /
          mass-energy, while stretched Aether manifests as regular spacetime
          support. Strong is the most concentrated separated regime; weak,
          electromagnetic and gravitational manifestations occur through and
          within progressively stretched support. The other interactions are
          interpreted as arising in that stretch. The ordering is conceptual,
          not a measured energy axis or a calculated coupling-merger curve.
        </p>
        <p>
          In this BHSM interpretation, Aether denotes the lack of spacetime,
          before extended spacetime support arises through stretch. It names the
          underlying energy–geometry interpretation; it does not introduce a
          material ether or a preferred frame. A mathematical map from stretch
          and condensation to physical modes, normalized interactions and scales
          remains open. E = mc² expresses the conventional mass–energy relation,
          not a BHSM derivation of core energy.
        </p>
        <p>
          <a
            href={`${SCIENCE}/docs/BHSM_AUTHOR_AETHER_SCALE_CLARIFICATION_20260908.md`}
          >
            BHSM ontology and scope ↗
          </a>
        </p>
        <p>
          Conventional references below retain their source definitions. They
          are independent comparison quantities, not values assigned to the
          geometric nodes. In particular, the Z reference energy is not a
          strong-force onset or a BHSM concentration scale.
        </p>
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Conventional quantity</th>
                <th>Conventional reference value</th>
                <th>Meaning</th>
              </tr>
            </thead>
            <tbody>
              {references.energy_scales.map((r) => (
                <tr key={r.id}>
                  <th>{r.label}</th>
                  <td>{r.scale}</td>
                  <td>
                    {r.meaning} <a href={r.source}>Source ↗</a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </div>
  );
}
