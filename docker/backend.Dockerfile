FROM python:3.11.4-slim-bullseye

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y locales locales-all && rm -rf /var/lib/apt/lists/* && apt-get purge && \
    pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt && pip install uvicorn && \
    playwright install --with-deps firefox && apt-get clean

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

COPY . .
EXPOSE 8000
CMD alembic upgrade head; uvicorn web.main:app --proxy-headers --forwarded-allow-ips='*' --host 0.0.0.0 --port 8000
