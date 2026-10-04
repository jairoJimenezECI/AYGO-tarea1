FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.9 /uv /bin/uv

WORKDIR /app

# Dependencias primero (capa cacheada mientras no cambie el lock).
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY app.py .
COPY static ./static

ENV PATH="/app/.venv/bin:$PATH"
ENV MONOLITH_URL=http://localhost:8081

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
