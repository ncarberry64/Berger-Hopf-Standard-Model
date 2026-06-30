#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <vector>

#include "BHSMCoordinate.hxx"

namespace {

using Clock = std::chrono::steady_clock;

struct State {
  double t;
  double x;
  double y;
  double z;
};

struct Output {
  double radius;
  double ux;
  double uy;
  double uz;
  double interval;
};

using Kernel = Output (*)(const State&);

Output angular_map(const State& state) {
  constexpr double tolerance = 32.0 * 2.2204460492503131e-16;
  const double rho = std::hypot(state.x, state.y);
  const double radius = std::hypot(rho, state.z);
  double ux = 0.0;
  double uy = 0.0;
  double uz = 0.0;
  if (radius != 0.0) {
    if (rho <= tolerance * radius) {
      ux = state.x / radius;
      uy = state.y / radius;
      uz = state.z / radius;
    } else {
      const double phi = std::atan2(state.y, state.x);
      const double theta = std::atan2(rho, state.z);
      const double sin_theta = std::sin(theta);
      ux = sin_theta * std::cos(phi);
      uy = sin_theta * std::sin(phi);
      uz = std::cos(theta);
    }
  }
  return {radius, ux, uy, uz, state.t * state.t - radius * radius};
}

Output direct_map(const State& state) {
  const auto mapped = bhsm::root::MapBoundaryState(state.t, state.x, state.y, state.z);
  return {mapped.radius, mapped.ux, mapped.uy, mapped.uz, mapped.minkowski_interval};
}

std::vector<double> split_numeric_csv(const std::string& line) {
  std::vector<double> values;
  std::size_t start = 0;
  std::size_t column = 0;
  while (start <= line.size()) {
    const auto stop = line.find(',', start);
    const auto token = line.substr(start, stop == std::string::npos ? stop : stop - start);
    if (column > 0) {
      values.push_back(std::strtod(token.c_str(), nullptr));
    }
    ++column;
    if (stop == std::string::npos) {
      break;
    }
    start = stop + 1;
  }
  return values;
}

std::vector<State> load_dimuon_csv(const std::string& path, std::size_t replication) {
  std::ifstream input(path);
  if (!input) {
    throw std::runtime_error("cannot open CMS dimuon CSV: " + path);
  }
  std::string line;
  std::getline(input, line);
  std::vector<State> unique;
  while (std::getline(input, line)) {
    const auto row = split_numeric_csv(line);
    if (row.size() < 19) {
      throw std::runtime_error("unexpected CMS dimuon CSV row width");
    }
    unique.push_back({row[2], row[3], row[4], row[5]});
    unique.push_back({row[10], row[11], row[12], row[13]});
  }
  std::vector<State> states;
  states.reserve(unique.size() * replication);
  for (std::size_t index = 0; index < replication; ++index) {
    states.insert(states.end(), unique.begin(), unique.end());
  }
  return states;
}

double run_kernel(const std::vector<State>& states, Kernel kernel) {
  double checksum = 0.0;
  for (const auto& state : states) {
    const auto output = kernel(state);
    checksum += output.radius + output.ux + output.uy + output.uz + output.interval;
  }
  return checksum;
}

int self_test() {
  const std::array<State, 4> states{{
      {2.0, 3.0, 4.0, 0.0},
      {5.0, 0.0, 0.0, 5.0},
      {3.0, -2.0, 0.0, 1.0},
      {1.0, 0.0, 0.0, 0.0},
  }};
  for (const auto& state : states) {
    const auto angular = angular_map(state);
    const auto direct = direct_map(state);
    const std::array<double, 5> lhs{
        angular.radius, angular.ux, angular.uy, angular.uz, angular.interval};
    const std::array<double, 5> rhs{
        direct.radius, direct.ux, direct.uy, direct.uz, direct.interval};
    for (std::size_t index = 0; index < lhs.size(); ++index) {
      if (std::abs(lhs[index] - rhs[index]) > 1.0e-12) {
        std::cerr << "native kernel equivalence self-test failed\n";
        return 1;
      }
    }
  }
  return 0;
}

}  // namespace

int main(int argc, char** argv) {
  std::string kernel_name = "direct";
  std::string csv_path;
  std::size_t repeats = 5;
  std::size_t replication = 10;
  bool run_self_test = false;
  for (int index = 1; index < argc; ++index) {
    const std::string argument = argv[index];
    if (argument == "--self-test") {
      run_self_test = true;
    } else if (argument == "--kernel" && index + 1 < argc) {
      kernel_name = argv[++index];
    } else if (argument == "--csv" && index + 1 < argc) {
      csv_path = argv[++index];
    } else if (argument == "--repeats" && index + 1 < argc) {
      repeats = std::stoul(argv[++index]);
    } else if (argument == "--replication-factor" && index + 1 < argc) {
      replication = std::stoul(argv[++index]);
    } else {
      std::cerr << "unknown or incomplete argument: " << argument << "\n";
      return 2;
    }
  }
  if (run_self_test) {
    return self_test();
  }
  if (csv_path.empty() || repeats == 0 || replication == 0) {
    std::cerr << "--csv, positive --repeats, and positive --replication-factor are required\n";
    return 2;
  }

  const Kernel kernel = kernel_name == "direct" ? direct_map :
                        kernel_name == "angular" ? angular_map : nullptr;
  if (kernel == nullptr) {
    std::cerr << "--kernel must be direct or angular\n";
    return 2;
  }

  try {
    const auto states = load_dimuon_csv(csv_path, replication);
    run_kernel(std::vector<State>(states.begin(), states.begin() + std::min<std::size_t>(states.size(), 10000)), kernel);
    std::vector<double> timings;
    timings.reserve(repeats);
    double checksum = 0.0;
    for (std::size_t repeat = 0; repeat < repeats; ++repeat) {
      const auto start = Clock::now();
      checksum = run_kernel(states, kernel);
      const auto elapsed = std::chrono::duration<double>(Clock::now() - start).count();
      timings.push_back(elapsed);
    }
    std::sort(timings.begin(), timings.end());
    const double median = timings[timings.size() / 2];
    std::cout << std::setprecision(17)
              << "{\"status\":\"NATIVE_COORDINATE_PROFILE_KERNEL\","
              << "\"kernel\":\"" << kernel_name << "\","
              << "\"states\":" << states.size() << ','
              << "\"repeats\":" << repeats << ','
              << "\"median_seconds\":" << median << ','
              << "\"states_per_second\":" << states.size() / median << ','
              << "\"checksum\":" << checksum << "}\n";
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    return 1;
  }
  return 0;
}
