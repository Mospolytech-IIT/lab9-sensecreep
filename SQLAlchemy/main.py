"""Работа с БД"""
from fastapi import FastAPI
from sqlalchemy import ForeignKey, create_engine, Column, String, Integer, Text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine("postgresql+pg8000://postgres:pass@localhost:5432/lab9")

class Base(DeclarativeBase):
    """Базовый класс"""
    pass

class Users(Base):
    """Таблица пользователей"""
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class Posts(Base):
    """Таблица постов"""
    __tablename__="Posts"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)

Base.metadata.create_all(bind=engine)

session = sessionmaker(bind=engine)
db = session()

users_data = [
    {"username": "valeria", "email": "valeria@gmail.com", "password": "password1"},
    {"username": "anastasia", "email": "anastasia@egmail.com", "password": "password2"},
]

for user in users_data:
    db.add(Users(**user))
db.commit()

posts_data = [
    {"title": "post1", "content": "content1", "user_id": 1},
    {"title": "post2", "content": "content2", "user_id": 2},
]

for post in posts_data:
    db.add(Posts(**post))
db.commit()

users = db.query(Users).all()
print("Users:")
for user in users:
    print(user.id, user.username, user.email, user.password)

posts = db.query(Posts).join(Users).all()
print("Posts:")
for post in posts:
    print(post.id, post.title, post.content, post.user_id)

users_posts = db.query(Posts).filter_by(user_id=1).all()
print("Posts by user 1:")
for post in users_posts:
    print(post.id, post.title, post.content)

email_update = db.query(Users).filter_by(id=1).first()
if email_update:
    email_update.email = "new_valeria@example.com"
db.commit()

post_update = db.query(Posts).filter_by(id=1).first()
if post_update:
    post_update.content = "Changed content"
db.commit()

post_to_delete = db.query(Posts).filter_by(id=1).first()
if post_to_delete:
    db.delete(post_to_delete)
db.commit()

user_to_delete = db.query(Users).filter_by(id=2).first()
if user_to_delete:
    db.query(Posts).filter_by(user_id=user_to_delete.id).delete()
    db.delete(user_to_delete)
db.commit()

app=FastAPI()
