FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Делаем стартовый скрипт исполняемым
RUN chmod +x docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]