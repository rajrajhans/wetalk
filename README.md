# wetalk
Wetalk is a social network built from ground up mainly using Python's Flask framework. 
The project is deployed live on [wetalk.rajrajhans.com](http://wetalk.rajrajhans.com/home)

## Aim of the project
The aim of the project was to develop a basic prototype of a social media platform.

## Technologies Used
- Flask, an open source web development framework for Python.
- Peewee, an open source Object Relational Mapper (ORM) made in Python. It supports SQLite, MySQL and PostgreSQL
- PosgreSQL and SQLite, as database management systems.
- Heroku, for deploying the webapp online.
- Bootstrap, for front end user interface.
- Git, as a version control system.

### Database Schema
In the spirit of the popular web framework Django, peewee uses declarative model definitions. The idea is that you declare a model class for each table. The model class then defines one or more field attributes which correspond to the table’s columns. For this project, there are just three models:
#### User
Represents a user account and stores the username and password, an email address for generating avatars using gravatar, and a datetime field indicating when that account was created, and a boolean field containing whether the User is has admin privilege.
#### Relationship
This is a utility model that contains two foreign-keys to the User model and stores which users follow one another.
#### Post
The Post model stores the text content of the post, when it was created, and who posted it (foreign key to User).
![image](http://wetalk.rajrajhans.com/static/img/relation.jpg)
This web app has been deployed on Heroku. Originally, SQLite was selected as the database management system for this project due to it's convenience. However, Heroku does not support SQLite due to it's ephemeral file system. Therefore, PostgreSQL had to be added as an DBMS. So, instead of scrapping SQLite and switching to postgres, we added a snippet which would check for HEROKU in the config vars (os.environment) and if it exists, instantiate a Postgresql object in peewee, and if not, a SQLiteDatabase object. The username, password and database url for postgres are included in config vars in heroku. So, url-parse was used.
