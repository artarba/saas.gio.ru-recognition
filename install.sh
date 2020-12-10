#!/bin/bash
if [ -f .env ]
then
  export $(cat .env | sed 's/#.*//g' | xargs)
fi

project_path=`pwd`


$base_python_interpreter -m venv env
source env/bin/activate
pip install -U pip
pip install -r requirements.txt

$base_python_interpreter file_maker.py

sed -i "s~dbms_template_path~$project_path~g" nginx/django.conf systemd/django.ini
sed -i "s~dbms_template_domain~$project_domain~g" nginx/django.conf src/django/recognition/settings.py
sed -i "s~dbms_template_path~$project_path~g" nginx/django.conf systemd/bot.ini

sudo ln -s $project_path/nginx/django.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/django.conf /etc/nginx/sites-enabled/
sudo ln -s $project_path/systemd/django.ini /etc/uwsgi/apps-enabled/
sudo ln -s $project_path/systemd/bot.ini /etc/uwsgi/apps-enabled/


sudo systemctl daemon-reload
sudo systemctl restart uwsgi
sudo service nginx reload
