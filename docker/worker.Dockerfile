FROM python:3.11.4-slim-bullseye

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y --no-install-recommends locales locales-all && rm -rf /var/lib/apt/lists/* && apt-get purge && \
    pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt && \
    playwright install --with-deps firefox && apt-get clean

ENV PYTHONPATH=/app

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN chmod +x ./worker-start.sh

CMD ["bash", "./worker-start.sh"]
