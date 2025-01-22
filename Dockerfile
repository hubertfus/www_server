FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/www

COPY config.ini /app/config.ini

COPY .htaccess /app/.htaccess

COPY .htaccess /app/redirect_log.txt

COPY www/ /app/www/

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
