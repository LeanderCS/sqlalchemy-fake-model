FROM python:3.6-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    make \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    git \
    libjpeg-dev

RUN curl https://pyenv.run | bash

ENV PATH="/root/.pyenv/bin:/root/.pyenv/shims:/root/.pyenv/versions/3.6.15/bin:$PATH"
RUN echo 'export PATH="/root/.pyenv/bin:$PATH"' >> ~/.bashrc
RUN echo 'eval "$(pyenv init --path)"' >> ~/.bashrc
RUN echo 'eval "$(pyenv init -)"' >> ~/.bashrc
RUN echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

RUN /root/.pyenv/bin/pyenv install 3.6.15
RUN /root/.pyenv/bin/pyenv install 3.7.12
RUN /root/.pyenv/bin/pyenv install 3.8.12
RUN /root/.pyenv/bin/pyenv install 3.9.7
RUN /root/.pyenv/bin/pyenv install 3.10.2
RUN /root/.pyenv/bin/pyenv install 3.11.0
RUN /root/.pyenv/bin/pyenv install 3.12.0
RUN /root/.pyenv/bin/pyenv install 3.13.0

RUN /root/.pyenv/bin/pyenv global 3.6.15 3.7.12 3.8.12 3.9.7 3.10.2 3.11.0 3.12.0 3.13.0

RUN pip install --upgrade pip

COPY ../requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt && pip install tox

COPY .. /app
