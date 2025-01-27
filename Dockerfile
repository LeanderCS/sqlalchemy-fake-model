FROM python:3.6-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc python3-dev

RUN pip install --upgrade pip

COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
