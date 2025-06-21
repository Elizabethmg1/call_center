FROM python:3.10-slim

WORKDIR /app

COPY agent.py /app/
COPY jsoncred.json /app/
COPY .env /app/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "realtime_crazy.py"]
