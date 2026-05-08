FROM python:3.13-alpine

WORKDIR /app

RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy all necessary backend files
COPY app.py agent.py config.py retrieval.py ./
COPY models/ ./models/
COPY utils/ ./utils/

EXPOSE 7860

CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]