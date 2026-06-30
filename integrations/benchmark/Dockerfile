FROM python:3.12-slim

WORKDIR /opt/bhsm
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir -e ".[benchmark]"

ENV BHSM_BENCHMARK_EVENTS=1000000
ENV BHSM_BENCHMARK_REPEATS=3
CMD ["python", "-m", "bhsm.interface.benchmarks.coordinate_benchmark", "--events", "1000000", "--boundary-fraction", "0.35", "--repeats", "3", "--summary", "--output", "/tmp/results.json", "--markdown", "/tmp/results.md", "--plot", "/tmp/results.png"]
