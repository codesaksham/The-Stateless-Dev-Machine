FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8999
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8999", "--ssl-keyfile", "certs/key.pem", "--ssl-certfile", "certs/cert.pem"]
