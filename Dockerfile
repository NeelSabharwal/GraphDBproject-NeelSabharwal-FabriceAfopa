FROM python:3.12.13-slim-bookworm@sha256:4766d8b510c428e595d74b9cc5bbb2fae8e26316fffb4adc89908d79aacd58a2

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1 COVERAGE_FILE=/tmp/.coverage
WORKDIR /workspace
COPY requirements.txt requirements-dev.txt requirements.lock.txt ./
RUN pip install --no-cache-dir -r requirements.lock.txt \
    && useradd --create-home --uid 10001 appuser
COPY app ./app
COPY scripts ./scripts
COPY tests ./tests
COPY pyproject.toml ./
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
