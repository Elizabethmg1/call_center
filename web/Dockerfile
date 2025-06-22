
FROM python:3.10-slim

WORKDIR /app

COPY web/requirements.txt .

RUN apt-get update && apt-get install -y \
    ffmpeg curl git build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY web /app

CMD ["uvicorn", "token_api:app", "--host", "0.0.0.0", "--port", "8000"]

