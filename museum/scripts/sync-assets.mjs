import { cp, mkdir, readdir, rm } from 'node:fs/promises';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const museumRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const sourceRoot = resolve(museumRoot, '..', 'docs', 'assets');
const publicRoot = resolve(museumRoot, 'public');
const targetRoot = resolve(publicRoot, 'exhibits');
const cmsSourceRoot = join(sourceRoot, 'pr98_cms_open_data_animation');

if (relative(publicRoot, targetRoot).startsWith('..')) {
  throw new Error('Refusing to sync outside museum/public.');
}

const exhibitBases = [
  'bhsm_geometry_to_prediction',
  'bhsm_universal_predictive_engine',
  'bhsm_spectral_forecast',
  'bhsm_muon_g2_pipeline',
  'bhsm_collision_predictor',
  'bhsm_decay_stability_engine',
  'bhsm_no_fit_firewall',
];
const allowedNames = new Set([
  ...exhibitBases.flatMap((base) => [
    `${base}.png`,
    `${base}.svg`,
    `${base}_animated.gif`,
  ]),
  'bhsm_readme_visual_status.json',
]);
const names = (await readdir(sourceRoot)).filter((name) =>
  allowedNames.has(name),
);
const cmsNames = [
  'pr98_cms_engine_validation_continuous.gif',
  'pr98_cms_engine_validation.svg',
];

await mkdir(targetRoot, { recursive: true });

for (const existing of await readdir(targetRoot)) {
  await rm(join(targetRoot, existing), { recursive: true, force: true });
}

for (const name of names) {
  await cp(join(sourceRoot, name), join(targetRoot, name));
}

for (const name of cmsNames) {
  await cp(join(cmsSourceRoot, name), join(targetRoot, name));
}

await cp(
  join(sourceRoot, 'bhsm_geometry_to_prediction.png'),
  join(publicRoot, 'og.png'),
);

console.log(
  `Synced ${names.length + cmsNames.length} provenance-tracked museum assets.`,
);
