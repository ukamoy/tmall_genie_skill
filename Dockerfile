FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV WEATHER_API_KEY=YOUR_API_KEY

CMD ["uvicorn", "handlers.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]