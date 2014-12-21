#Prerequisites:
create folder ../analysis/{media, media/repos}
pip install -r project_path/requirments.txt
sudo brew/apt-get install redis

#Run
1. `redis-server`
2.1 'export DJANGO_SETTINGS_MODULE=analysis.settings' 
2.  в той же консоли`celery -A analysis worker -l info`
Должно быть 2 активных процесса 
3. `python manage.py syncdb`
4. `python manage.py runserver`
Для тестирования регистрации/активации пользователя:
5. `python -m smtpd -n -c DebuggingServer localhost:1025`
Будет отображаться сообщение:
*Пример url для активации*
`localhost:8000/accounts/activate/77fd47a5426fbf7292e4d0693df5775df68054cb/`


