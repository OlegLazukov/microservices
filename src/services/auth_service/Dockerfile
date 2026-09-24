FROM python:latest

WORKDIR /app

COPY src/services/auth_service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src

CMD ["uvicorn", "src.services.auth_service.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
