#FROM python:3.8.6-alpine
FROM tiangolo/uwsgi-nginx:python3.8

WORKDIR /src/bot

ADD . /src/bot

ENV UWSGI_CHEAPER 0
ENV UWSGI_PROCESSES 1
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install wheel
RUN pwd
RUN pip install -r requirements.txt

CMD ["uwsgi", "--thunder-lock", "--ini", "./bot.ini"]
