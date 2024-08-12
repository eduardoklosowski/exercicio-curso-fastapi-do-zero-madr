FROM python:3.12-slim AS builder
ENV PYTHONUNBUFFERED=1

WORKDIR /app/
RUN pip install --disable-pip-version-check --no-cache-dir 'poetry==1.8.3' 'poetry-plugin-export==1.8.0'

COPY pyproject.toml poetry.lock README.md LICENSE.txt ./
RUN poetry export --format=constraints.txt --without-hashes --output=constraints.txt

COPY src ./src
RUN poetry build --format=wheel


# Imagem

FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /app/

COPY --from=builder /app/constraints.txt /app/dist/madr-*.whl ./
RUN pip install --disable-pip-version-check --no-cache-dir --constraint constraints.txt madr-*.whl

EXPOSE 8000
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "--access-log", "madr.api:app"]
