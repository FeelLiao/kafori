# 使用anaconda3镜像
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/continuumio/anaconda3:latest


# 将 Conda 添加到 PATH
#ENV PATH="/usr/local/conda/bin:$PATH"

RUN conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/ && \
    conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free/ && \
    conda config --set show_channel_urls yes

# 将项目文件复制到容器中
COPY ../backend /opt/kafori-backend

# 定位到工作目录
WORKDIR /opt/kafori-backend

# 创建 Conda 环境
RUN conda env create -f kafori_conda.yml && \
    conda clean --all --yes

# 激活 Conda 环境
RUN conda init bash
ENV CONDA_DEFAULT_ENV=kafori
ENV CONDA_PREFIX=/opt/conda/envs/kafori
ENV PATH="$CONDA_PREFIX/bin:$PATH"

# 安装 Poetry
RUN pip install poetry


RUN poetry lock && poetry install --no-root

# 暴露端口
EXPOSE 10020

# 启动 FastAPI 应用
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "10020"]