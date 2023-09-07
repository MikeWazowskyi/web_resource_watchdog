FROM python:3.11-buster

WORKDIR /app

COPY infra ./infra

COPY migrations ./migrations

COPY requirements/production.txt ./requirements.txt

COPY web_resource_watchdog ./web_resource_watchdog

RUN pip3 install --upgrade pip

RUN pip3 install -r requirements.txt --no-cache-dir

RUN chmod +x ./infra/flask-entrypoint.sh

RUN chmod +x ./infra/worker-entrypoint.sh
