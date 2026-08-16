FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app app
COPY main.py .

ENV HOST=0.0.0.0
EXPOSE 8756

CMD ["python", "-m", "app.server"]
