FROM python:3.11-alpine

WORKDIR /app

RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev \
    openssl-dev \
    libpq

COPY bot/requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY bot/. /app/

CMD ["python", "main.py"]