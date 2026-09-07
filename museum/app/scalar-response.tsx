'use client';

import { useEffect, useState } from 'react';
import { REPOSITORY } from './exhibits';

type ScalarData = {
  source_revision: string;
  source_certificate: string;
  source_data_SHA256: string;
  precision_bits: number;
  response_norm_upper: number[];
  maximum_response_upper: number;
  validation_passed: boolean;
  FULL_BHSM_COMPLETE: boolean;
};

export function ScalarResponse() {
  const [data, setData] = useState<ScalarData | null>(null);
  const [failed, setFailed] = useState(false);
  const [node, setNode] = useState(370);
  useEffect(() => {
    fetch('./data/gate7-scalar-response.json')
      .then((response) => {
        if (!response.ok) throw new Error('Missing certified data');
        return response.json();
      })
      .then((raw: unknown) => {
        const value = raw as ScalarData;
        if (value.validation_passed !== true || value.FULL_BHSM_COMPLETE !== false ||
          !Array.isArray(value.response_norm_upper) ||
          value.response_norm_upper.length !== 371 ||
          !value.response_norm_upper.every((v) => Number.isFinite(v) && v >= 0) ||
          !(value.maximum_response_upper > 0) ||
          typeof value.source_revision !== 'string' ||
          typeof value.source_certificate !== 'string') throw new Error('Invalid certified data');
        setData(value);
      })
      .catch(() => setFailed(true));
  }, []);
  const x = (index: number) => 60 + index / 370 * 600;
  const y = (value: number) => 330 - value / (data?.maximum_response_upper ?? 1) * 270;
  return (
    <section className="cms-explorer scalar-response" id="computed-data" aria-labelledby="scalar-title">
      <div className="cms-explorer-copy">
        <p className="eyebrow">Computed research data · Gate 7</p>
        <h2 id="scalar-title">Follow a certified response.</h2>
        <p>These values come from an actual BHSM calculation across 370 intervals.
          The curve bounds how the central scalar response accumulates along the
          frozen computational path. Each node is a saved result.</p>
        <p>This is a numerical certificate for one response component. It is not
          an experimental measurement, a particle mass, or a complete physical
          solution. The full transverse and neighborhood proof remains open.</p>
        {data && <>
          <label htmlFor="scalar-node">Computational node <strong>{node} / 370</strong></label>
          <input id="scalar-node" type="range" min={0} max={370} value={node}
            onChange={(event) => setNode(Number(event.target.value))} />
          <p className="scalar-reading" aria-live="polite">
            Response norm upper bound: <strong>{data.response_norm_upper[node].toPrecision(8)}</strong>
          </p>
          <p>{data.precision_bits}-bit interval arithmetic · 371 nodes</p>
          <div className="scalar-links">
            <a href={`${REPOSITORY}/blob/${data.source_revision}/${data.source_certificate}`}>Source certificate ↗</a>
            <a href="./data/gate7-scalar-response.json" download>Download plotted data ↗</a>
          </div>
        </>}
      </div>
      <div className="cms-event-instrument">
        {!data ? <output>{failed ? 'The certified dataset could not be loaded.' : 'Loading certified response data…'}</output> : <>
          <svg viewBox="0 0 710 400" aria-labelledby="scalar-chart-title scalar-chart-desc">
            <title id="scalar-chart-title">Certified scalar response norm along the frozen path</title>
            <desc id="scalar-chart-desc">Node {node}: upper bound {data.response_norm_upper[node]}.
              Horizontal axis: computational node, zero to 370. Vertical axis: response norm upper bound.</desc>
            {[0, 0.25, 0.5, 0.75, 1].map((fraction) => <g key={fraction}>
              <line x1={60} x2={660} y1={y(fraction * data.maximum_response_upper)} y2={y(fraction * data.maximum_response_upper)} stroke="#244149" />
              <text x={50} y={y(fraction * data.maximum_response_upper) + 5} textAnchor="end" fill="#bdd0d4" fontSize={15}>
                {(fraction * data.maximum_response_upper).toFixed(1)}
              </text>
            </g>)}
            <text x={60} y={30} fill="#bdd0d4" fontSize={17}>Response norm upper bound</text>
            <polyline points={data.response_norm_upper.map((value, index) => `${x(index)},${y(value)}`).join(' ')}
              fill="none" stroke="#43d7e8" strokeWidth={3} />
            <line x1={x(node)} x2={x(node)} y1={50} y2={330} stroke="#e2b85b" strokeDasharray="5 5" />
            <circle cx={x(node)} cy={y(data.response_norm_upper[node])} r={6} fill="#e2b85b" />
            {[0, 100, 200, 300, 370].map((index) => <text key={index} x={x(index)} y={355} textAnchor="middle" fill="#bdd0d4" fontSize={15}>{index}</text>)}
            <text x={360} y={390} textAnchor="middle" fill="#bdd0d4" fontSize={17}>Computational node</text>
          </svg>
          <p className="scalar-provenance">Frozen source revision {data.source_revision.slice(0, 8)}.
            The downloadable data includes the full source hash and claim boundaries.</p>
        </>}
      </div>
    </section>
  );
}
