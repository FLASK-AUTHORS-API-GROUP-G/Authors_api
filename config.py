#Create a class called config
class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/authors_db"
    JWT_SECRET_KEY = "authors"
