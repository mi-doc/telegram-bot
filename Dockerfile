FROM python:3.10-alpine3.15
LABEL maintainer='Mikhail Nikolaev'

ENV PYTHONUNBUFFERED 1
RUN apk update && apk add --update postgresql-dev && \
    apk add --update --no-cache --virtual .build-deps python3-dev musl-dev gcc && \
    python -m venv /py && \
    /py/bin/pip install --upgrade pip

COPY requirements.txt /telegram-bot/requirements.txt
WORKDIR /telegram-bot
RUN /py/bin/pip install -r requirements.txt && \
    apk del .build-deps
ENV PATH="/py/bin:$PATH"

COPY . /telegram-bot/

