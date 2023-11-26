# Build Stage
FROM python:3.11.6-alpine AS build

WORKDIR /app

COPY requirements.txt .

RUN apk --no-cache add build-base gcc musl-dev postgresql-dev python3-dev libffi-dev \
    && python -m ensurepip \
    && rm -r /usr/lib/python*/ensurepip \
    && pip install --upgrade pip \
    && pip install --no-cache-dir --user -r requirements.txt \
    && pip install --no-cache-dir --user uvicorn

# Production Stage
FROM python:3.11.6-alpine

WORKDIR /app

COPY --from=build /root/.local /root/.local
COPY . .

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

CMD alembic upgrade head || exit 1; uvicorn web.main:app --proxy-headers --forwarded-allow-ips='*' --host 0.0.0.0 --port 8000
