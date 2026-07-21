FROM python:3.13.14-slim-bookworm

ARG APP_VERSION=dev

ENV APP_VERSION=${APP_VERSION} \
    APP_HOST=0.0.0.0 \
    APP_PORT=5000 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
