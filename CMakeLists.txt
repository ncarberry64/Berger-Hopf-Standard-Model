cmake_minimum_required(VERSION 3.20 FATAL_ERROR)

project(BHSMCoordinateAdapter LANGUAGES CXX)

include(CheckCXXCompilerFlag)
include(CTest)

option(BUILD_ROOT_INTEGRATION "Build the optional CERN ROOT integration smoke test" OFF)
option(BUILD_NATIVE_BENCHMARK "Build the native coordinate profiling harness" ON)
option(ENABLE_AVX2 "Enable AVX2/FMA for BHSM C++ coordinate targets" OFF)
option(ENABLE_AVX512 "Enable AVX-512F/CD for BHSM C++ coordinate targets" OFF)

if(ENABLE_AVX2 AND ENABLE_AVX512)
  message(FATAL_ERROR "ENABLE_AVX2 and ENABLE_AVX512 are mutually exclusive")
endif()

add_library(bhsm_coordinate INTERFACE)
target_include_directories(
  bhsm_coordinate
  INTERFACE "${CMAKE_CURRENT_SOURCE_DIR}/integrations/cern-root/include"
)
target_compile_features(bhsm_coordinate INTERFACE cxx_std_17)

function(bhsm_require_compile_flag flag variable)
  check_cxx_compiler_flag("${flag}" "${variable}")
  if(NOT ${variable})
    message(FATAL_ERROR "Requested compiler flag is unavailable: ${flag}")
  endif()
endfunction()

if(ENABLE_AVX512)
  if(MSVC)
    bhsm_require_compile_flag("/arch:AVX512" BHSM_HAS_MSVC_AVX512)
    target_compile_options(bhsm_coordinate INTERFACE /arch:AVX512)
  else()
    bhsm_require_compile_flag("-mavx512f" BHSM_HAS_AVX512F)
    bhsm_require_compile_flag("-mavx512cd" BHSM_HAS_AVX512CD)
    target_compile_options(bhsm_coordinate INTERFACE -mavx512f -mavx512cd)
  endif()
elseif(ENABLE_AVX2)
  if(MSVC)
    bhsm_require_compile_flag("/arch:AVX2" BHSM_HAS_MSVC_AVX2)
    target_compile_options(bhsm_coordinate INTERFACE /arch:AVX2)
  else()
    bhsm_require_compile_flag("-mavx2" BHSM_HAS_AVX2)
    bhsm_require_compile_flag("-mfma" BHSM_HAS_FMA)
    target_compile_options(bhsm_coordinate INTERFACE -mavx2 -mfma)
  endif()
endif()

if(BUILD_NATIVE_BENCHMARK)
  add_executable(
    bhsm_native_coordinate_benchmark
    integrations/native-benchmark/native_coordinate_benchmark.cxx
  )
  target_link_libraries(bhsm_native_coordinate_benchmark PRIVATE bhsm_coordinate)
  add_test(
    NAME bhsm_native_coordinate_self_test
    COMMAND bhsm_native_coordinate_benchmark --self-test
  )
endif()

if(BUILD_ROOT_INTEGRATION)
  find_package(ROOT CONFIG REQUIRED COMPONENTS ROOTDataFrame)

  add_executable(
    bhsm_root_integration_smoke
    integrations/cern-root/tests/root_integration_smoke.cxx
  )
  target_link_libraries(
    bhsm_root_integration_smoke
    PRIVATE bhsm_coordinate ROOT::ROOTDataFrame
  )
  if(ROOT_CXX_STANDARD)
    set_property(
      TARGET bhsm_root_integration_smoke
      PROPERTY CXX_STANDARD "${ROOT_CXX_STANDARD}"
    )
  endif()

  add_test(NAME bhsm_root_integration_smoke COMMAND bhsm_root_integration_smoke)
endif()
