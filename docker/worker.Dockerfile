FROM python:3.11.6-slim-bullseye

WORKDIR /app

COPY requirements.txt .
RUN apt-get update &&  \
    apt-get install -y --no-install-recommends locales locales-all \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt  \
    && pip install --no-cache-dir playwright  \
    && rm -rf /var/lib/apt/lists/* && apt-get purge && apt-get clean
COPY . .

RUN playwright install webkit

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
ENV PYTHONPATH=/app

RUN chmod +x ./worker-start.sh
RUN chmod +x ./notifications-start.sh
