FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND=noninteractive TZ=Asia/Shanghai

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates git build-essential tzdata \
 && rm -rf /var/lib/apt/lists/*

# 仅 x86_64
ARG MINIFORGE_VERSION=25.3.0-3
RUN curl -fsSL -o /tmp/miniforge.sh \
      https://github.com/conda-forge/miniforge/releases/download/${MINIFORGE_VERSION}/Miniforge3-${MINIFORGE_VERSION}-Linux-x86_64.sh; \
    bash /tmp/miniforge.sh -b -p /opt/conda; \
    rm /tmp/miniforge.sh
ENV CONDA_DIR=/opt/conda
ENV PATH=${CONDA_DIR}/bin:$PATH

RUN conda config --set show_channel_urls yes

WORKDIR /app
# 先复制环境文件以利用缓存
COPY backend/kafori_conda.yml backend/kafori_conda.yml
RUN mamba env create -f backend/kafori_conda.yml && mamba clean -afy
ENV CONDA_DEFAULT_ENV=kafori
ENV PATH=/opt/conda/envs/kafori/bin:$PATH

# 再复制剩余代码
COPY . .

ENV POETRY_VIRTUALENVS_CREATE=false POETRY_NO_INTERACTION=1
WORKDIR /app/backend
RUN poetry install --no-root

WORKDIR /app

ARG APP_VERSION=dev
ARG GIT_COMMIT=unknown
LABEL org.opencontainers.image.title="kafori-backend" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.revision="${GIT_COMMIT}" \
      org.opencontainers.image.source="https://github.com/FeelLiao/kafori"

EXPOSE 10020
CMD ["conda", "run", "-n", "kafori", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10020"]