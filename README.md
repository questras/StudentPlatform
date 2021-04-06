# Student Platform
Web platform for students to share knowledge and homework. 

## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)

## General info
This application's purpose is to give students a possibility to gather in groups to share knowledge and homework. Each student needs to create an account. When signed in, they can create groups, share url to groups with others or search and join already existing groups. In a group, they can create tabs and posts. 

## Technologies
* Python 3
* Django 3
* Bootstrap 4
* PostgreSQL
* HTML
* CSS

## Setup
### Local development environment setup using **docker** and **docker-compose**.
1. Download repository and enter root directory (the one with manage.py)
2. Provide environment variables (e.g in .env file) e.g:
```
SECRET_KEY=some_secret_key
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
DEBUG=1
```
3. Export environment variables e.g with .env file:
```
export $(xargs < .env)
```
4. Run docker-compose:
```
docker-compose up --build -d
```
5. Perform migrations:
```
docker-compose exec web python3 manage.py migrate
```
6. That's it. Main page of the application should be in:
```
http://127.0.0.1:8000/platformapp/
```
7. To stop the application, type 
```
docker-compose down
```
Once setup is done, in order to run application it's enough to export environment variables (from point 3) and run docker-compose:
```
docker-compose up -d
```