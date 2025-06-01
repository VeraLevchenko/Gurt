# вывод структуры проекта
sudo apt install tree
tree -a -I 'node_modules|.git' > structure.txt  
# активация виртуального окружения
source venv/bin/activate
# работает ли сервер PostgreSQL
pg_isready -h localhost -p 5432
# запуск сервера
sudo service postgresql start