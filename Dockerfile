# 基于官方 Python 3.13 镜像
FROM python:3.13-slim
# 使用anaconda3镜像
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/continuumio/anaconda3:latest


# 将 Conda 添加到 PATH
ENV PATH="/usr/local/conda/bin:$PATH"

RUN conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/ && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free/ && \
    conda config --set show_channel_urls yes

# 创建 Conda 环境
COPY kafori_conda.yml /kafori_conda.yml
RUN conda env create -f /kafori_conda.yml && \
    conda clean --all --yes

# 激活 Conda 环境
RUN conda init bash
ENV CONDA_DEFAULT_ENV=kafori
ENV CONDA_PREFIX=/opt/conda/envs/kafori
ENV PATH="$CONDA_PREFIX/bin:$PATH"

# 安装 Poetry
RUN pip install poetry

# 将项目文件复制到容器中
COPY . /opt/kafori

# 安装项目依赖
WORKDIR /opt/kafori
RUN poetry lock && poetry install --no-root

# 暴露端口
EXPOSE 10020

# 启动 FastAPI 应用
CMD ["fastapi", "run", "backend.main:app", "--port", "10020"]