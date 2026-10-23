import example from './blackhole-tracker-example.json' with { type: 'json' };
import pilot from './blackhole-tracker-pilot.json' with { type: 'json' };
import joint from './blackhole-tracker-joint.json' with { type: 'json' };
import atlas from './blackhole-tracker-atlas.json' with { type: 'json' };

// The same IAU nominal solar mass parameter and units as the pinned product.
const GM_SUN = 1.3271244e20;
const C = 299792458;
const PC = 3.085677581491367e16;
const RAD_MAS = 206264806.24709636;
export const trackerExample = example;
export const trackerPilot = pilot;
export const trackerJoint = joint;
export const trackerAtlas = atlas;
export const trackerVersion = '0.2.0rc5';
export const trackerAnimationRevision = example.source_revision;
export const trackerCodeRevision = '8ca349fa8eb5c54c661a022790ae915d05060b59';
export const trackerPaperRevision = '5a785ea64fcdce58779a0f7431a6a218b3deadd4';
export const trackerReviewerRevision = '1cdd464c9a70d211b37008ed7f912be346a58e8f';

export function trackerCenter(epoch: number): [number, number] {
  if (!Number.isFinite(epoch) || epoch < 2015 || epoch > 2025)
    throw new RangeError('Exhibit epoch must be between 2015 and 2025.');
  return [0, 1].map(
    (i) =>
      example.truth.center_mas[i] +
      (epoch - example.reference_epoch_yr) *
        example.truth.proper_motion_mas_yr[i],
  ) as [number, number];
}

/** Noise-free ordinary monopole forward view, not an optimizer or R1 solver. */
export function trackerFrame(epoch: number, massScale = 1) {
  if (!Number.isFinite(massScale) || massScale < 0.5 || massScale > 2)
    throw new RangeError('Exhibit mass scale must be between 0.5 and 2.');
  const center = trackerCenter(epoch);
  const g = example.geometry;
  const mass = example.truth.mass_msun * massScale;
  const theta =
    Math.sqrt(
      (((4 * GM_SUN * mass) / (C * C * PC)) * g.D_ls_pc) /
        (g.D_l_pc * g.D_s_pc),
    ) * RAD_MAS;
  const timeScale = ((4 * GM_SUN * mass) / C ** 3) * (1 + g.z_l);
  const pairs = example.truth.source_mas.slice(0, 3).map((source) => {
    const beta = [source[0] - center[0], source[1] - center[1]];
    const separation = Math.hypot(...beta);
    const u = separation / theta;
    const root = Math.sqrt(u * u + 4);
    const image = (sign: number) =>
      beta.map(
        (b, i) =>
          center[i] + (((theta * (u + sign * root)) / 2) * b) / separation,
      );
    const amplification = (u * u + 2) / (u * root);
    return {
      source,
      plus: image(1),
      minus: image(-1),
      lnFluxRatio: Math.log((amplification + 1) / (amplification - 1)),
      delaySeconds:
        timeScale * ((u * root) / 2 + Math.log((root + u) / (root - u))),
    };
  });
  return { epoch, mass, center, theta, pairs };
}
