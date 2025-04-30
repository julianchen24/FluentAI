FROM ubuntu:22.04

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    MARIAN_PATH="/marian-dev/build"

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libboost-all-dev \
    libprotobuf-dev \
    protobuf-compiler \
    libssl-dev \
    intel-mkl-full \
    python3 \
    python3-pip \
    python3-dev \
    git \
    wget \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN git clone https://github.com/marian-nmt/marian-dev.git /marian-dev \
    && cd /marian-dev \
    && mkdir build \
    && cd build \
    && cmake .. -DUSE_SENTENCEPIECE=ON -DUSE_MKL=ON -DCOMPILE_CUDA=OFF -DMKL_ROOT=/opt/intel/mkl -DCMAKE_BUILD_TYPE=Release \
    && make -j1

ENV PATH="/marian-dev/build:${PATH}"

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p app/models logs

RUN echo '#!/bin/bash\n\
sed -i "s|/mnt/c/Users/julia/FluentAI/marian-dev/build/marian-decoder|${MARIAN_PATH}/marian-decoder|g" /app/app/services/marian_runtime.py\n\
exec uvicorn app.main:app --host 0.0.0.0 --port 8000\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/status || exit 1

EXPOSE 8000

CMD ["/app/entrypoint.sh"]