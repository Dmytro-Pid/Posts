from typing import List, Optional
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import String, Boolean, ForeignKey, func, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy(model_class=declarative_base(), engine_options=dict(echo=True))

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), default = None, nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), default = None, nullable=True)
    password: Mapped[str] = mapped_column(String(1000), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    created : Mapped[datetime] = mapped_column(DateTime(), server_default = func.now())
    posts: Mapped[List["Post"]] = relationship(back_populates="user")

    @property
    def password(self) -> str:
        return self.password_
    
    @password.setter
    def password(self, raw_password: str):
        self.password_ = generate_password_hash(raw_password)

    def is_verify_password(self, raw_password)-> bool:
        return check_password_hash(self.password_, raw_password)
    
class Post(db.Model):
    __tablename__ = 'posts'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(1000))
    text: Mapped[str] = mapped_column(Text())
    created : Mapped[datetime] = mapped_column(DateTime(), server_default = func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey(User.id, ondelete="CASCADE"))
    user: Mapped[User] = relationship(back_populates="posts")
    image: Mapped[str] = mapped_column(String(1000), default=None, nullable=True)