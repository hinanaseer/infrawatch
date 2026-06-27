FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim
RUN groupadd -r appuser && useradd -r -g appuser appuser
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app.py .
COPY templates/ templates/
ENV APP_ENV=production \
    APP_VERSION=1.0.0 \
    CLOUD_PROVIDER=unknown \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
USER appuser
EXPOSE 8888
CMD ["gunicorn", "--bind", "0.0.0.0:8888", "--workers", "2", "app:app"]