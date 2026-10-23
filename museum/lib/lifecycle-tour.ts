// Presentation timing only. These seconds are not a physical model clock.
export const lifecycleSceneDurations = [6, 6, 6, 10, 6, 6] as const;
export const lifecycleScaleDuration = lifecycleSceneDurations.reduce((sum, value) => sum + value, 0);
const scaleCount = 4;

export function lifecycleFrame(seconds: number) {
  if (!Number.isFinite(seconds) || seconds < 0) throw new RangeError('Tour time must be finite and nonnegative.');
  const offset = seconds % (lifecycleScaleDuration * scaleCount);
  const scale = Math.floor(offset / lifecycleScaleDuration);
  let remaining = offset - scale * lifecycleScaleDuration;
  let stage = 0;
  while (stage < lifecycleSceneDurations.length - 1 && remaining >= lifecycleSceneDurations[stage]) {
    remaining -= lifecycleSceneDurations[stage];
    stage += 1;
  }
  const progress = remaining / lifecycleSceneDurations[stage];
  return { stage, scale, progress, daughtersVisible: stage === 3 && progress >= 0.4 };
}

export function lifecycleOffset(scale: number, stage: number, progress = 0) {
  if (!Number.isInteger(scale) || scale < 0 || scale >= scaleCount || !Number.isInteger(stage) || stage < 0 || stage >= lifecycleSceneDurations.length || !Number.isFinite(progress) || progress < 0 || progress >= 1) {
    throw new RangeError('Choose an existing scale, scene and progress in [0, 1).');
  }
  return scale * lifecycleScaleDuration + lifecycleSceneDurations.slice(0, stage).reduce((sum, value) => sum + value, 0) + lifecycleSceneDurations[stage] * progress;
}
