FROM python:3.12-slim
WORKDIR /opt/bhsm
COPY . .
RUN python -m pip install --no-cache-dir -e .
ENV OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
CMD ["python", "tools/institutional_check.py", "--smoke"]
