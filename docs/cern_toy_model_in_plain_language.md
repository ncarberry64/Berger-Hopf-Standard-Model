# The CERN toy model in plain language

## What it is

The repository includes a computational demonstration built from published
CMS Open Data. The input is a collection of muon **four-vectors**: compact
records containing each muon's energy and three components of momentum.

The demonstration converts those vectors between two equivalent coordinate
descriptions. One description is familiar and direct; the other uses the
BHSM boundary-coordinate map. It then checks whether both routes reconstruct
the same physical vector to numerical precision and measures how quickly the
calculation runs.

It is called a toy model because it isolates one small, testable piece of the
software. It is not a miniature simulation of the whole BHSM universe.

## A map analogy

Imagine receiving real airline locations written as latitude and longitude.
You design a new map projection and test it on those locations.

If the new projection is fast and lets you recover the original locations
accurately, you have validated the projection software. You have not proved a
new theory of why airplanes fly or why the Earth has its observed geology.

The CMS demonstration has the same scope:

- the “locations” are real collision-derived muon four-vectors;
- the “map projection” is the BHSM coordinate transformation;
- the round-trip error tests numerical correctness;
- the throughput test measures computational performance;
- none of this establishes BHSM as particle physics.

## What happens to the data

1. The benchmark downloads or reads the checksum-controlled CMS education
   dataset from CERN Open Data Record 303.
2. It extracts 200,000 unique muon four-vectors.
3. The timed workload repeats them ten times, producing 2,000,000 vector
   transformations per pass.
4. A scalar control, a vectorized conventional control, and the BHSM
   boundary-coordinate implementation process the same values.
5. The outputs are compared numerically and summarized with deterministic
   provenance.

No event selection is used to tune a BHSM parameter, and no measured particle
property is used to close a BHSM theorem.

## What the benchmark established

For the recorded reference run:

- the BHSM coordinate kernel processed about 35.6 million four-vectors per
  second;
- it was about 3.225 times faster than the vectorized control in that run;
- the largest absolute numerical difference was about `5.821e-11`;
- the scale-aware backward-error gate passed.

These figures describe a particular implementation, dataset, machine, and
benchmark protocol. They are software-engineering evidence, not a new
particle-physics measurement.

## Why real CERN data is useful here

Synthetic tests are excellent for exact edge cases, but real data supplies a
messy and realistic distribution of magnitudes and directions. Using
published CMS vectors therefore makes the numerical test more demanding and
more reproducible without changing its scientific scope.

The benchmark helps answer:

- Does the coordinate map behave accurately on realistic inputs?
- Does it remain stable around awkward coordinate regions?
- Can it be implemented efficiently in Python, native code, and ROOT-style
  workflows?
- Can another reviewer reproduce the same checks from named public data?

## What it does not establish

The demonstration does not:

- reconstruct detector tracks or simulate the CMS detector;
- identify new particles or interactions;
- fit Standard Model or BHSM parameters;
- test BHSM mass, mixing, scale, cosmology, or boundary-formation claims;
- validate BHSM Physics experimentally;
- imply CMS or CERN endorsement.

The precise status label is
`CERN_OPEN_DATA_FOUR_VECTOR_BENCHMARK_NOT_TRACK_RECONSTRUCTION`.

## Technical and provenance links

- [Technical benchmark report](cern_open_data_benchmark.md)
- [Animation and provenance](pr98_cms_open_data_animation.md)
- [Engine versus Physics claim boundary](engine_vs_physics_claim_boundary.md)
- [CERN Open Data Record 303](https://opendata.cern.ch/record/303)
- Dataset DOI: `10.7483/OPENDATA.CMS.4M97.3SQ9`
