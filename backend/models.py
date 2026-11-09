import os
from urllib.parse import quote_plus

from sqlalchemy import Column, String, Integer, ForeignKey
from flask_sqlalchemy import SQLAlchemy

database_name = os.environ.get("DB_NAME", "trivia")
database_user = os.environ.get("DB_USER", "postgres")
database_password = os.environ.get("DB_PASSWORD", "password")
database_host = os.environ.get("DB_HOST", "localhost:5432")
database_path = "postgresql://{}:{}@{}/{}".format(
    database_user, quote_plus(database_password), database_host, database_name
)

db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    """Bind a Flask application and a SQLAlchemy service."""
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)


class Question(db.Model):
    """A trivia question with its answer, category and difficulty."""

    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    category = Column(Integer, ForeignKey("categories.id"), nullable=False)
    difficulty = Column(Integer, nullable=False)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
        }


class Category(db.Model):
    """A category of trivia questions."""

    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }
