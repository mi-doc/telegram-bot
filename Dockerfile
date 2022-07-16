FROM python:3.10-alpine3.15
LABEL maintainer='Mikhail Nikolaev'

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /telegram-bot

RUN apk update && apk add --update postgresql-dev libjpeg && \
    apk add --update --no-cache --virtual .build-deps  \
    python3-dev musl-dev gcc libc-dev linux-headers zlib-dev jpeg-dev && \
    pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt && \
    apk del .build-deps

COPY . .
RUN sed -i 's/\r$//g' /telegram-bot/scripts/entrypoint.sh
RUN chmod -R +x /telegram-bot/scripts/

ENTRYPOINT ["/telegram-bot/scripts/entrypoint.sh"]