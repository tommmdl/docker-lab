FROM python:3.13.16-alpine3.24@sha256:2d9aefe2fef018a7eb2c13064c89c71929800fd2e5dccdbf52ea5da5bb8d929a
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apk add --no-cache zlib=1.3.2-r1
WORKDIR /app
COPY requirements.lock .
# Fail rather than silently compiling platform-dependent dependencies.
RUN pip install --only-binary=:all: --no-cache-dir -r requirements.lock \
    && pip uninstall -y pip \
    && python -c "import ensurepip,pathlib,shutil; shutil.rmtree(pathlib.Path(ensurepip.__file__).parent)" \
    && addgroup -g 10001 app && adduser -D -u 10001 -G app app
COPY app/ ./
USER 10001:10001
EXPOSE 8000
CMD ["sh", "-c", "python migrate.py && exec gunicorn --bind 0.0.0.0:8000 --workers 2 --access-logfile - --error-logfile - server:app"]
