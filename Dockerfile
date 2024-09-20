FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=0

RUN apk update && apk add --no-cache netcat-openbsd

WORKDIR /app
ADD . ./

COPY requirements.txt .
RUN apk add --no-cache --virtual .build-deps gcc musl-dev libffi-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del .build-deps

RUN chmod +x ./run.sh

CMD ["./run.sh"]