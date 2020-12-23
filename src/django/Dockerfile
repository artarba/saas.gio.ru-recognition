FROM python:3.8

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update &&  apt-get install ffmpeg libsm6 libxext6  -y

WORKDIR ./src/django
#VOLUME ~/.mysql/root.crt/:/home/artarba/saas.gio.ru-recognition/src/django/recognition
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .


EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
