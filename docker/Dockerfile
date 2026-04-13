FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies for psycopg2 and Pillow
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq-dev \
        libjpeg62-turbo-dev \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements/prod.txt requirements/prod.txt
COPY requirements/base.txt requirements/base.txt
RUN pip install --no-cache-dir -r requirements/prod.txt

FROM base AS app

COPY . .

RUN python manage.py collectstatic --noinput --settings=educore.settings.prod 2>/dev/null || true

EXPOSE 8000

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "educore.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
