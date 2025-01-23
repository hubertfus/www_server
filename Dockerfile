FROM python:3.9-slim

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/www /app/config /app/logs

COPY config.ini /app/config.ini
COPY config/.htaccess /app/config/.htaccess

COPY logs/redirect_log.txt /app/logs/redirect_log.txt

COPY www/ /app/www/

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
