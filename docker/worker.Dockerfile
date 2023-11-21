FROM mcr.microsoft.com/playwright:v1.38.0-jammy

WORKDIR /app

COPY . .

RUN apt-get update &&  \
    apt-get install -y --no-install-recommends locales locales-all python3.11 python3-pip \
    # Install python3.11 from source
    build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev  \
    libffi-dev libsqlite3-dev wget libbz2-dev pkg-config \
    && wget https://www.python.org/ftp/python/3.11.4/Python-3.11.4.tgz && tar -xf Python-3.11.*.tgz && cd Python-3.11.*/\
    && ./configure --enable-optimizations && make -j $(nproc) && make altinstall \
    # Clean up
    && rm -rf /var/lib/apt/lists/* && apt-get purge && cd .. && \
    python3.11 -m pip install --upgrade pip && python3.11 -m pip install --no-cache-dir -r requirements.txt && apt-get clean

ENV PYTHONPATH=/app

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN chmod +x ./worker-start.sh
RUN chmod +x ./notifications-start.sh
