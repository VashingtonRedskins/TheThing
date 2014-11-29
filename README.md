pip install -r path_to_requirments
need install redis-server
brew/apt-get install redis






1) redis-server 
2) celery -A analysis worker -l info
Должно быть 2 активных процесса 

###Django-registration(Для тестирования):
*Отдельным потоком запускаем через терминал:*
```
python -m smtpd -n -c DebuggingServer localhost:1025
```
Здесь будет отображаться сообщение с активацией.
*Пример:*
localhost:8000/accounts/activate/77fd47a5426fbf7292e4d0693df5775df68054cb/

