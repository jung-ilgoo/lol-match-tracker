FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# 8080 포트 노출
EXPOSE 8080

# Gunicorn으로 서버 실행
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]