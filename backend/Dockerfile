# Backend Dockerfile
# References:
# - see docs/03_non_func_req.txt §7 Portability (Docker)
# - see docs/13_app_arch.txt §5 Deployment (Docker-ready)

FROM python:3.11-slim

WORKDIR /app

# System deps for psycopg2
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app
RUN chmod +x /app/start.sh

# Expose FastAPI port
EXPOSE 8000

# Default command: run migrations then API
CMD ["/app/start.sh"]
