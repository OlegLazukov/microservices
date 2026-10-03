FROM python:latest

WORKDIR /app

COPY src/gateway/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src

CMD ["uvicorn", "src.gateway.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
