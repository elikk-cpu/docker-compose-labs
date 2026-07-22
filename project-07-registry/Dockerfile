FROM python:3.13.14-slim-bookworm

ARG APP_VERSION=dev

LABEL org.opencontainers.image.title="hello-registry" \
      org.opencontainers.image.version="${APP_VERSION}"

ENV APP_VERSION=${APP_VERSION} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup --system app \
    && adduser --system --ingroup app --uid 10001 app

COPY app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=app:app app/app.py .

USER 10001:10001

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
