#pragma once

#include <cmath>

namespace bhsm::root {

struct BoundaryState {
  double radius;
  double ux;
  double uy;
  double uz;
  double minkowski_interval;
};

/**
 * @brief Direct Cartesian boundary-coordinate normalization.
 * @note This is the chart-free coordinate utility used by the synthetic
 * benchmark and optional ROOT adapter, not a detector-propagation or track fit.
 * @see docs/coordinate_method_benchmark.md for the measured kernel definition.
 * @see https://doi.org/10.5281/zenodo.20663419 for the archived BHSM package.
 * @details Computes radius, unit direction, and Minkowski interval directly
 * from Cartesian inputs. Avoiding angular coordinates removes the polar and
 * azimuth chart seams from this specific mapping; it does not establish
 * production tracking superiority or a full BHSM manifold transformation.
 */
inline BoundaryState MapBoundaryState(
    const double t, const double x, const double y, const double z) noexcept {
  const double radius = std::sqrt(x * x + y * y + z * z);
  const double inverse_radius = radius == 0.0 ? 0.0 : 1.0 / radius;
  return {
      radius,
      x * inverse_radius,
      y * inverse_radius,
      z * inverse_radius,
      t * t - radius * radius,
  };
}

}  // namespace bhsm::root
