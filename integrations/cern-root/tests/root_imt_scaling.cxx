#include <ROOT/RDataFrame.hxx>
#include <ROOT/RDFHelpers.hxx>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

#include "BHSMCoordinate.hxx"

int main(int argc, char** argv) {
  unsigned int threads = 1;
  unsigned long long entries = 1'000'000;
  unsigned int repeats = 3;
  for (int index = 1; index < argc; ++index) {
    const std::string argument = argv[index];
    if (argument == "--threads" && index + 1 < argc) {
      threads = static_cast<unsigned int>(std::stoul(argv[++index]));
    } else if (argument == "--entries" && index + 1 < argc) {
      entries = std::stoull(argv[++index]);
    } else if (argument == "--repeats" && index + 1 < argc) {
      repeats = static_cast<unsigned int>(std::stoul(argv[++index]));
    } else {
      std::cerr << "unknown or incomplete argument: " << argument << '\n';
      return 2;
    }
  }
  if (threads == 0 || entries == 0 || repeats == 0) {
    std::cerr << "threads, entries, and repeats must be positive\n";
    return 2;
  }

  ROOT::EnableImplicitMT(threads);
  std::vector<double> timings;
  timings.reserve(repeats);
  double checksum = 0.0;
  for (unsigned int repeat = 0; repeat < repeats; ++repeat) {
    const auto start = std::chrono::steady_clock::now();
    ROOT::RDataFrame source(entries);
    auto mapped = source
                      .Define("x", [](ULong64_t index) {
                        constexpr double values[] = {3.0, 5.0, 8.0};
                        return values[index % 3];
                      }, {"rdfentry_"})
                      .Define("y", [](ULong64_t index) {
                        constexpr double values[] = {4.0, 12.0, 15.0};
                        return values[index % 3];
                      }, {"rdfentry_"})
                      .Define("z", [] { return 0.0; })
                      .Define("t", [] { return 20.0; })
                      .Define(
                          "bhsm_radius",
                          [](double x, double y, double z) {
                            return bhsm::root::MapBoundaryState(20.0, x, y, z).radius;
                          },
                          {"x", "y", "z"});
    auto sum = mapped.Sum<double>("bhsm_radius");
    checksum = *sum;
    timings.push_back(
        std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count());
  }
  ROOT::DisableImplicitMT();

  std::sort(timings.begin(), timings.end());
  const double median = timings[timings.size() / 2];
  const auto groups = entries / 3;
  const auto remainder = entries % 3;
  const double expected = static_cast<double>(groups) * 35.0 +
                          (remainder >= 1 ? 5.0 : 0.0) +
                          (remainder >= 2 ? 13.0 : 0.0);
  const bool checksum_ok = std::abs(checksum - expected) <= 1.0e-9 * std::max(1.0, expected);

  std::cout << std::setprecision(17)
            << "{\"status\":\"ROOT_IMT_SCALING_ROW\","
            << "\"threads\":" << threads << ','
            << "\"entries\":" << entries << ','
            << "\"repeats\":" << repeats << ','
            << "\"median_seconds\":" << median << ','
            << "\"entries_per_second\":" << entries / median << ','
            << "\"checksum\":" << checksum << ','
            << "\"expected_checksum\":" << expected << ','
            << "\"checksum_ok\":" << (checksum_ok ? "true" : "false") << "}\n";
  return checksum_ok ? 0 : 1;
}
