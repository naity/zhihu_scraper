from sqlalchemy import create_engine, Column, Integer, Date, Text, Unicode, UnicodeText
from sqlalchemy.ext.declarative import declarative_base


DeclarativeBase = declarative_base()


def db_connect():
    """
    Performs database connection and returns a sqlalchemy engine instance
    """

    return create_engine('postgresql://yuantian:iverson3@localhost/zhihu_db')


def create_answers_table(engine):
    DeclarativeBase.metadata.create_all(engine)


class Answers(DeclarativeBase):
    """Sqlalchemy model for Zhihu answers"""

    # define attibutes
    __tablename__ = "answers"

    id = Column("answer_id", Integer, primary_key=True)
    question = Column("question", Unicode)

    # avoid duplicates by add UNIQUE contraint to the question_link attribute
    question_link = Column("question_link", Unicode, unique=True)

    author = Column("author", Unicode)
    author_link = Column("author_link", Unicode, nullable=True)
    vote = Column("vote", Integer)
    summary_img = Column("summary_img", Unicode, nullable=True)
    summary_text = Column("summary_text", UnicodeText)
    answer = Column("answer", Text)
    date = Column("date", Date)
