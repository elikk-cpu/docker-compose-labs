FROM python:3.13.14-slim-bookworm AS builder

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

WORKDIR /build

RUN python -m venv "${VIRTUAL_ENV}"

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.13.14-slim-bookworm

ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN addgroup --system app \
    && adduser --system --ingroup app --uid 10001 app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app worker.py healthcheck.py ./

USER 10001:10001

CMD ["python", "worker.py"]
