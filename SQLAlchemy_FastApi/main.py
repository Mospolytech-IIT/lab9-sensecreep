"""Работа с БД"""
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import ForeignKey, create_engine, Column, String, Integer, Text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

app=FastAPI()

engine = create_engine("postgresql+pg8000://postgres:pass@localhost:5432/lab9_fastapi")

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

def get_db():
    """Cоздаёт новый экземпляр сессии базы данных и
    позволяет передать созданную сессию db в вызывающую функцию"""
    db = session()
    try:
        yield db
    finally:
        db.close()

class UserBase(BaseModel):
    """pydantic-схема для пользователя"""
    username: str
    email: str
    password: str

class User(UserBase):
    """принимает id из бд"""
    id: int
    class Config:
        """конвертирует объекты ORM в соответствующие pydantic-схемы"""
        orm_mode = True

class PostBase(BaseModel):
    """pydantic-схема для поста"""
    title: str
    content: str
    user_id: int

class Post(PostBase):
    """принимает id из бд"""
    id: int
    class Config:
        """конвертирует объекты ORM в соответствующие pydantic-схемы"""
        orm_mode = True


@app.post("/createuser", response_model=User)
def create_user(user: UserBase, db: session = Depends(get_db)):
    """создает пользователя"""
    db_user = db.query(Users).filter(Users.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = Users(username=user.username, email=user.email, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/seeusers", response_model=list[User])
def get_users(db: session = Depends(get_db)):
    """выводит список всех пользователей"""
    return db.query(Users).all()

@app.put("/edituser/{user_id}", response_model=User)
def edit_user(user_id: int, user: UserBase, db: session = Depends(get_db)):
    """позволяет редактировать данные пользователя"""
    db_user = db.query(Users).filter(Users.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.username = user.username
    db_user.email = user.email
    db_user.password = user.password
    db.commit()
    db.refresh(db_user)
    return db_user

@app.delete("/deleteuser/{user_id}", response_model=list[User])
def delete_user(user_id: int, db: session = Depends(get_db)):
    """удаляет пользователя"""
    db_user = db.query(Users).filter(Users.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return db.query(Users).all()

@app.post("/createpost", response_model=Post)
def create_post(post: PostBase, db: session = Depends(get_db)):
    """создает пост"""
    db_user = db.query(Users).filter(Users.id == post.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    new_post = Posts(title=post.title, content=post.content, user_id=post.user_id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get("/seeposts", response_model=list[Post])
def get_posts(db: session = Depends(get_db)):
    """выводит все посты"""
    return db.query(Posts).all()

@app.put("/editposts/{post_id}", response_model=Post)
def edit_post(post_id: int, post: PostBase, db: session = Depends(get_db)):
    """редактирует пост"""
    db_post = db.query(Posts).filter(Posts.id == post_id).first()
    db_user = db.query(Users).filter(Users.id == post.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    db_post.title = post.title
    db_post.content = post.content
    db_post.user_id = post.user_id
    db.commit()
    db.refresh(db_post)
    return db_post

@app.delete("/deleteposts/{post_id}", response_model=list[Post])
def delete_post(post_id: int, db: session = Depends(get_db)):
    """удаляет пост"""
    db_post = db.query(Posts).filter(Posts.id == post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return db.query(Posts).all()
