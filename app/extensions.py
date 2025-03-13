from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# creating a db instance
db = SQLAlchemy()
# The extensions file used to initialize extensions to use in the app

# Creating another instance of flask migrate
migrate = Migrate()

bcrypt = Bcrypt()

jwt = JWTManager()
