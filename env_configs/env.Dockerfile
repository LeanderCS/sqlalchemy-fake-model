FROM debian:bullseye-slim

WORKDIR /app

RUN apt-get update  \
    && apt-get install -y \
        build-essential \
        curl \
        g++ \
        git \
        libbz2-dev \
        libffi-dev \
        libjpeg-dev \
        liblzma-dev \
        libncurses5-dev \
        libncursesw5-dev \
        libreadline-dev \
        libsqlite3-dev \
        libssl-dev \
        llvm \
        make \
        python3-dev \
        tk-dev \
        wget \
        xz-utils \
        zlib1g-dev \
    && apt-get clean \
    && curl https://pyenv.run | bash

ENV PATH="/root/.pyenv/bin:/root/.pyenv/shims:/root/.pyenv/versions/3.7.12/bin:$PATH"
RUN echo 'export PATH="/root/.pyenv/bin:$PATH"' >> ~/.bashrc \
    && echo 'eval "$(pyenv init --path)"' >> ~/.bashrc \
    && echo 'eval "$(pyenv init -)"' >> ~/.bashrc \
    && echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc \
    && /root/.pyenv/bin/pyenv install 3.7.12 \
    && /root/.pyenv/bin/pyenv install 3.8.12 \
    && /root/.pyenv/bin/pyenv install 3.9.7 \
    && /root/.pyenv/bin/pyenv install 3.10.2 \
    && /root/.pyenv/bin/pyenv install 3.11.0 \
    && /root/.pyenv/bin/pyenv install 3.12.0 \
    && /root/.pyenv/bin/pyenv install 3.13.0 \
    && /root/.pyenv/bin/pyenv install 3.14-dev \
    && /root/.pyenv/bin/pyenv global 3.7.12 3.8.12 3.9.7 3.10.2 3.11.0 3.12.0 3.13.0 3.14-dev

COPY pyproject.toml /app

RUN python -m pip install .[dev] && python -m pip install tox

COPY .. /app
