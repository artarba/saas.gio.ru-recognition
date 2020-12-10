import os


main_path = os.getcwd()
ini_location = main_path + '/systemd/'

with open(ini_location + 'bot.ini', 'w') as bot_ini_file:
    bot_ini_file.write("[uwsgi]\n"
                       "http-socket = :3500\n"
                       "socket = /run/uwsgi/bot.sock\n"
                       "chmod-socket    = 777\n"
                       "chdir =" + main_path + "/src/bot\n"
                       "home =" + main_path + "/env\n"
                       "wsgi-file = bot.py\n"
                       "touch-reload = /home/gitlab-runner/builds/fxy3Kp-o/0/root/savebot/.git/index\n"
                       "thunder-lock = true\n"
                       "processes = 1\n"
                       "threads = 2\n"
                       "uid = root\n"
                       "gid = root"
                            )


with open(ini_location + 'django.ini', 'w') as django_ini_file:
    django_ini_file.write("[uwsgi]\n"
                       "uid = root\n"
                       "gid = root\n"
                       "chdir =" + main_path + "/src/django\n"
                       "home =" + main_path + "/env\n"
                       "module = recognition.wsgi:application\n"
                       "env = DJANGO_SETTINGS_MODULE=recognition.settings\n"
                       "master = true\n"
                       "processes = 3\n"
                       "socket = /run/uwsgi/recognition.sock\n"
                       "logto = /tmp/recognition.log\n"
                       "chown-socket = root:root\n"
                       "chmod-socket = 664\n"
                       "vacuum = true"
                            )

