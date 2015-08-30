from sqlalchemy.orm import sessionmaker
from models import Answers, db_connect, create_answers_table


class CreateOrUpdate(object):
    def create_or_update(self, item, session):
            """
            Helper function that create a new answer,
            or update an answer's vote if it alreay exsists.
            """

            answer = session.query(Answers).filter_by(question_link=item["question_link"]).first()

            # if answer does not exist, then create it
            if not answer:
                answer = Answers(**item)
                session.add(answer)

            # update vote if answer exists
            else:
                answer.vote = item["vote"]


class ZhihuPipeline(object):
    """Pipeline for storing data in the database"""

    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates answers table
        """

        engine = db_connect()
        create_answers_table(engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """
        Save answers that have more than 1000 upvotes in the database.

        When encounter duplicates, update the upvotes.
        """

        if item["vote"] >= 1000:
            session = self.Session()

            try:
                # create or update an answer
                CreateOrUpdate().create_or_update(item=item, session=session)
                session.commit()
            except:
                # undo in case of errors
                session.rollback()
            finally:
                session.close()

        return item
