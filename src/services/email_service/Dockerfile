FROM python:latest

WORKDIR /app

COPY src/services/email_service/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src /app/src

CMD ["python", "-m", "src.services.email_service.main"]