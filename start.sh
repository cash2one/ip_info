# django start shell
port=`netstat -ntpl|grep 8011|awk '{print $7}'|awk -F '/' '{print $1}'`
kill $port
nohup python manage.py runserver 0.0.0.0:8011 > nohup.out 2>&1 &
