FROM python:3.13-alpine

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-group dev

COPY *.py ./
COPY models/ ./models/
COPY utils/ ./utils/
COPY scripts/ ./scripts/

EXPOSE 7860

CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
