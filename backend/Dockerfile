FROM python:3.14-slim

ENV PYTHONUNBUFFERED=1
ENV UV_PYTHON_DOWNLOADS=0
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY . .
RUN uv sync --locked --no-dev

ENV PORT=8080
EXPOSE 8080

USER 1000:1000

CMD ["sh", "-c", "exec uvicorn backend.server:app --host 0.0.0.0 --port \"$PORT\""]
