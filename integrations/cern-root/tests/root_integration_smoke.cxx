#include <ROOT/RDataFrame.hxx>

#include <cmath>
#include <cstddef>
#include <iostream>

#include "BHSMCoordinate.hxx"

int main() {
  ROOT::RDataFrame source(3);
  auto mapped = source
                    .Define("t", [] { return 2.0; })
                    .Define("x", [] { return 3.0; })
                    .Define("y", [] { return 4.0; })
                    .Define("z", [] { return 0.0; })
                    .Define(
                        "bhsm_state",
                        [](double t, double x, double y, double z) {
                          return bhsm::root::MapBoundaryState(t, x, y, z);
                        },
                        {"t", "x", "y", "z"})
                    .Define(
                        "bhsm_radius",
                        [](const bhsm::root::BoundaryState& state) {
                          return state.radius;
                        },
                        {"bhsm_state"});

  auto radii = mapped.Take<double>("bhsm_radius");
  if (radii->size() != 3) {
    std::cerr << "unexpected RDataFrame result size\n";
    return 1;
  }
  for (const double radius : *radii) {
    if (std::abs(radius - 5.0) > 1.0e-12) {
      std::cerr << "coordinate adapter returned an unexpected radius\n";
      return 1;
    }
  }
  return 0;
}
