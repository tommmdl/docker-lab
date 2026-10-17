FROM python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock && useradd --uid 10001 --create-home app
COPY app/ ./
USER 10001:10001
EXPOSE 8000
CMD ["sh", "-c", "python migrate.py && exec gunicorn --bind 0.0.0.0:8000 --workers 2 --access-logfile - --error-logfile - server:app"]
