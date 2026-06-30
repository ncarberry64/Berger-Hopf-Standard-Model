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

/// Direct Cartesian boundary normalization used by the synthetic benchmark.
/// This is a coordinate utility, not a detector-propagation or tracking fit.
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
