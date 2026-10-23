// A normalized field illustration only: this radial displacement is not a
// computed metric, physical surface, expansion factor or calibrated amplitude.
export function cosmologySurfacePoint(
  direction: readonly number[],
  value: number,
  maximumMagnitude: number,
) {
  const signed =
    maximumMagnitude > 0
      ? Math.max(-1, Math.min(1, value / maximumMagnitude))
      : 0;
  const radius = 1 + 0.26 * signed;
  return { point: direction.map((component) => component * radius), signed };
}
