# POC-only local runtime; never deploy as real identity issuer.
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml /app/
COPY src /app/src
RUN pip install --no-cache-dir '.[database]' && useradd -m -u 10001 mtuser
USER mtuser
EXPOSE 8080
CMD ["uvicorn", "mt_iam.api.app:app", "--host", "0.0.0.0", "--port", "8080"]
