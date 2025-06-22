FROM python:3.10-slim

WORKDIR /app

COPY . /app
COPY jsoncred.json /app/jsoncred.json

RUN apt-get update && apt-get install -y \
    ffmpeg curl git build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "agent.py", "start"]


