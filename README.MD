# REST API интернет-магазина по доставке конфет

Это выполненное задание второго этапа отбора в школу бэкенд-разработки от Яндекса


## Зависимости
Для запуска проекта вам потребуется Python 3.8+

Также перед запуском нужно установить специальные пакеты:

Библитека с фреймворком `Flask` версии `1.1.2+`, для создания Web-приложений
```sh
pip3 install flask
```
Библиотека `psycopg2` версии `2.8.6+` для взаимодействия с базой данных `PostgreSQL`:
```sh
pip3 install psycopg2
```


## Подготовка к запуску
Для корректной работы приложения на машине должна быть установлена быза данных `PostgreSQL`. Если у вас `Ubuntu`, тогда для её установки, введите в консоль:
<sudo apt-get install postgresql-12>

Для запуска бибилиотеки psycopg2 вам может понадобиться установить дополнительные пакеты `libpq-dev` и `gcc`
```sh
sudo apt-get install libpq-dev gcc
```
После установки пакетов, нужно создать базу данных, которую будет использовать приложение. Чтобы подключиться к СУБД в роли админимтратора, введите:
```sh
sudo -u postgres psql
```
Теперь создайте базу данных
```sql
CREATE DATABASE candy_shop;
```
Создайте нового пользователя и выдайте ему админ-права в базе данных candy_shop
```sql
CREATE USER candy_admin WITH PASSWORD '1';
GRANT ALL PRIVILEGES ON DATABASE candy_shop TO candy_admin;
```

## Запуск
По умолчанию сервис запускается на `0.0.0.0:8080`
КИРИЛЛ, НЕ ЗАБУДЬ ИЗМЕНИТЬ localhost на `0.0.0.0`


Подключиться к консоли PostgreSQL
> sudo -u postgres psql
> CREATE USER candy_admin WITH PASSWORD '1';
> GRANT ALL PRIVILEGES ON DATABASE "candy_shop"
> \c candy_shop;
