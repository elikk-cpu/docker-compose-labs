FROM python:3.13.14-slim-bookworm
RUN mkdir /data && chown 10001:10001 /data && chmod 700 /data
RUN useradd --uid 10001 --no-create-home app
WORKDIR /app
COPY writer.py .
USER 10001
CMD ["python", "writer.py"]
