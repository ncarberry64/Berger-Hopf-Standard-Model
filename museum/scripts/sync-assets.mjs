import { cp, mkdir, readdir, rm } from 'node:fs/promises';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const museumRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const sourceRoot = resolve(museumRoot, '..', 'docs', 'assets');
const cmsSourceRoot = join(sourceRoot, 'pr98_cms_open_data_animation');
const publicRoot = resolve(museumRoot, 'public');
const targetRoot = resolve(publicRoot, 'exhibits');

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
  'bhsm_physical_identification_bridge',
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

await rm(targetRoot, { recursive: true, force: true });
await mkdir(targetRoot, { recursive: true });

for (const name of names) {
  await cp(join(sourceRoot, name), join(targetRoot, name));
}

const cmsNames = [
  'pr98_cms_engine_validation.png',
  'pr98_cms_engine_validation.svg',
  'pr98_cms_engine_validation_continuous.gif',
];
for (const name of cmsNames) {
  await cp(join(cmsSourceRoot, name), join(targetRoot, name));
}

await cp(
  join(cmsSourceRoot, 'pr98_cms_engine_validation.png'),
  join(publicRoot, 'og.png'),
);

console.log(
  `Synced ${names.length + cmsNames.length} provenance-tracked museum assets.`,
);
