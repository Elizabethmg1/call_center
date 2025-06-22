FROM python:3.10-slim

WORKDIR /app

COPY agent.py /app/
COPY jsoncred.json /app/
COPY .env /app/
COPY requirements.txt /app/


RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "agent.py","dev"]
